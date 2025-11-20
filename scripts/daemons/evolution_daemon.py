#!/usr/bin/env python3
"""
🧬 Evolution Daemon - FASE 3
Evolución de agentes cada 7 días
"""

import schedule
import time
import logging
from datetime import datetime
from pathlib import Path
import json
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.evolution.darwin import Darwin
from app.economy import RevenueAttributionSystem

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/evolution_daemon.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EvolutionDaemonManager:
    """Gestor del daemon de evolución"""
    
    def __init__(self):
        self.darwin = Darwin()
        self.attribution = RevenueAttributionSystem()
        self.results_dir = Path("data/generations")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.generation_count = 0
        
    def run_evolution(self):
        """Ejecutar ciclo evolutivo completo"""
        self.generation_count += 1
        
        logger.info("="*60)
        logger.info(f"🧬 EVOLUTION CYCLE - Generation #{self.generation_count}")
        logger.info("="*60)
        
        try:
            # 1. Evaluar generación actual
            logger.info("📊 Evaluating current generation...")
            fitness_scores = self.darwin.evaluate_population()
            
            avg_fitness = sum(fitness_scores.values()) / len(fitness_scores) if fitness_scores else 0
            best_agent = max(fitness_scores.items(), key=lambda x: x[1]) if fitness_scores else (None, 0)
            
            logger.info(f"   - Population size: {len(fitness_scores)}")
            logger.info(f"   - Average fitness: {avg_fitness:.2f}")
            logger.info(f"   - Best agent: {best_agent[0]} (fitness: {best_agent[1]:.2f})")
            
            # 2. Selección natural (top 30%)
            logger.info("⚡ Selecting survivors (top 30%)...")
            survival_rate = 0.3
            survivors = self.darwin.select_survivors(
                fitness_scores=fitness_scores,
                survival_rate=survival_rate
            )
            
            logger.info(f"   - Survivors: {len(survivors)}/{len(fitness_scores)}")
            
            # 3. Reproducción
            logger.info("👶 Reproducing new generation...")
            target_size = 20
            next_gen = self.darwin.reproduce(
                parents=survivors,
                target_size=target_size
            )
            
            logger.info(f"   - New generation size: {len(next_gen)}")
            
            # 4. Guardar genomas
            logger.info("💾 Saving generation genomes...")
            self.save_generation(next_gen)
            
            # 5. Distribuir revenue
            logger.info("💰 Distributing revenue...")
            self.distribute_generation_revenue(fitness_scores)
            
            # 6. Desplegar nuevos agentes
            logger.info("🚀 Deploying new generation...")
            # TODO: Implementación real
            # self.deploy_generation(next_gen)
            
            logger.info("✅ Evolution cycle completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error in evolution cycle: {e}", exc_info=True)
    
    def save_generation(self, generation):
        """Guardar genomas de la generación"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        gen_dir = self.results_dir / f"gen_{self.generation_count}_{timestamp}"
        gen_dir.mkdir(parents=True, exist_ok=True)
        
        for i, agent in enumerate(generation):
            genome_file = gen_dir / f"agent_{i:03d}.json"
            
            genome_data = {
                "agent_id": f"agent_{self.generation_count}_{i:03d}",
                "generation": self.generation_count,
                "created_at": datetime.now().isoformat(),
                "genome": agent
            }
            
            with open(genome_file, 'w', encoding='utf-8') as f:
                json.dump(genome_data, f, indent=2)
        
        logger.info(f"💾 Saved {len(generation)} genomes to {gen_dir}")
    
    def distribute_generation_revenue(self, fitness_scores):
        """Distribuir revenue según contribuciones"""
        try:
            # Simular distribución 40/40/20
            total_fitness = sum(fitness_scores.values())
            
            if total_fitness > 0:
                for agent_id, fitness in fitness_scores.items():
                    contribution = (fitness / total_fitness) * 100
                    logger.info(f"   - {agent_id}: {contribution:.1f}% contribution")
            
            # TODO: Implementar distribución real con D8Credits
            # self.attribution.distribute_revenue(...)
            
        except Exception as e:
            logger.error(f"⚠️ Error distributing revenue: {e}")


def run_evolution_cycle():
    """Wrapper para schedule"""
    manager.run_evolution()


def main():
    """Main daemon loop"""
    global manager
    manager = EvolutionDaemonManager()
    
    logger.info("🏁 Evolution Daemon starting...")
    logger.info(f"📅 Schedule: Every 7 days")
    
    # Para testing: ejecutar cada 1 hora
    # schedule.every(1).hours.do(run_evolution_cycle)
    
    # Producción: cada 7 días
    schedule.every(7).days.do(run_evolution_cycle)
    
    logger.info("⏰ Daemon is running. Press Ctrl+C to stop.")
    logger.info("💡 Tip: For testing, change schedule to 1 hour in code")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour
    except KeyboardInterrupt:
        logger.info("🛑 Daemon stopped by user")


if __name__ == "__main__":
    main()
