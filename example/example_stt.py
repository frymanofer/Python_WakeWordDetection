#!/usr/bin/env python3
"""DaVoice speech to text.

    ./setup_voice_ai.sh && source venv-voice-ai/bin/activate     # once; see README.md
    python example_stt.py --locale en-US                    # microphone, with the bias list
    python example_stt.py --file recording.wav --locale de-DE
    python example_stt.py --speaker user=sv_enrollment.json   # only transcribe enrolled speakers
    python example_stt.py --help
"""
from pathlib import Path

from download_stt_model import ensure_stt_model_for_example
from keyword_detection.app import run_stt

HERE = Path(__file__).resolve().parent
ensure_stt_model_for_example(HERE / "models" / "davoice_stt.dm")   # downloads it the first time (2.5 GB)

run_stt(
    license_file=HERE / "licensekey.txt",
    bias_file=HERE / "stt_bias_conf" / "words_flattened.txt",
    speaker_model=HERE / "models" / "sv.dm",
    stt_model=HERE / "models" / "davoice_stt.dm",
)
