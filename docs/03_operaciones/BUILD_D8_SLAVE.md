# Build D8 Slave - Sistema HTTP de Instalación Automática

## 📋 Resumen

Sistema inteligente para instalar D8 Slave en máquinas remotas via HTTP, con fallback automático y escalación al Congreso.

---

## 🎯 Arquitectura

```
Master (start_d8.py)
   │
   ├─ Opción 10: Genera script .sh/.bat básico
   │              (crea slave_server.py mínimo + configuración)
   │
   └─ Opción 11: Build & Registro Automático
                  └─> BuildD8Slave.build()
                       │
                       ├─ 1. Verifica conectividad (GET /api/health)
                       ├─ 2. Verifica Python/Git (POST /api/execute)
                       ├─ 3. Instala faltantes si necesario
                       ├─ 4. Clona repositorio con GIT_TOKEN
                       │
                       ├─ 5. Estrategia A: Docker
                       │    ├─ Instala Docker + docker-compose
                       │    ├─ docker-compose up -d
                       │    ├─ 3 reintentos si falla
                       │    └─ Si falla → Estrategia B
                       │
                       ├─ 6. Estrategia B: VEnv
                       │    ├─ python3 -m venv venv
                       │    ├─ pip install -r requirements.txt
                       │    ├─ nohup slave_server.py &
                       │    ├─ 3 reintentos si falla
                       │    └─ Si falla → Estrategia C
                       │
                       ├─ 7. Estrategia C: Nativo
                       │    ├─ pip3 install --user
                       │    ├─ nohup python3 slave_server.py &
                       │    ├─ 3 reintentos si falla
                       │    └─ Si falla → Congreso
                       │
                       └─ 8. Si TODO falla:
                            └─> escalate_to_congress()
                                 └─> HumanRequest (HIGH priority)
                                      └─> Telegram notification
```

---

## 🚀 Uso

### Paso 1: Preparar Slave

En la máquina slave (Raspberry Pi, servidor, etc.):

**Generar script desde master:**
```bash
# En el master:
python start_d8.py
# Seleccionar: 10 (Generar Scripts)
```

Esto genera `install_slave_YYYYMMDD_HHMMSS.sh` con el token y configuración del master embedded.

**Transferir script al slave:**
```bash
# Desde master a slave:
scp scripts/setup/install_slave_*.sh pi@192.168.4.25:~/

# O descarga directa si tienes web server:
# wget http://192.168.4.25/install_slave_xxx.sh
```

**Ejecutar en el slave:**
```bash
chmod +x install_slave_*.sh
./install_slave_*.sh
```

**¿Qué hace el script?**
1. ✅ Verifica/instala Python 3
2. ✅ Instala dependencias mínimas: `flask requests`
3. ✅ Crea `~/d8_slave/slave_server.py` (servidor HTTP básico)
4. ✅ Verifica puerto 7600 disponible
5. ✅ Muestra IP local del slave
6. ⏸️ **Queda esperando** que inicies el servidor

**Iniciar servidor HTTP básico:**
```bash
cd ~/d8_slave
python3 slave_server.py
```

Output:
```
============================================================
🤖 D8 Slave Server - HTTP API Activo
============================================================
Puerto: 7600
Endpoints:
  GET  /api/health  - Health check
  POST /api/execute - Ejecutar comando
============================================================

⏳ Esperando conexión desde master...
   Master: 192.168.4.25:7600
```

El slave queda escuchando en `http://0.0.0.0:7600` esperando comandos del master.

### Paso 2: Build Automático desde Master

En el master:

```bash
python start_d8.py
# Seleccionar: 11 (Build & Registro Automático)
# Ingresar IP del slave: 192.168.4.25
# Confirmar: s
```

El master ejecutará:
1. ✅ Conectividad
2. ✅ Verificar/instalar Python + Git
3. ✅ Clonar repo D8
4. ⚡ Intentar Docker → VEnv → Nativo
5. 📊 Log completo en `~/Documents/d8_data/build_logs/`
6. ✅ Si éxito: Auto-registra slave
7. ❌ Si falla: Escala al Congreso

---

## 📊 Logs

Todos los comandos ejecutados se guardan en:

```
~/Documents/d8_data/build_logs/
  └─ build_slave-192-168-4-25_2025-11-19_143022.json
```

Estructura del log:

```json
{
  "slave_id": "slave-192-168-4-25",
  "slave_host": "192.168.4.25",
  "status": "success",
  "strategy": "docker",
  "commands": [
    {
      "command": "python3 --version",
      "success": true,
      "stdout": "Python 3.11.2",
      "stderr": "",
      "exit_code": 0,
      "timestamp": "2025-11-19T14:30:25.123456"
    },
    ...
  ],
  "error": null,
  "timestamp": "2025-11-19T14:30:22.123456"
}
```

---

## 🔧 Estrategias de Instalación

