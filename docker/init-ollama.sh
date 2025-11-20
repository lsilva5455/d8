#!/bin/bash
# ============================================
# Initialize Ollama with DeepSeek models
# ============================================
set -e

echo "📦 Initializing Ollama models..."

# Models to pre-download
MODELS=(
    "deepseek-coder:6.7b"
    "deepseek-coder:1.3b"
)

for model in "${MODELS[@]}"; do
    echo "⬇️  Pulling ${model}..."
    ollama pull "${model}" || echo "⚠️  Failed to pull ${model}, will retry on demand"
done

echo "✅ Ollama initialization complete"
