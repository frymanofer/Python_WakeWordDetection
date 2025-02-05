import numpy as np
import onnxruntime as ort
import pyaudio
import time

# Constants
MODEL_PATH = "models/silero_vad.onnx"
SAMPLE_RATE = 16000
START_THRESHOLD = 0.9
END_THRESHOLD = 0.25
MIN_SILENCE_DURATION_MS = 600
SPEECH_PAD_MS = 500
WINDOW_SIZE_SAMPLES = 1024

class SlieroVadDetector:
    def __init__(self, model_path, start_threshold, end_threshold, sample_rate, min_silence_duration_ms, speech_pad_ms):
        self.model = SlieroVadOnnxModel(model_path)
        self.start_threshold = start_threshold
        self.end_threshold = end_threshold
        self.sample_rate = sample_rate
        self.min_silence_samples = sample_rate * min_silence_duration_ms / 1000.0
        self.speech_pad_samples = sample_rate * speech_pad_ms / 1000.0
        self.reset()

    def reset(self):
        self.model.reset_states()
        self.triggered = False
        self.temp_end = 0
        self.current_sample = 0

    def apply(self, data, return_seconds=True):
        # Convert byte array to float array
        audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
        
        # Get the window size
        window_size_samples = len(audio_data)
        self.current_sample += window_size_samples

        # Call the model to get the speech probability
        speech_prob = self.model.call(audio_data)
        
        if speech_prob >= self.start_threshold and self.temp_end != 0:
            self.temp_end = 0
        
        if (speech_prob > 0.5):
            print(f'Speech prob == {speech_prob * 100:.2f}%')

        return {}

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
        return output[0][0]

def main():
    # Initialize VAD detector
    vad_detector = SlieroVadDetector(MODEL_PATH, START_THRESHOLD, END_THRESHOLD, SAMPLE_RATE, MIN_SILENCE_DURATION_MS, SPEECH_PAD_MS)

    # Setup PyAudio for real-time audio streaming
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=WINDOW_SIZE_SAMPLES)
    
    print("Starting VAD processing...")

    try:
        while True:
            # Read audio data from the microphone
            data = stream.read(WINDOW_SIZE_SAMPLES)
            
            # Apply the Voice Activity Detector to the data and get the result
            detect_result = vad_detector.apply(data, return_seconds=True)
            
            if detect_result:
                print(detect_result)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()

