import numpy as np
import onnxruntime as ort
import pyaudio
import time
import wave
import sys
import select

from scipy.signal import butter, lfilter

# -------------- CONFIGURABLE CONSTANTS --------------
MODEL_PATH = "models/silero_vad.onnx"
SAMPLE_RATE = 16000
MIN_SILENCE_DURATION_MS = 600
SPEECH_PAD_MS = 500
WINDOW_SIZE_SAMPLES = 1024

# Frequency bands: we’ll use 5 bands for demonstration
# (You can adjust cutoffs as desired, just ensure highcut < Nyquist=8000)
BAND_DEFINITIONS = [
    (20, 200),
    (200, 600),
    (600, 1600),
    (1600, 3200),
    (3200, 7900),  # slightly below 8000 to avoid butter() ValueError
]

# First-pass VAD threshold & second-pass threshold
# - If raw VAD < FIRST_PASS_THRESHOLD, skip
# - Then among bands, we only store if band’s VAD > SECOND_PASS_THRESHOLD
FIRST_PASS_THRESHOLD = 0.5
SECOND_PASS_THRESHOLD = 0.5

# -------------- UTILITY FUNCTIONS --------------
def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    if low <= 0:
        low = 0.0001  # avoid zero or negative
    if high >= 1.0:
        high = 0.9999  # avoid >= Nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=4):
    """
    data: float32 numpy array
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
        audio_data: float32 numpy array, shape (window_size,)
        Returns speech probability (float).
        """
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
    # 1) Create two separate VAD detectors:
    #    - One for the first pass (on full-band audio).
    #    - One for frequency-split pass (used only if first pass is above threshold).
    main_vad_detector = SlieroVadDetector(MODEL_PATH, SAMPLE_RATE, MIN_SILENCE_DURATION_MS, SPEECH_PAD_MS)
    freq_vad_detector = SlieroVadOnnxModel(MODEL_PATH)  # We'll reset states each time we do second pass

    # Setup PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=WINDOW_SIZE_SAMPLES)

    noise_reduced_buffer = []

    print("Starting multi-band VAD (two-pass).")
    print("Press Enter to stop and save file...")

    try:
        while True:
            # Non-blocking check if user pressed Enter
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                _ = sys.stdin.readline()
                print("Stop signal received. Saving noise-reduced audio...")
                break

            # Read a chunk
            data = stream.read(WINDOW_SIZE_SAMPLES, exception_on_overflow=False)

            # 2) First pass VAD: check entire chunk
            full_prob = main_vad_detector.apply(data)
            if full_prob < FIRST_PASS_THRESHOLD:
                # Below threshold, skip
                print(f"First-pass prob={full_prob*100:.2f}%. Skipped.")
                continue

            # 3) If above threshold, do second pass:
            #    a) Split into frequency bands.
            #    b) VAD each band. Keep best if above threshold.
            audio_float = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
            bands_data = split_into_bands(audio_float, SAMPLE_RATE, BAND_DEFINITIONS)

            # Reset freq VAD states so it doesn't accumulate across chunks
            freq_vad_detector.reset_states()

            best_prob = -1.0
            best_band = None

            for bd in bands_data:
                prob = freq_vad_detector.call(bd)
                if prob > best_prob:
                    best_prob = prob
                    best_band = bd

            # 4) If best band also above threshold, store that band
            if best_prob > SECOND_PASS_THRESHOLD:
                print(f"  2nd-pass best band prob={best_prob*100:.2f}% - storing it.")
                best_band_clipped = np.clip(best_band, -1.0, 1.0)
                best_band_int16 = (best_band_clipped * 32767.0).astype(np.int16)
                noise_reduced_buffer.append(best_band_int16.tobytes())
            else:
                print(f"  2nd-pass best band prob={best_prob*100:.2f}% - below threshold, not stored.")

    except KeyboardInterrupt:
        print("KeyboardInterrupt: stopping, saving what we have...")

    finally:
        # Cleanup
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
