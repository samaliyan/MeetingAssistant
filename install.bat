@echo off
setlocal
cd /d "%~dp0"
title Meeting Assistant - install

echo.
echo  [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
  echo.
  echo  Python was not found.
  echo  Install Python 3.12 from python.org and tick "Add python.exe to PATH".
  pause
  exit /b 1
)
python -c "import sys; sys.exit(0 if sys.version_info[:2] >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
  echo.
  echo  This Python is too old. Install Python 3.12 from python.org
  echo  and tick "Add python.exe to PATH", then run this file again.
  pause
  exit /b 1
)
python -c "import sys; sys.exit(0 if sys.version_info[:2] <= (3, 13) else 1)" >nul 2>&1
if errorlevel 1 (
  echo  Note: this Python is newer than the program was tested with ^(3.10 - 3.13^).
  echo  If a package fails to install, install Python 3.12 from python.org.
)

echo  [2/4] Preparing the program folder...
if not exist venv\Scripts\python.exe (
  python -m venv venv
  if errorlevel 1 (
    echo  Could not create the Python environment.
    pause
    exit /b 1
  )
)
rem Packages of the old version are not needed any more
venv\Scripts\python.exe -m pip uninstall -y -q PySide6 PySide6_Essentials PySide6_Addons shiboken6 groq >nul 2>&1

echo  [3/4] Installing packages (an internet connection is needed)...
set "PIPQ=-q --timeout 60 --retries 10 --disable-pip-version-check"
venv\Scripts\python.exe -m pip install %PIPQ% --upgrade pip
venv\Scripts\python.exe -m pip install %PIPQ% --upgrade -r requirements.txt
if errorlevel 1 (
  echo.
  echo  Installation failed. Check your internet connection and run install.bat again.
  pause
  exit /b 1
)

echo        Adding the local model engine (optional)...
venv\Scripts\python.exe -m pip install %PIPQ% "ctranslate2>=4.4" "tokenizers>=0.15" tqdm >nul 2>&1 && venv\Scripts\python.exe -m pip install %PIPQ% --no-deps "faster-whisper>=1.1" >nul 2>&1
if errorlevel 1 echo        Could not add it - the program works anyway, just without the local model.

echo        Adding the local AI engine (translation and answers on this computer, optional)...
venv\Scripts\python.exe -m pip install %PIPQ% --prefer-binary --only-binary=llama-cpp-python "llama-cpp-python>=0.3.19" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu >nul 2>&1
if errorlevel 1 echo        Could not add it - the program works anyway, just without the local AI model.

echo        Adding the hidden-window support (hide from screen sharing, optional)...
venv\Scripts\python.exe -m pip install %PIPQ% "pywebview>=5,<7" >nul 2>&1
if errorlevel 1 echo        Could not add it - the program works anyway, just without hiding from screen sharing.

echo  [4/4] Creating the desktop shortcut...
venv\Scripts\python.exe app.py --make-shortcut

echo.
echo  Done. Open "Meeting Assistant" from your desktop (or double-click run.bat).
echo.
pause
