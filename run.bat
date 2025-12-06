@echo off
echo ========================================
echo  Demand Forecasting Application
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
echo.

REM Install/upgrade dependencies
echo Installing dependencies...
pip install -r requirements_auth.txt
echo.

REM Create necessary directories
if not exist "uploads\" mkdir uploads
if not exist "models\" mkdir models

REM Run the application
echo ========================================
echo  Starting Flask Application...
echo  Access at: http://localhost:5000
echo ========================================
echo.
python run.py

pause
