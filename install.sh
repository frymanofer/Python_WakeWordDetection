
# Create your venv library:
#python3.12 -m venv venv3.12

# Activate your venv env
source venv3.12/bin/activate

# Capture the output of the Python script
command=$(python install.py)

# Run the command
echo "Running: $command"
eval "$command"
