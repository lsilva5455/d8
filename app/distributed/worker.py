"""
Distributed Worker Node
Runs on any computer (Windows/Linux/Mac) and connects to Raspberry Pi orchestrator
"""

import requests
import time
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WorkerConfig:
    """Worker node configuration"""
    orchestrator_url: str  # Raspberry Pi IP
    worker_id: str
    worker_type: str  # "groq", "gemini", "claude", "deepseek_gpu"
    api_key: str
    poll_interval: int = 5  # seconds
    max_tasks_parallel: int = 1


class DistributedWorker:
    """
    Worker node that polls Raspberry Pi orchestrator for tasks
    Executes agent actions or evolution operations
    Reports results back
    """
    
    def __init__(self, config: WorkerConfig):
        self.config = config
        self.active = False
        logger.info(f"🔧 Worker initialized: {config.worker_id} ({config.worker_type})")
    
    def register(self) -> bool:
        """Register with orchestrator"""
        try:
            response = requests.post(
                f"{self.config.orchestrator_url}/api/workers/register",
                json={
                    "worker_id": self.config.worker_id,
                    "worker_type": self.config.worker_type,
                    "capabilities": self._get_capabilities(),
                    "status": "online"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Registered with orchestrator")
                return True
            else:
                logger.error(f"❌ Registration failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Cannot reach orchestrator: {e}")
            return False
    
    def start(self):
        """Start polling for tasks"""
        if not self.register():
            logger.error("Failed to register, exiting")
            return
        
        self.active = True
        logger.info(f"🚀 Worker started, polling every {self.config.poll_interval}s")
        
        while self.active:
            try:
                task = self._poll_for_task()
                
                if task:
                    logger.info(f"📥 Received task: {task['task_id']} ({task['type']})")
                    result = self._execute_task(task)
                    self._report_result(task['task_id'], result)
                else:
                    time.sleep(self.config.poll_interval)
                    
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down...")
                self.active = False
                self._unregister()
                break
                
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                time.sleep(self.config.poll_interval)
    
    def _poll_for_task(self) -> Optional[Dict[str, Any]]:
        """Poll orchestrator for available tasks"""
        try:
            response = requests.get(
                f"{self.config.orchestrator_url}/api/workers/{self.config.worker_id}/tasks",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('task')
            
            return None
            
        except Exception as e:
            logger.debug(f"Poll failed: {e}")
            return None
    
    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task based on type"""
        task_type = task['type']
        
        if task_type == "agent_action":
            return self._execute_agent_action(task)
        
        elif task_type == "evolution_crossover":
            return self._execute_crossover(task)
        
        elif task_type == "evolution_mutation":
            return self._execute_mutation(task)
        
        elif task_type == "code_generation":
            return self._execute_code_generation(task)
        
        else:
            return {"success": False, "error": f"Unknown task type: {task_type}"}
    
    def _execute_agent_action(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent action using local LLM client"""
        try:
            # Import appropriate client based on worker type
            if self.config.worker_type == "groq":
                from lib.llm import GroqClient
                client = GroqClient(api_key=self.config.api_key)
                
            elif self.config.worker_type == "gemini":
                from lib.llm import GeminiClient
                client = GeminiClient(api_key=self.config.api_key)
                
            elif self.config.worker_type == "claude":
                from app.integrations.claude_client import ClaudeClient
                client = ClaudeClient(api_key=self.config.api_key)
            
            else:
                return {"success": False, "error": "Unsupported worker type"}
            
            # Execute
            result = client.chat(
                messages=task['messages'],
                model=task.get('model'),
                temperature=task.get('temperature', 0.8)
            )
            
            return {
                "success": True,
                "result": result,
                "worker_id": self.config.worker_id
            }
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_crossover(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute genetic crossover (for GPU nodes)"""
        # Similar to agent action but for evolution
        pass
    
    def _execute_mutation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute genetic mutation (for GPU nodes)"""
        pass
    
    def _execute_code_generation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code generation (for GPU nodes with DeepSeek)"""
        pass
    
    def _report_result(self, task_id: str, result: Dict[str, Any]):
        """Report task result back to orchestrator"""
        try:
            response = requests.post(
                f"{self.config.orchestrator_url}/api/workers/results",
                json={
                    "task_id": task_id,
                    "worker_id": self.config.worker_id,
                    "result": result,
                    "timestamp": time.time()
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Result reported for task {task_id}")
            else:
                logger.error(f"❌ Failed to report result: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Cannot report result: {e}")
    
    def _unregister(self):
        """Unregister from orchestrator"""
        try:
            requests.post(
                f"{self.config.orchestrator_url}/api/workers/unregister",
                json={"worker_id": self.config.worker_id},
                timeout=5
            )
            logger.info("👋 Unregistered from orchestrator")
        except:
            pass
    
    def _get_capabilities(self) -> Dict[str, Any]:
        """Return worker capabilities"""
        import platform
        import psutil
        
        return {
            "os": platform.system(),
            "cpu_count": psutil.cpu_count(),
            "memory_gb": psutil.virtual_memory().total / (1024**3),
            "worker_type": self.config.worker_type
        }


if __name__ == "__main__":
    # Load config from environment
    config = WorkerConfig(
        orchestrator_url=os.getenv("ORCHESTRATOR_URL", "http://raspberrypi.local:5000"),
        worker_id=os.getenv("WORKER_ID", f"worker_{int(time.time())}"),
        worker_type=os.getenv("WORKER_TYPE", "groq"),
        api_key=os.getenv("API_KEY"),
        poll_interval=int(os.getenv("POLL_INTERVAL", "5"))
    )
    
    worker = DistributedWorker(config)
    worker.start()
