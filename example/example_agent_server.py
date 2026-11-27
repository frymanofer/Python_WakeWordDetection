#!/usr/bin/env python3
"""DaVoice agent on a server: ONE loaded model answers MANY users.

The model weights are in memory once. `--slots` contexts share them (that many
requests are answered at the same time); each user has only a small session:
their own conversation, settings and tools. Here every user gets a simulated car.

    ./setup_voice_ai.sh --no-stt && source venv-voice-ai/bin/activate   # once (or without --no-stt for everything)
    python example_agent_server.py                       # 6 users, 2 slots, CPU
    python example_agent_server.py --users 20 --slots 4
    python example_agent_server.py --gpu                 # Metal / CUDA

In a real server, call session.turn(text) from your request handler (any thread):
    session = server.session(user_id) or server.open_car_session(user_id, language="en")
    reply = session.turn(text)["text"]
With your own tools instead of the demo car: server.open_session(config=..., tools=[...]).
"""
import argparse
import threading
import time
from pathlib import Path

from keyword_detection.llm import AgentServer

COMMANDS = {
    "en": ["open all the windows", "set the temperature to {n} degrees", "lock the car"],
    "pt-BR": ["abre todos os vidros", "coloca o ar em {n} graus", "tranca o carro"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--users", type=int, default=6)
    ap.add_argument("--slots", type=int, default=2, help="requests answered at the same time")
    ap.add_argument("--threads", type=int, default=None, help="threads per slot (default: the cores divided between the slots)")
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--data-dir", default=None, help="where the model is downloaded (default ~/.davoice)")
    args = ap.parse_args()
    key = (Path(__file__).resolve().parent / "licensekey.txt").read_text().strip()

    print("Loading the model once ...")
    server = AgentServer.car(key, data_dir=args.data_dir, slots=args.slots, threads_per_slot=args.threads,
                             n_gpu_layers=-1 if args.gpu else 0, log=print)
    users = [server.open_car_session(f"user-{i}", language="pt-BR" if i % 2 else "en") for i in range(args.users)]

    # Before the first request: process the part every user shares (system prompt + tools), once per language.
    half = max(1, args.slots // 2)
    for sample in (users[0], users[1] if len(users) > 1 else users[0]):
        print("warm-up", sample.language, server.warm_up(sample, slots=half))

    lock = threading.Lock()

    def drive(i, session):
        for command in COMMANDS[session.language]:
            text = command.format(n=18 + i % 8)
            result = session.turn(text)
            with lock:
                info = result["server"]
                print(f"[{session.id} slot {info['slot']} waited {info['waitMs']} ms, answered in {info['turnMs']} ms] "
                      f"{text!r} -> {result['text']!r}")

    started = time.time()
    threads = [threading.Thread(target=drive, args=(i, s)) for i, s in enumerate(users)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"\n{args.users} users x 3 turns in {time.time() - started:.1f} s on {args.slots} slots")
    for s in users[:4]:
        car = s.car.snapshot()
        print(f"  {s.id}: temperature {car['temperature']['driver']}, locked {car['locked']}, windows {car['windows']}")
    print("stats:", server.stats())
    server.close()


if __name__ == "__main__":
    main()
