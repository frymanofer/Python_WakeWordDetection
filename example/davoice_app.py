#!/usr/bin/env python3
"""The complete DaVoice app, the Python version of the React Native example app
(https://github.com/frymanofer/ReactNative_DaVoice), with the same models:

  1. language (11 languages; the voice pack is downloaded the first time),
  2. voice (built-in, your cloned voices, or clone a new one from a recording),
  3. speaker verification (create a voice signature, use the saved one, or skip),
  4. the wake word "Hey Coach",
  5. the mode: local_ai_chat (on-device car agent), full_ai_chat (Gemini),
     combined (speak -> hear it back), stt_only, type_to_tts.

    ./setup_voice_ai.sh && source venv-voice-ai/bin/activate     # once; see README.md
    python davoice_app.py                                   # asks for everything
    python davoice_app.py --language pt-BR --mode local_ai_chat
    python davoice_app.py --mode local_ai_chat --text-input   # type instead of speaking
    python davoice_app.py --help

Everything runs on this computer except Full AI Chat (Gemini).
"""
from pathlib import Path

from download_stt_model import ensure_stt_model_for_example
from keyword_detection.app import run_app

HERE = Path(__file__).resolve().parent
# The speech model is downloaded the first time (2.5 GB); typing-only modes don't need it.
ensure_stt_model_for_example(HERE / "models" / "davoice_stt.dm", skip_if=("type_to_tts", "--text-input"))

run_app(
    license_file=HERE / "licensekey.txt",
    wake_word_model=HERE / "models" / "hey_coach_model_28_22012026b.dm",
    speaker_model=HERE / "models" / "sv.dm",
    stt_model=HERE / "models" / "davoice_stt.dm",
    bias_file=HERE / "stt_bias_conf" / "words_flattened.txt",
)
