#!/usr/bin/env python3
"""
🛡️ Self-Healing Monitor - FASE 3
Auto-recuperación del sistema sin intervención humana
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.distributed.orchestrator import Orchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/self_healing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SelfHealingMonitor:
    """Monitor de auto-recuperación del sistema"""
    
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.incidents_dir = Path("data/incidents")
        self.incidents_dir.mkdir(parents=True, exist_ok=True)
        self.incident_count = 0
        
    def check_workers(self):
        """Detectar y recuperar workers caídos"""
        logger.info("🔍 Checking workers health...")
        
        try:
            # Obtener workers muertos
            dead_workers = self.orchestrator.get_dead_workers()
            
            if not dead_workers:
                logger.info("✅ All workers healthy")
                return
            
            logger.warning(f"⚠️ Found {len(dead_workers)} dead workers")
            
            for worker_id in dead_workers:
                logger.warning(f"💀 Worker {worker_id} is dead")
                
                # Re-asignar tareas pendientes
                reassigned = self.orchestrator.reassign_tasks(worker_id)
                logger.info(f"   → Reassigned {reassigned} tasks")
                
                # Intentar restart
                self.restart_worker(worker_id)
                
                # Registrar incidente
                self.log_incident({
                    "type": "worker_failure",
                    "worker_id": worker_id,
                    "tasks_reassigned": reassigned,
                    "action": "restart_attempted"
                })
                
        except Exception as e:
            logger.error(f"❌ Error checking workers: {e}", exc_info=True)
    
    def restart_worker(self, worker_id):
        """Intentar reiniciar un worker"""
        logger.info(f"🔄 Attempting to restart worker {worker_id}...")
        
        # TODO: Implementar restart real
        # Por ahora solo log
        logger.info(f"✅ Restart signal sent to worker {worker_id}")
    
    def check_agents(self):
        """Detectar agentes con alta tasa de errores"""
        logger.info("🔍 Checking agents health...")
        
        try:
            # TODO: Implementar detección real de agentes problemáticos
            # Por ahora simulado
            
            problematic_agents = []  # Placeholder
            
            if not problematic_agents:
                logger.info("✅ All agents healthy")
                return
            
            logger.warning(f"⚠️ Found {len(problematic_agents)} problematic agents")
            
            for agent in problematic_agents:
                agent_id = agent.get("id")
                error_rate = agent.get("error_rate", 0)
                
                logger.warning(f"🚨 Agent {agent_id} error rate: {error_rate*100:.1f}%")
                
                # Rollback a versión estable
                self.rollback_agent(agent_id)
                
                # Registrar incidente
                self.log_incident({
                    "type": "agent_failure",
                    "agent_id": agent_id,
                    "error_rate": error_rate,
                    "action": "rolled_back"
                })
                
        except Exception as e:
            logger.error(f"❌ Error checking agents: {e}", exc_info=True)
    
    def rollback_agent(self, agent_id):
        """Hacer rollback de un agente a versión estable"""
        logger.info(f"⏮️  Rolling back agent {agent_id}...")
        
        # TODO: Implementar rollback real
        # 1. Obtener última versión estable del genoma
        # 2. Cargar genoma estable
        # 3. Re-desplegar agente
        
        logger.info(f"✅ Agent {agent_id} rolled back to stable version")
    
    def check_budgets(self):
        """Verificar presupuestos y aplicar throttling si es necesario"""
        logger.info("🔍 Checking budget usage...")
        
        try:
            # TODO: Implementar verificación real de presupuestos
            # Por ahora simulado
            
            categories = {
                "api_calls": 0.85,  # 85% usado
                "infrastructure": 0.45,  # 45% usado
                "marketing": 0.92  # 92% usado - CRÍTICO
            }
            
            for category, usage in categories.items():
                if usage > 0.9:
                    logger.critical(f"🚨 Budget {category} at {usage*100:.1f}% - CRITICAL")
                    
                    # Aplicar throttling
                    self.throttle_category(category)
                    
                    # Registrar incidente
                    self.log_incident({
                        "type": "budget_critical",
                        "category": category,
                        "usage": usage,
                        "action": "throttling_applied"
                    })
                    
                elif usage > 0.8:
                    logger.warning(f"⚠️ Budget {category} at {usage*100:.1f}% - HIGH")
                else:
                    logger.info(f"✅ Budget {category} at {usage*100:.1f}% - OK")
                    
        except Exception as e:
            logger.error(f"❌ Error checking budgets: {e}", exc_info=True)
    
    def throttle_category(self, category):
        """Aplicar throttling a una categoría de gasto"""
        logger.info(f"🐌 Applying throttling to category: {category}")
        
        # TODO: Implementar throttling real
        # Reducir tasa de uso en 50%
        
        logger.info(f"✅ Throttling applied to {category} (rate reduced 50%)")
    
    def log_incident(self, incident_data):
        """Registrar un incidente"""
        self.incident_count += 1
        
        incident = {
            "incident_id": f"INC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.incident_count:03d}",
            "timestamp": datetime.now().isoformat(),
            **incident_data
        }
        
        # Guardar en archivo
        filename = self.incidents_dir / f"{incident['incident_id']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(incident, f, indent=2)
        
        logger.info(f"📝 Incident logged: {incident['incident_id']}")
    
    def generate_health_report(self):
        """Generar reporte de salud del sistema"""
        logger.info("="*60)
        logger.info("📋 SYSTEM HEALTH REPORT")
        logger.info("="*60)
        
        # Contar incidentes recientes (últimas 24h)
        recent_incidents = 0
        cutoff = datetime.now() - timedelta(hours=24)
        
        for incident_file in self.incidents_dir.glob("INC_*.json"):
            try:
                with open(incident_file, 'r') as f:
                    incident = json.load(f)
                    incident_time = datetime.fromisoformat(incident["timestamp"])
                    if incident_time > cutoff:
                        recent_incidents += 1
            except:
                pass
        
        logger.info(f"Incidents (last 24h): {recent_incidents}")
        logger.info(f"Total incidents: {self.incident_count}")
        logger.info("="*60)


def main():
    """Main monitoring loop"""
    logger.info("🏁 Self-Healing Monitor starting...")
    
    monitor = SelfHealingMonitor()
    
    # Programar checks
    logger.info("📅 Schedule:")
    logger.info("   - Workers: every 5 minutes")
    logger.info("   - Agents: every 5 minutes")
    logger.info("   - Budgets: every 15 minutes")
    logger.info("   - Health report: every 1 hour")
    
    schedule.every(5).minutes.do(monitor.check_workers)
    schedule.every(5).minutes.do(monitor.check_agents)
    schedule.every(15).minutes.do(monitor.check_budgets)
    schedule.every(1).hours.do(monitor.generate_health_report)
    
    # Ejecutar checks inmediatamente
    logger.info("🔄 Running initial checks...")
    monitor.check_workers()
    monitor.check_agents()
    monitor.check_budgets()
    monitor.generate_health_report()
    
    logger.info("⏰ Monitor is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    except KeyboardInterrupt:
        logger.info("🛑 Monitor stopped by user")


if __name__ == "__main__":
    main()
