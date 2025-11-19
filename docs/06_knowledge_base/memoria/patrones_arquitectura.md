# 🏗️ Patrones de Arquitectura

> **Soluciones estructurales probadas en producción**

---

## 📋 Índice

1. [Configuración Dual: .env + JSON](#configuracion-dual)
2. [Worker Distribuido con Heartbeat](#worker-heartbeat)
3. [Orchestrator Pattern](#orchestrator)
4. [Separación app/ + lib/](#separacion-app-lib)

---

## Configuración Dual: .env + JSON {#configuracion-dual}

### Contexto
Proyectos con múltiples entornos (dev/prod), usuarios diferentes, y secretos que no deben commitearse.

### Problema
- `.env` se commitea accidentalmente
- Configuraciones diferentes entre máquinas
- Secretos en el repositorio
- Difícil onboarding de nuevos devs

### Solución

**Separar responsabilidades:**
1. **`.env`** (root del proyecto): Solo API keys y secretos → gitignored
2. **JSON en `~/Documents/d8_data/`**: Configs funcionales → fuera del repo, per-user

**Auto-generación:** Si no existe config, se crea con defaults.

### Ejemplo

```python
from pathlib import Path
import json
from dotenv import load_dotenv

def load_config():
    """Carga config dual: .env + JSON en Documents/d8_data"""
    
    # 1. Cargar secretos del .env
    env_file = Path(__file__).parent / ".env"
    load_dotenv(env_file)
    
    # 2. Cargar config funcional de Documents/d8_data
    app_name = "myapp"
    config_dir = Path.home() / "Documents" / "d8_data" / app_name
    config_file = config_dir / "config.json"
    
    # 3. Auto-generar si no existe
    if not config_file.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        default_config = {
            "population_size": 20,
            "mutation_rate": 0.1,
            "max_actions_per_day": 1000
        }
        config_file.write_text(json.dumps(default_config, indent=2))
    
    # 4. Cargar y retornar
    return json.loads(config_file.read_text())

# Uso
config = load_config()
api_key = os.getenv("API_KEY")  # Desde .env
population = config["population_size"]  # Desde JSON
```

### Resultado

✅ **Seguridad:** Secretos nunca en repo  
✅ **Flexibilidad:** Cada usuario tiene su config  
✅ **DX:** Onboarding automático (configs se auto-generan)  
✅ **Portabilidad:** Funciona en cualquier máquina

### Tags
`#configuration` `#security` `#dx` `#python`

---

## Worker Distribuido con Heartbeat {#worker-heartbeat}

### Contexto
Sistema distribuido donde workers pueden fallar sin aviso (crash, red, etc.)

### Problema
- Orchestrator no sabe si worker está vivo
- Tareas enviadas a workers muertos
- No hay recuperación automática

### Solución

**Sistema de heartbeat:**
1. Worker envía señal cada N segundos
2. Orchestrator marca como "muerto" si no recibe señal
3. Tareas de workers muertos se re-asignan

### Ejemplo

```python
# Worker
import time
import requests
from threading import Thread

class Worker:
    def __init__(self, orchestrator_url, heartbeat_interval=30):
        self.orchestrator_url = orchestrator_url
        self.heartbeat_interval = heartbeat_interval
        self.worker_id = None
        self.running = True
    
    def register(self):
        """Registrarse con orchestrator"""
        response = requests.post(
            f"{self.orchestrator_url}/api/workers/register",
            json={"capabilities": ["llm", "vision"]}
        )
        self.worker_id = response.json()["worker_id"]
    
    def heartbeat_loop(self):
        """Enviar heartbeat periódicamente"""
        while self.running:
            try:
                requests.post(
                    f"{self.orchestrator_url}/api/workers/{self.worker_id}/heartbeat"
                )
            except:
                pass  # Continuar intentando
            time.sleep(self.heartbeat_interval)
    
    def start(self):
        self.register()
        Thread(target=self.heartbeat_loop, daemon=True).start()
        self.work_loop()

# Orchestrator
from datetime import datetime, timedelta

class Orchestrator:
    def __init__(self, heartbeat_timeout=60):
        self.workers = {}  # worker_id -> {last_heartbeat, status}
        self.heartbeat_timeout = heartbeat_timeout
    
    def update_heartbeat(self, worker_id):
        """Actualizar timestamp de heartbeat"""
        if worker_id in self.workers:
            self.workers[worker_id]["last_heartbeat"] = datetime.now()
            self.workers[worker_id]["status"] = "alive"
    
    def check_dead_workers(self):
        """Marcar workers sin heartbeat como muertos"""
        now = datetime.now()
        timeout = timedelta(seconds=self.heartbeat_timeout)
        
        for worker_id, info in self.workers.items():
            if now - info["last_heartbeat"] > timeout:
                info["status"] = "dead"
                self.reassign_tasks(worker_id)
    
    def get_alive_workers(self):
        """Retornar solo workers vivos"""
        return [
            wid for wid, info in self.workers.items()
            if info["status"] == "alive"
        ]
```

### Resultado

✅ **Resiliencia:** Detecta workers caídos automáticamente  
✅ **Recuperación:** Re-asigna tareas sin intervención  
✅ **Monitoreo:** Vista en tiempo real del estado del cluster  
✅ **Simplicidad:** Solo HTTP, sin dependencias complejas

### Tags
`#distributed` `#monitoring` `#resilience` `#python`

---

## Orchestrator Pattern {#orchestrator}

### Contexto
Sistema con múltiples workers procesando tareas en paralelo.

### Problema
- ¿Quién asigna tareas a workers?
- ¿Cómo balancear la carga?
- ¿Cómo escalar horizontalmente?

### Solución

**Orchestrator centralizado:**
1. Workers se registran con capabilities
2. Orchestrator mantiene cola de tareas
3. Asigna tareas según capability matching
4. Workers reportan resultados

### Ejemplo

```python
# Orchestrator (Flask)
from flask import Flask, request, jsonify
from queue import Queue
import uuid

app = Flask(__name__)

workers = {}  # worker_id -> capabilities
task_queue = Queue()
results = {}  # task_id -> result

@app.route("/api/workers/register", methods=["POST"])
def register_worker():
    """Registrar nuevo worker"""
    worker_id = str(uuid.uuid4())
    capabilities = request.json.get("capabilities", [])
    
    workers[worker_id] = {
        "capabilities": capabilities,
        "status": "idle"
    }
    
    return jsonify({"worker_id": worker_id})

@app.route("/api/tasks", methods=["POST"])
def create_task():
    """Crear nueva tarea"""
    task_id = str(uuid.uuid4())
    task_data = request.json
    
    task_queue.put({
        "task_id": task_id,
        "data": task_data
    })
    
    return jsonify({"task_id": task_id})

@app.route("/api/workers/<worker_id>/poll", methods=["GET"])
def poll_task(worker_id):
    """Worker solicita tarea"""
    if task_queue.empty():
        return jsonify({"task": None})
    
    task = task_queue.get()
    workers[worker_id]["status"] = "busy"
    
    return jsonify({"task": task})

@app.route("/api/tasks/<task_id>/result", methods=["POST"])
def submit_result(task_id):
    """Worker envía resultado"""
    result = request.json
    results[task_id] = result
    
    worker_id = request.json.get("worker_id")
    if worker_id:
        workers[worker_id]["status"] = "idle"
    
    return jsonify({"status": "ok"})

# Worker
class Worker:
    def __init__(self, orchestrator_url):
        self.orchestrator_url = orchestrator_url
        self.worker_id = None
    
    def register(self):
        resp = requests.post(
            f"{self.orchestrator_url}/api/workers/register",
            json={"capabilities": ["text_generation"]}
        )
        self.worker_id = resp.json()["worker_id"]
    
    def work_loop(self):
        while True:
            # Solicitar tarea
            resp = requests.get(
                f"{self.orchestrator_url}/api/workers/{self.worker_id}/poll"
            )
            task = resp.json().get("task")
            
            if task:
                # Procesar
                result = self.process(task)
                
                # Reportar resultado
                requests.post(
                    f"{self.orchestrator_url}/api/tasks/{task['task_id']}/result",
                    json={
                        "worker_id": self.worker_id,
                        "result": result
                    }
                )
            else:
                time.sleep(5)  # Esperar antes de reintentar
```

### Resultado

✅ **Escalabilidad:** Agregar workers = más capacidad  
✅ **Load Balancing:** Distribución automática de carga  
✅ **Flexibilidad:** Workers especializados por capability  
✅ **Simplicidad:** Protocolo HTTP simple

### Tags
`#distributed` `#coordination` `#scalability` `#flask` `#python`

---

## Separación app/ + lib/ {#separacion-app-lib}

### Contexto
Proyectos que necesitan separar lógica de negocio de utilities reutilizables.

### Problema
- Código genérico mezclado con lógica específica del proyecto
- Difícil reutilizar componentes en otros proyectos
- No está claro qué es específico y qué es genérico
- Crecimiento desordenado del código

### Solución

**Estructura flat layout con separación clara:**

```
proyecto/
├── app/              # Lógica específica del proyecto
│   ├── agents/       # Features del negocio
│   ├── evolution/    # Lógica core
│   └── distributed/  # Módulos específicos
├── lib/              # Utilities reutilizables
│   ├── llm/          # LLM clients
│   ├── validation/   # Schemas
│   └── parsers/      # Text processing
└── scripts/          # Executables
```

**Ventajas sobre `src/`:**
1. Estándar Python moderno (Django, FastAPI, Flask usan esto)
2. No requiere configuración de PYTHONPATH
3. Herramientas lo entienden nativamente
4. Separación clara sin over-engineering

### Ejemplo

```python
# Estructura de lib/llm/
lib/
├── __init__.py
└── llm/
    ├── __init__.py
    ├── base.py         # Abstract base class
    ├── groq.py         # Groq client
    ├── gemini.py       # Gemini client
    └── deepseek.py     # DeepSeek client

# lib/llm/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLLMClient(ABC):
    """Abstract base class for all LLM clients"""
    
    def __init__(self, model: str):
        self.model = model
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Any:
        """Send chat completion request"""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Simple text generation"""
        pass
    
    def estimate_cost(self, tokens: int) -> float:
        """Estimate cost for given token count"""
        return 0.0

# lib/llm/groq.py
from .base import BaseLLMClient
from groq import Groq

class GroqClient(BaseLLMClient):
    """Groq API client"""
    
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        super().__init__(model)
        self.client = Groq(api_key=api_key)
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        return {
            "content": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens
        }
    
    def generate(self, prompt: str, **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        response = self.chat(messages, **kwargs)
        return response["content"]

# lib/llm/__init__.py
from .base import BaseLLMClient
from .groq import GroqClient
from .gemini import GeminiClient
from .deepseek import DeepSeekClient

__all__ = [
    "BaseLLMClient",
    "GroqClient",
    "GeminiClient", 
    "DeepSeekClient"
]

# Uso en app/
from lib.llm import GroqClient, GeminiClient

# Instanciar
groq = GroqClient(api_key="gsk_xxx")
gemini = GeminiClient(api_key="AIza_xxx")

# Interface unificada
response = groq.chat(messages=[...])
response = gemini.chat(messages=[...])
```

### Criterio de Decisión

**→ lib/** si:
- ✅ Lo usarías en otro proyecto
- ✅ Es agnóstico del proyecto actual
- ✅ Tiene dependencias mínimas
- ✅ Es un utility o helper genérico

**→ app/** si:
- ✅ Específico del proyecto
- ✅ Usa lógica de negocio propia
- ✅ Depende de otros módulos de app/

### Resultado

✅ **Reutilización:** Código en lib/ portable a otros proyectos  
✅ **Claridad:** Separación explícita entre genérico y específico  
✅ **Simplicidad:** Sin configuración extra, funciona out-of-the-box  
✅ **Estándar:** Sigue convenciones modernas de Python  
✅ **Extensibilidad:** Fácil agregar nuevos componentes a lib/

### Alternativas Descartadas

**`src/` layout:**
```
src/
  app/
  lib/
```

❌ No es el estándar Python moderno  
❌ Requiere configuración de PYTHONPATH  
❌ Solo útil si publicas en PyPI

**Todo en `app/`:**
```
app/
  agents/
  llm_clients/  # Mezclado
```

❌ Código genérico no reutilizable  
❌ No está claro qué es qué

### Tags
`#arquitectura` `#organizacion` `#reutilizacion` `#python` `#lib`

---

**Última actualización:** 2025-11-19  
**Fuente:** Experiencias D8
