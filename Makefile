# D8 Docker - Makefile
# ====================
# Comandos útiles para gestionar el sistema distribuido

.PHONY: help build-all build-orchestrator build-worker-groq build-worker-gemini build-worker-deepseek
.PHONY: start-orchestrator start-worker-groq start-worker-gemini start-worker-deepseek stop-all
.PHONY: logs-orchestrator logs-worker status clean

# Variables
COMPOSE = docker compose
ORCHESTRATOR_PROFILE = orchestrator
WORKER_GROQ_PROFILE = worker-groq
WORKER_GEMINI_PROFILE = worker-gemini
WORKER_DEEPSEEK_PROFILE = worker-deepseek

help: ## Mostrar esta ayuda
	@echo "D8 Docker - Comandos Disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ====================
# BUILD
# ====================

build-all: ## Construir todas las imágenes
	@echo "🏗️  Construyendo todas las imágenes..."
	docker build -f docker/Dockerfile.orchestrator -t d8-orchestrator .
	docker build -f docker/Dockerfile.worker --build-arg WORKER_TYPE=groq -t d8-worker-groq .
	docker build -f docker/Dockerfile.worker --build-arg WORKER_TYPE=gemini -t d8-worker-gemini .
	docker build -f docker/Dockerfile.worker-deepseek -t d8-worker-deepseek .
	@echo "✅ Build completado"

build-orchestrator: ## Construir imagen del orchestrator
	@echo "🏗️  Construyendo orchestrator..."
	docker build -f docker/Dockerfile.orchestrator -t d8-orchestrator .

build-worker-groq: ## Construir imagen worker Groq
	@echo "🏗️  Construyendo worker Groq..."
	docker build -f docker/Dockerfile.worker --build-arg WORKER_TYPE=groq -t d8-worker-groq .

build-worker-gemini: ## Construir imagen worker Gemini
	@echo "🏗️  Construyendo worker Gemini..."
	docker build -f docker/Dockerfile.worker --build-arg WORKER_TYPE=gemini -t d8-worker-gemini .

build-worker-deepseek: ## Construir imagen worker DeepSeek
	@echo "🏗️  Construyendo worker DeepSeek..."
	docker build -f docker/Dockerfile.worker-deepseek -t d8-worker-deepseek .

# ====================
# START / STOP
# ====================

start-orchestrator: ## Iniciar orchestrator
	@echo "🚀 Iniciando orchestrator..."
	$(COMPOSE) --profile $(ORCHESTRATOR_PROFILE) up -d
	@echo "✅ Orchestrator corriendo en http://localhost:5000"

start-worker-groq: ## Iniciar worker Groq
	@echo "🚀 Iniciando worker Groq..."
	$(COMPOSE) --profile $(WORKER_GROQ_PROFILE) up -d

start-worker-gemini: ## Iniciar worker Gemini
	@echo "🚀 Iniciando worker Gemini..."
	$(COMPOSE) --profile $(WORKER_GEMINI_PROFILE) up -d

start-worker-deepseek: ## Iniciar worker DeepSeek
	@echo "🚀 Iniciando worker DeepSeek..."
	$(COMPOSE) --profile $(WORKER_DEEPSEEK_PROFILE) up -d

start-all: ## Iniciar sistema completo (orchestrator + todos los workers)
	@echo "🚀 Iniciando sistema completo..."
	$(COMPOSE) --profile full-system up -d

stop-all: ## Detener todos los containers
	@echo "🛑 Deteniendo todos los containers..."
	$(COMPOSE) --profile full-system down

restart-orchestrator: ## Reiniciar orchestrator
	$(COMPOSE) --profile $(ORCHESTRATOR_PROFILE) restart

restart-worker-groq: ## Reiniciar worker Groq
	$(COMPOSE) --profile $(WORKER_GROQ_PROFILE) restart

restart-worker-gemini: ## Reiniciar worker Gemini
	$(COMPOSE) --profile $(WORKER_GEMINI_PROFILE) restart

restart-worker-deepseek: ## Reiniciar worker DeepSeek
	$(COMPOSE) --profile $(WORKER_DEEPSEEK_PROFILE) restart

# ====================
# LOGS
# ====================

logs-orchestrator: ## Ver logs del orchestrator
	$(COMPOSE) logs -f d8-orchestrator

logs-worker-groq: ## Ver logs del worker Groq
	$(COMPOSE) logs -f d8-worker-groq

logs-worker-gemini: ## Ver logs del worker Gemini
	$(COMPOSE) logs -f d8-worker-gemini

logs-worker-deepseek: ## Ver logs del worker DeepSeek
	$(COMPOSE) logs -f d8-worker-deepseek

logs-all: ## Ver logs de todos los containers
	$(COMPOSE) logs -f

# ====================
# STATUS & MONITORING
# ====================

