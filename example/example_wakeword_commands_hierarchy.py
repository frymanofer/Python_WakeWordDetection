"""Wake words with commands under them (a command hierarchy).

A command model listens only for a short time after ITS OWN wake word was detected.
Said on its own, without the wake word first, a command is ignored. This keeps
false detections low and lets every wake word have its own set of commands.

The hierarchy in this example (all models are in ./models):

    "Engine"   (English)
        ├── "Dead slow ahead"
        └── "Stand by the engine"
    "Mashina"  (Russian, "Машина")
        ├── "Prigotovit mashinu"   ("Приготовить машину", "prepare the engine")
        └── "Samyj malyj vpered"   ("Самый малый вперёд", "dead slow ahead")

Run it from this folder (with keyword_detection_lib installed, see README.md):

    python example_wakeword_commands_hierarchy.py                  # microphone: say "Engine ... dead slow ahead"
    python example_wakeword_commands_hierarchy.py --files a.wav b.wav   # WAV files (16 kHz, mono, 16-bit)

The same "commands" configuration works with every input:
start_keyword_detection() (the microphone), a stream you supply,
start_keyword_detection_external_audio() + feed_audio_frame(),
start_keyword_detection_from_file() and start_keyword_detection_from_file_list().
"""
import argparse
import os
import threading
import time

from keyword_detection import KeywordDetection

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "models")


def model_path(name):
    return os.path.join(MODELS, name)


def nice_name(phrase):
    """'dead_slow_ahead_model_28_02042025_pyv2' -> 'dead slow ahead'"""
    return phrase.split("_model_")[0].replace("_", " ")


# ---------------------------------------------------------------- callbacks
# Callbacks run on a separate thread. Keep them short; hand longer work to your own code.

def on_wake_word(params):
    print(f"\n[wake word] '{nice_name(params['phrase'])}' heard - listening for its commands")


def on_command(params):
    # params: phrase (the command model), parent_wakeword (the wake word it belongs to),
    #         threshold_scores, version, type ("command")
    print(
        f"[command]   '{nice_name(params['phrase'])}' "
        f"(after wake word '{nice_name(params['parent_wakeword'])}')"
    )


# ------------------------------------------------------------ the hierarchy

def command(file_name, callback=on_command):
    """One command under a wake word."""
    return {
        "model_path": model_path(file_name),
        "callback_function": callback,
        "threshold": 0.99,           # score needed for a frame to count (0..1)
        "buffer_cnt": 5,             # consecutive frames above threshold before the callback fires
        "wait_time": 2000,           # ms before the same command can fire again
        "prefetch_ms": 0,            # also look this many ms before the wake word started
        "command_timeout_ms": 5000,  # how long the command listens after its wake word
    }


keyword_detection_models = [
    {
        "model_path": model_path("engine_model_28_02042025_pyv2.onnx"),
        "callback_function": on_wake_word,
        "threshold": 0.99,
        "buffer_cnt": 5,
        "wait_time": 2000,
        "commands": [
            command("dead_slow_ahead_model_28_02042025_pyv2.onnx"),
            command("stand_by_the_engine_model_28_02042025_pyv2.onnx"),
        ],
    },
    {
        "model_path": model_path("mashina_model_28_08042025_pyv2.onnx"),
        "callback_function": on_wake_word,
        "threshold": 0.8,
        "buffer_cnt": 2,
        "wait_time": 2000,
        "commands": [
            command("prigotovit_mashinu_model_28_08042025_pyv2.onnx"),
            command("samyj_malyj_vpered_model_28_08042025_pyv2.onnx"),
        ],
    },
]


def main():
    parser = argparse.ArgumentParser(description="Wake words with commands under them.")
    parser.add_argument("--files", nargs="+", metavar="WAV",
                        help="detect in these WAV files (16 kHz, mono, 16-bit) instead of the microphone")
    parser.add_argument("--license", default=os.path.join(HERE, "licensekey.txt"),
                        help="license key file (default: licensekey.txt in this folder)")
    args = parser.parse_args()

    detector = KeywordDetection(keyword_models=keyword_detection_models)
    with open(args.license) as f:
        detector.set_keyword_detection_license(f.read().strip())

    if args.files:
        for wav in args.files:
            print(f"\n=== {os.path.basename(wav)}")
            detector.start_keyword_detection_from_file(wav)
            time.sleep(0.3)  # let the callback threads print
        return

    try:
        import pyaudio  # noqa: F401  (the microphone needs it)
    except ImportError:
        raise SystemExit(
            "The microphone needs PyAudio: pip install pyaudio\n"
            "(macOS: brew install portaudio first; Ubuntu/Debian: sudo apt install portaudio19-dev).\n"
            "Or test with WAV files: python example_wakeword_commands_hierarchy.py --files a.wav"
        )

    print('\nListening. Say "Engine" and then "Dead slow ahead" or "Stand by the engine",')
    print('or "Mashina" and then "Prigotovit mashinu" or "Samyj malyj vpered".')
    print("A command said without its wake word is ignored. Press Ctrl+C to quit.\n")
    listener = threading.Thread(
        target=detector.start_keyword_detection,
        kwargs={"enable_vad": False, "buffer_ms": 100},
        daemon=True,
    )
    listener.start()
    try:
        while listener.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        detector.stop_keyword_detection()


if __name__ == "__main__":
    main()
