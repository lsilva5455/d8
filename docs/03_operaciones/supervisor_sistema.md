# 🔄 Sistema de Supervisión D8

**Fecha:** 2025-11-21  
**Versión:** 1.0  
**Estado:** ✅ Operacional

---

## 📋 Descripción

El Sistema de Supervisión D8 es un conjunto de herramientas que mantienen los componentes críticos corriendo de forma continua con auto-recuperación automática. Ideal para entornos de producción que requieren alta disponibilidad.

---

## 🎯 Componentes

### 1. Supervisor Master (`supervisor_d8.py`)
Supervisa los componentes principales en el master (Raspberry Pi):
- 🏛️ Congreso Autónomo
- 💎 Niche Discovery
- 🎯 Orchestrator

### 2. Supervisor Slave (`supervisor_slave.py`)
Supervisa el slave server en máquinas remotas:
- 🔧 Slave Server (API en puerto 7600)

---

## 🚀 Uso

### Modo Interactivo

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Iniciar start_d8.py
python start_d8.py

# Seleccionar opción 6: Supervisor D8
```

### Modo CLI (Directo)

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Iniciar supervisor directamente
python start_d8.py supervisor
```

### Iniciar Componente Específico

```bash
# Congreso Autónomo
python start_d8.py congress

# Niche Discovery
python start_d8.py niche

# Sistema Evolutivo
python start_d8.py evolution

# Orchestrator
python start_d8.py orchestrator

# Slave Server
python start_d8.py slave
```

---

## 🔧 Características

### Auto-Recuperación
- ✅ Reinicia automáticamente componentes caídos
- ✅ Límite de 5 reintentos por componente
- ✅ Delay de 5 segundos entre reintentos
- ✅ Logging detallado de crashes

### Prevención de Duplicados
- ✅ Sistema de lockfile
- ✅ Verifica si ya hay supervisor corriendo
- ✅ Previene múltiples instancias

### Cierre Limpio
- ✅ Ctrl+C detiene todos los procesos
- ✅ Termination graceful (SIGTERM)
- ✅ Force kill después de 10s timeout
- ✅ Elimina lockfile al salir

### Monitoreo
- ✅ Health check cada 10 segundos
- ✅ Logs estructurados en `~/Documents/d8_data/logs/`
- ✅ Captura stderr de procesos caídos

---

## 📊 Logs

### Ubicación de Logs

**Master:**
```
~/Documents/d8_data/logs/supervisor.log
```

**Slave:**
```
~/Documents/d8_data/logs/supervisor_slave.log
```

### Formato de Logs

```
2025-11-21 08:59:16,530 - __main__ - INFO - 🔄 D8 SUPERVISOR INICIADO
2025-11-21 08:59:16,536 - __main__ - INFO - ✅ Congreso Autónomo iniciado (PID: 28192)
2025-11-21 08:59:19,569 - __main__ - INFO - ✅ Niche Discovery iniciado (PID: 18620)
2025-11-21 08:59:22,578 - __main__ - INFO - ✅ Orchestrator iniciado (PID: 26472)
2025-11-21 08:59:25,579 - __main__ - INFO - 🔄 Supervisor activo - Presiona Ctrl+C para detener
```

### Ver Logs en Tiempo Real

**PowerShell:**
```powershell
Get-Content "$env:USERPROFILE\Documents\d8_data\logs\supervisor.log" -Wait -Tail 20
```

**Linux/Mac:**
```bash
tail -f ~/Documents/d8_data/logs/supervisor.log
```

---

## 🛑 Detener el Supervisor

### Método 1: Ctrl+C (Recomendado)
En la terminal donde corre el supervisor, presiona `Ctrl+C`.

### Método 2: Kill por PID
```powershell
# Leer PID del lockfile
$lock = Get-Content "$env:USERPROFILE\Documents\d8_data\supervisor.lock" | ConvertFrom-Json
$pid = $lock.pid

# Detener proceso
Stop-Process -Id $pid -Force
```

### Método 3: Eliminar lockfile y matar procesos
```powershell
# Eliminar lockfile
Remove-Item "$env:USERPROFILE\Documents\d8_data\supervisor.lock" -Force

# Matar procesos Python relacionados
Get-Process python | Where-Object {$_.Path -like "*d8*"} | Stop-Process -Force
```

---

## 🔍 Verificar Estado

### Verificar si el Supervisor está Corriendo

