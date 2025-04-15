@echo off
setlocal

REM Define Python version
set PYTHON_VERSION=3.12
set PYTHON_VERSION_SHORT=312

REM Ensure Python 3.12 is installed and used
py -%PYTHON_VERSION% --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python %PYTHON_VERSION% is not installed. Please install it from https://www.python.org/downloads/
    exit /b 1
)

REM Ensure pip is updated
py -%PYTHON_VERSION% -m ensurepip
py -%PYTHON_VERSION% -m pip install --upgrade pip

REM Create virtual environment
py -%PYTHON_VERSION% -m venv venv%PYTHON_VERSION_SHORT%

REM Activate virtual environment
call venv%PYTHON_VERSION_SHORT%\Scripts\activate

REM Verify Python version inside venv
py --version

REM Set the right library of keyword_detection
set KEYWORD_DETECTION_VERSION=2.0.1

REM Run the Python install script directly
py win_install.py

endlocal

