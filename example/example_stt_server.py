#!/usr/bin/env python3
"""DaVoice speech to text for servers: one model, many simultaneous sessions.

Each WAV file plays the part of one client. The clients start half a second apart
and stream their audio in real time (80 ms frames), the way a live connection
would; one STTServer transcribes all of them at once with a single copy of the
model. See README_STT.md, "Many users: STTServer".

    ./setup_voice_ai.sh && source venv-voice-ai/bin/activate     # once; see README.md
    python example_stt_server.py --files a.wav b.wav c.wav
    python example_stt_server.py --files a.wav b.wav --clients 6 --threads 4 --locale en-US
    python example_stt_server.py --files a.wav --fast            # no real-time pacing: measures throughput

WAV files must be 16 kHz mono 16-bit (../resampleTo16kHZ.sh converts other files).
"""
import argparse
import threading
import time
import wave
from pathlib import Path

import numpy as np

from download_stt_model import DEFAULT_MODEL_PATH, ensure_stt_model
from keyword_detection.stt import STTServer, language_list_text, load_bias_phrases

HERE = Path(__file__).resolve().parent
FRAME = 1280  # 80 ms at 16 kHz


def read_wav_16k(path):
    with wave.open(str(path), "rb") as wf:
        if wf.getframerate() != 16000 or wf.getnchannels() != 1 or wf.getsampwidth() != 2:
            raise SystemExit(f"{path}: needs 16 kHz mono 16-bit WAV "
                             f"(got {wf.getframerate()} Hz, {wf.getnchannels()} channel(s))")
        pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
    return pcm.astype(np.float32) / 32768.0


def main():
    p = argparse.ArgumentParser(description="DaVoice multi-stream speech to text (server mode).")
    p.add_argument("--files", nargs="+", help="16 kHz mono WAV files, one per client (required)")
    p.add_argument("--clients", type=int, default=0, help="number of clients (default: one per file; files repeat)")
    p.add_argument("--locale", default="auto", help="e.g. en-US, de-DE, or auto (--list-languages)")
    p.add_argument("--list-languages", "--lang-list", "--locale-list", dest="list_languages", action="store_true",
                   help="list the supported languages and exit")
    p.add_argument("--bias-file", default=str(HERE / "stt_bias_conf" / "words_flattened.txt"),
                   help="bias list for every session ('' for none)")
    p.add_argument("--threads", type=int, default=4, help="CPU threads for this server process")
    p.add_argument("--chunk", type=float, default=0.56, help="0.56 (default) or 1.04 seconds; same for all sessions")
    p.add_argument("--right", type=float, default=0.56, help="look-ahead seconds: 0.56 (default) or 1.04")
    p.add_argument("--device", default="cpu", help="cpu (tested), cuda")
    p.add_argument("--fast", action="store_true", help="push audio as fast as possible instead of in real time")
    p.add_argument("--license-file", default=str(HERE / "licensekey.txt"))
    p.add_argument("--stt-model", default=str(DEFAULT_MODEL_PATH),
                   help="the speech model file (default: %(default)s; downloaded the first time)")
    args = p.parse_args()
    if args.list_languages:
        print(language_list_text())
        return
    if not args.files:
        p.error("--files is required")
    ensure_stt_model(args.stt_model)   # offers the download (2.5 GB) when the file is missing

    license_key = Path(args.license_file).read_text().strip()
    phrases = load_bias_phrases(args.bias_file) if args.bias_file else None
    files = [Path(f) for f in args.files]
    n_clients = args.clients or len(files)
    audio = {f: read_wav_16k(f) for f in set(files)}

    # Results arrive here, on the server's scheduler thread. In a real server, hand
    # them to the client's connection (e.g. loop.call_soon_threadsafe(queue.put_nowait, ...)).
    finals = {}
    print_lock = threading.Lock()

    def on_event(session_id, kind, text, client):
        with print_lock:
            if kind == "final":
                finals[client] = text
                print(f"[client {client}] FINAL: {text}")
            else:
                print(f"[client {client}] ... {text}")

    server = STTServer(on_event=on_event, license_key=license_key, model=args.stt_model, device=args.device,
                       num_threads=args.threads, chunk_secs=args.chunk, right_context_secs=args.right,
                       max_batch=max(n_clients, 1), record_latency=True)
    print("Loading the speech recognizer...")
    server.start()

    def client(index, pcm):
        time.sleep(0 if args.fast else 0.5 * index)
        # One session = one utterance / one request. The app decides where it ends.
        session = server.open_stream(language=args.locale, phrases=phrases, user=index)
        t0 = time.monotonic()
        for k, start in enumerate(range(0, pcm.size, FRAME)):
            server.push(session, pcm[start:start + FRAME])
            if not args.fast:  # real time: one 80 ms frame every 80 ms
                delay = t0 + (k + 1) * FRAME / 16000 - time.monotonic()
                if delay > 0:
                    time.sleep(delay)
        server.finish(session)  # the ("final", text) event follows

    started = time.monotonic()
    threads = [threading.Thread(target=client, args=(i, audio[files[i % len(files)]])) for i in range(n_clients)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    while len(finals) < n_clients:
        time.sleep(0.05)
    elapsed = time.monotonic() - started
    server.stop()

    rec = server.recognizer
    lat = np.array(rec.latencies or [0.0])
    audio_s = sum(audio[files[i % len(files)]].size for i in range(n_clients)) / 16000
    print(f"\n{n_clients} sessions, {audio_s:.1f} s of audio in {elapsed:.1f} s; "
          f"{rec.stats['items']} chunks in {rec.stats['steps']} batched steps "
          f"(mean batch {rec.stats['items'] / max(rec.stats['steps'], 1):.1f}); "
          f"processing delay per chunk p50 {np.percentile(lat, 50) * 1000:.0f} ms, "
          f"p95 {np.percentile(lat, 95) * 1000:.0f} ms (keep p95 under {args.chunk * 1000:.0f} ms)")


if __name__ == "__main__":
    main()