```powershell
# Verificar lockfile
if (Test-Path "$env:USERPROFILE\Documents\d8_data\supervisor.lock") {
    $lock = Get-Content "$env:USERPROFILE\Documents\d8_data\supervisor.lock" | ConvertFrom-Json
    Write-Host "✅ Supervisor corriendo (PID: $($lock.pid))"
    Write-Host "   Iniciado: $($lock.started_at)"
    Write-Host "   Componentes: $($lock.components -join ', ')"
} else {
    Write-Host "❌ Supervisor no está corriendo"
}
```

### Verificar Procesos Supervisados

```powershell
# Ver procesos Python activos
Get-Process python | Select-Object Id, ProcessName, StartTime, Path
```

---

## ⚙️ Configuración

### Habilitar/Deshabilitar Componentes

Editar `scripts/supervisor_d8.py`:

```python
self.components = [
    {
        "name": "congress",
        "script": "scripts/autonomous_congress.py",
        "description": "Congreso Autónomo",
        "enabled": True  # ← Cambiar a False para deshabilitar
    },
    {
        "name": "niche_discovery",
        "script": "scripts/niche_discovery_agent.py",
        "description": "Niche Discovery",
        "enabled": True
    },
    {
        "name": "orchestrator",
        "module": "app.orchestrator_app",
        "description": "Orchestrator",
        "enabled": True
    }
]
```

### Cambiar Límite de Reintentos

```python
self.max_retries = 5  # ← Cambiar valor
```

### Cambiar Intervalo de Health Check

```python
check_interval = 10  # segundos ← Cambiar valor
```

---

## 🚨 Troubleshooting

### Problema: "Supervisor ya corriendo"

**Causa:** Hay un lockfile de una instancia anterior.

**Solución 1 (verificar si realmente está corriendo):**
```powershell
$lock = Get-Content "$env:USERPROFILE\Documents\d8_data\supervisor.lock" | ConvertFrom-Json
Get-Process -Id $lock.pid -ErrorAction SilentlyContinue
```

**Solución 2 (forzar limpieza):**
```powershell
Remove-Item "$env:USERPROFILE\Documents\d8_data\supervisor.lock" -Force
```

### Problema: Componente alcanzó límite de reintentos

**Causa:** El componente falla repetidamente al iniciar.

**Diagnóstico:**
```powershell
# Ver logs del supervisor
Get-Content "$env:USERPROFILE\Documents\d8_data\logs\supervisor.log" -Tail 50
```

**Acciones:**
1. Revisar error en logs
2. Verificar dependencias (venv activado, API keys, etc.)
3. Probar componente manualmente: `python start_d8.py <componente>`

### Problema: Procesos no se detienen con Ctrl+C

**Causa:** Procesos zombies o colgados.

**Solución:**
```powershell
# Forzar kill de todos los procesos Python de D8
Get-Process python | Where-Object {
    $_.Path -like "*d8*"
} | Stop-Process -Force
```

---

## 📈 Casos de Uso

### Caso 1: Producción 24/7 (Raspberry Pi)

```bash
# Activar venv
source venv/bin/activate

# Iniciar supervisor en background con nohup
nohup python start_d8.py supervisor > /dev/null 2>&1 &

# Verificar que está corriendo
cat ~/Documents/d8_data/supervisor.lock
```

### Caso 2: Desarrollo con Hot-Reload

**NO usar supervisor en desarrollo.** Mejor ejecutar componentes individuales:

```bash
# Terminal 1: Congreso
python start_d8.py congress

# Terminal 2: Niche Discovery
python start_d8.py niche

# Terminal 3: Orchestrator
python start_d8.py orchestrator
```

### Caso 3: Testing de Resiliencia

```bash
# Iniciar supervisor
python start_d8.py supervisor

# En otra terminal, matar un componente
Get-Process python | Where-Object {$_.Id -eq <PID>} | Stop-Process -Force

# Verificar que se reinicia automáticamente
Get-Content "$env:USERPROFILE\Documents\d8_data\logs\supervisor.log" -Wait -Tail 20
```

---

## 🔗 Referencias

- **Código:** `scripts/supervisor_d8.py`, `scripts/supervisor_slave.py`
- **Launcher:** `start_d8.py`
- **Logs:** `~/Documents/d8_data/logs/`
- **Lockfiles:** `~/Documents/d8_data/supervisor*.lock`

---

## 📝 Notas

- ⚠️ **Importante:** Siempre activar el entorno virtual antes de usar el supervisor
- ⚠️ **Importante:** En Windows, el supervisor requiere PowerShell 5.1+
- ✅ Compatible con Windows, Linux y macOS
- ✅ No requiere dependencias adicionales (usa solo stdlib + psutil)

---

**Última actualización:** 2025-11-21  
**Mantenedor:** Sistema D8
