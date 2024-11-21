PYTHON_VERSION=3.12
# Create your venv library:
python${PYTHON_VERSION} -m venv venv${PYTHON_VERSION}

# Activate your venv env
source venv${PYTHON_VERSION}/bin/activate

# Set the right library of keyword_detection
export KEYWORD_DETECTION_VERSION="1.0.17"

# Capture the output of the Python script
command=$(python install.py)

# Run the command
echo "Running: $command"
eval "$command"
