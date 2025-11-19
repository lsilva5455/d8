@echo off
setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║     THE HIVE - SISTEMA DISTRIBUIDO FULL TEST           ║
echo ║     Prueba Automatica Completa                         ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"
set PYTHONPATH=%CD%

REM ===== PASO 1: LIMPIAR PROCESOS ANTERIORES =====
echo [PASO 1/7] Limpiando procesos anteriores...
taskkill /F /FI "WINDOWTITLE eq Hive Orchestrator*" 2>nul
taskkill /F /FI "WINDOWTITLE eq Gemini Worker*" 2>nul
timeout /t 2 /nobreak >nul
echo    ✓ Procesos limpiados
echo.

REM ===== PASO 2: INICIAR ORCHESTRADOR =====
echo [PASO 2/7] Iniciando Orchestrator...
start "Hive Orchestrator" /MIN cmd /k "title Hive Orchestrator && set PYTHONPATH=%CD% && venv\Scripts\python.exe test_orchestrator.py"
timeout /t 5 /nobreak >nul
echo    ✓ Orchestrator iniciado
echo.

REM ===== PASO 3: INICIAR WORKER =====
echo [PASO 3/7] Iniciando Gemini Worker...
start "Gemini Worker" /MIN cmd /k "title Gemini Worker && set PYTHONPATH=%CD% && venv\Scripts\python.exe app\distributed\worker_fixed.py"
timeout /t 5 /nobreak >nul
echo    ✓ Worker iniciado
echo.

REM ===== PASO 4: VERIFICAR CONEXIÓN =====
echo [PASO 4/7] Verificando conexion del sistema...
timeout /t 3 /nobreak >nul
powershell -Command "$stats = Invoke-RestMethod -Uri 'http://localhost:5000/api/workers/stats'; Write-Host '   Workers online:' $stats.workers.online -ForegroundColor Green; Write-Host '   Worker type:' ($stats.workers.by_type | ConvertTo-Json -Compress) -ForegroundColor Green"

if %ERRORLEVEL% NEQ 0 (
    echo    ✗ Error: No se pudo conectar al orchestrador
    pause
    exit /b 1
)
echo    ✓ Sistema conectado
echo.

REM ===== PASO 5: TEST OPCIÓN A - CONTENT EMPIRE =====
echo [PASO 5/7] ════════════════════════════════════════════
echo              TEST OPCION A: CONTENT EMPIRE
echo              ════════════════════════════════════════════
echo.
echo    Simulando: 3 agentes generando contenido SEO
echo    Platform: WordPress, Medium, Blog
echo.

REM Task 1: Blog post sobre IA
echo    [A1] Enviando tarea: Blog post sobre IA...
powershell -Command "$body = @{ prompt = 'Write a 150-word SEO-optimized blog introduction about Artificial Intelligence trends in 2025. Include keywords: AI, machine learning, future tech.' } | ConvertTo-Json; try { $response = Invoke-RestMethod -Uri 'http://localhost:5000/api/test/task' -Method POST -Body $body -ContentType 'application/json'; Write-Host '        ✓ Task ID:' $response.task_id -ForegroundColor Green } catch { Write-Host '        ✗ Error' -ForegroundColor Red }"
timeout /t 3 /nobreak >nul

REM Task 2: Social media content
echo    [A2] Enviando tarea: Social media viral post...
powershell -Command "$body = @{ prompt = 'Create a viral Twitter thread (3 tweets) about productivity hacks for remote workers. Make it engaging and shareable.' } | ConvertTo-Json; try { $response = Invoke-RestMethod -Uri 'http://localhost:5000/api/test/task' -Method POST -Body $body -ContentType 'application/json'; Write-Host '        ✓ Task ID:' $response.task_id -ForegroundColor Green } catch { Write-Host '        ✗ Error' -ForegroundColor Red }"
timeout /t 3 /nobreak >nul

REM Task 3: Product review
echo    [A3] Enviando tarea: Product review...
powershell -Command "$body = @{ prompt = 'Write a 100-word product review for a fictional smart home device. Focus on benefits and user experience.' } | ConvertTo-Json; try { $response = Invoke-RestMethod -Uri 'http://localhost:5000/api/test/task' -Method POST -Body $body -ContentType 'application/json'; Write-Host '        ✓ Task ID:' $response.task_id -ForegroundColor Green } catch { Write-Host '        ✗ Error' -ForegroundColor Red }"

echo.
echo    ⏳ Esperando que workers procesen tareas (15 segundos)...
timeout /t 15 /nobreak >nul

echo.
echo    📊 Estadisticas OPCION A:
powershell -Command "$stats = Invoke-RestMethod -Uri 'http://localhost:5000/api/workers/stats'; Write-Host '       - Tareas completadas:' $stats.tasks.completed -ForegroundColor Cyan; Write-Host '       - Tareas fallidas:' $stats.tasks.failed -ForegroundColor Yellow; Write-Host '       - Success rate:' $stats.performance.success_rate'%%' -ForegroundColor Green"
echo.

