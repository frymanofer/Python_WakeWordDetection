# example_external_audio.py
import time
from keyword_detection import KeywordDetection
import asyncio
import threading
import os
import pyaudio
import numpy as np

def restart_mic(py_audio, FORMAT, CHANNELS, RATE, CHUNK):
    # You may want to close and reopen, here is a simple version:
    return py_audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

def mic_dispatcher_thread(keyword_model):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1280

    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_frame = np.frombuffer(data, dtype=np.int16)

            if keyword_model.is_listening:
                keyword_model.feed_audio_frame(audio_frame)

            if keyword_model.is_listening_vad_stand_alone:
                speech_probability = keyword_model.feed_audio_frame_vad(audio_frame)
                if (speech_probability > 0.2):
                    print(f"speech_probability is {speech_probability * 100:.1f}%")

            dbfs, actual_sound = keyword_model.feed_audio_frame_noise_detection(audio_frame, low_noise_margin_db = 20, high_noise_margin_db = 40)
            if (actual_sound != 'silence'):
                print (f"dbfs = {dbfs} actual sound = {actual_sound}")

    except Exception as e:
        print("Mic dispatcher crashed:", e)

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def feed_audio_wakeword(keyword_model):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1280

    py_audio = pyaudio.PyAudio()
    mic_stream = py_audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    while keyword_model.is_listening:
        try:
            if not mic_stream.is_active():
                print("Restarting microphone stream...")
                mic_stream = restart_mic(py_audio, FORMAT, CHANNELS, RATE, CHUNK)
            audio = np.frombuffer(mic_stream.read(CHUNK), dtype=np.int16)
        except OSError as e:
            print(f"Error reading from microphone: {e}")
            mic_stream = restart_mic(py_audio, FORMAT, CHANNELS, RATE, CHUNK)
            continue
        keyword_model.feed_audio_frame(audio)

def lower_threshold_callback(params):
    """Secondary detection callback with structured params."""
    print(f"THIS IS NOT A DETECTION!!!!!",)
    print(f"THIS IS JUST TO INFORM THAT WE GOT HIGHER THAN USUAL THRESHOLD !!!!!",)
    print(f"Threshold is : {params['threshold_scores']}")
    print(f"Recommended to save the activation sound for continuously improving the model Detected phrase: {params['phrase']} threshold_score: {params['threshold_scores']}")

def detection_callback(params):
    """Main detection callback with structured params."""
    phrase = params["phrase"]
    threshold_scores = params["threshold_scores"]
    non_zero_scores = [score for score in threshold_scores if score != 0]
    version = 'N/A'
    if "version" in params:
        version = params["version"]
    print(f"detection_callback() Detected phrase: {phrase} scores={non_zero_scores} version={version}")

async def main():
    
    # The array of models to be used:
    keyword_detection_models = [
        {
            "model_path": "models/hey_lookdeep_model_28_06032025_bno22.onnx",
            "callback_function": detection_callback,
            "threshold": 0.9,
            "buffer_cnt": 4,
            "wait_time": 50 # wait in ms
        },        
         # Add more models here:
        #,
        # {
        #     "model_path": "models/hey_nexus_model_28_13022025.onnx",
        #     "callback_function": detection_callback,
        #     "threshold": 0.9999,
        #     "buffer_cnt": 3
        # }

    ]
    
    keyword_model = KeywordDetection(keyword_models=keyword_detection_models)
    #license for the library:
    #license_key = "MTczODEwMTYwMDAwMA==-Vmv1jwEG+Fbog9LoblZnVT4TzAXDhZs7l9O18A+8ul8="
    # Read the license key from the file
    with open("licensekey.txt", "r") as file:
        license_key = file.read().strip()

    # Print to verify (optional)
    print(f"lincese key is {license_key}")

    keyword_model.set_keyword_detection_license(license_key)
    for keyword_models_name in keyword_model.keyword_models_names:
        #keyword_model.set_callback(keyword_model_name=keyword_models_name,callback=detection_callback)
        keyword_model.set_secondary_callback(keyword_model_name=keyword_models_name,callback=lower_threshold_callback, secondary_threshold=0.9)
    
    # Use this to loop forever: 
    # in the internal audio API we must create a thread!
    #thread = threading.Thread(target=keyword_model.start_keyword_detection, 
    #                        kwargs={"enable_vad": False, "buffer_ms": 100})
    

    # Run with one audio frame dispatcher
    keyword_model.start_keyword_detection_external_audio(enable_vad=False, buffer_ms=100)
    keyword_model.start_vad_external_audio()
    thread = threading.Thread(target=mic_dispatcher_thread, args=(keyword_model,))
    thread.start()
    thread.join()

    # # Run independently:
    # thread = threading.Thread(target=feed_audio_wakeword, args=(keyword_model,))
    # thread.start()
    # print(f"Thread created start_keyword_detection()")

    # #keyword_model.start_keyword_detection()
    # thread_vad = threading.Thread(target=feed_audio_frame_vad, args=(keyword_model,))
    # thread_vad.start()
    # print(f"Thread created feed_audio_frame_vad()")

    # no need to start the noise detection.
    #thread_noise_detect = threading.Thread(target=feed_audio_frame_noise_detection, args=(keyword_model,))
    #thread_noise_detect.start()
    #print(f"Thread created thread_noise_detect()")

    # thread.join()
    # thread_vad.join()
    # thread_noise_detect.join()

    while True:
        time.sleep(1)  # Sleep for 1 second

    # await keyword_model.start_keyword_detection()
    # or setup an async call:
    # asyncio.create_task(keyword_model.start_keyword_detection())  # This will run in the background
    
if __name__ == "__main__":
    # Run the asyncio event loop
    asyncio.run(main())
