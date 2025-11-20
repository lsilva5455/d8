# 🔌 D8 - Asignación de Puertos

**Rango asignado para D8:** `7001 - 8000`

---

## 📊 Puertos Actuales

| Puerto | Servicio | Descripción | Protocolo |
|--------|----------|-------------|-----------|
| **7001** | Orchestrator | Servidor central de coordinación (Flask API) | HTTP |
| **7100** | Ollama/DeepSeek | Servidor local de LLM (DeepSeek) | HTTP |
| **7200** | Worker Status | Endpoint de salud de workers | HTTP |

---

## 🎯 Endpoints Principales

### Orchestrator (Puerto 7001)

```bash
# Health check
curl http://localhost:7001/health

# Registrar worker
POST http://localhost:7001/api/workers/register

# Listar workers
GET http://localhost:7001/api/workers/list

# Enviar tarea
POST http://localhost:7001/api/tasks/submit

# Obtener tarea (worker polling)
GET http://localhost:7001/api/workers/{worker_id}/tasks

# Reportar resultado
POST http://localhost:7001/api/tasks/{task_id}/result

# Consultar estado de tarea
GET http://localhost:7001/api/tasks/status/{task_id}

# Estadísticas del sistema
GET http://localhost:7001/api/stats
```

### Ollama/DeepSeek (Puerto 7100)

```bash
# Listar modelos instalados
curl http://localhost:7100/api/tags

# Generar texto
POST http://localhost:7100/api/generate

# Chat completion
POST http://localhost:7100/api/chat
```

### Worker Status (Puerto 7200)

```bash
# Health check del worker
curl http://localhost:7200/health
```

---

## 🔧 Configuración

### Variables de Entorno

```bash
# .env
FLASK_PORT=7001
DEEPSEEK_BASE_URL=http://localhost:7100
ORCHESTRATOR_URL=http://localhost:7001
OLLAMA_HOST=0.0.0.0:7100
WORKER_STATUS_PORT=7200
```

### Docker Compose

```yaml
orchestrator:
  ports:
    - "7001:7001"

worker-deepseek:
  ports:
    - "7100:7100"
```

---

## 📈 Puertos Futuros (Disponibles)

Puertos disponibles en el rango para futuros servicios:

| Rango | Propósito Sugerido |
|-------|-------------------|
| 7201-7210 | Workers adicionales (status endpoints) |
| 7300-7399 | APIs de agentes especializados |
| 7400-7499 | Servicios de monitoreo y métricas |
| 7500-7599 | Servicios de base de datos (ChromaDB, Redis, etc.) |
| 7600-7699 | Webhooks y callbacks |
| 7700-7799 | Servicios experimentales |
| 7800-7899 | Servicios de desarrollo/testing |
| 7900-8000 | Reserva para expansión |

---

## 🚀 Ejemplos de Uso

### Modo Local (Single Machine)

```bash
# Terminal 1: Orchestrator
python start_d8.py  # Opción 4
# Escucha en: http://localhost:7001

# Terminal 2: Worker DeepSeek
python start_d8.py  # Opción 7
# Ollama en: http://localhost:7100

# Terminal 3: Cliente (Niche Discovery)
python start_d8.py  # Opción 2
# Conecta a: http://localhost:7001
```

### Modo Distribuido (Múltiples Máquinas)

**Máquina 1 (Orchestrator - IP: 192.168.1.100):**
```bash
python start_d8.py  # Opción 4
# Escucha en: http://0.0.0.0:7001
```

**Máquina 2 (Raspberry Pi Worker):**
```bash
# Configurar ORCHESTRATOR_URL
export ORCHESTRATOR_URL=http://192.168.1.100:7001

python start_d8.py  # Opción 7
# Ollama local: http://localhost:7100
# Conecta a orchestrator: http://192.168.1.100:7001
```

**Máquina 3 (Cliente):**
```bash
export ORCHESTRATOR_URL=http://192.168.1.100:7001
python start_d8.py  # Opción 2
```

---

## 🔒 Firewall

### Permitir puertos en firewall (Linux)

```bash
# Orchestrator
sudo ufw allow 7001/tcp

# Ollama (si se expone en red)
sudo ufw allow 7100/tcp

# Solo desde red local (recomendado)
sudo ufw allow from 192.168.1.0/24 to any port 7001
sudo ufw allow from 192.168.1.0/24 to any port 7100
```

### Windows Firewall

```powershell
# Orchestrator
New-NetFirewallRule -DisplayName "D8 Orchestrator" -Direction Inbound -LocalPort 7001 -Protocol TCP -Action Allow

# Ollama
New-NetFirewallRule -DisplayName "D8 Ollama" -Direction Inbound -LocalPort 7100 -Protocol TCP -Action Allow
```

---

## 🐛 Troubleshooting

### Puerto ya en uso

```bash
# Verificar qué está usando el puerto
netstat -ano | findstr :7001  # Windows
lsof -i :7001                  # Linux/Mac

# Cambiar puerto temporalmente
export FLASK_PORT=7002
python start_d8.py
```

### No se puede conectar al orchestrator

```bash
# 1. Verificar que orchestrator está corriendo
curl http://localhost:7001/health

# 2. Verificar firewall
telnet 192.168.1.100 7001

# 3. Verificar logs
docker logs d8-orchestrator  # Si usa Docker
# O revisar logs en data/logs/
```

### Ollama no responde

```bash
# Verificar servicio
curl http://localhost:7100/api/tags

# Reiniciar Ollama
ollama serve --host 0.0.0.0:7100

# Verificar modelo instalado
ollama list
```

---

## 📝 Notas

- **Puertos reservados:** 7001, 7100, 7200 (no cambiar)
- **Próximo puerto disponible:** 7201
- **Rango total:** 7001-8000 (1000 puertos disponibles)
- **Protocolo:** Todos los servicios usan HTTP por ahora
- **Seguridad:** Recomendado usar firewall para limitar acceso a red local

---

## 🔄 Historial de Cambios

### 2025-11-19
- **Cambio:** Migración de puertos anteriores al rango 7001-8000
  - Orchestrator: 5000 → 7001
  - Ollama: 11434 → 7100
  - Worker Status: 8080 → 7200
- **Razón:** Evitar conflictos con servicios comunes (Flask default, Ollama default)
- **Impacto:** 21 archivos actualizados

---

**Última actualización:** 2025-11-19  
**Versión:** 1.0.0
