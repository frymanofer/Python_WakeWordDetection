# example.py
import sys

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
    consecutiveCountThreshold = 4
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
    keyword_model.set_keyword_detection_threshold_and_gateway_count(predThreshold, consecutiveCountThreshold)

    # read sound files from "list.txt" into a list
    soundFiles=[]
    f = open(fileList,'r')
    for line in f:
       soundFiles.append(line.rstrip('\n'))
    f.close()

    # run keyword detections on this filelist: 
    keyword_model.start_keyword_detection_from_file_list(soundFiles)
    
