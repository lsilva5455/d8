#!/usr/bin/env python3
"""Groq Worker - Fast, reliable, and generous free tier"""

import os
import time
import requests
from dataclasses import dataclass
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from groq import Groq

# Load environment
load_dotenv('.env.worker.groq')

@dataclass
class WorkerConfig:
    worker_id: str = os.getenv('WORKER_ID', 'groq-worker-1')
    worker_type: str = 'groq'
    orchestrator_url: str = os.getenv('ORCHESTRATOR_URL', 'http://localhost:5000')
    poll_interval: int = int(os.getenv('WORKER_POLL_INTERVAL', '5'))
    api_key: str = os.getenv('GROQ_API_KEY', '')

class GroqWorker:
    def __init__(self, config: WorkerConfig):
        self.config = config
        self.client = Groq(api_key=config.api_key)
        self.model = "llama-3.3-70b-versatile"
        
        # Stats
        self.total_requests = 0
        self.successful_requests = 0
        
    def register(self) -> bool:
        """Register with orchestrator"""
        try:
            response = requests.post(
                f"{self.config.orchestrator_url}/api/workers/register",
                json={
                    "worker_id": self.config.worker_id,
                    "worker_type": self.config.worker_type,
                    "capabilities": {
                        "models": [self.model],
                        "max_tokens": 32768,
                        "supports_streaming": True,
                        "speed": "very_fast"
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
            task_data = task.get('task_data', {})
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
                f"{self.config.orchestrator_url}/api/workers/{self.config.worker_id}/result",
                json={
                    "task_id": task_id,
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
    config = WorkerConfig()
    
    if not config.api_key:
        print("❌ GROQ_API_KEY not set in .env.worker.groq")
        print("\n📝 Para configurar:")
        print("   1. Obtén key gratis: https://console.groq.com/keys")
        print("   2. Crea .env.worker.groq con:")
        print("      GROQ_API_KEY=gsk_tu_key_aqui")
        print("      WORKER_ID=groq-worker-1")
        print("      WORKER_TYPE=groq")
        print("      ORCHESTRATOR_URL=http://localhost:5000")
        print("      WORKER_POLL_INTERVAL=5")
        exit(1)
    
    worker = GroqWorker(config)
    worker.start()
