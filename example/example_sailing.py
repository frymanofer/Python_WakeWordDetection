# example.py
import time
from keyword_detection import KeywordDetection
import asyncio
import threading
import os
import platform
import argparse


# Global activation flags and timeout timestamps
activation_flags = {
    "engine": {"active": False, "timeout": 0},
    "mashina": {"active": False, "timeout": 0}
}

countdown_thread = None
stop_event = threading.Event()

timeout = 15
# Lock for thread safety
activation_lock = threading.Lock()

def clear_console():
    # Works on Windows and Unix-like systems
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def print_countdown_banner(message_prefix, seconds):
    global countdown_thread, stop_event

    # Stop the previous countdown if still running
    if countdown_thread and countdown_thread.is_alive():
        stop_event.set()
        countdown_thread.join()

    # Reset for the new countdown
    stop_event = threading.Event()

    def run_countdown():
        width = 90
        border = "*" * width
        for remaining in range(seconds, 0, -1):
            if stop_event.is_set():
                return
            clear_console()
            if (seconds > 100):
                message = f"{message_prefix}"
            else:
                message = f"{message_prefix} for {remaining} seconds"
            middle = f"** {message.center(width - 6)} **"
            print(border)
            print(border)
            print(middle)
            print(border)
            print(border)
            time.sleep(1)
        clear_console()
    # Start new countdown
    countdown_thread = threading.Thread(target=run_countdown)
    countdown_thread.start()

def __print_countdown_banner(message_prefix, seconds):
    width = 60
    border = "*" * width

    for remaining in range(seconds, 0, -1):
        clear_console()
        message = f"{message_prefix} for {remaining} seconds"
        middle = f"** {message.center(width - 6)} **"  # 6 = "** " + " **"
        print(border)
        print(border)
        print(middle)
        print(border)
        print(border)
        time.sleep(1)

def print_banner(message):
    width = 60
    border = "*" * width
    middle = f"** {message.center(width - 6)} **"  # 6 = len("** ") + len(" **")

    print("\n" + border)
    print(border)
    print(middle)
    print(border)
    print(border + "\n")

def _is_activated(name):
    with activation_lock:
        now = time.time()
        entry = activation_flags.get(name)
        return entry["active"] and now < entry["timeout"]

def _activate(name):
        activation_flags[name]["active"] = True
        activation_flags[name]["timeout"] = time.time() + timeout
        #print(f"[WakeWord] '{name}' activated. Listening for commands for {timeout} seconds...")

def _refresh_timeout(name):
    with activation_lock:
        activation_flags[name]["timeout"] = time.time() + timeout
        print(f"[Command] '{name}' timeout refreshed to {timeout} seconds from now.")

def _deactivate_if_expired():
    with activation_lock:
        now = time.time()
        for name, state in activation_flags.items():
            if state["active"] and now >= state["timeout"]:
                state["active"] = False
                print_banner("Waiting For Commands")

def machine_commands_callback(params):
    _deactivate_if_expired()
    phrase = params["phrase"]
    model_index = phrase.find("_model_28")
    if model_index != -1:
        phrase = phrase[:model_index]
    # Step 2: Remove all underscores
    phrase = phrase.replace("_", " ")

    if not _is_activated("mashina"):
        print_countdown_banner(f"[Command] {phrase} Ignored: 'mashina' not activated.", 50000)
        return

    threshold_scores = [score for score in params["threshold_scores"] if score != 0]
    version = params.get("version", "N/A")

    print_countdown_banner(f"Mashina Command \"{phrase}\" Activated", timeout)

    #print_countdown_banner("Engine Command Activated", timeout)
    #print(f"[Command] 'engine' Detected: '{phrase}', scores={threshold_scores}, version={version}")
    _refresh_timeout("mashina")


def engine_commands_callback(params):
    _deactivate_if_expired()
    phrase = params["phrase"]
    model_index = phrase.find("_model_28")
    if model_index != -1:
        phrase = phrase[:model_index]
    # Step 2: Remove all underscores
    phrase = phrase.replace("_", " ")

    if not _is_activated("engine"):
        print_countdown_banner(f"[Command] {phrase} Ignored: 'engine' not activated.", 50000)
        return

    threshold_scores = [score for score in params["threshold_scores"] if score != 0]
    version = params.get("version", "N/A")

    print_countdown_banner(f"Engine Command \"{phrase}\" Activated", timeout)

    #print_countdown_banner("Engine Command Activated", timeout)
    #print(f"[Command] 'engine' Detected: '{phrase}', scores={threshold_scores}, version={version}")
    _refresh_timeout("engine")

