import numpy as np
import onnxruntime as ort
import pyaudio
import time
import wave
import sys
import select
import math

from scipy.signal import butter, lfilter

# ---------------- CONFIGURABLE CONSTANTS ----------------
MODEL_PATH = "models/silero_vad.onnx"
SAMPLE_RATE = 16000
MIN_SILENCE_DURATION_MS = 600
SPEECH_PAD_MS = 500
WINDOW_SIZE_SAMPLES = 1024

# Two thresholds:
# 1) FIRST_PASS_THRESHOLD: if the full-range VAD is below this, skip the chunk
# 2) BAND_THRESHOLD: each band must exceed this to be included
FIRST_PASS_THRESHOLD = 0.5
BAND_THRESHOLD = 0.2

# Number of total bands (25). We'll generate them below from 20 Hz to ~7900 Hz.
NUM_BANDS = 25
BAND_LOW_FREQ = 20
BAND_HIGH_FREQ = 7900  # Slightly below Nyquist=8000 to avoid butter() ValueError.

# -------------- UTILITY FUNCTIONS --------------

def generate_log_bands(num_bands, min_freq, max_freq):
    """
    Generate 'num_bands' frequency bands, log-spaced between min_freq and max_freq.
    Returns a list of (lowcut, highcut) tuples as floats.
    """
    # We'll space boundaries in log domain
    boundaries = np.logspace(np.log10(min_freq), np.log10(max_freq), num_bands + 1)
    bands = []
    for i in range(num_bands):
        low = boundaries[i]
        high = boundaries[i+1]
        bands.append((low, high))
    return bands

def butter_bandpass(lowcut, highcut, fs, order=4):
    """
    Design a Butterworth bandpass filter for [lowcut, highcut].
    SciPy requires 0 < low < high < 1 in normalized freq, so we clamp if needed.
    """
    nyq = 0.5 * fs
    low = max(0.0001, lowcut / nyq)   # clamp > 0
    high = min(0.9999, highcut / nyq) # clamp < 1
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=4):
    """
    data: float32 array in [-1,1].
    Returns band-passed version of `data`.
    """
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    return lfilter(b, a, data)

def split_into_bands(audio_float, sample_rate, bands):
    """
    Splits float32 audio into multiple frequency bands (each band is float32).
    Returns a list of arrays, one per band.
    """
    banded_data = []
    for (lowcut, highcut) in bands:
        filtered = bandpass_filter(audio_float, lowcut, highcut, sample_rate, order=4)
        banded_data.append(filtered)
    return banded_data

# -------------- SILERO VAD CLASSES --------------

class SlieroVadOnnxModel:
    def __init__(self, model_path):
        self.session = ort.InferenceSession(model_path)
        self.reset_states()

    def reset_states(self):
        self.h = np.zeros((2, 1, 64), dtype=np.float32)
        self.c = np.zeros((2, 1, 64), dtype=np.float32)

    def close(self):
        del self.session

    def call(self, audio_data):
        """
        audio_data: float32 array of shape (window_size,).
        Returns speech probability (float).
        """
        # Model expects shape (1, samples)
        input_data = np.array([audio_data], dtype=np.float32)
        input_feed = {
            'input': input_data,
            'sr': np.array([SAMPLE_RATE], dtype=np.int64),
            'h': self.h,
            'c': self.c
        }
        outputs = self.session.run(None, input_feed)
        output = outputs[0]
        self.h = outputs[1]
        self.c = outputs[2]
        return float(output[0][0])

class SlieroVadDetector:
    """
    Small wrapper around SlieroVadOnnxModel that
    handles raw int16 frames from PyAudio, plus
    some usage of min_silence & speech_pad if needed.
    """
    def __init__(self, model_path, sample_rate, min_silence_duration_ms, speech_pad_ms):
        self.model = SlieroVadOnnxModel(model_path)
        self.sample_rate = sample_rate
        self.min_silence_samples = sample_rate * min_silence_duration_ms / 1000.0
        self.speech_pad_samples = sample_rate * speech_pad_ms / 1000.0
        self.reset()

    def reset(self):
        self.model.reset_states()
        self.triggered = False
        self.current_sample = 0

    def apply(self, data):
        """
        data: raw int16 bytes from PyAudio
        Returns the speech probability (float).
        """
        audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
        self.current_sample += len(audio_data)
        return self.model.call(audio_data)

# -------------- MAIN PROGRAM --------------

def main():
    # Generate the 25 log-spaced frequency bands
    band_definitions = generate_log_bands(
        num_bands=NUM_BANDS,
        min_freq=BAND_LOW_FREQ,
        max_freq=BAND_HIGH_FREQ
    )

    # VAD for first-pass (entire chunk)
    main_vad_detector = SlieroVadDetector(MODEL_PATH, SAMPLE_RATE, MIN_SILENCE_DURATION_MS, SPEECH_PAD_MS)
    # For band-level VAD, we’ll use a separate model instance so we can reset each chunk
    band_vad_model = SlieroVadOnnxModel(MODEL_PATH)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=WINDOW_SIZE_SAMPLES)

    noise_reduced_buffer = []

    print(f"Starting multi-band composite approach with {NUM_BANDS} log-spaced bands.")
    print("Press Enter to stop and save file...")

    try:
        while True:
            # Non-blocking check for user pressing Enter
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                _ = sys.stdin.readline()
                print("Stop signal received. Saving noise-reduced audio...")
                break

            # Read a chunk
            data = stream.read(WINDOW_SIZE_SAMPLES, exception_on_overflow=False)

            # 1) First-pass VAD on full audio
            full_prob = main_vad_detector.apply(data)
            if full_prob < FIRST_PASS_THRESHOLD:
                print(f"Full-range prob={full_prob*100:.2f}% < {FIRST_PASS_THRESHOLD*100:.0f}% -> skip")
                continue

            # 2) If above threshold, do band-level checks
            print(f"Full-range prob={full_prob*100:.2f}% -> Checking {NUM_BANDS} bands...")

            # Convert data to float
            audio_float = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0

            # Split into bands
            bands_data = split_into_bands(audio_float, SAMPLE_RATE, band_definitions)

            # Reset band-level VAD states
            band_vad_model.reset_states()

            # We'll sum the "kept" bands into this composite
            composite_audio = np.zeros_like(audio_float)

            # For each band, decide whether to keep it
            for i, bd in enumerate(bands_data):
                prob = band_vad_model.call(bd)
                (lowcut, highcut) = band_definitions[i]
                if prob > BAND_THRESHOLD:
                    print(f"  Band {int(lowcut)}-{int(highcut)} Hz: prob={prob*100:.1f}% (kept)")
                    composite_audio += bd
                else:
                    print(f"  Band {int(lowcut)}-{int(highcut)} Hz: prob={prob*100:.1f}% (discarded)")

            # Clip and store
            composite_audio = np.clip(composite_audio, -1.0, 1.0)
            composite_int16 = (composite_audio * 32767.0).astype(np.int16)
            noise_reduced_buffer.append(composite_int16.tobytes())

    except KeyboardInterrupt:
        print("KeyboardInterrupt: Stopping and saving...")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

        if noise_reduced_buffer:
            output_filename = "noise_reduced_data.wav"
            with wave.open(output_filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(b"".join(noise_reduced_buffer))

            print(f"Saved noise-reduced audio to '{output_filename}'")
        else:
            print("No audio frames were stored. Nothing to save.")

if __name__ == "__main__":
    main()
