import pyaudio
import wave
import uuid
import os
import sys

# Settings for audio recording
if len(sys.argv) == 1:
    print(f"Usage: {sys.argv[0]} \"<KeyWord>\" (best without spaces - use 'underscore' instead, or put at least \" \" around")
    sys.exit()

KEYWORD=sys.argv[1]
KEYWORD=KEYWORD.replace(" ","_")
print(f"using keyword: {KEYWORD}")


FORMAT = pyaudio.paInt16  # Format for audio input
CHANNELS = 1             # Number of audio channels (1 for mono)
RATE = 16000            # Sample rate in Hz
CHUNK = 1280             # Size of each audio chunk
RECORD_SECONDS = 2       # Duration of the recording in seconds
OUTPUT_FILENAME = KEYWORD+"_{COUNT}.wav"  # Name of the output file
OUTPUT_DIR=KEYWORD

os.system(f"mkdir -p {OUTPUT_DIR}")


# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open a new stream
while True:
    stream = audio.open(format=FORMAT, 
                        channels=CHANNELS,
                        rate=RATE, 
                        input=True,
                        frames_per_buffer=CHUNK)
    print("Recording...")

    frames = []

# Record audio in chunks
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

# Stop and close the stream
    stream.stop_stream()
    stream.close()
 
    ID=uuid.uuid4().hex

# Save the recorded audio to a file
    with wave.open(OUTPUT_FILENAME.format(COUNT=ID), 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved as {OUTPUT_FILENAME.format(COUNT=ID)}")
    input("Press Enter to continue...")

# Terminate the PyAudio object
audio.terminate()
