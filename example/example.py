# example.py

from keyword_detection import KeywordDetection

def detection_callback(phrase):
    print(f"detection_callback() Detected phrase: {phrase}")

if __name__ == "__main__":
    # The array of models to be used:
    
    keyword_detection_models = ["models/need_help_now.onnx"]
#    keyword_detection_models = ["models/lunafit_done_model_28_07112024.onnx"]
    keyword_model = KeywordDetection(keyword_models=keyword_detection_models)
    #license for the library:
    license_key = "MTczMjkxNzYwMDAwMA==-DDwBWs914KpHbWBBSqi28vhiM4l5CYG+YgS2n9Z3DMI="
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
    keyword_model.set_keyword_detection_threshold_and_gateway_count('high', 2)

    # Use this to loop forever: 
    keyword_model.start_keyword_detection()
    # or setup an async call:
    # asyncio.create_task(keyword_model.start_keyword_detection())  # This will run in the background
