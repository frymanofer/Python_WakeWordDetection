# DaVoice Text to Speech (Python)

On-device speech synthesis: natural voices in 11 languages, real-time playback with
a speech queue, stop (barge-in), WAV output, voice styles and voice cloning. Nothing
is sent to a server. It uses the same voice packs as the DaVoice React Native, iOS
and Android libraries.

Languages: `en`, `pt-BR`, `pt-PT`, `de`, `es`, `fr`, `it`, `nl`, `da`, `sv`, `el`.

## Install

Requirements: Python 3.9 to 3.13. The examples are set up for Apple Silicon Macs (M1 or newer)
and Linux x86_64 / aarch64.

```bash
cd Python_WakeWordDetection/example
./setup_voice_ai.sh --no-stt            # text to speech + the AI agent only (no 2.5 GB speech model)
source venv-voice-ai/bin/activate
```

(`./setup_voice_ai.sh` without `--no-stt` also sets up speech to text.)

To add it to your own environment instead, install the wheel for your Python and platform from
`../dist/` with an extra:

```bash
pip install "../dist/keyword_detection_lib-2.1.3-cp312-none-macosx_11_0_arm64.whl[tts-audio]"   # synthesis + speaker playback
pip install "../dist/keyword_detection_lib-2.1.3-cp312-none-macosx_11_0_arm64.whl[tts]"         # synthesis + WAV files only (servers)
```

On Linux, playback also needs the system PortAudio library (`sudo apt install libportaudio2`).

A license key is required: the same key as the wake word (`licensekey.txt`).

## Try it

```bash
python example_tts_speak.py                          # English, default voice
python example_tts_speak.py --language de --voice Kate
python example_tts_speak.py --text "Hello there."
python example_tts_speak.py --list-voices
python example_tts_speak.py --list-languages             # the languages that have a voice pack
python example_tts_speak.py --help
```

## Voice packs

Each language is one voice pack (about 160 MB), downloaded on first use and checked
against a signed manifest (size and sha256). Packs are stored in `~/.davoice`
(change it with `data_dir=` or the `DAVOICE_DATA_DIR` environment variable).

```python
from keyword_detection.tts import LanguagePacks, TextToSpeech

packs = LanguagePacks()                              # or LanguagePacks(data_dir="/path/with/space")
packs.refresh_manifest()                             # newest versions (never raises)
if not packs.is_ready("de"):
    packs.download("de", on_progress=lambda p: print(p["bytesDone"], "/", p["bytesTotal"]))
tts = TextToSpeech(packs.file_path("de", "model"), license_key=key)
packs.mark_working("de")                             # remember this version works
```

| Method | Meaning |
|---|---|
| `languages()` | the languages that have a pack |
| `is_ready(lang)` / `size_bytes(lang)` | downloaded? download size |
| `download(lang, on_progress=None)` | download now (`{"stage", "bytesDone", "bytesTotal"}`) |
| `update_in_background(lang)` | fetch a newer version without blocking; used from the next load |
| `file_path(lang, "model")` | the pack's model file; `"embedder"` for voice cloning |
| `rollback(lang)` | go back to the previous version if a new one fails to load |
| `delete(lang)` | remove the pack |

You can also pass any DaVoice `.dm` model file directly: `TextToSpeech("model.dm", license_key=key)`.

## Speak

```python
tts = TextToSpeech(model_path, license_key=key)       # or tts.set_tts_license(key)

tts.speak("Hello there.")                             # plays, returns when done
tts.speak("First sentence.", blocking=False)          # queued: returns at once
tts.speak("Second sentence.", blocking=False)         # plays after the first
tts.wait_until_done()                                 # until the queue is empty

tts.stop_speaking()                                   # stop now and drop the queue (barge-in)
tts.is_speaking()                                     # playing or queued?
tts.on_finished_speaking = lambda: print("done")      # the queue ran empty

tts.play_wav("chime.wav")                             # audio files and PCM in the same queue
tts.play_buffer(pcm, sample_rate)
tts.close()
```

For a voice assistant, call `speak(sentence, blocking=False)` for each sentence as
the reply text arrives: speech starts with the first sentence, and
`stop_speaking()` cuts it off when the user interrupts. Use headphones, or `pause()`
the speech recognizer while speaking, so the microphone doesn't hear the reply.

Output goes to the default sound device (the `[tts-audio]` extra). To send it
somewhere else, give a function that receives the audio:

```python
tts.set_audio_output(lambda pcm_float32, sample_rate: my_stream.write(pcm_float32))
tts.set_audio_output(None)                            # back to the speakers
```

## Without playback: files, buffers, streaming

```python
tts.synthesize_to_file("This goes to a file.", "out.wav")
audio = tts.synthesize("Whole sentence as one array.")      # float32 at tts.sample_rate (24 kHz)
for chunk in tts.stream("Long text, sent as it is produced."):
    send(chunk)                                             # float32 chunks, low first-audio latency
```

These need only the `[tts]` extra (no sound card), so they suit servers.

## Voices

```python
tts.get_all_voices()            # voices of this pack; the first is the default
tts.default_voice
tts.speak("Hi.", voice="Kate")  # per call; or TextToSpeech(..., default_voice="Kate")
```

### Voice styles

Some voices have style variants. List them, then switch style inside the text with
tags:

```python
tts.get_voice_abilities("Rich")     # e.g. ["angry_whisper", ..., "military_sergeant_hard", ...]
tts.speak("Okay. [drill sergeant] Give me fifty push-ups! [regular] Thanks.", voice="Rich")
```

### Clone a voice

A short, clean recording of one person becomes a voice file (`.emd`):

```python
from keyword_detection.tts import create_voice_clone

create_voice_clone("me.wav", "my_voices/Me.emd", packs.file_path("en", "embedder"),
                   volume=1.0, license_key=key)
tts.set_external_voices_path("my_voices")    # voices in this folder are listed after the bundled ones
tts.speak("Hello in my own voice.", voice="Me")
```

`tts.create_voice_clone(...)` does the same and makes the voice available at once when
the file is written into the external voices folder. `davoice_app.py` has a guided
version (choose "Clone my voice").
