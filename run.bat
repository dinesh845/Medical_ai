@echo off
REM Medical AI Application Launcher
REM This script sets up and runs the Medical AI application

echo.
echo ========================================
echo   Medical AI Pre-Diagnosis System
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install/Update dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Create necessary directories
if not exist "uploads\images\" mkdir uploads\images
if not exist "uploads\audio\" mkdir uploads\audio
if not exist "data\" mkdir data

echo.
echo ========================================
echo   Starting Medical AI Server...
echo ========================================
echo.
echo Server will be available at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Run the application
python app.py

pause
