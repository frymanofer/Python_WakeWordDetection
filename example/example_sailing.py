# example.py
import time
from keyword_detection import KeywordDetection
import asyncio
import threading
import os

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
    for seconds_left in range(5, -1, -1):
        print(f"Please wait for {seconds_left} seconds before calling '{phrase}' again.")
        time.sleep(1)

async def main():
    # The array of models to be used:
    keyword_detection_models = [
        {
            "model_path": 
    "models/prigotovit_mashinu_model_28_08042025_pyv2.onnx"
                ,
            "callback_function": detection_callback,
            "threshold": 0.99,
            "buffer_cnt": 5
        },
        {
            "model_path": 
    "models/dead_slow_ahead_model_28_02042025_pyv2.onnx"
                ,
            "callback_function": detection_callback,
            "threshold": 0.9999,
            "buffer_cnt": 5
        },
        {
            "model_path": 
"models/stand_by_the_engine_model_28_02042025_pyv2.onnx"
                ,
            "callback_function": detection_callback,
            "threshold": 0.9999,
            "buffer_cnt": 5
        },
        {
            "model_path": "models/engine_model_28_02042025_pyv2.onnx",
            "callback_function": detection_callback,
            "threshold": 0.99,
            "buffer_cnt": 5
        },
        {
            "model_path": "models/hey_mitch_model_28_24032025PY.onnx",
            "callback_function": detection_callback,
            "threshold": 0.99,
            "buffer_cnt": 5
        },
        {
            "model_path": "models/hey_phoenix_model_28_20032025.onnx",
            "callback_function": detection_callback,
            "threshold": 0.99,
            "buffer_cnt": 5
        },
        {
              "model_path": "models/hey_mitch_model_28_24032025PY.onnx",
              "callback_function": detection_callback,
             "threshold": 0.99,
              "buffer_cnt": 3
         }
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
    #thread = threading.Thread(target=keyword_model.start_keyword_detection)
    thread = threading.Thread(target=keyword_model.start_keyword_detection, 
                            kwargs={"enable_vad": True, "buffer_ms": 100})
    #keyword_model.start_keyword_detection()
    thread.start()
    print(f"Thread created start_keyword_detection()")
    thread.join()

    while True:
        time.sleep(1)  # Sleep for 1 second

    # await keyword_model.start_keyword_detection()
    # or setup an async call:
    # asyncio.create_task(keyword_model.start_keyword_detection())  # This will run in the background
    
if __name__ == "__main__":
    # Run the asyncio event loop
    asyncio.run(main())
