#!/usr/bin/env powershell
<#
.SYNOPSIS
    Migración de configuración D8 a nueva estructura ~/Documents/d8_data/

.DESCRIPTION
    Este script migra automáticamente:
    - ~/Documents/agentes/ → ~/Documents/d8_data/agentes/
    - ~/Documents/workers/ → ~/Documents/d8_data/workers/
    
    Preserva todos los archivos existentes y crea backups.

.NOTES
    Fecha: 2025-11-19
    Versión: 1.0
    Autor: D8 System
#>

# Set error action
$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  D8 - Migración de Estructura de Configuración" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Paths
$documentsPath = [Environment]::GetFolderPath("MyDocuments")
$oldAgentesPath = Join-Path $documentsPath "agentes"
$oldWorkersPath = Join-Path $documentsPath "workers"
$newBasePath = Join-Path $documentsPath "d8_data"
$newAgentesPath = Join-Path $newBasePath "agentes"
$newWorkersPath = Join-Path $newBasePath "workers"
$backupPath = Join-Path $newBasePath "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Banner
Write-Host "📦 NUEVA ESTRUCTURA:" -ForegroundColor Yellow
Write-Host "   ~/Documents/d8_data/" -ForegroundColor White
Write-Host "   ├── agentes/       (antes: ~/Documents/agentes/)" -ForegroundColor Gray
Write-Host "   └── workers/       (antes: ~/Documents/workers/)" -ForegroundColor Gray
Write-Host ""

# Check if migration needed
$needsMigration = $false

if (Test-Path $oldAgentesPath) {
    Write-Host "✓ Encontrado: ~/Documents/agentes/" -ForegroundColor Green
    $needsMigration = $true
}

if (Test-Path $oldWorkersPath) {
    Write-Host "✓ Encontrado: ~/Documents/workers/" -ForegroundColor Green
    $needsMigration = $true
}

if (-not $needsMigration) {
    Write-Host "ℹ️  No se encontraron carpetas para migrar." -ForegroundColor Yellow
    Write-Host "   La estructura ya está actualizada o es una instalación nueva." -ForegroundColor Gray
    Write-Host ""
    Write-Host "   La nueva ubicación será: $newBasePath" -ForegroundColor Cyan
    Write-Host ""
    pause
    exit 0
}

Write-Host ""
Write-Host "⚠️  ATENCIÓN:" -ForegroundColor Yellow
Write-Host "   Se moverán las carpetas existentes a la nueva estructura." -ForegroundColor White
Write-Host "   Se creará un backup automático en: $backupPath" -ForegroundColor Gray
Write-Host ""

$confirmation = Read-Host "¿Continuar con la migración? (s/n)"

if ($confirmation -ne "s" -and $confirmation -ne "S") {
    Write-Host ""
    Write-Host "❌ Migración cancelada por el usuario." -ForegroundColor Red
    Write-Host ""
    pause
    exit 1
}

Write-Host ""
Write-Host "🚀 Iniciando migración..." -ForegroundColor Cyan
Write-Host ""

