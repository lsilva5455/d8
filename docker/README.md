# 🐳 Docker Configuration Files

Este directorio contiene toda la configuración Docker para el sistema distribuido D8.

---

## 📁 Estructura

```
docker/
├── Dockerfile.orchestrator          # Imagen del coordinador central
├── Dockerfile.worker                # Imagen base de workers (Groq, Gemini)
├── Dockerfile.worker-deepseek       # Imagen especializada con Ollama
├── entrypoint-orchestrator.sh       # Script de inicio del orchestrator
├── entrypoint-worker.sh             # Script de inicio de workers genéricos
├── entrypoint-worker-deepseek.sh    # Script de inicio con Ollama
├── init-ollama.sh                   # Pre-descarga de modelos
├── .env.orchestrator.template       # Template de config del orchestrator
├── .env.worker-groq.template        # Template para worker Groq
├── .env.worker-gemini.template      # Template para worker Gemini
└── .env.worker-deepseek.template    # Template para worker DeepSeek
```

---

## 🚀 Uso Rápido

### Setup Automático (Recomendado)

```bash
cd d8
./scripts/setup/setup_worker.sh
```

### Setup Manual

```bash
# 1. Copiar template
cp docker/.env.worker-deepseek.template .env.worker

# 2. Editar configuración
nano .env.worker

# 3. Iniciar con docker-compose
docker compose --profile worker-deepseek up -d
```

---

## 🏗️ Build Manual

### Orchestrator

```bash
docker build -f docker/Dockerfile.orchestrator -t d8-orchestrator .
```

### Worker Groq

```bash
docker build -f docker/Dockerfile.worker --build-arg WORKER_TYPE=groq -t d8-worker-groq .
```

### Worker DeepSeek (con Ollama)

```bash
docker build -f docker/Dockerfile.worker-deepseek -t d8-worker-deepseek .
```

---

## ⚙️ Configuración

### Variables de Entorno Comunes

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `ORCHESTRATOR_URL` | URL del coordinador | `http://192.168.1.100:5000` |
| `WORKER_TYPE` | Tipo de worker | `groq`, `gemini`, `deepseek` |
| `WORKER_ID` | ID único del worker | Auto-generado si se omite |
| `POLL_INTERVAL` | Segundos entre polling | `5` para cloud, `10` para local |
| `MAX_TOKENS` | Tokens máximos por request | `2000` |
| `TEMPERATURE` | Temperatura de generación | `0.7` - `0.9` |

### Configuraciones Específicas

#### Groq
```bash
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile
```

#### Gemini
```bash
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-2.0-flash-exp
```

#### DeepSeek
```bash
DEEPSEEK_MODEL=deepseek-coder:6.7b
OLLAMA_HOST=0.0.0.0:11434
DEEPSEEK_BASE_URL=http://localhost:11434
```

---

## 🔧 Multi-Arquitectura

Los Dockerfiles soportan tanto **amd64** (x86_64) como **arm64** (Raspberry Pi).

### Build Multi-Platform

```bash
# Setup buildx (una vez)
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap

# Build para múltiples plataformas
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f docker/Dockerfile.worker-deepseek \
  -t d8-worker-deepseek:latest \
  --push .
```

---

## 📊 Recursos

### Límites Recomendados

#### Orchestrator
- CPU: 1-2 cores
- RAM: 512MB - 1GB
- Disk: 5GB

#### Worker Groq/Gemini (Cloud)
- CPU: 0.5-1 core
- RAM: 256MB - 512MB
- Disk: 2GB

#### Worker DeepSeek (Raspberry Pi 4)
- CPU: 3-4 cores
- RAM: 4-6GB (según modelo)
- Disk: 20GB (modelos + cache)

---

## 🩺 Health Checks

Todos los containers tienen health checks configurados:

### Orchestrator
```bash
curl http://localhost:5000/health
```

### Workers
```bash
curl http://localhost:8080/health
```

### DeepSeek (Ollama + Worker)
```bash
# Ollama
curl http://localhost:11434/api/tags

# Worker
curl http://localhost:8080/health
```

---

## 🔒 Seguridad

### Best Practices

1. **No hardcodear secrets:** Usar `.env` files (gitignored)
2. **Run as non-root:** Los Dockerfiles crean usuarios dedicados
3. **Limitar recursos:** Ver `deploy.resources` en docker-compose.yml
4. **Network isolation:** Usar red bridge privada
5. **Read-only filesystem:** Agregar si es crítico

### Escaneo de Vulnerabilidades

```bash
# Escanear imagen
docker scan d8-worker-deepseek

# O con trivy
trivy image d8-worker-deepseek
```

---

## 📝 Logs

### Ubicación de Logs

- **Orchestrator:** `/app/data/logs/orchestrator.log`
- **Workers:** `/app/data/logs/worker-{type}.log`
- **Ollama:** `/app/data/logs/ollama.log`

### Ver Logs

```bash
# Logs en tiempo real
docker logs -f d8-worker-deepseek

# Últimas 100 líneas
docker logs --tail 100 d8-worker-deepseek

# Desde una fecha
docker logs --since 2025-11-19T10:00:00 d8-orchestrator
```

---

## 🐛 Debugging

### Entrar a un Container

```bash
docker exec -it d8-worker-deepseek /bin/bash
```

### Inspeccionar Red

```bash
# Ver IPs de containers
docker network inspect d8_d8-network

# Verificar conectividad entre containers
docker exec d8-worker-groq ping orchestrator
```

### Ver Recursos en Uso

```bash
docker stats d8-worker-deepseek
```

---

## 🔄 Updates

### Actualizar Workers

```bash
# Pull nuevas imágenes
docker compose pull

# Recrear containers
docker compose --profile worker-deepseek up -d --force-recreate

# O rebuild desde código
docker compose --profile worker-deepseek build
docker compose --profile worker-deepseek up -d
```

---

## 📚 Documentación Completa

Ver: [`docs/02_setup/docker_deployment.md`](../docs/02_setup/docker_deployment.md)

---

**Última actualización:** 2025-11-19
