# DaVoice Speech to Text (Python)

On-device speech recognition for 25 European languages. Audio never leaves the
machine. The recognizer is streaming, with partial results while the user speaks, a per-session bias list for names and
rare words, and optional speaker filtering (transcribe only enrolled voices).

There are two ways to use it:

| | `SpeechToText` (one user) | `STTServer` (many users) |
|---|---|---|
| Use it for | an app, a device, a kiosk: one microphone | a server that transcribes many connections at once |
| Sessions | one at a time | any number at once, one model shared by all |
| Sentence end | automatic (voice activity detection) | decided by your code: `finish()` |
| Speaker filtering | yes | no |
| Example | `example_stt.py` | `example_stt_server.py` |

Both give exactly the same text for the same audio and settings.

Languages: `bg cs da de el en es et fi fr hr hu it lt lv mt nl pl pt ro ru sk sl sv uk`,
or `auto` (the model detects the language). Locales such as `en-US` or `de_DE` are accepted;
`python example_stt.py --list-languages` prints them with their names.

## Install

Requirements: Python 3.10 to 3.13 on an Apple Silicon Mac (M1 or newer, macOS 11+) or on
Linux x86_64 / aarch64 (glibc 2.28+: Ubuntu 20.04+, Debian 10+, RHEL 8+). About 6 GB of free disk
space (packages + the 2.5 GB model) and 4 GB of free RAM.

```bash
cd Python_WakeWordDetection/example
./setup_voice_ai.sh                  # once: venv + the speech-recognition runtime + the library
                                     # + the speech model (runs download_stt_model.py)
source venv-voice-ai/bin/activate
```

`setup_voice_ai.sh` installs the speech recognition runtime (a pinned version), then the
library wheel for your platform from `../dist/` with the `[app]` extra. On Linux it installs the
CPU build of PyTorch first (run `DAVOICE_GPU=1 ./setup_voice_ai.sh` on a machine with a CUDA
GPU). For the live microphone you also need PyAudio: `pip install pyaudio` (on Linux first
`sudo apt install portaudio19-dev`). Transcribing WAV files and the server need no sound card.

The speech model is one file, `davoice_stt.dm` (about 2.5 GB). Download it once:

```bash
python download_stt_model.py            # saves models/davoice_stt.dm; skipped if it is already there
python download_stt_model.py --verify   # re-checks the SHA-256 of the file you have
python download_stt_model.py --dest /path/with/space
```

`setup_voice_ai.sh` runs it for you, and the examples offer the download when the file is
missing. An interrupted download resumes where it stopped. Its license notice is saved next to it
(`models/davoice_stt_NOTICES.md`). The library itself never downloads the model.

The examples load it from `models/davoice_stt.dm`, next to the wake word models
(`--stt-model` for another path). In your own code pass `SpeechToText(model="path/davoice_stt.dm")`;
without it the library looks at the `DAVOICE_STT_MODEL` environment variable, then
`~/.davoice/stt/davoice_stt.dm`. It is loaded in memory; nothing is unpacked to disk.

A license key is required: the same key as the wake word (`licensekey.txt`).

## Try it

Both examples use `models/davoice_stt.dm`, `licensekey.txt` and the bias list
`stt_bias_conf/words_flattened.txt` from this folder; no option is needed to start.

```bash
python example_stt.py --list-languages                     # the 25 languages and their locale codes
python example_stt.py                                      # microphone, English
python example_stt.py --locale de-DE                       # microphone, German (or --locale auto)
python example_stt.py --file recording.wav --locale es-ES  # a WAV file instead of the microphone
python example_stt.py --speaker me=sv_enrollment.json      # only transcribe this voice

python example_stt_server.py --files a.wav b.wav c.wav     # 3 simultaneous clients
python example_stt_server.py --files a.wav --clients 8     # 8 clients (files repeat)
```

`example_stt.py` prints `... text so far` while you speak and `FINAL: text` at the end of
each sentence. The live microphone needs PyAudio (`pip install pyaudio`); `--file` does not.

