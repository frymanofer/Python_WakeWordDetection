#!/usr/bin/env python3
"""DaVoice on-device car assistant: type a command, the local AI agent drives a
simulated car. Nothing goes to the cloud.

    ./setup_voice_ai.sh --no-stt && source venv-voice-ai/bin/activate   # once (or without --no-stt for everything)
    python example_car_assistant.py
    python example_car_assistant.py --language pt-BR
    python example_car_assistant.py --speak             # also say the replies

Try: "open all the windows", "set the temperature to 22", "lock the car",
"turn on the seat heating", "play some jazz".
"""
from pathlib import Path

from keyword_detection.app import run_car_assistant

run_car_assistant(license_file=Path(__file__).resolve().parent / "licensekey.txt")
