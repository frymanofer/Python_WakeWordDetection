#!/usr/bin/env python3
"""
Standalone speaker-verification gateway example.

This shows how to use SpeakerVerificationGateway as a gate in front of an STT
pipeline or any other downstream audio consumer:
- incoming mic audio is blocked by default
- once the enrolled speaker is identified, the gateway flushes a pre-buffer
- while the gate stays open, downstream keeps receiving frames
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from keyword_detection import SpeakerVerification


DEFAULT_SAMPLE_RATE = 16000
DEFAULT_FRAME_SIZE = 1280

def build_parser() -> argparse.ArgumentParser:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Run the standalone speaker-verification gateway in front of a simple downstream sink.")
    parser.add_argument("--enrollment", default=str(script_dir / "sv_enrollment.json"), help="Enrollment JSON created by speaker_id_onboarding.py.")
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--frame-size", type=int, default=DEFAULT_FRAME_SIZE)
    parser.add_argument("--pre-ms", type=int, default=500, help="Pre-buffer to flush when the gate opens.")
    parser.add_argument("--gate-hangover-ms", type=int, default=1000, help="How long to keep forwarding after the last positive speaker match.")
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


def fake_stt_sink(audio_frame: np.ndarray) -> None:
    print(f"downstream got frame: samples={audio_frame.size}")


def format_gateway_status(last_result: dict | None, gate_open: bool, flushed_frames: int = 0) -> str:
    if last_result is None:
        return "gate=CLOSED awaiting-decision"

    ui_score = float(last_result.get("uiScore", last_result.get("score", 0.0)))
    ui_is_match = bool(last_result.get("uiIsMatch", False))

    if gate_open:
        return (
            f"gate=OPEN uiScore={ui_score:.3f} "
            f"match={'YES' if ui_is_match else 'NO'} "
            f"flushing={flushed_frames} frame(s)"
        )

    if ui_is_match:
        return f"gate=CLOSED uiScore={ui_score:.3f} match=YES pending-open"

    return "gate=CLOSED match=NO"


def main() -> None:
    args = build_parser().parse_args()
    script_dir = Path(__file__).resolve().parent
    license_path = script_dir / "licensekey.txt"
    license_key = license_path.read_text(encoding="utf-8").strip()
    enrollment_path = Path(args.enrollment).expanduser().resolve()
    if not enrollment_path.exists():
        raise FileNotFoundError(f"Enrollment JSON not found: {enrollment_path}")

    sv = SpeakerVerification()
    print(f"license key is {license_key}")
    sv.set_speaker_verification_license(license_key)

    gateway = sv.SpeakerVerificationGateway(
        enrollment_json_or_path=str(enrollment_path),
        sample_rate=args.sample_rate,
        frame_size=args.frame_size,
        pre_ms=args.pre_ms,
        gate_hangover_ms=args.gate_hangover_ms,
    )

    py_audio, stream = open_input_stream(args.sample_rate, args.frame_size)

    print("Speaker verification gateway")
    print(f"Enrollment JSON : {enrollment_path}")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            data = stream.read(args.frame_size, exception_on_overflow=False)
            frame = np.frombuffer(data, dtype=np.int16)
            gated_frames = gateway.feed_audio_frame(frame)
            last_result = gateway.get_last_result()
            if gated_frames is None:
                print(format_gateway_status(last_result, gate_open=False))
                continue

            print(format_gateway_status(last_result, gate_open=True, flushed_frames=len(gated_frames)))
            for gated_frame in gated_frames:
                fake_stt_sink(np.asarray(gated_frame, dtype=np.int16))
    except KeyboardInterrupt:
        print("\nStopped speaker gateway example.")
    finally:
        stream.stop_stream()
        stream.close()
        py_audio.terminate()


if __name__ == "__main__":
    main()
