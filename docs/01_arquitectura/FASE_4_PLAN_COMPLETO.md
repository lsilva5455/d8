# 🚀 FASE 4: Master-Slave con Verificación de Versiones

## Resumen Ejecutivo

Sistema distribuido master-slave con:
- ✅ Ejecución remota con 3 métodos (Docker → venv → Python nativo)
- ✅ **Sincronización automática de versiones**
- ✅ Comunicación robusta (retry/timeout/exponential backoff)
- ✅ Notificaciones por Telegram
- ✅ Auto-recuperación de slaves caídos

---

## 🔖 Sistema de Versiones

### Componentes

1. **`version_info.json`** (root)
   ```json
   {
     "branch": "main",
     "commit": "76d62ab",  ← ID único
     "version": "0.0.8",
     "deployed_at": "2025-11-19T15:24:32Z"
   }
   ```

2. **`scripts/setup/capture_version.py`**
   - Actualiza `version_info.json` desde Git
   - Ejecutado automáticamente por master al iniciar

3. **Verificación en SlaveManager**
   ```python
   def __init__(self):
       self.master_version = self._get_master_version()  # Ejecuta capture_version.py
   
   def check_health(self, slave_id):
       # Compara master_version con slave commit
       if slave_commit != self.master_version:
           # Notificar por Telegram + marcar como version_mismatch
   ```

4. **Endpoint en Slave Server**
   ```python
   @app.route("/api/version", methods=["GET"])
   def version():
       return jsonify(get_version_info())  # Lee version_info.json local
   ```

### Flujo

```
Master inicia
    ↓
Ejecuta capture_version.py
    ↓
Lee version_info.json
    ↓
master_version = "76d62ab"
    ↓
Health check cada 30s
    ↓
GET /api/health de cada slave
    ↓
Compara commits
    ↓
┌────────────┬────────────┐
│   IGUAL    │ DIFERENTE  │
│   healthy  │  version_  │
│            │  mismatch  │
└────────────┴─────┬──────┘
                   ↓
            Telegram alerta
```

---

## 📁 Estructura de Archivos

### Nuevos Archivos (FASE 4)

```
app/distributed/
├── slave_server.py              [240 líneas] ← NUEVO
│   ├── get_version_info()       ← Lee version_info.json
│   ├── /api/version             ← Endpoint de versión
│   ├── /api/execute             ← Ejecuta comandos
│   ├── /api/health              ← Health check con versión
│   └── /api/install             ← Instalación remota
│
├── slave_manager.py             [520 líneas] ← NUEVO
│   ├── __init__()               ← Llama _get_master_version()
│   ├── _get_master_version()   ← Ejecuta capture_version.py
│   ├── register_slave()
│   ├── check_health()           ← Verifica versión
│   ├── execute_remote_task()
│   ├── install_slave_remote()
│   ├── auto_recover_slave()
│   ├── auto_update_slave()      ← Actualización remota
│   └── get_all_status()         ← Incluye commit y version_mismatch
│
└── robust_connection.py         [180 líneas] ← NUEVO
    ├── get/post con retry
    ├── exponential backoff
    └── circuit breaker

app/integrations/
└── telegram_notifier.py         [150 líneas] ← ACTUALIZAR
    └── send_alert()             ← Notificaciones de mismatch

docker/
├── Dockerfile.slave             [35 líneas] ← NUEVO
└── entrypoint-slave.sh          [20 líneas] ← NUEVO

scripts/setup/
├── install_slave_venv.sh        [60 líneas] ← NUEVO
└── install_slave_native.sh      [40 líneas] ← NUEVO
```

### Archivos Actualizados

```
start_d8.py                      [+80 líneas]
├── 10. Construir Slave
├── 11. Ejecutar Slave
├── 12. Agregar IP Slave
├── 13. Ver Status               ← Muestra versiones y mismatches
└── 14. Reintentar Slave

scripts/setup/capture_version.py [Ya existe, sin cambios]

version_info.json                [Ya existe, sin cambios]
```

---

## 🔑 Funcionalidades Clave

### 1. Detección de Desincronización

```python
# En slave_manager.py

def check_health(self, slave_id: str) -> bool:
    response = self.connection.get(f"http://{slave['host']}:{slave['port']}/api/health")
    
    slave_commit = response.json().get('commit', 'unknown')
    
    if slave_commit != self.master_version:
        # Log warning
        self.logger.warning(f"⚠️  Version mismatch: {slave_id}")
        
        # Notificar Telegram
        self.notifier.send_alert(
            f"🔴 Slave {slave_id} en versión incorrecta\n"
            f"Master: {self.master_version}\n"
            f"Slave: {slave_commit}"
        )
        
        # Marcar estado
        slave['status'] = 'version_mismatch'
        slave['version_mismatch'] = True
        return False
    
    return True
```

