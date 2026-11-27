# Example App: DaVoice Car Agent (Python)

An on-device voice assistant for a car, the Python version of the React Native example
[`example_car_agent`](https://github.com/frymanofer/ReactNative_DaVoice/tree/main/example_car_agent):
the same steps and the same screens. The whole voice pipeline runs on your computer:

- wake word detection ("Hey Coach")
- speaker verification (optional: only your voice is answered)
- real-time speech to text
- the DaVoice Automotive Agent: a small on-device language model that turns what was said into car actions
- on-device text to speech for the reply

The car is **simulated** (the drawing on the screen). This example does not control a real vehicle.

The screens open in your web browser. The browser only shows them: the microphone, the speakers and
every model are used by the Python program.

## Run it (Apple Silicon Mac or Linux)

You need an Apple Silicon Mac (M1 or newer) or Linux x86_64 / aarch64, Python 3.10 to 3.13, about
10 GB of free disk space, and headphones (so the microphone doesn't hear the replies).

```bash
cd Python_WakeWordDetection/example
./setup_voice_ai.sh                     # once: creates example/venv-voice-ai with everything this needs
source venv-voice-ai/bin/activate
python download_stt_model.py            # once: the speech model (2.5 GB); setup_voice_ai.sh already ran it

cd ../example_car_agent
python car_agent.py                     # opens http://127.0.0.1:8770 in your browser
```

macOS asks for microphone permission the first time: allow it for your terminal (or VS Code).
Press Ctrl+C in the terminal to quit.

The license key is read from `licensekey.txt` in this folder, or else `../example/licensekey.txt`
(the same key as the wake word). Use `--license-file` for another place.

## Flow

1. **Language**: pick the language for speech recognition and the voices. Every language is
   downloaded on first use (about 170 MB) and shown on the speedometer while it installs.
2. **Voice**: pick the voice that speaks the replies, play its styles, or clone a new voice
   (record about 10 seconds with the microphone, or upload a recording).
3. **Speaker verification**: create a voice signature (read 5 short sentences, then test it),
   use the saved one, or skip. With a signature, only your voice is answered and only you can
   open or unlock the doors.
4. **Wake word**: say **"Hey Coach"**. "Simulate wake word" does the same without speaking.
5. **Car agent**: speak a command: "open the windows", "set the temperature to 21",
   "take me home", "turn on the driver seat heater", "lock the car". The car drawing shows what
   changed, the card shows what was heard, the tool the agent called and the spoken reply. You can
   also tap a suggestion or type a command.

   The first start downloads the agent model (382 MB), once. The speech model is downloaded
   separately (see below).

**Back** returns to the wake-word screen; the next wake word opens the car agent again. Saying the
wake word while the agent speaks stops the reply (barge-in).

The car screen also has:

- **Parked / Driving**: some actions are refused while driving.
- **Reset**: the car and the conversation start over.
- **Settings → Local confidence** (Off, 0.80, 0.90, 0.95): the on-device model gives every car
  action a probability. When it is below the setting, the action does not run and the app says it
  needs a remote agent. A higher value means fewer wrong actions and more requests sent to the
  remote assistant (none is set up in this example).

## Where the files go

| What | Where | Change it with |
|---|---|---|
| Voice packs, agent model, cloned voices, voice signature, recordings | `~/.davoice` | `--data-dir /path/with/space` (or `DAVOICE_DATA_DIR`) |
| Speech model `davoice_stt.dm` (about 2.5 GB; `python ../example/download_stt_model.py` downloads it, and `car_agent.py` offers it when missing) | `../example/models/davoice_stt.dm` | `--stt-model /path/davoice_stt.dm` |

To keep everything on another drive:

```bash
python car_agent.py --data-dir /Volumes/MyDrive/davoice
```

## Options

```bash
python car_agent.py --help
python car_agent.py --port 8780 --no-browser       # open the page yourself
python car_agent.py --audio-file test.wav --mute   # tests: a 16 kHz mono WAV plays in as the microphone, no sound out
python car_agent.py --verbose                      # print the agent's log
python car_agent.py --list-languages               # the languages offered on the first screen
```

## What is in this folder

| Path | What |
|---|---|
| `car_agent.py` | The app: microphone, wake word, speaker verification, speech to text, the car agent, text to speech, and a small web server for the screens |
| `web/` | The screens (HTML, CSS, JavaScript; no build step). `web/car.js` draws the car |
| `stt_bias_conf/` | Car phrases the speech recognizer favors (English and Brazilian Portuguese) |

The wake word model (`hey_coach_model_28_22012026b.dm`), the speaker-verification model (`sv.dm`)
and the speech model (`davoice_stt.dm`) are shared with the other examples, in `../example/models/`.

The car itself (its state and the tool handlers) and the agent are in the library:
`keyword_detection.llm.LocalAssistant` with `demo="car"`; `assistant.car` is the simulated car.
