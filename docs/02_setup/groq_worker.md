# 🚀 GUÍA RÁPIDA: CONFIGURAR GROQ WORKER (SOLUCIÓN INMEDIATA)

## ⏱️ Tiempo estimado: 3 minutos

---

## 📝 PASO 1: Obtener API Key de Groq (GRATIS)

1. Visita: https://console.groq.com/keys
2. Crea cuenta con Google/GitHub
3. Click en "Create API Key"
4. Copia la key (empieza con `gsk_...`)

**Free Tier Groq:**
- ✅ 30 requests/minuto (2x más que Gemini)
- ✅ 14,400 requests/día
- ✅ Modelo: llama-3.3-70b-versatile (más rápido)
- ✅ Sin verificación de tarjeta

---

## 🔧 PASO 2: Crear Worker de Groq

Crea archivo: `.env.worker.groq`

```bash
# API Configuration
GROQ_API_KEY=gsk_TU_KEY_AQUI

# Worker Configuration  
WORKER_ID=groq-worker-1
WORKER_TYPE=groq
ORCHESTRATOR_URL=http://localhost:5000

# System
WORKER_POLL_INTERVAL=5
```

---

## 📄 PASO 3: Crear Script del Worker

Crea archivo: `app/distributed/worker_groq.py`

```python
#!/usr/bin/env python3
"""Groq Worker - Fast and free inference"""

import os
import time
import requests
from dataclasses import dataclass
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from groq import Groq

# Load environment
load_dotenv('.env.worker.groq')

@dataclass
class WorkerConfig:
    worker_id: str = os.getenv('WORKER_ID', 'groq-worker-1')
    worker_type: str = 'groq'
    orchestrator_url: str = os.getenv('ORCHESTRATOR_URL', 'http://localhost:5000')
    poll_interval: int = int(os.getenv('WORKER_POLL_INTERVAL', '5'))
    api_key: str = os.getenv('GROQ_API_KEY', '')

class GroqWorker:
    def __init__(self, config: WorkerConfig):
        self.config = config
        self.client = Groq(api_key=config.api_key)
        self.model = "llama-3.3-70b-versatile"
        
    def register(self) -> bool:
        """Register with orchestrator"""
        try:
            response = requests.post(
                f"{self.config.orchestrator_url}/api/workers/register",
                json={
                    "worker_id": self.config.worker_id,
                    "worker_type": self.config.worker_type,
                    "capabilities": {
                        "models": [self.model],
                        "max_tokens": 32768,
                        "supports_streaming": True
                    }
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return False
    
    def get_task(self) -> Optional[Dict[str, Any]]:
        """Poll for tasks"""
        try:
            response = requests.get(
                f"{self.config.orchestrator_url}/api/workers/{self.config.worker_id}/tasks",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('task')
        except:
            pass
        return None
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent action via Groq"""
        try:
            task_data = task.get('task_data', {})
            messages = task_data.get('messages', [])
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=task_data.get('temperature', 0.8),
                max_tokens=task_data.get('max_tokens', 2000)
            )
            
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model": self.model,
                "tokens": response.usage.total_tokens
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def report_result(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Report task result"""
        try:
            response = requests.post(
                f"{self.config.orchestrator_url}/api/workers/{self.config.worker_id}/result",
                json={
                    "task_id": task_id,
                    "result": result
                },
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def start(self):
        """Main worker loop"""
        print(f"🚀 Groq Worker starting...")
        print(f"   ID: {self.config.worker_id}")
        print(f"   Model: {self.model}")
        print(f"   Orchestrator: {self.config.orchestrator_url}")
        
        # Register
        if not self.register():
            print("❌ Failed to register, exiting")
            return
        
        print("✅ Registered successfully")
        print("⏳ Polling for tasks...")
        
        while True:
            try:
                # Get task
                task = self.get_task()
                
                if task:
                    task_id = task.get('task_id')
                    print(f"\n📥 Received task: {task_id}")
                    
                    # Execute
                    result = self.execute_task(task)
                    
                    # Report
                    if self.report_result(task_id, result):
                        status = "✅" if result.get('success') else "❌"
                        print(f"{status} Task {task_id} completed")
                    else:
                        print(f"⚠️  Failed to report result for {task_id}")
                
                time.sleep(self.config.poll_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️  Worker stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in worker loop: {e}")
                time.sleep(self.config.poll_interval)

if __name__ == '__main__':
    config = WorkerConfig()
    
    if not config.api_key:
        print("❌ GROQ_API_KEY not set in .env.worker.groq")
        exit(1)
    
    worker = GroqWorker(config)
    worker.start()
```

