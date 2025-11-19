@echo off
echo ========================================
echo THE HIVE - Distributed Test
echo Launching Orchestrator and Worker
echo ========================================
echo.

cd /d "%~dp0"

REM Start Orchestrator in new window
echo [1/2] Starting Orchestrator...
start "Hive Orchestrator" cmd /k "set PYTHONPATH=%CD% && venv\Scripts\python.exe test_orchestrator.py"

REM Wait for orchestrator to start
timeout /t 5 /nobreak > nul

REM Start Gemini Worker in new window
echo [2/2] Starting Gemini Worker...
start "Gemini Worker" cmd /k "set PYTHONPATH=%CD% && venv\Scripts\python.exe app\distributed\worker_fixed.py"

echo.
echo ========================================
echo Both services launched!
echo ========================================
echo.
echo Check the opened windows:
echo - "Hive Orchestrator" - Flask server
echo - "Gemini Worker" - Gemini API worker
echo.
echo Test with: curl http://localhost:5000/api/workers/stats
echo.
pause
