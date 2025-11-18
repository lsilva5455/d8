"""
Distributed Worker Node - Fixed imports
Runs on any computer (Windows/Linux/Mac) and connects to Raspberry Pi orchestrator
"""

import requests
import time
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from dotenv import load_dotenv

load_dotenv('.env.worker')  # Load worker-specific config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
        self.client = None
        self._initialize_client()
        logger.info(f"🔧 Worker initialized: {config.worker_id} ({config.worker_type})")
    
    def _initialize_client(self):
        """Initialize appropriate API client"""
        try:
            if self.config.worker_type == "groq":
                from groq import Groq
                self.client = Groq(api_key=self.config.api_key)
                logger.info("✅ Groq client initialized")
                
            elif self.config.worker_type == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=self.config.api_key)
                self.client = genai.GenerativeModel('gemini-2.0-flash-exp')
                logger.info("✅ Gemini client initialized")
                
            elif self.config.worker_type == "claude":
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.config.api_key)
                logger.info("✅ Claude client initialized")
                
            else:
                logger.warning(f"⚠️ Unknown worker type: {self.config.worker_type}")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize client: {e}")
            raise
    
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
            # Suppress connection errors during normal polling
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
            messages = task['messages']
            model = task.get('model', 'gemini-2.0-flash-exp')
            temperature = task.get('temperature', 0.8)
            
            # Execute based on worker type
            if self.config.worker_type == "groq":
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature
                )
                result = response.choices[0].message.content
                
            elif self.config.worker_type == "gemini":
                # Convert messages to Gemini format
                prompt = "\n\n".join([
                    f"{m['role']}: {m['content']}" for m in messages
                ])
                
                response = self.client.generate_content(
                    prompt,
                    generation_config={
                        'temperature': temperature,
                        'max_output_tokens': 1000
                    }
                )
                result = response.text
            
            else:
                return {"success": False, "error": "Unsupported worker type"}
            
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
        # TODO: Implement for evolution tasks
        return {"success": False, "error": "Not implemented"}
    
    def _execute_mutation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute genetic mutation (for GPU nodes)"""
        # TODO: Implement for evolution tasks
        return {"success": False, "error": "Not implemented"}
    
    def _execute_code_generation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code generation (for GPU nodes with DeepSeek)"""
        # TODO: Implement for code generation tasks
        return {"success": False, "error": "Not implemented"}
    
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
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "worker_type": self.config.worker_type
        }


if __name__ == "__main__":
    # Load config from environment
    config = WorkerConfig(
        orchestrator_url=os.getenv("ORCHESTRATOR_URL", "http://localhost:5000"),
        worker_id=os.getenv("WORKER_ID", f"worker_{int(time.time())}"),
        worker_type=os.getenv("WORKER_TYPE", "gemini"),
        api_key=os.getenv("GEMINI_API_KEY") if os.getenv("WORKER_TYPE") == "gemini" else os.getenv("API_KEY"),
        poll_interval=int(os.getenv("POLL_INTERVAL", "5"))
    )
    
    print(f"""
╔══════════════════════════════════════════════════╗
║          🤖 DISTRIBUTED WORKER NODE             ║
╠══════════════════════════════════════════════════╣
║  Worker ID:   {config.worker_id:30s} ║
║  Type:        {config.worker_type:30s} ║
║  Orchestrator: {config.orchestrator_url:27s} ║
╚══════════════════════════════════════════════════╝
    """)
    
    worker = DistributedWorker(config)
    worker.start()
