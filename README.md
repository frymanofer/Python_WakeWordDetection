# Python_WakeWordDetection
# Python Wake Words Detection / Keywords Detection by Davoice

[![GitHub release](https://img.shields.io/github/release/frymanofer/KeyWordDetectionIOSFramework.svg)](https://github.com/frymanofer/KeyWordDetectionIOSFramework/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

By [DaVoice.io](https://davoice.io)

[![Twitter URL](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2FDaVoiceAI)](https://twitter.com/DaVoiceAI)

Welcome to **Davoice WakeWord / Keywords Detection** – Wake words and keyword detection solution designed by **DaVoice.io**.

🔵  🟢  🟡  🔴  

## About this project

This is a **"<a href="https://davoice.io/wake-word" target="_blank">wake word</a>"** package for Python. 

A **"wake word"** is a keyword or a phrase that activates your device or commands your application, like "Hey Siri" or "OK Google". "Wake Word" is also known as "keyword detection", "Phrase Recognition", "Phrase Spotting", “Voice triggered”, “hotword”, “trigger word”

Except for **"Python wake word"** It also provide **"Python Speech to Intent"**. **Speech to Intent** refers to the ability to recognize a spoken word or phrase
and directly associate it with a specific action or operation within an application. Unlike a **"wake word"**, which typically serves to activate or wake up the application,
Speech to Intent goes further by enabling complex interactions and functionalities based on the recognized intent behind the speech.

For example, a wake word like "Hey App" might activate the application, while Speech
to Intent could process a phrase like "Play my favorite song" or "Order a coffee" to
execute corresponding tasks within the app.
Speech to Intent is often triggered after a wake word activates the app, making it a key
component of more advanced voice-controlled applications. This layered approach allows for
seamless and intuitive voice-driven user experiences.

# Features

- **Easy to use and deploy with Python:** Check out our example code and install scripts.
- **Cross-Platform Support:** Integrate Davoice "Python wake word" into most known HW architectures and OS.
- **Low Latency:** Experience near-instantaneous keyword detection.
- **High Accuracy:** We have successfully reached over 99% accuracy for all our models.
- **Real-World Benchmarks:** At DaVoice, we believe in real benchmarks done by customers on actual use cases rather than static tests. We actively encourage our customers to share their real-world experiences and results.

# <u> 🟢🟢 Customer Benchmarks 🟢🟢 </u>



Provided by: Tyler Troy, CTO & Co-Founder, LookDeep Health
Context: Tyler .

🔵 Criterion I — False Positives (hospital relevance)

## <u>Customer Benchmark **Ⅰ** — LookDeep Health (Customer-reported):</u>
#### <u>Provided by **[Tyler Troy](https://www.lookdeep.health/about-us)**, Co-Founder at **[LookDeep Health](https://lookdeep.health/)**</u>  
**[Tyler Troy](https://www.lookdeep.health/about-us)** at **[LookDeep Health](https://lookdeep.health/)** reported benchmark below as part of selecting a **"phrase detection"** vendor.

## **RESULTS BELOW:**

### ** 🔵 Criteria **Ⅰ** - False Positives**
- In hospital settings, false alerts waste valuable time and can compromise patient care.  
- **✅ DaVoice: "ZERO FALSE POSITIVES" within a month duration of testing.**  
- Porcupine (Picovoice): Several false alerts triggered daily observed under a similar setup.
- OpenWakeWord was not tested for false positives because its true positive rate was too low.

**Definition used by the customer: a “false positive” is a wake event when no wake phrase was spoken, counted over the monitored period.**

### **🔵 Criteria II - True Positive**

**Table 1: A comparison of model performance on custom keywords**  
```
MODEL         DETECTION RATE
===========================
DaVoice                    0.992481 ✅
Porcupine (Picovoice)      0.924812
OpenWakeWords              0.686567
```

- Source: Customer-reported results received on Dec 20, 2024.
- OS: [Linux Python].
- Models/versions: [hey_look_deep_model_28_08122024.py2].
- Thresholds/params: [0.99].
- Note: Results reflect this customer’s setup. Your results may vary.

### **Customer Benchmark II - customer preferred to remain anonymous**  
Benchmark on "Python wake word", vs top competitors:
- Benmark used recordings with 1326 TP files.
- Second best was on of the industry top players who detected 1160 TP 
- Third  detected TP 831 out of 1326

#### **Table 1: A comparison of model performance on custom keywords**  

```
MODEL         DETECTION RATE
===========================
DaVoice        0.992458
Top Player     0.874811
Third          0.626697
```


## Platforms and Supported Languages

- **"Python wake word "** on **linux.x86_64**
- **"Python wake word "** on **linux.aarch64**
- **"Python wake word "** on **linux.armv7**
- **"Python wake word "** on **linux.ppc64**
- **"Python wake word "** on **linux.ppc64le**
- **"Python wake word "** on **linux.s390x**
- **"Python wake word "** on **darwin.x86_64**
- **"Python wake word"** on **darwin.arm64**
- **"Python wake word"** on **win32**
- **"Python wake word"** on **win_amd64**
- **"Python wake word"** on **win.arm64**

# Python Wake word generator

## Create your "custom wake word" for Python

In order to generate your **"custom wake word"** you will need to:

- **Create Python wake word model:**
    Contact us at info@davoice.io with a list of your desired **"custom wake words"**.

    We will send you corresponding models typically your **wake word phrase .onnx** for example:

    A wake word ***"hey sky"** will correspond to **hey_sky.onnx**.

- **Add wake words to Python example:**
    Simply copy your model onnx files to:
    example/models/

    In example.py change the "need_help_now.onnx" to your model.onnx
    keyword_detection_models = ["models/need_help_now.onnx"]
    run python example.py

## Contact

For any questions, requirements, or more support for other platforms, please contact us at info@davoice.io.

## Installation and Usage

Clone this repo

### Important! 
Please edit the installation files (install.sh or first_time_install.sh) and change PYTHON_VERSION=3.12 to your python version!!!

### First time installation without venv environment:
source first_time_installation.sh

### If you already have venv environment:
source install.sh

### Important! 
Please edit the installation files and change PYTHON_VERSION=3.12 to your python version!!!

### Demo Instructions

$ cd example
$ python example.py

## Screenshots from the demo App

### Usage Example
See example

## API Reference

### Initialization

#### `KeywordDetection(keyword_models=keyword_detection_models)`

Creates a new keyword detection instance. `keyword_detection_models` is a list of model configuration dictionaries:

```python
from keyword_detection import KeywordDetection

keyword_detection_models = [
    {
        "model_path": "models/your_wake_word.onnx",  # Path to the ONNX model file
        "callback_function": detection_callback,       # Function called on detection
        "threshold": 0.9,                              # Detection sensitivity (0.0 - 1.0)
        "buffer_cnt": 4,                               # | `buffer_cnt` | `int` Number of sub models to predict on the buffer -> more equals less false positives |

        "wait_time": 50                                # Wait time in ms between inferences
    }
]

keyword_model = KeywordDetection(keyword_models=keyword_detection_models)
```

You can add multiple models to the list to detect several wake words simultaneously.

### License

#### `set_keyword_detection_license(license_key)`

Sets the license key for the library. The license key can be read from a file:

```python
with open("licensekey.txt", "r") as file:
    license_key = file.read().strip()

keyword_model.set_keyword_detection_license(license_key)
```

### Callbacks

#### Detection Callback

The callback function receives a `params` dictionary with the following keys:

| Key | Type | Description |
|-----|------|-------------|
| `phrase` | `str` | The detected wake word / phrase |
| `threshold_scores` | `list[float]` | Array of detection scores |
| `version` | `str` (optional) | Model version |

```python
def detection_callback(params):
    phrase = params["phrase"]
    threshold_scores = params["threshold_scores"]
    version = params.get("version", "N/A")
    print(f"Detected: {phrase} scores={threshold_scores} version={version}")
```

#### `set_secondary_callback(keyword_model_name, callback, secondary_threshold)`

Sets a secondary callback that fires when audio scores are higher than usual but below the primary detection threshold. Useful for logging near-detections and improving models:

```python
def lower_threshold_callback(params):
    print(f"Near-detection for: {params['phrase']} scores: {params['threshold_scores']}")

for name in keyword_model.keyword_models_names:
    keyword_model.set_secondary_callback(
        keyword_model_name=name,
        callback=lower_threshold_callback,
        secondary_threshold=0.9
    )
```

### Detection Modes

#### Mode 1: Internal Audio (Built-in Microphone Capture)

Use `start_keyword_detection()` when you want the library to handle microphone audio capture internally. This is the simplest approach.

**Example** ([example/example.py](example/example.py) for Linux/macOS, [example_windows/example.py](example_windows/example.py) for Windows):

```python
import threading

thread = threading.Thread(
    target=keyword_model.start_keyword_detection,
    kwargs={"enable_vad": False, "buffer_ms": 100}
)
thread.start()
thread.join()
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `enable_vad` | `bool` | Enable Voice Activity Detection |
| `buffer_ms` | `int` | Audio buffer size in milliseconds |

#### Mode 2: External Audio (You Provide Audio Frames)

Use the external audio API when you need to capture and control audio yourself (e.g., from a custom source, network stream, or shared microphone). Audio frames must be **16-bit PCM, mono, 16 kHz**.

**Example** ([example/example_external_audio.py](example/example_external_audio.py) for Linux/macOS, [example_windows/example_external_audio.py](example_windows/example_external_audio.py) for Windows):

```python
import pyaudio
import numpy as np

# 1. Start external audio detection (non-blocking)
keyword_model.start_keyword_detection_external_audio(enable_vad=False, buffer_ms=100)

# 2. Optionally start standalone VAD
keyword_model.start_vad_external_audio()

# 3. Feed audio frames in a loop
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1280

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                input=True, frames_per_buffer=CHUNK)

while True:
    data = stream.read(CHUNK, exception_on_overflow=False)
    audio_frame = np.frombuffer(data, dtype=np.int16)

    # Feed audio for wake word detection
    if keyword_model.is_listening:
        keyword_model.feed_audio_frame(audio_frame)

    # Feed audio for standalone VAD
    if keyword_model.is_listening_vad_stand_alone:
        speech_probability = keyword_model.feed_audio_frame_vad(audio_frame)

    # Noise level detection
    dbfs, actual_sound = keyword_model.feed_audio_frame_noise_detection(
        audio_frame, low_noise_margin_db=20, high_noise_margin_db=40
    )
```

#### External Audio API Methods

| Method | Description |
|--------|-------------|
| `start_keyword_detection_external_audio(enable_vad, buffer_ms)` | Initialize wake word detection for external audio |
| `start_vad_external_audio()` | Initialize standalone Voice Activity Detection |
| `feed_audio_frame(audio_frame)` | Feed a `numpy.int16` audio frame for wake word detection |
| `feed_audio_frame_vad(audio_frame)` | Feed audio for VAD; returns `float` speech probability (0.0 - 1.0) |
| `feed_audio_frame_noise_detection(audio_frame, low_noise_margin_db, high_noise_margin_db)` | Returns `(dbfs, sound_type)` where `sound_type` is e.g. `'silence'`, or an indication of detected sound |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `is_listening` | `bool` | `True` when wake word detection is active and ready for audio |
| `is_listening_vad_stand_alone` | `bool` | `True` when standalone VAD is active and ready for audio |
| `keyword_models_names` | `list[str]` | List of loaded model names |

### File-Based Detection

#### `start_keyword_detection_from_file(file_path)`

Run wake word detection on a `.wav` file. Returns a dictionary with detection results per model:

```python
output = keyword_model.start_keyword_detection_from_file("path/to/audio.wav")
# output: { model_name: { "detections": <int>, ... }, ... }
```

## Documentation
- ["Python Wake Word" API Reference](docs/python_wake_word.md)
- frymanofer.github.io

## Benchmark.

Our customers have benchmarked our technology against leading solutions, including Picovoice Porcupine, Snowboy, Pocketsphinx, Sensory, and others. 
In several tests, our performance was comparable to Picovoice Porcupine, occasionally surpassing it, however both technologies consistently outperformed all others in specific benchmarks. 
For detailed references or specific benchmark results, please contact us at ofer@davoice.io.

### Key words

DaVoice.io Voice commands / Wake words / Voice to Intent / keyword detection npm for Android and IOS.
"Python Wake word detection github"
"Python Wake word detection",
"Python Wake word",
"Python Phrase Recognition",
 "Python Phrase Spotting",
 “Python  Voice triggered”,
 “Python  hotword”,
 “Python trigger word”,
"Wake word detection Python"
"react-native wake word",
"Wake word detection github",
"Wake word generator",
"Custom wake word",
"voice commands",
"wake word",
"wakeword",
"wake words",
"keyword detection",
"keyword spotting",
"speech to intent",
"voice to intent",
"phrase spotting",
"react native wake word",
"Davoice.io wake word",
"Davoice wake word",
"Davoice react native wake word",
"Davoice react-native wake word",
"wake",
"word",
"Voice Commands Recognition",
"lightweight Voice Commands Recognition",
"customized lightweight Voice Commands Recognition",
"rn wake word"

## Links

Here are wakeword detection GitHub links per platform:

- **Web / JS / Angular / React:** https://github.com/frymanofer/Web_WakeWordDetection/tree/main
- **For React Native:** [ReactNative_WakeWordDetection](https://github.com/frymanofer/ReactNative_WakeWordDetection)
- **For Android:** [KeywordsDetectionAndroidLibrary](https://github.com/frymanofer/KeywordsDetectionAndroidLibrary)
- **For iOS framework:** 
  - With React Native bridge: [KeyWordDetectionIOSFramework](https://github.com/frymanofer/KeyWordDetectionIOSFramework)
  - Sole Framework: [KeyWordDetection](https://github.com/frymanofer/KeyWordDetection)
