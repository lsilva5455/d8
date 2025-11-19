# 🚀 Quick Start - Docker Workers

## ✅ Estado del Branch

**Branch:** `docker-workers`  
**Commit:** ee01f28  
**Estado:** ✅ Listo para testing en hardware real  
**Validación:** 100% (42/42 checks passed)

---

## 📦 Lo que se ha creado

### Dockerfiles (Multi-arquitectura: ARM64 + AMD64)
- `docker/Dockerfile.orchestrator` - Coordinador central
- `docker/Dockerfile.worker` - Workers cloud (Groq, Gemini)
- `docker/Dockerfile.worker-deepseek` - Worker local con Ollama

### Configuración
- `docker-compose.yml` - Orchestration con 4 perfiles
- Templates de configuración para cada tipo de worker
- Scripts de entrypoint con lógica de startup

### Automatización
- `scripts/setup/setup_worker.py` - Setup completo en Python
- `scripts/setup/setup_worker.sh` - Wrapper interactivo en Bash
- `Makefile` - Comandos útiles (`make help`)

### Documentación
- `docs/02_setup/docker_deployment.md` - Guía completa (320+ líneas)
- `docker/README.md` - Referencia rápida
- `BRANCH_SUMMARY.md` - Resumen del branch

---

## 🎯 Caso de Uso Principal: Raspberry Pi 4 + DeepSeek

### Hardware Recomendado
- **Raspberry Pi 4 8GB** con DeepSeek 6.7B (óptimo)
- Raspberry Pi 4 4GB con DeepSeek 1.3B (funcional)

### Setup en 3 Pasos

#### 1. En la máquina con el Orchestrator (servidor principal)

```bash
# Clonar repo
git clone https://github.com/lsilva5455/d8.git
cd d8
git checkout docker-workers

# Iniciar orchestrator
make init-env-orchestrator
nano .env  # Editar si necesario
make start-orchestrator

# Verificar
make check-health
# Debe retornar: {"status": "healthy"}
```

**IP del orchestrator:** La que muestre `ip addr show` o `hostname -I`

#### 2. En la Raspberry Pi (worker)

```bash
# Clonar repo
git clone https://github.com/lsilva5455/d8.git
cd d8
git checkout docker-workers

# Setup automático (modo interactivo)
chmod +x scripts/setup/setup_worker.sh
./scripts/setup/setup_worker.sh
```

**El script preguntará:**
1. Tipo de worker → Seleccionar `1` (DeepSeek)
2. URL del orchestrator → Ingresar `http://192.168.1.X:5000` (IP del paso 1)

**⚠️ Primera ejecución:** Descarga del modelo DeepSeek (~4GB) tarda 10-30 min.

#### 3. Verificar que todo funciona

```bash
# En orchestrator
make check-workers
# Debe mostrar el worker registrado

# Ver logs del worker
make logs-worker-deepseek
```

---

## 🔧 Comandos Útiles (Makefile)

```bash
# Ver todos los comandos disponibles
make help

# Gestión de containers
make status              # Estado de containers
make logs-orchestrator   # Logs del orchestrator
make logs-worker-deepseek  # Logs del worker
make restart-worker-deepseek  # Reiniciar worker

# Ollama (DeepSeek)
make ollama-list         # Ver modelos instalados
make ollama-pull-1.3b    # Descargar modelo ligero
make ollama-pull-6.7b    # Descargar modelo recomendado
make ollama-test         # Probar modelo

# Mantenimiento
make clean               # Limpiar containers detenidos
make update              # Actualizar imágenes
```

---

## 🌐 Workers Adicionales

### Worker Groq (Cloud, rápido)

```bash
# En cualquier máquina
cd d8
git checkout docker-workers

# Setup
cp docker/.env.worker-groq.template .env.worker
nano .env.worker
# Cambiar:
# - ORCHESTRATOR_URL
# - GROQ_API_KEY

# Iniciar
make start-worker-groq
```

### Worker Gemini (Cloud, gratis)

```bash
# Setup similar a Groq
cp docker/.env.worker-gemini.template .env.worker
nano .env.worker
# Cambiar:
# - ORCHESTRATOR_URL
# - GEMINI_API_KEY

make start-worker-gemini
```

---

## 🐛 Troubleshooting Rápido

### Worker no se conecta al orchestrator

