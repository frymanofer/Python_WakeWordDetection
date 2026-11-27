#!/usr/bin/env python3
"""DaVoice text to speech: voice packs, queued playback, stop, voices, WAV output.

    ./setup_voice_ai.sh --no-stt && source venv-voice-ai/bin/activate   # once (or without --no-stt for everything)
    python example_tts_speak.py                               # English, default voice
    python example_tts_speak.py --language de --voice Kate
    python example_tts_speak.py --text "Hello there."
    python example_tts_speak.py --list-voices

Languages: en, pt-BR, pt-PT, de, el, es, fr, it, nl, da, sv.
"""
from pathlib import Path

from keyword_detection.app import run_tts

run_tts(license_file=Path(__file__).resolve().parent / "licensekey.txt")
