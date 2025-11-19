# 🐳 D8 Docker Deployment Guide

**Sistema distribuido de workers con Docker y comunicación HTTP**

---

## 📋 Índice

1. [Arquitectura](#arquitectura)
2. [Tipos de Worker](#tipos-de-worker)
3. [Setup Rápido](#setup-rápido)
4. [Configuración Detallada](#configuración-detallada)
5. [Raspberry Pi 4 + DeepSeek](#raspberry-pi-4--deepseek)
6. [Troubleshooting](#troubleshooting)

---

## Arquitectura

```
┌─────────────────────────────────────────┐
│         ORCHESTRATOR                    │
│    (Coordinador Central)                │
│    - Gestiona cola de tareas            │
│    - Asigna trabajo a workers           │
│    - Monitorea heartbeats               │
│    Puerto: 7001                         │
└──────────────┬──────────────────────────┘
               │ HTTP
               │
    ┌──────────┴──────────┬─────────────┐
    │                     │             │
┌───▼────┐          ┌─────▼───┐    ┌───▼─────┐
│ Worker │          │ Worker  │    │ Worker  │
│  Groq  │          │ Gemini  │    │DeepSeek │
│ (Cloud)│          │(Cloud)  │    │ (Local) │
└────────┘          └─────────┘    └─────────┘
                                   Raspberry Pi 4
```

**Comunicación:**
- Workers se registran con Orchestrator vía HTTP
- Polling periódico para obtener tareas
- Heartbeat cada 30s para indicar que están vivos
- Resultados enviados de vuelta al Orchestrator

---

## Tipos de Worker

### 1. 🚀 Worker Groq (Cloud)
- **Ventajas:** Rápido, modelos potentes (70B)
- **Requisitos:** API key, conexión a internet
- **Costo:** ~$0.27 por millón de tokens
- **Hardware:** Mínimo (512MB RAM)

### 2. 🧠 Worker Gemini (Cloud)
- **Ventajas:** Tier gratuito generoso, buena calidad
- **Requisitos:** API key, conexión a internet
- **Costo:** Gratis hasta 1500 req/día
- **Hardware:** Mínimo (512MB RAM)

### 3. 🍓 Worker DeepSeek (Local)
- **Ventajas:** Cero costo de API, privacidad total
- **Requisitos:** Hardware decente (Raspberry Pi 4 8GB+)
- **Costo:** Solo electricidad (~$2/mes)
- **Hardware:** 4-8GB RAM, 4+ cores

---

## Setup Rápido

### Opción 1: Script Automático (Recomendado)

```bash
# En la máquina worker (Raspberry Pi o servidor)

# 1. Clonar repositorio
git clone https://github.com/lsilva5455/d8.git
cd d8
git checkout docker-workers

# 2. Hacer ejecutable el script
chmod +x scripts/setup/setup_worker.sh

# 3. Ejecutar setup interactivo
./scripts/setup/setup_worker.sh
```

**El script preguntará:**
- Tipo de worker (deepseek/groq/gemini)
- URL del orchestrator
- API key (si aplica)

### Opción 2: Setup Manual

```bash
# 1. Copiar template de configuración
cp docker/.env.worker-deepseek.template .env.worker

# 2. Editar configuración
nano .env.worker
# Cambiar ORCHESTRATOR_URL a IP real

# 3. Iniciar worker
docker compose --profile worker-deepseek up -d
```

---

## Configuración Detallada

### 1️⃣ Setup del Orchestrator

El orchestrator debe correr en la máquina principal o en un servidor dedicado.

```bash
# En la máquina orchestrator
cd d8
git checkout docker-workers

# Configurar
cp docker/.env.orchestrator.template .env

# Editar si es necesario
nano .env

# Iniciar orchestrator
docker compose --profile orchestrator up -d

# Verificar
curl http://localhost:7001/health
```

**Abrir puerto en firewall:**
```bash
sudo ufw allow 7001/tcp
```

**Obtener IP del orchestrator:**
```bash
ip addr show | grep "inet "
# O en Raspberry Pi:
hostname -I
```

### 2️⃣ Setup de Workers

#### Worker DeepSeek (Raspberry Pi 4)

```bash
# En la Raspberry Pi
git clone https://github.com/lsilva5455/d8.git
cd d8
git checkout docker-workers

# Configurar
cp docker/.env.worker-deepseek.template .env.worker
nano .env.worker

# Cambiar:
# ORCHESTRATOR_URL=http://192.168.1.100:7001  <- IP del orchestrator
# DEEPSEEK_MODEL=deepseek-coder:6.7b  (o :1.3b para Pi con 4GB)

# Iniciar worker
docker compose --profile worker-deepseek up -d

# Ver logs (primera vez descarga modelo ~4GB)
docker logs -f d8-worker-deepseek
```

**⚠️ Primera ejecución:** Descarga del modelo tarda 10-30 min dependiendo de conexión.

#### Worker Groq

```bash
# Obtener API key: https://console.groq.com/keys

# Configurar
cp docker/.env.worker-groq.template .env.worker
nano .env.worker

# Cambiar:
# ORCHESTRATOR_URL=http://192.168.1.100:7001
# GROQ_API_KEY=gsk_your_actual_key_here

# Iniciar
docker compose --profile worker-groq up -d

# Verificar
docker logs d8-worker-groq
```

#### Worker Gemini

```bash
# Obtener API key: https://aistudio.google.com/app/apikey

# Configurar
cp docker/.env.worker-gemini.template .env.worker
nano .env.worker

# Cambiar:
# ORCHESTRATOR_URL=http://192.168.1.100:7001
# GEMINI_API_KEY=AIza_your_actual_key_here

# Iniciar
docker compose --profile worker-gemini up -d

# Verificar
docker logs d8-worker-gemini
```

---

## Raspberry Pi 4 + DeepSeek

### Hardware Recomendado

| Componente | Recomendado | Mínimo |
|------------|-------------|---------|
| RAM | 8GB | 4GB |
| Modelo DeepSeek | 6.7B | 1.3B |
| Storage | 32GB+ | 16GB |
| Fuente | 5V 3A oficial | 5V 2.5A |

### Optimizaciones para Raspberry Pi

**1. Usar SD Card rápida (UHS-I Clase 10 o mejor)**

**2. Limitar recursos de Docker:**

En `.env.worker`:
```bash
# Para Pi con 8GB
OLLAMA_MAX_VRAM=4096
DEEPSEEK_MODEL=deepseek-coder:6.7b

# Para Pi con 4GB
OLLAMA_MAX_VRAM=2048
DEEPSEEK_MODEL=deepseek-coder:1.3b
```

**3. Configurar swap:**

```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Cambiar: CONF_SWAPSIZE=4096
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

**4. Refrigeración:**
- Disipador + ventilador recomendado
- Monitorear temperatura: `vcgencmd measure_temp`

### Monitoreo de Recursos

```bash
# CPU y RAM
htop

# Temperatura
watch -n 2 vcgencmd measure_temp

# GPU memory
vcgencmd get_mem gpu

# Logs de Ollama
docker exec -it d8-worker-deepseek tail -f /app/data/logs/ollama.log
```

---

## Comandos Útiles

### Gestión de Containers

```bash
# Ver estado de todos los servicios
docker compose ps

# Ver logs
docker logs -f d8-worker-deepseek
docker logs -f d8-orchestrator

# Reiniciar worker
docker compose --profile worker-deepseek restart

# Detener worker
docker compose --profile worker-deepseek down

# Actualizar imagen
docker compose --profile worker-deepseek pull
docker compose --profile worker-deepseek up -d
```

### Gestión de Modelos Ollama

```bash
# Listar modelos instalados
docker exec d8-worker-deepseek ollama list

# Descargar modelo manualmente
docker exec d8-worker-deepseek ollama pull deepseek-coder:1.3b

# Probar modelo
docker exec -it d8-worker-deepseek ollama run deepseek-coder:6.7b "print hello world in python"

# Eliminar modelo
docker exec d8-worker-deepseek ollama rm deepseek-coder:33b
```

### Verificar Conectividad

```bash
# Desde worker, verificar orchestrator
curl http://192.168.1.100:7001/health

# Ver workers registrados (desde orchestrator)
curl http://localhost:7001/api/workers/list

# Ver tareas pendientes
curl http://localhost:7001/api/tasks/queue
```

---

## Troubleshooting

### ❌ Worker no se conecta al orchestrator

**Síntoma:** Logs muestran "Cannot reach orchestrator"

**Soluciones:**
1. Verificar IP del orchestrator: `ping 192.168.1.100`
2. Verificar puerto abierto: `nc -zv 192.168.1.100 7001`
3. Verificar firewall: `sudo ufw allow 7001/tcp`
4. Verificar que orchestrator esté corriendo: `docker ps`

### ❌ Ollama falla al descargar modelo

**Síntoma:** "Failed to pull deepseek-coder"

**Soluciones:**
1. Verificar espacio en disco: `df -h`
2. Descargar manualmente: `docker exec -it d8-worker-deepseek ollama pull deepseek-coder:1.3b`
3. Usar modelo más pequeño en `.env.worker`

### ❌ Raspberry Pi se congela o reinicia

**Síntoma:** Sistema inestable, logs se cortan

**Soluciones:**
1. Verificar temperatura: `vcgencmd measure_temp` (debe ser <80°C)
2. Verificar fuente de poder (usar oficial 5V 3A)
3. Reducir RAM del modelo en `.env.worker`: `OLLAMA_MAX_VRAM=2048`
4. Usar modelo 1.3B en lugar de 6.7B
5. Agregar swap: ver [Optimizaciones](#optimizaciones-para-raspberry-pi)

### ❌ Worker muestra como "dead" en orchestrator

**Síntoma:** Worker aparece offline en dashboard

**Soluciones:**
1. Verificar logs del worker: `docker logs d8-worker-deepseek`
2. Verificar heartbeat: buscar "heartbeat" en logs
3. Reiniciar worker: `docker compose --profile worker-deepseek restart`
4. Verificar reloj del sistema (NTP): `timedatectl status`

### ❌ Error "Model not found"

**Síntoma:** Worker no puede usar modelo

**Soluciones:**
```bash
# Ver modelos disponibles
docker exec d8-worker-deepseek ollama list

# Si está vacío, descargar
docker exec d8-worker-deepseek ollama pull deepseek-coder:6.7b

# Verificar nombre exacto en .env.worker
grep DEEPSEEK_MODEL .env.worker
```

### ❌ Docker Compose no encuentra perfil

**Síntoma:** "no services to start"

**Solución:**
```bash
# Asegurarse de usar --profile
docker compose --profile worker-deepseek up -d

# NO solo:
docker compose up -d  # ❌ No funciona
```

---

## Auto-inicio con Systemd

Para que el worker inicie automáticamente al bootear:

```bash
# El script de setup puede crear el servicio
./scripts/setup/setup_worker.sh

# O manualmente:
sudo nano /etc/systemd/system/d8-worker.service
```

Contenido:
```ini
[Unit]
Description=D8 Worker DeepSeek
Requires=docker.service
After=docker.service network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/pi/d8
ExecStart=/usr/bin/docker compose --profile worker-deepseek up -d
ExecStop=/usr/bin/docker compose --profile worker-deepseek down
User=pi

[Install]
WantedBy=multi-user.target
```

Activar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable d8-worker
sudo systemctl start d8-worker

# Verificar
sudo systemctl status d8-worker
```

---

## Seguridad

### Recomendaciones

1. **No exponer Orchestrator a internet:** Solo en red local
2. **Usar HTTPS en producción:** Agregar nginx con SSL
3. **Rotar API keys regularmente**
4. **Limitar recursos de Docker:** Ver `deploy.resources` en docker-compose.yml
5. **Monitorear logs:** Buscar actividad sospechosa

### Firewall

```bash
# Permitir solo red local al orchestrator
sudo ufw allow from 192.168.1.0/24 to any port 7001

# Bloquear acceso externo
sudo ufw deny 7001/tcp
```

---

## Performance

### Benchmarks (Raspberry Pi 4 8GB)

| Modelo | Tokens/s | RAM Uso | Primera Carga |
|--------|----------|---------|---------------|
| deepseek-coder:1.3b | ~15 | 2GB | 30s |
| deepseek-coder:6.7b | ~5 | 4.5GB | 60s |
| deepseek-coder:33b | ~1 | ❌ No cabe | N/A |

### Optimización de Latencia

Para reducir tiempo de primera respuesta:

```bash
# Pre-cargar modelo en memoria
docker exec d8-worker-deepseek ollama run deepseek-coder:6.7b "test"

# O configurar en .env.worker:
OLLAMA_KEEP_ALIVE=-1  # Mantener en memoria indefinidamente
```

---

## Próximos Pasos

1. ✅ **Setup básico completo**
2. 🔄 **Monitorear workers:** Ver dashboard (próximamente)
3. 🧪 **Probar con tareas reales:** Enviar requests al orchestrator
4. 📊 **Agregar más workers:** Escalar horizontalmente
5. 🔧 **Optimizar configuración:** Ajustar según workload

---

## Referencias

- [Docker Compose Profiles](https://docs.docker.com/compose/profiles/)
- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/README.md)
- [Raspberry Pi Optimization](https://www.raspberrypi.com/documentation/computers/config_txt.html)
- [DeepSeek Models](https://ollama.com/library/deepseek-coder)

---

**Última actualización:** 2025-11-19  
**Branch:** `docker-workers`  
**Estado:** ✅ Listo para producción
