#!/bin/bash

set -e


echo "=========================================="
echo "       Monki Labs Linux Installer"
echo "=========================================="


echo
echo "Checking Python..."


if ! command -v python3 >/dev/null 2>&1; then

    echo "ERROR: Python 3 not found."
    echo "Please use a Python-enabled RunPod environment."

    exit 1

fi


python3 --version

echo "Python detected."


echo
echo "Upgrading pip..."


python3 -m pip install --upgrade pip --break-system-packages


echo
echo "Checking NVIDIA GPU..."


if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi >/dev/null 2>&1; then

    echo "NVIDIA GPU detected."
    echo "Installing CUDA PyTorch..."

    python3 -m pip install \
        --upgrade \
        torch \
        torchvision \
        torchaudio \
        --index-url https://download.pytorch.org/whl/cu128 \
        --break-system-packages

else

    echo "No NVIDIA GPU detected."
    echo "Installing CPU PyTorch..."

    python3 -m pip install \
        --upgrade \
        torch \
        torchvision \
        torchaudio \
        --break-system-packages

fi


echo
echo "Installing Monki Labs dependencies..."


python3 -m pip install \
    --upgrade \
    -r requirements.txt \
    --break-system-packages


echo
echo "Checking FFmpeg..."


if ! command -v ffmpeg >/dev/null 2>&1; then

    echo "FFmpeg not found."
    echo "Installing FFmpeg..."

    if command -v apt-get >/dev/null 2>&1; then

        apt-get update
        apt-get install -y ffmpeg

    else

        echo "ERROR: apt-get is not available."
        echo "Please use an environment with FFmpeg installed."

        exit 1

    fi

else

    echo "FFmpeg detected."

fi


echo
echo "Checking Ollama..."


if ! command -v ollama >/dev/null 2>&1; then

    echo "Ollama not found."
    echo "Installing Ollama..."

    curl -fsSL https://ollama.com/install.sh | sh

else

    echo "Ollama detected."

fi


echo
echo "Reading Ollama configuration..."


OLLAMA_CONFIG=$(python3 -c "
import json

with open('config/ai_models.json', encoding='utf-8') as f:
    config = json.load(f)

model = config.get('models', {}).get('language_model', {})

print(model.get('provider', ''))
print(model.get('model', ''))
print(str(model.get('enabled', False)).lower())
")


OLLAMA_CONFIG_PROVIDER=$(echo "$OLLAMA_CONFIG" | sed -n '1p')
OLLAMA_CONFIG_MODEL=$(echo "$OLLAMA_CONFIG" | sed -n '2p')
OLLAMA_CONFIG_ENABLED=$(echo "$OLLAMA_CONFIG" | sed -n '3p')


if [ "$OLLAMA_CONFIG_ENABLED" = "true" ] && [ "$OLLAMA_CONFIG_PROVIDER" = "ollama" ]; then

    echo "Configured Ollama model: $OLLAMA_CONFIG_MODEL"


    echo
    echo "Starting Ollama..."


    if ! pgrep -x "ollama" >/dev/null 2>&1; then

        nohup ollama serve > /tmp/ollama.log 2>&1 &

        sleep 5

    else

        echo "Ollama is already running."

    fi


    echo
    echo "Checking Ollama service..."


    if ! curl -fsS http://localhost:11434/api/tags >/dev/null 2>&1; then

        echo "ERROR: Ollama service failed to start."

        echo
        echo "Ollama log:"
        cat /tmp/ollama.log

        exit 1

    fi


    echo
    echo "Checking configured Ollama model..."


    if ! ollama list | awk '{print $1}' | grep -Fxq "$OLLAMA_CONFIG_MODEL"; then

        echo "Model not found."
        echo "Pulling $OLLAMA_CONFIG_MODEL..."

        ollama pull "$OLLAMA_CONFIG_MODEL"

    else

        echo "Ollama model already available."

    fi

else

    echo "Ollama language model is disabled or provider is not Ollama."
    echo "Skipping Ollama model setup."

fi


echo
echo "Running hardware verification..."


python3 -c "
import torch

print('PyTorch:', torch.__version__)
print('CUDA Available:', torch.cuda.is_available())
print(
    'Device:',
    torch.cuda.get_device_name(0)
    if torch.cuda.is_available()
    else 'CPU'
)
"


echo
echo "=========================================="
echo "  Monki Labs Linux Installation Complete"
echo "=========================================="


echo
echo "Run:"
echo
echo "./run_linux.sh"
echo