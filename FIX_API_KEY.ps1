# Script para diagnosticar y corregir problemas de API Key

Write-Host "`n🔧 DIAGNÓSTICO AUTOMÁTICO DE API KEYS" -ForegroundColor Cyan
Write-Host "=" * 50

# 1. Verificar .env.worker
Write-Host "`n[1/4] Verificando .env.worker..." -ForegroundColor Yellow
$envFile = "C:\Users\PcDos\d8\.env.worker"

if (Test-Path $envFile) {
    $content = Get-Content $envFile
    $geminiKey = ($content | Select-String "GEMINI_API_KEY=").ToString().Split("=")[1]
    
    if ($geminiKey -and $geminiKey -ne "your_gemini_api_key_here") {
        Write-Host "✅ API Key encontrada: $($geminiKey.Substring(0,10))..." -ForegroundColor Green
    } else {
        Write-Host "❌ API Key no configurada o es placeholder" -ForegroundColor Red
        Write-Host "`n💡 Solución:" -ForegroundColor Cyan
        Write-Host "   1. Obtén tu API key gratis en: https://makersuite.google.com/app/apikey"
        Write-Host "   2. Edita .env.worker y reemplaza 'your_gemini_api_key_here'"
        Write-Host "   3. Reinicia el worker: launch_distributed.bat"
    }
} else {
    Write-Host "❌ Archivo .env.worker no encontrado" -ForegroundColor Red
}

# 2. Probar API de Gemini
Write-Host "`n[2/4] Probando conexión con Gemini API..." -ForegroundColor Yellow

$testScript = @"
import os
import sys
from dotenv import load_dotenv

# Cargar .env.worker
load_dotenv('.env.worker')
api_key = os.getenv('GEMINI_API_KEY')

if not api_key or api_key == 'your_gemini_api_key_here':
    print('❌ API_KEY_NOT_CONFIGURED')
    sys.exit(1)

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content('Say hello in one word')
    print(f'✅ API_WORKING: {response.text.strip()}')
except ImportError:
    print('❌ INSTALL_MISSING: pip install google-generativeai')
except Exception as e:
    print(f'❌ API_ERROR: {str(e)}')
"@

Set-Content -Path "test_gemini_api.py" -Value $testScript
$env:PYTHONPATH = "C:\Users\PcDos\d8"
$result = & "C:\Users\PcDos\d8\venv\Scripts\python.exe" test_gemini_api.py 2>&1

if ($result -match "✅ API_WORKING") {
    Write-Host "$result" -ForegroundColor Green
} elseif ($result -match "INSTALL_MISSING") {
    Write-Host "$result" -ForegroundColor Yellow
    Write-Host "`n💡 Instalando google-generativeai..." -ForegroundColor Cyan
    & "C:\Users\PcDos\d8\venv\Scripts\pip.exe" install google-generativeai
} else {
    Write-Host "$result" -ForegroundColor Red
}

Remove-Item "test_gemini_api.py" -ErrorAction SilentlyContinue

# 3. Verificar logs del worker
Write-Host "`n[3/4] Buscando errores en logs del worker..." -ForegroundColor Yellow
Write-Host "(Logs solo visibles en ventana 'Gemini Worker')" -ForegroundColor Gray
Write-Host "`n💡 Para ver logs completos:" -ForegroundColor Cyan
Write-Host "   - Busca la ventana minimizada 'Gemini Worker'"
Write-Host "   - O ejecuta: python app/distributed/worker_fixed.py"

# 4. Verificar estado del orchestrator
Write-Host "`n[4/4] Verificando estado del orchestrator..." -ForegroundColor Yellow

try {
    $stats = Invoke-RestMethod -Uri "http://localhost:5000/api/workers/stats" -Method GET
    
    Write-Host "`n📊 Estadísticas actuales:" -ForegroundColor Cyan
    Write-Host "   Workers online: $($stats.workers.online)"
    Write-Host "   Tasks pending: $($stats.tasks.pending)"
    Write-Host "   Tasks completed: $($stats.tasks.completed)"
    Write-Host "   Tasks failed: $($stats.tasks.failed)"
    
    if ($stats.tasks.failed -gt 0) {
        Write-Host "`n⚠️  Hay $($stats.tasks.failed) tareas fallidas" -ForegroundColor Yellow
        Write-Host "   Causa probable: API key incorrecta o no configurada"
    }
    
    if ($stats.workers.online -eq 0) {
        Write-Host "`n❌ No hay workers conectados" -ForegroundColor Red
        Write-Host "   Ejecuta: launch_distributed.bat"
    }
    
} catch {
    Write-Host "❌ Orchestrator no responde (¿está corriendo?)" -ForegroundColor Red
    Write-Host "   Ejecuta: launch_distributed.bat"
}

# Recomendaciones finales
Write-Host "`n" + ("=" * 50)
Write-Host "🎯 RESUMEN DE ACCIONES:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Si API key no está configurada:" -ForegroundColor Yellow
Write-Host "   → Edita .env.worker con tu key de Gemini"
Write-Host "   → https://makersuite.google.com/app/apikey"
Write-Host ""
Write-Host "2. Si faltan dependencias:" -ForegroundColor Yellow
Write-Host "   → venv\Scripts\pip.exe install google-generativeai"
Write-Host ""
Write-Host "3. Reinicia los servicios:" -ForegroundColor Yellow
Write-Host "   → .\launch_distributed.bat"
Write-Host ""
Write-Host "4. Prueba una tarea simple:" -ForegroundColor Yellow
Write-Host '   → Invoke-RestMethod -Uri "http://localhost:5000/api/test/task" -Method POST -Body (ConvertTo-Json @{prompt="Hello"}) -ContentType "application/json"'
Write-Host ""
Write-Host "Para más detalles: RESULTADOS_PRUEBA_AUTOMATICA.md" -ForegroundColor Gray
Write-Host ""