```bash
# Verificar orchestrator está corriendo
curl http://192.168.1.X:5000/health

# Verificar conectividad desde worker
ping 192.168.1.X
nc -zv 192.168.1.X 5000

# Ver logs del worker
docker logs d8-worker-deepseek
```

### Raspberry Pi se congela

```bash
# Verificar temperatura
vcgencmd measure_temp
# Si > 80°C, mejorar refrigeración

# Usar modelo más ligero
nano .env.worker
# Cambiar: DEEPSEEK_MODEL=deepseek-coder:1.3b
docker compose --profile worker-deepseek restart
```

### Modelo no se descarga

```bash
# Verificar espacio en disco
df -h

# Descargar manualmente
docker exec d8-worker-deepseek ollama pull deepseek-coder:6.7b

# Ver progreso
docker logs -f d8-worker-deepseek
```

---

## 📊 Arquitectura del Sistema

```
┌─────────────────────────────────────────┐
│    ORCHESTRATOR (Puerto 5000)           │
│    - Gestiona cola de tareas            │
│    - Distribuye trabajo                 │
│    - Monitorea workers (heartbeat)      │
└────────────┬────────────────────────────┘
             │ HTTP REST API
             │
    ┌────────┴─────────┬──────────────┐
    │                  │              │
┌───▼────┐       ┌─────▼────┐   ┌────▼─────┐
│ Groq   │       │ Gemini   │   │ DeepSeek │
│ Worker │       │ Worker   │   │ Worker   │
│ (Cloud)│       │ (Cloud)  │   │ (Local)  │
└────────┘       └──────────┘   └──────────┘
                                 Raspberry Pi 4
                                 + Ollama
```

**Ventajas:**
- ✅ Escalabilidad horizontal (agregar más workers)
- ✅ Zero-cost con DeepSeek local
- ✅ Fallback a cloud si local falla
- ✅ HTTP simple = fácil debugging

---

## 🎓 Conceptos Clave

### Perfiles de Docker Compose

El sistema usa **profiles** para iniciar solo lo necesario:

```bash
# Solo orchestrator
docker compose --profile orchestrator up -d

# Solo worker DeepSeek
docker compose --profile worker-deepseek up -d

# Todo junto (testing)
docker compose --profile full-system up -d
```

### Comunicación Worker ↔ Orchestrator

1. Worker se registra: `POST /api/workers/register`
2. Worker hace polling: `GET /api/workers/{id}/poll` (cada 5-10s)
3. Orchestrator asigna tarea si hay disponible
4. Worker procesa y reporta: `POST /api/tasks/{id}/result`
5. Worker envía heartbeat: `POST /api/workers/{id}/heartbeat` (cada 30s)

### Ollama + DeepSeek

Ollama es un servidor que expone modelos LLM vía API REST:

```bash
# Listar modelos
curl http://localhost:11434/api/tags

# Generar texto
curl http://localhost:11434/api/generate -d '{
  "model": "deepseek-coder:6.7b",
  "prompt": "print hello world in python"
}'
```

El worker D8 usa esta API internamente.

---

## 📚 Documentación Completa

Para más detalles, ver:

- **Guía completa:** `docs/02_setup/docker_deployment.md`
- **Docker README:** `docker/README.md`
- **Resumen del branch:** `BRANCH_SUMMARY.md`
- **Comandos Make:** `make help`

---

## 🚧 Siguientes Pasos

### Inmediatos (Testing)
1. [ ] Testear en Raspberry Pi 4 real
2. [ ] Benchmark de performance (tokens/s)
3. [ ] Validar comunicación orchestrator ↔ workers
4. [ ] Ajustar configuración según resultados

### Mejoras Futuras
1. [ ] Dashboard web para monitoreo
2. [ ] Métricas con Prometheus
3. [ ] Auto-scaling de workers
4. [ ] GPU support para DeepSeek

---

## 🤝 Contribuir

Si encuentras bugs o tienes mejoras:

1. Crear issue en GitHub
2. Fork del repo
3. Crear branch desde `docker-workers`
4. Pull request con descripción detallada

---

## 📞 Soporte

- **Documentación:** Ver `docs/02_setup/docker_deployment.md`
- **Validación:** `python scripts/tests/validate_docker_setup.py`
- **Logs:** `make logs-all`
- **Status:** `make status`

---

**Última actualización:** 2025-11-19  
**Branch:** `docker-workers`  
**Estado:** ✅ Listo para deployment  
**Próximo paso:** Testing en hardware real
