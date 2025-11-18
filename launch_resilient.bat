@echo off
REM Lanza sistema distribuido con worker resiliente (maneja 429 errors)

echo.
echo ========================================
echo   LANZANDO SISTEMA DISTRIBUIDO
echo   Worker: Gemini Resilient (Anti-429)
echo ========================================
echo.

REM Launch Orchestrator (sin cambios)
echo [1/2] Lanzando Orchestrator...
start "Hive Orchestrator" cmd /k "cd /d %~dp0 && set PYTHONPATH=%~dp0 && venv\Scripts\python.exe test_orchestrator.py"

REM Wait for orchestrator to start
timeout /t 5 /nobreak

REM Launch Resilient Gemini Worker
echo [2/2] Lanzando Gemini Worker Resiliente...
start "Gemini Resilient Worker" cmd /k "cd /d %~dp0 && set PYTHONPATH=%~dp0 && venv\Scripts\python.exe app/distributed/worker_gemini_resilient.py"

echo.
echo ========================================
echo   SERVICIOS LANZADOS
echo ========================================
echo.
echo   [*] Orchestrator: http://localhost:5000
echo   [*] Worker: Gemini con retry logic
echo.
echo Caracteristicas del Worker Resiliente:
echo   - Rate limiting: 10 req/min (conservador)
echo   - Retry automatico en 429 errors
echo   - Exponential backoff: 2s, 4s, 8s, 16s, 32s
echo   - Max retries: 5
echo   - Poll interval: 10s (menos agresivo)
echo.
echo Verifica estado en:
echo   curl http://localhost:5000/api/workers/stats
echo.
echo Los servicios estan en ventanas CMD separadas.
echo Cierra este mensaje cuando estes listo.
echo ========================================
echo.
pause
