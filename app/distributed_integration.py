"""
D8 Integration with Distributed System
=======================================
Conecta el sistema evolutivo D8 con el orchestrator distribuido.

Este módulo permite que Darwin (sistema evolutivo) y el Congreso
envíen tareas a workers remotos en lugar de ejecutarlas localmente.
"""

import requests
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class D8DistributedClient:
    """
    Cliente para interactuar con el orchestrator desde D8
    
    Uso:
        client = D8DistributedClient("http://192.168.1.100:7001")
        
        # Ejecutar acción de agente de forma distribuida
        result = client.execute_agent_action(
            messages=[{"role": "user", "content": "Generate ideas"}],
            model="llama-3.3-70b"
        )
    """
    
    orchestrator_url: str
    timeout: int = 60  # Timeout para esperar resultado
    poll_interval: int = 2  # Intervalo de polling para resultado
    
    def __post_init__(self):
        """Validar conexión con orchestrator"""
        try:
            response = requests.get(f"{self.orchestrator_url}/health", timeout=5)
            response.raise_for_status()
            logger.info(f"✅ Connected to orchestrator at {self.orchestrator_url}")
        except Exception as e:
            logger.error(f"❌ Cannot connect to orchestrator: {e}")
            raise ConnectionError(f"Orchestrator not reachable at {self.orchestrator_url}")
    
    def execute_agent_action(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.3-70b",
        temperature: float = 0.8,
        priority: int = 5,
        wait_for_result: bool = True
    ) -> Dict[str, Any]:
        """
        Ejecutar acción de agente en worker distribuido
        
        Args:
            messages: Lista de mensajes para el LLM
            model: Modelo a usar
            temperature: Temperatura de generación
            priority: Prioridad de la tarea (1-10)
            wait_for_result: Si True, espera el resultado. Si False, retorna task_id
        
        Returns:
            Si wait_for_result=True: {"success": True, "output": "..."}
            Si wait_for_result=False: {"task_id": "uuid"}
        """
        # Enviar tarea al orchestrator
        task_id = self._submit_task(
            task_type="agent_action",
            task_data={
                "messages": messages,
                "model": model,
                "temperature": temperature
            },
            priority=priority
        )
        
        if not wait_for_result:
            return {"task_id": task_id}
        
        # Esperar resultado
        return self._wait_for_result(task_id)
    
    def execute_evolution_crossover(
        self,
        genome1: Dict[str, Any],
        genome2: Dict[str, Any],
        wait_for_result: bool = True
    ) -> Dict[str, Any]:
        """
        Ejecutar crossover de genomas en worker distribuido
        
        Ideal para DeepSeek local (zero-cost)
        """
        task_id = self._submit_task(
            task_type="evolution_crossover",
            task_data={
                "genome1": genome1,
                "genome2": genome2
            },
            priority=7  # Alta prioridad para evolución
        )
        
        if not wait_for_result:
            return {"task_id": task_id}
        
        return self._wait_for_result(task_id)
    
    def execute_evolution_mutation(
        self,
        genome: Dict[str, Any],
        mutation_rate: float = 0.1,
        wait_for_result: bool = True
    ) -> Dict[str, Any]:
        """
        Ejecutar mutación de genoma en worker distribuido
        """
        task_id = self._submit_task(
            task_type="evolution_mutation",
            task_data={
                "genome": genome,
                "mutation_rate": mutation_rate
            },
            priority=7
        )
        
        if not wait_for_result:
            return {"task_id": task_id}
        
        return self._wait_for_result(task_id)
    
    def execute_code_generation(
        self,
        prompt: str,
        language: str = "python",
        priority: int = 5,
        wait_for_result: bool = True
    ) -> Dict[str, Any]:
        """
        Ejecutar generación de código en worker distribuido
        """
        task_id = self._submit_task(
            task_type="code_generation",
            task_data={
                "prompt": prompt,
                "language": language
            },
            priority=priority
        )
        
        if not wait_for_result:
            return {"task_id": task_id}
        
        return self._wait_for_result(task_id)
    
    def get_available_workers(self) -> List[Dict[str, Any]]:
        """Obtener lista de workers disponibles"""
        try:
            response = requests.get(
                f"{self.orchestrator_url}/api/workers/list",
                timeout=5
            )
            response.raise_for_status()
            return response.json()["workers"]
        except Exception as e:
            logger.error(f"Error getting workers: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema distribuido"""
        try:
            response = requests.get(
                f"{self.orchestrator_url}/api/stats",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    def _submit_task(
        self,
        task_type: str,
        task_data: Dict[str, Any],
        priority: int = 5
    ) -> str:
        """Enviar tarea al orchestrator"""
        try:
            response = requests.post(
                f"{self.orchestrator_url}/api/tasks/submit",
                json={
                    "type": task_type,
                    "data": task_data,
                    "priority": priority
                },
                timeout=10
            )
            response.raise_for_status()
            task_id = response.json()["task_id"]
            logger.info(f"📤 Task submitted: {task_id} ({task_type})")
            return task_id
        except Exception as e:
            logger.error(f"Error submitting task: {e}")
            raise
    
    def _wait_for_result(self, task_id: str) -> Dict[str, Any]:
        """Esperar resultado de tarea con polling"""
        start_time = time.time()
        
        while (time.time() - start_time) < self.timeout:
            try:
                response = requests.get(
                    f"{self.orchestrator_url}/api/tasks/status/{task_id}",
                    timeout=5
                )
                response.raise_for_status()
                task_status = response.json()
                
                if task_status["status"] == "completed":
                    logger.info(f"✅ Task completed: {task_id}")
                    return task_status["result"]
                
                elif task_status["status"] == "failed":
                    logger.error(f"❌ Task failed: {task_id}")
                    return {"success": False, "error": "Task failed"}
                
                # Aún en progreso, esperar
                time.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Error polling task status: {e}")
                time.sleep(self.poll_interval)
        
        # Timeout
        logger.warning(f"⏱️ Task timeout: {task_id}")
        return {"success": False, "error": f"Timeout after {self.timeout}s"}


# ==========================================
# Integration with Darwin (Evolution System)
# ==========================================

class DistributedEvolutionAdapter:
    """
    Adapter para que Darwin use workers distribuidos
    
    Uso en darwin.py:
        from app.distributed_integration import DistributedEvolutionAdapter
        
        adapter = DistributedEvolutionAdapter("http://orchestrator:7001")
        
        # En lugar de:
        # offspring = self._crossover_local(parent1, parent2)
        
        # Usar:
        # offspring = adapter.crossover(parent1, parent2)
    """
    
    def __init__(self, orchestrator_url: str):
        self.client = D8DistributedClient(orchestrator_url)
        logger.info("🧬 Distributed Evolution Adapter initialized")
    
    def crossover(self, genome1: Dict, genome2: Dict) -> Dict:
        """Crossover distribuido"""
        result = self.client.execute_evolution_crossover(genome1, genome2)
        
        if result.get("success"):
            return result["genome"]
        else:
            logger.error("Crossover failed, falling back to local")
            # Fallback a crossover local si falla
            return self._fallback_crossover(genome1, genome2)
    
    def mutate(self, genome: Dict, mutation_rate: float = 0.1) -> Dict:
        """Mutación distribuida"""
        result = self.client.execute_evolution_mutation(genome, mutation_rate)
        
        if result.get("success"):
            return result["genome"]
        else:
            logger.error("Mutation failed, falling back to local")
            return self._fallback_mutation(genome, mutation_rate)
    
    def _fallback_crossover(self, genome1: Dict, genome2: Dict) -> Dict:
        """Crossover local como fallback"""
        # Implementación simple: mezclar 50/50
        import random
        
        offspring = {}
        for key in genome1.keys():
            offspring[key] = genome1[key] if random.random() < 0.5 else genome2.get(key, genome1[key])
        
        return offspring
    
    def _fallback_mutation(self, genome: Dict, mutation_rate: float) -> Dict:
        """Mutación local como fallback"""
        import random
        import copy
        
        mutated = copy.deepcopy(genome)
        
        # Mutación simple: modificar valores numéricos
        for key, value in mutated.items():
            if isinstance(value, (int, float)) and random.random() < mutation_rate:
                mutated[key] = value * random.uniform(0.8, 1.2)
        
        return mutated


# ==========================================
# Helper Functions
# ==========================================

def create_distributed_client(orchestrator_url: Optional[str] = None) -> D8DistributedClient:
    """
    Factory para crear cliente distribuido
    
    Lee URL del orchestrator de environment variable si no se provee
    """
    import os
    
    if orchestrator_url is None:
        orchestrator_url = os.getenv("ORCHESTRATOR_URL", "http://localhost:7001")
    
    return D8DistributedClient(orchestrator_url)


def check_distributed_system_health(orchestrator_url: str) -> Dict[str, Any]:
    """
    Verificar salud del sistema distribuido
    
    Returns:
        {
            "orchestrator_healthy": bool,
            "workers_online": int,
            "workers_busy": int,
            "tasks_pending": int
        }
    """
    try:
        response = requests.get(f"{orchestrator_url}/health", timeout=5)
        response.raise_for_status()
        health = response.json()
        
        return {
            "orchestrator_healthy": True,
            "workers_online": health.get("workers_online", 0),
            "tasks_pending": health.get("tasks_pending", 0),
            "tasks_in_progress": health.get("tasks_in_progress", 0)
        }
    except Exception as e:
        return {
            "orchestrator_healthy": False,
            "error": str(e)
        }
