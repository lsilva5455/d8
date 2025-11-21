"""
Darwin Integration with Distributed Orchestrator
=================================================
Wrapper que permite a Darwin trabajar con agentes distribuidos sin
modificar completamente la lógica existente.

ESTRATEGIA:
- Darwin sigue operando con Genomes (solo lógica genética)
- Este módulo traduce: Genome → Agent deployment
- Mantiene compatibilidad con código existente
"""

from typing import List, Optional, Dict, Any
import logging
from dataclasses import dataclass
import requests

from app.evolution.darwin import Genome
from app.distributed.orchestrator import orchestrator

logger = logging.getLogger(__name__)


@dataclass
class DistributedAgentRef:
    """
    Referencia a un agente distribuido
    Reemplaza BaseAgent en contexto evolutivo
    """
    agent_id: str
    genome: Genome
    slave_id: Optional[str] = None
    
    def get_fitness(self) -> float:
        """Get fitness from genome"""
        return self.genome.fitness
    
    def __repr__(self):
        return f"DistributedAgentRef(agent_id={self.agent_id}, fitness={self.genome.fitness:.2f})"


class DistributedDarwinOrchestrator:
    """
    Wrapper que permite a Darwin trabajar con agentes distribuidos
    """
    
    def __init__(self, orchestrator_instance=None):
        """
        Args:
            orchestrator_instance: Instancia de DistributedOrchestrator
                Si None, usa el singleton global
        """
        self.orchestrator = orchestrator_instance or orchestrator
        self.agent_refs: Dict[str, DistributedAgentRef] = {}  # agent_id -> ref
    
    def create_initial_population(self, genomes: List[Genome]) -> List[DistributedAgentRef]:
        """
        Crear población inicial distribuyéndola en slaves
        
        Args:
            genomes: Lista de genomes iniciales
            
        Returns:
            Lista de referencias a agentes distribuidos
        """
        logger.info(f"🧬 Creating initial distributed population: {len(genomes)} agents")
        
        refs = []
        for genome in genomes:
            ref = self._deploy_agent(genome)
            if ref:
                refs.append(ref)
        
        logger.info(f"✅ Population created: {len(refs)}/{len(genomes)} deployed successfully")
        return refs
    
    def evolve_generation(self, current_refs: List[DistributedAgentRef]) -> List[DistributedAgentRef]:
        """
        Evolucionar generación:
        1. Extraer genomes actuales con fitness
        2. Aplicar evolución (crossover/mutation) - esto sigue igual
        3. Destruir agentes viejos
        4. Deployar agentes nuevos con genomes evolucionados
        
        Args:
            current_refs: Referencias a agentes de generación actual
            
        Returns:
            Referencias a nueva generación de agentes
        """
        logger.info(f"🧬 Evolving generation: {len(current_refs)} agents")
        
        # 1. Extraer genomes con fitness actualizado
        genomes = [ref.genome for ref in current_refs]
        
        # 2. Aplicar evolución (ESTO NO CAMBIA - Darwin sigue igual)
        # Nota: Aquí se usaría el EvolutionOrchestrator de Darwin
        # Para este ejemplo, solo incrementamos generación
        for genome in genomes:
            genome.generation += 1
        
        # 3. Destruir agentes viejos
        logger.info("💀 Destroying old generation...")
        for ref in current_refs:
            self.orchestrator.destroy_agent(ref.agent_id)
            del self.agent_refs[ref.agent_id]
        
        # 4. Deployar nueva generación
        logger.info("🚀 Deploying new generation...")
        new_refs = []
        for genome in genomes:
            ref = self._deploy_agent(genome)
            if ref:
                new_refs.append(ref)
        
        logger.info(f"✅ Evolution complete: {len(new_refs)} agents in new generation")
        return new_refs
    
    def update_fitness(self, agent_id: str, fitness: float):
        """
        Actualizar fitness de un agente
        
        Args:
            agent_id: ID del agente
            fitness: Nuevo valor de fitness
        """
        if agent_id in self.agent_refs:
            self.agent_refs[agent_id].genome.fitness = fitness
            logger.info(f"📊 Updated fitness for {agent_id}: {fitness:.2f}")
    
    def get_population_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas de la población distribuida
        
        Returns:
            Dict con estadísticas
        """
        if not self.agent_refs:
            return {
                "population_size": 0,
                "avg_fitness": 0,
                "best_fitness": 0,
                "worst_fitness": 0
            }
        
        fitnesses = [ref.genome.fitness for ref in self.agent_refs.values()]
        
        return {
            "population_size": len(self.agent_refs),
            "avg_fitness": sum(fitnesses) / len(fitnesses),
            "best_fitness": max(fitnesses),
            "worst_fitness": min(fitnesses),
            "generation": list(self.agent_refs.values())[0].genome.generation
        }
    
    def destroy_all_agents(self):
        """Destruir todos los agentes (útil para shutdown)"""
        logger.info(f"💀 Destroying all agents: {len(self.agent_refs)}")
        
        for agent_id in list(self.agent_refs.keys()):
            self.orchestrator.destroy_agent(agent_id)
            del self.agent_refs[agent_id]
        
        logger.info("✅ All agents destroyed")
    
    def _deploy_agent(self, genome: Genome) -> Optional[DistributedAgentRef]:
        """
        Deploy agente con genome dado
        
        Args:
            genome: Genome del agente
            
        Returns:
            Referencia al agente o None si falla
        """
        # Convertir Genome a formato para orchestrator
        genome_dict = {
            "prompt": genome.prompt,
            "fitness": genome.fitness,
            "generation": genome.generation,
            "parent_ids": genome.parent_ids,
            "mutations": genome.mutations,
            "created_at": genome.created_at
        }
        
        # Deployar via orchestrator
        agent_id = self.orchestrator.deploy_agent(genome=genome_dict)
        
        if not agent_id:
            logger.error("❌ Failed to deploy agent (no slaves available?)")
            return None
        
        # Obtener placement info
        placement = self.orchestrator.agent_pool.get_placement(agent_id)
        slave_id = placement.get("slave_id") if placement else None
        
        # Crear referencia
        ref = DistributedAgentRef(
            agent_id=agent_id,
            genome=genome,
            slave_id=slave_id
        )
        
        self.agent_refs[agent_id] = ref
        logger.info(f"✅ Agent deployed: {agent_id} on {slave_id}")
        
        return ref
    
    def get_agent_ref(self, agent_id: str) -> Optional[DistributedAgentRef]:
        """
        Obtener referencia a agente por ID
        
        Args:
            agent_id: ID del agente
            
        Returns:
            Referencia o None si no existe
        """
        return self.agent_refs.get(agent_id)
    
    def get_all_refs(self) -> List[DistributedAgentRef]:
        """
        Obtener todas las referencias a agentes
        
        Returns:
            Lista de referencias
        """
        return list(self.agent_refs.values())


# ============================================
# UTILITY FUNCTIONS
# ============================================

def migrate_local_to_distributed(local_agents: List[Any]) -> List[DistributedAgentRef]:
    """
    Migrar agentes locales (BaseAgent) a distribuidos
    
    Args:
        local_agents: Lista de BaseAgent instancias locales
        
    Returns:
        Lista de DistributedAgentRef
    """
    darwin_orch = DistributedDarwinOrchestrator()
    
    # Extraer genomes
    genomes = [agent.genome for agent in local_agents]
    
    # Crear población distribuida
    refs = darwin_orch.create_initial_population(genomes)
    
    logger.info(f"✅ Migrated {len(refs)}/{len(local_agents)} agents to distributed")
    return refs


def create_initial_genomes(base_prompt: str, count: int, generation: int = 0) -> List[Genome]:
    """
    Helper para crear genomes iniciales con variaciones
    
    Args:
        base_prompt: Prompt base
        count: Cuántos genomes crear
        generation: Número de generación inicial
        
    Returns:
        Lista de Genomes
    """
    genomes = []
    
    for i in range(count):
        # Crear variación del prompt
        prompt = f"{base_prompt}\n\n# Agent #{i}: Focus on {'innovation' if i % 2 == 0 else 'optimization'}"
        
        genome = Genome(
            prompt=prompt,
            fitness=0.0,
            generation=generation,
            parent_ids=[],
            mutations=[]
        )
        genomes.append(genome)
    
    return genomes
