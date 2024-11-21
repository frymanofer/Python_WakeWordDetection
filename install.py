import platform
import sys
import subprocess

def install_wheel(wheel_url):
    try:
        # Use subprocess to run the pip install command
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", wheel_url],
            check=True,  # Raise an exception on error
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print(result.stdout)
        print("Installation successful.")
    except subprocess.CalledProcessError as e:
        print("An error occurred while installing the package:")
        print(e.stderr)

# Base URL where wheels are hosted
BASE_URL = "https://github.com/frymanofer/Python_WakeWordDetection/raw/main/dist"

# Wheel prefix
PACKAGE_NAME = "keyword_detection_lib"
KEYWORD_DETECTION_VERSION = "1.0.17"

# Determine Python version
python_version = f"cp{sys.version_info.major}{sys.version_info.minor}"

# Determine platform and architecture
system = platform.system().lower()
arch = platform.machine().lower()

if system == "darwin":  # macOS
    if arch == "x86_64":
        platform_tag = "macosx_10_9_x86_64"  # Default macOS version
    elif arch == "arm64":
        platform_tag = "macosx_11_0_arm64"  # Default ARM macOS
    else:
        raise ValueError(f"Unsupported macOS architecture: {arch}")
elif system == "linux":  # Linux
    if arch in ["x86_64", "aarch64", "armv7l", "ppc64le"]:
        platform_tag = f"manylinux2014_{arch}"  # Default Linux tag
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

