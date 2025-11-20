# 🌐 Arquitectura Distribuida - Guía de Implementación

## 🎯 Concepto

**Raspberry Pi 4** actúa como **orquestador central** que coordina múltiples nodos worker (PCs Windows, Linux, Mac) para ejecutar agentes en paralelo.

### Beneficios

✅ **Escalabilidad infinita:** Agrega computadores según necesites  
✅ **Costo optimizado:** Usa hardware que ya tienes  
✅ **GPU on-demand:** DeepSeek local solo cuando evoluciones  
✅ **Heterogéneo:** Windows, Linux, Mac, lo que sea  
✅ **Tolerancia a fallos:** Si un worker cae, otros continúan  

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────┐
│      RASPBERRY PI 4 (Orquestador)           │
│  - Flask API (puerto 5000)                  │
│  - Task Queue (Redis/in-memory)             │
│  - ChromaDB (memoria compartida)            │
│  - Dashboard (monitoreo)                    │
└──────────────────┬──────────────────────────┘
                   │ HTTP/JSON
        ┌──────────┼──────────┬───────────┐
        │          │          │           │
   ┌────▼───┐ ┌───▼────┐ ┌───▼─────┐ ┌──▼──────┐
   │Worker 1│ │Worker 2│ │Worker 3│ │Worker N │
   │PC Win  │ │Laptop  │ │Server  │ │GPU Node │
   │(Groq)  │ │(Gemini)│ │(Claude)│ │(DeepSeek)
   └────────┘ └────────┘ └────────┘ └─────────┘
```

### Componentes

1. **Orchestrator (Raspi):**
   - Recibe peticiones de agentes
   - Divide en tasks
   - Asigna a workers disponibles
   - Consolida resultados

2. **Workers (cualquier PC):**
   - Registrarse con orchestrator
   - Poll por tasks
   - Ejecutar (llamar a Groq/Gemini/Claude/DeepSeek)
   - Reportar resultados

---

## 🚀 Setup Paso a Paso

### 1. Raspberry Pi (Orquestador)

```bash
# En Raspberry Pi
cd ~/d8

# Activar distributed mode
nano .env
```

Agregar:
```bash
DISTRIBUTED_MODE=true
ORCHESTRATOR_PORT=5000
```

Iniciar:
```bash
python app/main.py
```

Verifica que esté online:
```bash
curl http://raspberrypi.local:5000/api/workers/stats
```

---

### 2. Worker Node (Windows PC)

**En tu PC Windows:**

```powershell
# Clonar repo
git clone https://github.com/lsilva5455/d8.git
cd d8

# Crear virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias (solo lo necesario)
pip install requests python-dotenv psutil

# Si usas Groq
pip install groq

# Si usas Gemini (GRATIS)
pip install google-generativeai
```

**Configurar worker:**

```powershell
# Crear .env para worker
echo @"
ORCHESTRATOR_URL=http://192.168.1.X:5000
WORKER_ID=pc-windows-groq
WORKER_TYPE=groq
API_KEY=tu_groq_api_key
POLL_INTERVAL=5
"@ > .env
```

**Iniciar worker:**

```powershell
python app/distributed/worker.py
```

Output esperado:
```
🔧 Worker initialized: pc-windows-groq (groq)
✅ Registered with orchestrator
🚀 Worker started, polling every 5s
```

---

### 3. Worker Node con GPU (DeepSeek)

**En PC con GPU (Windows/Linux):**

```bash
# Instalar Ollama
curl https://ollama.ai/install.sh | sh  # Linux
# o descargar installer para Windows

