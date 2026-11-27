#!/usr/bin/env python3
"""Downloads the DaVoice speech model (davoice_stt.dm, about 2.5 GB) into models/.

Run it once before the speech examples:

    python download_stt_model.py            # downloads models/davoice_stt.dm (skipped if it is there)
    python download_stt_model.py --verify   # also checks the SHA-256 of a file that is already there
    python download_stt_model.py --dest /path/to/folder

The examples that need the model (davoice_app.py, example_stt.py,
example_stt_server.py, example_voice_car_assistant.py, ../example_car_agent)
call ensure_stt_model() and offer this download themselves when the file is
missing. setup_voice_ai.sh runs it at the end of the setup.

Only the Python standard library is used. An interrupted download resumes from
where it stopped. The file is checked (size and SHA-256) before it is put in
place. Its license notice is saved next to it as davoice_stt_NOTICES.md.
"""
import argparse
import hashlib
import os
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODELS_DIR = HERE / "models"
MODEL_FILE = "davoice_stt.dm"
NOTICE_FILE = "davoice_stt_NOTICES.md"
BASE_URL = os.environ.get("DAVOICE_STT_MODEL_URL_BASE",
                          "https://pub-27f94b1602c647ab95a601086cf52820.r2.dev/stt_models")
MODEL_URL = f"{BASE_URL}/{MODEL_FILE}"
NOTICE_URL = f"{BASE_URL}/THIRD_PARTY_NOTICES.md"
MODEL_SIZE = 2_507_489_296
MODEL_SHA256 = "f3e81348dbd6455d9afcffee6fd2e66a5151e1bb881addadfeea5bb2aef84a98"
DEFAULT_MODEL_PATH = MODELS_DIR / MODEL_FILE
_CHUNK = 1 << 20


def _gb(n):
    return f"{n / 1e9:.2f} GB"


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(8 * _CHUNK)
            if not block:
                return h.hexdigest()
            h.update(block)


