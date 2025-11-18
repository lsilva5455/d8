# Test del Worker Resiliente con manejo de 429 errors

Write-Host "`n🧪 PROBANDO WORKER RESILIENTE (ANTI-429)" -ForegroundColor Cyan
Write-Host "=" * 60

# Wait for worker to register
Write-Host "`n[1/4] Esperando registro del worker..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Check worker status
Write-Host "`n[2/4] Verificando workers online..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "http://localhost:5000/api/workers/stats" -Method GET
    Write-Host "   Workers online: $($stats.workers.online)" -ForegroundColor Green
    Write-Host "   Worker types: $($stats.workers.by_type | ConvertTo-Json -Compress)" -ForegroundColor Green
    
    if ($stats.workers.online -eq 0) {
        Write-Host "   ❌ No hay workers. Espera 10s más..." -ForegroundColor Red
        Start-Sleep -Seconds 10
    }
} catch {
    Write-Host "   ❌ Orchestrator no responde" -ForegroundColor Red
    exit 1
}

# Submit test task (simple)
Write-Host "`n[3/4] Enviando tarea de prueba simple..." -ForegroundColor Yellow

$testTask = @{
    prompt = "Di 'OK' en una palabra"
}

try {
    $result = Invoke-RestMethod -Uri "http://localhost:5000/api/test/task" `
        -Method POST `
        -Body ($testTask | ConvertTo-Json) `
        -ContentType "application/json"
    
    $taskId = $result.task_id
    Write-Host "   ✅ Task enviada: $taskId" -ForegroundColor Green
    
    # Wait for worker to process (with retry logic, may take time)
    Write-Host "`n[4/4] Esperando procesamiento (puede tomar hasta 60s con retries)..." -ForegroundColor Yellow
    
    $maxWait = 60
    $waited = 0
    $completed = $false
    
    while ($waited -lt $maxWait) {
        Start-Sleep -Seconds 5
        $waited += 5
        
        $stats = Invoke-RestMethod -Uri "http://localhost:5000/api/workers/stats" -Method GET
        
        Write-Host "   ⏳ $waited s - Completed: $($stats.tasks.completed), Failed: $($stats.tasks.failed), Pending: $($stats.tasks.pending)" -ForegroundColor Gray
        
        if ($stats.tasks.completed -gt 0) {
            Write-Host "`n   ✅ TAREA COMPLETADA!" -ForegroundColor Green
            Write-Host "   Success rate: $($stats.performance.success_rate * 100)%" -ForegroundColor Green
            $completed = $true
            break
        }
        
        if ($stats.tasks.failed -gt 0) {
            Write-Host "`n   ❌ Tarea falló después de todos los retries" -ForegroundColor Red
            Write-Host "   Verifica logs en ventana 'Gemini Resilient Worker'" -ForegroundColor Yellow
            break
        }
    }
    
    if (-not $completed -and $stats.tasks.failed -eq 0) {
        Write-Host "`n   ⚠️  Timeout: Worker aún procesando (429 con múltiples retries)" -ForegroundColor Yellow
        Write-Host "   El worker seguirá intentando en background" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "   ❌ Error enviando task: $_" -ForegroundColor Red
}

# Final stats
Write-Host "`n" + ("=" * 60)
Write-Host "📊 ESTADÍSTICAS FINALES" -ForegroundColor Cyan

try {
    $finalStats = Invoke-RestMethod -Uri "http://localhost:5000/api/workers/stats" -Method GET
    
    Write-Host "`nWorkers:"
    Write-Host "   Online: $($finalStats.workers.online)"
    Write-Host "   Types: $($finalStats.workers.by_type | ConvertTo-Json -Compress)"
    
    Write-Host "`nTasks:"
    Write-Host "   Total: $($finalStats.tasks.total)"
    Write-Host "   Completed: $($finalStats.tasks.completed)"
    Write-Host "   Failed: $($finalStats.tasks.failed)"
    Write-Host "   Pending: $($finalStats.tasks.pending)"
    
    Write-Host "`nPerformance:"
    Write-Host "   Success Rate: $($finalStats.performance.success_rate * 100)%"
    
    if ($finalStats.tasks.completed -gt 0) {
        Write-Host "`n✅ WORKER RESILIENTE FUNCIONANDO CORRECTAMENTE" -ForegroundColor Green
        Write-Host "   El sistema maneja 429 errors con retry automático" -ForegroundColor Green
    } elseif ($finalStats.tasks.failed -gt 0) {
        Write-Host "`n⚠️  TODOS LOS RETRIES FALLARON" -ForegroundColor Yellow
        Write-Host "   Posible causa: Rate limit muy restrictivo de Gemini" -ForegroundColor Yellow
        Write-Host "   Solución: Usar Groq worker (ver SETUP_GROQ_WORKER.md)" -ForegroundColor Cyan
    } else {
        Write-Host "`n⏳ WORKER AÚN PROCESANDO CON RETRIES" -ForegroundColor Yellow
        Write-Host "   Revisa ventana 'Gemini Resilient Worker' para ver intentos" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "❌ Error obteniendo stats finales" -ForegroundColor Red
}

Write-Host "`n" + ("=" * 60)
Write-Host "💡 PRÓXIMOS PASOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Si 429 persiste incluso con retries:" -ForegroundColor Yellow
Write-Host "  1. Google tiene rate limits MUY agresivos (15 req/min)" -ForegroundColor Gray
Write-Host "  2. Worker resiliente ya implementa:" -ForegroundColor Gray
Write-Host "     - Rate limiting proactivo (10 req/min)" -ForegroundColor Gray
Write-Host "     - Exponential backoff (2s → 32s)" -ForegroundColor Gray
Write-Host "     - 5 retries automáticos" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Solución recomendada: Groq" -ForegroundColor Green
Write-Host "     - 30 req/min (3x más que Gemini)" -ForegroundColor Gray
Write-Host "     - Sin 429 errors en testing" -ForegroundColor Gray
Write-Host "     - Setup: SETUP_GROQ_WORKER.md" -ForegroundColor Gray
Write-Host ""
Write-Host "Logs detallados en: Ventana 'Gemini Resilient Worker'" -ForegroundColor Gray
Write-Host ""
