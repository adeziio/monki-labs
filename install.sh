#!/bin/bash

set -e


echo "=========================================="
echo "      Monki Labs Linux Installer"
echo "=========================================="


echo
echo "Checking Python..."

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: Python 3 not found."
    echo "Please install Python 3.12 or newer."
    exit 1
fi

python3 --version

echo "Python detected."


echo
echo "Checking FFmpeg..."

if ! command -v ffmpeg >/dev/null 2>&1; then

    echo "FFmpeg not found."

    if command -v apt-get >/dev/null 2>&1; then

        echo "Installing FFmpeg..."

        sudo apt-get update
        sudo apt-get install -y ffmpeg

    else

        echo "ERROR: FFmpeg is not installed."
        echo "Please install FFmpeg manually."
        exit 1

    fi

else

    echo "FFmpeg detected."

fi


echo
echo "Creating virtual environment..."

if [ ! -d ".venv" ]; then

    python3 -m venv .venv

fi

echo "Virtual environment ready."


echo
echo "Activating environment..."

source .venv/bin/activate


echo
echo "Upgrading pip..."

python -m pip install --upgrade pip


echo
echo "Checking PyTorch..."

if python -c "import torch" >/dev/null 2>&1; then

    echo "PyTorch already installed."

    python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA Available:', torch.cuda.is_available())"

else

    echo "PyTorch not found."
    echo "Installing PyTorch dependencies..."

    python -m pip install --upgrade -r requirements-pytorch.txt

fi


echo
echo "Installing Monki Labs dependencies..."

python -m pip install --upgrade -r requirements.txt


echo
echo "Running hardware verification..."

python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"


echo
echo "=========================================="
echo "      Monki Labs Installation Complete"
echo "=========================================="

echo
echo "Run the application with:"
echo
echo "./run.sh"
echo