def _download(url, part, total):
    """Downloads url into the .part file, resuming it. Retries on network errors."""
    for attempt in range(1, 6):
        have = part.stat().st_size if part.exists() else 0
        if have >= total:
            return
        req = urllib.request.Request(url, headers={"User-Agent": "davoice-examples",
                                                   "Range": f"bytes={have}-"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                if have and resp.status != 206:      # the server ignored the range: start again
                    have = 0
                mode = "ab" if have else "wb"
                start, last = time.time(), 0.0
                got = have
                with open(part, mode) as f:
                    while True:
                        block = resp.read(_CHUNK)
                        if not block:
                            break
                        f.write(block)
                        got += len(block)
                        now = time.time()
                        if now - last >= 0.5 or got >= total:
                            last = now
                            rate = (got - have) / max(now - start, 1e-6)
                            left = (total - got) / rate if rate > 0 else 0
                            sys.stdout.write(f"\r  {_gb(got)} / {_gb(total)}  ({100 * got / total:5.1f}%)  "
                                             f"{rate / 1e6:6.1f} MB/s  ~{int(left // 60)}m{int(left % 60):02d}s left   ")
                            sys.stdout.flush()
            sys.stdout.write("\n")
            if part.stat().st_size >= total:
                return
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            sys.stdout.write("\n")
            print(f"  network error ({e}); retrying ({attempt}/5)...")
            time.sleep(min(2 * attempt, 10))
    raise RuntimeError(f"could not download {url}; run this script again to resume")


def download_stt_model(dest_dir=MODELS_DIR, verify=False):
    """Makes sure <dest_dir>/davoice_stt.dm is there and complete; returns its path."""
    dest_dir = Path(dest_dir).expanduser()
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / MODEL_FILE
    notice = dest_dir / NOTICE_FILE

    if target.is_file() and target.stat().st_size == MODEL_SIZE:
        if verify:
            print(f"Checking {target} ...")
            if _sha256(target) != MODEL_SHA256:
                raise RuntimeError(f"{target} is damaged (SHA-256 mismatch). Delete it and run this script again.")
            print("  OK")
        else:
            print(f"Speech model already downloaded: {target}")
    else:
        if target.exists():
            print(f"{target} is incomplete ({_gb(target.stat().st_size)}); downloading it again.")
            target.unlink()
        part = target.with_name(target.name + ".part")
        need = MODEL_SIZE - (part.stat().st_size if part.exists() else 0)
        free = shutil.disk_usage(dest_dir).free
        if free < need + 200_000_000:
            raise RuntimeError(f"not enough disk space in {dest_dir}: {_gb(need)} needed, {_gb(free)} free. "
                               f"Use --dest on a disk with more space.")
        print(f"Downloading the speech model ({_gb(MODEL_SIZE)}) to {target}")
        _download(MODEL_URL, part, MODEL_SIZE)
        if part.stat().st_size != MODEL_SIZE:
            part.unlink()
            raise RuntimeError("the download has the wrong size; run this script again")
        print("  checking the file ...")
        if _sha256(part) != MODEL_SHA256:
            part.unlink()
            raise RuntimeError("the download is damaged (SHA-256 mismatch); run this script again")
        os.replace(part, target)
        print(f"  done: {target}")

    if not notice.is_file():
        try:
            req = urllib.request.Request(NOTICE_URL, headers={"User-Agent": "davoice-examples"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                notice.write_bytes(resp.read())
        except (urllib.error.URLError, OSError) as e:
            print(f"  (could not download the license notice {NOTICE_URL}: {e})")
    return target


def ensure_stt_model(path=DEFAULT_MODEL_PATH, ask=True):
    """Called by the examples. If `path` is missing, offers to download it (asks only when
    run from a terminal). Returns the path; it may still be missing if the user declined."""
    path = Path(path).expanduser()
    if path.is_dir():
        path = path / MODEL_FILE
    if path.is_file():
        return path                     # never touch a file that is there (run the script with --verify to check it)
    if path.name != MODEL_FILE:
        sys.exit(f"Speech model not found: {path}")
    print(f"The speech model is not downloaded yet: {path}")
    if ask and sys.stdin.isatty():
        answer = input(f"Download it now ({_gb(MODEL_SIZE)})? [Y/n] ").strip().lower()
        if answer not in ("", "y", "yes"):
            print(f"Skipped. Speech recognition will not work until you run: python {HERE / 'download_stt_model.py'}")
            return path
    try:
        return download_stt_model(path.parent)
    except RuntimeError as e:
        sys.exit(f"Speech model download failed: {e}")
    except KeyboardInterrupt:
        sys.exit("\nStopped. Run the example (or download_stt_model.py) again to resume the download.")


_NO_MODEL_FLAGS = ("-h", "--help", "--list-languages", "--lang-list", "--locale-list")


def ensure_stt_model_for_example(path=DEFAULT_MODEL_PATH, argv=None, skip_if=()):
    """For the example scripts, before they parse their options: offers the download unless
    the command line does not need the default model (--help, --list-languages, an explicit
    --stt-model, or any of `skip_if`, e.g. "type_to_tts")."""
    argv = sys.argv[1:] if argv is None else argv
    words = set()
    for a in argv:
        words.update(a.split("=", 1))
    if words & set(_NO_MODEL_FLAGS) or "--stt-model" in words or words & set(skip_if):
        return Path(path)
    return ensure_stt_model(path)


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--dest", default=str(MODELS_DIR), help="folder to save davoice_stt.dm in (default: %(default)s)")
    p.add_argument("--verify", action="store_true", help="check the SHA-256 of a file that is already downloaded")
    args = p.parse_args()
    try:
        download_stt_model(args.dest, verify=args.verify)
    except RuntimeError as e:
        sys.exit(f"Error: {e}")
    except KeyboardInterrupt:
        sys.exit("\nStopped. Run the script again to resume the download.")


if __name__ == "__main__":
    main()
