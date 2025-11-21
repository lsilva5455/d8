# 🌐 Guía Rápida: Agregar Slaves a la Red D8

**Objetivo:** Conectar una máquina remota como slave para ejecutar tareas distribuidas.

---

## 📡 Comunicación Master-Slave

### Protocolo: HTTP REST API

**Puerto:** 7600 (configurable)  
**Autenticación:** Bearer token  
**Formato:** JSON

### Endpoints del Slave

```
GET  /api/health    - Health check + capacidades
GET  /api/version   - Versión del código (commit)
POST /api/execute   - Ejecutar tarea
```

### Flujo de Comunicación

```
MASTER (Raspberry Pi / PC Principal)
    │
    │ HTTP POST /api/execute
    │ Authorization: Bearer token
    │ {"command": "...", "working_dir": "..."}
    ▼
SLAVE (PC remoto / VPS / Laptop)
    │
    │ Ejecuta en: Docker > venv > Python
    │
    │ {"success": true, "output": "...", "method": "docker"}
    ▼
MASTER
    │
    └─ Recibe resultado
```

---

## 🚀 Setup del Slave (Máquina Remota)

### Paso 1: Clonar D8

```bash
cd ~
git clone https://github.com/lsilva5455/d8.git
cd d8
git checkout docker-workers
```

### Paso 2: Instalar Dependencias

```bash
# Crear venv
python -m venv venv

# Activar
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar
pip install -r requirements.txt
```

### Paso 3: Configurar Token (Opcional)

Crear `.env` en el directorio raíz:
```env
SLAVE_TOKEN=tu-token-secreto-aqui
SLAVE_PORT=7600
SLAVE_HOST=0.0.0.0
```

**IMPORTANTE:** Usa el mismo `SLAVE_TOKEN` en master y slave.

### Paso 4: Iniciar Slave Server

```bash
python app/distributed/slave_server.py
```

**Output esperado:**
```
🚀 Starting Slave Server on 0.0.0.0:7600
🔖 Version: {'commit': 'abc1234', 'version': '1.0.0', 'branch': 'docker-workers'}
🔧 Available methods: {'docker': False, 'venv': True, 'python': True}
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:7600
 * Running on http://192.168.1.100:7600
```

**Nota la IP local:** En este ejemplo es `192.168.1.100`

---

## 🔌 Registrar Slave en el Master

### Opción 1: Script Interactivo (Recomendado)

En la máquina **MASTER** (Raspberry Pi / PC principal):

```bash
python scripts/add_slave.py
```

**Flujo interactivo:**
```
🌐 AGREGAR SLAVE A LA RED D8
============================================================

📝 DATOS DEL NUEVO SLAVE:

ID del slave (ej: pc-leo, vps-us, raspi-backup): pc-leo
Host/IP del slave (ej: 192.168.1.100): 192.168.1.100
Puerto [7600]: 

🔍 VERIFICANDO CONECTIVIDAD...
✅ Slave respondió correctamente!

📊 INFORMACIÓN DEL SLAVE:
   Estado: healthy
   Python: 3.10.11 (main, Apr  5 2023...)
   Commit: abc1234
   Branch: docker-workers

   Métodos disponibles:
      ❌ docker
      ✅ venv
      ✅ python

💾 REGISTRANDO SLAVE...
✅ SLAVE REGISTRADO EXITOSAMENTE!
```

### Opción 2: Con Argumentos

```bash
python scripts/add_slave.py pc-leo 192.168.1.100 7600
```

### Opción 3: Manualmente en Python

```python
from app.distributed.slave_manager import SlaveManager

manager = SlaveManager()
manager.register_slave(
    slave_id="pc-leo",
    host="192.168.1.100",
    port=7600,
    install_method="venv"
)
```

---

## ✅ Verificar Slaves

### Ver Estado de Todos los Slaves

```bash
python scripts/check_slaves.py
```

**Output:**
```
🌐 ESTADO DE SLAVES EN LA RED D8
======================================================================

📊 MASTER VERSION: abc1234

📋 SLAVES REGISTRADOS: 2

----------------------------------------------------------------------
🖥️  SLAVE: pc-leo
----------------------------------------------------------------------
   Host: 192.168.1.100:7600
   Método: venv
   
   🔍 Verificando salud...
   ✅ Estado: ALIVE
   ✅ Commit: abc1234
   📦 Capacidades:
      ❌ docker
      ✅ venv
      ✅ python

----------------------------------------------------------------------
🖥️  SLAVE: vps-us
----------------------------------------------------------------------
   Host: vps.midominio.com:7600
   Método: docker
   
   🔍 Verificando salud...
   ✅ Estado: ALIVE
   ✅ Commit: abc1234
   📦 Capacidades:
      ✅ docker
      ✅ venv
      ✅ python

======================================================================
📊 RESUMEN
======================================================================

   Total slaves: 2
   ✅ Vivos: 2
   ❌ Muertos: 0
   ⚠️  Version mismatch: 0

🎉 ¡Todos los slaves están operacionales!
```

---

## 🧪 Probar Ejecución Remota

### Test Manual

```python
from app.distributed.slave_manager import SlaveManager

manager = SlaveManager()

# Ejecutar tarea simple
result = manager.execute_remote_task(
    slave_id="pc-leo",
    task_type="python_code",
    command="print('Hola desde slave!'); import sys; print(sys.version)"
)

print(f"Success: {result['success']}")
print(f"Output: {result['output']}")
print(f"Method: {result['method']}")
```

