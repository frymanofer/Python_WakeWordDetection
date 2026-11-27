# Python_WakeWordDetection
# Python Wake Words / Keywords Detection by Davoice

[![GitHub release](https://img.shields.io/github/release/frymanofer/KeyWordDetectionIOSFramework.svg)](https://github.com/frymanofer/KeyWordDetectionIOSFramework/releases)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

By [DaVoice.io](https://davoice.io)

[![Twitter URL](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2FDaVoiceAI)](https://twitter.com/DaVoiceAI)


Welcome to **Davoice WakeWord / Keywords Detection** – Wake words and keyword detection solution designed by **DaVoice.io**.

## This example folder!

Follow installation on in the main folder and run the below command:
$ python example.py
change example.py accordingly.

For the new speaker-aware flows, see:

- [../docs/speaker-verification-wake-word.md](../docs/speaker-verification-wake-word.md)
- [wakeword_with_speaker_id.py](wakeword_with_speaker_id.py)
- [speaker_id_onboarding.py](speaker_id_onboarding.py)
- [speaker_id_verification.py](speaker_id_verification.py)
- [speaker_id_gateway.py](speaker_id_gateway.py)

### Commands under a wake word

[example_wakeword_commands_hierarchy.py](example_wakeword_commands_hierarchy.py): each command
listens only for a few seconds after its own wake word; said on its own, it is ignored.

```
pip install pyaudio
python example_wakeword_commands_hierarchy.py                      # microphone
python example_wakeword_commands_hierarchy.py --files a.wav b.wav  # WAV files: 16 kHz, mono, 16-bit
```

Say "Engine", then "Dead slow ahead" or "Stand by the engine". In Russian, say "Mashina", then
"Prigotovit mashinu" or "Samyj malyj vpered". The configuration options are explained in
[../example/README.md](../example/README.md#commands-under-a-wake-word).

## Features

- **High Accuracy:** Our advanced machine learning models deliver top-notch accuracy.
- **Easy to deploy with React Native:** Check out our example code.
- **Cross-Platform Support:** Integrate Davoice KeywordsDetection into most known architectures and OS.
- **Low Latency:** Experience near-instantaneous keyword detection.

## Platforms and Supported Languages

- **linux.x86_64**
- **linux.aarch64**
- **linux.armv7**
- **linux.ppc64**
- **linux.ppc64le**
- **linux.s390x**
- **darwin.x86_64**
- **darwin.arm64**
- **win32**
- **win_amd64**
- **win.arm64**

## Contact

For any questions, requirements, or more support for other platforms, please contact us at info@davoice.io.

## Installation and Usage

### This Example Instructions

Follow installation on in the main folder and run the below command:
$ python example.py
change example.py accordingly.

## Benchmark.

Our customers have benchmarked our technology against leading solutions, including Picovoice Porcupine, Snowboy, Pocketsphinx, Sensory, and others. 
In several tests, our performance was comparable to Picovoice Porcupine, occasionally surpassing it, however both technologies consistently outperformed all others in specific benchmarks. 
For detailed references or specific benchmark results, please contact us at ofer@davoice.io.

## Links

Here are wakeword detection GitHub links per platform:

- **Web / JS / Angular / React:** https://github.com/frymanofer/Web_WakeWordDetection/tree/main
- **For React Native:** [ReactNative_WakeWordDetection](https://github.com/frymanofer/ReactNative_WakeWordDetection)
- **For Android:** [KeywordsDetectionAndroidLibrary](https://github.com/frymanofer/KeywordsDetectionAndroidLibrary)
- **For iOS framework:** 
  - With React Native bridge: [KeyWordDetectionIOSFramework](https://github.com/frymanofer/KeyWordDetectionIOSFramework)
  - Sole Framework: [KeyWordDetection](https://github.com/frymanofer/KeyWordDetection)
