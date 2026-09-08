# example.py
import time
from keyword_detection import KeywordDetection
import asyncio
import threading
import os
import argparse

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

def _print_command_detection(model_label, params):
    """Print an unmistakable command detection with the exact model identity."""
    phrase = params["phrase"]
    parent_wakeword = params["parent_wakeword"]
    threshold_scores = params["threshold_scores"]
    non_zero_scores = [score for score in threshold_scores if score != 0]
    print("\n" + "=" * 72)
    print(f">>> COMMAND TRIGGERED: {model_label} <<<")
    print(
        f"Detected command: {phrase} "
        f"after wakeword={parent_wakeword} scores={non_zero_scores}"
    )
    print("=" * 72 + "\n")

def help_cnn_command_callback(params):
    _print_command_detection(
        "HELP CNN (help_model_16_02092026_cnn_pyv2.onnx)", params
    )

def help_command_callback(params):
    _print_command_detection(
        "HELP NON-CNN (help_model_16_03032026_pyv2.onnx)", params
    )

def nurse_command_callback(params):
    _print_command_detection(
        "NURSE (nurse_model_16_27022026_pyv2.onnx)", params
    )

def _iter_wav_files_in_folders(folders):
    """Yield .wav files from one or many folders (recursive)."""
    for folder in folders:
        if not os.path.isdir(folder):
            print(f"Skipping (not a folder): {folder}")
            continue
        for root, _, files in os.walk(folder):
            for f in files:
                if f.lower().endswith(".wav"):
                    yield os.path.join(root, f)

def _is_detected(output):
    """
    Best-effort detector for start_keyword_detection_from_file() return value,
    without changing KeywordDetection logic.
    """
    if output is None:
        return False
    if isinstance(output, bool):
        return output
    if isinstance(output, (list, tuple, set)):
        return len(output) > 0
    if isinstance(output, str):
        return len(output.strip()) > 0
    if isinstance(output, dict):
        if "detected" in output:
            return bool(output["detected"])
        if "phrase" in output:
            return bool(output["phrase"])
        if "detections" in output:
            return bool(output["detections"])
        # fallback: any truthy value
        return any(bool(v) for v in output.values())
    # fallback: treat any other non-None object as a detection-ish result
    return True

def _sum_detections(output):
    """
    Sums 'detections' across all models in the output of start_keyword_detection_from_file().
    Expected structure:
      { model_name: { 'detections': <int>, ... }, ... }
    """
    if not isinstance(output, dict):
        return 0
    total = 0
    for _, model_block in output.items():
        if isinstance(model_block, dict):
            try:
                total += int(model_block.get("detections", 0) or 0)
            except Exception:
                pass
    return total

