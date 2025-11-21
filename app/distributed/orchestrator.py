"""
Orchestrator Service (runs on Master - Raspberry Pi)
Manages distributed slave nodes and agent pool
REFACTORED: Workers → Slaves hosting D8 Agents
"""

from flask import Blueprint, request, jsonify
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time
import uuid
import logging
import threading
from datetime import datetime, timedelta

# Import new components
from app.distributed.agent_pool import AgentPoolManager
from app.distributed.overbooking_optimizer import OverbookingOptimizer

logger = logging.getLogger(__name__)

# Blueprint for orchestrator endpoints
orchestrator_bp = Blueprint('orchestrator', __name__, url_prefix='/api/slaves')


@dataclass
class Slave:
    """Registered slave node (host de agentes)"""
    slave_id: str
    device_type: str  # raspberry_pi_4, pc_desktop, server_high_end, etc.
    resources: Dict[str, Any]  # cpu_cores, memory_gb, max_agents
    capabilities: Dict[str, Any]  # llm_providers, gpu
    status: str  # online, offline
    last_heartbeat: float
    
    # Version info
    git_branch: str = "unknown"
    git_commit: str = "unknown"
    python_version: str = "unknown"
    
    # Stats
    agents_registered: int = 0
    agents_active: int = 0
    
    # Downtime tracking
    went_offline_at: Optional[float] = None


@dataclass
class SlaveCommand:
    """Command pendiente para un slave"""
    command_id: str
    slave_id: str
    type: str  # deploy_agent, destroy_agent, update_agent
    data: Dict[str, Any]
    created_at: float = field(default_factory=time.time)
    status: str = "pending"  # pending, sent, completed, failed


