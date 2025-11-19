"""
Orchestrator Service (runs on Raspberry Pi)
Manages distributed worker nodes and task queue
"""

from flask import Blueprint, request, jsonify
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time
import uuid
import logging
from collections import deque
import threading

logger = logging.getLogger(__name__)

# Blueprint for orchestrator endpoints
orchestrator_bp = Blueprint('orchestrator', __name__, url_prefix='/api/workers')


@dataclass
class Worker:
    """Registered worker node"""
    worker_id: str
    worker_type: str  # groq, gemini, claude, deepseek_gpu
    capabilities: Dict[str, Any]
    status: str  # online, offline, busy
    last_heartbeat: float
    tasks_completed: int = 0
    tasks_failed: int = 0


@dataclass
class Task:
    """Task to be executed by worker"""
    task_id: str
    type: str  # agent_action, evolution_crossover, evolution_mutation, code_generation
    data: Dict[str, Any]
    priority: int = 5  # 1-10, higher = more urgent
    assigned_to: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, assigned, completed, failed


class DistributedOrchestrator:
    """
    Manages distributed worker pool and task queue
    Runs on Raspberry Pi as central coordinator
    """
    
    def __init__(self):
        self.workers: Dict[str, Worker] = {}
        self.task_queue: deque[Task] = deque()
        self.tasks: Dict[str, Task] = {}
        self.lock = threading.Lock()
        
        # Start background thread for task assignment
        self.active = True
        self.assignment_thread = threading.Thread(target=self._assignment_loop, daemon=True)
        self.assignment_thread.start()
        
        logger.info("🎯 Distributed Orchestrator initialized")
    
    def register_worker(self, worker_id: str, worker_type: str, capabilities: Dict) -> bool:
        """Register a new worker node"""
        with self.lock:
            self.workers[worker_id] = Worker(
                worker_id=worker_id,
                worker_type=worker_type,
                capabilities=capabilities,
                status="online",
                last_heartbeat=time.time()
            )
        
        logger.info(f"✅ Worker registered: {worker_id} ({worker_type})")
        logger.info(f"   Capabilities: {capabilities}")
        logger.info(f"   Total workers: {len(self.workers)}")
        return True
    
    def unregister_worker(self, worker_id: str):
        """Unregister worker"""
        with self.lock:
            if worker_id in self.workers:
                del self.workers[worker_id]
                logger.info(f"👋 Worker unregistered: {worker_id}")
    
    def update_heartbeat(self, worker_id: str):
        """Update worker heartbeat timestamp"""
        with self.lock:
            if worker_id in self.workers:
                self.workers[worker_id].last_heartbeat = time.time()
    
    def submit_task(self, task_type: str, task_data: Dict[str, Any], priority: int = 5) -> str:
        """Submit task to queue"""
        task_id = str(uuid.uuid4())
        
        task = Task(
            task_id=task_id,
            type=task_type,
            data=task_data,
            priority=priority
        )
        
        with self.lock:
            self.tasks[task_id] = task
            self.task_queue.append(task)
        
        logger.info(f"📥 Task submitted: {task_id} ({task_type}, priority={priority})")
        return task_id
    
    def get_task_for_worker(self, worker_id: str) -> Optional[Task]:
        """Get next available task for worker"""
        with self.lock:
            worker = self.workers.get(worker_id)
            
            if not worker or worker.status != "online":
                return None
            
            # Find suitable task
            for task in sorted(self.task_queue, key=lambda t: -t.priority):
                if task.status == "pending" and self._can_worker_handle_task(worker, task):
                    # Assign task
                    task.status = "assigned"
                    task.assigned_to = worker_id
                    worker.status = "busy"
                    self.task_queue.remove(task)
                    
                    logger.info(f"📤 Task assigned: {task.task_id} → {worker_id}")
                    return task
            
            return None
    
    def report_result(self, task_id: str, worker_id: str, result: Dict[str, Any]):
        """Worker reports task completion"""
        with self.lock:
            task = self.tasks.get(task_id)
            worker = self.workers.get(worker_id)
            
            if not task or not worker:
                logger.error(f"❌ Invalid task or worker: {task_id}, {worker_id}")
                return
            
            # Update task
            task.result = result
            task.completed_at = time.time()
            task.status = "completed" if result.get("success") else "failed"
            
            # Update worker
            worker.status = "online"
            if result.get("success"):
                worker.tasks_completed += 1
            else:
                worker.tasks_failed += 1
            
            logger.info(f"✅ Task completed: {task_id} by {worker_id} (success={result.get('success')})")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        with self.lock:
            online_workers = [w for w in self.workers.values() if w.status in ["online", "busy"]]
            
            return {
                "workers": {
                    "total": len(self.workers),
                    "online": len([w for w in self.workers.values() if w.status == "online"]),
                    "busy": len([w for w in self.workers.values() if w.status == "busy"]),
                    "by_type": self._count_by_type(self.workers.values())
                },
                "tasks": {
                    "pending": len([t for t in self.tasks.values() if t.status == "pending"]),
                    "assigned": len([t for t in self.tasks.values() if t.status == "assigned"]),
                    "completed": len([t for t in self.tasks.values() if t.status == "completed"]),
                    "failed": len([t for t in self.tasks.values() if t.status == "failed"]),
                    "total": len(self.tasks)
                },
                "performance": {
                    "total_completed": sum(w.tasks_completed for w in self.workers.values()),
                    "total_failed": sum(w.tasks_failed for w in self.workers.values()),
                    "success_rate": self._calculate_success_rate()
                }
            }
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        with self.lock:
            return self.tasks.get(task_id)
    
    def get_workers(self) -> Dict[str, Worker]:
        """Get all registered workers"""
        with self.lock:
            return dict(self.workers)
    
    def _assignment_loop(self):
        """Background thread that assigns tasks to workers"""
        while self.active:
            time.sleep(1)
            
            # Check for stale workers
            self._cleanup_stale_workers()
    
    def _cleanup_stale_workers(self, timeout: int = 60):
        """Remove workers that haven't sent heartbeat"""
        with self.lock:
            current_time = time.time()
            stale = [
                wid for wid, w in self.workers.items()
                if current_time - w.last_heartbeat > timeout
            ]
            
            for wid in stale:
                logger.warning(f"⚠️ Worker timeout: {wid}")
                del self.workers[wid]
    
    def _can_worker_handle_task(self, worker: Worker, task: Task) -> bool:
        """Check if worker can handle task type"""
        # Map task types to worker types
        if task.type == "agent_action":
            return True  # Any worker can handle
        
        elif task.type in ["evolution_crossover", "evolution_mutation", "code_generation"]:
            return worker.worker_type in ["deepseek_gpu", "claude", "gemini"]
        
        return False
    
    def _count_by_type(self, workers) -> Dict[str, int]:
        """Count workers by type"""
        counts = {}
        for w in workers:
            counts[w.worker_type] = counts.get(w.worker_type, 0) + 1
        return counts
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate"""
        total = sum(w.tasks_completed + w.tasks_failed for w in self.workers.values())
        if total == 0:
            return 0.0
        completed = sum(w.tasks_completed for w in self.workers.values())
        return (completed / total) * 100


# Global orchestrator instance
orchestrator = DistributedOrchestrator()


# Flask endpoints

@orchestrator_bp.route('/register', methods=['POST'])
def register_worker():
    """Register new worker"""
    data = request.json
    
    success = orchestrator.register_worker(
        worker_id=data['worker_id'],
        worker_type=data['worker_type'],
        capabilities=data['capabilities']
    )
    
    return jsonify({"success": success})


@orchestrator_bp.route('/unregister', methods=['POST'])
def unregister_worker():
    """Unregister worker"""
    data = request.json
    orchestrator.unregister_worker(data['worker_id'])
    return jsonify({"success": True})


@orchestrator_bp.route('/<worker_id>/tasks', methods=['GET'])
def get_task(worker_id: str):
    """Worker polls for tasks"""
    # Update heartbeat
    with orchestrator.lock:
        if worker_id in orchestrator.workers:
            orchestrator.workers[worker_id].last_heartbeat = time.time()
    
    task = orchestrator.get_task_for_worker(worker_id)
    
    if task:
        return jsonify({
            "task": {
                "task_id": task.task_id,
                "type": task.type,
                **task.data
            }
        })
    else:
        return jsonify({"task": None})


@orchestrator_bp.route('/results', methods=['POST'])
def report_result():
    """Worker reports task result"""
    data = request.json
    
    orchestrator.report_result(
        task_id=data['task_id'],
        worker_id=data['worker_id'],
        result=data['result']
    )
    
    return jsonify({"success": True})


@orchestrator_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get orchestrator statistics"""
    return jsonify(orchestrator.get_stats())