# Pull DeepSeek
ollama pull deepseek-coder:33b
ollama serve
```

**Configurar worker:**

```bash
ORCHESTRATOR_URL=http://192.168.1.X:5000
WORKER_ID=gpu-node-deepseek
WORKER_TYPE=deepseek_gpu
API_KEY=none  # Local
DEEPSEEK_BASE_URL=http://localhost:11434
POLL_INTERVAL=5
```

**Iniciar worker:**

```bash
python app/distributed/worker.py
```

---

## 📊 Monitoreo

### Dashboard en Raspi

```bash
curl http://localhost:5000/api/workers/stats | jq
```

Output:
```json
{
  "workers": {
    "total": 3,
    "online": 2,
    "busy": 1,
    "by_type": {
      "groq": 1,
      "gemini": 1,
      "deepseek_gpu": 1
    }
  },
  "tasks": {
    "pending": 5,
    "assigned": 2,
    "completed": 150,
    "failed": 3
  },
  "performance": {
    "total_completed": 150,
    "total_failed": 3,
    "success_rate": 98.04
  }
}
```

### Ver workers registrados

```bash
curl http://raspberrypi.local:5000/api/workers/stats
```

---

## 🔄 Flujo de Ejecución

### Ejemplo: Agent Action

**1. Raspi recibe request:**
```bash
POST /api/agents/agent123/act
{
  "action_type": "content_generation",
  "input_data": {"topic": "AI trends"}
}
```

**2. Orchestrator crea task:**
```python
task_id = orchestrator.submit_task(
    task_type="agent_action",
    task_data={
        "messages": [...],
        "model": "llama-3.1-8b-instant",
        "temperature": 0.8
    },
    priority=5
)
```

**3. Worker disponible poll:**
```python
# Worker PC-Windows-Groq
task = requests.get("http://raspi:5000/api/workers/pc-windows-groq/tasks")
# Recibe task
```

**4. Worker ejecuta:**
```python
from groq import Groq
client = Groq(api_key=api_key)
result = client.chat.completions.create(...)
```

**5. Worker reporta:**
```python
requests.post("http://raspi:5000/api/workers/results", json={
    "task_id": task_id,
    "result": {"success": True, "result": content}
})
```

**6. Raspi retorna a cliente:**
```json
{
  "success": true,
  "result": "AI trends article...",
  "worker_id": "pc-windows-groq"
}
```

---

## 💰 Costos con Arquitectura Distribuida

### Setup Típico

| Componente | Hardware | API | Costo/mes |
|------------|----------|-----|-----------|
| Orchestrator | Raspi 4 8GB | - | $0.50 (electricidad) |
| Worker 1 | PC Windows | Gemini (GRATIS) | $0 |
| Worker 2 | Laptop | Groq | $5-10 |
| Worker 3 | Server | Claude | $10-20 |
| Worker 4 | GPU PC | DeepSeek (local) | $3 (electricidad) |
| **Total** | | | **$18.50-33.50/mes** |

### Capacidad

- **10 agentes** actuando simultáneamente
- **100+ acciones/hora** por agente
- **Evolución local** con GPU (gratis)
- **Escalabilidad horizontal** ilimitada

**ROI esperado:** Depende de nichos descubiertos autónomamente  
**Net profit:** Variable según estrategia evolutiva

---

## 🛠️ Optimizaciones

### 1. Priorización de Tasks

```python
# High priority para revenue-critical actions
orchestrator.submit_task(
    task_type="agent_action",
    task_data=...,
    priority=10  # Ejecuta primero
)
```

### 2. Load Balancing Inteligente

```python
# Orchestrator asigna según:
# - Worker type (Groq para acciones rápidas, Claude para razonamiento)
# - Worker load (evita sobrecargar un worker)
# - Task priority
```

### 3. Failover Automático

```python
# Si worker no responde en 60s:
# - Task regresa a queue
# - Se reasigna a otro worker
# - Worker marcado como offline
```

### 4. Caching de Resultados

```python
# ChromaDB en Raspi cachea:
# - Agent responses frecuentes
# - Evolution results
# - Reduce llamadas API
```

---

## 🔐 Seguridad

### 1. API Key Management

```bash
# Cada worker tiene su propia API key
# No compartas keys entre workers
# Usa .env files (no commitear)
```

### 2. Network Security

```bash
# Firewall en Raspi
sudo ufw allow from 192.168.1.0/24 to any port 5000
sudo ufw enable

# O usa VPN (Tailscale)
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

### 3. Worker Authentication

```python
# TODO: Agregar token-based auth
# Orchestrator verifica worker_token antes de aceptar
```

---

## 📈 Escalabilidad

### Agregar Worker en Runtime

**No requiere reiniciar Raspi:**

```powershell
# En nuevo PC
git clone https://github.com/lsilva5455/d8.git
cd d8
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install requests python-dotenv google-generativeai

# Configurar
echo "ORCHESTRATOR_URL=http://raspi:5000" > .env
echo "WORKER_TYPE=gemini" >> .env
echo "API_KEY=gemini_key" >> .env

# Iniciar
python app/distributed/worker.py
```

**Automáticamente:**
- Worker se registra
- Orchestrator comienza a asignarle tasks
- Capacidad total aumenta

---

## 🧪 Testing

### Test Worker Registration

```python
# test_distributed.py
import requests

# Register fake worker
response = requests.post("http://raspberrypi.local:5000/api/workers/register", json={
    "worker_id": "test-worker",
    "worker_type": "groq",
    "capabilities": {"cpu": 4, "memory_gb": 8}
})

assert response.json()["success"] == True
print("✅ Worker registration OK")
```

### Test Task Execution

```python
# Submit task
task_id = requests.post("http://raspberrypi.local:5000/api/agents/123/act", json={
    "action_type": "test",
    "input_data": {}
}).json()["task_id"]

# Poll for result
time.sleep(5)

result = requests.get(f"http://raspberrypi.local:5000/api/tasks/{task_id}").json()
assert result["status"] == "completed"
print("✅ Task execution OK")
```

---

## 🔄 Migración desde Modo Single

### Antes (todo en Raspi):

```python
# main.py
agent.act(input_data)  # Llama Groq directamente
```

### Después (distribuido):

```python
# main.py
task_id = orchestrator.submit_task("agent_action", {...})
result = wait_for_result(task_id)  # Worker ejecuta
```

**Ventajas:**
- Raspi no hace requests pesados
- Workers en PCs más potentes ejecutan
- Raspi solo coordina

---

## 📚 Próximos Pasos

1. **Implementar en main.py:**
   - Integrar orchestrator blueprint
   - Modificar BaseAgent para usar orchestrator
   
2. **Testing con 1 worker:**
   - Raspi + 1 PC Windows
   - Verificar latencia
   
3. **Escalar gradualmente:**
   - Agregar 2do worker (Gemini gratis)
   - Agregar 3er worker (GPU para evolución)
   
4. **Monitoreo:**
   - Dashboard web en Raspi
   - Logs centralizados

¿Quieres que implemente la integración con `main.py` para habilitar el modo distribuido?
