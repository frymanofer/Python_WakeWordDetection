#!/usr/bin/env python3
"""DaVoice Car Agent (Python): an on-device voice assistant for a simulated car.

The Python version of the React Native example `example_car_agent`, with the same
steps and the same screens, shown in your browser:

  1. Language: pick the language; its voice pack downloads on first use (~170 MB).
  2. Voice: pick the voice that speaks the replies, or clone a new one.
  3. Speaker verification: create a voice signature (then only you are answered),
     use the saved one, or skip.
  4. Wake word: say "Hey Coach".
  5. Car agent: speak a command ("open the windows", "set the temperature to 21").
     The first start downloads the agent model (382 MB).

Everything runs on this computer: the microphone and the speakers are used by this
Python process, the browser only shows the screens. The car is simulated; nothing
here controls a real vehicle.

    python car_agent.py                       # opens http://127.0.0.1:8770 in your browser
    python car_agent.py --data-dir /path/with/space
    python car_agent.py --help

See README.md.
"""
import argparse
import json
import mimetypes
import os
import queue
import re
import sys
import threading
import time
import traceback
import wave
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import numpy as np

from keyword_detection import KeywordDetection, SpeakerVerification
from keyword_detection.app_languages import APP_LANGUAGES, ORIGINAL_TTS_VOICES, get_language
from keyword_detection.llm import LocalAssistant, split_completed_sentences
from keyword_detection.llm.remote import DID_NOT_CATCH, is_bare_done
from keyword_detection.stt import SpeechToText
from keyword_detection.tts import LanguagePacks, TextToSpeech

HERE = Path(__file__).resolve().parent
WEB = HERE / "web"
RN_DATA = json.loads((WEB / "data" / "rn_data.json").read_text(encoding="utf-8"))

SAMPLE_RATE = 16000
FRAME = 1280                       # 80 ms: the wake word and the speech recognizer take these frames
WAKE_PHRASE = "Hey Coach"
WAKE_WORD_SETTINGS = {"threshold": 0.999, "buffer_cnt": 3, "wait_time": 1000}   # the React Native app's
SPEAKER_ID = "owner"
SIGNATURE_SAMPLES = 5
SIGNATURE_SAMPLE_SECONDS = 5.0     # the longest sentence takes about 5 s to read
CLONE_RECOMMENDED_SECONDS = 10
CLONE_MAX_SECONDS = 30
CONFIDENCE_CHOICES = [0.0, 0.80, 0.90, 0.95]        # "Local confidence": Off, 0.80, 0.90, 0.95


def log(*args):
    print(time.strftime("%H:%M:%S"), *args, flush=True)


# ---------------------------------------------------------------------------------------------------
# Shared UI state: the browser gets the whole state (JSON) every time it changes (server-sent events).
class Hub:
    def __init__(self):
        self._state = {}
        self._version = 0
        self._cond = threading.Condition()

    def set(self, **values):
        with self._cond:
            self._state.update(values)
            self._version += 1
            self._cond.notify_all()

    def patch(self, key, **values):
        with self._cond:
            self._state[key] = dict(self._state.get(key) or {}, **values)
            self._version += 1
            self._cond.notify_all()

    def get(self, key, default=None):
        with self._cond:
            return self._state.get(key, default)

    def snapshot(self):
        with self._cond:
            return json.dumps(self._state)

    def wait(self, version, timeout=15.0):
        with self._cond:
            self._cond.wait_for(lambda: self._version != version, timeout)
            return self._version, json.dumps(self._state)


# ---------------------------------------------------------------------------------------------------
class Microphone:
    """One 16 kHz mono int16 input, 80 ms frames, handed to every consumer (wake word, speech
    recognizer, voice signature, voice-clone recording). `audio_file` plays a 16 kHz mono WAV in
    instead of the microphone (tests): it waits while the app holds the input."""

    def __init__(self, audio_file=None):
        self.consumers = []
        self._frames = queue.Queue(maxsize=200)
        self._file = audio_file
        self._open = threading.Event()
        if not audio_file:      # a recording waits for the wake-word screen (release())
            self._open.set()
        self._stream = None
        self._running = False

    def hold(self):
        self._open.clear()

    def release(self):
        self._open.set()

    def start(self):
        self._running = True
        threading.Thread(target=self._pump, daemon=True).start()
        if self._file:
            threading.Thread(target=self._play_file, daemon=True).start()
            return
        import sounddevice as sd

        def callback(indata, frames, time_info, status):
            try:
                self._frames.put_nowait(indata[:, 0].copy())
            except queue.Full:
                pass

        self._stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16", blocksize=FRAME,
                                      callback=callback)
        self._stream.start()

    def _play_file(self):
        with wave.open(str(self._file), "rb") as wf:
            if wf.getframerate() != SAMPLE_RATE or wf.getnchannels() != 1 or wf.getsampwidth() != 2:
                log(f"--audio-file must be 16 kHz mono 16-bit: {self._file}")
                return
            audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        audio = np.concatenate([audio, np.zeros(SAMPLE_RATE * 3, np.int16)])
        for i in range(0, len(audio) - FRAME + 1, FRAME):
            self._open.wait()
            self._frames.put(audio[i:i + FRAME].copy())
            time.sleep(FRAME / SAMPLE_RATE)
        log("[mic] the audio file finished; silence from now on")
        while self._running:
            self._open.wait()
            self._frames.put(np.zeros(FRAME, np.int16))
            time.sleep(FRAME / SAMPLE_RATE)

    def _pump(self):
        while self._running:
            try:
                frame = self._frames.get(timeout=0.5)
            except queue.Empty:
                continue
            for consumer in list(self.consumers):
                try:
                    consumer(frame)
                except Exception as exc:
                    log(f"[mic] consumer failed: {exc}")

    def stop(self):
        self._running = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()


