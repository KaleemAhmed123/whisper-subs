@echo off
setlocal EnableDelayedExpansion

:: ============================================================
::  Whisper Subtitle Generator -- Run
::  Double-click this after setup is done.
:: ============================================================

title Whisper Subtitle Generator -- Running

echo.
echo  +--------------------------------------------------+
echo  ^|    Whisper Subtitle Generator  --  Generate     ^|
echo  +--------------------------------------------------+
echo.

:: -- Check setup was run --------------------------------------
if not exist venv\Scripts\python.exe (
    echo  [ERROR] Virtual environment not found.
    echo  Please run setup.bat first!
    echo.
    pause
    exit /b 1
)

if not exist "%~dp0config.env" (
    echo  [ERROR] config.env not found.
    echo  Please run setup.bat first!
    echo.
    pause
    exit /b 1
)

:: Use direct path to venv python
set VENV_PYTHON=%~dp0venv\Scripts\python.exe

:: -- Read config.env ------------------------------------------
:: Reads KEY=VALUE lines, skips # comments and blank lines
:: VIDEO_FOLDER is read separately to preserve spaces in the path
echo  Reading config.env...

for /f "usebackq eol=# tokens=1,* delims==" %%A in ("%~dp0config.env") do (
    if /i "%%A"=="VIDEO_FOLDER"   set "VIDEO_FOLDER=%%B"
    if /i "%%A"=="MODEL"          set "MODEL=%%B"
    if /i "%%A"=="LANGUAGE"       set "LANGUAGE=%%B"
    if /i "%%A"=="SKIP_EXISTING"  set "SKIP_EXISTING=%%B"
    if /i "%%A"=="OUTPUT_FORMAT"  set "OUTPUT_FORMAT=%%B"
    if /i "%%A"=="HINGLISH"       set "HINGLISH=%%B"
    if /i "%%A"=="HF_TOKEN"       set "HF_TOKEN=%%B"
)

:: Trim spaces from simple single-word values only (NOT VIDEO_FOLDER)
set "MODEL=%MODEL: =%"
set "LANGUAGE=%LANGUAGE: =%"
set "SKIP_EXISTING=%SKIP_EXISTING: =%"
set "OUTPUT_FORMAT=%OUTPUT_FORMAT: =%"
set "HINGLISH=%HINGLISH: =%"
set "HF_TOKEN=%HF_TOKEN: =%"

:: Export HF_TOKEN so HuggingFace Hub picks it up (speeds up model downloads)
if not "!HF_TOKEN!"=="" (
    set "HF_TOKEN=!HF_TOKEN!"
    echo         HF_TOKEN     : set
) else (
    echo         HF_TOKEN     : not set ^(optional — see config.env^)
)

:: Strip any trailing spaces or carriage returns from VIDEO_FOLDER
:: (common when config.env is saved on Windows with CRLF line endings)
for /f "tokens=* delims= " %%X in ("!VIDEO_FOLDER!") do set "VIDEO_FOLDER=%%X"

echo         VIDEO_FOLDER  : !VIDEO_FOLDER!
echo         MODEL         : !MODEL!
echo         LANGUAGE      : !LANGUAGE!
echo         SKIP_EXISTING : !SKIP_EXISTING!
echo         OUTPUT_FORMAT : !OUTPUT_FORMAT!
echo         HINGLISH      : !HINGLISH!
echo.

:: -- Validate VIDEO_FOLDER is set -----------------------------
if "!VIDEO_FOLDER!"=="" (
    echo  [ERROR] VIDEO_FOLDER is not set in config.env
    echo  Open config.env and set it to your videos folder path.
    echo  Example:  VIDEO_FOLDER=D:/My Course Videos
    echo.
    pause
    exit /b 1
)

if "!VIDEO_FOLDER!"=="C:/Path/To/Your/Videos" (
    echo  [ERROR] VIDEO_FOLDER is still the default placeholder.
    echo  Open config.env and set it to your actual videos folder.
    echo  Example:  VIDEO_FOLDER=C:/Users/YourName/Videos
    echo.
    pause
    exit /b 1
)

:: -- Run the Python script ------------------------------------
"%VENV_PYTHON%" "%~dp0scripts\generate_subtitles.py" ^
    --folder "!VIDEO_FOLDER!" ^
    --model "!MODEL!" ^
    --language "!LANGUAGE!" ^
    --skip-existing "!SKIP_EXISTING!" ^
    --output-format "!OUTPUT_FORMAT!" ^
    --hinglish "!HINGLISH!"

echo.
echo  Press any key to exit...
pause >nul
