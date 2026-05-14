#!/usr/bin/env python3
"""
Speaker verification example using a saved enrollment JSON.

This follows the React Native verification flow idea:
- load enrollment
- verify from microphone continuously
- evaluate every hop interval
- keep a short match-hold window for smoother UI/logging
"""

from __future__ import annotations

import argparse
from pathlib import Path

from keyword_detection import SpeakerVerification


DEFAULT_SAMPLE_RATE = 16000
DEFAULT_FRAME_SIZE = 1280
DEFAULT_HOP_SECONDS = 0.25
DEFAULT_MATCH_HOLD_MS = 750

def build_parser() -> argparse.ArgumentParser:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Verify microphone audio against a saved speaker enrollment.")
    parser.add_argument("--enrollment", default=str(script_dir / "sv_enrollment.json"), help="Enrollment JSON created by speaker_id_onboarding.py.")
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--frame-size", type=int, default=DEFAULT_FRAME_SIZE)
    parser.add_argument("--hop-seconds", type=float, default=DEFAULT_HOP_SECONDS)
    parser.add_argument("--match-hold-ms", type=int, default=DEFAULT_MATCH_HOLD_MS)
    return parser

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

    enrollment_json = enrollment_path.read_text(encoding="utf-8")
    controller = sv.SpeakerVerificationMicController(
        sample_rate=args.sample_rate,
        frame_size=args.frame_size,
    )

    print("Speaker verification")
    print(f"Enrollment JSON : {enrollment_path}")
    print(f"Hop seconds     : {args.hop_seconds:.2f}")
    print("Press Ctrl+C to stop.\n")

    try:
        for result in controller.iter_verify_from_mic(
            enrollment_json,
            hop_seconds=args.hop_seconds,
            match_hold_ms=args.match_hold_ms,
        ):
            print(
                f"SV score={float(result['uiScore']):.3f} "
                f"match={'YES' if result['uiIsMatch'] else 'NO'}"
            )
    except KeyboardInterrupt:
        print("\nStopped speaker verification.")


if __name__ == "__main__":
    main()
