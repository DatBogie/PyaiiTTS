### PyaiiTTS
**Py**<sub>thon</sub>**a**<sub>rtificial</sub>**i**<sub>ntelligence</sub>**i**<sub>nterface</sub>**T**<sub>ext</sub>**T**<sub>o</sub>**S**<sub>peech</sub><br>_<sub>100% didn't accidentally spell it with an extra i on accident or anything</sub>_<br>
A simple python program that generates an mp3 of an AI voice using [elevenlabs](https://elevenlabs.io).

> [!Note]
All versions of PyaiiTTS support Linux and Windows.
**MacOS is only supported for ≥v1.3**
If you want to use an older version on MacOS, please [build from an older version](#build-version-from-zip-archive).

> [!Important]
**Please don't download from the releases page directly. _Instead..._**
### [DOWNLOAD HERE](https://github.com/DatBogie/PyaiiTTS-Installer/releases/latest)

*Or...*

> [!Important]
The following installation methods require Python to be installed.
    • On Linux, it should already be installed.
    • On Windows, the easiest way is to do so is to simply install it from the Microsoft Store.
    • On MacOS, it should already be installed. If you encounter problems, try installing the latest version [here](https://www.python.org/downloads/).
    **Make sure to add Python to PATH as well!**

### Build from Source
> [!Note]
    Make sure Git is installed.
    • Windows: [download here](https://gitforwindows.org)
    • Linux:
    &nbsp;&nbsp;&nbsp;&nbsp;Install from your package manager in a terminal if it isn't already, eg.:
    &nbsp;&nbsp;&nbsp;&nbsp;◦ `#`​```apt install git # Debian```
    &nbsp;&nbsp;&nbsp;&nbsp;◦ `#`​```pacman -S git # Arch```
    • MacOS: `$`​```git --version```

1. Clone this repo.
    Run the following in a terminal emulator or PowerShell:
    ```git clone https://github.com/DatBogie/PyaiiTTS && cd PyaiiTTS```
2. Run the build file for your OS.
    This will create a venv and install all needed Python modules before building an executable.
    You will find the executable in `./dist/` (`.\dist\` on Windows)
    - **Linux:**
    `$`​```./build-linux.sh```
    - **Windows:**
    ```.\build-windows.bat```
    - **MacOS:**
    `$`​```./build-mac.sh```

*Or or...*

### Build Version from ZIP Archive
> [!Note]
This can be useful for using older versions on a Mac. For other versions.
For other OSes, please just use [PyaiiTTS-Installer](https://github.com/DatBogie/PyaiiTTS-Installer/releases).

&nbsp;
1. Download the ZIP archive of the version you would like (you can find those [here](https://github.com/DatBogie/PyaiiTTS/releases)) and extract its contents into a folder.
2. Download the `requirements.txt` file from this repo [here](requirements.txt) and put it in the folder your extracted into above.
3. Download the build script for your OS from this repo and place it in the aformentioned folder.
    - **Linux:** [build-linux.sh](build-linux.sh)
    - **Windows:** [build-windows.bat](build-windows.bat)
    - **MacOS:** [build-mac.sh](build-mac.sh)
4. Run the build file. An executable file should be created in the `dist` folder.

&nbsp;
> [!Note]
PyaiiTTS will create files such as `conf.json`, `pref.json`, `themes.json`, and `voices.json` in the directory that the executable is placed in!

&nbsp;
### Screenshot (Windows 11):
![](https://raw.githubusercontent.com/DatBogie/PyaiiTTS/refs/heads/main/.web-assets/pyaiitts.png)
