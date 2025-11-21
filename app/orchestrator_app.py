"""
D8 Orchestrator Flask Application - REFACTORED
===============================================
API REST para gestión de slaves y agentes distribuidos.

NUEVO MODELO: Slaves hosting D8 Agents (no más workers/tasks)

Endpoints:
    # Slave Management
    POST   /api/slaves/register                - Registrar slave
    POST   /api/slaves/{id}/heartbeat          - Heartbeat de slave
    POST   /api/slaves/{id}/unregister         - Desregistrar slave
    GET    /api/slaves/{id}/commands           - Obtener comandos para slave
    GET    /api/slaves/list                    - Listar slaves
    
    # Agent Management
    POST   /api/agents/deploy                  - Deploy nuevo agente
    POST   /api/agents/{id}/destroy            - Destruir agente
    POST   /api/agents/{id}/update_genome      - Actualizar genome
    GET    /api/agents/placements              - Ver distribución de agentes
    
    # Dashboard & Monitoring
    GET    /api/cluster/stats                  - Estadísticas del cluster
    GET    /api/cluster/dashboard              - Dashboard completo
    GET    /health                             - Health check
    
    # LLM Manager
    GET    /api/llm/health                     - Estado LLM Fallback Manager
"""

from flask import Flask, request, jsonify
from app.distributed.orchestrator import DistributedOrchestrator
import logging
from datetime import datetime
from typing import Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_orchestrator_app() -> Flask:
    """Factory para crear aplicación Flask del orchestrator"""
    
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    
    # Instancia global del orchestrator
    orchestrator = DistributedOrchestrator()
    
    # ==========================================
    # HEALTH CHECK
    # ==========================================
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        stats = orchestrator.get_stats()
        
        return jsonify({
            "status": "healthy",
            "service": "d8-orchestrator",
            "timestamp": datetime.utcnow().isoformat(),
            "slaves_online": stats['cluster']['slaves_online'],
            "agents_total": stats['agents']['total'],
            "agents_active": stats['agents']['active']
        })
    
    # ==========================================
    # SLAVE MANAGEMENT
    # ==========================================
    
    @app.route('/api/slaves/register', methods=['POST'])
    def register_slave():
        """
        Registrar nuevo slave
        
        Request body:
        {
            "slave_id": "raspi-001",
            "device_type": "raspberry_pi_4",
            "resources": {
                "cpu_cores": 4,
                "memory_gb": 8,
                "max_agents": 8
            },
            "capabilities": {
                "llm_providers": ["groq"],
                "gpu": false
            },
            "version": {
                "git_branch": "docker-workers",
                "git_commit": "abc123",
                "python_version": "3.11.2"
            }
        }
        """
        try:
            data = request.json
            
            # Validar campos requeridos
            required = ['slave_id', 'device_type', 'resources', 'capabilities', 'version']
            for field in required:
                if field not in data:
                    return jsonify({"error": f"Missing field: {field}"}), 400
            
            # Registrar slave
            success = orchestrator.register_slave(
                slave_id=data['slave_id'],
                device_type=data['device_type'],
                resources=data['resources'],
                capabilities=data['capabilities'],
                version=data['version']
            )
            
            if success:
                return jsonify({
                    "status": "registered",
                    "slave_id": data['slave_id'],
                    "message": "Slave registered successfully"
                }), 200
            else:
                return jsonify({"error": "Registration failed"}), 500
                
        except Exception as e:
            logger.error(f"Error registering slave: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/slaves/<slave_id>/heartbeat', methods=['POST'])
    def slave_heartbeat(slave_id: str):
        """
        Recibir heartbeat de slave
        
        Request body:
        {
            "agents_status": {
                "agent_abc123": {
                    "status": "active",
                    "uptime": 3600,
                    "last_action": "search_info"
                }
            },
            "resources_usage": {
                "cpu_percent": 45.2,
                "memory_percent": 62.0,
                "agents_latency_avg": 120
            },
            "version": {
                "git_branch": "docker-workers",
                "git_commit": "abc123",
                "python_version": "3.11.2"
            }
        }
        """
        try:
            data = request.json
            
            orchestrator.update_slave_heartbeat(
                slave_id=slave_id,
                agents_status=data.get('agents_status', {}),
                resources_usage=data.get('resources_usage', {}),
                version=data.get('version', {})
            )
            
            return jsonify({"status": "ok"}), 200
            
        except Exception as e:
            logger.error(f"Error processing heartbeat from {slave_id}: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/slaves/<slave_id>/commands', methods=['GET'])
    def get_slave_commands(slave_id: str):
        """
        Slave solicita comandos pendientes
        
        Response:
        {
            "commands": [
                {
                    "type": "deploy_agent",
                    "agent_id": "agent_xyz789",
                    "genome": {...}
                },
                {
                    "type": "destroy_agent",
                    "agent_id": "agent_old123"
                }
            ]
        }
        """
        try:
            commands = orchestrator.get_commands_for_slave(slave_id)
            
            return jsonify({
                "commands": commands,
                "count": len(commands)
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting commands for {slave_id}: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/slaves/<slave_id>/unregister', methods=['POST'])
    def unregister_slave(slave_id: str):
        """Desregistrar slave"""
        try:
            orchestrator.unregister_slave(slave_id)
            return jsonify({"status": "unregistered"}), 200
        except Exception as e:
            logger.error(f"Error unregistering slave: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/slaves/list', methods=['GET'])
    def list_slaves():
        """Listar todos los slaves registrados"""
        try:
            slaves = orchestrator.get_slaves()
            
            slaves_data = []
            for slave_id, slave in slaves.items():
                slaves_data.append({
                    "slave_id": slave_id,
                    "device_type": slave.device_type,
                    "status": slave.status,
                    "resources": slave.resources,
                    "agents_registered": slave.agents_registered,
                    "agents_active": slave.agents_active,
                    "last_heartbeat": slave.last_heartbeat,
                    "version": {
                        "git_branch": slave.git_branch,
                        "git_commit": slave.git_commit,
                        "python_version": slave.python_version
                    }
                })
            
            return jsonify({
                "slaves": slaves_data,
                "total": len(slaves_data),
                "online": len([s for s in slaves.values() if s.status == "online"])
            }), 200
            
        except Exception as e:
            logger.error(f"Error listing slaves: {e}")
            return jsonify({"error": str(e)}), 500
    
    # ==========================================
    # AGENT MANAGEMENT
    # ==========================================
    
    @app.route('/api/agents/deploy', methods=['POST'])
    def deploy_agent():
        """
        Deploy nuevo agente en el mejor slave disponible
        
        Request body:
        {
            "genome": {
                "agent_id": "agent_xyz",  # Opcional, se genera si no se provee
                "prompt": "You are...",
                "actions": ["search_info", "write_code"],
                "params": {
                    "temperature": 0.8,
                    "model": "llama-3.3-70b"
                }
            }
        }
        """
        try:
            data = request.json
            
            if 'genome' not in data:
                return jsonify({"error": "Missing 'genome' field"}), 400
            
            agent_id = orchestrator.deploy_agent(genome=data['genome'])
            
            if agent_id:
                return jsonify({
                    "status": "deployed",
                    "agent_id": agent_id,
                    "message": "Agent deployment scheduled"
                }), 201
            else:
                return jsonify({"error": "No slaves available"}), 503
                
        except Exception as e:
            logger.error(f"Error deploying agent: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/agents/<agent_id>/destroy', methods=['POST'])
    def destroy_agent(agent_id: str):
        """Destruir agente existente"""
        try:
            success = orchestrator.destroy_agent(agent_id)
            
            if success:
                return jsonify({
                    "status": "destroyed",
                    "agent_id": agent_id,
                    "message": "Agent destruction scheduled"
                }), 200
            else:
                return jsonify({"error": "Agent not found"}), 404
                
        except Exception as e:
            logger.error(f"Error destroying agent: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/agents/<agent_id>/update_genome', methods=['POST'])
    def update_agent_genome(agent_id: str):
        """
        Actualizar genome de agente
        
        Request body:
        {
            "genome": {
                "prompt": "You are...",
                "actions": ["new_action"],
                "params": {...}
            }
        }
        """
        try:
            data = request.json
            
            if 'genome' not in data:
                return jsonify({"error": "Missing 'genome' field"}), 400
            
            success = orchestrator.update_agent_genome(
                agent_id=agent_id,
                genome=data['genome']
            )
            
            if success:
                return jsonify({
                    "status": "updated",
                    "agent_id": agent_id,
                    "message": "Genome update scheduled"
                }), 200
            else:
                return jsonify({"error": "Agent not found"}), 404
                
        except Exception as e:
            logger.error(f"Error updating agent genome: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/agents/placements', methods=['GET'])
    def get_agent_placements():
        """Ver distribución de agentes en el cluster"""
        try:
            placements = orchestrator.get_agent_placements()
            
            # Agrupar por slave
            by_slave = {}
            for agent_id, placement in placements.items():
                slave_id = placement['slave_id']
                if slave_id not in by_slave:
                    by_slave[slave_id] = []
                by_slave[slave_id].append(agent_id)
            
            return jsonify({
                "placements": placements,
                "total_agents": len(placements),
                "by_slave": by_slave
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting placements: {e}")
            return jsonify({"error": str(e)}), 500
    
    # ==========================================
    # DASHBOARD & CLUSTER MONITORING
    # ==========================================
    
    @app.route('/api/cluster/stats', methods=['GET'])
    def get_cluster_stats():
        """Estadísticas del cluster"""
        try:
            stats = orchestrator.get_stats()
            return jsonify(stats), 200
        except Exception as e:
            logger.error(f"Error getting cluster stats: {e}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/cluster/dashboard', methods=['GET'])
    def get_dashboard():
        """Dashboard completo con toda la información del cluster"""
        try:
            stats = orchestrator.get_stats()
            slaves = orchestrator.get_slaves()
            placements = orchestrator.get_agent_placements()
            
            # Agrupar agents por slave
            agents_by_slave = {}
            for agent_id, placement in placements.items():
                slave_id = placement['slave_id']
                if slave_id not in agents_by_slave:
                    agents_by_slave[slave_id] = []
                agents_by_slave[slave_id].append({
                    "agent_id": agent_id,
                    "placed_at": placement.get('placed_at')
                })
            
            # Formato slaves para dashboard
            slaves_info = []
            for slave_id, slave in slaves.items():
                slaves_info.append({
                    "slave_id": slave_id,
                    "device_type": slave.device_type,
                    "status": slave.status,
                    "resources": slave.resources,
                    "agents": agents_by_slave.get(slave_id, []),
                    "agents_count": len(agents_by_slave.get(slave_id, [])),
                    "agents_active": slave.agents_active,
                    "last_heartbeat": slave.last_heartbeat,
                    "version": {
                        "git_branch": slave.git_branch,
                        "git_commit": slave.git_commit[:7] if slave.git_commit else "unknown"
                    }
                })
            
            return jsonify({
                "summary": stats,
                "slaves": slaves_info,
                "timestamp": datetime.utcnow().isoformat()
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting dashboard: {e}")
            return jsonify({"error": str(e)}), 500
    
    # ==========================================
    # LLM FALLBACK MANAGER STATUS
    # ==========================================
    
    @app.route('/api/llm/health', methods=['GET'])
    def llm_health():
        """
        Estado de salud del LLM Fallback Manager
        
        Returns:
        {
            "total_requests": 123,
            "congress_escalations": 5,
            "providers": {
                "groq": {
                    "is_available": true,
                    "consecutive_failures": 0,
                    "success_rate": 95.2,
                    "in_cooldown": false
                },
                ...
            }
        }
        """
        try:
            from app.llm_manager_singleton import get_llm_manager
            llm_manager = get_llm_manager()
            
            health_report = llm_manager.get_health_report()
            
            return jsonify(health_report), 200
            
        except Exception as e:
            logger.error(f"Error getting LLM health: {e}")
            return jsonify({"error": str(e)}), 500
    
    logger.info("🎯 Orchestrator Flask app created")
    return app


def main():
    """Punto de entrada principal para ejecutar como módulo"""
    import sys
    
    logger.info("="*60)
    logger.info("🎯 D8 ORCHESTRATOR - Starting...")
    logger.info("="*60)
    
    app = create_orchestrator_app()
    
    # Configuración del servidor
    host = "0.0.0.0"  # Escuchar en todas las interfaces
    port = 7001
    
    logger.info(f"🌐 Orchestrator listening on http://{host}:{port}")
    logger.info(f"📊 Health check: http://{host}:{port}/health")
    logger.info(f"📈 Statistics: http://{host}:{port}/api/stats")
    logger.info("="*60)
    
    try:
        # Iniciar servidor
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down orchestrator...")
        sys.exit(0)


if __name__ == '__main__':
    """Ejecutar orchestrator en modo standalone"""
    main()
