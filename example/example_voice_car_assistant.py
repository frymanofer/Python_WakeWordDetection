#!/usr/bin/env python3
"""DaVoice voice car assistant, fully on-device:

    "Hey Coach"  ->  speech to text  ->  local AI agent (simulated car)  ->  spoken reply

Say "Hey Coach", then a command ("open all the windows", "set the temperature to
22", "lock the car"). Follow-up commands within a few seconds of a reply need no
wake word. Saying "Hey Coach" while it speaks stops the reply.

    ./setup_voice_ai.sh && source venv-voice-ai/bin/activate     # once; see README.md
    python example_voice_car_assistant.py
    python example_voice_car_assistant.py --language pt-BR
    python example_voice_car_assistant.py --audio-file recording.wav   # 16 kHz mono, instead of the mic

Use headphones: with speakers the microphone also hears the replies.
"""
from pathlib import Path

from download_stt_model import ensure_stt_model_for_example
from keyword_detection.app import run_voice_car_assistant

HERE = Path(__file__).resolve().parent
ensure_stt_model_for_example(HERE / "models" / "davoice_stt.dm")   # downloads it the first time (2.5 GB)

run_voice_car_assistant(
    license_file=HERE / "licensekey.txt",
    wake_word_model=HERE / "models" / "hey_coach_model_28_22012026b.dm",
    stt_model=HERE / "models" / "davoice_stt.dm",
)