| `example_stt.py` option | Default | Meaning |
|---|---|---|
| `--locale` | `en-US` | the language (`--list-languages`), or `auto` |
| `--file` | microphone | transcribe a WAV file (other sample rates are resampled) |
| `--bias-file` | `stt_bias_conf/words_flattened.txt` | names and rare words to favor; `''` turns it off |
| `--bias-strength` | 2.0 | higher favors the list more (and risks false hits) |
| `--speaker ID=JSON` | none | an enrolled voice (repeat for several); then only those voices are transcribed |
| `--speaker-model` | `models/sv.dm` | the speaker-verification model |
| `--device` | `auto` | `mps` (Apple GPU), `cpu`, `cuda` |
| `--performance` | `auto` | `low_latency`, `balanced` or `efficient` (see "Speed and latency settings") |
| `--max-latency` | none | an upper limit in seconds for `auto` |
| `--stt-model` | `models/davoice_stt.dm` | another speech model file |
| `--list-languages` | | list the languages and exit (also `--lang-list`, `--locale-list`) |

`example_stt_server.py`: each WAV file plays one client; the clients start half a second
apart and stream in real time; one model transcribes all of them. It prints every
client's text, then a summary with the processing delay per chunk (p50 / p95): the
number of clients is sustainable while p95 stays under the chunk length (560 ms).

| `example_stt_server.py` option | Default | Meaning |
|---|---|---|
| `--files` | required | 16 kHz mono 16-bit WAV files, one per client (`../resampleTo16kHZ.sh` converts others) |
| `--clients` | one per file | number of simultaneous clients |
| `--locale` | `auto` | one language for every session (`--list-languages`) |
| `--threads` | 4 | CPU threads for this server process |
| `--chunk` / `--right` | 0.56 / 0.56 | 1.04: less CPU per session, text later; shared by all sessions |
| `--device` | `cpu` | `cuda` should work but is not tested yet |
| `--bias-file` | `stt_bias_conf/words_flattened.txt` | bias list for every session (`''` for none) |
| `--fast` | off | push audio as fast as possible: measures throughput (the delay numbers are then not meaningful) |
| `--license-file` | `licensekey.txt` | the license key file |
| `--stt-model` | `models/davoice_stt.dm` | another speech model file |
| `--list-languages` | | list the languages and exit |

---

## One user: `SpeechToText`

```python
from keyword_detection import SpeechToText

stt = SpeechToText(
    model="models/davoice_stt.dm",
    locale="en-US",
    bias_file_path="stt_bias_conf/words_flattened.txt",
    on_speech_partial_results=lambda e: print("...", e["value"][0]),
    on_speech_results=lambda e: print("FINAL:", e["value"][0]),
)
stt.set_stt_license(open("licensekey.txt").read().strip())
stt.load()          # optional: load the model now instead of on start
stt.start()         # microphone
...
stt.stop()          # finishes the current sentence; keeps the bias list and speakers
stt.destroy()       # also frees the model
```

### Audio input (pick one)

| Method | Audio |
|---|---|
| `start(locale=None, input_device_index=None)` | the microphone (needs PyAudio) |
| `start_external_audio(locale=None)` then `feed_audio_frame(frame)` for every frame | your own audio: 16 kHz, mono, int16, exactly 1280 samples (80 ms) per frame, as a numpy array or bytes |
| `transcribe_file(path, locale=None)` | a WAV file; returns the final results as a list (callbacks fire too). Other sample rates are resampled. |

`pause()` makes the recognizer hear silence until `unpause()` (for example while
your app is speaking).

### Events

Each callback gets one dictionary. They run on the STT worker thread, in order:
keep them short.

| Callback | When | Payload |
|---|---|---|
| `on_speech_start` | a sentence starts | `{}` |
| `on_speech_partial_results` | the text so far changed | `{"value": [text]}` |
| `on_speech_results` | the sentence is final | `{"value": [text]}` |
| `on_speech_end` | right after the final result | `{}` |
| `on_speech_error` | something failed | `{"error": {"code": ..., "message": ...}}` |

