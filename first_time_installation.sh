# To use different versions of python, you can use something like:
# pyenv global  3.11.6 3.10.13 3.9.18 3.12.3 3.13.0
PYTHON_VERSION=3.11
# Create your venv library:
python${PYTHON_VERSION} -m venv venv${PYTHON_VERSION}

# Activate your venv env
source venv${PYTHON_VERSION}/bin/activate

# Set the right library of keyword_detection
export KEYWORD_DETECTION_VERSION="2.0.3"

# Capture the output of the Python script
command=$(python install.py)

# Run the command
echo "Running: $command"
eval "$command"
