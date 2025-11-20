# 🚀 Guía de Uso: Sistema Distribuido D8

## Descripción General

El sistema distribuido D8 permite ejecutar el **orquestador** (servidor central) y los **workers** (procesadores) de forma independiente y escalable. Esto habilita:

- ✅ Procesamiento distribuido en múltiples máquinas
- ✅ Workers especializados (Groq, Gemini, DeepSeek local)
- ✅ Fallback automático cuando no hay API keys disponibles
- ✅ Zero-cost processing con DeepSeek local

---

## Arquitectura

```
┌─────────────────────┐
│   NICHE DISCOVERY   │
│  (Cliente D8)       │
└──────────┬──────────┘
           │ HTTP POST /api/tasks/submit
           ▼
┌─────────────────────┐
│   ORCHESTRATOR      │ ← Puerto 7001
│  (Servidor Central) │
└──────────┬──────────┘
           │ HTTP GET /api/workers/{id}/tasks
           ▼
┌─────────────────────┐
│   WORKERS           │
│  ├─ Groq            │
│  ├─ Gemini          │
│  └─ DeepSeek Local  │
└─────────────────────┘
```

---

## 🎯 Inicio Rápido

### 1. Levantar Orchestrator (Servidor Central)

```bash
python start_d8.py
# Seleccionar opción 4: Orchestrator
```

El orchestrator escuchará en `http://localhost:7001`

**Verificar:**
```bash
curl http://localhost:7001/health
# Respuesta: {"status": "healthy", "service": "d8-orchestrator", ...}
```

### 2. Levantar Workers (Procesadores)

**En terminales separadas:**

#### Worker Groq (requiere API key):
```bash
python start_d8.py
# Seleccionar opción 5: Worker Groq
```

#### Worker Gemini (requiere API key):
```bash
python start_d8.py
# Seleccionar opción 6: Worker Gemini
```

#### Worker DeepSeek Local (zero-cost):
```bash
python start_d8.py
# Seleccionar opción 7: Worker DeepSeek
```

### 3. Ejecutar Niche Discovery

```bash
python start_d8.py
# Seleccionar opción 2: Niche Discovery
```

---

## 🔄 Flujo Automático

### Sin API Keys (Zero-Cost Mode)

Si no tienes `GEMINI_API_KEY` ni `GROQ_API_KEY`:

1. **Niche Discovery detecta ausencia de APIs**
2. **Se conecta automáticamente al orchestrator**
3. **Envía tareas al orchestrator** con prioridad alta
4. **Workers procesan las tareas**
5. **Niche Discovery recibe resultados**

### Con API Keys

Si tienes API keys, Niche Discovery las usará directamente (más rápido).

---

## ⚙️ Configuración

### Variables de Entorno

Crea/edita `.env` en la raíz del proyecto:

```bash
# API Keys (opcional)
GEMINI_API_KEY=tu_api_key_aqui
GROQ_API_KEY=tu_api_key_aqui

# Orchestrator URL (si está en otra máquina)
ORCHESTRATOR_URL=http://192.168.1.100:7001
```

### Prioridades de Tareas

En `scripts/niche_discovery_agent.py`:

```python
response = distributed_client.execute_agent_action(
    messages=[{"role": "user", "content": prompt}],
    model="llama-3.3-70b",
    temperature=0.3,
    priority=7,  # 1-10, más alto = más urgente
    wait_for_result=True
)
```

---

## 📊 Monitoreo

### Ver Estadísticas del Orchestrator

```bash
curl http://localhost:7001/api/stats
```

**Respuesta:**
```json
{
  "workers": {
    "total": 2,
    "online": 2,
    "busy": 0,
    "by_type": {
      "groq": 1,
      "gemini": 1
    }
  },
  "tasks": {
    "total": 15,
    "pending": 0,
    "assigned": 0,
    "completed": 14,
    "failed": 1
  },
  "performance": {
    "total_completed": 14,
    "total_failed": 1,
    "success_rate": 93.3
  }
}
```

### Ver Workers Registrados

```bash
curl http://localhost:7001/api/workers/list
```

### Ver Estado de una Tarea

```bash
curl http://localhost:7001/api/tasks/status/{task_id}
```

---

## 🛠️ Troubleshooting

### Error: "Orchestrator not reachable"

**Problema:** Niche Discovery no puede conectarse al orchestrator.

**Solución:**
1. Verificar que orchestrator está corriendo:
   ```bash
   curl http://localhost:7001/health
   ```
2. Si orchestrator está en otra máquina, verificar URL en `.env`:
   ```bash
   ORCHESTRATOR_URL=http://192.168.1.100:7001
   ```

### Error: "No workers available"

**Problema:** No hay workers registrados para procesar tareas.

**Solución:**
1. Levantar al menos un worker (opciones 5, 6 o 7 en `start_d8.py`)
2. Verificar que el worker se registró:
   ```bash
   curl http://localhost:7001/api/workers/list
   ```

### Worker no procesa tareas

**Problema:** Worker está online pero no toma tareas.

**Solución:**
1. Verificar logs del worker para errores
2. Verificar que el worker tiene las capabilities correctas
3. Reiniciar worker

### Tareas quedan en "pending"

**Problema:** Tareas no se asignan a workers.

**Solución:**
1. Verificar que hay workers online:
   ```bash
   curl http://localhost:7001/api/stats
   ```
2. Verificar que los workers tienen capacidad para el tipo de tarea
3. Verificar logs del orchestrator

---

## 🚀 Casos de Uso

### Caso 1: Desarrollo Local (1 máquina)

```bash
# Terminal 1
python start_d8.py  # Opción 4: Orchestrator

# Terminal 2
python start_d8.py  # Opción 5: Worker Groq

# Terminal 3
python start_d8.py  # Opción 2: Niche Discovery
```

### Caso 2: Raspberry Pi como Worker Zero-Cost

**En Raspberry Pi:**
```bash
python start_d8.py  # Opción 7: Worker DeepSeek
```

**En PC principal:**
```bash
# Terminal 1
python start_d8.py  # Opción 4: Orchestrator

# Terminal 2
python start_d8.py  # Opción 2: Niche Discovery
```

### Caso 3: Múltiples Workers (Escalabilidad)

```bash
# Terminal 1: Orchestrator
python start_d8.py  # Opción 4

# Terminal 2-N: Workers (mismo comando N veces)
python start_d8.py  # Opción 5 o 6 o 7
```

Cada worker se registra automáticamente con ID único.

---

## 📝 Notas

### Prioridades de Fallback

Niche Discovery intenta en orden:

1. **Gemini API** (si `GEMINI_API_KEY` está definida)
2. **Orchestrator distribuido** (si está disponible)
3. **Groq API via BaseAgent** (si `GROQ_API_KEY` está definida)

### Heartbeat

Workers envían heartbeat cada 30 segundos. Si el orchestrator no recibe heartbeat en 60 segundos, marca el worker como "stale" y lo elimina.

### Polling Interval

Workers hacen polling cada 5-10 segundos buscando tareas nuevas.

---

## 🔗 Referencias

- [Documentación Docker](../02_setup/docker_deployment.md)
- [Administración de Tareas](../03_operaciones/administracion_tareas.md)
- [Troubleshooting](../05_troubleshooting/)

---

**Última actualización:** 2025-11-19  
**Versión:** 1.0.0
