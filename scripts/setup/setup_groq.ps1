# Configuración rápida de Groq Worker

Write-Host "`n🚀 CONFIGURACIÓN GROQ WORKER (SOLUCIÓN AL 429)" -ForegroundColor Cyan
Write-Host "=" * 60

Write-Host "`n📝 PASO 1: Obtener API Key de Groq (GRATIS)" -ForegroundColor Yellow
Write-Host ""
Write-Host "   1. Visita: https://console.groq.com/keys" -ForegroundColor White
Write-Host "   2. Crea cuenta (Google/GitHub)" -ForegroundColor White
Write-Host "   3. Click 'Create API Key'" -ForegroundColor White
Write-Host "   4. Copia la key (empieza con gsk_...)" -ForegroundColor White
Write-Host ""
Write-Host "   Free Tier Groq:" -ForegroundColor Green
Write-Host "   ✅ 30 requests/minuto (2x Gemini)"
Write-Host "   ✅ 14,400 requests/día (10x Gemini)"
Write-Host "   ✅ Sin 429 errors"
Write-Host "   ✅ 2-3x más rápido"
Write-Host ""

# Ask for API key
Write-Host "🔑 Ingresa tu Groq API Key:" -ForegroundColor Cyan -NoNewline
Write-Host " (o presiona Enter para abrir el navegador)" -ForegroundColor Gray
$apiKey = Read-Host

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host "`n📱 Abriendo navegador..." -ForegroundColor Yellow
    Start-Process "https://console.groq.com/keys"
    Write-Host "   Obtén tu key y vuelve aquí" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔑 Ingresa tu Groq API Key:" -ForegroundColor Cyan
    $apiKey = Read-Host
}

if ([string]::IsNullOrWhiteSpace($apiKey)) {
    Write-Host "`n❌ API Key requerida. Saliendo..." -ForegroundColor Red
    exit 1
}

# Update .env.worker.groq
Write-Host "`n📄 PASO 2: Configurando .env.worker.groq..." -ForegroundColor Yellow

$envContent = @"
# API Configuration
GROQ_API_KEY=$apiKey

# Worker Configuration
WORKER_ID=groq-worker-1
WORKER_TYPE=groq
ORCHESTRATOR_URL=http://localhost:5000

# System
WORKER_POLL_INTERVAL=5
"@

Set-Content -Path ".env.worker.groq" -Value $envContent
Write-Host "   ✅ Archivo .env.worker.groq actualizado" -ForegroundColor Green

# Test API key
Write-Host "`n🧪 PASO 3: Probando API Key..." -ForegroundColor Yellow

$testScript = @"
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv('.env.worker.groq')
api_key = os.getenv('GROQ_API_KEY')

try:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[{'role': 'user', 'content': 'Say OK'}],
        max_tokens=10
    )
    print(f'✅ API_KEY_VALID: {response.choices[0].message.content.strip()}')
except Exception as e:
    print(f'❌ API_ERROR: {str(e)}')
"@

Set-Content -Path "test_groq_key.py" -Value $testScript
$env:PYTHONPATH = "C:\Users\PcDos\d8"
$result = & "C:\Users\PcDos\d8\venv\Scripts\python.exe" test_groq_key.py 2>&1

if ($result -match "✅ API_KEY_VALID") {
    Write-Host "   $result" -ForegroundColor Green
    Write-Host "   ✅ API Key válida y funcional!" -ForegroundColor Green
    
    Remove-Item "test_groq_key.py" -ErrorAction SilentlyContinue
    
    # Offer to launch worker
    Write-Host "`n🚀 PASO 4: Lanzar Groq Worker" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "¿Deseas lanzar el Groq Worker ahora? (S/N):" -ForegroundColor Cyan -NoNewline
    $launch = Read-Host
    
    if ($launch -eq "S" -or $launch -eq "s" -or $launch -eq "Y" -or $launch -eq "y") {
        Write-Host "`n⏹️  Deteniendo workers anteriores..." -ForegroundColor Yellow
        taskkill /F /FI "WINDOWTITLE eq *Worker*" 2>$null | Out-Null
        Start-Sleep -Seconds 2
        
        Write-Host "🚀 Lanzando Groq Worker..." -ForegroundColor Yellow
        $env:PYTHONPATH = "C:\Users\PcDos\d8"
        Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd /d C:\Users\PcDos\d8 && set PYTHONPATH=C:\Users\PcDos\d8 && venv\Scripts\python.exe app/distributed/worker_groq.py" -WindowStyle Normal
        
        Start-Sleep -Seconds 3
        
        Write-Host "`n✅ Worker lanzado en ventana CMD" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 Verifica estado:" -ForegroundColor Cyan
        Write-Host "   curl http://localhost:5000/api/workers/stats" -ForegroundColor White
        Write-Host ""
        Write-Host "🧪 Prueba el sistema:" -ForegroundColor Cyan
        Write-Host "   .\test_groq_system.ps1" -ForegroundColor White
        
    } else {
        Write-Host "`n📝 Para lanzar manualmente:" -ForegroundColor Cyan
        Write-Host "   python app/distributed/worker_groq.py" -ForegroundColor White
    }
    
} else {
    Write-Host "   $result" -ForegroundColor Red
    Write-Host "`n❌ API Key inválida. Verifica y vuelve a intentar." -ForegroundColor Red
    Remove-Item "test_groq_key.py" -ErrorAction SilentlyContinue
}

Write-Host ""
