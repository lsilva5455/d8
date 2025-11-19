# ========================================
# TEST SETUP - Simulated Distributed Mode
# Run orchestrator + worker in parallel
# ========================================

Write-Host "🐝 THE HIVE - Distributed Testing Mode" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Virtual environment not found. Creating..." -ForegroundColor Red
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies if needed
Write-Host "📦 Checking dependencies..." -ForegroundColor Yellow
pip install -q google-generativeai psutil requests python-dotenv 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Installing dependencies..." -ForegroundColor Yellow
    pip install google-generativeai psutil requests python-dotenv
}

Write-Host "✅ Dependencies ready" -ForegroundColor Green
Write-Host ""

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating minimal config..." -ForegroundColor Yellow
    
    @"
# Minimal config for testing
POPULATION_SIZE=2
GROQ_API_KEY=test_key
DEEPSEEK_BASE_URL=http://localhost:11434
DEEPSEEK_MODEL=deepseek-coder:33b
GROQ_MODEL=llama-3.1-8b-instant
FLASK_PORT=5000
FLASK_DEBUG=true
LOG_LEVEL=INFO
"@ | Out-File -FilePath ".env" -Encoding utf8
    
    Write-Host "✅ Created .env (you'll need to add real API keys)" -ForegroundColor Green
}

# Check for .env.worker file
if (-not (Test-Path ".env.worker")) {
    Write-Host "⚠️  .env.worker not found. Creating..." -ForegroundColor Yellow
    
    @"
# Worker configuration
ORCHESTRATOR_URL=http://localhost:5000
WORKER_ID=gemini-test-worker
WORKER_TYPE=gemini
GEMINI_API_KEY=your_gemini_api_key_here
POLL_INTERVAL=5
"@ | Out-File -FilePath ".env.worker" -Encoding utf8
    
    Write-Host "✅ Created .env.worker (add your Gemini API key)" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔑 Get free Gemini API key at: https://makersuite.google.com/app/apikey" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter after adding your GEMINI_API_KEY to .env.worker"
}

Write-Host ""
Write-Host "🚀 Starting services..." -ForegroundColor Cyan
Write-Host ""

# Start orchestrator (main.py) in background
Write-Host "1️⃣  Starting Orchestrator (Flask)..." -ForegroundColor Yellow
$orchestratorJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & .\venv\Scripts\Activate.ps1
    python app/main.py
}

Write-Host "   Job ID: $($orchestratorJob.Id)" -ForegroundColor Gray

# Wait for Flask to start
Write-Host "   Waiting for orchestrator to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Check if orchestrator is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/" -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Orchestrator is online!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Orchestrator may still be starting..." -ForegroundColor Yellow
}

Write-Host ""

# Start worker in background
Write-Host "2️⃣  Starting Gemini Worker..." -ForegroundColor Yellow
$workerJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & .\venv\Scripts\Activate.ps1
    python app/distributed/worker_fixed.py
}

Write-Host "   Job ID: $($workerJob.Id)" -ForegroundColor Gray
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "✅ Both services started!" -ForegroundColor Green
Write-Host ""

# Show status
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║           🎯 SYSTEM STATUS                       ║" -ForegroundColor Cyan
Write-Host "╠══════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║  Orchestrator:  http://localhost:5000           ║" -ForegroundColor White
Write-Host "║  Worker Stats:  http://localhost:5000/api/workers/stats ║" -ForegroundColor White
Write-Host "╠══════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║  Jobs Running:                                   ║" -ForegroundColor White
Write-Host "║    - Orchestrator (Job $($orchestratorJob.Id))                      ║" -ForegroundColor White
Write-Host "║    - Gemini Worker (Job $($workerJob.Id))                      ║" -ForegroundColor White
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Show logs
Write-Host "📊 Live Logs (press Ctrl+C to stop monitoring):" -ForegroundColor Yellow
Write-Host ""

# Monitor jobs
try {
    while ($true) {
        # Check orchestrator
        $orchOutput = Receive-Job -Job $orchestratorJob 2>&1 | Select-Object -Last 5
        if ($orchOutput) {
            Write-Host "🐝 ORCHESTRATOR:" -ForegroundColor Magenta
            $orchOutput | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
        }
        
        # Check worker
        $workerOutput = Receive-Job -Job $workerJob 2>&1 | Select-Object -Last 5
        if ($workerOutput) {
            Write-Host "🤖 WORKER:" -ForegroundColor Blue
            $workerOutput | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
        }
        
        Start-Sleep -Seconds 5
        
        # Check if jobs are still running
        if ($orchestratorJob.State -ne "Running" -or $workerJob.State -ne "Running") {
            Write-Host ""
            Write-Host "⚠️  One or more services stopped!" -ForegroundColor Red
            break
        }
    }
} finally {
    # Cleanup
    Write-Host ""
    Write-Host "🛑 Stopping services..." -ForegroundColor Yellow
    
    Stop-Job -Job $orchestratorJob -ErrorAction SilentlyContinue
    Stop-Job -Job $workerJob -ErrorAction SilentlyContinue
    
    Remove-Job -Job $orchestratorJob -Force -ErrorAction SilentlyContinue
    Remove-Job -Job $workerJob -Force -ErrorAction SilentlyContinue
    
    Write-Host "✅ Services stopped" -ForegroundColor Green
}
