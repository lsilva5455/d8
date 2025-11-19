#!/bin/bash
# ============================================
# D8 Worker Entrypoint Script
# ============================================
set -e

echo "================================================"
echo "🤖 D8 Worker Node Starting..."
echo "================================================"
echo "Worker Type: ${WORKER_TYPE}"
echo "Orchestrator URL: ${ORCHESTRATOR_URL}"
echo "Platform: $(uname -m)"
echo "================================================"

# Validate required environment variables
if [ -z "$ORCHESTRATOR_URL" ]; then
    echo "❌ ERROR: ORCHESTRATOR_URL not set"
    exit 1
fi

if [ -z "$API_KEY" ] && [ "$WORKER_TYPE" != "deepseek" ]; then
    echo "❌ ERROR: API_KEY not set for worker type ${WORKER_TYPE}"
    exit 1
fi

# Generate unique worker ID if not provided
if [ -z "$WORKER_ID" ]; then
    export WORKER_ID="${WORKER_TYPE}-$(hostname)-$(date +%s)"
    echo "📝 Generated Worker ID: ${WORKER_ID}"
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
    echo "❌ ERROR: Orchestrator not reachable after $max_retries attempts"
    exit 1
fi

# Start worker based on type
echo "🚀 Starting ${WORKER_TYPE} worker..."

case "$WORKER_TYPE" in
    groq)
        python -m app.distributed.worker_groq
        ;;
    gemini)
        python -m app.distributed.worker_gemini_resilient
        ;;
    deepseek)
        echo "⚠️  Use Dockerfile.worker-deepseek for DeepSeek workers"
        exit 1
        ;;
    *)
        python -m app.distributed.worker_fixed
        ;;
esac
