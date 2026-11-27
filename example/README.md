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

## Voice AI examples: wake word, speech to text, text to speech, on-device AI agent

Everything below runs on your own computer: no cloud, no per-minute fees. The examples use the
same license key as the wake word (`licensekey.txt` in this folder).

| Feature | What you get |
|---|---|
| Speech to text | Real-time, streaming, 25 European languages (or automatic language detection), a bias list for names and rare words, optional "only my voice" filtering, and a server mode where one model serves many users |
| Text to speech | Natural voices in 11 languages, real-time playback with a speech queue and barge-in, voice styles, WAV output, and voice cloning from a short recording |
| On-device AI agent | A small language model that turns requests into actions (the demo drives a simulated car), in English and Brazilian Portuguese, plus a server mode for many users |
| Wake word + speaker verification | "Hey Coach" starts listening; a voice signature makes it answer only you |

### Step 1: set up (once)

You need:

- an Apple Silicon Mac (M1 or newer), or Linux x86_64 / aarch64 (Ubuntu 20.04+, Debian 10+, RHEL 8+)
- Python 3.10 to 3.13 (3.12 is the default below) and `git`
- about 10 GB of free disk space
- headphones for the voice examples (so the microphone doesn't hear the replies)

```bash
git clone https://github.com/frymanofer/Python_WakeWordDetection.git
cd Python_WakeWordDetection/example

./setup_voice_ai.sh                  # once: creates ./venv-voice-ai, installs everything and downloads
                                     # the speech model models/davoice_stt.dm (2.5 GB)
source venv-voice-ai/bin/activate    # in every new terminal
```

Options:

```bash
./setup_voice_ai.sh python3.11           # another Python version
./setup_voice_ai.sh --no-stt             # text to speech + AI agent only (skips about 3.5 GB)
DAVOICE_GPU=1 ./setup_voice_ai.sh        # Linux with a CUDA GPU (default: the CPU build of PyTorch)
```

On Linux, the live microphone and speaker playback also need the system audio library:
`sudo apt install portaudio19-dev libportaudio2`, then `pip install pyaudio` in the venv.

> **About the speech model.** `davoice_stt.dm` (2.5 GB) is downloaded separately by
> `python download_stt_model.py`; `setup_voice_ai.sh` runs it for you. The speech examples also
> check for it when they start and offer the download when it is missing. An interrupted
> download resumes where it stopped, and the file is checked (SHA-256) before it is used;
> `python download_stt_model.py --verify` re-checks a file you already have.

### Step 2: run the complete app

```bash
python davoice_app.py
```

1. It asks for the language (type the number, or press Enter for the default). The first time,
   it downloads that language's voice pack (about 170 MB).
2. It asks for the voice. Press Enter for the default, or clone your own voice.
3. Speaker verification: choose "Create a new signature" and read the five lines it shows aloud,
   or choose "Skip".
4. It asks you to say **"Hey Coach"**. macOS asks for microphone permission the first time: allow
   it for your terminal (or VS Code).
5. It asks for the mode. Press Enter for the car demo. The first time, it downloads the AI model
   (about 0.4 GB).
6. Speak: "open all the windows", "set the temperature to 22", "lock the car". Press Ctrl+C to quit.

Shortcuts:

```bash
python davoice_app.py --mode local_ai_chat --text-input --no-wake-word --sv skip   # type instead of speaking
python davoice_app.py --language pt-BR --mode local_ai_chat                        # Brazilian Portuguese
python davoice_app.py --mode stt_only                                              # speech to text only
python davoice_app.py --mode type_to_tts                                           # type, hear it spoken
python davoice_app.py --data-dir /path/with/space                                  # where downloads go (default ~/.davoice)
python davoice_app.py --list-languages                                             # the languages
python davoice_app.py --help                                                       # every option
```

### Step 3: the individual examples

Each example is a few lines: it tells the library where its files are, and the library does the
rest. Every one has `--help`.

| Example | What it shows | Speech model needed |
|---|---|---|
| `example_car_assistant.py` | Type a command; the on-device AI agent drives a simulated car (`--speak` also says the replies) | no |
| `example_tts_speak.py` | Text to speech: languages, voices, queued playback, stop, WAV output | no |
| `example_agent_server.py` | The AI agent on a server: one loaded model answers many users, each with their own conversation | no |
| `example_stt.py` | Live speech to text from the microphone or a WAV file, with a bias list and speaker filtering | yes |
| `example_stt_server.py` | Speech to text on a server: one model transcribes many simultaneous sessions | yes |
| `example_voice_car_assistant.py` | "Hey Coach" → speech to text → car agent → spoken reply, with barge-in | yes |
| `davoice_app.py` | The complete app (step 2) | yes |
| [`../example_car_agent/`](../example_car_agent/README.md) | The car agent with screens in your web browser: language, voice, voice signature, "Hey Coach", then a live car you control by voice | yes |

```bash
python example_car_assistant.py                          # type: "open all the windows"
python example_car_assistant.py --language pt-BR --speak
python example_tts_speak.py --language de --voice Kate
python example_tts_speak.py --list-voices
python example_agent_server.py --users 6 --slots 2       # 6 users at once on one model
python example_stt.py                                    # microphone, English
python example_stt.py --file recording.wav --locale es-ES
python example_stt.py --list-languages                   # the 25 speech-to-text languages
python example_stt_server.py --files a.wav b.wav c.wav   # 3 simultaneous sessions
python example_voice_car_assistant.py                    # say: "Hey Coach ... set the temperature to 22"
```

The car assistant understands English and Brazilian Portuguese. Try: "open all the windows",
"set the temperature to 22", "lock the car", "turn on the seat heating", "play some jazz".

### Where the files go

| What | Where | Change it with |
|---|---|---|
| Speech model `davoice_stt.dm` (2.5 GB) | `models/` in this folder | `--stt-model /path/davoice_stt.dm` (or `download_stt_model.py --dest`) |
| Wake word (`hey_coach_model_28_22012026b.dm`) and speaker verification (`sv.dm`) models | `models/` in this folder | the examples' options (`--help`) |
| Voice packs (about 170 MB each), the AI model (about 0.4 GB), cloned voices, voice signatures | `~/.davoice` | `--data-dir /path` or the `DAVOICE_DATA_DIR` environment variable |

Models are read straight from the `.dm` files into memory; nothing is unpacked to disk.

### Use it in your own code

- Speech to text (one user, and a server for many): [README_STT.md](README_STT.md)
- Text to speech (voice packs, playback, files, voices, cloning, streaming server): [README_TTS.md](README_TTS.md)
- The AI agent:

```python
from keyword_detection.llm import LocalAssistant

license_key = open("licensekey.txt").read().strip()
assistant = LocalAssistant(license_key, language="en", demo="car")
assistant.warm_up()                                  # downloads the model the first time
reply = assistant.ask("open all the windows")        # the agent calls the car's tools
print(reply["text"], assistant.car.state["windows"])
```

### Troubleshooting

| Problem | What to do |
|---|---|
| `No keyword_detection_lib wheel for ...` | Use Python 3.10 to 3.13 on an Apple Silicon Mac or Linux x86_64 / aarch64, and run the script from this folder |
| The microphone hears nothing (macOS) | System Settings → Privacy & Security → Microphone: allow your terminal (or VS Code), then restart it |
| The assistant answers itself | Use headphones |
| `not enough disk space` while downloading | `python download_stt_model.py --dest /path/with/space`, then `--stt-model /path/with/space/davoice_stt.dm`; `--data-dir` for the rest |
| `License key ... expired` | The demo key in `licensekey.txt` is valid until 2026-12-31. Contact info@davoice.io for a key |

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
For detailed references or specific benchmark results, please contact us at info@davoice.io.

## Links

Here are wakeword detection GitHub links per platform:

- **Web / JS / Angular / React:** https://github.com/frymanofer/Web_WakeWordDetection/tree/main
- **For React Native:** [ReactNative_WakeWordDetection](https://github.com/frymanofer/ReactNative_WakeWordDetection)
- **For Android:** [KeywordsDetectionAndroidLibrary](https://github.com/frymanofer/KeywordsDetectionAndroidLibrary)
- **For iOS framework:** 
  - With React Native bridge: [KeyWordDetectionIOSFramework](https://github.com/frymanofer/KeyWordDetectionIOSFramework)
  - Sole Framework: [KeyWordDetection](https://github.com/frymanofer/KeyWordDetection)
