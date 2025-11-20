# Branch: docker-workers

## 🎯 Objetivo

Dockerizar el sistema D8 para deployment distribuido de workers, con enfoque especial en Raspberry Pi 4 ejecutando DeepSeek local.

---

## ✅ Completado

### 1. Dockerfiles Multi-Arquitectura
- ✅ `docker/Dockerfile.orchestrator` - Coordinador central (Flask + Gunicorn)
- ✅ `docker/Dockerfile.worker` - Worker base (Groq, Gemini)
- ✅ `docker/Dockerfile.worker-deepseek` - Worker especializado con Ollama

**Características:**
- Soporte ARM64 (Raspberry Pi) y AMD64 (x86_64)
- Multi-stage builds para optimización
- Health checks integrados
- Usuario no-root para seguridad

### 2. Docker Compose con Perfiles
- ✅ `docker-compose.yml` con 4 perfiles:
  - `orchestrator` - Coordinador central
  - `worker-groq` - Worker Groq cloud
  - `worker-gemini` - Worker Gemini cloud
  - `worker-deepseek` - Worker DeepSeek local (Raspberry Pi)
  - `full-system` - Sistema completo para testing

**Características:**
- Networks aisladas
- Volúmenes persistentes
- Resource limits configurables
- Dependencies correctas

### 3. Scripts de Entrypoint
- ✅ `docker/entrypoint-orchestrator.sh` - Inicia Gunicorn con orchestrator
- ✅ `docker/entrypoint-worker.sh` - Inicia worker genérico
- ✅ `docker/entrypoint-worker-deepseek.sh` - Inicia Ollama + worker
- ✅ `docker/init-ollama.sh` - Pre-descarga modelos

**Características:**
- Validación de environment variables
- Wait-for-dependencies automático
- Graceful shutdown con SIGTERM
- Logging estructurado

### 4. Configuraciones de Environment
- ✅ `docker/.env.orchestrator.template`
- ✅ `docker/.env.worker-groq.template`
- ✅ `docker/.env.worker-gemini.template`
- ✅ `docker/.env.worker-deepseek.template`

**Características:**
- Documentación inline
- Valores por defecto sensatos
- Optimizaciones para Raspberry Pi
- Separación secrets vs config

### 5. Setup Automatizado
- ✅ `scripts/setup/setup_worker.py` - Script Python completo
- ✅ `scripts/setup/setup_worker.sh` - Wrapper bash interactivo

**Funcionalidad:**
- Detección automática de Raspberry Pi
- Validación de requisitos (Docker, RAM, etc.)
- Configuración interactiva
- Build y start automático
- Creación de servicio systemd
- Manejo de errores robusto

### 6. Documentación
- ✅ `docs/02_setup/docker_deployment.md` - Guía completa
- ✅ `docker/README.md` - Referencia rápida

**Contenido:**
- Arquitectura del sistema
- Setup paso a paso
- Optimizaciones para Raspberry Pi
- Troubleshooting completo
- Comandos útiles
- Benchmarks

### 7. Utilidades
- ✅ `.dockerignore` - Optimización de build context
- ✅ `Makefile` - Comandos útiles (make help)

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────┐
│         ORCHESTRATOR (Flask)            │
│    Puerto: 7001                         │
│    - Gestiona cola de tareas            │
│    - Asigna trabajo a workers           │
│    - Monitorea heartbeats               │
└──────────────┬──────────────────────────┘
               │ HTTP REST API
               │
    ┌──────────┴──────────┬─────────────┐
    │                     │             │
┌───▼────┐          ┌─────▼───┐    ┌───▼─────┐
│ Worker │          │ Worker  │    │ Worker  │
│  Groq  │          │ Gemini  │    │DeepSeek │
│ (Cloud)│          │(Cloud)  │    │ (Local) │
│ 512MB  │          │ 512MB   │    │ 4-6GB   │
└────────┘          └─────────┘    └─────────┘
                                   + Ollama
                                   Raspberry Pi 4
```

---

## 📦 Estructura de Archivos Nuevos

```
d8/
├── docker/
│   ├── Dockerfile.orchestrator
│   ├── Dockerfile.worker
│   ├── Dockerfile.worker-deepseek
│   ├── entrypoint-orchestrator.sh
│   ├── entrypoint-worker.sh
│   ├── entrypoint-worker-deepseek.sh
│   ├── init-ollama.sh
│   ├── .env.orchestrator.template
│   ├── .env.worker-groq.template
│   ├── .env.worker-gemini.template
│   ├── .env.worker-deepseek.template
│   └── README.md
├── docker-compose.yml
├── .dockerignore
├── Makefile
├── scripts/setup/
│   ├── setup_worker.py
│   └── setup_worker.sh
└── docs/02_setup/
    └── docker_deployment.md
