@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
title Meeting Assistant - build the exe

echo.
echo  Builds a small MeetingAssistant.exe once. After that Python is not needed.
echo  An internet connection is needed. It takes about 3-5 minutes.
echo.

rem ---------- 1. a clean, temporary build environment (only what the program needs) ----------
echo  [1/4] Preparing a clean build environment...
set "PY="
python --version >nul 2>&1 && set "PY=python"
if not defined PY if exist venv\Scripts\python.exe set "PY=venv\Scripts\python.exe"
if not defined PY (
  echo  Python was not found. Install Python 3.12 from python.org
  echo  and tick "Add python.exe to PATH", then run this file again.
  pause
  exit /b 1
)
%PY% -c "import sys; sys.exit(0 if sys.version_info[:2] >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
  echo  This Python is too old. Install Python 3.12 from python.org, then run this file again.
  pause
  exit /b 1
)
%PY% -c "import sys; sys.exit(0 if sys.version_info[:2] <= (3, 13) else 1)" >nul 2>&1
if errorlevel 1 (
  echo  Note: this Python is newer than the program was tested with ^(3.10 - 3.13^).
  echo  If a package fails to install, install Python 3.12 from python.org.
)
if exist .buildenv rmdir /s /q .buildenv
%PY% -m venv .buildenv
if errorlevel 1 (
  echo  Could not create the build environment.
  pause
  exit /b 1
)
set "BPY=.buildenv\Scripts\python.exe"
rem  slow or unstable internet: wait longer and try more often; details go to pip_log.txt
set "PIPQ=-q --no-cache-dir --timeout 60 --retries 10 --disable-pip-version-check"
if exist pip_log.txt del /q pip_log.txt

echo  [2/4] Downloading packages (no cache is kept on disk)...
%BPY% -m pip install %PIPQ% --upgrade pip >>pip_log.txt 2>&1
%BPY% -m pip install %PIPQ% -r requirements.txt pyinstaller >>pip_log.txt 2>&1
if errorlevel 1 (
  echo.
  echo  Download or installation failed. Check your internet connection ^(and the lines below^), then run this file again.
  echo  The last lines of pip_log.txt:
  powershell -NoProfile -Command "Get-Content pip_log.txt -Tail 8"
  rmdir /s /q .buildenv
  pause
  exit /b 1
)

rem  The engine for the local model (speech to text on this computer). The model files
rem  themselves are NOT put in the exe - they are downloaded or chosen inside the program.
rem  If this part fails, the program is still built, only without the local model.
echo        Adding the local model engine...
set "LOCALOPTS="
rem  its helpers first, then faster-whisper itself WITHOUT the two packages we do not need
rem  (av reads audio files, onnxruntime is an extra voice detector - the program has its own)
%BPY% -m pip install %PIPQ% "ctranslate2>=4.4" "tokenizers>=0.15" tqdm >>pip_log.txt 2>&1
if errorlevel 1 goto nolocal
%BPY% -m pip install %PIPQ% --no-deps "faster-whisper>=1.1" >>pip_log.txt 2>&1
if errorlevel 1 goto nolocal
%BPY% -c "import sys,types;sys.modules.setdefault('av',types.ModuleType('av'));import faster_whisper,ctranslate2" >>pip_log.txt 2>&1
if errorlevel 1 goto nolocal
set "LOCALOPTS=--hidden-import faster_whisper --collect-binaries ctranslate2"
echo        OK - the local model engine is included.
goto afterlocal
:nolocal
echo        Could not add it ^(see pip_log.txt^). The program is built anyway - just without the local model.
%BPY% -m pip uninstall -y -q faster-whisper ctranslate2 >nul 2>&1
:afterlocal

rem  The engine for the local AI model (translation and answers on this computer). Ready-made
rem  packages only (no compiler is needed); if there is none for this Python, it is simply left out.
echo        Adding the local AI engine (translation and answers on this computer)...
set "LLMOK="
%BPY% -m pip install %PIPQ% --prefer-binary --only-binary=llama-cpp-python "llama-cpp-python>=0.3.19" --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu >>pip_log.txt 2>&1
if errorlevel 1 goto nollm
%BPY% -c "import llama_cpp" >>pip_log.txt 2>&1
if errorlevel 1 goto nollm
set "LLMOK=1"
echo        OK - the local AI engine is included.
goto afterllm
:nollm
echo        Could not add it ^(see pip_log.txt^). The program is built anyway - just without the local AI model.
%BPY% -m pip uninstall -y -q llama-cpp-python >nul 2>&1
:afterllm

