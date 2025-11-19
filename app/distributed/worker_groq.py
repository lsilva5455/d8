#!/usr/bin/env python3
"""Groq Worker - Fast, reliable, and generous free tier"""

import os
import json
import time
import requests
from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path
from groq import Groq

# Worker configuration - Consolidated under d8_data/
D8_DATA_PATH = Path(os.path.expanduser("~/Documents/d8_data"))
WORKERS_BASE_PATH = D8_DATA_PATH / "workers"

def load_worker_config() -> Dict[str, Any]:
    """Load worker configuration from JSON"""
    config_path = WORKERS_BASE_PATH / "groq/worker_config.json"
    creds_path = WORKERS_BASE_PATH / "groq/credentials.json"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Worker config not found: {config_path}")
    if not creds_path.exists():
        raise FileNotFoundError(f"Credentials not found: {creds_path}")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    with open(creds_path, 'r') as f:
        creds = json.load(f)
    
    return {**config, **creds}

@dataclass
class WorkerConfig:
    worker_id: str
    worker_type: str
    orchestrator_url: str
    poll_interval: int
    api_key: str
    model: str
    
    @classmethod
    def from_json(cls, config_data: Dict[str, Any]):
        """Create config from JSON data"""
        worker = config_data.get("worker", {})
        model = config_data.get("model", {})
        polling = config_data.get("polling", {})
        
        # Get orchestrator URL from main config
        main_config_path = WORKERS_BASE_PATH / "config.json"
        orchestrator_url = "http://localhost:5000"
        if main_config_path.exists():
            with open(main_config_path, 'r') as f:
                main_config = json.load(f)
                orchestrator_url = main_config.get("orchestrator", {}).get("url", orchestrator_url)
        
        return cls(
            worker_id=worker.get("id", "groq-worker-1"),
            worker_type=worker.get("type", "groq"),
            orchestrator_url=orchestrator_url,
            poll_interval=polling.get("interval_seconds", 5),
            api_key=config_data.get("api_key", ""),
            model=model.get("name", "llama-3.3-70b-versatile")
        )

class GroqWorker:
    def __init__(self, config: WorkerConfig):
        self.config = config
        self.client = Groq(api_key=config.api_key)
        self.model = config.model
        
        # Stats
        self.total_requests = 0
        self.successful_requests = 0
        
    def register(self) -> bool:
        """Register with orchestrator"""
        try:
            # Load capabilities from config
            config_data = load_worker_config()
            capabilities = config_data.get("capabilities", {})
            model_info = config_data.get("model", {})
            
            response = requests.post(
                f"{self.config.orchestrator_url}/api/workers/register",
                json={
                    "worker_id": self.config.worker_id,
                    "worker_type": self.config.worker_type,
                    "capabilities": {
                        "models": [model_info.get("name", self.model)],
                        "max_tokens": model_info.get("max_tokens", 32768),
                        "supports_streaming": model_info.get("supports_streaming", True),
                        "speed": model_info.get("speed_class", "very_fast")
                    }
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return False
    
    def get_task(self) -> Optional[Dict[str, Any]]:
        """Poll for tasks"""
        try:
            response = requests.get(
                f"{self.config.orchestrator_url}/api/workers/{self.config.worker_id}/tasks",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('task')
        except:
            pass
        return None
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent action via Groq"""
        try:
            # Handle both formats: task with task_data or direct data
            if 'task_data' in task:
                task_data = task.get('task_data', {})
            else:
                # Direct format from orchestrator
                task_data = task
            
            messages = task_data.get('messages', [])
            
            # Call Groq API
            self.total_requests += 1
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=task_data.get('temperature', 0.8),
                max_tokens=task_data.get('max_tokens', 2000)
            )
            
            elapsed = time.time() - start_time
            self.successful_requests += 1
            
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "model": self.model,
                "tokens": response.usage.total_tokens,
                "elapsed": round(elapsed, 2),
                "stats": {
                    "total_requests": self.total_requests,
                    "successful_requests": self.successful_requests,
                    "success_rate": self.successful_requests / self.total_requests if self.total_requests > 0 else 0
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stats": {
                    "total_requests": self.total_requests,
                    "successful_requests": self.successful_requests
                }
            }
    
    def report_result(self, task_id: str, result: Dict[str, Any]) -> bool:
        """Report task result"""
        try:
            response = requests.post(
                f"{self.config.orchestrator_url}/api/workers/results",
                json={
                    "task_id": task_id,
                    "worker_id": self.config.worker_id,
                    "result": result
                },
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def start(self):
        """Main worker loop"""
        print(f"🚀 Groq Worker starting...")
        print(f"   ID: {self.config.worker_id}")
        print(f"   Model: {self.model}")
        print(f"   Free Tier: 30 req/min, 14,400 req/día")
        print(f"   Orchestrator: {self.config.orchestrator_url}")
        
        # Register
        if not self.register():
            print("❌ Failed to register, exiting")
            return
        
        print("✅ Registered successfully")
        print("⏳ Polling for tasks...\n")
        
        while True:
            try:
                # Get task
                task = self.get_task()
                
                if task:
                    task_id = task.get('task_id')
                    print(f"📥 Received task: {task_id}")
                    
                    # Execute
                    result = self.execute_task(task)
                    
                    # Report
                    if self.report_result(task_id, result):
                        status = "✅" if result.get('success') else "❌"
                        elapsed = result.get('elapsed', 0)
                        tokens = result.get('tokens', 0)
                        stats = result.get('stats', {})
                        
                        print(f"{status} Task {task_id} completed")
                        print(f"   ⏱️  Time: {elapsed}s, Tokens: {tokens}")
                        print(f"   📊 Success rate: {stats.get('success_rate', 0) * 100:.1f}%\n")
                    else:
                        print(f"⚠️  Failed to report result for {task_id}\n")
                
                time.sleep(self.config.poll_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️  Worker stopped by user")
                print(f"\n📊 Final Stats:")
                print(f"   Total requests: {self.total_requests}")
                print(f"   Successful: {self.successful_requests}")
                print(f"   Success rate: {self.successful_requests / self.total_requests * 100 if self.total_requests > 0 else 0:.1f}%")
                break
            except Exception as e:
                print(f"❌ Error in worker loop: {e}")
                time.sleep(self.config.poll_interval)

if __name__ == '__main__':
    try:
        # Load configuration from JSON
        config_data = load_worker_config()
        config = WorkerConfig.from_json(config_data)
        
        if not config.api_key:
            print("❌ GROQ_API_KEY not found in credentials.json")
            print(f"\n📝 Config location: {WORKERS_BASE_PATH / 'groq/credentials.json'}")
            print("   Update the api_key field with your Groq API key")
            print("   Get key at: https://console.groq.com/keys")
            exit(1)
        
        worker = GroqWorker(config)
        worker.start()
        
    except FileNotFoundError as e:
        print(f"❌ Configuration error: {e}")
        print(f"\n📁 Expected structure:")
        print(f"   {WORKERS_BASE_PATH / 'config.json'}")
        print(f"   {WORKERS_BASE_PATH / 'groq/worker_config.json'}")
        print(f"   {WORKERS_BASE_PATH / 'groq/credentials.json'}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)
