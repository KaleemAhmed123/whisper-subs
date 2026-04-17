@echo off
setlocal EnableDelayedExpansion

:: ============================================================
::  Whisper Subtitle Generator -- One-Click Setup
::  Run this ONCE after cloning the repo.
:: ============================================================

title Whisper Subtitle Generator -- Setup

echo.
echo  +--------------------------------------------------+
echo  ^|    Whisper Subtitle Generator  --  Setup        ^|
echo  +--------------------------------------------------+
echo.

:: -- 1. Check Python ------------------------------------------
echo  [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [ERROR] Python not found!
    echo  Please install Python 3.10+ from https://python.org
    echo  Make sure to check "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PY_VER=%%v
echo         OK  Python !PY_VER! found

:: -- 2. Check ffmpeg ------------------------------------------
echo  [2/6] Checking ffmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo         ffmpeg not found. Trying winget...
    winget install --id=Gyan.FFmpeg -e --silent
    if errorlevel 1 (
        echo.
        echo  [ERROR] Could not auto-install ffmpeg.
        echo  Please install manually:
        echo    1. Download from https://ffmpeg.org/download.html
        echo    2. Extract to C:\ffmpeg
        echo    3. Add C:\ffmpeg\bin to your System PATH
        echo    4. Re-run this setup script
        echo.
        pause
        exit /b 1
    )
    echo         OK  ffmpeg installed
) else (
    echo         OK  ffmpeg found
)

:: -- 3. Create virtual environment ----------------------------
echo  [3/6] Creating virtual environment...
if exist "%~dp0venv\Scripts\python.exe" (
    echo         OK  venv already exists, skipping
) else (
    if exist "%~dp0venv" (
        echo         Removing broken venv...
        rmdir /s /q "%~dp0venv"
    )
    python -m venv "%~dp0venv"
    if errorlevel 1 (
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo         OK  venv created
)

:: Use direct paths to venv executables (avoids activate issues)
set VENV_PYTHON=%~dp0venv\Scripts\python.exe
set VENV_PIP=%~dp0venv\Scripts\pip.exe

if not exist "%VENV_PYTHON%" (
    echo  [ERROR] venv\Scripts\python.exe not found after creation.
    echo  Try deleting the venv folder and re-running setup.bat
    pause
    exit /b 1
)

:: -- 4. Upgrade pip -------------------------------------------
echo  [4/6] Upgrading pip...
"%VENV_PYTHON%" -m pip install --upgrade pip --quiet --no-cache-dir
echo         OK  pip upgraded

:: -- 5. Install Python dependencies --------------------------
echo  [5/6] Installing dependencies (this may take a few minutes)...
echo.

:: Detect NVIDIA GPU
nvidia-smi >nul 2>&1
if not errorlevel 1 (
    echo         NVIDIA GPU detected! Installing PyTorch with CUDA...
    "%VENV_PYTHON%" -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126 --quiet --no-cache-dir
    if errorlevel 1 (
        echo         CUDA install failed, falling back to CPU version...
        "%VENV_PYTHON%" -m pip install torch torchvision torchaudio --quiet --no-cache-dir
    )
) else (
    echo         No NVIDIA GPU. Installing CPU-only PyTorch...
    "%VENV_PYTHON%" -m pip install torch torchvision torchaudio --quiet --no-cache-dir
    if errorlevel 1 (
        echo  [ERROR] Failed to install PyTorch. Check internet and retry.
        pause
        exit /b 1
    )
)
echo         OK  PyTorch installed

echo         Installing openai-whisper...
"%VENV_PYTHON%" -m pip install openai-whisper --quiet --no-cache-dir
if errorlevel 1 (
    echo  [ERROR] Failed to install openai-whisper. Check internet and retry.
    pause
    exit /b 1
)
echo         OK  openai-whisper installed

echo         Installing faster-whisper (optional speedup)...
"%VENV_PYTHON%" -m pip install faster-whisper --quiet --no-cache-dir
if errorlevel 1 (
    echo         faster-whisper skipped (optional, not required)
) else (
    echo         OK  faster-whisper installed
)

:: -- 6. Create config file ------------------------------------
echo  [6/6] Creating config file...
if not exist "%~dp0config.env" (
    (
        echo # -- Whisper Subtitle Generator Config --
        echo.
        echo # Path to your video folder ^(use forward slashes^)
        echo # Example: C:/Users/YourName/Videos   or   D:/My Course Videos
        echo VIDEO_FOLDER=C:/Path/To/Your/Videos
        echo.
        echo # Model: tiny, base, small, medium, large-v3
        echo # No GPU: use "small"    With GPU: use "medium" or "large-v3"
        echo MODEL=small
        echo.
        echo # Language code or "auto" to detect automatically
        echo # Examples: en, ur, ar, hi, fr, auto
        echo LANGUAGE=auto
        echo.
        echo # Skip videos that already have .srt files ^(true/false^)
        echo SKIP_EXISTING=true
        echo.
        echo # Output format: srt, vtt, both
        echo OUTPUT_FORMAT=srt
    ) > "%~dp0config.env"
    echo         OK  config.env created
) else (
    echo         OK  config.env already exists — skipping ^(delete it to regenerate^)
)

:: -- Done -----------------------------------------------------
echo.
echo  +--------------------------------------------------+
echo  ^|   Setup complete! Ready to generate subtitles   ^|
echo  +--------------------------------------------------+
echo.
echo   NEXT STEPS:
echo   1. Open config.env and set VIDEO_FOLDER to your videos path
echo   2. Double-click generate.bat to start
echo.
pause