### 2. Actualización Automática (Opcional)

```python
def auto_update_slave(self, slave_id: str) -> bool:
    """Intenta actualizar slave desactualizado"""
    
    # 1. Git pull
    self.connection.post(
        f"http://{slave['host']}:{slave['port']}/api/execute",
        json={"command": "git pull origin main"}
    )
    
    # 2. Reiniciar
    self.connection.post(
        f"http://{slave['host']}:{slave['port']}/api/restart"
    )
    
    # 3. Verificar
    time.sleep(5)
    return self.check_health(slave_id)
```

### 3. Visualización en UI

```
============================================================
📊 ESTADO DE SLAVES
============================================================

🔖 Versión Master: 76d62ab

✅ slave-001
   192.168.1.100:7600
   Estado: healthy
   Commit: 76d62ab                    ← Mismo que master
   Última conexión: 2025-11-20T10:30:00
   Método: docker

⚠️ slave-002 [🔴 v73a51f2]           ← Indicador visual
   192.168.1.101:7600
   Estado: version_mismatch
   Commit: 73a51f2                    ← Desactualizado
   Última conexión: 2025-11-20T10:29:45
   Método: venv

❌ slave-003
   192.168.1.102:7600
   Estado: unhealthy
   Commit: unknown                    ← No responde
   Última conexión: 2025-11-20T09:15:00
   Método: docker
```

---

## 🧪 Testing

### Test de Detección

```python
# tests/integration/test_version_sync.py

def test_version_mismatch_detection():
    """Verifica que se detecte desincronización"""
    manager = SlaveManager()
    manager.master_version = "76d62ab"
    
    # Mock slave con versión diferente
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {
            "status": "healthy",
            "commit": "73a51f2"
        }
        
        # Debe detectar mismatch y retornar False
        assert manager.check_health("slave-001") == False
        assert manager.slaves["slave-001"]["version_mismatch"] == True

def test_version_match():
    """Verifica que versiones iguales pasen"""
    manager = SlaveManager()
    manager.master_version = "76d62ab"
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {
            "status": "healthy",
            "commit": "76d62ab"
        }
        
        assert manager.check_health("slave-001") == True
        assert manager.slaves["slave-001"]["version_mismatch"] == False
```

---

## 📊 Métricas

| Métrica | Valor | Notas |
|---------|-------|-------|
| Tiempo detección mismatch | < 30s | Intervalo health check |
| Overhead por verificación | ~10ms | Lectura de version_info.json |
| False positives | 0 | Comparación exacta de commit hash |
| Notificaciones | Telegram + logs | Alertas inmediatas |
| Auto-actualización | Opcional | Puede ser manual o automática |

---

## 🎯 Casos de Uso

### Caso 1: Master Actualizado

```
1. Admin hace 'git pull' en master
2. Nuevos commits: 76d62ab → 78c92fe
3. Admin reinicia master
4. SlaveManager ejecuta capture_version.py
5. master_version = "78c92fe"
6. Próximo health check detecta todos slaves desactualizados
7. Telegram notifica para cada slave
8. Admin actualiza slaves (manual o automático)
```

### Caso 2: Slave Instalado Nuevo

```
1. Admin ejecuta opción 10 (Construir Slave)
2. Sistema crea imagen Docker con código actual (78c92fe)
3. Admin ejecuta opción 11 (Ejecutar Slave) en máquina remota
4. Slave inicia con version_info.json actual
5. Health check: 78c92fe == 78c92fe ✅
6. Slave marcado como 'healthy'
```

### Caso 3: Slave Desactualizado

```
1. Slave-002 tiene commit 73a51f2 (varios commits atrás)
2. Health check: 73a51f2 != 78c92fe
3. Logger: "⚠️  DESINCRONIZACIÓN DE VERSIÓN detectada en slave-002"
4. Telegram: "🔴 Slave slave-002 en versión incorrecta"
5. Admin ve opción 13: slave-002 [🔴 v73a51f2]
6. Admin ejecuta opción 14 (Reintentar Slave)
7. Sistema intenta actualización automática
8. Si falla: Admin notificado para actualización manual
```

---

## 🔄 Integración con Arquitectura Existente

### Con Orchestrator

