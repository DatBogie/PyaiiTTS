#!/bin/bash

# Install Dependancies
pip3 install pyinstaller
pip3 install PyQt6
pip3 install elevenlabs
pip3 install requests

# Build main.py
pyinstaller --onefile main.py