class DistributedOrchestrator:
    """
    Orchestrator refactorizado para agentes D8 distribuidos
    
    Responsabilidades:
    - Registro de slaves (no workers)
    - Gestión de agent pool global
    - Placement de nuevos agentes
    - Detección y recuperación de slaves caídos
    - Overbooking adaptativo
    """
    
    def __init__(self, start_background_threads=True):
        # Slave registry
        self.slaves: Dict[str, Slave] = {}
        
        # Agent pool manager
        self.agent_pool = AgentPoolManager()
        
        # Overbooking optimizer
        self.overbooking = OverbookingOptimizer()
        
        # Command queue por slave
        self.commands: Dict[str, List[SlaveCommand]] = {}
        
        # Lock para thread safety
        self.lock = threading.Lock()
        
        # Background threads
        self.active = True
        self.health_thread = None
        self.recovery_thread = None
        
        logger.info("🎯 Distributed Orchestrator initialized (Agent Pool Mode)")
        logger.info(f"   Agents in pool: {len(self.agent_pool.placements)}")
        
        # Start background threads if requested
        if start_background_threads:
            self.start_background_threads()
    
    def start_background_threads(self):
        """Start health and recovery background threads"""
        if self.health_thread is None or not self.health_thread.is_alive():
            self.health_thread = threading.Thread(target=self._health_monitoring_loop, daemon=True)
            self.health_thread.start()
            logger.info("🔄 Health monitoring thread started")
        
        if self.recovery_thread is None or not self.recovery_thread.is_alive():
            self.recovery_thread = threading.Thread(target=self._recovery_loop, daemon=True)
            self.recovery_thread.start()
            logger.info("🔄 Recovery thread started")
    
    def stop_background_threads(self):
        """Stop background threads"""
        self.active = False
        logger.info("⏸️  Background threads stopped")
    
    def register_slave(
        self,
        slave_id: str,
        device_type: str,
        resources: Dict[str, Any],
        capabilities: Dict[str, Any],
        version: Dict[str, str]
    ) -> bool:
        """Registrar nuevo slave"""
        with self.lock:
            self.slaves[slave_id] = Slave(
                slave_id=slave_id,
                device_type=device_type,
                resources=resources,
                capabilities=capabilities,
                status="online",
                last_heartbeat=time.time(),
                git_branch=version.get("git_branch", "unknown"),
                git_commit=version.get("git_commit", "unknown"),
                python_version=version.get("python_version", "unknown")
            )
            
            # Inicializar queue de comandos
            if slave_id not in self.commands:
                self.commands[slave_id] = []
        
        logger.info(f"✅ Slave registered: {slave_id} ({device_type})")
        logger.info(f"   Resources: {resources}")
        logger.info(f"   Version: {version.get('git_branch')}@{version.get('git_commit')}")
        logger.info(f"   Total slaves: {len(self.slaves)}")
        return True
    
    def unregister_slave(self, slave_id: str):
        """Desregistrar slave"""
        with self.lock:
            if slave_id in self.slaves:
                del self.slaves[slave_id]
                logger.info(f"👋 Slave unregistered: {slave_id}")
    
    def update_slave_heartbeat(
        self,
        slave_id: str,
        agents_status: Dict[str, Dict[str, Any]],
        resources_usage: Dict[str, float],
        version: Dict[str, str]
    ):
        """Actualizar heartbeat de slave"""
        with self.lock:
            slave = self.slaves.get(slave_id)
            
            if not slave:
                logger.warning(f"⚠️ Heartbeat from unknown slave: {slave_id}")
                return
            
            # Update heartbeat
            slave.last_heartbeat = time.time()
            slave.status = "online"
            
            # Si estaba offline, registrar que volvió
            if slave.went_offline_at:
                downtime = time.time() - slave.went_offline_at
                logger.info(f"🔄 Slave {slave_id} back online (downtime: {downtime/60:.1f}min)")
                slave.went_offline_at = None
            
            # Update agent counts
            slave.agents_registered = len(agents_status)
            slave.agents_active = sum(
                1 for status in agents_status.values()
                if status.get('status') in ['active', 'busy']
            )
            
            # Record overbooking sample
            self.overbooking.record_sample(
                device_type=slave.device_type,
                agents_registered=slave.agents_registered,
                agents_active=slave.agents_active,
                cpu_percent=resources_usage.get('cpu_percent', 0),
                memory_percent=resources_usage.get('memory_percent', 0)
            )
    
    # ============================================
    # AGENT MANAGEMENT
    # ============================================
    
    def deploy_agent(self, genome: Dict[str, Any]) -> Optional[str]:
        """
        Deployar nuevo agente en el mejor slave disponible
        
        Returns:
            agent_id si exitoso, None si no hay slaves disponibles
        """
        # Construir available_slaves dict para agent_pool
        available_slaves = {}
        with self.lock:
            for slave_id, slave in self.slaves.items():
                if slave.status == "online":
                    available_slaves[slave_id] = {
                        "resources": slave.resources,
                        "current_agents": slave.agents_registered,
                        "max_agents": slave.resources.get('max_agents', 10)
                    }
        
        # Encontrar mejor slave según agent pool
        best_slave_id = self.agent_pool.find_best_slave(available_slaves)
        
        if not best_slave_id:
            logger.error("❌ No slaves available for agent deployment")
            return None
        
        # Generar agent_id
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        
        # Registrar en pool (reserva slot)
        self.agent_pool.register_agent(agent_id, best_slave_id, genome)
        
        # Enviar comando al slave
        command = {
            "type": "deploy_agent",
            "agent_id": agent_id,
            "genome": genome
        }
        
        with self.lock:
            if best_slave_id not in self.commands:
                self.commands[best_slave_id] = []
            self.commands[best_slave_id].append(command)
        
        logger.info(f"🚀 Agent deployment scheduled: {agent_id} → {best_slave_id}")
        return agent_id
    
    def destroy_agent(self, agent_id: str) -> bool:
        """
        Destruir agente existente
        
        Returns:
            True si comando enviado, False si agente no existe
        """
        # Buscar en pool
        placement = self.agent_pool.get_placement(agent_id)
        
        if not placement:
            logger.warning(f"⚠️ Agent not found in pool: {agent_id}")
            return False
        
        slave_id = placement["slave_id"]
        
        # Enviar comando al slave
        command = {
            "type": "destroy_agent",
            "agent_id": agent_id
        }
        
        with self.lock:
            if slave_id not in self.commands:
                self.commands[slave_id] = []
            self.commands[slave_id].append(command)
        
        # Remover del pool
        self.agent_pool.unregister_agent(agent_id)
        
        logger.info(f"💀 Agent destruction scheduled: {agent_id} (was on {slave_id})")
        return True
    
    def update_agent_genome(self, agent_id: str, genome: Dict[str, Any]) -> bool:
        """
        Actualizar genome de agente existente
        
        Returns:
            True si comando enviado, False si agente no existe
        """
        # Buscar en pool
        placement = self.agent_pool.get_placement(agent_id)
        
        if not placement:
            logger.warning(f"⚠️ Agent not found in pool: {agent_id}")
            return False
        
        slave_id = placement["slave_id"]
        
        # Enviar comando al slave
        command = {
            "type": "update_agent",
            "agent_id": agent_id,
            "genome": genome
        }
        
        with self.lock:
            if slave_id not in self.commands:
                self.commands[slave_id] = []
            self.commands[slave_id].append(command)
        
        # Actualizar en pool
        self.agent_pool.update_agent_genome(agent_id, genome)
        
        logger.info(f"🔄 Agent genome update scheduled: {agent_id} on {slave_id}")
        return True
    
    def get_commands_for_slave(self, slave_id: str) -> List[Dict[str, Any]]:
        """
        Obtener comandos pendientes para un slave y limpiar la queue
        
        Returns:
            Lista de comandos pendientes
        """
        with self.lock:
            commands = self.commands.get(slave_id, [])
            self.commands[slave_id] = []  # Clear queue
            return commands
    
    # ============================================
    # STATS & QUERIES
    # ============================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        with self.lock:
            online_slaves = [s for s in self.slaves.values() if s.status == "online"]
            
            # Calcular capacidad total vs uso
            total_capacity = sum(
                s.resources.get('cpu_cores', 0) * 
                self.overbooking.get_overbooking_factor(s.device_type)
                for s in online_slaves
            )
            
            total_agents = len(self.agent_pool.placements)
            
            # Version compliance (inline para evitar deadlock)
            expected_branch = "docker-workers"
            compliant = []
            non_compliant = []
            for slave_id, slave in self.slaves.items():
                if slave.git_branch == expected_branch:
                    compliant.append(slave_id)
                else:
                    non_compliant.append({
                        "slave_id": slave_id,
                        "current_branch": slave.git_branch,
                        "expected_branch": expected_branch
                    })
            
            version_compliance = {
                "expected_branch": expected_branch,
                "compliant_count": len(compliant),
                "non_compliant_count": len(non_compliant),
                "non_compliant_slaves": non_compliant
            }
            
            return {
                "cluster": {
                    "slaves_total": len(self.slaves),
                    "slaves_online": len(online_slaves),
                    "slaves_by_type": self._count_by_type([s.device_type for s in self.slaves.values()])
                },
                "agents": {
                    "total": total_agents,
                    "active": sum(s.agents_active for s in online_slaves),
                    "registered": sum(s.agents_registered for s in online_slaves),
                    "orphaned": len(self.agent_pool.get_orphaned_agents(self.slaves))
                },
                "capacity": {
                    "theoretical_slots": total_capacity,
                    "used_slots": total_agents,
                    "utilization_percent": (total_agents / total_capacity * 100) if total_capacity > 0 else 0
                },
                "overbooking": {
                    device_type: self.overbooking.get_overbooking_factor(device_type)
                    for device_type in set(s.device_type for s in self.slaves.values())
                },
                "version_compliance": version_compliance
            }
    
    def get_slaves(self) -> Dict[str, Slave]:
        """Get all registered slaves"""
        with self.lock:
            return dict(self.slaves)
    
    def get_agent_placements(self) -> Dict[str, Dict[str, Any]]:
        """Get all agent placements"""
        return dict(self.agent_pool.placements)
    
    # ============================================
    # BACKGROUND MONITORING THREADS
    # ============================================
    
    def _health_monitoring_loop(self):
        """
        Thread que monitorea health de slaves y marca offline si no responden
        """
        while self.active:
            time.sleep(30)  # Check every 30s
            
            current_time = time.time()
            timeout = 60  # 60s sin heartbeat = offline
            
            with self.lock:
                for slave_id, slave in self.slaves.items():
                    if current_time - slave.last_heartbeat > timeout:
                        if slave.status == "online":
                            # Marcar como offline
                            slave.status = "offline"
                            slave.went_offline_at = current_time
                            
                            logger.warning(f"⚠️ Slave went offline: {slave_id}")
                            
                            # Trigger recovery check
                            self._check_recovery_needed(slave_id, slave)
    
    def _recovery_loop(self):
        """
        Thread que maneja recovery de agentes huérfanos
        """
        while self.active:
            time.sleep(60)  # Check every minute
            
            # Obtener agentes huérfanos
            orphaned = self.agent_pool.get_orphaned_agents(self.slaves)
            
            if not orphaned:
                continue
            
            logger.info(f"🔍 Found {len(orphaned)} orphaned agents, evaluating recovery...")
            
            for agent_id in orphaned:
                placement = self.agent_pool.get_placement(agent_id)
                if not placement:
                    continue
                
                old_slave_id = placement["slave_id"]
                old_slave = self.slaves.get(old_slave_id)
                
                if not old_slave:
                    # Slave completamente desaparecido, recovery inmediato
                    self._recover_agent_permanent(agent_id, placement)
                    continue
                
                # Check downtime
                if old_slave.went_offline_at:
                    downtime = time.time() - old_slave.went_offline_at
                    downtime_hours = downtime / 3600
                    
                    if downtime_hours < 48:
                        # Temporary recovery
                        logger.info(f"⏳ Agent {agent_id}: temporary recovery (downtime: {downtime_hours:.1f}h)")
                        self._recover_agent_temporary(agent_id, placement, old_slave_id)
                    else:
                        # Permanent restructuring
                        logger.info(f"🔄 Agent {agent_id}: permanent restructuring (downtime: {downtime_hours:.1f}h)")
                        self._recover_agent_permanent(agent_id, placement)
    
    def _check_recovery_needed(self, slave_id: str, slave: Slave):
        """
        Verificar si se necesita recovery inmediato cuando slave cae
        """
        # Por ahora solo log, recovery loop lo manejará
        agents_count = slave.agents_registered
        if agents_count > 0:
            logger.warning(f"⚠️ {agents_count} agents affected on offline slave {slave_id}")
    
    def _recover_agent_temporary(self, agent_id: str, placement: Dict, original_slave_id: str):
        """
        Recovery temporal: mover agente a otro slave pero mantener registro del original
        """
        # Construir available_slaves
        available_slaves = {}
        with self.lock:
            for slave_id, slave in self.slaves.items():
                if slave.status == "online":
                    available_slaves[slave_id] = {
                        "resources": slave.resources,
                        "current_agents": slave.agents_registered,
                        "max_agents": slave.resources.get('max_agents', 10)
                    }
        
        # Buscar slave temporal
        temp_slave_id = self.agent_pool.find_best_slave(available_slaves)
        
        if not temp_slave_id:
            logger.error(f"❌ No slaves available for temporary recovery of {agent_id}")
            return
        
        # Mover agente
        success = self.agent_pool.move_agent(
            agent_id=agent_id,
            new_slave_id=temp_slave_id,
            reason="temporary_recovery"
        )
        
        if success:
            # Enviar comando de deploy al nuevo slave
            command = {
                "type": "deploy_agent",
                "agent_id": agent_id,
                "genome": placement.get("genome", {}),
                "is_recovery": True,
                "original_slave": original_slave_id
            }
            
            with self.lock:
                if temp_slave_id not in self.commands:
                    self.commands[temp_slave_id] = []
                self.commands[temp_slave_id].append(command)
            
            logger.info(f"✅ Temporary recovery: {agent_id} → {temp_slave_id} (waiting for {original_slave_id})")
    
    def _recover_agent_permanent(self, agent_id: str, placement: Dict):
        """
        Recovery permanente: mover agente definitivamente y olvidar slave original
        """
        # Construir available_slaves
        available_slaves = {}
        with self.lock:
            for slave_id, slave in self.slaves.items():
                if slave.status == "online":
                    available_slaves[slave_id] = {
                        "resources": slave.resources,
                        "current_agents": slave.agents_registered,
                        "max_agents": slave.resources.get('max_agents', 10)
                    }
        
        # Buscar nuevo slave permanente
        new_slave_id = self.agent_pool.find_best_slave(available_slaves)
        
        if not new_slave_id:
            logger.error(f"❌ No slaves available for permanent recovery of {agent_id}")
            return
        
        # Mover agente
        success = self.agent_pool.move_agent(
            agent_id=agent_id,
            new_slave_id=new_slave_id,
            reason="permanent_recovery"
        )
        
        if success:
            # Enviar comando de deploy
            command = {
                "type": "deploy_agent",
                "agent_id": agent_id,
                "genome": placement.get("genome", {}),
                "is_recovery": True,
                "permanent": True
            }
            
            with self.lock:
                if new_slave_id not in self.commands:
                    self.commands[new_slave_id] = []
                self.commands[new_slave_id].append(command)
            
            logger.info(f"✅ Permanent recovery: {agent_id} → {new_slave_id}")
    
    # ============================================
    # HELPER METHODS
    # ============================================
    
    def _count_by_type(self, items: List[str]) -> Dict[str, int]:
        """Count items by type"""
        counts = {}
        for item in items:
            counts[item] = counts.get(item, 0) + 1
        return counts
    
    def _check_version_compliance(self) -> Dict[str, Any]:
        """
        Verificar que todos los slaves estén en la branch correcta
        """
        expected_branch = "docker-workers"
        
        with self.lock:
            compliant = []
            non_compliant = []
            
            for slave_id, slave in self.slaves.items():
                if slave.git_branch == expected_branch:
                    compliant.append(slave_id)
                else:
                    non_compliant.append({
                        "slave_id": slave_id,
                        "current_branch": slave.git_branch,
                        "expected_branch": expected_branch
                    })
            
            return {
                "expected_branch": expected_branch,
                "compliant_count": len(compliant),
                "non_compliant_count": len(non_compliant),
                "non_compliant_slaves": non_compliant
            }


# ============================================
# GLOBAL INSTANCE (used by orchestrator_app.py)
# ============================================
orchestrator = DistributedOrchestrator()

