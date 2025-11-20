#!/usr/bin/env python3
"""
🚀 D8 Sistema Autónomo - FASE 3
Lanzamiento del sistema completo autónomo 24/7
"""

import subprocess
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/d8_autonomous.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class D8AutonomousSystem:
    """Gestor del sistema autónomo completo"""
    
    def __init__(self):
        self.processes = {}
        self.project_root = Path(__file__).parent.parent
        
    def start_component(self, name, script_path):
        """Iniciar un componente del sistema"""
        logger.info(f"🚀 Starting {name}...")
        
        try:
            # Ejecutar en background
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.processes[name] = process
            logger.info(f"✅ {name} started (PID: {process.pid})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start {name}: {e}")
            return False
    
    def check_health(self):
        """Verificar salud de todos los componentes"""
        logger.info("\n" + "="*60)
        logger.info("💊 HEALTH CHECK")
        logger.info("="*60)
        
        all_healthy = True
        
        for name, process in self.processes.items():
            if process.poll() is None:
                logger.info(f"✅ {name}: RUNNING (PID: {process.pid})")
            else:
                logger.error(f"❌ {name}: STOPPED")
                all_healthy = False
        
        logger.info("="*60 + "\n")
        return all_healthy
    
    def stop_all(self):
        """Detener todos los componentes"""
        logger.info("\n🛑 Stopping all components...")
        
        for name, process in self.processes.items():
            if process.poll() is None:
                logger.info(f"   Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    logger.info(f"   ✅ {name} stopped")
                except subprocess.TimeoutExpired:
                    process.kill()
                    logger.warning(f"   ⚠️ {name} force killed")
    
    def start_all(self):
        """Iniciar todos los componentes del sistema"""
        logger.info("="*60)
        logger.info("🤖 D8 AUTONOMOUS SYSTEM - FASE 3")
        logger.info("="*60)
        logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*60 + "\n")
        
        components = [
            ("Niche Discovery Daemon", "scripts/daemons/niche_discovery_daemon.py"),
            ("Congress Daemon", "scripts/daemons/congress_daemon.py"),
            ("Evolution Daemon", "scripts/daemons/evolution_daemon.py"),
            ("Monitoring Dashboard", "app/monitoring/dashboard.py"),
            ("Self-Healing Monitor", "app/self_healing/monitor.py"),
        ]
        
        for name, script in components:
            script_path = self.project_root / script
            
            if not script_path.exists():
                logger.error(f"❌ Script not found: {script}")
                continue
            
            success = self.start_component(name, script_path)
            
            if not success:
                logger.error(f"Failed to start {name}, aborting...")
                self.stop_all()
                return False
            
            time.sleep(2)  # Dar tiempo para inicializar
        
        logger.info("\n" + "="*60)
        logger.info("✅ ALL SYSTEMS OPERATIONAL")
        logger.info("="*60)
        logger.info("\n📊 Dashboard: http://localhost:7500")
        logger.info("📝 Logs: data/logs/")
        logger.info("\n⚠️  Press Ctrl+C to stop all systems\n")
        
        return True
    
    def monitor_loop(self):
        """Loop de monitoreo continuo"""
        try:
            while True:
                time.sleep(300)  # Check every 5 minutes
                
                if not self.check_health():
                    logger.warning("⚠️ Some components are not healthy")
                    # TODO: Intentar restart automático
                    
        except KeyboardInterrupt:
            logger.info("\n\n🛑 Shutdown signal received")
            self.stop_all()
            logger.info("✅ All systems stopped cleanly")


def main():
    """Main entry point"""
    system = D8AutonomousSystem()
    
    # Iniciar todos los componentes
    success = system.start_all()
    
    if not success:
        logger.error("❌ System startup failed")
        sys.exit(1)
    
    # Monitorear continuamente
    system.monitor_loop()


if __name__ == "__main__":
    main()
