# example.py
import sys
import json
import os

from keyword_detection import KeywordDetection

def detection_callback(phrase):
    print(f"detection_callback() Detected phrase: {phrase}")

if __name__ == "__main__":

    if len(sys.argv) <= 2:
        print(f"Usage: {sys.argv[0]} <list_of_wav_files.txt> <model.onnx,model2.onnx..> <pred_threshold (high,medium,log)> <consecutive_count_threshold> ")
        sys.exit()

    fileList = sys.argv[1]
    models   = sys.argv[2]
    predThreshold = 'high'
    consecutiveCountThreshold = 5
    if len(sys.argv) > 3:
        predThreshold = sys.argv[3]
        print(f"setting prediction threshold to: {predThreshold}")
    if len(sys.argv) > 4:
        consecutiveCountThreshold = int(sys.argv[4])
        print(f"setting consecutiveCount threshold to: {consecutiveCountThreshold}")


    # The array of models to be used:
    
    #keyword_detection_models = ["models/hey_look_deep_model_28_08122024.onnx", "models/get_nurse_model_28_08122024.onnx"]
    keyword_detection_models = [models]

    
    keyword_model = KeywordDetection(keyword_models=keyword_detection_models)
    #license for the library:
    #icense_key = "MTczMjkxNzYwMDAwMA==-DDwBWs914KpHbWBBSqi28vhiM4l5CYG+YgS2n9Z3DMI="
    #icense_key = "MTczNDIxMzYwMDAwMA==-tNV5HJ3NTRQCs5IpOe0imza+2PgPCJLRdzBJmMoJvok="
    license_key = "MTczNDY0NTYwMDAwMA==-KyuASkB3Qk5SW/yWSwwzCtnd1nEuIMLPP8BxHWpfQno="
    keyword_model.set_keyword_detection_license(license_key)
    for keyword_models_name in keyword_model.keyword_models_names:
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
    #keyword_model.set_keyword_detection_threshold_and_gateway_count('high', 2)
    #keyword_model.set_keyword_detection_threshold_and_gateway_count('low', 10)
    #keyword_model.set_keyword_detection_threshold_and_gateway_count('low', 4)
    keyword_model.set_keyword_detection_threshold_and_gateway_count(predThreshold, consecutiveCountThreshold)
    print(f"\n")
    print(f"\n")
    print(f"         *** Starting to detect from files ***\n")

    # read sound files from "list.txt" 
    summary={}
    input_path = fileList
    if input_path.endswith(".txt"):
        with open(input_path, 'r') as f:
            sound_files = [line.strip() for line in f if line.strip().endswith(".wav")]
    elif input_path.endswith(".wav"):
        sound_files = [input_path]
    elif os.path.isdir(input_path):
        sound_files = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith(".wav")]
    else:
        print("Invalid input. Please provide a .txt file, .wav file, or a folder containing .wav files.")
        sys.exit(1)
 
    for soundFile in sound_files:
        print(f"detecting file:\n{soundFile}")
        output = keyword_model.start_keyword_detection_from_file(soundFile)
        summary[soundFile] = output
#    f = open(fileList,'r')
#    for line in f:
#       soundFile=line.rstrip('\n')
#       print(f"detecting file: {soundFile}")
#       # run keyword detections on this filelist: 
#       output = keyword_model.start_keyword_detection_from_file(soundFile)
#       summary[soundFile]=output
       
    output_file_path = 'summary_output.json'
    print(f"\n        *** Done Processing *** \nSaving results to : {output_file_path}")
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(summary, file, indent=4)

#    f.close()

    