### Test Completo

```bash
python scripts/tests/test_fase4_complete.py
```

---

## 🔧 Troubleshooting

### ❌ "No se pudo conectar"

**Causas comunes:**

1. **Slave server no está corriendo**
   ```bash
   # En la máquina slave
   python app/distributed/slave_server.py
   ```

2. **Firewall bloqueando el puerto**
   ```bash
   # Windows (abrir puerto 7600)
   netsh advfirewall firewall add rule name="D8 Slave" dir=in action=allow protocol=TCP localport=7600
   
   # Linux
   sudo ufw allow 7600/tcp
   ```

3. **IP incorrecta**
   ```bash
   # Ver IP del slave
   # Windows:
   ipconfig
   # Linux:
   ip addr show
   ```

4. **Redes diferentes sin port forwarding**
   - Si master y slave están en redes diferentes, necesitas configurar port forwarding en el router del slave
   - O usar VPN/túnel SSH

### ⚠️ "Version mismatch"

**Causa:** El slave tiene código desactualizado.

**Solución:**
```bash
# En la máquina slave
cd ~/d8
git pull origin docker-workers
# Reiniciar slave server
python app/distributed/slave_server.py
```

### ❌ "Unauthorized"

**Causa:** Token de autenticación no coincide.

**Solución:**
```bash
# Asegúrate que master y slave tengan el mismo SLAVE_TOKEN en .env
# O usa el token por defecto: "default-dev-token-change-in-production"
```

---

## 📊 Arquitectura de Red

### Red Local (LAN)

```
┌─────────────────────────────────────────┐
│  Router WiFi (192.168.1.1)              │
│                                         │
│  ┌──────────────┐   ┌──────────────┐   │
│  │ MASTER       │   │ SLAVE 1      │   │
│  │ 192.168.1.10 │   │ 192.168.1.100│   │
│  │ (Raspi)      │───│ (PC Leo)     │   │
│  └──────────────┘   └──────────────┘   │
│                                         │
│         ┌──────────────┐                │
│         │ SLAVE 2      │                │
│         │ 192.168.1.150│                │
│         │ (Laptop)     │                │
│         └──────────────┘                │
└─────────────────────────────────────────┘
```

### Red Remota (VPS)

```
MASTER (Raspi - Home)         SLAVE (VPS - Cloud)
192.168.1.10                  vps.midominio.com
                              (IP pública: 45.123.45.67)
    │
    │ HTTP Request
    │ Host: vps.midominio.com:7600
    ▼
    🌐 Internet
    │
    ▼
    🖥️ VPS ejecuta tarea
```

---

## 🔐 Seguridad

### 1. Token de Autenticación

```env
# .env en master y slaves
SLAVE_TOKEN=generar-token-largo-y-aleatorio-aqui
```

Generar token seguro:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Solo Red Local (Recomendado para Desarrollo)

- Configurar `SLAVE_HOST=127.0.0.1` para solo localhost
- O `SLAVE_HOST=192.168.1.100` para solo LAN

### 3. VPS Público (Producción)

- Usar HTTPS con Nginx reverse proxy
- Configurar fail2ban
- Rate limiting
- VPN entre master y slaves

---

## 📈 Métricas y Monitoreo

### Ver Slaves en Tiempo Real

```python
from app.distributed.slave_manager import SlaveManager
import time

manager = SlaveManager()

while True:
    status = manager.get_all_status()
    
    print("\n🌐 SLAVES STATUS:")
    for slave in status:
        icon = "✅" if slave['status'] == 'alive' else "❌"
        print(f"{icon} {slave['name']}: {slave['status']}")
    
    time.sleep(30)  # Update cada 30s
```

---

## 🎯 Casos de Uso

### 1. PC Potente como Slave

Tu PC principal ejecuta tareas pesadas mientras el Raspberry Pi coordina.

```python
# Master (Raspi) detecta tarea pesada
if task.requires_gpu or task.memory_intensive:
    # Enviar a PC con más recursos
    result = manager.execute_remote_task("pc-leo", task)
```

### 2. VPS para Disponibilidad 24/7

VPS remoto siempre disponible para tareas programadas.

```python
# Tarea que debe correr incluso si estás offline
result = manager.execute_remote_task("vps-us", scheduled_task)
```

### 3. Laptop como Backup

Laptop se une cuando está disponible, se desconecta cuando te lo llevas.

```python
# Manager detecta automáticamente
slaves_disponibles = manager.get_alive_slaves()
# Usa laptop si está disponible
```

---

## 🚀 Siguiente Nivel

### Auto-scaling con Docker

Ver `docs/01_arquitectura/FASE_4_PLAN_COMPLETO.md` para:
- Docker Swarm deployment
- Kubernetes orchestration
- Auto-scaling basado en carga

### Dashboard Web

Ver roadmap en `docs/01_arquitectura/FASE_4_README.md` para:
- Interfaz web para gestión de slaves
- Métricas en tiempo real
- Logs centralizados

---

**¿Listo para agregar tu primer slave?**

```bash
# 1. En el slave
python app/distributed/slave_server.py

# 2. En el master
python scripts/add_slave.py

# 3. Verificar
python scripts/check_slaves.py
```

🎉 ¡Ya tienes un sistema distribuido funcionando!
