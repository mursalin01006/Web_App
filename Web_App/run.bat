@echo off
echo ========================================================
echo SQLi Shield - Local Web Server Startup
echo ========================================================

:: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10 or higher.
    pause
    exit /b 1
)

echo [1/3] Setting up Python virtual environment...
IF NOT EXIST "venv" (
    python -m venv venv
    echo Virtual environment created successfully.
) ELSE (
    echo Virtual environment already exists.
)

echo [2/3] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

echo [3/3] Starting Flask Application...
echo.
echo The app will open in your browser automatically.
echo Press CTRL+C in this window to stop the server.
echo.

:: Start the browser and the app
start http://127.0.0.1:5000
python app.py

pause