### Estrategia A: Docker (Preferida)

**Ventajas:**
- ✅ Aislamiento completo
- ✅ Dependencias containerizadas
- ✅ Fácil actualización

**Requisitos:**
- Docker 20.10+
- docker-compose 1.29+
- Usuario con permisos docker

**Proceso:**
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker $USER

# docker-compose
pip3 install docker-compose

# Levantar
cd d8
docker-compose up -d
```

### Estrategia B: VEnv (Fallback)

**Ventajas:**
- ✅ Aislamiento de dependencias
- ✅ No requiere Docker
- ✅ Compatible con cualquier Linux

**Requisitos:**
- Python 3.11+
- python3-venv

**Proceso:**
```bash
cd d8
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nohup python slave_server.py > slave.log 2>&1 &
```

### Estrategia C: Nativo (Último recurso)

**Ventajas:**
- ✅ Funciona sin venv/docker
- ✅ Mínimos requisitos

**Desventajas:**
- ❌ Contamina Python global
- ❌ Conflictos de dependencias posibles

**Proceso:**
```bash
cd d8
pip3 install --user -r requirements.txt
nohup python3 slave_server.py > slave.log 2>&1 &
```

---

## 🏛️ Escalación al Congreso

Si las 3 estrategias fallan después de 3 reintentos cada una:

1. `BuildD8Slave.escalate_to_congress()` se ejecuta
2. Crea `HumanRequest` con prioridad HIGH:
   ```python
   {
     "title": "Fallo en instalación de slave: slave-192-168-4-25",
     "description": "...",
     "priority": "high",
     "category": "infrastructure",
     "log_file": "~/Documents/d8_data/build_logs/build_xxx.json"
   }
   ```
3. Congreso Autónomo procesa la request:
   - Analiza logs
   - Intenta soluciones alternativas
   - Si no puede resolver → Notifica a Leo via Telegram
4. Leo recibe mensaje:
   ```
   🚨 INFRAESTRUCTURA: Fallo instalación slave
   
   Slave: slave-192-168-4-25
   IP: 192.168.4.25
   Estrategias fallidas: Docker, VEnv, Nativo
   
   Log: ~/Documents/d8_data/build_logs/build_xxx.json
   
   Congreso no pudo resolver automáticamente.
   Requiere intervención manual.
   ```

---

## 🐛 Troubleshooting

### Error: "Connection refused"

**Causa:** `slave_server.py` no está corriendo o puerto bloqueado.

**Solución:**
```bash
# En el slave, verificar:
ps aux | grep slave_server

# Verificar puerto:
netstat -tulpn | grep 7600

# Verificar firewall:
sudo ufw status
```

### Error: "Authentication failed"

**Causa:** Token incorrecto.

**Solución:**
```bash
# Verificar token en slave_server.py:
grep TOKEN slave_server.py

# Verificar token en master:
grep SLAVE_AUTH_TOKEN .env
```

### Error: "Docker installation failed"

**Causa:** Permisos o red.

**Solución:**
```bash
# Verificar conexión:
curl -fsSL https://get.docker.com

# Verificar permisos:
sudo usermod -aG docker $USER
newgrp docker
```

### Error: "Git clone failed"

**Causa:** GIT_TOKEN inválido o expirado.

**Solución:**
```bash
# Generar nuevo token en GitHub:
# https://github.com/settings/tokens

# Actualizar .env:
GIT_TOKEN=ghp_nuevotokenXXXXXX
```

---

## 📝 Notas de Implementación

### Comunicación HTTP

Todos los comandos se envían via POST al endpoint `/api/execute`:

```python
response = requests.post(
    f"http://{slave_host}:{slave_port}/api/execute",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "command": "python3 --version",
        "working_dir": "/home/pi"
    },
    timeout=300
)

result = response.json()
# {
#   "success": true,
#   "stdout": "Python 3.11.2\n",
#   "stderr": "",
#   "exit_code": 0
# }
```

### Retry Logic

Cada estrategia se reintenta 3 veces con delay de 10 segundos:

```python
for attempt in range(3):
    result = try_strategy()
    if result["success"]:
        break
    time.sleep(10)
```

### Logging Completo

Cada comando ejecutado se registra:

```python
self.build_log.append({
    "command": command,
    "success": result["success"],
    "stdout": result["stdout"],
    "stderr": result["stderr"],
    "exit_code": result["exit_code"],
    "timestamp": datetime.now().isoformat()
})
```

---

## 🔐 Seguridad

- ✅ Autenticación Bearer token en todas las requests
- ✅ GIT_TOKEN nunca se expone en logs (sanitizado)
- ✅ Comandos ejecutados con usuario no-root
- ✅ Timeouts para prevenir comandos colgados
- ✅ Logs locales solo accesibles por usuario D8

---

**Última actualización:** 2025-11-19  
**Autor:** D8 System  
**Versión:** 1.0.0
