# 🐛 Debug Guide - D8

**Guía completa para debuggear componentes de D8**

---

## 🎯 Estrategia General de Debugging

### 1. Identifica el Componente
- ¿Orchestrator?
- ¿Worker?
- ¿Agent?
- ¿Sistema evolutivo?
- ¿Congreso?

### 2. Revisa Logs
```bash
# Logs generales
Get-Content data/logs/d8.log -Tail 100

# Logs de orchestrator
Get-Content data/logs/orchestrator.log -Tail 50

# Logs de workers
Get-Content data/logs/worker_*.log -Tail 50
```

### 3. Reproduce el Error
```bash
# Ejecuta en modo verbose
python script.py --verbose

# O con debugging
python -m pdb script.py
```

---

## 🔍 Debugging por Componente

### Orchestrator

**Estado del orchestrator:**
```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/workers
curl http://localhost:5000/api/tasks
```

**Logs en tiempo real:**
```powershell
Get-Content data/logs/orchestrator.log -Wait
```

**Breakpoints comunes:**
```python
# app/distributed/orchestrator.py
@app.route('/api/task', methods=['POST'])
def submit_task():
    import pdb; pdb.set_trace()  # ← Breakpoint aquí
    # ...
```

### Workers

**Verificar registro:**
```python
# app/distributed/worker_groq.py
def register_worker():
    print(f"Registrando worker en {ORCHESTRATOR_URL}")
    import pdb; pdb.set_trace()
    # ...
```

**Heartbeat debugging:**
```python
def send_heartbeat():
    print(f"Enviando heartbeat: {self.worker_id}")
    # Log response
    print(f"Response: {response.status_code}")
```

### Agents

**Trace de decisiones:**
```python
# app/agents/base_agent.py
def run(self, task: str) -> str:
    print(f"[{self.name}] Task: {task}")
    print(f"[{self.name}] Genome: {self.genome[:100]}...")
    
    result = self._call_llm(task)
    print(f"[{self.name}] Result: {result[:200]}...")
    
    return result
```

---

## 🧪 Testing en Modo Debug

### Ejecutar test específico con debugging:
```bash
pytest -v -s tests/unit/test_agent.py::test_specific_function
```

### Breakpoint en test:
```python
def test_agent_fitness():
    agent = BaseAgent(genome="test genome")
    import pdb; pdb.set_trace()
    fitness = agent.evaluate_fitness(task)
    assert fitness > 0
```

---

## 📊 Monitoring en Producción

### Health checks:
```bash
# Script de monitoreo
while ($true) {
    $health = Invoke-RestMethod http://localhost:5000/api/health
    Write-Host "$(Get-Date) - Status: $($health.status)"
    Start-Sleep -Seconds 30
}
```

### Alertas automáticas:
```python
# scripts/monitor.py
import requests
import time

while True:
    try:
        r = requests.get("http://localhost:5000/api/health", timeout=5)
        if r.status_code != 200:
            send_alert("Orchestrator down!")
    except:
        send_alert("Orchestrator unreachable!")
    
    time.sleep(60)
```

---

## 🔧 Herramientas Útiles

### PowerShell
```powershell
# Ver procesos Python
Get-Process python

# Ver puertos en uso
netstat -ano | findstr :5000

# Matar proceso por puerto
Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess
```

### Python
```python
# Profiling
python -m cProfile -o profile.stats script.py
python -m pstats profile.stats

# Memory profiling
from memory_profiler import profile

@profile
def mi_funcion():
    # ...
```

---

**Volver a [Troubleshooting](README.md)**
