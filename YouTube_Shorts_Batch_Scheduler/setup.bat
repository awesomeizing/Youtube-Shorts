@echo off
cd /d "%~dp0"

echo Checking Python installation...
py --version >nul 2>&1

IF ERRORLEVEL 1 (
    echo Python is not installed or the Python launcher is unavailable.
    pause
    exit /b 1
)

echo Creating virtual environment...
py -m venv .venv

IF ERRORLEVEL 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

echo Installing requirements...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt

IF ERRORLEVEL 1 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

echo.
echo =========================================
echo Setup completed successfully!
echo =========================================
pause