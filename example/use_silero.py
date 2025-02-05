import numpy as np
import onnxruntime as ort
import pyaudio

def preprocess_audio(audio):
    """Preprocess the audio to the desired format for the model."""
    audio = audio / 32768.0  # Normalize to [-1, 1]
    audio = np.expand_dims(audio, axis=0)  # Add batch dimension
    return audio.astype(np.float32)

def load_model(model_path):
    """Load the ONNX model."""
    return ort.InferenceSession(model_path)

def detect_voice_activity(model, audio, sr, h, c):
    """Detect voice activity using the Silero VAD model."""
    input_name = model.get_inputs()[0].name
    sr_name = model.get_inputs()[1].name
    h_name = model.get_inputs()[2].name
    c_name = model.get_inputs()[3].name
    output_name = model.get_outputs()[0].name
    
    # Run the model
    inputs = {
        input_name: audio,
        sr_name: sr,
        h_name: h,
        c_name: c
    }
    outputs = model.run([output_name], inputs)
    return outputs[0]

def main(model_path):
    # Load model
    model = load_model(model_path)
    
    # Initialize PyAudio
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1536
    audio = pyaudio.PyAudio()
    
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    
    print("Listening for speech...")

    # Initialize sr, h, and c inputs
    sr = np.array([RATE], dtype=np.int64)
    h = np.zeros((2, 1, 64), dtype=np.float32)  # Adjusted to expected shape
    c = np.zeros((2, 1, 64), dtype=np.float32)  # Adjusted to expected shape

    try:
        while True:
            # Read audio from microphone
            audio_data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
            
            # Preprocess audio
            audio_data = preprocess_audio(audio_data)
            
            # Detect voice activity
            vad_output = detect_voice_activity(model, audio_data, sr, h, c)
            
            # Process and print results
            for i, frame in enumerate(vad_output[0]):
                print(f"Frame {i}: {'Speech' if frame > 0.5 else 'Silence'} (Confidence: {frame*100:.2f})")

    except KeyboardInterrupt:
        print("Stopping...")
        
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    model_path = "./models/silero_vad_old.onnx"
    main(model_path)
