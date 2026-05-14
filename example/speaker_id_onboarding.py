#!/usr/bin/env python3
"""
Speaker verification onboarding example.

This mirrors the React Native onboarding flow at a high level:
- collect multiple microphone samples
- create speaker embeddings
- save enrollment JSON for later verification / wake-word gating
"""

from __future__ import annotations

import argparse
import keyword_detection
import os
from pathlib import Path

from keyword_detection import SpeakerVerification


DEFAULT_SAMPLE_RATE = 16000
DEFAULT_FRAME_SIZE = 1280
DEFAULT_SAMPLE_SECONDS = 2.0
DEFAULT_SAMPLE_COUNT = 5

def build_parser() -> argparse.ArgumentParser:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Create a speaker-verification enrollment JSON from microphone audio.")
    parser.add_argument("--output", default=str(script_dir / "sv_enrollment.json"), help="Where to write the enrollment JSON.")
    parser.add_argument("--enrollment-id", default="davoice", help="Enrollment id stored in the JSON.")
    parser.add_argument("--sample-count", type=int, default=DEFAULT_SAMPLE_COUNT, help="Number of enrollment samples to collect.")
    parser.add_argument("--sample-seconds", type=float, default=DEFAULT_SAMPLE_SECONDS, help="Seconds to record per enrollment sample. iOS/RN currently use 2.0; try 0.5 to experiment.")
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE, help="Microphone sample rate.")
    parser.add_argument("--frame-size", type=int, default=DEFAULT_FRAME_SIZE, help="Microphone frame size.")
    return parser

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    script_dir = Path(__file__).resolve().parent
    license_path = script_dir / "licensekey.txt"
    license_key = license_path.read_text(encoding="utf-8").strip()

    sv = SpeakerVerification()
    print(f"license key is {license_key}")
    sv.set_speaker_verification_license(license_key)

    controller = sv.SpeakerVerificationMicController(
        sample_rate=args.sample_rate,
        frame_size=args.frame_size,
    )

    print("Speaker verification onboarding")
    print(f"Sample count     : {args.sample_count}")
    print(f"Sample duration  : {args.sample_seconds:.2f}s")
    print(f"Sample rate      : {args.sample_rate}")
    print(f"Frame size       : {args.frame_size}")
    print(f"Output JSON      : {args.output}")
    print(f"keyword_detection package path: {keyword_detection.__file__}")
    print(f"DAVOICE_SV_DEBUG={os.environ.get('DAVOICE_SV_DEBUG', '')}")
    print("")
    print("Press Enter before each enrollment sample and speak clearly.")
    embeddings = []
    for index in range(1, args.sample_count + 1):
        input(f"\n[{index}/{args.sample_count}] Press Enter to record sample {index}...")
        print(f"Recording sample {index}/{args.sample_count} for {args.sample_seconds:.2f}s...")
        embeddings.append(controller.create_enrollment_embedding_from_mic(sample_seconds=args.sample_seconds))
        print(f"Collected sample {index}/{args.sample_count}.")
    enrollment_json = controller.create_enrollment_json(args.enrollment_id, embeddings)
    output_path = Path(args.output).expanduser().resolve()
    output_path.write_text(enrollment_json, encoding="utf-8")

    print("")
    print(f"Saved enrollment JSON to: {output_path}")
    print("You can reuse it with speaker_id_verification.py or wakeword_with_speaker_id.py.")


if __name__ == "__main__":
    main()