---

## 🎯 PASO 4: Instalar Dependencia

```powershell
.\venv\Scripts\pip.exe install groq
```

---

## 🚀 PASO 5: Lanzar Worker de Groq

**Opción A: Terminal manual**
```powershell
$env:PYTHONPATH="C:\Users\PcDos\d8"
.\venv\Scripts\python.exe app/distributed/worker_groq.py
```

**Opción B: Actualizar launch_distributed.bat**
Edita `launch_distributed.bat` y agrega:

```batch
REM Launch Groq Worker (nuevo)
timeout /t 10 /nobreak
start "Groq Worker" cmd /k "cd /d %~dp0 && set PYTHONPATH=%~dp0 && venv\Scripts\python.exe app/distributed/worker_groq.py"
```

---

## ✅ PASO 6: Verificar Sistema

```powershell
# Ver estadísticas
curl http://localhost:5000/api/workers/stats

# Deberías ver:
# "by_type": {
#   "gemini": 1,
#   "groq": 1    ← NUEVO
# }
```

---

## 🧪 PASO 7: Probar con Groq

```powershell
# Enviar tarea de prueba
Invoke-RestMethod -Uri "http://localhost:5000/api/test/task" `
  -Method POST `
  -Body (ConvertTo-Json @{prompt="Responde en español: ¿Quién eres?"}) `
  -ContentType "application/json"
```

El orchestrator asignará la tarea al worker **más rápido disponible** (Groq).

---

## 💰 VENTAJAS DE GROQ

### vs Gemini Free:
- ✅ 2x más requests/minuto (30 vs 15)
- ✅ 10x más requests/día (14,400 vs 1,500)
- ✅ **2-3x MÁS RÁPIDO** (tokens/segundo)
- ✅ Modelo más potente (Llama 3.3 70B)

### Costos Real-World:
```
Content Empire (Opción A):
- 5 agentes × 100 posts/día = 500 requests/día
- Groq free tier: 14,400/día
- SOBRAN: 13,900 requests
- Costo: $0.00/mes ✅

Device Farm (Opción B):  
- 20 dispositivos × 50 acciones/día = 1,000 requests/día
- Groq free tier: 14,400/día
- SOBRAN: 13,400 requests  
- Costo: $0.00/mes ✅
```

---

## 🎯 RESULTADO ESPERADO

```
🚀 Groq Worker starting...
   ID: groq-worker-1
   Model: llama-3.3-70b-versatile
   Orchestrator: http://localhost:5000
✅ Registered successfully
⏳ Polling for tasks...

📥 Received task: abc-123-def
✅ Task abc-123-def completed (1.2s, 150 tokens)
```

---

## 📊 PRÓXIMOS PASOS

1. **Una vez funcionando Groq:**
   - Deshabilita temporalmente worker de Gemini (hasta que resetee)
   - Groq manejará todas las tareas

2. **Mañana cuando Gemini resetee:**
   - Reactiva worker de Gemini
   - Tendrás **2 workers heterogéneos**
   - Load balancing automático

3. **Para producción:**
   - Agrega 1-2 workers más (DeepSeek local, Claude, etc.)
   - Diversificación = sin rate limits

---

**🔗 Recursos:**
- Groq Console: https://console.groq.com
- Groq Docs: https://console.groq.com/docs
- Modelos disponibles: https://console.groq.com/docs/models

---

**Tiempo total: 3 minutos**  
**Costo: $0.00**  
**Resultado: Sistema funcional AHORA** ✅
