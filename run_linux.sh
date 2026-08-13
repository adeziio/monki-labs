#!/bin/bash

set -e


echo "=========================================="
echo "       Starting Monki Labs"
echo "=========================================="


echo
echo "Running Monki Labs..."


python3 main.py


if [ $? -ne 0 ]; then

    echo
    echo "Monki Labs exited with an error."

    exit 1

fi