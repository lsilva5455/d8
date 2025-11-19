# Script para ejecutar todos los tests D8
# Ejecuta Content Empire, Device Farm y Niche Congress secuencialmente

Write-Host "`n🧪 D8 TESTS - FULL SUITE" -ForegroundColor Cyan
Write-Host "=" * 70
Write-Host ""

# Activate venv
Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Create results directory
$resultsDir = "data\test_results"
if (-not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Path $resultsDir -Force | Out-Null
}

# Test 1: Content Empire
Write-Host "`n[1/3] 🎨 CONTENT EMPIRE TEST" -ForegroundColor Cyan
Write-Host "-" * 70

try {
    python test_content_empire.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Content Empire test passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Content Empire test failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error running Content Empire test: $_" -ForegroundColor Red
}

Write-Host ""
Start-Sleep -Seconds 2

# Test 2: Device Farm
Write-Host "`n[2/3] 📱 DEVICE FARM TEST" -ForegroundColor Cyan
Write-Host "-" * 70

try {
    python test_device_farm.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Device Farm test passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Device Farm test failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error running Device Farm test: $_" -ForegroundColor Red
}

Write-Host ""
Start-Sleep -Seconds 2

# Test 3: Niche Congress
Write-Host "`n[3/3] 🏛️  NICHE CONGRESS TEST" -ForegroundColor Cyan
Write-Host "-" * 70

try {
    python test_niche_congress.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Niche Congress test passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Niche Congress test failed" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error running Niche Congress test: $_" -ForegroundColor Red
}

# Summary
Write-Host "`n" + ("=" * 70)
Write-Host "📊 RESUMEN FINAL" -ForegroundColor Cyan
Write-Host ("=" * 70)

Write-Host "`nResultados guardados en: $resultsDir"
Write-Host ""

# List result files
if (Test-Path $resultsDir) {
    $files = Get-ChildItem $resultsDir -Filter "*.json"
    
    if ($files.Count -gt 0) {
        Write-Host "📄 Archivos generados:" -ForegroundColor Yellow
        foreach ($file in $files) {
            $size = [math]::Round($file.Length / 1KB, 2)
            Write-Host "   ✓ $($file.Name) ($size KB)"
        }
    } else {
        Write-Host "⚠️  No se encontraron archivos de resultados" -ForegroundColor Yellow
    }
}

Write-Host "`n💡 Para ver resultados detallados:" -ForegroundColor Yellow
Write-Host "   Get-Content data\test_results\*.json | ConvertFrom-Json"

Write-Host "`n✅ Test suite completo" -ForegroundColor Green
Write-Host ""