async def main():
    
    # The array of models to be used:
    keyword_detection_models = [
        {
#            "model_path": "models/hey_look_deep.onnx",
            "model_path": "models/hey_nexus_model_28_10082026_pyv2.onnx",
#            "model_path": "models/hey_lookdeep_model_28_06032025_bno22.onnx",
            "callback_function": detection_callback,
            "threshold": 0.99,
            "buffer_cnt": 4,
            "wait_time": 1500, # wait in ms
            "commands": [
                {
                    "model_path": "models/help_model_16_02092026_cnn_pyv2.onnx",
                    "callback_function": help_cnn_command_callback,
                    "prefetch_ms": 0,
                    "threshold": 0.9,
                    "buffer_cnt": 1,
                    "wait_time": 2000,
                    # Time limit the command model is active after wakeword detection.
                    "command_timeout_ms": 5000,
                },
                {
                    "model_path": "models/help_model_16_03032026_pyv2.onnx",
                    "callback_function": help_command_callback,
                    "prefetch_ms": 0,
                    "threshold": 0.9,
                    "buffer_cnt": 1,
                    "wait_time": 2000,
                    # Time limit the command model is active after wakeword detection.
                    "command_timeout_ms": 5000,
                },
                {
                    "model_path": "models/nurse_model_16_27022026_pyv2.onnx",
                    "callback_function": nurse_command_callback,
                    "prefetch_ms": 0,
                    "threshold": 0.9,
                    "buffer_cnt": 1,
                    "wait_time": 2000,
                    # Time limit the command model is active after wakeword detection.
                    "command_timeout_ms": 5000,
                },
            ],
        },
                
        # ./DisneyData/audio/Has_tp_inside_wav/_denois regular 75.94% denoise 76.23%
         # Add more models here:
        # hey_lookdeep_model_28_12122025c_pyv2.onnx Recall: 96.27% denoise: 93.28% Nov11Stacy: 33.33% Nov11Stacy_denoise: 55.56%
        # hey_lookdeep_model_28_12122025b_pyv2_NODENOISE.onnx their: 94.78% denoise: 92.54% Nov11Stacy: 33.33% Nov11Stacy_denoise: 44.44%
        # hey_lookdeep_model_28_06032025_bno22.onnx their_test - 98.51% denoise 98.51% Nov11Stacy: 88.89% Nov11Stacy_denoise: 100.00%
        # hey_lookdeep_model_28_12122025c_pyv2
        #   
        #  Tyler model models/hey_look_deep.onnx:
        #   "threshold": 0.999995,
        #   "buffer_cnt": 5,
        #    /Users/ofer/Downloads/hey_lookdeep_their-test_denoise 86.57%
        #   "threshold": 0.99,
        #   "buffer_cnt": 4,
        #    /Users/ofer/Downloads/hey_lookdeep_their-test_denoise 97.76%
        
        #   hey_lookdeep_model_28_06032025_bno22
        #   "threshold": 0.999995,
        #   "buffer_cnt": 5,
        #    /Users/ofer/Downloads/hey_lookdeep_their-test_denoise 96.27%
        #    /Users/ofer/Downloads/hey_lookdeep_their-test 94.03%
        #    /Users/ofer/Downloads/hey_lookdeep_their-test_strong_denois 92.54%

        # hey_lookdeep_model_28_06032025_bno22 99 / 4
        # Nov11Stacy 88.89%
        # Nov11Stacy_denoise 100.00%
        # Nov11Stacy_strong_denois/ 88.89%
 
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

    # New: optional folder mode (one or many folders). If not provided -> microphone mode as before.
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument(
        "--folders",
        nargs="+",
        default=None,
        help="One or more folders containing .wav files. If provided, runs start_keyword_detection_from_file on files and prints recall%%. If omitted, uses microphone."
    )
    args, _ = parser.parse_known_args()

    if args.folders:
        # Folder mode: run wake word over the folder(s) and provide recall %
        sound_files = list(_iter_wav_files_in_folders(args.folders))
        if not sound_files:
            print(f"No .wav files found in: {args.folders}")
            return

        total = 0
        detected = 0
        summary = {}

        total_detections = 0
        files_with_detection = 0
        hist = {}  # detections_count -> number_of_files

        for soundFile in sound_files:
            total += 1
            print(f"\n>>> Detecting file:\n{soundFile}")
            output = keyword_model.start_keyword_detection_from_file(soundFile)
            print(f"\n>>> output: {output}")
            summary[soundFile] = output

            file_detections = _sum_detections(output)
            total_detections += file_detections
            hist[file_detections] = hist.get(file_detections, 0) + 1

            if file_detections > 0:
                files_with_detection += 1

            if _is_detected(output):
                detected += 1

        recall = (files_with_detection / total) * 100.0 if total > 0 else 0.0
        print(f"\n=== Folder mode results ===")
        print(f"Folders: {args.folders}")
        print(f"Files: {total}")
        print(f"Files with >=1 detection: {files_with_detection}")
        print(f"Total detections (sum over files, sum over models): {total_detections}")
        print(f"Recall: {recall:.2f}% (files with >=1 detection / total files)")

        print(f"\nDetections histogram (detections_in_file -> num_files):")
        for k in sorted(hist.keys()):
            print(f"  {k} -> {hist[k]}")

        return
    
    # Use this to loop forever: 
    #thread = threading.Thread(target=keyword_model.start_keyword_detection)
    thread = threading.Thread(target=keyword_model.start_keyword_detection, 
                            kwargs={"enable_vad": False, "buffer_ms": 100})
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
