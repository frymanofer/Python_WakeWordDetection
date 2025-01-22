# API Documentation for Wake Word / Keyword Detection

# Python Wakeword Detection Library
Learn how to implement "wake word", AKA  detection in Python applications with this lightweight and efficient library.

## Overview
This module provides functionality for detecting specific keywords in audio input using a machine learning model. It utilizes asynchronous programming and threading to manage keyword detection and callbacks effectively.

## Dependencies
- `keyword_detection`: A custom library for keyword detection.
- `asyncio`: A standard library for asynchronous programming in Python.
- `threading`: A standard library for creating and managing threads.

## Functions

### `detection_callback(phrase: str) -> None`
This function is called when a keyword is detected. It prints the detected phrase and prompts the user to wait before calling the phrase again.

#### Parameters
- `phrase` (str): The detected keyword or phrase.

#### Returns
- None

#### Example
```python
detection_callback("need help")

main() -> None
The main asynchronous function that initializes the keyword detection model, sets the license, configures the detection parameters, and starts the detection process in a separate thread.

Parameters
None

Returns
None

Example
asyncio.run(main())

Keyword Detection Model Configuration
KeywordDetection
This class is responsible for managing the keyword detection models.

Methods
set_keyword_detection_license(license_key: str) -> None

Sets the license key for the keyword detection model.

set_callback(keyword_model_name: str, callback: Callable) -> None

Sets a callback function that will be called when a keyword is detected.

set_keyword_detection_threshold_and_gateway_count(threshold: str, gateway_count: int) -> None

Configures the sensitivity threshold and the number of checks before calling the callback.

Parameters for set_keyword_detection_threshold_and_gateway_count
threshold (str): Sensitivity level for detection. Options include:

'high'

'medium'

'low'

'lowest'

gateway_count (int): Number of times to double-check before calling the callback. Should be between 1 and 10.

Example
keyword_model.set_keyword_detection_threshold_and_gateway_count('high', 3)

start_keyword_detection() -> None
Starts the keyword detection process. This method should be run in a separate thread or as an asynchronous task.

Parameters
None

Returns
None

Example
thread = threading.Thread(target=keyword_model.start_keyword_detection)
thread.start()

Usage
To use the keyword detection functionality, follow these steps:

Import the necessary libraries and the KeywordDetection class.

Initialize the KeywordDetection instance with the model paths.

Set the license key for the model.

Configure the callback and detection parameters.

Start the detection process in a separate thread or asynchronously.

Example
import asyncio
import threading
from keyword_detection import KeywordDetection

async def main():
    keyword_detection_models = ["models/need_help_now.onnx"]
    keyword_model = KeywordDetection(keyword_models=keyword_detection_models)
    license_key = "your_license_key_here"
    keyword_model.set_keyword_detection_license(license_key)
    
    for model_name in keyword_model.keyword_models_names:
        keyword_model.set_callback(keyword_model_name=model_name, callback=detection_callback)
    
    keyword_model.set_keyword_detection_threshold_and_gateway_count('high', 3)
    
    thread = threading.Thread(target=keyword_model.start_keyword_detection)
    thread.start()
    thread.join()

if __name__ == "__main__":
    asyncio.run(main())

