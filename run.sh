#!/bin/bash

set -e


echo "=========================================="
echo "         Monki Labs"
echo "=========================================="


if [ ! -d ".venv" ]; then

    echo
    echo "ERROR: Virtual environment not found."
    echo "Run ./install.sh first."
    exit 1

fi


echo
echo "Activating virtual environment..."

source .venv/bin/activate


echo
echo "Running Monki Labs..."

python main.py