@echo off
cd /d "%~dp0"

IF NOT EXIST ".venv\Scripts\python.exe" (
    echo ERROR: Setup has not been completed.
    echo Run setup.bat first.
    pause
    exit /b 1
)

IF NOT EXIST "client_secret.json" (
    echo ERROR: client_secret.json is missing.
    pause
    exit /b 1
)

echo Starting YouTube Shorts Batch Scheduler...
".venv\Scripts\python.exe" main.py

echo.
echo Uploader finished.
pause