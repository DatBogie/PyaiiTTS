REM Install Dependancies
pip3 install pyinstaller
pip3 install PyQt6
pip3 install elevenlabs
pip3 install requests

REM Build main.py
pyinstaller --onefile --noconsole main.py