try {
    # Step 1: Create new base directory
    Write-Host "[1/5] Creando estructura base..." -ForegroundColor Yellow
    if (-not (Test-Path $newBasePath)) {
        New-Item -ItemType Directory -Path $newBasePath -Force | Out-Null
        Write-Host "      ✓ Creado: $newBasePath" -ForegroundColor Green
    } else {
        Write-Host "      ℹ️  Ya existe: $newBasePath" -ForegroundColor Gray
    }
    
    # Step 2: Create backup directory
    Write-Host ""
    Write-Host "[2/5] Creando directorio de backup..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
    Write-Host "      ✓ Backup en: $backupPath" -ForegroundColor Green
    
    # Step 3: Backup old structure
    Write-Host ""
    Write-Host "[3/5] Creando backup de configuración actual..." -ForegroundColor Yellow
    
    if (Test-Path $oldAgentesPath) {
        $backupAgentes = Join-Path $backupPath "agentes"
        Copy-Item -Path $oldAgentesPath -Destination $backupAgentes -Recurse -Force
        Write-Host "      ✓ Backup agentes: $backupAgentes" -ForegroundColor Green
    }
    
    if (Test-Path $oldWorkersPath) {
        $backupWorkers = Join-Path $backupPath "workers"
        Copy-Item -Path $oldWorkersPath -Destination $backupWorkers -Recurse -Force
        Write-Host "      ✓ Backup workers: $backupWorkers" -ForegroundColor Green
    }
    
    # Step 4: Move to new structure
    Write-Host ""
    Write-Host "[4/5] Moviendo carpetas a nueva estructura..." -ForegroundColor Yellow
    
    if (Test-Path $oldAgentesPath) {
        if (Test-Path $newAgentesPath) {
            Write-Host "      ⚠️  Destino ya existe: $newAgentesPath" -ForegroundColor Yellow
            Write-Host "         Fusionando contenido..." -ForegroundColor Gray
            Copy-Item -Path "$oldAgentesPath\*" -Destination $newAgentesPath -Recurse -Force
            Remove-Item -Path $oldAgentesPath -Recurse -Force
        } else {
            Move-Item -Path $oldAgentesPath -Destination $newAgentesPath -Force
        }
        Write-Host "      ✓ Movido: agentes/ → d8_data/agentes/" -ForegroundColor Green
    }
    
    if (Test-Path $oldWorkersPath) {
        if (Test-Path $newWorkersPath) {
            Write-Host "      ⚠️  Destino ya existe: $newWorkersPath" -ForegroundColor Yellow
            Write-Host "         Fusionando contenido..." -ForegroundColor Gray
            Copy-Item -Path "$oldWorkersPath\*" -Destination $newWorkersPath -Recurse -Force
            Remove-Item -Path $oldWorkersPath -Recurse -Force
        } else {
            Move-Item -Path $oldWorkersPath -Destination $newWorkersPath -Force
        }
        Write-Host "      ✓ Movido: workers/ → d8_data/workers/" -ForegroundColor Green
    }
    
    # Step 5: Verify migration
    Write-Host ""
    Write-Host "[5/5] Verificando migración..." -ForegroundColor Yellow
    
    $success = $true
    
    if (Test-Path $newAgentesPath) {
        $agentesCount = (Get-ChildItem -Path $newAgentesPath -Recurse -File).Count
        Write-Host "      ✓ d8_data/agentes/ OK ($agentesCount archivos)" -ForegroundColor Green
    } else {
        Write-Host "      ⚠️  d8_data/agentes/ no encontrado" -ForegroundColor Yellow
    }
    
    if (Test-Path $newWorkersPath) {
        $workersCount = (Get-ChildItem -Path $newWorkersPath -Recurse -File).Count
        Write-Host "      ✓ d8_data/workers/ OK ($workersCount archivos)" -ForegroundColor Green
    } else {
        Write-Host "      ⚠️  d8_data/workers/ no encontrado" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  ✅ MIGRACIÓN COMPLETADA EXITOSAMENTE" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📂 Nueva estructura:" -ForegroundColor Cyan
    Write-Host "   $newBasePath" -ForegroundColor White
    Write-Host "   ├── agentes/" -ForegroundColor Gray
    Write-Host "   └── workers/" -ForegroundColor Gray
    Write-Host ""
    Write-Host "💾 Backup guardado en:" -ForegroundColor Cyan
    Write-Host "   $backupPath" -ForegroundColor White
    Write-Host ""
    Write-Host "ℹ️  PRÓXIMOS PASOS:" -ForegroundColor Yellow
    Write-Host "   1. Verifica que D8 funciona correctamente" -ForegroundColor Gray
    Write-Host "   2. Si todo está OK, puedes borrar el backup:" -ForegroundColor Gray
    Write-Host "      Remove-Item -Recurse '$backupPath'" -ForegroundColor DarkGray
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Red
    Write-Host "  ❌ ERROR EN LA MIGRACIÓN" -ForegroundColor Red
    Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔄 RESTAURANDO DESDE BACKUP..." -ForegroundColor Yellow
    
    # Attempt to restore from backup
    if (Test-Path $backupPath) {
        if (Test-Path "$backupPath\agentes") {
            Copy-Item -Path "$backupPath\agentes" -Destination $oldAgentesPath -Recurse -Force
            Write-Host "   ✓ Restaurado: agentes/" -ForegroundColor Green
        }
        if (Test-Path "$backupPath\workers") {
            Copy-Item -Path "$backupPath\workers" -Destination $oldWorkersPath -Recurse -Force
            Write-Host "   ✓ Restaurado: workers/" -ForegroundColor Green
        }
        Write-Host ""
        Write-Host "✓ Configuración restaurada a estado anterior." -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Por favor, reporta este error en GitHub:" -ForegroundColor Yellow
    Write-Host "https://github.com/lsilva5455/d8/issues" -ForegroundColor Cyan
    Write-Host ""
    pause
    exit 1
}

pause