class FrameStream:
    """Microphone frames as a PyAudio-style stream with read(), for speaker verification."""

    def __init__(self):
        self._frames = queue.Queue()
        self.closed = threading.Event()

    def feed(self, frame):
        self._frames.put(frame)

    def drain(self):
        while not self._frames.empty():
            try:
                self._frames.get_nowait()
            except queue.Empty:
                break

    def read(self, frame_count, exception_on_overflow=False):
        while not self.closed.is_set():
            try:
                return self._frames.get(timeout=0.5).tobytes()
            except queue.Empty:
                continue
        raise EOFError("stream closed")


class SentenceSpeaker:
    """Speaks a streamed reply sentence by sentence: each complete sentence is queued at once."""

    def __init__(self, tts, voice, language):
        self.tts, self.voice, self.language, self._buffer = tts, voice, language, ""

    def feed(self, delta):
        self._buffer += delta
        done, self._buffer = split_completed_sentences(self._buffer)
        for sentence in done:
            self.say(sentence)

    def say(self, text):
        text = (text or "").strip()
        if is_bare_done(text):     # the car demo never confirms with a bare "Done."
            text = DID_NOT_CATCH.get(self.language, DID_NOT_CATCH["en"])
        if text:
            self.tts.speak(text, voice=self.voice, blocking=False)

    def flush(self):
        rest, self._buffer = self._buffer, ""
        self.say(rest)


def strip_wake_word(text):
    """The recognizer hears the wake word too: "Hey Coach, open the windows" -> "open the windows"."""
    wake = {w.lower() for w in WAKE_PHRASE.split()}
    words = text.split()
    while words and re.sub(r"[^\w]", "", words[0].lower()) in wake:
        words.pop(0)
    return " ".join(words).strip()


def safe_name(name):
    return re.sub(r"[^\w\- ]+", "", name or "", flags=re.UNICODE).strip()[:40]


