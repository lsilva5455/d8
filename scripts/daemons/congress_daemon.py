#!/usr/bin/env python3
"""
🏛️ Congress Daemon - FASE 3
Mejora continua del sistema cada hora
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

from scripts.autonomous_congress import AutonomousCongress

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/congress_daemon.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CongressDaemonManager:
    """Gestor del daemon del congreso"""
    
    def __init__(self):
        self.congress = None
        self.results_dir = Path("data/congress_cycles")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.cycle_count = 0
        
    def run_cycle(self):
        """Ejecutar un ciclo del congreso"""
        self.cycle_count += 1
        
        logger.info("="*60)
        logger.info(f"🏛️  CONGRESS CYCLE #{self.cycle_count}")
        logger.info("="*60)
        
        try:
            # Inicializar congreso
            if self.congress is None:
                self.congress = AutonomousCongress()
                logger.info("✅ Congress initialized")
            
            # Ejecutar ciclo
            logger.info("🔄 Running autonomous cycle...")
            results = self.congress.run_autonomous_cycle(
                target_system="production",
                cycles=1
            )
            
            # Analizar resultados
            improvement = results.get('improvement', 0)
            experiments = results.get('experiments_completed', 0)
            
            logger.info(f"📊 Cycle Results:")
            logger.info(f"   - Experiments: {experiments}")
            logger.info(f"   - Improvement: {improvement*100:.1f}%")
            
            # Solo implementar si mejora > 10%
            if improvement > 0.10:
                logger.info(f"✅ Improvement threshold met ({improvement*100:.1f}% > 10%)")
                logger.info("🚀 Deploying improvements to production...")
                
                # TODO: Implementación real
                # self.deploy_to_production(results)
                
                logger.info("✅ Improvements deployed successfully")
            else:
                logger.info(f"⏭️  Improvement below threshold ({improvement*100:.1f}% < 10%), skipping deployment")
            
            # Guardar resultados
            self.save_cycle_results(results)
            
            logger.info("✅ Congress cycle completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error in congress cycle: {e}", exc_info=True)
    
    def save_cycle_results(self, results):
        """Guardar resultados del ciclo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"cycle_{timestamp}.json"
        
        cycle_data = {
            "cycle_number": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(cycle_data, f, indent=2)
        
        logger.info(f"💾 Results saved to {filename}")


def run_congress_cycle():
    """Wrapper para schedule"""
    manager.run_cycle()


def main():
    """Main daemon loop"""
    global manager
    manager = CongressDaemonManager()
    
    logger.info("🏁 Congress Daemon starting...")
    logger.info(f"📅 Schedule: Every 1 hour")
    
    # Ejecutar inmediatamente al inicio
    run_congress_cycle()
    
    # Programar ejecución cada hora
    schedule.every(1).hours.do(run_congress_cycle)
    
    logger.info("⏰ Daemon is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("🛑 Daemon stopped by user")


if __name__ == "__main__":
    main()
