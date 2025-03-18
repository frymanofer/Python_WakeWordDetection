# example.py
import time
from keyword_detection import KeywordDetection
import asyncio
import threading

def detection_callback(phrase):
    print(f"detection_callback() Detected phrase: {phrase}")
    for seconds_left in range(5, -1, -1):
        print(f"Please wait for {seconds_left} seconds before calling '{phrase}' again.")
        time.sleep(1)

async def main():
    # The array of models to be used:
    keyword_detection_models = ["models/hey_lookdeep.onnx"]
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
        print ("model_name = ", keyword_models_name)
        keyword_model.set_callback(keyword_model_name=keyword_models_name,callback=detection_callback)
    
        # set keyword detection threshold sensitivity:
    # threshold sensitivity values:
    #   'high' - default
    #   'medium'
    #   'low'
    #   'lowest' 
    # gateway count: how many time to double check before calling callback
    # gateway count values:
    # 2 - default
    # number between 1 and 10.
#    keyword_model.set_keyword_detection_threshold_and_gateway_count('medium', 2)
    keyword_model.set_keyword_detection_threshold_and_gateway_count('high', 5)

    # Use this to loop forever: 
    # keyword_model.start_keyword_detection()
    thread = threading.Thread(target=keyword_model.start_keyword_detection)
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