# ---------------------------------------------------------------------------------------------------
class CarAgentApp:
    def __init__(self, args):
        self.args = args
        self.hub = Hub()
        self.license_key = Path(args.license_file).expanduser().read_text(encoding="utf-8").strip()
        self.data_dir = Path(args.data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.signature_path = self.data_dir / "sv_enrollment.json"
        # The speech model file: ../example/download_stt_model.py downloads it (main() offers it).
        self.stt_model = Path(args.stt_model).expanduser()
        self.mic = Microphone(args.audio_file)
        self.packs = LanguagePacks(data_dir=str(self.data_dir), local_dirs=list(args.models_dir or []))
        self.language = None
        self.tts = None
        self.voice = None
        self.voices_dir = None
        self.enrollment = None          # the voice signature JSON text when speaker verification is on
        self.kd = None
        self.stt = None
        self.assistant = None
        self.confidence = 0.0
        self._install_token = 0
        self._recording = None          # voice clone: {"frames": [...], "stop": Event}
        self._clone_sample = None       # path of the recording / uploaded file
        self._clone_volume = 100
        self._signature_stream = None
        self._voice_test_stream = None
        self._listening = False         # the speech recognizer gets the microphone (car screen)
        self._turns = queue.Queue()
        self._busy = threading.Lock()   # one action at a time for the slow steps
        threading.Thread(target=self._turn_worker, daemon=True).start()

    # ---- start ---------------------------------------------------------------------------------
    def start(self):
        log(f"[packs] {self.packs.refresh_manifest()}")
        log(f"[stt] speech model: {self.stt_model} ({'found' if self.stt_model.is_file() else 'NOT FOUND: run python ../example/download_stt_model.py'})")
        self.mic.start()
        self.show_language_screen()

    def show_language_screen(self):
        languages = []
        for x in APP_LANGUAGES:
            if x.get("hidden"):
                continue
            name = x["label"].split(" (")[0]
            try:
                size_mb = round(self.packs.size_bytes(x["id"]) / 1e6)
            except Exception:
                size_mb = 0
            languages.append({"id": x["id"], "code": x["id"].upper(), "name": name, "shortName": name.split(" ")[0],
                              "sizeMB": size_mb, "installed": bool(self.packs.is_ready(x["id"]))})
        default = "pt-BR" if any(x["id"] == "pt-BR" for x in languages) else languages[0]["id"]
        self.hub.set(screen="language", languages=languages, defaultLanguage=self.language or default,
                     wakePhrase=WAKE_PHRASE)

    # ---- 1. language + install -------------------------------------------------------------------
    def a_install(self, body):
        language = get_language(body["id"])["id"]
        self.language = language
        self._install_token += 1
        token = self._install_token
        lang = next(x for x in self.hub.get("languages") if x["id"] == language)
        self.hub.set(screen="install", install={"name": lang["name"], "code": lang["code"], "sizeMB": lang["sizeMB"],
                                                "pct": 0, "mbDone": 0, "mbTotal": lang["sizeMB"], "stage": None,
                                                "installed": False, "error": None})
        threading.Thread(target=self._install, args=(language, token), daemon=True).start()

    def _install(self, language, token):
        def progress(p):
            if token != self._install_token:
                return
            total = max(1, p.get("bytesTotal") or 1)
            self.hub.patch("install", stage=p.get("stage"), pct=int(100 * p.get("bytesDone", 0) / total),
                           mbDone=round(p.get("bytesDone", 0) / 1e6), mbTotal=round(total / 1e6))

        try:
            if not self.packs.is_ready(language):
                self.packs.download(language, on_progress=progress)
            else:
                self.packs.update_in_background(language)
            if token != self._install_token:
                return
            self.hub.patch("install", stage="verify", pct=100)
            self._load_tts(language)
            if token == self._install_token:
                self.hub.patch("install", installed=True, pct=100)
        except Exception as exc:
            log(f"[install] failed: {exc}")
            if token == self._install_token:
                self.hub.patch("install", error=f"The voice pack could not be installed: {exc}")

    def _load_tts(self, language):
        if self.tts is not None:
            self.tts.close()
            self.tts = None
        model = str(self.packs.file_path(language, "model"))
        try:
            tts = TextToSpeech(model, license_key=self.license_key)
        except Exception:
            if not self.packs.rollback(language):
                raise
            tts = TextToSpeech(str(self.packs.file_path(language, "model")), license_key=self.license_key)
        self.packs.mark_working(language)
        if self.args.mute:
            tts.set_audio_output(lambda pcm, rate: None)
        self.voices_dir = self.data_dir / "cloned_voices" / language
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        tts.set_external_voices_path(str(self.voices_dir))
        self.tts = tts
        self.voice = ORIGINAL_TTS_VOICES.get(language) or tts.default_voice or (tts.get_all_voices() or [None])[0]

    def a_cancelInstall(self, body):
        self._install_token += 1          # the download finishes in the background and is kept
        self.show_language_screen()

    def a_retryInstall(self, body):
        self.a_install({"id": self.language})

    def a_installContinue(self, body):
        self.show_voice_screen()

    # ---- 2. voice ------------------------------------------------------------------------------------
    def _cloned(self):
        return sorted(p.stem for p in self.voices_dir.glob("*.emd"))

    def _examples(self, voice):
        abilities = self.tts.get_voice_abilities(voice) or []
        first, last = ["military_sergeant_hard", "whisper"], ["disappointed"]

        def rank(a):
            a = a.lower()
            return first.index(a) - len(first) if a in first else (1 + last.index(a) if a in last else 0)

        out = []
        for ability in sorted(abilities, key=rank):
            example = (RN_DATA["styleExamples"].get(ability.lower()) or {}).get(self.language)
            if not example:
                words = ability.replace("_", " ").strip()
                example = {"label": words[:1].upper() + words[1:], "text": f"[{words}] Hello! This is my voice in this style."}
            out.append({"ability": ability, **example})
        return out

    def show_voice_screen(self):
        voices = self.tts.get_all_voices()
        cloned = self._cloned()
        original = ORIGINAL_TTS_VOICES.get(self.language)
        original = original if original in voices else None
        abilities = {v: self.tts.get_voice_abilities(v) or [] for v in voices if v not in cloned}
        expressive = [{"name": v, "styles": len(a)} for v, a in abilities.items() if a]
        example_voice = self.voice if abilities.get(self.voice) else (expressive[0]["name"] if expressive else None)
        self.hub.set(screen="voice", voice={
            "expressive": expressive, "originalVoice": original,
            "builtIn": [v for v in voices if v not in cloned and not abilities.get(v) and v != original],
            "cloned": cloned, "selected": self.voice, "exampleVoice": example_voice,
            "examples": self._examples(example_voice)[:3] if example_voice else [], "playing": None})

    def a_selectVoice(self, body):
        self.voice = body["voice"]
        self.show_voice_screen()

    def a_playExample(self, body):
        voice = self.hub.get("voice", {}).get("exampleVoice")
        self.tts.stop_speaking()
        self.hub.patch("voice", playing=body["text"])
        self.tts.speak(body["text"], voice=voice, blocking=True)
        if self.hub.get("voice", {}).get("playing") == body["text"]:
            self.hub.patch("voice", playing=None)

    def a_deleteCloned(self, body):
        name = body["voice"]
        if name in self._cloned():
            (self.voices_dir / f"{name}.emd").unlink(missing_ok=True)
            self._load_tts_voices_again()
            if self.voice == name:
                self.voice = self.tts.default_voice
        self.show_voice_screen()

    def _load_tts_voices_again(self):
        self.tts.set_external_voices_path(str(self.voices_dir))

    def a_voiceContinue(self, body):
        self.show_speaker_screen()

    # ---- 2b. clone a voice ----------------------------------------------------------------------------
    def a_openClone(self, body):
        self._clone_sample, self._clone_volume = None, 100
        self.hub.set(screen="clone", clone={
            "source": "mic", "readingText": RN_DATA["cloneReadingTexts"].get(self.language, ""),
            "recommendedSeconds": CLONE_RECOMMENDED_SECONDS, "maxSeconds": CLONE_MAX_SECONDS,
            "recording": False, "recordSeconds": 0, "peak": 0, "sample": None, "volume": 100,
            "busy": False, "error": None, "result": None, "folder": str(self.voices_dir)})

    def a_cloneSource(self, body):
        self.hub.patch("clone", source=body["source"], error=None)

    def a_toggleRecording(self, body):
        if self._recording is not None:
            self._recording["stop"].set()
            return
        rec = {"frames": [], "stop": threading.Event()}
        self._recording = rec
        self.hub.patch("clone", recording=True, recordSeconds=0, peak=0, error=None, result=None)

        def capture(frame):
            rec["frames"].append(frame.copy())
            seconds = len(rec["frames"]) * FRAME / SAMPLE_RATE
            if len(rec["frames"]) % 3 == 0:
                self.hub.patch("clone", recordSeconds=round(seconds, 1),
                               peak=float(np.abs(frame).max()) / 32768.0)
            if seconds >= CLONE_MAX_SECONDS:
                rec["stop"].set()

        self.mic.consumers.append(capture)
        rec["stop"].wait()
        self.mic.consumers.remove(capture)
        self._recording = None
        audio = np.concatenate(rec["frames"]) if rec["frames"] else np.zeros(0, np.int16)
        if audio.size < SAMPLE_RATE * 3:
            self.hub.patch("clone", recording=False, error="The recording is too short: read for about 10 seconds.")
            return
        out = self.data_dir / "clone_recordings" / f"recording_{int(time.time())}.wav"
        out.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio.tobytes())
        self._clone_sample = out
        self.hub.patch("clone", recording=False, sample=f"Recording · {audio.size / SAMPLE_RATE:.0f} s")

    def upload(self, filename, data):
        name = safe_name(Path(filename).stem) or "upload"
        suffix = Path(filename).suffix.lower()[:6] or ".wav"
        out = self.data_dir / "clone_uploads" / f"{name}{suffix}"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
        self._clone_sample = out
        self.hub.patch("clone", sample=Path(filename).name, error=None, result=None)

    def a_playSample(self, body):
        if self._clone_sample:
            self.tts.stop_speaking()
            self.tts.play_wav(str(self._clone_sample))

    def a_cloneVolume(self, body):
        self._clone_volume = int(min(200, max(50, self._clone_volume + int(body["step"]))))
        self.hub.patch("clone", volume=self._clone_volume)

    def a_createClone(self, body):
        name = safe_name(body.get("name"))
        if not name:
            self.hub.patch("clone", error="Give the voice a name.")
            return
        if not self._clone_sample:
            self.hub.patch("clone", error="Record yourself or choose a file first.")
            return
        self.hub.patch("clone", busy=True, error=None, result=None)
        try:
            info = self.tts.create_voice_clone(str(self._clone_sample), str(self.voices_dir / f"{name}.emd"),
                                               str(self.packs.file_path(self.language, "embedder")),
                                               volume=self._clone_volume / 100.0)
            self.hub.patch("clone", busy=False, result={"voice": info["voice"], "weak": bool(info.get("warnings"))})
        except Exception as exc:
            self.hub.patch("clone", busy=False, error=f"The voice could not be created: {exc}")

    def a_listenClone(self, body):
        result = self.hub.get("clone", {}).get("result")
        if result:
            self.tts.stop_speaking()
            self.tts.speak(RN_DATA["cloneReadingTexts"].get(self.language, "Hello!").split(".")[0] + ".",
                           voice=result["voice"], blocking=False)

    def a_useClone(self, body):
        result = self.hub.get("clone", {}).get("result")
        if result:
            self.voice = result["voice"]
        self.show_voice_screen()

    def a_cloneBack(self, body):
        if self._recording is not None:
            self._recording["stop"].set()
        self.show_voice_screen()

    # ---- 3. speaker verification ----------------------------------------------------------------------
    def show_speaker_screen(self):
        self.hub.set(screen="speaker", speaker={"hasSaved": self.signature_path.is_file()})

    def a_useSaved(self, body):
        self.enrollment = self.signature_path.read_text(encoding="utf-8")
        self.show_wake_screen()

    def a_skipSpeaker(self, body):
        self.enrollment = None
        self.show_wake_screen()

    def _controller(self):
        sv = SpeakerVerification()
        sv.set_speaker_verification_license(self.license_key)
        return sv.SpeakerVerificationMicController(model_path=str(self.args.speaker_model), sample_rate=SAMPLE_RATE,
                                                   frame_size=FRAME)

    def a_createSignature(self, body):
        sentences = [s.replace("{wake}", WAKE_PHRASE)
                     for s in RN_DATA["enrollmentSentences"].get(self.language) or RN_DATA["enrollmentSentences"]["en"]]
        self.hub.set(screen="signature", signature={"collected": 0, "target": SIGNATURE_SAMPLES, "sentences": sentences})
        controller = self._controller()
        stream = FrameStream()
        self.mic.consumers.append(stream.feed)
        try:
            embeddings = []
            for i in range(SIGNATURE_SAMPLES):
                time.sleep(0.6)            # time to read the new sentence
                stream.drain()
                embeddings.append(controller.create_enrollment_embedding_from_stream(
                    stream, sample_seconds=SIGNATURE_SAMPLE_SECONDS))
                self.hub.patch("signature", collected=i + 1)
            enrollment = controller.create_enrollment_json(SPEAKER_ID, embeddings)
        finally:
            self.mic.consumers.remove(stream.feed)
        enrollment = enrollment if isinstance(enrollment, str) else json.dumps(enrollment)
        self.signature_path.write_text(enrollment, encoding="utf-8")
        self.enrollment = enrollment
        self._start_voice_test()

    def _start_voice_test(self):
        self.hub.set(screen="voicetest", voicetest={"result": None, "at": None})
        controller = self._controller()
        stream = FrameStream()
        self._voice_test_stream = stream
        self.mic.consumers.append(stream.feed)

        def run():
            try:
                for result in controller.iter_verify_from_stream(stream, self.enrollment):
                    self.hub.patch("voicetest", result={"score": float(result.get("uiScore", result["score"])),
                                                        "isMatch": bool(result["isMatch"])}, at=time.time())
            except EOFError:
                pass
            except Exception as exc:
                log(f"[voice test] {exc}")
            finally:
                if stream.feed in self.mic.consumers:
                    self.mic.consumers.remove(stream.feed)

        threading.Thread(target=run, daemon=True).start()

    def a_voiceTestContinue(self, body):
        if self._voice_test_stream is not None:
            self._voice_test_stream.closed.set()
            self._voice_test_stream = None
        self.show_wake_screen()

    # ---- 4. wake word -----------------------------------------------------------------------------------
    def show_wake_screen(self, message="Say the wake word"):
        self._listening = False
        language = next((x["label"].split(" (")[0] for x in APP_LANGUAGES if x["id"] == self.language), self.language)
        self.hub.set(screen="wakeword", wakeword={"listening": False, "heard": False, "message": "Starting the wake word…",
                                                  "voice": self.voice, "language": language,
                                                  "driverOnly": bool(self.enrollment)})
        try:
            self._start_wake_word()
            self.hub.patch("wakeword", listening=True, message=message)
            self.mic.release()
        except Exception as exc:
            log(f"[wake word] {exc}")
            self.hub.patch("wakeword", message=f"The wake word could not start: {exc}. Use “Simulate wake word”.")

    def _start_wake_word(self):
        if self.kd is not None:
            self.kd.stop_keyword_detection()
            if self.kd.feed_audio_frame in self.mic.consumers:
                self.mic.consumers.remove(self.kd.feed_audio_frame)
        config = {"model_path": str(self.args.wake_word_model), "callback_function": self._on_wake_word,
                  "_davoice_speaker_id_internal_options": {"model_path": str(self.args.speaker_model)}}
        config.update(WAKE_WORD_SETTINGS)
        self.kd = KeywordDetection(keyword_models=[config])
        self.kd.set_keyword_detection_license(self.license_key)
        if self.enrollment:
            self.kd.add_speaker(SPEAKER_ID, self.enrollment)
        self.kd.start_keyword_detection_external_audio()
        self.mic.consumers.append(self.kd.feed_audio_frame)

    def _on_wake_word(self, params=None):
        log(f"[wake word] {WAKE_PHRASE} detected")
        screen = self.hub.get("screen")
        if screen == "car":
            if self.tts is not None and self.tts.is_speaking():      # barge-in: stop the reply
                self.tts.stop_speaking()
                if self.assistant is not None:
                    self.assistant.cancel()
            return
        if screen == "wakeword":
            if self.args.audio_file:
                self.mic.hold()        # a recording waits while the agent loads (a live microphone just drops it)
            self.hub.patch("wakeword", heard=True)
            threading.Thread(target=self._open_car_agent, daemon=True).start()

    def a_simulateWake(self, body):
        self._on_wake_word()

    def a_wakeBack(self, body):
        self.show_speaker_screen()

    # ---- 5. car agent: loading ----------------------------------------------------------------------------
    def _open_car_agent(self):
        if not self._busy.acquire(blocking=False):
            return
        try:
            if self.assistant is not None and self.stt is not None:
                self._show_car()
                return
            self._load_agent()
        finally:
            self._busy.release()

    def _load_agent(self):
        stages = [{"key": "download", "label": "Downloading the agent model", "detail": "382 MB, first start only"},
                  {"key": "load", "label": "Loading the model", "detail": ""},
                  {"key": "warm", "label": "Preparing the agent", "detail": ""},
                  {"key": "stt", "label": "Loading speech recognition",
                   "detail": ""}]
        started = time.time()
        state = {"index": 0}
        self.hub.set(screen="loading", loading={"modelName": "", "stages": stages, "activeIndex": 0, "seconds": 0,
                                                "error": None, "progress": None})
        ticking = threading.Event()

        def tick():
            while not ticking.wait(1.0):
                self.hub.patch("loading", seconds=int(time.time() - started))

        threading.Thread(target=tick, daemon=True).start()

        def stage(index, **extra):
            state["index"] = index
            self.hub.patch("loading", activeIndex=index, **extra)

        try:
            if self.assistant is None:
                assistant = LocalAssistant(self.license_key, language=self.language, demo="car",
                                           data_dir=str(self.data_dir), layer2="none",
                                           log=lambda m: log(m) if self.args.verbose else None)
                self.hub.patch("loading", modelName=assistant.model["displayName"])
                if assistant.store.model_path(assistant.model).is_file():
                    stage(1)                  # downloaded before: loading starts right away

                def progress(fraction):
                    if state["index"] == 0:
                        self.hub.patch("loading", progress=int(100 * fraction))
                        if fraction >= 1.0:
                            stage(1, progress=None)

                def warming():
                    stage(2)

                assistant.warm_up(on_progress=progress, on_warming=warming)
                if self.enrollment:
                    assistant.speakers.set_gate(True, SPEAKER_ID)
                assistant.car.on_change(lambda car: self._push_car())
                self.assistant = assistant
                self._apply_confidence()
            stage(3)
            if self.stt is None:
                self._load_stt()
            ticking.set()
            self._show_car()
        except Exception as exc:
            ticking.set()
            traceback.print_exc()
            self.hub.patch("loading", error=str(exc), activeIndex=-1)

    def _load_stt(self):
        locale = get_language(self.language)["sttLocale"]
        bias = HERE / "stt_bias_conf" / ("words_flattened.pt-BR.txt" if self.language == "pt-BR" else "words_flattened.txt")
        stt = SpeechToText(model=str(self.stt_model), locale=locale, bias_file_path=str(bias) if self.language in ("en", "pt-BR") else None,
                           speaker_model_path=str(self.args.speaker_model),
                           on_speech_partial_results=self._on_partial, on_speech_results=self._on_final,
                           on_speech_error=lambda e: log(f"[STT] error: {e.get('error')}"))
        stt.set_stt_license(self.license_key)
        if self.enrollment:
            stt.add_speaker(SPEAKER_ID, self.enrollment)
        stt.load()
        stt.start_external_audio()
        self.mic.consumers.append(lambda frame: self._listening and stt.feed_audio_frame(frame))
        self.stt = stt

    def a_loadingBack(self, body):
        self.show_wake_screen()

    def a_loadingRetry(self, body):
        threading.Thread(target=self._open_car_agent, daemon=True).start()

    # ---- 5. car agent: the screen --------------------------------------------------------------------------
    def _show_car(self):
        self.hub.set(screen="car", car={"heard": "", "partial": "", "reply": "", "working": False, "ignored": False,
                                        "modelName": self.assistant.model["displayName"], "voice": self.voice,
                                        "confidence": self.confidence, "choices": CONFIDENCE_CHOICES,
                                        "lastTurn": None, "language": self.language})
        self._push_car()
        self._listening = True
        self.mic.release()

    def _push_car(self):
        car = self.assistant.car
        actions = list(car.actions)
        self.hub.set(carState=car.snapshot(), carLatest=actions[-1] if actions else None, carActionCount=len(actions))

    def _on_partial(self, event):
        if self.assistant is not None:
            self.assistant.speakers.note_speech_result(event)
        text = strip_wake_word((event.get("value") or [""])[0])
        if text and self.hub.get("screen") == "car":
            self.hub.patch("car", partial=text)
            self.assistant.prefill(text)

    def _on_final(self, event):
        if self.assistant is not None:
            self.assistant.speakers.note_speech_result(event)
        text = strip_wake_word((event.get("value") or [""])[0])
        log(f"[STT] {text!r}{'  [' + event['speaker_id'] + ']' if event.get('speaker_id') else ''}")
        if text and self.hub.get("screen") == "car":
            self._turns.put(text)
        else:
            self.hub.patch("car", partial="")

    def a_sendText(self, body):
        text = (body.get("text") or "").strip()
        if text:
            if self.enrollment:      # typed text has no voice: treat it as the owner's
                self.assistant.speakers.note_speech_result({"speaker_id": SPEAKER_ID})
            self._turns.put(text)

    def _turn_worker(self):
        while True:
            text = self._turns.get()
            try:
                self._turn(text)
            except Exception as exc:
                traceback.print_exc()
                self.hub.patch("car", working=False, reply=f"Error: {exc}")

    def _turn(self, text):
        log(f"[you] {text}")
        if self.stt is not None:
            self.stt.pause()          # the microphone must not hear the reply
        if self.args.audio_file:
            self.mic.hold()
        self.hub.patch("car", heard=text, partial="", working=True, reply="", ignored=False, lastTurn=None)
        speaker = SentenceSpeaker(self.tts, self.voice, self.language)
        pieces = []

        def on_text(piece):
            pieces.append(piece)
            speaker.feed(piece)
            self.hub.patch("car", reply="".join(pieces).strip())

        def on_event(event):
            if event.get("type") == "filler" and event.get("reason") != "remote":
                speaker.say(event.get("text"))

        t0 = time.time()
        try:
            result = self.assistant.ask(text, on_text=on_text, on_event=on_event)
            speaker.flush()
            reply = (result.get("text") or "".join(pieces)).strip()
            scope = (result.get("scope") or {}).get("outcome")
            log(f"[agent] {reply}  ({time.time() - t0:.2f} s{', scope ' + scope if scope else ''})")
            self.hub.patch("car", working=False, reply=reply, ignored=scope == "ignore",
                           lastTurn={"scope": scope, "seconds": round(time.time() - t0, 2),
                                     "confidence": result.get("confidence")})
            self.tts.wait_until_done()
        finally:
            if self.stt is not None:
                self.stt.unpause()
            self.mic.release()

    def a_setDriving(self, body):
        self.assistant.car.set_driving(bool(body["driving"]))

    def a_resetCar(self, body):
        self.assistant.car.reset()
        self.assistant.reset_conversation()
        self.hub.patch("car", heard="", partial="", reply="", ignored=False, lastTurn=None)

    def a_setConfidence(self, body):
        self.confidence = float(body["value"])
        self._apply_confidence()
        self.hub.patch("car", confidence=self.confidence)

    def _apply_confidence(self):
        if self.assistant is not None:
            self.assistant.agent.configure({"confidence": {"min": self.confidence}})

    def a_carBack(self, body):
        if self.tts is not None:
            self.tts.stop_speaking()
        self.show_wake_screen()

    # ---- actions from the browser ---------------------------------------------------------------------
    def handle(self, action, body):
        method = getattr(self, f"a_{action}", None)
        if method is None:
            raise KeyError(action)

        def run():
            try:
                method(body)
            except Exception as exc:
                traceback.print_exc()
                self.hub.set(toast=f"{action} failed: {exc}", toastAt=time.time())

        threading.Thread(target=run, daemon=True).start()

    def close(self):
        for stop in (lambda: self.mic.stop(), lambda: self.stt and self.stt.stop(),
                     lambda: self.kd and self.kd.stop_keyword_detection(), lambda: self.tts and self.tts.close(),
                     lambda: self.assistant and self.assistant.close()):
            try:
                stop()
            except Exception:
                pass


