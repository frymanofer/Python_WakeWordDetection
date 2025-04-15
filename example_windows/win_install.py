#install.py:

import platform
import sys
import os
import subprocess

# Base URL where wheels are hosted
BASE_URL = "https://github.com/frymanofer/Python_WakeWordDetection/raw/main/dist"

# Wheel prefix
PACKAGE_NAME = "keyword_detection_lib"

# Check for the environment variable or use the default version
KEYWORD_DETECTION_VERSION = os.getenv("KEYWORD_DETECTION_VERSION", "2.0.1")

# Determine Python version
python_version = f"cp{sys.version_info.major}{sys.version_info.minor}"
platform_tag = "win_amd64"  # Default for Windows

# Construct the wheel filename
wheel_name = f"{PACKAGE_NAME}-{KEYWORD_DETECTION_VERSION}-{python_version}-none-{platform_tag}.whl"

# Construct the URL
wheel_url = f"{BASE_URL}/{wheel_name}"

# Install the package using py -m pip
subprocess.run(["py", "-m", "pip", "install", wheel_url], check=True)