While speakers are enrolled, the text payloads also have `"speaker_ids"` (every
verified speaker of the sentence) and `"speaker_id"` (the latest).

### When a sentence ends

A voice activity detector opens the recognizer when someone speaks. The sentence is
final after `vad_keep_alive_ms` (700) of no voice plus `end_of_utterance_ms` (500) of
silence, so about 1.2 s after the user stops talking.

| Option | Default | Meaning |
|---|---|---|
| `end_of_utterance_ms` | 500 | silence that ends a sentence |
| `vad_threshold` | 0.3 | speech probability that counts as voice |
| `vad_keep_alive_ms` | 700 | how long the input stays open after the last voice |
| `vad_gate` | True | False sends all audio to the recognizer |

### Bias list (names, products, rare words)

Phrases on the list are favored when the audio is close to them. Without a list,
"Mirenzo" may come out as "My Renzo"; with it, "Mirenzo".

The file format is the same as in the React Native, iOS and Android libraries
(`words_flattened.txt`): one phrase per line, a trailing comma is allowed,
comma-separated phrases on one line work too, quotes and empty lines are ignored.

```
Mirenzo,
DaVoice,
A for Alpha,
```

| Option / method | Meaning |
|---|---|
| `bias_file_path=` / `set_bias_file(path)` | load a list file |
| `bias_phrases=` / `set_bias_phrases([...])` | a Python list; `[]` turns biasing off |
| `set_bias_text(text)` | the file's content as a string |
| `bias_strength` | 2.0; higher favors the phrases more (and risks false hits) |
| `bias_case_insensitive` | False: matching is case-sensitive, and each phrase is also added with a capital first letter ("apixaban" -> "Apixaban") so it matches at the start of a sentence. True: case-insensitive matching |

Changes apply from the next sentence.

### Speaker filtering

Enroll a voice once (`speaker_id_onboarding.py`, or the onboarding in
`davoice_app.py`), which writes an enrollment JSON file. With speakers added, only
their speech is transcribed and each result says who spoke.

```python
stt = SpeechToText(speaker_model_path="models/sv.dm", ...)
stt.set_stt_license(key)
stt.add_speaker("alice", "sv_enrollment.json")  # JSON text or a path; applies immediately
stt.set_speakers([{"id": "a", "json": "a.json"}, {"id": "b", "json": "b.json"}])
stt.remove_speaker("a")                          # removing the last one turns filtering off
stt.get_speaker_ids()
```

### Speed and latency settings

By default (`performance="auto"`) the library measures this machine when the model
loads and picks the lowest-latency setting that runs at least 1.5x faster than real
time. Anything you set yourself is used as given.

| Option | Default | Meaning |
|---|---|---|
| `performance` | `"auto"` | `"auto"`, or a preset: `"low_latency"`, `"balanced"`, `"efficient"` |
| `device` | `"auto"` | `"cuda"`, `"mps"` (Apple GPU), `"cpu"`; auto picks in that order |
| `chunk_secs` | auto | audio per decoding step: the main speed/latency knob |
| `right_context_secs` | 0.56 | look-ahead per step |
| `left_context_secs` | 5.6 | past audio the model sees; keep it (shorter lowers accuracy) |
| `num_threads` | auto | CPU threads; on Apple Silicon the performance cores |
| `compute_dtype` | auto | `bfloat16` on CUDA, `float32` elsewhere |
| `max_latency_secs` | none | an upper limit for auto |

| Preset | chunk | Text appears after about | Cost |
|---|---|---|---|
| `low_latency` | 0.56 s | 1.1 s | 1x |
| `balanced` | 1.12 s | 1.7 s | ~0.5x |
| `efficient` | 2.0 s | 2.6 s | ~0.35x |

```python
stt.get_runtime_settings()                         # what is in use, and how it was chosen
stt.set_runtime_settings(performance="balanced")   # applied between sentences
stt.benchmark_runtime()                            # measure the candidates on this machine
```