rem ---------- 2. build ONE exe file ----------
rem  (The PyInstaller options are in tools\build.py - the same file GitHub uses for the releases.
rem   UPX is not used: inside a single exe it saves very little and makes antivirus warnings more likely.)
echo  [3/4] Building the exe (please wait)...
if exist build rmdir /s /q build
if exist dist\MeetingAssistant.exe del /q dist\MeetingAssistant.exe
%BPY% tools\build.py > build_log.txt 2>&1
if errorlevel 1 (
  echo.
  echo  BUILD FAILED. The last lines of build_log.txt:
  echo  ------------------------------------------------
  powershell -NoProfile -Command "Get-Content build_log.txt -Tail 25"
  echo  ------------------------------------------------
  echo  Send the file build_log.txt for help.
  pause
  exit /b 1
)

rem ---------- 3. your settings, shortcut, clean-up ----------
echo  [4/4] Copying your settings and meetings, cleaning up...
rem  everything the program writes lives in ONE folder next to the exe: dist\Data
if not exist dist\Data mkdir dist\Data
rem  files of earlier builds that lay next to the exe go into Data
for %%F in (config.json config.json.bak app.log app.log.old .port) do if exist "dist\%%F" move /y "dist\%%F" "dist\Data\" >nul
for %%D in (meetings models .window) do if exist "dist\%%D" if not exist "dist\Data\%%D" move "dist\%%D" "dist\Data\" >nul
rem  settings and meetings of the Python version (this folder) are COPIED (both versions keep them);
rem  downloaded models are MOVED (they are big) - after this, the model is used by the exe version
if exist config.json if not exist dist\Data\config.json copy /y config.json dist\Data\ >nul
if exist Data\config.json if not exist dist\Data\config.json copy /y Data\config.json dist\Data\ >nul
if exist meetings xcopy /e /i /y /q meetings dist\Data\meetings >nul
if exist Data\meetings xcopy /e /i /y /q Data\meetings dist\Data\meetings >nul
if exist models if not exist dist\Data\models move models dist\Data\models >nul
rem  settings and meetings of an earlier folder-style build
if exist dist\MeetingAssistant\config.json if not exist dist\Data\config.json copy /y dist\MeetingAssistant\config.json dist\Data\ >nul
if exist dist\MeetingAssistant\meetings xcopy /e /i /y /q dist\MeetingAssistant\meetings dist\Data\meetings >nul
if exist dist\MeetingAssistant rmdir /s /q dist\MeetingAssistant
dist\MeetingAssistant.exe --make-shortcut
for %%D in (build .buildenv __pycache__ tools\__pycache__) do if exist "%%D" rmdir /s /q "%%D"
if exist MeetingAssistant.spec del /q MeetingAssistant.spec
if defined LOCALOPTS if defined LLMOK if exist pip_log.txt del /q pip_log.txt

for /f %%S in ('powershell -NoProfile -Command "[math]::Round((Get-Item 'dist\MeetingAssistant.exe').Length/1MB)"') do set "SIZE=%%S"

echo.
echo  DONE.  MeetingAssistant.exe - !SIZE! MB, one single file.
if defined LOCALOPTS echo  Local model engine: included.
if defined LLMOK echo  Local AI engine ^(translation and answers^): included.
if not defined LLMOK echo  Local AI engine: NOT included ^(details in pip_log.txt^).
if not defined LOCALOPTS echo  Local model engine: NOT included ^(details in pip_log.txt - usually slow internet: run this file again^).
echo  It is in:  %~dp0dist
echo  Start it with the "Meeting Assistant" icon on your desktop.
echo  Your settings, meetings and log are kept in the folder "Data" next to the exe.
echo.

rem ---------- old Python version is not needed any more (optional clean-up) ----------
set "OLD="
if exist venv set "OLD=1"
if exist .window set "OLD=1"
if defined OLD (
  echo  The old Python version of the program ^(folders "venv" and ".window"^) is not needed any more.
  choice /C YN /M "  Delete it now to free disk space"
  if !errorlevel! EQU 1 (
    if exist venv rmdir /s /q venv
    if exist .window rmdir /s /q .window
    echo  Deleted.
  )
  echo.
)
explorer /select,"%~dp0dist\MeetingAssistant.exe"
pause
