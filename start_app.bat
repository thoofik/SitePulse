@echo off
echo Starting SitePulse Audit Tool API v2.0 with WebSocket Support...
echo.
echo Using Python 3.11 with all required packages...
echo.

REM Set the Python path
set PYTHON_PATH=E:\Python311\python.exe

REM Check if Python 3.11 exists
if not exist "%PYTHON_PATH%" (
    echo ERROR: Python 3.11 not found at %PYTHON_PATH%
    echo Please check your Python installation.
    pause
    exit /b 1
)

echo Python 3.11 found at: %PYTHON_PATH%
echo.
echo Starting the Flask application with WebSocket support...
echo Server will be available at: http://localhost:5000
echo WebSocket endpoint: ws://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the Flask app
"%PYTHON_PATH%" app.py

pause
