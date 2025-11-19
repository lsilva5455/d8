"""
Simple Flask orchestrator for testing distributed workers
WITHOUT D8-GENESIS (no heavy ML dependencies)
"""

from flask import Flask, jsonify
from app.distributed.orchestrator import orchestrator_bp, orchestrator
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Register distributed orchestrator blueprint
app.register_blueprint(orchestrator_bp)


@app.route('/')
def index():
    """API health check"""
    return jsonify({
        "status": "online",
        "project": "The Hive - Distributed Test",
        "version": "0.1.0-test",
        "endpoints": {
            "/": "This health check",
            "/api/workers/register": "Register worker",
            "/api/workers/stats": "Worker statistics",
            "/api/workers/<id>/tasks": "Poll for tasks",
            "/api/test/task": "Submit test task (POST)"
        }
    })


@app.route('/api/test/task', methods=['POST'])
def submit_test_task():
    """Submit a test task to the orchestrator"""
    from flask import request
    
    data = request.json or {}
    prompt = data.get('prompt', 'Hello! Respond in Spanish.')
    
    # Submit task to orchestrator
    task_id = orchestrator.submit_task(
        task_type="agent_action",
        task_data={
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "model": "gemini-2.0-flash-exp",
            "temperature": 0.8
        },
        priority=5
    )
    
    return jsonify({
        "success": True,
        "task_id": task_id,
        "message": "Task submitted! Worker will process it soon.",
        "check_stats": "/api/workers/stats"
    })


if __name__ == "__main__":
    logger.info("🚀 Starting test orchestrator...")
    app.run(host='0.0.0.0', port=5000, debug=True)
