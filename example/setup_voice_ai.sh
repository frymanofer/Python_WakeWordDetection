#!/bin/bash
# One-time setup for the voice AI examples (speech to text, text to speech, the on-device AI agent,
# davoice_app.py and ../example_car_agent). Everything goes into a virtual environment next to
# this script: ./venv-voice-ai
#
#   ./setup_voice_ai.sh                      # Python 3.12, everything
#   ./setup_voice_ai.sh python3.11           # another Python (3.10 to 3.13)
#   ./setup_voice_ai.sh python3.12 --no-stt  # text to speech + AI agent only (skips about 3.5 GB)
#
# Runs on Apple Silicon Macs (M1 or newer) and on Linux x86_64 / aarch64.
# Downloads about 1 GB of Python packages, then the speech model models/davoice_stt.dm
# (2.5 GB, skipped if it is already there).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PY="python3.12"
WITH_STT=1
for arg in "$@"; do
  case "$arg" in
    --no-stt) WITH_STT=0 ;;
    -h|--help) sed -n 2,11p "$0"; exit 0 ;;
    *) PY="$arg" ;;
  esac
done
# The speech recognition runtime, pinned to the version the speech model is tested with.
RUNTIME="nemo_toolkit[asr] @ git+https://github.com/NVIDIA-NeMo/Speech.git@991bd974583878d78d7869cbd881a1b09c7a2272"

case "$(uname -s)-$(uname -m)" in
  Darwin-arm64)  PLATFORM_TAG="macosx_11_0_arm64" ;;
  Linux-x86_64)  PLATFORM_TAG="manylinux_2_28_x86_64" ;;
  Linux-aarch64) PLATFORM_TAG="manylinux_2_28_aarch64" ;;
  *) echo "The voice AI examples run on Apple Silicon Macs and on Linux x86_64 / aarch64."; exit 1 ;;
esac
command -v "$PY" >/dev/null || { echo "$PY not found. Install it (macOS: brew install python@3.12) or pass another: ./setup_voice_ai.sh python3.11"; exit 1; }
TAG="$("$PY" -c 'import sys; print(f"cp{sys.version_info.major}{sys.version_info.minor}")')"
case "$TAG" in cp310|cp311|cp312|cp313) ;; *) echo "Python 3.10 to 3.13 is needed (got $TAG)."; exit 1;; esac
WHEEL="$(ls "$HERE"/../dist/keyword_detection_lib-*-"$TAG"-none-"$PLATFORM_TAG".whl 2>/dev/null | sort -V | tail -1)"
[ -n "$WHEEL" ] || { echo "No keyword_detection_lib wheel for $TAG / $PLATFORM_TAG in ../dist"; exit 1; }

echo "== Creating $HERE/venv-voice-ai ($("$PY" -V))"
"$PY" -m venv "$HERE/venv-voice-ai"
PIP="$HERE/venv-voice-ai/bin/python -m pip"
$PIP install --upgrade pip
if [ "$WITH_STT" = 1 ]; then
  if [ "$(uname -s)" = "Linux" ] && [ -z "${DAVOICE_GPU:-}" ]; then
    # The CPU build of PyTorch (much smaller). With a CUDA GPU, run with DAVOICE_GPU=1 instead.
    echo "== Installing PyTorch (CPU)"
    $PIP install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
  fi
  echo "== Installing the speech recognition runtime (the long step)"
  $PIP install "$RUNTIME"
  EXTRA="app"
else
  EXTRA="tts-audio,llm"
fi
echo "== Installing $(basename "$WHEEL") [$EXTRA]"
$PIP install "${WHEEL}[$EXTRA]"
if [ "$WITH_STT" = 1 ]; then
  echo "== Downloading the speech model (2.5 GB, once)"
  "$HERE/venv-voice-ai/bin/python" "$HERE/download_stt_model.py"
fi

echo
echo "Done. Now run:"
echo "  source venv-voice-ai/bin/activate"
if [ "$WITH_STT" = 1 ]; then
  echo "  python davoice_app.py"
else
  echo "  python example_car_assistant.py      # or: python example_tts_speak.py"
fi
