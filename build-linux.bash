#!/bin/bash

# Create venv
python3 -m venv ./.venv

# Source venv
source ./.venv/bin/activate

# Install dependancies
pip3 install -r ./requirements.txt

# Build and copy assets
pyinstaller --onefile -n PyaiiTTS ./main.py && chmod +x ./dist/PyaiiTTS && cp -rf ./assets ./dist

# Finish
read -p "Press return to exit."