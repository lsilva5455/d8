"""
D8 Orchestrator Flask Application
===================================
Expone API REST para gestión de workers y tareas distribuidas.

Endpoints:
    POST   /api/workers/register          - Registrar worker
    POST   /api/workers/{id}/heartbeat    - Heartbeat de worker
    GET    /api/workers/{id}/tasks        - Obtener tarea para worker
    POST   /api/tasks/submit               - Crear nueva tarea
    POST   /api/tasks/{id}/result          - Reportar resultado
    GET    /api/tasks/status/{id}          - Consultar estado de tarea
    GET    /api/workers/list               - Listar workers
    GET    /health                         - Health check
"""

from flask import Flask, request, jsonify
from app.distributed.orchestrator import DistributedOrchestrator
import logging
from datetime import datetime
from typing import Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_orchestrator_app() -> Flask:
    """Factory para crear aplicación Flask del orchestrator"""
    
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    
    # Instancia global del orchestrator
    orchestrator = DistributedOrchestrator()
    
    # ==========================================
    # HEALTH CHECK
    # ==========================================
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "service": "d8-orchestrator",
            "timestamp": datetime.utcnow().isoformat(),
            "workers_online": len([w for w in orchestrator.workers.values() if w.status in ["online", "busy"]]),
            "tasks_pending": len([t for t in orchestrator.tasks.values() if t.status == "pending"]),
            "tasks_in_progress": len([t for t in orchestrator.tasks.values() if t.status == "assigned"])
        })
    
    # ==========================================
    # WORKER MANAGEMENT
    # ==========================================
    
    @app.route('/api/workers/register', methods=['POST'])
    def register_worker():
        """
        Registrar nuevo worker
        
        Request body:
        {
            "worker_id": "groq-worker-1",
            "worker_type": "groq",
            "capabilities": {
                "max_tokens": 2000,
                "models": ["llama-3.3-70b"]
            }
        }
        """
        try:
            data = request.json
            
            # Validar campos requeridos
            required = ['worker_id', 'worker_type', 'capabilities']
            for field in required:
                if field not in data:
                    return jsonify({"error": f"Missing field: {field}"}), 400
            
            # Registrar worker
            success = orchestrator.register_worker(
                worker_id=data['worker_id'],
                worker_type=data['worker_type'],
                capabilities=data['capabilities']
            )
            
            if success:
                return jsonify({
                    "status": "registered",
                    "worker_id": data['worker_id'],
                    "message": "Worker registered successfully"
                }), 200
            else:
                return jsonify({"error": "Registration failed"}), 500
                
        except Exception as e:
            logger.error(f"Error registering worker: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/workers/<worker_id>/heartbeat', methods=['POST'])
    def worker_heartbeat(worker_id: str):
        """
        Recibir heartbeat de worker
        Workers deben enviar esto cada 30s para indicar que están vivos
        """
        try:
            orchestrator.update_heartbeat(worker_id)
            return jsonify({"status": "ok"}), 200
        except Exception as e:
            logger.error(f"Error processing heartbeat: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/workers/<worker_id>/tasks', methods=['GET'])
    def get_task_for_worker(worker_id: str):
        """
        Worker solicita tarea
        Retorna tarea si hay disponible, o null si no hay trabajo
        
        Response:
        {
            "task": {
                "task_id": "uuid",
                "type": "agent_action",
                "data": {...}
            }
        }
        """
        try:
            task = orchestrator.get_task_for_worker(worker_id)
            
            if task:
                return jsonify({
                    "task": {
                        "task_id": task.task_id,
                        "type": task.type,
                        "data": task.data,
                        "priority": task.priority
                    }
                }), 200
            else:
                return jsonify({"task": None}), 200
                
        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/workers/list', methods=['GET'])
    def list_workers():
        """Listar todos los workers registrados"""
        try:
            workers_data = []
            for worker_id, worker in orchestrator.workers.items():
                workers_data.append({
                    "worker_id": worker_id,
                    "worker_type": worker.worker_type,
                    "status": worker.status,
                    "last_heartbeat": worker.last_heartbeat,
                    "tasks_completed": worker.tasks_completed,
                    "tasks_failed": worker.tasks_failed,
                    "capabilities": worker.capabilities
                })
            
            return jsonify({
                "workers": workers_data,
                "total": len(workers_data)
            }), 200
            
        except Exception as e:
            logger.error(f"Error listing workers: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/workers/<worker_id>/unregister', methods=['POST'])
    def unregister_worker(worker_id: str):
        """Desregistrar worker"""
        try:
            orchestrator.unregister_worker(worker_id)
            return jsonify({"status": "unregistered"}), 200
        except Exception as e:
            logger.error(f"Error unregistering worker: {e}")
            return jsonify({"error": str(e)}), 500
    
    # ==========================================
    # TASK MANAGEMENT
    # ==========================================
    
    @app.route('/api/tasks/submit', methods=['POST'])
    def submit_task():
        """
        Crear nueva tarea
        
        Request body:
        {
            "type": "agent_action",
            "data": {
                "messages": [...],
                "model": "llama-3.3-70b",
                "temperature": 0.8
            },
            "priority": 5
        }
        """
        try:
            data = request.json
            
            # Validar campos
            if 'type' not in data or 'data' not in data:
                return jsonify({"error": "Missing 'type' or 'data' field"}), 400
            
            # Crear tarea
            task_id = orchestrator.submit_task(
                task_type=data['type'],
                task_data=data['data'],
                priority=data.get('priority', 5)
            )
            
            return jsonify({
                "task_id": task_id,
                "status": "submitted",
                "message": "Task queued successfully"
            }), 201
            
        except Exception as e:
            logger.error(f"Error submitting task: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/tasks/<task_id>/result', methods=['POST'])
    def report_task_result(task_id: str):
        """
        Worker reporta resultado de tarea
        
        Request body:
        {
            "worker_id": "groq-worker-1",
            "result": {
                "success": true,
                "output": "...",
                "tokens_used": 150
            }
        }
        """
        try:
            data = request.json
            
            if 'worker_id' not in data or 'result' not in data:
                return jsonify({"error": "Missing 'worker_id' or 'result'"}), 400
            
            orchestrator.report_result(
                task_id=task_id,
                worker_id=data['worker_id'],
                result=data['result']
            )
            
            return jsonify({"status": "received"}), 200
            
        except Exception as e:
            logger.error(f"Error reporting result: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/tasks/status/<task_id>', methods=['GET'])
    def get_task_status(task_id: str):
        """Consultar estado de tarea"""
        try:
            task = orchestrator.tasks.get(task_id)
            
            if not task:
                return jsonify({"error": "Task not found"}), 404
            
            return jsonify({
                "task_id": task_id,
                "type": task.type,
                "status": task.status,
                "assigned_to": task.assigned_to,
                "created_at": task.created_at,
                "completed_at": task.completed_at,
                "result": task.result
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting task status: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/tasks/queue', methods=['GET'])
    def get_task_queue():
        """Ver estado de la cola de tareas"""
        try:
            queue_data = []
            for task in orchestrator.task_queue:
                queue_data.append({
                    "task_id": task.task_id,
                    "type": task.type,
                    "priority": task.priority,
                    "status": task.status,
                    "created_at": task.created_at
                })
            
            return jsonify({
                "queue": queue_data,
                "pending": len([t for t in orchestrator.tasks.values() if t.status == "pending"]),
                "assigned": len([t for t in orchestrator.tasks.values() if t.status == "assigned"]),
                "completed": len([t for t in orchestrator.tasks.values() if t.status == "completed"]),
                "failed": len([t for t in orchestrator.tasks.values() if t.status == "failed"])
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting queue: {e}")
            return jsonify({"error": str(e)}), 500
    
    # ==========================================
    # STATS & MONITORING
    # ==========================================
    
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """Estadísticas del sistema"""
        try:
            online_workers = [w for w in orchestrator.workers.values() if w.status in ["online", "busy"]]
            
            return jsonify({
                "workers": {
                    "total": len(orchestrator.workers),
                    "online": len(online_workers),
                    "busy": len([w for w in online_workers if w.status == "busy"]),
                    "by_type": {
                        worker_type: len([w for w in online_workers if w.worker_type == worker_type])
                        for worker_type in set(w.worker_type for w in orchestrator.workers.values())
                    }
                },
                "tasks": {
                    "total": len(orchestrator.tasks),
                    "pending": len([t for t in orchestrator.tasks.values() if t.status == "pending"]),
                    "assigned": len([t for t in orchestrator.tasks.values() if t.status == "assigned"]),
                    "completed": len([t for t in orchestrator.tasks.values() if t.status == "completed"]),
                    "failed": len([t for t in orchestrator.tasks.values() if t.status == "failed"])
                },
                "performance": {
                    "total_completed": sum(w.tasks_completed for w in orchestrator.workers.values()),
                    "total_failed": sum(w.tasks_failed for w in orchestrator.workers.values()),
                    "success_rate": (
                        sum(w.tasks_completed for w in orchestrator.workers.values()) / 
                        max(1, sum(w.tasks_completed + w.tasks_failed for w in orchestrator.workers.values()))
                    ) * 100
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return jsonify({"error": str(e)}), 500
    
    logger.info("🎯 Orchestrator Flask app created")
    return app


def main():
    """Punto de entrada principal para ejecutar como módulo"""
    import sys
    
    logger.info("="*60)
    logger.info("🎯 D8 ORCHESTRATOR - Starting...")
    logger.info("="*60)
    
    app = create_orchestrator_app()
    
    # Configuración del servidor
    host = "0.0.0.0"  # Escuchar en todas las interfaces
    port = 7001
    
    logger.info(f"🌐 Orchestrator listening on http://{host}:{port}")
    logger.info(f"📊 Health check: http://{host}:{port}/health")
    logger.info(f"📈 Statistics: http://{host}:{port}/api/stats")
    logger.info("="*60)
    
    try:
        # Iniciar servidor
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down orchestrator...")
        sys.exit(0)


if __name__ == '__main__':
    """Ejecutar orchestrator en modo standalone"""
    main()
