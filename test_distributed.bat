@echo off
echo ========================================
echo THE HIVE - Distributed Testing
echo ========================================
echo.

REM Check virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate
call venv\Scripts\activate.bat

REM Install deps
echo Installing dependencies...
pip install -q google-generativeai psutil requests python-dotenv flask

echo.
echo ========================================
echo Starting Orchestrator (Flask)...
echo ========================================
start "Orchestrator" cmd /k "venv\Scripts\activate.bat && python app/main.py"

timeout /t 8 /nobreak

echo.
echo ========================================
echo Starting Gemini Worker...
echo ========================================
start "Gemini Worker" cmd /k "venv\Scripts\activate.bat && python app/distributed/worker_fixed.py"

echo.
echo ========================================
echo Services started in separate windows!
echo ========================================
echo.
echo Orchestrator: http://localhost:5000
echo Worker Stats: http://localhost:5000/api/workers/stats
echo.
pause
