# Python Wake Word / Keyword Detection — API Reference

By [DaVoice.io](https://davoice.io)

## Overview

This library provides real-time wake word (keyword) detection for Python applications. It supports:

- **Internal audio mode** — the library captures microphone audio for you.
- **External audio mode** — you capture audio yourself and feed frames to the library.
- **File-based detection** — run detection on `.wav` files.
- **Voice Activity Detection (VAD)** — standalone speech probability estimation.
- **Noise detection** — ambient noise level classification.

## Dependencies

- `keyword_detection` — the DaVoice keyword detection library.
- `asyncio` — standard library for async programming.
- `threading` — standard library for thread management.
- For external audio mode: `pyaudio` and `numpy`.

---

## Quick Start

```python
import asyncio
import threading
from keyword_detection import KeywordDetection

def detection_callback(params):
    print(f"Detected: {params['phrase']}  scores: {params['threshold_scores']}")

async def main():
    models = [
        {
            "model_path": "models/your_wake_word.onnx",
            "callback_function": detection_callback,
            "threshold": 0.9,
            "buffer_cnt": 4,
            "wait_time": 50
        }
    ]

    kw = KeywordDetection(keyword_models=models)

    with open("licensekey.txt") as f:
        kw.set_keyword_detection_license(f.read().strip())

    thread = threading.Thread(
        target=kw.start_keyword_detection,
        kwargs={"enable_vad": False, "buffer_ms": 100}
    )
    thread.start()
    thread.join()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Class: `KeywordDetection`

### Constructor

```python
KeywordDetection(keyword_models=keyword_detection_models)
```

Creates a keyword detection instance.

**Parameter:** `keyword_models` — a list of model configuration dictionaries. Each dictionary accepts:

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `model_path` | `str` | Yes | Path to the `.onnx` model file |
| `callback_function` | `callable` | Yes | Function invoked when the wake word is detected |
| `threshold` | `float` | Yes | Detection sensitivity (`0.0` – `1.0`). Higher = fewer false positives |
| `buffer_cnt` | `int` | Yes | Number of consecutive inference frames to buffer before triggering |
| `wait_time` | `int` | No | Wait time in milliseconds between inferences (default varies) |

You can supply multiple model dictionaries to detect several wake words simultaneously.

**Example:**

```python
keyword_detection_models = [
    {
        "model_path": "models/hey_assistant.onnx",
        "callback_function": detection_callback,
        "threshold": 0.9,
        "buffer_cnt": 4,
        "wait_time": 50
    },
    {
        "model_path": "models/ok_assistant.onnx",
        "callback_function": detection_callback,
        "threshold": 0.8,
        "buffer_cnt": 3,
        "wait_time": 50
    }
]

keyword_model = KeywordDetection(keyword_models=keyword_detection_models)
```

---

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `keyword_models_names` | `list[str]` | List of loaded model names (derived from model paths) |
| `is_listening` | `bool` | `True` when wake word detection is active and accepting audio |
| `is_listening_vad_stand_alone` | `bool` | `True` when standalone VAD is active and accepting audio |

---

## License

### `set_keyword_detection_license(license_key)`

Sets the license key required to use the library.

| Parameter | Type | Description |
|-----------|------|-------------|
| `license_key` | `str` | Your DaVoice license key |

```python
with open("licensekey.txt", "r") as file:
    license_key = file.read().strip()

keyword_model.set_keyword_detection_license(license_key)
```

Contact info@davoice.io to obtain a license key.

---

## Callbacks

### Detection Callback

The callback function you provide in `callback_function` receives a single `params` dictionary:

| Key | Type | Description |
|-----|------|-------------|
| `phrase` | `str` | The detected wake word / phrase |
| `threshold_scores` | `list[float]` | Array of detection confidence scores |
| `version` | `str` *(optional)* | Model version identifier |

```python
def detection_callback(params):
    phrase = params["phrase"]
    threshold_scores = params["threshold_scores"]
    version = params.get("version", "N/A")
    print(f"Detected: {phrase}  scores={threshold_scores}  version={version}")
```

### `set_secondary_callback(keyword_model_name, callback, secondary_threshold)`

Registers a secondary callback that fires when inference scores exceed `secondary_threshold` but remain below the primary detection threshold. This is useful for logging near-miss detections and collecting audio samples to improve your model.

| Parameter | Type | Description |
|-----------|------|-------------|
| `keyword_model_name` | `str` | Model name (from `keyword_models_names`) |
| `callback` | `callable` | Callback function (same signature as detection callback) |
| `secondary_threshold` | `float` | Score threshold to trigger this callback |

```python
def lower_threshold_callback(params):
    print(f"Near-detection: {params['phrase']}  scores: {params['threshold_scores']}")

for name in keyword_model.keyword_models_names:
    keyword_model.set_secondary_callback(
        keyword_model_name=name,
        callback=lower_threshold_callback,
        secondary_threshold=0.9
    )
```

---

## Detection Modes

### Mode 1: Internal Audio (Built-in Microphone Capture)

The simplest approach — the library handles microphone capture internally.

#### `start_keyword_detection(enable_vad=False, buffer_ms=100)`

Starts keyword detection using the system microphone. **This call blocks**, so it should be run in a separate thread.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_vad` | `bool` | `False` | Enable built-in Voice Activity Detection |
| `buffer_ms` | `int` | `100` | Audio buffer size in milliseconds |

**Full example** (see [example/example.py](../example/example.py) for Linux/macOS, [example_windows/example.py](../example_windows/example.py) for Windows):

```python
import asyncio
import threading
from keyword_detection import KeywordDetection

def detection_callback(params):
    phrase = params["phrase"]
    scores = [s for s in params["threshold_scores"] if s != 0]
    print(f"Detected: {phrase}  scores={scores}")

async def main():
    models = [
        {
            "model_path": "models/your_wake_word.onnx",
            "callback_function": detection_callback,
            "threshold": 0.9,
            "buffer_cnt": 4,
            "wait_time": 50
        }
    ]

    keyword_model = KeywordDetection(keyword_models=models)

    with open("licensekey.txt") as f:
        keyword_model.set_keyword_detection_license(f.read().strip())

    thread = threading.Thread(
        target=keyword_model.start_keyword_detection,
        kwargs={"enable_vad": False, "buffer_ms": 100}
    )
    thread.start()
    thread.join()

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Mode 2: External Audio (You Provide Audio Frames)

Use this mode when you need full control over audio capture — for example, when reading from a custom source, a network stream, or a shared microphone. Audio frames must be **16-bit PCM, mono, 16 kHz** (`numpy.int16`).

#### `start_keyword_detection_external_audio(enable_vad=False, buffer_ms=100)`

Initializes the wake word detection engine for external audio. **Non-blocking** — after calling this, feed audio frames via `feed_audio_frame()`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_vad` | `bool` | `False` | Enable built-in Voice Activity Detection |
| `buffer_ms` | `int` | `100` | Audio buffer size in milliseconds |

#### `start_vad_external_audio()`

Initializes standalone Voice Activity Detection for external audio. After calling this, feed audio frames via `feed_audio_frame_vad()`.

#### `feed_audio_frame(audio_frame)`

Feeds a single audio frame for wake word detection.

| Parameter | Type | Description |
|-----------|------|-------------|
| `audio_frame` | `numpy.ndarray` (int16) | A single audio frame (e.g., 1280 samples at 16 kHz = 80 ms) |

Only feed frames when `keyword_model.is_listening` is `True`.

#### `feed_audio_frame_vad(audio_frame)`

Feeds a single audio frame for standalone VAD.

| Parameter | Type | Description |
|-----------|------|-------------|
| `audio_frame` | `numpy.ndarray` (int16) | A single audio frame |

**Returns:** `float` — speech probability between `0.0` and `1.0`.

Only feed frames when `keyword_model.is_listening_vad_stand_alone` is `True`.

#### `feed_audio_frame_noise_detection(audio_frame, low_noise_margin_db, high_noise_margin_db)`

Feeds a single audio frame for ambient noise level detection. This method can be called at any time (no initialization step required).

| Parameter | Type | Description |
|-----------|------|-------------|
| `audio_frame` | `numpy.ndarray` (int16) | A single audio frame |
| `low_noise_margin_db` | `int` | Lower dBFS margin for silence/noise boundary |
| `high_noise_margin_db` | `int` | Upper dBFS margin for noise/loud boundary |

**Returns:** `(dbfs, sound_type)` — a tuple of the dBFS value and a string classification (e.g., `'silence'`).

#### Full External Audio Example

See [example/example_external_audio.py](../example/example_external_audio.py) for Linux/macOS, [example_windows/example_external_audio.py](../example_windows/example_external_audio.py) for Windows.

```python
import asyncio
import threading
import pyaudio
import numpy as np
from keyword_detection import KeywordDetection

def detection_callback(params):
    phrase = params["phrase"]
    scores = [s for s in params["threshold_scores"] if s != 0]
    print(f"Detected: {phrase}  scores={scores}")

def mic_dispatcher_thread(keyword_model):
    """Reads microphone audio and dispatches frames to all detection engines."""
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1280

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                    input=True, frames_per_buffer=CHUNK)
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_frame = np.frombuffer(data, dtype=np.int16)

            # Wake word detection
            if keyword_model.is_listening:
                keyword_model.feed_audio_frame(audio_frame)

            # Standalone VAD
            if keyword_model.is_listening_vad_stand_alone:
                speech_prob = keyword_model.feed_audio_frame_vad(audio_frame)
                if speech_prob > 0.2:
                    print(f"Speech probability: {speech_prob * 100:.1f}%")

            # Noise detection
            dbfs, sound_type = keyword_model.feed_audio_frame_noise_detection(
                audio_frame, low_noise_margin_db=20, high_noise_margin_db=40
            )
            if sound_type != "silence":
                print(f"dBFS={dbfs}  sound={sound_type}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

async def main():
    models = [
        {
            "model_path": "models/your_wake_word.onnx",
            "callback_function": detection_callback,
            "threshold": 0.9,
            "buffer_cnt": 4,
            "wait_time": 50
        }
    ]

    keyword_model = KeywordDetection(keyword_models=models)

    with open("licensekey.txt") as f:
        keyword_model.set_keyword_detection_license(f.read().strip())

    # Initialize external audio detection (non-blocking)
    keyword_model.start_keyword_detection_external_audio(enable_vad=False, buffer_ms=100)

    # Initialize standalone VAD (non-blocking)
    keyword_model.start_vad_external_audio()

    # Start feeding audio in a thread
    thread = threading.Thread(target=mic_dispatcher_thread, args=(keyword_model,))
    thread.start()
    thread.join()

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Mode 3: File-Based Detection

#### `start_keyword_detection_from_file(file_path)`

Runs wake word detection on a `.wav` file (useful for testing and benchmarking).

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | `str` | Path to a `.wav` audio file |

**Returns:** `dict` — detection results keyed by model name:

```python
{
    "model_name": {
        "detections": 2,   # number of detections in the file
        ...
    }
}
```

**Example:**

```python
output = keyword_model.start_keyword_detection_from_file("test_audio.wav")
for model_name, result in output.items():
    print(f"{model_name}: {result.get('detections', 0)} detections")
```

---

## API Summary

| Method | Mode | Blocking | Description |
|--------|------|----------|-------------|
| `KeywordDetection(keyword_models=...)` | — | — | Constructor |
| `set_keyword_detection_license(key)` | — | — | Set license key |
| `set_secondary_callback(name, cb, threshold)` | — | — | Register near-detection callback |
| `start_keyword_detection(enable_vad, buffer_ms)` | Internal | Yes | Start detection with built-in mic capture |
| `start_keyword_detection_external_audio(enable_vad, buffer_ms)` | External | No | Initialize detection for external audio |
| `start_vad_external_audio()` | External | No | Initialize standalone VAD |
| `feed_audio_frame(frame)` | External | No | Feed audio for wake word detection |
| `feed_audio_frame_vad(frame)` | External | No | Feed audio for VAD; returns speech probability |
| `feed_audio_frame_noise_detection(frame, low_db, high_db)` | External | No | Feed audio for noise detection; returns `(dBFS, type)` |
| `start_keyword_detection_from_file(path)` | File | Yes | Run detection on a `.wav` file |

| Property | Type | Description |
|----------|------|-------------|
| `keyword_models_names` | `list[str]` | Loaded model names |
| `is_listening` | `bool` | Wake word detection is active |
| `is_listening_vad_stand_alone` | `bool` | Standalone VAD is active |

---

## Examples

| File | Platform | Mode |
|------|----------|------|
| [example/example.py](../example/example.py) | Linux / macOS | Internal audio |
| [example/example_external_audio.py](../example/example_external_audio.py) | Linux / macOS | External audio |
| [example_windows/example.py](../example_windows/example.py) | Windows | Internal audio |
| [example_windows/example_external_audio.py](../example_windows/example_external_audio.py) | Windows | External audio |

---

## Contact

For questions, custom wake word models, or additional platform support, contact info@davoice.io.
