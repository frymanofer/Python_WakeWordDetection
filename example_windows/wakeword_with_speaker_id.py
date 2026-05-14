#!/usr/bin/env python3
"""
Wake word example with optional speaker-verification gateway.

This script uses:
- KeywordDetection external-audio API for wake-word detection
- SpeakerVerificationEngine for speaker gating
- a simple VAD-based speaker-verification trigger
- pre-gate buffering so late speaker decisions do not drop the wake word
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from keyword_detection import KeywordDetection


DEFAULT_SAMPLE_RATE = 16000
DEFAULT_FRAME_SIZE = 1280

def build_parser() -> argparse.ArgumentParser:
    script_dir = Path(__file__).resolve().parent
    default_model = script_dir / "models" / "hey_lookdeep_model_28_06032025_bno22.onnx"
    parser = argparse.ArgumentParser(description="Run wake-word detection with an optional speaker-verification gateway.")
    parser.add_argument("--license-file", default=str(script_dir / "licensekey.txt"), help="Wake-word license key file.")
    parser.add_argument("--keyword-model", default=str(default_model), help="Wake-word ONNX model path.")
    parser.add_argument("--enrollment", default=str(script_dir / "sv_enrollment.json"), help="Enrollment JSON created by speaker_id_onboarding.py. Use empty string to disable speaker verification.")
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--frame-size", type=int, default=DEFAULT_FRAME_SIZE)
    parser.add_argument("--keyword-threshold", type=float, default=0.9999)
    parser.add_argument("--keyword-buffer-cnt", type=int, default=4)
    parser.add_argument("--keyword-wait-ms", type=int, default=50)
    parser.add_argument("--speaker-hop-seconds", type=float, default=0.25, help="How often the built-in speaker gate should re-run verification while voice is active.")
    return parser


def open_input_stream(sample_rate: int, frame_size: int):
    try:
        import pyaudio
    except ImportError as exc:
        raise ImportError(
            "This example requires PyAudio for microphone capture. "
            "Install it with 'pip install keyword_detection_lib[mic]' or install "
            "PyAudio manually."
        ) from exc

    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=frame_size,
    )
    return audio, stream


def wakeword_callback(info):
    print(f"\nWake word detected: {info.get('phrase')} version={info.get('version')}")


def read_license(license_path: Path) -> str:
    if not license_path.exists():
        raise FileNotFoundError(f"License file not found: {license_path}")
    return license_path.read_text(encoding="utf-8").strip()


def main() -> None:
    args = build_parser().parse_args()

    enrollment_path = ""
    if args.enrollment.strip():
        enrollment_file = Path(args.enrollment).expanduser().resolve()
        if not enrollment_file.exists():
            raise FileNotFoundError(f"Enrollment JSON not found: {enrollment_file}")
        enrollment_path = str(enrollment_file)

    keyword_model_path = Path(args.keyword_model).expanduser().resolve()
    if not keyword_model_path.exists():
        raise FileNotFoundError(f"Keyword model not found: {keyword_model_path}")

    license_key = read_license(Path(args.license_file).expanduser().resolve())
    keyword_detector = KeywordDetection(
        keyword_models=[
            {
                "model_path": str(keyword_model_path),
                "callback_function": wakeword_callback,
                "threshold": args.keyword_threshold,
                "buffer_cnt": args.keyword_buffer_cnt,
                "wait_time": args.keyword_wait_ms,
                "speaker_id_enrollment_path": enrollment_path,
                "speaker_id_hop_seconds": args.speaker_hop_seconds,
            }
        ],
        sample_rate=args.sample_rate,
        frame_size=args.frame_size,
    )
    keyword_detector.set_keyword_detection_license(license_key)
    keyword_detector.start_keyword_detection_external_audio(enable_vad=False, buffer_ms=100)

    py_audio, stream = open_input_stream(args.sample_rate, args.frame_size)

    print("Wake word with speaker verification")
    print(f"Enrollment JSON : {enrollment_path or 'disabled'}")
    print(f"Keyword model   : {keyword_model_path}")
    print(f"Speaker hop     : {args.speaker_hop_seconds:.2f}s")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            data = stream.read(args.frame_size, exception_on_overflow=False)
            frame = np.frombuffer(data, dtype=np.int16)
            keyword_detector.feed_audio_frame(frame)
    except KeyboardInterrupt:
        print("\nStopped wake word + speaker verification.")
    finally:
        keyword_detector.stop_keyword_detection()
        stream.stop_stream()
        stream.close()
        py_audio.terminate()


if __name__ == "__main__":
    main()
