"""
Slave Node - Host de Agentes D8
================================
Reemplaza el concepto de "worker" por un host que mantiene agentes D8 autónomos.

Diferencias clave con worker.py:
- NO ejecuta tareas (los agentes deciden qué hacer)
- SÍ mantiene pool local de agentes activos
- SÍ reporta métricas de cada agente
- SÍ permite crear/destruir/actualizar agentes remotamente

Author: D8 System
Date: 2025-11-21
"""

import requests
import time
import logging
import json
import subprocess
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import psutil
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SlaveResources:
    """Recursos disponibles del slave"""
    cpu_cores: int
    memory_gb: float
    disk_gb: float
    max_agents: int  # Calculado automáticamente


@dataclass
class AgentInstance:
    """Instancia de agente corriendo en este slave"""
    agent_id: str
    genome: Dict[str, Any]
    status: str  # "starting", "active", "idle", "error", "stopped"
    pid: Optional[int] = None
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    actions_executed: int = 0
    errors: int = 0
    cpu_percent: float = 0.0
    memory_mb: float = 0.0


class SlaveNode:
    """
    Slave Node - Host de agentes D8 distribuidos
    
    Responsabilidades:
    - Registrarse con orchestrator
    - Mantener pool local de agentes
    - Crear/destruir agentes según comandos del orchestrator
    - Monitorear salud de cada agente
    - Reportar métricas en heartbeat
    - Persistir estado para recuperación
    """
    
    def __init__(
        self,
        orchestrator_url: str,
        slave_id: str,
        groq_api_key: str,
        gemini_api_key: Optional[str] = None
    ):
        self.orchestrator_url = orchestrator_url
        self.slave_id = slave_id
        self.groq_api_key = groq_api_key
        self.gemini_api_key = gemini_api_key
        
        # Pool de agentes activos
        self.agents: Dict[str, AgentInstance] = {}
        
        # Recursos del slave
        self.resources = self._detect_resources()
        
        # Estado
        self.active = False
        self.heartbeat_interval = 30  # segundos
        
        # Paths
        self.data_dir = Path.home() / "Documents" / "d8_data" / "slave" / slave_id
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Git version info
        self.version_info = self._get_version_info()
        
        logger.info(f"🔧 SlaveNode initialized: {slave_id}")
        logger.info(f"   Orchestrator: {orchestrator_url}")
        logger.info(f"   Resources: {self.resources.cpu_cores} cores, "
                   f"{self.resources.memory_gb:.1f}GB RAM, "
                   f"max {self.resources.max_agents} agents")
        logger.info(f"   Version: {self.version_info['git_branch']}@{self.version_info['git_commit']}")
    
    def _detect_resources(self) -> SlaveResources:
        """Detectar recursos disponibles del sistema"""
        cpu_cores = psutil.cpu_count(logical=True)
        memory_gb = psutil.virtual_memory().total / (1024**3)
        disk_gb = psutil.disk_usage('/').free / (1024**3)
        
        # Calcular max_agents basado en recursos
        # Fórmula: 1 agente por core, ajustado por RAM disponible
        max_by_cpu = cpu_cores
        max_by_ram = int(memory_gb / 0.5)  # 0.5GB por agente
        max_agents = min(max_by_cpu, max_by_ram, 20)  # Cap at 20
        
        return SlaveResources(
            cpu_cores=cpu_cores,
            memory_gb=memory_gb,
            disk_gb=disk_gb,
            max_agents=max_agents
        )
    
    def _get_version_info(self) -> Dict[str, str]:
        """Obtener información de versión Git"""
        try:
            # Git branch
            branch = subprocess.check_output(
                ["git", "branch", "--show-current"],
                text=True,
                cwd=Path(__file__).parent.parent.parent
            ).strip()
            
            # Git commit
            commit = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                text=True,
                cwd=Path(__file__).parent.parent.parent
            ).strip()
            
            # Python version
            import sys
            python_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            
            return {
                "git_branch": branch,
                "git_commit": commit,
                "python_version": python_ver,
                "d8_version": f"{branch}@{commit}"
            }
        except Exception as e:
            logger.warning(f"Could not get version info: {e}")
            return {
                "git_branch": "unknown",
                "git_commit": "unknown",
                "python_version": "unknown",
                "d8_version": "unknown"
            }
    
    def register(self) -> bool:
        """Registrarse con orchestrator"""
        try:
            response = requests.post(
                f"{self.orchestrator_url}/api/slaves/register",
                json={
                    "slave_id": self.slave_id,
                    "device_type": self._detect_device_type(),
                    "resources": {
                        "cpu_cores": self.resources.cpu_cores,
                        "memory_gb": self.resources.memory_gb,
                        "disk_gb": self.resources.disk_gb,
                        "max_agents": self.resources.max_agents
                    },
                    "capabilities": {
                        "llm_providers": ["groq"] + (["gemini"] if self.gemini_api_key else []),
                        "gpu": self._has_gpu()
                    },
                    "version": self.version_info
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
    
    def _detect_device_type(self) -> str:
        """Detectar tipo de dispositivo"""
        # Simple heuristic basado en hardware
        if self.resources.cpu_cores <= 4 and self.resources.memory_gb <= 4:
            return "raspberry_pi_4"
        elif self.resources.cpu_cores >= 12 and self.resources.memory_gb >= 32:
            return "server_high_end"
        elif self.resources.cpu_cores >= 8:
            return "pc_desktop"
        else:
            return "generic_device"
    
    def _has_gpu(self) -> bool:
        """Detectar si tiene GPU (NVIDIA)"""
        try:
            subprocess.check_output(["nvidia-smi"], stderr=subprocess.DEVNULL)
            return True
        except:
            return False
    
    def start(self):
        """Iniciar loop principal del slave"""
        if not self.register():
            logger.error("Failed to register, exiting")
            return
        
        self.active = True
        logger.info(f"🚀 SlaveNode started, heartbeat every {self.heartbeat_interval}s")
        
        last_heartbeat = time.time()
        
        while self.active:
            try:
                current_time = time.time()
                
                # Heartbeat periódico
                if current_time - last_heartbeat >= self.heartbeat_interval:
                    self._send_heartbeat()
                    last_heartbeat = current_time
                
                # Chequear comandos del orchestrator
                self._check_commands()
                
                # Monitorear salud de agentes
                self._monitor_agents()
                
                # Sleep pequeño para no saturar CPU
                time.sleep(2)
                    
            except KeyboardInterrupt:
                logger.info("🛑 Shutting down...")
                self.active = False
                self._shutdown()
                break
                
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                time.sleep(5)
    
    def _send_heartbeat(self):
        """Enviar heartbeat al orchestrator"""
        try:
            # Actualizar métricas de agentes
            self._update_agent_metrics()
            
            response = requests.post(
                f"{self.orchestrator_url}/api/slaves/heartbeat",
                json={
                    "slave_id": self.slave_id,
                    "status": "online",
                    "agents_count": len(self.agents),
                    "agents_status": {
                        agent_id: {
                            "status": agent.status,
                            "cpu_percent": agent.cpu_percent,
                            "memory_mb": agent.memory_mb,
                            "actions_executed": agent.actions_executed,
                            "errors": agent.errors
                        }
                        for agent_id, agent in self.agents.items()
                    },
                    "resources_usage": {
                        "cpu_percent": psutil.cpu_percent(interval=1),
                        "memory_percent": psutil.virtual_memory().percent,
                        "disk_percent": psutil.disk_usage('/').percent
                    },
                    "version": self.version_info
                },
                timeout=5
            )
            
            if response.status_code != 200:
                logger.warning(f"⚠️ Heartbeat failed: {response.text}")
                
        except Exception as e:
            logger.debug(f"Heartbeat failed: {e}")
    
    def _check_commands(self):
        """Chequear si hay comandos pendientes del orchestrator"""
        try:
            response = requests.get(
                f"{self.orchestrator_url}/api/slaves/{self.slave_id}/commands",
                timeout=3
            )
            
            if response.status_code == 200:
                commands = response.json().get('commands', [])
                
                for cmd in commands:
                    self._execute_command(cmd)
                    
        except Exception as e:
            logger.debug(f"Check commands failed: {e}")
    
    def _execute_command(self, command: Dict[str, Any]):
        """Ejecutar comando del orchestrator"""
        cmd_type = command.get('type')
        
        if cmd_type == 'deploy_agent':
            self._deploy_agent(command['data'])
        elif cmd_type == 'destroy_agent':
            self._destroy_agent(command['data']['agent_id'])
        elif cmd_type == 'update_agent':
            self._update_agent(command['data']['agent_id'], command['data']['genome'])
        else:
            logger.warning(f"⚠️ Unknown command type: {cmd_type}")
    
    def _deploy_agent(self, agent_data: Dict[str, Any]):
        """Crear nuevo agente en este slave"""
        agent_id = agent_data['agent_id']
        genome = agent_data['genome']
        
        logger.info(f"🚀 Deploying agent: {agent_id}")
        
        # Verificar que no exista ya
        if agent_id in self.agents:
            logger.warning(f"⚠️ Agent {agent_id} already exists")
            return
        
        # Verificar capacidad
        if len(self.agents) >= self.resources.max_agents:
            logger.error(f"❌ Max agents capacity reached ({self.resources.max_agents})")
            return
        
        try:
            # Crear instancia del agente
            # TODO: Implementar creación real de BaseAgent
            agent = AgentInstance(
                agent_id=agent_id,
                genome=genome,
                status="active"
            )
            
            self.agents[agent_id] = agent
            
            logger.info(f"✅ Agent {agent_id} deployed successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy agent {agent_id}: {e}")
    
    def _destroy_agent(self, agent_id: str):
        """Destruir agente existente"""
        logger.info(f"🗑️ Destroying agent: {agent_id}")
        
        if agent_id not in self.agents:
            logger.warning(f"⚠️ Agent {agent_id} not found")
            return
        
        try:
            agent = self.agents[agent_id]
            
            # TODO: Cleanup resources, stop threads, etc.
            
            del self.agents[agent_id]
            
            logger.info(f"✅ Agent {agent_id} destroyed")
            
        except Exception as e:
            logger.error(f"❌ Failed to destroy agent {agent_id}: {e}")
    
    def _update_agent(self, agent_id: str, new_genome: Dict[str, Any]):
        """Actualizar genoma de agente (post-evolución)"""
        logger.info(f"🔄 Updating agent: {agent_id}")
        
        if agent_id not in self.agents:
            logger.warning(f"⚠️ Agent {agent_id} not found")
            return
        
        try:
            self.agents[agent_id].genome = new_genome
            
            logger.info(f"✅ Agent {agent_id} updated")
            
        except Exception as e:
            logger.error(f"❌ Failed to update agent {agent_id}: {e}")
    
    def _monitor_agents(self):
        """Monitorear salud de agentes activos"""
        for agent_id, agent in list(self.agents.items()):
            try:
                # TODO: Check if agent process is alive
                # TODO: Check if agent is responding
                # TODO: Update status accordingly
                pass
            except Exception as e:
                logger.error(f"❌ Error monitoring agent {agent_id}: {e}")
    
    def _update_agent_metrics(self):
        """Actualizar métricas de CPU/memoria de cada agente"""
        for agent in self.agents.values():
            try:
                # TODO: Get real metrics from agent process
                agent.cpu_percent = 0.0
                agent.memory_mb = 0.0
            except:
                pass
    
    def _shutdown(self):
        """Cierre limpio del slave"""
        logger.info("🛑 Shutting down all agents...")
        
        for agent_id in list(self.agents.keys()):
            self._destroy_agent(agent_id)
        
        # Notificar al orchestrator
        try:
            requests.post(
                f"{self.orchestrator_url}/api/slaves/{self.slave_id}/unregister",
                timeout=5
            )
            logger.info("👋 Unregistered from orchestrator")
        except:
            pass
        
        logger.info("✅ Shutdown complete")


if __name__ == "__main__":
    # Cargar configuración desde .env
    orchestrator_url = os.getenv("ORCHESTRATOR_URL", "http://localhost:7001")
    slave_id = os.getenv("SLAVE_ID", f"slave-{int(time.time())}")
    groq_api_key = os.getenv("GROQ_API_KEY")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not groq_api_key:
        logger.error("❌ GROQ_API_KEY not found in .env")
        exit(1)
    
    slave = SlaveNode(
        orchestrator_url=orchestrator_url,
        slave_id=slave_id,
        groq_api_key=groq_api_key,
        gemini_api_key=gemini_api_key
    )
    
    slave.start()