# ---------------------------------------------------------------------------------------------------
def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def _send(self, code, body, ctype="application/json"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/events":
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                version = -1
                try:
                    while True:
                        new, data = app.hub.wait(version)
                        if new == version:
                            self.wfile.write(b": keep-alive\n\n")
                        else:
                            version = new
                            self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    return
            if path == "/state":           # the same state without streaming (the page's ?poll mode)
                return self._send(200, app.hub.snapshot().encode("utf-8"))
            file = (WEB / ("index.html" if path == "/" else path.lstrip("/"))).resolve()
            if WEB.resolve() not in file.parents or not file.is_file():
                return self._send(404, b"not found", "text/plain")
            ctype = mimetypes.guess_type(str(file))[0] or "application/octet-stream"
            self._send(200, file.read_bytes(), ctype)

        def do_POST(self):
            url = urlparse(self.path)
            length = int(self.headers.get("Content-Length") or 0)
            data = self.rfile.read(length) if length else b""
            try:
                if url.path == "/api/upload":
                    name = (parse_qs(url.query).get("name") or ["upload.wav"])[0]
                    app.upload(name, data)
                elif url.path.startswith("/api/"):
                    app.handle(url.path[len("/api/"):], json.loads(data or b"{}"))
                else:
                    return self._send(404, b'{"ok":false}')
                self._send(200, b'{"ok":true}')
            except Exception as exc:
                self._send(400, json.dumps({"ok": False, "error": str(exc)}).encode("utf-8"))

    return Handler


def main():
    p = argparse.ArgumentParser(description="DaVoice Car Agent: on-device voice assistant for a simulated car.")
    p.add_argument("--license-file", default=str(HERE / "licensekey.txt"
                                                   if (HERE / "licensekey.txt").is_file()
                                                   else HERE.parent / "example" / "licensekey.txt"),
                   help="your DaVoice license key file")
    p.add_argument("--data-dir", default=os.environ.get("DAVOICE_DATA_DIR") or str(Path.home() / ".davoice"),
                   help="where voice packs, the agent model, cloned voices and the voice signature are stored")
    p.add_argument("--models-dir", action="append", help="a folder that already holds language-pack files")
    p.add_argument("--wake-word-model", default=str(HERE.parent / "example" / "models" / "hey_coach_model_28_22012026b.dm"))
    p.add_argument("--speaker-model", default=str(HERE.parent / "example" / "models" / "sv.dm"))
    p.add_argument("--stt-model", default=str(HERE.parent / "example" / "models" / "davoice_stt.dm"),
                   help="the speech model file (default: ../example/models/davoice_stt.dm, "
                        "downloaded the first time by ../example/download_stt_model.py)")
    p.add_argument("--port", type=int, default=8770)
    p.add_argument("--no-browser", action="store_true", help="don't open the browser")
    p.add_argument("--audio-file", help="a 16 kHz mono WAV played in as the microphone (tests)")
    p.add_argument("--mute", action="store_true", help="synthesize speech but play nothing (tests)")
    p.add_argument("--verbose", action="store_true", help="print the agent's log")
    p.add_argument("--list-languages", "--lang-list", "--locale-list", dest="list_languages", action="store_true",
                   help="list the languages (chosen on the first screen) and exit")
    args = p.parse_args()
    if args.list_languages:
        print("Languages (picked on the first screen): voice pack, speech recognition and replies")
        for x in APP_LANGUAGES:
            if not x.get("hidden"):
                print(f"  {x['id']:<6} {x['label']}")
        return

    if not Path(args.license_file).is_file():
        sys.exit(f"License key file not found: {args.license_file} (use --license-file)")
    # The speech model (2.5 GB) is downloaded the first time, into ../example/models/.
    sys.path.insert(0, str(HERE.parent / "example"))
    from download_stt_model import ensure_stt_model
    ensure_stt_model(args.stt_model)
    app = CarAgentApp(args)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(app))
    server.daemon_threads = True
    url = f"http://127.0.0.1:{args.port}"
    app.start()
    log(f"DaVoice Car Agent: {url}   (data: {app.data_dir}; Ctrl+C to quit)")
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        app.close()


if __name__ == "__main__":
    main()
