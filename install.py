import platform
import sys
import os
import subprocess


# Base URL where wheels are hosted
BASE_URL = "https://github.com/frymanofer/Python_WakeWordDetection/raw/main/dist"

# Wheel prefix
PACKAGE_NAME = "keyword_detection_lib"
# Check for the environment variable or use the default version
KEYWORD_DETECTION_VERSION = os.getenv("KEYWORD_DETECTION_VERSION", "2.1.3")

# Determine Python version
python_version = f"cp{sys.version_info.major}{sys.version_info.minor}"

# Determine platform and architecture
system = platform.system().lower()
arch = platform.machine().lower()

if system == "darwin":  # macOS
    if arch == "x86_64":
        platform_tag = "macosx_11_0_x86_64"  # Intel Mac, macOS 11+
    elif arch == "arm64":
        platform_tag = "macosx_11_0_arm64"  # Default ARM macOS
    else:
        raise ValueError(f"Unsupported macOS architecture: {arch}")
elif system == "linux":  # Linux
    if arch in ["x86_64", "aarch64"]:
        platform_tag = f"manylinux_2_28_{arch}"  # glibc 2.28+ (Ubuntu 20.04+, Debian 10+, RHEL 8+)
    elif arch == "armv7l":
        # Raspberry Pi 32-bit (Pi 2 and newer, glibc 2.31+): Python 3.9 and 3.11 only.
        if python_version not in ("cp39", "cp311"):
            raise ValueError(f"Linux armv7l wheels exist for Python 3.9 and 3.11 only (this is {python_version}).")
        platform_tag = "manylinux_2_31_armv7l"
    else:
        raise ValueError(f"Unsupported Linux architecture: {arch}")
elif system == "windows":  # Windows
    platform_tag = "win_amd64"  # Default for Windows
else:
    raise ValueError(f"Unsupported platform: {system}")

# Construct the wheel filename
wheel_name = f"{PACKAGE_NAME}-{KEYWORD_DETECTION_VERSION}-{python_version}-none-{platform_tag}.whl"

# Construct the URL
wheel_url = f"{BASE_URL}/{wheel_name}"

# Output the installation command
print(f"pip install {wheel_url}")

