#!/bin/bash
# ============================================
# D8 Orchestrator Entrypoint Script
# ============================================
set -e

echo "================================================"
echo "🎯 D8 Orchestrator Starting..."
echo "================================================"
echo "Flask Host: ${FLASK_HOST:-0.0.0.0}"
echo "Flask Port: ${FLASK_PORT:-5000}"
echo "Workers: ${GUNICORN_WORKERS:-2}"
echo "Platform: $(uname -m)"
echo "================================================"

# Create necessary directories
mkdir -p /app/data/logs /app/data/tasks /app/data/results /app/data/metrics

# Wait a moment for filesystem to be ready
sleep 2

echo "🚀 Starting orchestrator with Gunicorn..."

# Start Flask app with Gunicorn (production-ready)
exec gunicorn \
    --bind ${FLASK_HOST:-0.0.0.0}:${FLASK_PORT:-5000} \
    --workers ${GUNICORN_WORKERS:-2} \
    --threads ${GUNICORN_THREADS:-4} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --access-logfile /app/data/logs/access.log \
    --error-logfile /app/data/logs/error.log \
    --log-level ${LOG_LEVEL:-info} \
    --preload \
    "app.main:create_orchestrator_app()"
