"""
Slave Manager - Gestiona slaves remotos
Registra, monitorea, y ejecuta tareas en slaves
"""

import logging
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
import time
from datetime import datetime
import threading
import subprocess
import sys

from app.distributed.robust_connection import RobustConnection

logger = logging.getLogger(__name__)


class SlaveManager:
    """
    Gestiona el ciclo de vida de slaves remotos:
    - Registro de nuevos slaves
    - Health monitoring (cada 30s)
    - Verificación de versiones
    - Ejecución remota de tareas
    - Auto-recovery
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / "Documents" / "d8_data" / "slaves" / "config.json"
        self.slaves: Dict[str, Dict] = self._load_config()
        self.connection = RobustConnection()
        self.logger = logging.getLogger(__name__)
        self.master_version = self._get_master_version()
        
        # Auto-guardar config cada 5 minutos
        self._start_autosave_thread()
    
    def _get_master_version(self) -> str:
        """Actualiza y obtiene la versión actual del master"""
        try:
            # Ejecutar capture_version.py para actualizar version_info.json
            script_path = Path(__file__).parent.parent.parent / "scripts" / "setup" / "capture_version.py"
            subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                timeout=10
            )
            
            # Leer version_info.json
            version_file = Path(__file__).parent.parent.parent / "version_info.json"
            if version_file.exists():
                version_data = json.loads(version_file.read_text())
                return version_data.get("commit", "unknown")
        except Exception as e:
            self.logger.error(f"Error obteniendo versión del master: {e}")
        
        return "unknown"
    
    def _start_autosave_thread(self):
        """Inicia thread que guarda config periódicamente"""
        def autosave_loop():
            while True:
                time.sleep(300)  # 5 minutos
                self._save_config()
        
        thread = threading.Thread(target=autosave_loop, daemon=True)
        thread.start()
    
    def _load_config(self) -> Dict[str, Dict]:
        """Carga configuración de slaves"""
        if not self.config_path.exists():
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            return {}
        
        try:
            return json.loads(self.config_path.read_text())
        except Exception as e:
            logger.error(f"Error cargando config de slaves: {e}")
            return {}
    
    def _save_config(self):
        """Guarda configuración de slaves"""
        try:
            self.config_path.write_text(json.dumps(self.slaves, indent=2))
        except Exception as e:
            logger.error(f"Error guardando config de slaves: {e}")
    
    def register_slave(
        self,
        slave_id: str,
        host: str,
        port: int = 7600,
        install_method: str = "unknown"
    ) -> bool:
        """
        Registra nuevo slave
        
        Args:
            slave_id: ID único del slave
            host: IP o hostname
            port: Puerto (default 7600)
            install_method: docker/venv/python
        
        Returns:
            True si registro exitoso
        """
        if slave_id in self.slaves:
            logger.warning(f"⚠️ Slave {slave_id} ya está registrado")
            return False
        
        self.slaves[slave_id] = {
            "host": host,
            "port": port,
            "status": "unknown",
            "install_method": install_method,
            "registered_at": datetime.now().isoformat(),
            "last_seen": "never"
        }
        
        self._save_config()
        logger.info(f"✅ Slave registrado: {slave_id} ({host}:{port})")
        
        # Health check inmediato
        self.check_health(slave_id)
        
        return True
    
    def unregister_slave(self, slave_id: str) -> bool:
        """Desregistra slave"""
        if slave_id not in self.slaves:
            return False
        
        del self.slaves[slave_id]
        self._save_config()
        logger.info(f"👋 Slave desregistrado: {slave_id}")
        
        return True
    
    def check_health(self, slave_id: str) -> bool:
        """Verifica si un slave está saludable y en la versión correcta"""
        if slave_id not in self.slaves:
            return False
        
        slave = self.slaves[slave_id]
        url = f"http://{slave['host']}:{slave['port']}/api/health"
        
        try:
            response = self.connection.get(url, timeout=10)
            if response and response.status_code == 200:
                health_data = response.json()
                slave['last_seen'] = datetime.now().isoformat()
                
                # Verificar versión
                slave_commit = health_data.get('commit', 'unknown')
                slave['commit'] = slave_commit
                
                if slave_commit != self.master_version:
                    warning_msg = (
                        f"⚠️  DESINCRONIZACIÓN DE VERSIÓN detectada en {slave_id}:\n"
                        f"   Master: {self.master_version}\n"
                        f"   Slave:  {slave_commit}"
                    )
                    self.logger.warning(warning_msg)
                    
                    slave['status'] = 'version_mismatch'
                    slave['version_mismatch'] = True
                else:
                    slave['status'] = 'healthy'
                    slave['version_mismatch'] = False
                
                self._save_config()
                return slave['status'] == 'healthy'
        except Exception as e:
            self.logger.error(f"Health check falló para {slave_id}: {e}")
        
        slave['status'] = 'unhealthy'
        self._save_config()
        return False
    
    def execute_remote_task(self, slave_id: str, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Ejecuta tarea en slave remoto
        
        Args:
            slave_id: ID del slave
            task: Diccionario con datos de la tarea
        
        Returns:
            Resultado de la ejecución o None si falla
        """
        if slave_id not in self.slaves:
            logger.error(f"❌ Slave {slave_id} no encontrado")
            return None
        
        slave = self.slaves[slave_id]
        
        # Verificar versión
        if slave.get('version_mismatch', False):
            logger.error(
                f"❌ Rechazando ejecución en {slave_id}: versión incorrecta "
                f"(esperado {self.master_version}, tiene {slave.get('commit', 'unknown')})"
            )
            return None
        
        # Construir comando Python
        command = self._build_python_command(task)
        
        url = f"http://{slave['host']}:{slave['port']}/api/execute"
        token = self._get_slave_token()
        
        try:
            response = self.connection.post(
                url,
                json={"command": command, "working_dir": task.get("working_dir")},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response and response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Tarea ejecutada en {slave_id} con método {result.get('method')}")
                return result
            else:
                logger.error(f"❌ Error ejecutando tarea en {slave_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Excepción ejecutando tarea en {slave_id}: {e}")
            return None
    
    def _build_python_command(self, task: Dict[str, Any]) -> str:
        """Construye comando Python para ejecutar tarea"""
        task_type = task.get("type", "unknown")
        
        # Mapeo de tipos de tarea a código Python
        if task_type == "niche_analysis":
            market = task["data"]["market"]
            return f"""
import sys
sys.path.insert(0, '.')
from scripts.daemons.niche_discovery_daemon import NicheDiscoveryAgent
import json

agent = NicheDiscoveryAgent()
result = agent.discover_opportunities(['{market}'])
print(json.dumps({{'success': True, 'result': result}}))
"""
        
        elif task_type == "fitness_evaluation":
            genome = task["data"]["genome"]
            return f"""
import sys
sys.path.insert(0, '.')
from app.evolution.darwin import evaluate_fitness
import json

genome_data = {json.dumps(genome)}
fitness = evaluate_fitness(genome_data)
print(json.dumps({{'success': True, 'fitness': fitness}}))
"""
        
        elif task_type == "genetic_crossover":
            parent1 = task["data"]["parent1"]
            parent2 = task["data"]["parent2"]
            return f"""
import sys
sys.path.insert(0, '.')
from app.evolution.darwin import crossover
import json

p1 = {json.dumps(parent1)}
p2 = {json.dumps(parent2)}
child = crossover(p1, p2)
print(json.dumps({{'success': True, 'genome': child}}))
"""
        
        else:
            # Comando genérico
            return task.get("command", "print('No command specified')")
    
    def _get_slave_token(self) -> str:
        """Obtiene token de autenticación para slaves"""
        import os
        return os.getenv("SLAVE_TOKEN", "default-dev-token-change-in-production")
    
    def find_available_slave(self, task: Dict[str, Any]) -> Optional[str]:
        """
        Encuentra slave disponible para ejecutar tarea
        
        Args:
            task: Tarea a ejecutar
        
        Returns:
            ID del slave disponible o None
        """
        for slave_id, slave_data in self.slaves.items():
            # Verificar estado
            if slave_data.get('status') != 'healthy':
                continue
            
            # Verificar versión
            if slave_data.get('version_mismatch', False):
                continue
            
            # TODO: Verificar capabilities
            
            return slave_id
        
        return None
    
    def get_all_status(self) -> List[Dict[str, Any]]:
        """Obtiene el estado de todos los slaves"""
        status_list = []
        
        for slave_id, slave_data in self.slaves.items():
            status_list.append({
                "id": slave_id,
                "host": slave_data['host'],
                "port": slave_data['port'],
                "status": slave_data.get('status', 'unknown'),
                "last_seen": slave_data.get('last_seen', 'never'),
                "install_method": slave_data.get('install_method', 'unknown'),
                "commit": slave_data.get('commit', 'unknown'),
                "version_mismatch": slave_data.get('version_mismatch', False)
            })
        
        return status_list
    
    def auto_recover_slave(self, slave_id: str) -> bool:
        """
        Intenta recuperar slave caído
        
        Args:
            slave_id: ID del slave
        
        Returns:
            True si recuperación exitosa
        """
        if slave_id not in self.slaves:
            return False
        
        logger.info(f"🔄 Intentando recuperar slave {slave_id}...")
        
        # Esperar 5 segundos
        time.sleep(5)
        
        # Verificar health
        if self.check_health(slave_id):
            logger.info(f"✅ Slave {slave_id} recuperado")
            return True
        
        logger.error(f"❌ No se pudo recuperar slave {slave_id}")
        return False
    
    def install_slave_remote(
        self,
        host: str,
        user: str,
        port: int = 22,
        slave_id: Optional[str] = None,
        github_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Instala D8 Slave en máquina remota via SSH
        
        Args:
            host: IP o hostname
            user: Usuario SSH
            port: Puerto SSH
            slave_id: ID para registrar (auto-generado si None)
            github_token: Token de GitHub (opcional)
        
        Returns:
            Dict con success, slave_id, output, errors
        """
        logger.info(f"🚀 Instalando slave remotamente en {user}@{host}:{port}...")
        
        # Importar RemoteInstaller
        try:
            from scripts.setup.remote_installer import RemoteInstaller
        except ImportError:
            logger.error("❌ No se pudo importar RemoteInstaller")
            return {
                "success": False,
                "errors": ["RemoteInstaller not found"]
            }
        
        installer = RemoteInstaller()
        
        # Verificar conexión SSH
        success, msg = installer.check_ssh_connection(host, user, port)
        if not success:
            logger.error(f"❌ No se pudo conectar via SSH: {msg}")
            return {
                "success": False,
                "errors": [f"SSH connection failed: {msg}"]
            }
        
        # Detectar OS remoto
        remote_os = installer.detect_remote_os(host, user, port)
        if not remote_os:
            logger.error("❌ No se pudo detectar OS remoto")
            return {
                "success": False,
                "errors": ["Could not detect remote OS"]
            }
        
        logger.info(f"✅ OS detectado: {remote_os}")
        
        # Ejecutar instalación según OS
        if remote_os in ["linux", "raspberry", "darwin"]:
            result = installer.install_via_ssh_linux(host, user, port, github_token)
        elif remote_os == "windows":
            result = installer.install_via_ssh_windows(host, user, port)
        else:
            logger.error(f"❌ OS no soportado: {remote_os}")
            return {
                "success": False,
                "errors": [f"Unsupported OS: {remote_os}"]
            }
        
        # Si instalación exitosa, registrar slave
        if result["success"]:
            if not slave_id:
                # Auto-generar ID basado en host
                slave_id = f"slave-{host.replace('.', '-')}"
            
            logger.info(f"📝 Registrando slave como: {slave_id}")
            
            self.register_slave(
                slave_id=slave_id,
                host=host,
                port=7600,  # Puerto por defecto del slave
                install_method="remote_automated"
            )
            
            # Guardar log de instalación
            log_path = installer.save_install_log(
                f"install_{slave_id}_{int(time.time())}.log"
            )
            
            logger.info(f"✅ Slave instalado y registrado: {slave_id}")
            logger.info(f"📝 Log: {log_path}")
            
            result["slave_id"] = slave_id
            result["log_path"] = str(log_path)
        
        return result
