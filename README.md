# Python_WakeWordDetection
# Python Wake Words / Keywords Detection by Davoice

[![GitHub release](https://img.shields.io/github/release/frymanofer/KeyWordDetectionIOSFramework.svg)](https://github.com/frymanofer/KeyWordDetectionIOSFramework/releases)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

By [DaVoice.io](https://davoice.io)

[![Twitter URL](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2FDaVoiceAI)](https://twitter.com/DaVoiceAI)


Welcome to **Davoice WakeWord / Keywords Detection** – Wake words and keyword detection solution designed by **DaVoice.io**.

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

### pip install keyword_detection_lib

### Demo Instructions

Use the example to see how to run the demo:

## Screenshots from the demo App

### Usage Example
See example

## Benchmark.

Our customers have benchmarked our technology against leading solutions, including Picovoice Porcupine, Snowboy, Pocketsphinx, Sensory, and others. 
In several tests, our performance was comparable to Picovoice Porcupine, occasionally surpassing it, however both technologies consistently outperformed all others in specific benchmarks. 
For detailed references or specific benchmark results, please contact us at ofer@davoice.io.

## Activating Microphone while the app operates in the background or during shutdown/closure.
This example in the Git repository enables Android functionality in both the foreground and background, and iOS functionality in the foreground. However, we have developed an advanced SDK that allows the microphone to be activated from a complete shutdown state on Android and from the background state on iOS. If you require this capability for your app, please reach out to us at ofer@davoice.io.

#### Example for iOS Background State

Apple restricts background microphone access for privacy and battery efficiency. However, certain applications, such as security apps, car controlling apps, apps for the blind or visually impaired may require this functionality.

Below is an example for one of the workarounds we have done in order to activate microphone with an empty listener. This approach avoids unnecessary battery usage until real audio capture is needed, at which point you can swap the placeholder listener with the actual microphone callback.

The example below, built in React Native, demonstrates this approach. The function backgroundMicEmptyListener() creates a minimal listener with negligible CPU impact, only processing the function call and return.

```javascript
const handleAppStateChange = (nextAppState) => {
  console.log("handleAppStateChange(): ", nextAppState);
  
  if (nextAppState === 'background') {
    console.log("nextAppState === 'background'");
    BackgroundJob.start(backgroundMicEmptyListener, backgroundOptions)
      .then(() => {
        console.log('Background job started successfully');
      })
      .catch((err) => {
        console.error('Error starting background job:', err);
      });
  }
}
```

## Links

Here are wakeword detection GitHub links per platform:

- **Web / JS / Angular / React:** https://github.com/frymanofer/Web_WakeWordDetection/tree/main
- **For React Native:** [ReactNative_WakeWordDetection](https://github.com/frymanofer/ReactNative_WakeWordDetection)
- **For Android:** [KeywordsDetectionAndroidLibrary](https://github.com/frymanofer/KeywordsDetectionAndroidLibrary)
- **For iOS framework:** 
  - With React Native bridge: [KeyWordDetectionIOSFramework](https://github.com/frymanofer/KeyWordDetectionIOSFramework)
  - Sole Framework: [KeyWordDetection](https://github.com/frymanofer/KeyWordDetection)
