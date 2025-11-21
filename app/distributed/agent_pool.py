"""
Agent Pool Manager - Gestión Global de Agentes Distribuidos
============================================================
Mantiene registro de qué agente vive en qué slave.
Decide placement de nuevos agentes.
Gestiona migración entre slaves.

Author: D8 System
Date: 2025-11-21
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AgentPlacement:
    """Información de ubicación de un agente"""
    agent_id: str
    slave_id: str
    genome: Dict[str, Any]
    placed_at: float = field(default_factory=lambda: datetime.utcnow().timestamp())
    is_temporary: bool = False  # True si fue movido por fallo de slave original
    original_slave_id: Optional[str] = None  # Si es temporal, dónde vivía originalmente


class AgentPoolManager:
    """
    Gestiona el pool global de agentes distribuidos
    
    Responsabilidades:
    - Mantener registro agent_id → slave_id
    - Decidir placement de nuevos agentes
    - Migrar agentes entre slaves
    - Detectar agentes huérfanos (slave caído)
    - Rebalancear carga
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        # Registry de placements
        self.placements: Dict[str, AgentPlacement] = {}
        
        # Data directory para persistencia
        self.data_dir = data_dir or (Path.home() / "Documents" / "d8_data" / "orchestrator")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load persisted state
        self._load_state()
        
        logger.info("🎯 AgentPoolManager initialized")
        logger.info(f"   Total agents: {len(self.placements)}")
    
    def register_agent(
        self,
        agent_id: str,
        slave_id: str,
        genome: Dict[str, Any],
        is_temporary: bool = False,
        original_slave_id: Optional[str] = None
    ):
        """Registrar nuevo agente en el pool"""
        placement = AgentPlacement(
            agent_id=agent_id,
            slave_id=slave_id,
            genome=genome,
            is_temporary=is_temporary,
            original_slave_id=original_slave_id
        )
        
        self.placements[agent_id] = placement
        self._save_state()
        
        logger.info(f"✅ Agent {agent_id} registered in {slave_id}")
    
    def unregister_agent(self, agent_id: str):
        """Eliminar agente del pool"""
        if agent_id in self.placements:
            del self.placements[agent_id]
            self._save_state()
            logger.info(f"🗑️ Agent {agent_id} unregistered")
    
    def get_agent_location(self, agent_id: str) -> Optional[str]:
        """Obtener slave_id donde vive el agente"""
        placement = self.placements.get(agent_id)
        return placement.slave_id if placement else None
    
    def get_agents_in_slave(self, slave_id: str) -> List[str]:
        """Obtener lista de agentes en un slave específico"""
        return [
            agent_id
            for agent_id, placement in self.placements.items()
            if placement.slave_id == slave_id
        ]
    
    def find_best_slave(
        self,
        available_slaves: Dict[str, Dict[str, Any]],
        agent_requirements: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Encontrar mejor slave para nuevo agente
        
        Args:
            available_slaves: {slave_id: {resources, current_agents, max_agents}}
            agent_requirements: Requisitos del agente (GPU, RAM, etc.)
        
        Returns:
            slave_id del mejor candidato o None
        """
        if not available_slaves:
            return None
        
        # Score cada slave
        scored_slaves = []
        
        for slave_id, slave_info in available_slaves.items():
            # Calcular score basado en:
            # 1. Slots disponibles
            # 2. Carga actual
            # 3. Recursos
            
            current_agents = len(self.get_agents_in_slave(slave_id))
            max_agents = slave_info.get('max_agents', 10)
            available_slots = max_agents - current_agents
            
            if available_slots <= 0:
                continue  # No capacity
            
            # Score: más slots = mejor
            score = available_slots * 100
            
            # Bonus: menos carga actual = mejor
            load_factor = current_agents / max_agents if max_agents > 0 else 1.0
            score += (1.0 - load_factor) * 50
            
            # TODO: Check agent_requirements (GPU, etc.)
            
            scored_slaves.append((slave_id, score))
        
        if not scored_slaves:
            return None
        
        # Retornar el con mejor score
        scored_slaves.sort(key=lambda x: x[1], reverse=True)
        best_slave_id = scored_slaves[0][0]
        
        logger.info(f"🎯 Best slave for placement: {best_slave_id}")
        return best_slave_id
    
    def move_agent(
        self,
        agent_id: str,
        new_slave_id: str,
        is_temporary: bool = False
    ) -> bool:
        """
        Mover agente a otro slave
        
        Args:
            agent_id: ID del agente
            new_slave_id: Slave destino
            is_temporary: Si es movimiento temporal (por fallo)
        
        Returns:
            True si se movió exitosamente
        """
        placement = self.placements.get(agent_id)
        
        if not placement:
            logger.error(f"❌ Agent {agent_id} not found in pool")
            return False
        
        old_slave_id = placement.slave_id
        
        logger.info(f"🔄 Moving agent {agent_id}: {old_slave_id} → {new_slave_id}")
        
        # Actualizar placement
        if is_temporary and not placement.is_temporary:
            # Primera vez que se mueve por fallo
            placement.original_slave_id = old_slave_id
            placement.is_temporary = True
        
        placement.slave_id = new_slave_id
        self._save_state()
        
        logger.info(f"✅ Agent {agent_id} moved successfully")
        return True
    
    def get_temporary_agents(self, original_slave_id: str) -> List[str]:
        """Obtener agentes que fueron movidos temporalmente desde un slave"""
        return [
            agent_id
            for agent_id, placement in self.placements.items()
            if placement.is_temporary and placement.original_slave_id == original_slave_id
        ]
    
    def make_placement_permanent(self, agent_id: str):
        """Convertir placement temporal en permanente"""
        placement = self.placements.get(agent_id)
        
        if placement and placement.is_temporary:
            placement.is_temporary = False
            placement.original_slave_id = None
            self._save_state()
            
            logger.info(f"📌 Agent {agent_id} placement is now permanent")
    
    def get_orphaned_agents(self, dead_slave_id: str) -> List[AgentPlacement]:
        """Obtener agentes que quedaron huérfanos por slave caído"""
        return [
            placement
            for placement in self.placements.values()
            if placement.slave_id == dead_slave_id
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del pool"""
        agents_by_slave = {}
        temporary_count = 0
        
        for placement in self.placements.values():
            slave_id = placement.slave_id
            agents_by_slave[slave_id] = agents_by_slave.get(slave_id, 0) + 1
            
            if placement.is_temporary:
                temporary_count += 1
        
        return {
            "total_agents": len(self.placements),
            "agents_by_slave": agents_by_slave,
            "temporary_placements": temporary_count,
            "permanent_placements": len(self.placements) - temporary_count
        }
    
    def _save_state(self):
        """Persistir estado del pool"""
        try:
            state_file = self.data_dir / "agent_pool.json"
            
            state = {
                agent_id: {
                    "slave_id": p.slave_id,
                    "genome": p.genome,
                    "placed_at": p.placed_at,
                    "is_temporary": p.is_temporary,
                    "original_slave_id": p.original_slave_id
                }
                for agent_id, p in self.placements.items()
            }
            
            state_file.write_text(json.dumps(state, indent=2))
            
        except Exception as e:
            logger.error(f"❌ Failed to save agent pool state: {e}")
    
    def _load_state(self):
        """Cargar estado persistido"""
        try:
            state_file = self.data_dir / "agent_pool.json"
            
            if not state_file.exists():
                return
            
            state = json.loads(state_file.read_text())
            
            for agent_id, data in state.items():
                self.placements[agent_id] = AgentPlacement(
                    agent_id=agent_id,
                    slave_id=data["slave_id"],
                    genome=data["genome"],
                    placed_at=data["placed_at"],
                    is_temporary=data.get("is_temporary", False),
                    original_slave_id=data.get("original_slave_id")
                )
            
            logger.info(f"📂 Loaded {len(self.placements)} agents from persistent state")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load agent pool state: {e}")
