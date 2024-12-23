@echo off

REM Create venv
python -m venv .\.venv

REM Source venv
call .\.venv\Scripts\activate

REM Install dependancies
pip install -r .\requirements.txt

REM Build and copy assets
pyinstaller --onefile --noconsole --name PyaiiTTS --icon .\.web-assets\PyaiiTTS-Logo.ico .\main.py
xcopy /e /h /y /i .\assets .\dist\assets

REM Finish
echo "Press return to exit."
pause