REM ===== PASO 6: TEST OPCIÓN B - DEVICE FARM =====
echo [PASO 6/7] ════════════════════════════════════════════
echo              TEST OPCION B: DEVICE FARM
echo              ════════════════════════════════════════════
echo.
echo    Simulando: Automatizacion de apps (Instagram, TikTok)
echo    Note: Sin Selenium, solo test de prompts
echo.

REM Task 1: Instagram automation script
echo    [B1] Enviando tarea: Instagram automation logic...
powershell -Command "$body = @{ prompt = 'Generate Python pseudo-code for an Instagram bot that: 1) Logs in, 2) Searches hashtag, 3) Likes 10 posts. Use polymorphic variable names to avoid detection. Output: function signatures only.' } | ConvertTo-Json; try { $response = Invoke-RestMethod -Uri 'http://localhost:5000/api/test/task' -Method POST -Body $body -ContentType 'application/json'; Write-Host '        ✓ Task ID:' $response.task_id -ForegroundColor Green } catch { Write-Host '        ✗ Error' -ForegroundColor Red }"
timeout /t 3 /nobreak >nul

REM Task 2: TikTok comment bot
echo    [B2] Enviando tarea: TikTok comment strategy...
powershell -Command "$body = @{ prompt = 'List 5 engaging comment templates for TikTok videos about cooking. Make them human-like and varied to avoid bot detection.' } | ConvertTo-Json; try { $response = Invoke-RestMethod -Uri 'http://localhost:5000/api/test/task' -Method POST -Body $body -ContentType 'application/json'; Write-Host '        ✓ Task ID:' $response.task_id -ForegroundColor Green } catch { Write-Host '        ✗ Error' -ForegroundColor Red }"
timeout /t 3 /nobreak >nul

REM Task 3: Error handling code
echo    [B3] Enviando tarea: Self-healing error handler...
powershell -Command "$body = @{ prompt = 'Write a Python try-except block that catches NoSuchElementException and retries with alternative CSS selectors. Show 3 selector variations.' } | ConvertTo-Json; try { $response = Invoke-RestMethod -Uri 'http://localhost:5000/api/test/task' -Method POST -Body $body -ContentType 'application/json'; Write-Host '        ✓ Task ID:' $response.task_id -ForegroundColor Green } catch { Write-Host '        ✗ Error' -ForegroundColor Red }"

echo.
echo    ⏳ Esperando que workers procesen tareas (15 segundos)...
timeout /t 15 /nobreak >nul

echo.
echo    📊 Estadisticas OPCION B:
powershell -Command "$stats = Invoke-RestMethod -Uri 'http://localhost:5000/api/workers/stats'; Write-Host '       - Tareas completadas:' $stats.tasks.completed -ForegroundColor Cyan; Write-Host '       - Tareas fallidas:' $stats.tasks.failed -ForegroundColor Yellow; Write-Host '       - Success rate:' $stats.performance.success_rate'%%' -ForegroundColor Green"
echo.

REM ===== PASO 7: ESTADÍSTICAS FINALES =====
echo [PASO 7/7] ════════════════════════════════════════════
echo              ESTADISTICAS FINALES DEL SISTEMA
echo              ════════════════════════════════════════════
echo.

powershell -Command "$stats = Invoke-RestMethod -Uri 'http://localhost:5000/api/workers/stats'; Write-Host '📊 WORKERS:' -ForegroundColor Cyan; Write-Host '   Total:' $stats.workers.total; Write-Host '   Online:' $stats.workers.online -ForegroundColor Green; Write-Host '   Busy:' $stats.workers.busy; Write-Host '   Types:' ($stats.workers.by_type | ConvertTo-Json -Compress); Write-Host ''; Write-Host '📈 TASKS:' -ForegroundColor Cyan; Write-Host '   Total procesadas:' $stats.tasks.total; Write-Host '   Completadas:' $stats.tasks.completed -ForegroundColor Green; Write-Host '   Fallidas:' $stats.tasks.failed -ForegroundColor Red; Write-Host '   Pendientes:' $stats.tasks.pending -ForegroundColor Yellow; Write-Host ''; Write-Host '⚡ PERFORMANCE:' -ForegroundColor Cyan; Write-Host '   Success rate:' $stats.performance.success_rate'%%' -ForegroundColor Green; Write-Host '   Total completed:' $stats.performance.total_completed; Write-Host '   Total failed:' $stats.performance.total_failed"

echo.
echo ════════════════════════════════════════════════════════════
echo.
echo ✅ PRUEBA COMPLETA FINALIZADA
echo.
echo 🔍 Para ver logs detallados, revisa las ventanas:
echo    - "Hive Orchestrator" (minimizada)
echo    - "Gemini Worker" (minimizada)
echo.
echo 💡 Endpoints disponibles:
echo    - Stats: http://localhost:5000/api/workers/stats
echo    - Submit task: POST http://localhost:5000/api/test/task
echo.
echo ⚠️  Los servicios siguen corriendo en background.
echo    Para detenerlos: Cierra las ventanas CMD o ejecuta:
echo    taskkill /F /FI "WINDOWTITLE eq Hive*"
echo.
pause
