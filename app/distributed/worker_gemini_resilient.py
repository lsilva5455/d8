#!/usr/bin/env python3
"""
Gemini Worker con Retry Logic y Rate Limiting
Maneja errores 429 con exponential backoff
"""

import os
import time
import requests
from dataclasses import dataclass
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime, timedelta

# Load environment
load_dotenv('.env.worker')

@dataclass
class WorkerConfig:
    worker_id: str = os.getenv('WORKER_ID', 'gemini-resilient-1')
    worker_type: str = 'gemini'
    orchestrator_url: str = os.getenv('ORCHESTRATOR_URL', 'http://localhost:5000')
    poll_interval: int = int(os.getenv('WORKER_POLL_INTERVAL', '10'))  # Aumentado a 10s
    api_key: str = os.getenv('GEMINI_API_KEY', '')
    max_retries: int = 5
    initial_backoff: float = 2.0  # segundos

class RateLimiter:
    """Controla rate limiting para evitar 429"""
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
        
    def wait_if_needed(self):
        """Espera si estamos cerca del límite"""
        now = datetime.now()
        # Remover requests más viejos de 1 minuto
        self.request_times = [t for t in self.request_times if now - t < timedelta(minutes=1)]
        
        if len(self.request_times) >= self.requests_per_minute:
            # Esperar hasta que el más viejo tenga > 1 minuto
            oldest = self.request_times[0]
            wait_time = 60 - (now - oldest).total_seconds()
            if wait_time > 0:
                print(f"⏳ Rate limit: esperando {wait_time:.1f}s...")
                time.sleep(wait_time + 1)
        
        self.request_times.append(now)

class ResilientGeminiWorker:
    def __init__(self, config: WorkerConfig):
        self.config = config
        self.rate_limiter = RateLimiter(requests_per_minute=10)  # Conservador
        
        # Configure Gemini
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Stats
        self.total_requests = 0
        self.failed_requests = 0
        self.retries_count = 0
        
    def register(self) -> bool:
        """Register with orchestrator"""
        try:
            response = requests.post(
                f"{self.config.orchestrator_url}/api/workers/register",
                json={
                    "worker_id": self.config.worker_id,
                    "worker_type": self.config.worker_type,
                    "capabilities": {
                        "models": ["gemini-2.0-flash-exp"],
                        "max_tokens": 8192,
                        "resilient": True,
                        "rate_limiting": True
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
    
    def execute_task_with_retry(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task with exponential backoff retry"""
        task_data = task.get('task_data', {})
        messages = task_data.get('messages', [])
        
        backoff = self.config.initial_backoff
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                # Rate limiting proactivo
                self.rate_limiter.wait_if_needed()
                
                # Convert messages to Gemini format
                full_prompt = ""
                for msg in messages:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if role == 'system':
                        full_prompt += f"{content}\n\n"
                    elif role == 'user':
                        full_prompt += content
                
                # Call Gemini
                print(f"  📡 Attempt {attempt + 1}/{self.config.max_retries}")
                self.total_requests += 1
                
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=task_data.get('temperature', 0.8),
                        max_output_tokens=task_data.get('max_tokens', 2000)
                    )
                )
                
                # Success!
                return {
                    "success": True,
                    "response": response.text,
                    "model": "gemini-2.0-flash-exp",
                    "attempts": attempt + 1,
                    "stats": {
                        "total_requests": self.total_requests,
                        "failed_requests": self.failed_requests,
                        "retries": self.retries_count
                    }
                }
                
            except Exception as e:
                error_str = str(e)
                last_error = error_str
                
                # Check if it's a 429 rate limit error
                if "429" in error_str or "TooManyRequests" in error_str or "quota" in error_str.lower():
                    self.retries_count += 1
                    
                    if attempt < self.config.max_retries - 1:
                        wait_time = backoff * (2 ** attempt)  # Exponential backoff
                        print(f"  ⚠️  429 Rate Limit - Esperando {wait_time:.1f}s antes de retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"  ❌ Max retries alcanzado para 429 error")
                        self.failed_requests += 1
                        break
                
                # Other errors (not retryable)
                print(f"  ❌ Error no recuperable: {error_str[:100]}")
                self.failed_requests += 1
                break
        
        # All retries failed
        return {
            "success": False,
            "error": last_error,
            "attempts": self.config.max_retries,
            "stats": {
                "total_requests": self.total_requests,
                "failed_requests": self.failed_requests,
                "retries": self.retries_count
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
        print(f"🚀 Resilient Gemini Worker starting...")
        print(f"   ID: {self.config.worker_id}")
        print(f"   Model: gemini-2.0-flash-exp")
        print(f"   Rate Limit: 10 req/min (conservador)")
        print(f"   Max Retries: {self.config.max_retries}")
        print(f"   Poll Interval: {self.config.poll_interval}s")
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
                    
                    # Execute with retry
                    result = self.execute_task_with_retry(task)
                    
                    # Report
                    if self.report_result(task_id, result):
                        status = "✅" if result.get('success') else "❌"
                        attempts = result.get('attempts', 1)
                        print(f"{status} Task {task_id} completed (attempts: {attempts})")
                        print(f"   📊 Stats: {result.get('stats', {})}\n")
                    else:
                        print(f"⚠️  Failed to report result for {task_id}\n")
                else:
                    # No task, just heartbeat
                    pass
                
                # Wait before next poll
                time.sleep(self.config.poll_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️  Worker stopped by user")
                print(f"\n📊 Final Stats:")
                print(f"   Total requests: {self.total_requests}")
                print(f"   Failed: {self.failed_requests}")
                print(f"   Retries: {self.retries_count}")
                break
            except Exception as e:
                print(f"❌ Error in worker loop: {e}")
                time.sleep(self.config.poll_interval)

if __name__ == '__main__':
    config = WorkerConfig()
    
    if not config.api_key or config.api_key == 'your_gemini_api_key_here':
        print("❌ GEMINI_API_KEY not set in .env.worker")
        exit(1)
    
    worker = ResilientGeminiWorker(config)
    worker.start()
