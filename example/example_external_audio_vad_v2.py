# example_external_audio_vad_v2.py
import time
from keyword_detection import KeywordDetection
import asyncio
import threading
import pyaudio
import numpy as np

VAD_PRINT_THRESHOLD = 0.3


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

            vad_v1_probability = None
            vad_v2_probability = None

            if keyword_model.is_listening_vad_stand_alone:
                vad_v1_probability = keyword_model.feed_audio_frame_vad(audio_frame)

            if keyword_model.is_listening_vad_v2_stand_alone:
                vad_v2_probability = keyword_model.feed_audio_frame_vad_v2(audio_frame)

            should_print_v1 = vad_v1_probability is not None and vad_v1_probability > VAD_PRINT_THRESHOLD
            should_print_v2 = vad_v2_probability is not None and vad_v2_probability > VAD_PRINT_THRESHOLD

            if should_print_v1 or should_print_v2:
                v1_text = "N/A" if vad_v1_probability is None else f"{vad_v1_probability * 100:.1f}%"
                v2_text = "N/A" if vad_v2_probability is None else f"{vad_v2_probability * 100:.1f}%"
                print(f"vad_v1={v1_text}  vad_v2={v2_text}")

    except Exception as e:
        print("Mic dispatcher crashed:", e)

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


def detection_callback(params):
    phrase = params["phrase"]
    threshold_scores = params["threshold_scores"]
    non_zero_scores = [score for score in threshold_scores if score != 0]
    version = params.get("version", "N/A")
    print(f"detection_callback() Detected phrase: {phrase} scores={non_zero_scores} version={version}")


async def main():
    keyword_detection_models = [
        {
            "model_path": "models/hey_lookdeep_model_28_06032025_bno22.onnx",
            "callback_function": detection_callback,
            "threshold": 0.9,
            "buffer_cnt": 4,
            "wait_time": 50
        },
    ]

    keyword_model = KeywordDetection(keyword_models=keyword_detection_models)

    with open("licensekey.txt", "r") as file:
        license_key = file.read().strip()

    print(f"lincese key is {license_key}")
    keyword_model.set_keyword_detection_license(license_key)

    keyword_model.start_keyword_detection_external_audio(enable_vad=False, buffer_ms=100)
    keyword_model.start_vad_external_audio()
    keyword_model.start_vad_v2_external_audio()

    thread = threading.Thread(target=mic_dispatcher_thread, args=(keyword_model,))
    thread.start()
    thread.join()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
