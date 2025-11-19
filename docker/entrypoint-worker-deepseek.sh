#!/bin/bash
# ============================================
# D8 Worker Entrypoint - DeepSeek with Ollama
# ============================================
set -e

echo "================================================"
echo "🧠 D8 DeepSeek Worker Starting..."
echo "================================================"
echo "Orchestrator URL: ${ORCHESTRATOR_URL}"
echo "Ollama Host: ${OLLAMA_HOST}"
echo "DeepSeek Model: ${DEEPSEEK_MODEL:-deepseek-coder:6.7b}"
echo "Platform: $(uname -m)"
echo "================================================"

# Validate required environment variables
if [ -z "$ORCHESTRATOR_URL" ]; then
    echo "❌ ERROR: ORCHESTRATOR_URL not set"
    exit 1
fi

# Generate unique worker ID if not provided
if [ -z "$WORKER_ID" ]; then
    export WORKER_ID="deepseek-$(hostname)-$(date +%s)"
    echo "📝 Generated Worker ID: ${WORKER_ID}"
fi

# Start Ollama in background
echo "🚀 Starting Ollama server..."
ollama serve > /app/data/logs/ollama.log 2>&1 &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to start..."
max_retries=30
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is ready"
        break
    fi
    retry_count=$((retry_count + 1))
    echo "   Attempt $retry_count/$max_retries..."
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ ERROR: Ollama failed to start"
    kill $OLLAMA_PID 2>/dev/null || true
    exit 1
fi

# Pull DeepSeek model if not exists
DEEPSEEK_MODEL=${DEEPSEEK_MODEL:-deepseek-coder:6.7b}
echo "📦 Checking for model: ${DEEPSEEK_MODEL}..."
if ! ollama list | grep -q "${DEEPSEEK_MODEL}"; then
    echo "⬇️  Pulling ${DEEPSEEK_MODEL} (this may take a while on first run)..."
    ollama pull "${DEEPSEEK_MODEL}"
    echo "✅ Model downloaded successfully"
else
    echo "✅ Model already available"
fi

# Wait for orchestrator to be ready
echo "⏳ Waiting for orchestrator at ${ORCHESTRATOR_URL}..."
max_retries=30
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    if curl -sf "${ORCHESTRATOR_URL}/health" > /dev/null 2>&1; then
        echo "✅ Orchestrator is ready"
        break
    fi
    retry_count=$((retry_count + 1))
    echo "   Attempt $retry_count/$max_retries..."
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ ERROR: Orchestrator not reachable"
    kill $OLLAMA_PID 2>/dev/null || true
    exit 1
fi

# Start DeepSeek worker
echo "🚀 Starting DeepSeek worker..."
export WORKER_TYPE=deepseek
export DEEPSEEK_BASE_URL=http://localhost:11434

# Trap signals to gracefully shutdown
trap "echo '🛑 Shutting down...'; kill $OLLAMA_PID 2>/dev/null; exit 0" SIGTERM SIGINT

# Start worker (keeps running in foreground)
python -m app.distributed.worker_fixed &
WORKER_PID=$!

# Wait for both processes
wait $WORKER_PID