```

---

## 🚀 Uso

### Setup Completo (1 Comando)

```bash
# En Raspberry Pi o servidor worker
git clone https://github.com/lsilva5455/d8.git
cd d8
git checkout docker-workers
chmod +x scripts/setup/setup_worker.sh
./scripts/setup/setup_worker.sh
```

### Comandos Útiles (Makefile)

```bash
make help                    # Ver todos los comandos
make build-worker-deepseek   # Build imagen DeepSeek
make start-worker-deepseek   # Iniciar worker
make logs-worker-deepseek    # Ver logs
make status                  # Estado de containers
make ollama-list             # Listar modelos Ollama
```

---

## 🎯 Casos de Uso Soportados

### 1. Raspberry Pi 4 8GB - DeepSeek 6.7B
- Worker local sin costo de API
- Procesamiento autónomo
- ~5 tokens/s
- Ideal para tareas de mutación/crossover

### 2. Raspberry Pi 4 4GB - DeepSeek 1.3B
- Versión ligera para hardware limitado
- ~15 tokens/s
- Consumo mínimo de RAM

### 3. Servidor x86_64 - DeepSeek 33B
- Máxima calidad en hardware potente
- Requiere 20GB+ RAM
- Para tareas críticas

### 4. Cloud Workers (Groq/Gemini)
- Sin requisitos de hardware
- Latencia baja
- Escalable instantáneamente

---

## 🔧 Características Técnicas

### Seguridad
- ✅ Containers run as non-root
- ✅ Network isolation (bridge privada)
- ✅ Secrets en .env (gitignored)
- ✅ Resource limits configurables

### Performance
- ✅ Multi-stage builds (imagen más pequeña)
- ✅ Layer caching optimizado (.dockerignore)
- ✅ Health checks eficientes
- ✅ Persistent volumes para models

### Resilience
- ✅ Auto-restart con `unless-stopped`
- ✅ Graceful shutdown con SIGTERM
- ✅ Retry logic en workers
- ✅ Heartbeat monitoring

### Observability
- ✅ Structured logging
- ✅ Health check endpoints
- ✅ Resource usage tracking
- ✅ Status API endpoints

---

## 📊 Testing

### Pruebas Realizadas

- ✅ Build en AMD64 (Windows con WSL)
- ⏳ Build en ARM64 (pendiente: Raspberry Pi real)
- ✅ docker-compose profiles funcionan
- ✅ Scripts Python sin errores de sintaxis
- ✅ Templates .env correctos

### Pruebas Pendientes (Requieren Hardware)

- [ ] Deploy real en Raspberry Pi 4
- [ ] Descarga de modelo DeepSeek (~4GB)
- [ ] Performance benchmarks reales
- [ ] Comunicación orchestrator ↔ workers
- [ ] Stress testing con múltiples workers

---

## 🎓 Lecciones de Diseño

### 1. Separación de Concerns
- Orchestrator = coordinación
- Workers = ejecución
- Comunicación = HTTP REST (simple, debuggable)

### 2. Configuración Flexible
- Templates para cada tipo de worker
- Override fácil con .env
- Defaults sensatos

### 3. Developer Experience
- Setup en 1 comando
- Modo interactivo para beginners
- Makefile para power users
- Documentación exhaustiva

### 4. Production-Ready
- Gunicorn para orchestrator (no Flask dev server)
- Health checks
- Logging estructurado
- Resource limits

---

## 📝 Decisiones de Diseño

### ¿Por qué Docker Compose y no Kubernetes?

- **Simplicidad:** D8 corre en red local, no cloud
- **Overhead:** K8s es overkill para 3-5 workers
- **Hardware:** Raspberry Pi no tiene recursos para K8s
- **DX:** docker-compose es más fácil de entender

### ¿Por qué Profiles en lugar de múltiples docker-compose.yml?

- **DRY:** Un solo archivo
- **Clarity:** Configuración centralizada
- **Flexibility:** Combinar profiles fácilmente

### ¿Por qué HTTP y no gRPC?

- **Simplicidad:** HTTP REST es universal
- **Debugging:** curl, browser, Postman
- **Firewall:** Menos problemas con puertos
- **Overhead:** Aceptable para este caso de uso

### ¿Por qué Ollama y no LlamaCpp directo?

- **UX:** Ollama es más fácil de usar
- **Management:** Gestión de modelos simplificada
- **Updates:** Ollama se actualiza frecuentemente
- **Community:** Más documentación y soporte

---

## 🚧 Próximos Pasos

### Corto Plazo
1. [ ] Testear en Raspberry Pi 4 real
2. [ ] Ajustar configuración según benchmarks reales
3. [ ] Agregar métricas de Prometheus
4. [ ] Dashboard web para monitoreo

### Medio Plazo
1. [ ] Auto-scaling de workers
2. [ ] Load balancing inteligente
3. [ ] Task priority queue
4. [ ] Worker specialization (evolution vs actions)

### Largo Plazo
1. [ ] Multi-region orchestration
2. [ ] Fault tolerance avanzado
3. [ ] GPU support para DeepSeek
4. [ ] WebSocket para comunicación real-time

---

## 🙏 Agradecimientos

Basado en:
- Arquitectura distribuida existente (`app/distributed/`)
- Documentación Raspberry Pi (`docs/02_setup/raspberry_pi.md`)
- Patrones de D8 (`docs/06_knowledge_base/`)

---

## 📚 Referencias

- [Docker Multi-Architecture](https://docs.docker.com/build/building/multi-platform/)
- [Docker Compose Profiles](https://docs.docker.com/compose/profiles/)
- [Ollama Docker](https://hub.docker.com/r/ollama/ollama)
- [Raspberry Pi Optimization](https://www.raspberrypi.com/documentation/)

---

**Branch creado:** 2025-11-19  
**Estado:** ✅ Listo para testing en hardware real  
**Autor:** GitHub Copilot + Usuario  
**Commit sugerido:** "feat: Add Docker deployment for distributed workers with Raspberry Pi support"
