# 📡 Comunicación Master-Slave en D8 - Explicación Técnica

**Fecha:** 2025-11-20  
**Propósito:** Documentar cómo funciona la comunicación distribuida en FASE 4

---

## 🎯 Resumen Ejecutivo

**Protocolo:** HTTP REST API sobre TCP/IP  
**Puerto:** 7600 (configurable)  
**Autenticación:** Bearer Token  
**Retry:** 3 intentos con exponential backoff  
**Health Check:** Cada 30 segundos  
**Version Sync:** Verificación automática por Git commit

---

## 🏗️ Arquitectura de Comunicación

```
┌──────────────────────────────────────────────────┐
│                    MASTER                        │
│              (Raspberry Pi / PC)                 │
│                                                  │
│  ┌────────────────┐     ┌─────────────────┐     │
│  │ SlaveManager   │────▶│ RobustConnection│     │
│  │                │     │                 │     │
│  │ - register()   │     │ - retry 3x      │     │
│  │ - health()     │     │ - backoff       │     │
│  │ - execute()    │     │ - timeout 30s   │     │
│  └────────────────┘     └────────┬────────┘     │
│                                  │              │
└──────────────────────────────────┼──────────────┘
                                   │
                                   │ HTTP Request
                                   │ POST /api/execute
                                   │ Authorization: Bearer token
                                   │
                                   ▼
┌──────────────────────────────────────────────────┐
│                    SLAVE                         │
│            (PC / VPS / Laptop)                   │
│                                                  │
│  ┌────────────────────────────────────────┐     │
│  │         SlaveServer (Flask)            │     │
│  │                                        │     │
│  │  GET  /api/health  → Status + version │     │
│  │  GET  /api/version → Git commit       │     │
│  │  POST /api/execute → Run task         │     │
│  │                                        │     │
│  └────────────┬───────────────────────────┘     │
│               │                                  │
│               ├─▶ Docker (si disponible)        │
│               ├─▶ venv (si disponible)          │
│               └─▶ Python nativo (siempre)       │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 🔌 Endpoints del Slave

### 1. Health Check

**Endpoint:** `GET /api/health`  
**Auth:** No requerido  
**Timeout:** 10 segundos

**Request:**
```http
GET http://192.168.1.100:7600/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "python_version": "3.10.11 (main, Apr  5 2023...)",
  "execution_methods": {
    "docker": false,
    "venv": true,
    "python": true
  },
  "version": "1.0.0",
  "commit": "66a81d3f2c4a8b9e1d5f7a2b8c9d0e1f2a3b4c5d",
  "branch": "docker-workers"
}
```

**Uso:** Master lo llama cada 30s para verificar que slave esté vivo.

### 2. Version Check

**Endpoint:** `GET /api/version`  
**Auth:** No requerido  
**Timeout:** 5 segundos

**Request:**
```http
GET http://192.168.1.100:7600/api/version
```

**Response:**
```json
{
  "commit": "66a81d3f2c4a8b9e1d5f7a2b8c9d0e1f2a3b4c5d",
  "version": "1.0.0",
  "branch": "docker-workers"
}
```

**Uso:** Master compara commit del slave con el suyo para detectar desincronización.

### 3. Execute Task

**Endpoint:** `POST /api/execute`  
**Auth:** Bearer token requerido  
**Timeout:** 300 segundos (5 minutos)

**Request:**
```http
POST http://192.168.1.100:7600/api/execute
Authorization: Bearer default-dev-token-change-in-production
Content-Type: application/json

{
  "command": "def fibonacci(n):\n    if n <= 1: return n\n    return fibonacci(n-1) + fibonacci(n-2)\nprint(fibonacci(10))",
  "working_dir": "/app"
}
```

**Response (éxito):**
```json
{
  "success": true,
  "output": "55\n",
  "error": "",
  "method": "venv"
}
```

**Response (error):**
```json
{
  "success": false,
  "output": "",
  "error": "NameError: name 'fibonaccci' is not defined",
  "method": "python"
}
```

---

## 🔐 Autenticación

### Token Bearer

**Configuración (.env):**
```env
SLAVE_TOKEN=tu-token-secreto-muy-largo-y-aleatorio
```

**Header HTTP:**
```
Authorization: Bearer tu-token-secreto-muy-largo-y-aleatorio
```

### Validación en Slave

```python
def _validate_token(token: str) -> bool:
    """Valida token de autenticación"""
    return token == SLAVE_TOKEN