Measured on an Apple M4: Apple GPU about 2x real time at `low_latency`, CPU (4
performance cores) about 1x.

---

## Many users: `STTServer`

One process holds one copy of the model and serves any number of sessions. Every
0.56 s it takes the sessions that have new audio and decodes them together in one
batch, so N sessions cost far less than N separate recognizers, and memory stays
at one model.

```python
from keyword_detection.stt import STTServer, load_bias_phrases

def on_event(session_id, kind, text, user):
    # kind: "partial" (text so far) or "final". Runs on the server thread: keep it short,
    # e.g. loop.call_soon_threadsafe(connections[user].put_nowait, (kind, text))
    print(user, kind, text)

server = STTServer(on_event=on_event, license_key=key, model="models/davoice_stt.dm",
                   device="cpu", num_threads=4)
server.start()                                   # loads the model

# for each connection / request:
sid = server.open_stream(language="en-US",       # or "auto"
                         phrases=load_bias_phrases("words_flattened.txt"),   # optional, per session
                         user=connection_id)     # any object; comes back with every event
server.push(sid, audio_float32)                  # 16 kHz mono float32 in [-1, 1], any length, any thread
...
server.finish(sid)                               # end of the utterance -> one "final" event
# or server.close_stream(sid) to drop it without a result

server.stop()
```

What differs from `SpeechToText`:

* **One session is one utterance.** Your code decides where it ends (end of a request,
  push-to-talk released, your own voice activity detection) and calls `finish()`.
  Open a new session for the next utterance.
* Each session has its own language and bias list (handled like `SpeechToText`'s,
  including `case_insensitive=`). **Speed settings are shared**: one
  `chunk_secs` / `right_context_secs` for every session of a server.
* No speaker filtering in server mode.
* `push()`, `finish()`, `open_stream()` and `close_stream()` can be called from any
  thread. Decoding happens on the server's own thread.

`STTServer` options (the same for `BatchedStreamingRecognizer`, which is the engine
without the thread):

| Option | Default | Meaning |
|---|---|---|
| `license_key` | required | or `server.set_stt_license(key)` before `start()` |
| `model` | `DAVOICE_STT_MODEL`, else `~/.davoice/stt/davoice_stt.dm` | the speech model file |
| `device` | `"cpu"` | `"cpu"` is tested; `"cuda"` should work but is not tested yet |
| `num_threads` | torch default | CPU threads for this process |
| `max_batch` | 16 | most sessions decoded in one step |
| `chunk_secs`, `right_context_secs` | 0.56, 0.56 | see below |
| `record_latency` | False | True: `server.recognizer.latencies` gets the delay of every chunk |

### Choosing the chunk size

Use one of these settings.

| `chunk_secs` / `right_context_secs` | Text appears after about | CPU per session (relative) |
|---|---|---|
| 0.56 / 0.56 (default) | 1.1 s + processing | 1x |
| 1.04 / 0.56 | 1.6 s + processing | ~0.7x |
| 1.04 / 1.04 | 2.1 s + processing | ~0.6x |

### Sizing a CPU server

* Run several server processes, each with its own `STTServer` and `num_threads` set
  to the cores you give it (for example 4 processes x 4 threads on a 16-core machine),
  and send each new connection to the least busy process. Several smaller processes
  usually do better than one process with all the cores; measure both on your machine.
* Each process holds one model: about 2.5 GB of RAM.
* A process keeps up while its decoding delay stays below the chunk length. Watch it
  with `record_latency=True`: the 95th percentile of `server.recognizer.latencies`
  must stay under `chunk_secs` (0.56 s by default). `example_stt_server.py` prints it.
* Measured on Apple M4 performance cores (with other work running, so only a rough
  guide): about 0.6 core-seconds of CPU per second of audio per session at the
  default chunk, about 0.4 with 1.04 s chunks. Measure on your own server type before
  deciding how many sessions a machine takes: `example_stt_server.py --files ... --clients N`.
