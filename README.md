# Python_WakeWordDetection
# Python Wake Words Detection / Keywords Detection by Davoice

[![GitHub release](https://img.shields.io/github/release/frymanofer/KeyWordDetectionIOSFramework.svg)](https://github.com/frymanofer/KeyWordDetectionIOSFramework/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

By [DaVoice.io](https://davoice.io)

[![Twitter URL](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2FDaVoiceAI)](https://twitter.com/DaVoiceAI)

Welcome to **Davoice WakeWord / Keywords Detection** – Wake words and keyword detection solution designed by **DaVoice.io**.

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

## Features

- **High Accuracy:** We have succesfully reached over 99% accurary for all our models.
- **Here is on of our customer's benchmarks**:
Benchmark on "Python wake word", vs top competitors:

Benmark used recordings with 1326 TP files.

Second best was on of the industry top players who detected 1160 TP 

Third  detected TP 831 out of 1326

Score:
```
MODEL         DETECTION RATE
===========================
DaVoice        0.992458
Top Player     0.874811
Third          0.626697
```
- **Easy to use and deploy with Python:** Check out our example code and install scripts.
- **Cross-Platform Support:** Integrate Davoice "Python wake word" into most known HW architectures and OS.
- **Low Latency:** Experience near-instantaneous keyword detection.

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