```python
# app/distributed/orchestrator.py

class DistributedOrchestrator:
    def __init__(self):
        self.workers = {}
        self.slave_manager = SlaveManager()  # ← Integración
    
    def assign_task(self, task):
        # Validar versión antes de asignar
        if worker_id in self.slave_manager.slaves:
            if self.slave_manager.slaves[worker_id].get('version_mismatch', False):
                self.logger.error(f"Rechazando tarea para {worker_id}: versión incorrecta")
                return False
        
        # Proceder con asignación
        self.workers[worker_id]['current_task'] = task
```

### Con Autonomous Congress

```python
# scripts/autonomous_congress.py

class AutonomousCongress:
    def run_autonomous_cycle(self):
        # Antes de implementar mejoras, verificar versiones
        slave_manager = SlaveManager()
        mismatches = [
            s['id'] for s in slave_manager.get_all_status()
            if s.get('version_mismatch', False)
        ]
        
        if mismatches:
            self.logger.warning(
                f"⚠️  Detectados {len(mismatches)} slaves desactualizados. "
                f"Actualizarlos antes de implementar mejoras."
            )
```

---

## 📝 Checklist de Implementación

### Fase 1: Infraestructura Base
- [ ] Crear `app/distributed/slave_server.py`
  - [ ] Implementar `get_version_info()`
  - [ ] Endpoint `/api/version`
  - [ ] Endpoint `/api/health` con versión
  - [ ] Endpoint `/api/execute`
- [ ] Crear `app/distributed/slave_manager.py`
  - [ ] Método `_get_master_version()`
  - [ ] Actualizar `check_health()` con verificación
  - [ ] Método `auto_update_slave()` (opcional)
- [ ] Crear `app/distributed/robust_connection.py`

### Fase 2: Notificaciones
- [ ] Actualizar `app/integrations/telegram_notifier.py`
  - [ ] Método `send_alert()` para mismatches
  - [ ] Formateo de mensajes con versiones

### Fase 3: UI
- [ ] Actualizar `start_d8.py`
  - [ ] Opción 10: Construir Slave
  - [ ] Opción 11: Ejecutar Slave
  - [ ] Opción 12: Agregar IP Slave
  - [ ] Opción 13: Ver Status (con versiones)
  - [ ] Opción 14: Reintentar Slave

### Fase 4: Testing
- [ ] Crear `tests/integration/test_version_sync.py`
  - [ ] Test detección de mismatch
  - [ ] Test versiones iguales
  - [ ] Test actualización automática
- [ ] Test manual con 2 máquinas

### Fase 5: Documentación
- [x] `docs/06_knowledge_base/experiencias_profundas/verificacion_versiones_master_slave.md`
- [ ] `docs/01_arquitectura/FASE_4_MASTER_SLAVE.md`
- [ ] Actualizar README principal

---

## 🎓 Lecciones Clave

1. **Commit Hash > Version Tag**
   - Siempre existe
   - Único e inmutable
   - No requiere disciplina de tagging

2. **Actualización Automática en Init**
   - Master ejecuta `capture_version.py` al iniciar
   - No depende de disciplina humana
   - Siempre refleja HEAD actual

3. **Notificaciones Inmediatas**
   - Telegram alerta en < 1 minuto
   - Previene ejecuciones con código desactualizado
   - Evita desperdicio de créditos

4. **Estado Persistente**
   - Guardar `commit` y `version_mismatch` en config
   - Permite histórico y debugging
   - Dashboard visualiza sin hacer requests

5. **Separación de Endpoints**
   - `/api/health`: Info completa cada 30s
   - `/api/version`: Solo versión on-demand

---

## 🚀 Próximos Pasos

1. **Implementar infraestructura base** (~3 horas)
   - slave_server.py
   - slave_manager.py
   - robust_connection.py

2. **Integrar notificaciones** (~1 hora)
   - Telegram alerts
   - Logging estructurado

3. **Actualizar UI** (~2 horas)
   - Opciones 10-14 en start_d8.py
   - Visualización de versiones

4. **Testing local** (~2 horas)
   - Test con localhost como slave
   - Simular desincronización
   - Validar notificaciones

5. **Deployment real** (~4 horas)
   - Instalar slave en segunda máquina
   - Prueba con tráfico real
   - Validar monetización local

**Tiempo estimado total:** ~12 horas de implementación

---

**Fecha:** 2025-11-20  
**Estado:** ⏳ Diseñado (pendiente implementación)  
**Prioridad:** 🔴 ALTA (requisito crítico de FASE 4)
