# 🎯 Administración de Tareas en Sistema Distribuido D8

## 📋 Índice

1. [Arquitectura de Comunicación](#arquitectura)
2. [Flujo de Tareas](#flujo-de-tareas)
3. [Quién Administra Qué](#administración)
4. [Protocolo HTTP](#protocolo-http)
5. [Tipos de Tareas](#tipos-de-tareas)
6. [Ejemplos de Uso](#ejemplos)

---

## Arquitectura de Comunicación {#arquitectura}

### Componentes del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                  SISTEMA PRINCIPAL D8                   │
│  - Darwin (Evolución Genética)                          │
│  - Congreso Autónomo                                    │
│  - Niche Discovery                                      │
│  - Agents                                               │
│                                                         │
│  Usa: app/distributed_integration.py                   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ HTTP POST /api/tasks/submit
                   │ {"type": "agent_action", "data": {...}}
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│             ORCHESTRATOR (Coordinador)                  │
│             Puerto: 5000                                │
│                                                         │
│  Responsabilidades:                                     │
│  ✅ Recibir tareas del sistema principal                │
│  ✅ Mantener cola de tareas (priority queue)            │
│  ✅ Asignar tareas a workers disponibles                │
│  ✅ Monitorear heartbeats de workers                    │
│  ✅ Recolectar resultados                               │
│  ✅ Manejar timeouts y reintentos                       │
│                                                         │
│  Implementación: app/orchestrator_app.py               │
│  Lógica: app/distributed/orchestrator.py               │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ Workers hacen polling:
                   │ GET /api/workers/{id}/tasks
                   │
    ┌──────────────┼──────────────┬──────────────┐
    │              │              │              │
    ▼              ▼              ▼              ▼
┌────────┐    ┌─────────┐   ┌──────────┐   ┌──────────┐
│ Worker │    │ Worker  │   │ Worker   │   │ Worker   │
│ Groq   │    │ Gemini  │   │ DeepSeek │   │ DeepSeek │
│ PC 1   │    │ PC 2    │   │ Raspi #1 │   │ Raspi #2 │
└────────┘    └─────────┘   └──────────┘   └──────────┘

Responsabilidades:
✅ Registrarse con orchestrator al iniciar
✅ Hacer polling cada 5-10s pidiendo trabajo
✅ Ejecutar tareas asignadas
✅ Reportar resultados
✅ Enviar heartbeat cada 30s
```

---

## Flujo de Tareas {#flujo-de-tareas}

### Ciclo Completo de una Tarea

```
┌─────────────────────────────────────────────────────────┐
│ PASO 1: Sistema D8 necesita ejecutar algo              │
│                                                         │
│ Ejemplo: Darwin necesita hacer crossover de genomas    │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ PASO 2: D8 envía tarea al Orchestrator                 │
│                                                         │
│ POST /api/tasks/submit                                 │
│ {                                                       │
│   "type": "evolution_crossover",                       │
│   "data": {                                            │
│     "genome1": {...},                                  │
│     "genome2": {...}                                   │
│   },                                                   │
│   "priority": 7                                        │
│ }                                                      │
│                                                         │
│ Respuesta: {"task_id": "uuid-1234"}                   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ PASO 3: Orchestrator agrega tarea a la cola            │
│                                                         │
│ Cola interna (priority queue):                         │
│   Priority 10: [tarea-A]                               │
│   Priority 7:  [tarea-uuid-1234] ← Nueva               │
│   Priority 5:  [tarea-B, tarea-C]                      │
│                                                         │
│ Estado: "pending"                                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ PASO 4: Worker hace polling                            │
│                                                         │
│ Worker DeepSeek (Raspi):                               │
│   GET /api/workers/deepseek-raspi-1/tasks             │
│                                                         │
│ Orchestrator analiza:                                  │
│   - ¿Worker está disponible? ✅ (status: online)       │
│   - ¿Hay tareas en cola? ✅                            │
│   - ¿Worker puede manejar tarea? ✅                    │
│     (evolution_crossover → DeepSeek OK)                │
│                                                         │
│ Respuesta:                                             │
│ {                                                      │
│   "task": {                                            │
│     "task_id": "uuid-1234",                           │
│     "type": "evolution_crossover",                    │
│     "data": {...}                                     │
│   }                                                   │
│ }                                                      │
│                                                         │
│ Estado tarea: "pending" → "assigned"                   │
│ Estado worker: "online" → "busy"                       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ PASO 5: Worker ejecuta tarea                           │
│                                                         │
│ Worker llama a LLM local (DeepSeek via Ollama):        │
│   - Genera offspring combinando genome1 + genome2       │
│   - Tiempo: ~30 segundos                               │
│                                                         │
│ Resultado:                                             │
│ {                                                      │
│   "success": true,                                     │
│   "genome": {...},                                     │
│   "tokens_used": 500                                   │
│ }                                                      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ PASO 6: Worker reporta resultado                       │
│                                                         │
│ POST /api/tasks/uuid-1234/result                       │
│ {                                                      │
│   "worker_id": "deepseek-raspi-1",                    │
│   "result": {                                          │
│     "success": true,                                   │
│     "genome": {...}                                    │
│   }                                                   │
│ }                                                      │
│                                                         │
│ Orchestrator actualiza:                                │
│   - Estado tarea: "assigned" → "completed"             │
│   - Estado worker: "busy" → "online"                   │
│   - Worker.tasks_completed += 1                        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│ PASO 7: D8 obtiene resultado                           │
│                                                         │
│ D8 estaba haciendo polling:                            │
│   GET /api/tasks/status/uuid-1234                      │
│   (cada 2 segundos)                                    │
│                                                         │
│ Respuesta:                                             │
│ {                                                      │
│   "task_id": "uuid-1234",                             │
│   "status": "completed",                               │
│   "result": {                                          │
│     "success": true,                                   │
│     "genome": {...}                                    │
│   }                                                   │
│ }                                                      │
│                                                         │
│ D8 usa el genoma offspring en su evolución             │
└─────────────────────────────────────────────────────────┘
```

---

## Quién Administra Qué {#administración}

### 🎯 ORCHESTRATOR (El Coordinador)

**Ubicación:** Puede ser el servidor principal o una Raspberry Pi dedicada

**Responsabilidades:**

1. **📥 Recepción de Tareas**
   - Escucha en `0.0.0.0:5000`
   - Endpoint: `POST /api/tasks/submit`
   - Valida formato de tareas
   - Genera UUID para cada tarea

2. **📊 Gestión de Cola**
   - Mantiene `deque` (double-ended queue) con prioridades
   - Ordena por prioridad (1-10, mayor = más urgente)
   - Asigna tareas según capacidad de workers

3. **🤖 Registro de Workers**
   - Endpoint: `POST /api/workers/register`
   - Mantiene diccionario: `worker_id → Worker`
   - Almacena capabilities de cada worker

4. **💓 Monitoreo de Heartbeats**
   - Endpoint: `POST /api/workers/{id}/heartbeat`
   - Actualiza timestamp cada vez que recibe heartbeat
   - Thread background: revisa cada 1s
   - Si worker no envía heartbeat en 60s → marca como "dead"
   - Tareas de workers muertos → regresa a cola

5. **🔄 Asignación de Tareas**
   - Workers hacen polling: `GET /api/workers/{id}/tasks`
   - Orchestrator busca:
     - Worker con status "online" (no "busy" o "dead")
     - Tarea compatible con capabilities del worker
     - Prioridad más alta
   - Si encuentra match → asigna tarea

6. **📤 Recolección de Resultados**
   - Endpoint: `POST /api/tasks/{id}/result`
   - Actualiza estado de tarea
   - Libera worker (busy → online)
   - Incrementa contadores de métricas

7. **📈 Estadísticas**
   - Endpoint: `GET /api/stats`
   - Workers online/busy/dead
   - Tareas pending/assigned/completed/failed
   - Success rate por worker

**Implementación:**
- Archivo: `app/orchestrator_app.py` (Flask app)
- Lógica: `app/distributed/orchestrator.py` (DistributedOrchestrator class)
- Thread background para cleanup de workers muertos

### 🤖 WORKERS (Los Ejecutores)

**Ubicación:** Cualquier máquina en la red (PC, servidor, Raspberry Pi)

**Responsabilidades:**

1. **🔌 Registro al Iniciar**
   ```python
   POST /api/workers/register
   {
       "worker_id": "deepseek-raspi-1",
       "worker_type": "deepseek",
       "capabilities": {
           "models": ["deepseek-coder:6.7b"],
           "max_tokens": 2000
       }
   }
   ```

2. **🔄 Polling Periódico**
   - Cada 5-10 segundos: `GET /api/workers/{id}/tasks`
   - Si hay tarea → la procesa
   - Si no hay → espera y reintenta

3. **💓 Heartbeat**
   - Cada 30 segundos: `POST /api/workers/{id}/heartbeat`
   - Indica "estoy vivo y listo"

4. **⚙️ Ejecución de Tareas**
   - Tipos de tareas que puede manejar:
     - `agent_action`: Generar texto con LLM
     - `evolution_crossover`: Combinar genomas
     - `evolution_mutation`: Mutar genoma
     - `code_generation`: Generar código
   
   - Según worker_type:
     - **Groq:** API cloud, modelos rápidos
     - **Gemini:** API cloud, tier gratis
     - **DeepSeek:** Ollama local, zero-cost

5. **📤 Reporte de Resultados**
   ```python
   POST /api/tasks/{task_id}/result
   {
       "worker_id": "deepseek-raspi-1",
       "result": {
           "success": true,
           "output": "...",
           "tokens_used": 500
       }
   }
   ```

6. **🛑 Desregistro al Cerrar**
   - `POST /api/workers/{id}/unregister`
   - Opcional (orchestrator detecta timeout)

**Implementación:**
- Archivo: `app/distributed/worker_fixed.py` (DistributedWorker class)
- Scripts de inicio: `docker/entrypoint-worker*.sh`

### 🧠 SISTEMA PRINCIPAL D8

**Ubicación:** Servidor principal donde corre Darwin, Congreso, etc.

**Responsabilidades:**

1. **📤 Envío de Tareas**
   - Usa `D8DistributedClient` para comunicarse con orchestrator
   - Decide qué operaciones ejecutar remotamente vs localmente
   - Ejemplo en Darwin:
     ```python
     from app.distributed_integration import DistributedEvolutionAdapter
     
     adapter = DistributedEvolutionAdapter("http://orchestrator:5000")
     offspring = adapter.crossover(parent1.genome, parent2.genome)
     ```

2. **⏳ Espera de Resultados**
   - Dos modos:
     - **Síncrono:** Espera resultado con polling (default)
     - **Asíncrono:** Envía tarea y continúa, consulta después

3. **🔄 Fallback Local**
   - Si orchestrator no disponible → ejecuta localmente
   - Si timeout → reintenta o ejecuta localmente

**Implementación:**
- Módulo: `app/distributed_integration.py`
- Clases principales:
  - `D8DistributedClient`: Cliente genérico
  - `DistributedEvolutionAdapter`: Específico para Darwin

---

## Protocolo HTTP {#protocolo-http}

### Endpoints del Orchestrator

#### 1. Health Check
```http
GET /health

Response:
{
    "status": "healthy",
    "workers_online": 3,
    "tasks_pending": 5
}
```

#### 2. Registrar Worker
```http
POST /api/workers/register

Request:
{
    "worker_id": "groq-worker-1",
    "worker_type": "groq",
    "capabilities": {
        "max_tokens": 2000,
        "models": ["llama-3.3-70b"]
    }
}

Response:
{
    "status": "registered",
    "worker_id": "groq-worker-1"
}
```

#### 3. Heartbeat
```http
POST /api/workers/{worker_id}/heartbeat

Response:
{
    "status": "ok"
}
```

#### 4. Obtener Tarea
```http
GET /api/workers/{worker_id}/tasks

Response (si hay tarea):
{
    "task": {
        "task_id": "uuid-1234",
        "type": "agent_action",
        "data": {...}
    }
}

Response (sin tareas):
{
    "task": null
}
```

#### 5. Enviar Tarea (desde D8)
```http
POST /api/tasks/submit

Request:
{
    "type": "evolution_crossover",
    "data": {
        "genome1": {...},
        "genome2": {...}
    },
    "priority": 7
}

Response:
{
    "task_id": "uuid-1234",
    "status": "submitted"
}
```

#### 6. Reportar Resultado
```http
POST /api/tasks/{task_id}/result

Request:
{
    "worker_id": "deepseek-raspi-1",
    "result": {
        "success": true,
        "output": "..."
    }
}

Response:
{
    "status": "received"
}
```

#### 7. Consultar Estado
```http
GET /api/tasks/status/{task_id}

Response:
{
    "task_id": "uuid-1234",
    "status": "completed",
    "assigned_to": "deepseek-raspi-1",
    "result": {...}
}
```

#### 8. Listar Workers
```http
GET /api/workers/list

Response:
{
    "workers": [
        {
            "worker_id": "groq-worker-1",
            "worker_type": "groq",
            "status": "online",
            "tasks_completed": 150
        },
        ...
    ],
    "total": 3
}
```

---

## Tipos de Tareas {#tipos-de-tareas}

### 1. agent_action
**Propósito:** Ejecutar acción de agente (generar texto con LLM)

**Datos:**
```json
{
    "type": "agent_action",
    "data": {
        "messages": [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."}
        ],
        "model": "llama-3.3-70b",
        "temperature": 0.8
    }
}
```

**Workers compatibles:** Todos (Groq, Gemini, DeepSeek)

### 2. evolution_crossover
**Propósito:** Combinar dos genomas para crear offspring

**Datos:**
```json
{
    "type": "evolution_crossover",
    "data": {
        "genome1": {"param1": 0.8, "param2": 100},
        "genome2": {"param1": 0.6, "param2": 150}
    }
}
```

**Workers compatibles:** DeepSeek (recomendado para zero-cost)

### 3. evolution_mutation
**Propósito:** Mutar un genoma

**Datos:**
```json
{
    "type": "evolution_mutation",
    "data": {
        "genome": {"param1": 0.7, "param2": 120},
        "mutation_rate": 0.1
    }
}
```

**Workers compatibles:** DeepSeek

### 4. code_generation
**Propósito:** Generar código

**Datos:**
```json
{
    "type": "code_generation",
    "data": {
        "prompt": "Create a function that...",
        "language": "python"
    }
}
```

**Workers compatibles:** DeepSeek (especializado en código)

---

## Ejemplos de Uso {#ejemplos}

### Ejemplo 1: Uso Simple desde Python

```python
from app.distributed_integration import D8DistributedClient

# Conectar
client = D8DistributedClient("http://192.168.1.100:5000")

# Ejecutar tarea
result = client.execute_agent_action(
    messages=[{"role": "user", "content": "Generate business ideas"}],
    model="llama-3.3-70b"
)

print(result["output"])
```

### Ejemplo 2: Integración con Darwin

```python
# En app/evolution/darwin.py

from app.distributed_integration import DistributedEvolutionAdapter

class Darwin:
    def __init__(self, use_distributed=True):
        if use_distributed:
            self.adapter = DistributedEvolutionAdapter("http://orchestrator:5000")
    
    def evolve(self, population):
        # Crossover distribuido
        offspring = []
        for i in range(0, len(population), 2):
            child = self.adapter.crossover(
                population[i].genome,
                population[i+1].genome
            )
            offspring.append(Agent(child))
        
        # Mutación distribuida
        for agent in offspring:
            agent.genome = self.adapter.mutate(agent.genome)
        
        return offspring
```

### Ejemplo 3: Tareas en Paralelo

```python
# Enviar 10 tareas sin esperar
task_ids = []
for i in range(10):
    result = client.execute_agent_action(
        messages=[{"role": "user", "content": f"Task {i}"}],
        wait_for_result=False
    )
    task_ids.append(result["task_id"])

# Esperar todas
results = [client._wait_for_result(tid) for tid in task_ids]
```

---

## 🎯 Ventajas del Sistema

1. **Zero-cost con DeepSeek local** - Raspberry Pi 4 + Ollama = $0 API costs
2. **Escalabilidad horizontal** - Agregar más workers = más capacidad
3. **Fault tolerance** - Workers caídos se detectan automáticamente
4. **Load balancing** - Orchestrator distribuye carga según disponibilidad
5. **Paralelización real** - 5 workers = 5x más rápido
6. **Simplicidad** - HTTP REST = fácil debugging con curl
7. **Flexibilidad** - Mix de workers cloud + local
8. **Monitoreo** - Estadísticas en tiempo real

---

**Para más información:**
- Código: `app/orchestrator_app.py`, `app/distributed_integration.py`
- Ejemplos: `examples/distributed_system_usage.py`
- Docker: `docs/02_setup/docker_deployment.md`
