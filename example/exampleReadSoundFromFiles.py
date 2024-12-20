# example.py
import sys
import json
import os

from keyword_detection import KeywordDetection

def detection_callback(phrase):
    print(f"\n>>> Detected phrase: {phrase}\n")

def print_banner(text):
    print("\n" + "-" * 78)
    print(f"{text.center(78)}")
    print("-" * 78 + "\n")

if __name__ == "__main__":

    if len(sys.argv) <= 2:
        print(f"Usage: {sys.argv[0]} <list_of_wav_files.txt> <model.onnx,model2.onnx..> <pred_threshold (high,medium,log)> <consecutive_count_threshold>")
        sys.exit()

    fileList = sys.argv[1]
    models = sys.argv[2]
    predThreshold = 'high'
    consecutiveCountThreshold = 5

    if len(sys.argv) > 3:
        predThreshold = sys.argv[3]
        print(f"Setting prediction threshold to: {predThreshold}")
    if len(sys.argv) > 4:
        consecutiveCountThreshold = int(sys.argv[4])
        print(f"Setting consecutive count threshold to: {consecutiveCountThreshold}")

    keyword_detection_models = [models]

    keyword_model = KeywordDetection(keyword_models=keyword_detection_models)
    license_key = "MTczODEwMTYwMDAwMA==-Vmv1jwEG+Fbog9LoblZnVT4TzAXDhZs7l9O18A+8ul8="
    keyword_model.set_keyword_detection_license(license_key)

    for keyword_models_name in keyword_model.keyword_models_names:
        keyword_model.set_callback(keyword_model_name=keyword_models_name, callback=detection_callback)

    keyword_model.set_keyword_detection_threshold_and_gateway_count(predThreshold, consecutiveCountThreshold)

    print_banner("Starting Keyword Detection from Files")

    # Process input files or folders
    summary = {}
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
        print(f"\n>>> Detecting file:\n{soundFile}")
        output = keyword_model.start_keyword_detection_from_file(soundFile)
        summary[soundFile] = output

    output_file_path = 'summary_output.json'
    print_banner("Done Processing")

    text = "Saving results to: " + output_file_path
    print("" + "-" * 78)
    print(f"{text.center(78)}")
    print("-" * 78 + "\n")

    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(summary, file, indent=4)