def wakeword_callback(params):
    phrase = params["phrase"]
    threshold_scores = [score for score in params["threshold_scores"] if score != 0]
    version = params.get("version", "N/A")

    # Determine which wakeword was triggered
    if "engine" in phrase:
        if _is_activated("engine"):
            print("[WakeWord] 'engine' already activated. Refreshing timeout...")
            print_countdown_banner("Engine Command Re-Activated", timeout)
        else:
            print_countdown_banner("Engine Command Activated", timeout)
        _activate("engine")

    if "mashina" in phrase:
        if _is_activated("mashina"):
            print("[WakeWord] 'Mashina' already activated. Refreshing timeout...")
            print_countdown_banner("Mashina Command Re-Activated", timeout)
        else:
            print_countdown_banner("Mashina Command Activated", timeout)
        _activate("mashina")
    # elif "prigotovit_mashinu" in phrase:
    #     if _is_activated("prigotovit_mashinu"):
    #         print("[WakeWord] 'prigotovit_mashinu' already activated. Refreshing timeout...")
    #     else:
    #         print("[WakeWord] Activating 'prigotovit_mashinu'. Listening for commands...")
    #     _activate("prigotovit_mashinu")

    # The array of models to be used:

keyword_detection_models_russian = [
    {
        "model_path": 
"models/prigotovit_mashinu_model_28_08042025_pyv2.onnx"
            ,
        "callback_function": machine_commands_callback,
        "threshold": 0.99,
        "buffer_cnt": 5
    },
    {
        "model_path": 
"models/samyj_malyj_vpered_model_28_08042025_pyv2.onnx"
            ,
        "callback_function": machine_commands_callback,
        "threshold": 0.99,
        "buffer_cnt": 5
    },
    {
        "model_path": "models/mashina_model_28_08042025_pyv2.onnx",
        "callback_function": wakeword_callback,
        "threshold": 0.8,
        "buffer_cnt": 2
    }
]

# The array of models to be used:
keyword_detection_models = [
    {
        "model_path": 
"models/dead_slow_ahead_model_28_02042025_pyv2.onnx"
            ,
        "callback_function": engine_commands_callback,
        "threshold": 0.99,
        "buffer_cnt": 5
    },
    {
        "model_path": 
"models/stand_by_the_engine_model_28_02042025_pyv2.onnx"
            ,
        "callback_function": engine_commands_callback,
        "threshold": 0.99,
        "buffer_cnt": 5
    },
    {
        "model_path": "models/engine_model_28_02042025_pyv2.onnx",
        "callback_function": wakeword_callback,
        "threshold": 0.99,
        "buffer_cnt": 5
    }
]


async def main():
    global keyword_detection_models_russian, keyword_detection_models
    global countdown_thread, stop_event

    parser = argparse.ArgumentParser(description="Wake Word Detection with Language Option")
    parser.add_argument('--lang', choices=['english', 'russian'], default='english', help='Choose language')
    args = parser.parse_args()
    lang = args.lang.lower()
    print(f"Running in {lang} mode")
    
    keyword_model = KeywordDetection(keyword_models=keyword_detection_models_russian if lang == 'russian' else keyword_detection_models)
    #license for the library:
    #license_key = "MTczODEwMTYwMDAwMA==-Vmv1jwEG+Fbog9LoblZnVT4TzAXDhZs7l9O18A+8ul8="
    # Read the license key from the file
    with open("licensekey.txt", "r") as file:
        license_key = file.read().strip()

    # Print to verify (optional)
    print(f"lincese key is {license_key}")

    keyword_model.set_keyword_detection_license(license_key)
    #for keyword_models_name in keyword_model.keyword_models_names:
        #keyword_model.set_callback(keyword_model_name=keyword_models_name,callback=detection_callback)
    #    keyword_model.set_secondary_callback(keyword_model_name=keyword_models_name,callback=lower_threshold_callback, secondary_threshold=0.9)
    
    # Use this to loop forever: 
    #thread = threading.Thread(target=keyword_model.start_keyword_detection)
    thread = threading.Thread(target=keyword_model.start_keyword_detection, 
                            kwargs={"enable_vad": True, "buffer_ms": 100})
    #keyword_model.start_keyword_detection()
    thread.start()
    print(f"Thread created start_keyword_detection()")
    while True:
        time.sleep(1)  # Sleep for 1 second
      # Stop the previous countdown if still running
        if not countdown_thread or not countdown_thread.is_alive():
            print_countdown_banner(f"Waiting for {lang} Wake Word", 100000)

    thread.join()

    while True:
        time.sleep(1)  # Sleep for 1 second

    # await keyword_model.start_keyword_detection()
    # or setup an async call:
    # asyncio.create_task(keyword_model.start_keyword_detection())  # This will run in the background
    
if __name__ == "__main__":
    # Run the asyncio event loop
    asyncio.run(main())
