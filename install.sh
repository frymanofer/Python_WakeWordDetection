PYTHON_VERSION=3.12

# Activate your venv env
source venv${PYTHON_VERSION}/bin/activate

# Set the right library of keyword_detection
export KEYWORD_DETECTION_VERSION="2.1.0"

# Capture the output of the Python script
command=$(python install.py)

# Run the command
echo "Running: $command"
eval "$command"
