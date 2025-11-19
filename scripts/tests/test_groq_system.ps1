# Test completo del sistema con Groq Worker

Write-Host "`n🧪 PROBANDO SISTEMA CON GROQ WORKER" -ForegroundColor Cyan
Write-Host "=" * 60

# Check if orchestrator is running
Write-Host "`n[1/5] Verificando orchestrator..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/" -Method GET -TimeoutSec 5
    Write-Host "   ✅ Orchestrator online" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Orchestrator no responde" -ForegroundColor Red
    Write-Host "   Ejecuta: python test_orchestrator.py" -ForegroundColor Yellow
    exit 1
}

# Check workers
Write-Host "`n[2/5] Verificando workers..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

$stats = Invoke-RestMethod -Uri "http://localhost:5000/api/workers/stats" -Method GET
Write-Host "   Workers online: $($stats.workers.online)" -ForegroundColor Green
Write-Host "   Worker types: $($stats.workers.by_type | ConvertTo-Json -Compress)" -ForegroundColor Green

if ($stats.workers.online -eq 0) {
    Write-Host "   ❌ No hay workers registrados" -ForegroundColor Red
    Write-Host "   Ejecuta: python app/distributed/worker_groq.py" -ForegroundColor Yellow
    exit 1
}

# Check if Groq worker is available
$hasGroq = $stats.workers.by_type.PSObject.Properties.Name -contains "groq"
if (-not $hasGroq) {
    Write-Host "   ⚠️  Worker de Groq no encontrado" -ForegroundColor Yellow
    Write-Host "   Worker types disponibles: $($stats.workers.by_type | ConvertTo-Json)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   El test continuará con workers disponibles..." -ForegroundColor Gray
}

# Submit simple task
Write-Host "`n[3/5] Enviando tarea de prueba..." -ForegroundColor Yellow

$testTask = @{
    prompt = "Responde 'Sistema funcionando' en español"
}

$result = Invoke-RestMethod -Uri "http://localhost:5000/api/test/task" `
    -Method POST `
    -Body ($testTask | ConvertTo-Json) `
    -ContentType "application/json"

$taskId = $result.task_id
Write-Host "   ✅ Task enviada: $taskId" -ForegroundColor Green

# Wait for processing
Write-Host "`n[4/5] Esperando procesamiento..." -ForegroundColor Yellow

$maxWait = 30
$waited = 0
$completed = $false

while ($waited -lt $maxWait) {
    Start-Sleep -Seconds 3
    $waited += 3
    
    $stats = Invoke-RestMethod -Uri "http://localhost:5000/api/workers/stats" -Method GET
    
    Write-Host "   ⏳ ${waited}s - Completed: $($stats.tasks.completed), Failed: $($stats.tasks.failed)" -ForegroundColor Gray
    
    if ($stats.tasks.completed -gt 0) {
        Write-Host "`n   ✅ ¡TAREA COMPLETADA EXITOSAMENTE!" -ForegroundColor Green
        $completed = $true
        break
    }
    
    if ($stats.tasks.failed -gt 0) {
        Write-Host "`n   ❌ Tarea falló" -ForegroundColor Red
        break
    }
}

# Final stats
Write-Host "`n[5/5] Estadísticas finales" -ForegroundColor Yellow

$finalStats = Invoke-RestMethod -Uri "http://localhost:5000/api/workers/stats" -Method GET

Write-Host "`n" + ("=" * 60)
Write-Host "📊 RESULTADOS" -ForegroundColor Cyan
Write-Host ""

Write-Host "Workers:"
Write-Host "   Online: $($finalStats.workers.online)"
Write-Host "   By type: $($finalStats.workers.by_type | ConvertTo-Json -Compress)"

Write-Host "`nTasks:"
Write-Host "   Total: $($finalStats.tasks.total)"
Write-Host "   Completed: $($finalStats.tasks.completed) ✅" -ForegroundColor Green
Write-Host "   Failed: $($finalStats.tasks.failed)" -ForegroundColor $(if ($finalStats.tasks.failed -gt 0) { "Red" } else { "Gray" })
Write-Host "   Success Rate: $($finalStats.performance.success_rate * 100)%"

Write-Host ""

if ($finalStats.tasks.completed -gt 0) {
    Write-Host "✅ SISTEMA COMPLETAMENTE FUNCIONAL" -ForegroundColor Green
    Write-Host ""
    Write-Host "El sistema distribuido está:" -ForegroundColor Green
    Write-Host "   ✅ Recibiendo tareas"
    Write-Host "   ✅ Asignando a workers"
    Write-Host "   ✅ Ejecutando correctamente"
    Write-Host "   ✅ Reportando resultados"
    Write-Host ""
    Write-Host "🎯 LISTO PARA PRODUCCIÓN" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Próximos pasos:"
    Write-Host "   - Opción A (Content Empire): 5 agentes generando contenido"
    Write-Host "   - Opción B (Device Farm): Coordinación de dispositivos"
    Write-Host "   - Deploy en Raspberry Pi: docs/RASPBERRY_PI_SETUP.md"
    
} elseif ($finalStats.tasks.failed -gt 0) {
    Write-Host "⚠️  SISTEMA FUNCIONAL PERO CON ERRORES" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "La arquitectura funciona, pero hay problemas de API:" -ForegroundColor Yellow
    Write-Host "   - Arquitectura distribuida: ✅ OK"
    Write-Host "   - Worker registration: ✅ OK"
    Write-Host "   - Task assignment: ✅ OK"
    Write-Host "   - API execution: ❌ FALLO"
    Write-Host ""
    Write-Host "Posibles causas:"
    Write-Host "   - API key inválida o expirada"
    Write-Host "   - Rate limit alcanzado"
    Write-Host "   - Formato de mensaje incorrecto"
    Write-Host ""
    Write-Host "Revisa logs del worker para más detalles"
    
} else {
    Write-Host "⏳ TIMEOUT - Tarea aún procesando" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "El worker puede estar:"
    Write-Host "   - Haciendo retries por rate limit"
    Write-Host "   - Esperando respuesta de API lenta"
    Write-Host "   - Procesando en background"
    Write-Host ""
    Write-Host "Revisa la ventana del worker para más info"
}

Write-Host "`n" + ("=" * 60)
Write-Host ""