```

**Si token inválido:**
```json
{
  "error": "Unauthorized"
}
```
HTTP Status: 401

---

## 🔄 RobustConnection - Sistema de Retry

### Características

- **3 intentos** antes de fallar
- **Exponential backoff:** 2^n segundos (2s, 4s, 8s)
- **Circuit breaker:** Abre tras 5 fallos consecutivos por 60s
- **Timeout configurable:** 30s por defecto

### Código

```python
class RobustConnection:
    def get(self, url, timeout=30, retries=3):
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=timeout)
                self._record_success()
                return response
                
            except requests.exceptions.Timeout:
                logger.warning(f"⏱️ Timeout en intento {attempt+1}/{retries}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Backoff
                    
            except requests.exceptions.ConnectionError:
                logger.warning(f"🔌 Connection error en intento {attempt+1}/{retries}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        
        self._record_failure()
        return None
```

### Circuit Breaker

```python
def _is_circuit_open(self) -> bool:
    if self.failure_count >= 5:
        # Abrir circuito por 60 segundos
        if time.time() - self.last_failure < 60:
            return True
        else:
            # Reintentar tras cooldown
            self.failure_count = 0
    return False
```

---

## 📊 Flujo Completo de Ejecución

### 1. Master Asigna Tarea

```python
from app.distributed.slave_manager import SlaveManager

manager = SlaveManager()

# Buscar slave disponible
slave_id = manager.find_available_slave(task_type="niche_analysis")

# Ejecutar tarea
result = manager.execute_remote_task(
    slave_id=slave_id,
    task={
        "type": "niche_analysis",
        "data": {"niche": "AI productivity tools"}
    }
)
```

### 2. SlaveManager Prepara Request

```python
def execute_remote_task(self, slave_id, task):
    slave = self.slaves[slave_id]
    
    # Verificar versión
    if slave.get('version_mismatch'):
        logger.error("❌ Slave tiene versión incorrecta")
        return None
    
    # Construir comando Python
    command = self._build_python_command(task)
    
    # Enviar HTTP request
    url = f"http://{slave['host']}:{slave['port']}/api/execute"
    
    response = self.connection.post(
        url,
        json={"command": command},
        headers={"Authorization": f"Bearer {SLAVE_TOKEN}"},
        timeout=300
    )
    
    return response.json()
```

### 3. RobustConnection Envía con Retry

```python
# Intento 1
try:
    response = requests.post(url, json=data, timeout=30)
    return response  # ✅ Éxito
except:
    time.sleep(2)  # Backoff 2s
    
# Intento 2
try:
    response = requests.post(url, json=data, timeout=30)
    return response  # ✅ Éxito
except:
    time.sleep(4)  # Backoff 4s
    
# Intento 3
try:
    response = requests.post(url, json=data, timeout=30)
    return response  # ✅ Éxito o ❌ Falla definitiva
except:
    return None
```

### 4. Slave Recibe y Ejecuta

```python
@app.route("/api/execute", methods=["POST"])
def execute():
    # Validar token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not _validate_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    # Obtener comando
    command = request.json.get("command")
    
    # Detectar métodos disponibles
    methods = _get_available_methods()
    
    # Ejecutar con prioridad: Docker > venv > Python
    if methods["docker"]:
        result = _execute_in_docker(command)
    elif methods["venv"]:
        result = _execute_in_venv(command)
    else:
        result = _execute_in_python(command)
    
    return jsonify(result)
```

### 5. Ejecución en venv

```python
def _execute_in_venv(command: str, working_dir: str = None):
    venv_python = Path(__file__).parent.parent.parent / "venv" / "Scripts" / "python.exe"
    
    result = subprocess.run(
        [str(venv_python), "-c", command],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=working_dir
    )
    
    return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr,
        "method": "venv"
    }
```

### 6. Master Recibe Resultado

```python
if result and result['success']:
    logger.info(f"✅ Tarea completada en {slave_id}")
    logger.info(f"Output: {result['output']}")
    return result['output']
else:
    logger.error(f"❌ Tarea falló en {slave_id}")
    logger.error(f"Error: {result['error']}")
    return None
```

---

## 🔍 Monitoreo y Health Checks

### Health Check Loop (Automático)

```python
class SlaveManager:
    def _start_health_monitoring(self):
        def health_loop():
            while True:
                for slave_id in self.slaves:
                    self.check_health(slave_id)
                time.sleep(30)  # Cada 30 segundos
        
        thread = threading.Thread(target=health_loop, daemon=True)
        thread.start()
```

### Estados del Slave

| Estado | Descripción | Acción Master |
|--------|-------------|---------------|
| `alive` | Respondió correctamente, versión OK | ✅ Asignar tareas |
| `version_mismatch` | Respondió pero versión incorrecta | ⚠️ Notificar, no asignar |
| `dead` | No respondió tras 3 intentos | ❌ Marcar como muerto, no asignar |
| `unknown` | Nunca se ha verificado | ❓ Verificar antes de usar |

### Detección de Desincronización

```python
def check_health(self, slave_id: str):
    response = self.connection.get(f"http://{host}:{port}/api/health")
    
    if response:
        slave_commit = response.json()['commit']
        master_commit = self.master_version
        
        if slave_commit != master_commit:
            logger.warning(f"⚠️ DESINCRONIZACIÓN en {slave_id}:")
            logger.warning(f"   Master: {master_commit[:8]}")
            logger.warning(f"   Slave:  {slave_commit[:8]}")
            
            slave['status'] = 'version_mismatch'
            
            # TODO: Enviar notificación por Telegram a Leo
```

---

## 🧪 Ejemplo Práctico

### Configurar y Usar un Slave

**1. Iniciar slave server en PC remoto:**

```bash
# En PC Leo (192.168.1.100)
cd ~/d8
python app/distributed/slave_server.py

# Output:
# 🚀 Starting Slave Server on 0.0.0.0:7600
# 🔖 Version: {'commit': '66a81d3', ...}
# 🔧 Available methods: {'venv': True, ...}
```

**2. Registrar desde master (Raspberry Pi):**

```python
# En Raspberry Pi
from app.distributed.slave_manager import SlaveManager

manager = SlaveManager()
manager.register_slave(
    slave_id="pc-leo",
    host="192.168.1.100",
    port=7600
)

# Output:
# ✅ Slave registrado: pc-leo (192.168.1.100:7600)
# 🔍 Verificando salud...
# ✅ Estado: alive
```

**3. Ejecutar tarea:**

```python
result = manager.execute_remote_task(
    slave_id="pc-leo",
    task={
        "type": "python_code",
        "command": """
import sys
print(f"Ejecutando en: {sys.platform}")
print(f"Python: {sys.version[:20]}")

def factorial(n):
    return 1 if n <= 1 else n * factorial(n-1)

print(f"Factorial de 10: {factorial(10)}")
"""
    }
)

print(result)
```

**Output:**
```json
{
  "success": true,
  "output": "Ejecutando en: win32\nPython: 3.10.11 (main, Apr\nFactorial de 10: 3628800\n",
  "error": "",
  "method": "venv"
}
```

---

## 🔧 Troubleshooting

### Error: "Connection refused"

**Problema:** Slave server no está corriendo o puerto bloqueado.

**Diagnóstico:**
```bash
# En el slave, verificar que server esté corriendo
netstat -an | findstr :7600

# Debería mostrar:
# TCP    0.0.0.0:7600           0.0.0.0:0              LISTENING
```

**Solución:**
```bash
python app/distributed/slave_server.py
```

### Error: "Unauthorized"

**Problema:** Token no coincide entre master y slave.

**Solución:**
```bash
# Asegúrate que ambos tengan el mismo SLAVE_TOKEN en .env
# O elimina el token para usar el default
```

### Error: "Version mismatch"

**Problema:** Slave tiene código desactualizado.

**Solución:**
```bash
# En el slave
git pull origin docker-workers
# Reiniciar server
python app/distributed/slave_server.py
```

### Error: "Timeout"

**Problema:** Tarea tomó más de 5 minutos.

**Solución:**
```python
# Aumentar timeout en master
result = manager.execute_remote_task(
    slave_id="pc-leo",
    task=task,
    timeout=600  # 10 minutos
)
```

---

## 📈 Métricas de Performance

### Latencia Típica (LAN)

| Operación | Tiempo |
|-----------|--------|
| Health check | ~5-10ms |
| Execute (simple) | ~50-100ms |
| Execute (complejo) | ~1-30s |
| Version check | ~5-10ms |

### Latencia Típica (Internet/VPS)

| Operación | Tiempo |
|-----------|--------|
| Health check | ~50-200ms |
| Execute (simple) | ~100-500ms |
| Execute (complejo) | ~1-30s + latencia |

### Throughput

- **LAN:** ~100-500 tareas/segundo (limitado por CPU)
- **Internet:** ~10-50 tareas/segundo (limitado por latencia)

---

## 🚀 Optimizaciones Futuras

### 1. Compresión

Comprimir payloads grandes con gzip:
```python
import gzip
compressed_command = gzip.compress(command.encode())
```

### 2. Keep-Alive Connections

Reutilizar conexiones HTTP:
```python
session = requests.Session()
session.get(url)  # Mantiene conexión abierta
```

### 3. WebSockets

Para tareas de larga duración:
```python
# Slave envía actualizaciones en tiempo real
ws.send(json.dumps({"progress": 50, "status": "processing"}))
```

### 4. Batching

Enviar múltiples tareas en un solo request:
```python
{
  "tasks": [
    {"type": "niche1", "data": {...}},
    {"type": "niche2", "data": {...}},
  ]
}
```

---

## 📚 Referencias

- **SlaveServer:** `app/distributed/slave_server.py` (245 líneas)
- **SlaveManager:** `app/distributed/slave_manager.py` (357 líneas)
- **RobustConnection:** `app/distributed/robust_connection.py` (140 líneas)
- **Tests:** `scripts/tests/test_fase4_complete.py` (400 líneas)
- **Guía de setup:** `docs/02_setup/AGREGAR_SLAVES_GUIA_RAPIDA.md`

---

**Tags:** `#comunicacion` `#master-slave` `#http-api` `#distributed` `#fase4`

**Última actualización:** 2025-11-20