status: ## Mostrar estado de todos los containers
	@echo "📊 Estado del sistema:"
	@$(COMPOSE) ps
	@echo ""
	@echo "🔍 Verificando health:"
	@docker ps --filter "name=d8-" --format "table {{.Names}}\t{{.Status}}"

ps: status ## Alias para status

check-health: ## Verificar health checks
	@echo "🩺 Verificando health del orchestrator..."
	@curl -s http://localhost:5000/health | jq . || echo "❌ Orchestrator no responde"

check-workers: ## Verificar workers registrados
	@echo "🤖 Workers registrados:"
	@curl -s http://localhost:5000/api/workers/list | jq . || echo "❌ No se puede conectar al orchestrator"

stats: ## Mostrar uso de recursos
	docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# ====================
# MAINTENANCE
# ====================

clean: ## Limpiar containers y volúmenes
	@echo "🧹 Limpiando containers detenidos..."
	docker container prune -f
	@echo "🧹 Limpiando imágenes sin usar..."
	docker image prune -f

clean-all: ## Limpiar containers, imágenes y volúmenes (⚠️ DESTRUCTIVO)
	@echo "⚠️  Esto eliminará TODOS los datos en volúmenes Docker"
	@read -p "¿Estás seguro? (y/N): " confirm; \
	if [ "$$confirm" = "y" ]; then \
		$(COMPOSE) --profile full-system down -v; \
		docker system prune -af --volumes; \
		echo "✅ Limpieza completa"; \
	else \
		echo "❌ Cancelado"; \
	fi

update: ## Actualizar imágenes y recrear containers
	@echo "🔄 Actualizando imágenes..."
	$(COMPOSE) --profile full-system pull
	$(COMPOSE) --profile full-system up -d --force-recreate

# ====================
# TESTING
# ====================

test-connection: ## Probar conexión orchestrator -> worker
	@echo "🧪 Probando conectividad..."
	@docker exec d8-orchestrator curl -s http://localhost:5000/health || echo "❌ Orchestrator no responde"

shell-orchestrator: ## Abrir shell en orchestrator
	docker exec -it d8-orchestrator /bin/bash

shell-worker-deepseek: ## Abrir shell en worker DeepSeek
	docker exec -it d8-worker-deepseek /bin/bash

# ====================
# OLLAMA (DeepSeek)
# ====================

ollama-list: ## Listar modelos Ollama instalados
	docker exec d8-worker-deepseek ollama list

ollama-pull-1.3b: ## Descargar modelo DeepSeek 1.3B
	docker exec d8-worker-deepseek ollama pull deepseek-coder:1.3b

ollama-pull-6.7b: ## Descargar modelo DeepSeek 6.7B
	docker exec d8-worker-deepseek ollama pull deepseek-coder:6.7b

ollama-test: ## Probar modelo DeepSeek
	docker exec -it d8-worker-deepseek ollama run deepseek-coder:6.7b "print hello world in python"

# ====================
# SETUP
# ====================

setup-worker: ## Ejecutar setup interactivo de worker
	./scripts/setup/setup_worker.sh

init-env-orchestrator: ## Crear .env desde template (orchestrator)
	cp docker/.env.orchestrator.template .env
	@echo "✅ Archivo .env creado. Edítalo con: nano .env"

init-env-worker-groq: ## Crear .env.worker desde template (Groq)
	cp docker/.env.worker-groq.template .env.worker
	@echo "✅ Archivo .env.worker creado. Edítalo con: nano .env.worker"

init-env-worker-gemini: ## Crear .env.worker desde template (Gemini)
	cp docker/.env.worker-gemini.template .env.worker
	@echo "✅ Archivo .env.worker creado. Edítalo con: nano .env.worker"

init-env-worker-deepseek: ## Crear .env.worker desde template (DeepSeek)
	cp docker/.env.worker-deepseek.template .env.worker
	@echo "✅ Archivo .env.worker creado. Edítalo con: nano .env.worker"

# ====================
# INFO
# ====================

version: ## Mostrar versión de Docker y Docker Compose
	@echo "Docker version:"
	@docker --version
	@echo ""
	@echo "Docker Compose version:"
	@docker compose version

info: ## Mostrar información del sistema
	@echo "==================================="
	@echo "D8 Docker System Info"
	@echo "==================================="
	@echo "Platform: $(shell uname -s) $(shell uname -m)"
	@echo "Docker: $(shell docker --version)"
	@echo "Compose: $(shell docker compose version)"
	@echo ""
	@echo "Running containers:"
	@docker ps --filter "name=d8-" --format "  - {{.Names}} ({{.Status}})"
	@echo ""
	@echo "Images:"
	@docker images --filter "reference=d8-*" --format "  - {{.Repository}}:{{.Tag}} ({{.Size}})"
