#!/usr/bin/env python3
"""
D8 Process Supervisor - Auto-recovery system for D8 Master
============================================================
Supervises and automatically restarts D8 core components:
- Congreso Autónomo
- Niche Discovery
- Orchestrator

Features:
- Auto-restart on crash
- Retry limit (5 attempts)
- Lockfile to prevent duplicates
- Ctrl+C for clean shutdown
- Process health monitoring
- Structured logging

Author: D8 System
Date: 2025-11-21
"""

import subprocess
import signal
import sys
import time
import os
from pathlib import Path
from typing import Dict, Optional
import logging
import json
from datetime import datetime

# Configurar logging
log_dir = Path.home() / "Documents" / "d8_data" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "supervisor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ProcessSupervisor:
    """
    Supervisor de procesos D8 con auto-recuperación
    
    Características:
    - Inicia múltiples componentes
    - Monitorea health de cada uno
    - Reinicia automáticamente si se caen
    - Ctrl+C para cierre limpio
    - Lockfile para evitar duplicados
    """
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.retry_counts: Dict[str, int] = {}
        self.max_retries = 5
        self.running = True
        self.data_dir = Path.home() / "Documents" / "d8_data"
        self.lockfile = self.data_dir / "supervisor.lock"
        self.project_root = Path(__file__).parent.parent
        
        # Crear directorio de logs
        (self.data_dir / "logs").mkdir(parents=True, exist_ok=True)
        
        # Componentes a supervisar
        self.components = [
            {
                "name": "congress",
                "script": "scripts/autonomous_congress.py",
                "description": "Congreso Autónomo",
                "enabled": True
            },
            {
                "name": "niche_discovery",
                "script": "scripts/niche_discovery_agent.py",
                "description": "Niche Discovery",
                "enabled": True
            },
            {
                "name": "orchestrator",
                "module": "app.orchestrator_app",
                "description": "Orchestrator",
                "enabled": True
            }
        ]
        
        logger.info("🔄 Process Supervisor initialized")
        logger.info(f"   Project root: {self.project_root}")
        logger.info(f"   Lockfile: {self.lockfile}")
    
    def check_lockfile(self) -> bool:
        """Verificar si ya hay supervisor corriendo"""
        if self.lockfile.exists():
            try:
                lock_data = json.loads(self.lockfile.read_text())
                pid = lock_data.get("pid")
                
                # Verificar si el proceso aún existe
                if pid:
                    try:
                        # En Windows, usar tasklist
                        if sys.platform == "win32":
                            import subprocess as sp
                            result = sp.run(
                                ["tasklist", "/FI", f"PID eq {pid}"],
                                capture_output=True,
                                text=True
                            )
                            if str(pid) in result.stdout:
                                logger.error(f"❌ Supervisor ya corriendo (PID: {pid})")
                                logger.error(f"   Iniciado: {lock_data.get('started_at')}")
                                return False
                        else:
                            # En Linux/Mac, verificar /proc
                            os.kill(pid, 0)
                            logger.error(f"❌ Supervisor ya corriendo (PID: {pid})")
                            logger.error(f"   Iniciado: {lock_data.get('started_at')}")
                            return False
                    except (OSError, ProcessLookupError):
                        # Proceso no existe, lockfile obsoleto
                        pass
                
                # Lockfile obsoleto, eliminar
                logger.warning("⚠️ Lockfile obsoleto encontrado, limpiando...")
                self.lockfile.unlink()
                
            except Exception as e:
                logger.warning(f"⚠️ Error leyendo lockfile: {e}, limpiando...")
                if self.lockfile.exists():
                    self.lockfile.unlink()
        
        # Crear lockfile
        lock_data = {
            "pid": os.getpid(),
            "started_at": datetime.now().isoformat(),
            "components": [c["name"] for c in self.components if c.get("enabled", True)]
        }
        self.lockfile.write_text(json.dumps(lock_data, indent=2))
        logger.info(f"✅ Lockfile creado (PID: {os.getpid()})")
        
        return True
    
    def start_component(self, component: dict):
        """Iniciar un componente"""
        name = component["name"]
        
        if not component.get("enabled", True):
            logger.info(f"⏭️  {name} está deshabilitado, saltando...")
            return
        
        if name in self.processes and self.processes[name].poll() is None:
            logger.info(f"⏭️  {name} ya está corriendo")
            return
        
        logger.info(f"🚀 Iniciando {component['description']}...")
        
        try:
            # Preparar environment con PYTHONPATH correcto
            env = os.environ.copy()
            env["PYTHONPATH"] = str(self.project_root)
            
            if "script" in component:
                script_path = self.project_root / component["script"]
                process = subprocess.Popen(
                    [sys.executable, str(script_path)],
                    cwd=self.project_root,
                    env=env,  # ← AGREGADO: Pasar environment con PYTHONPATH
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=1,
                    universal_newlines=True
                )
            elif "module" in component:
                process = subprocess.Popen(
                    [sys.executable, "-m", component["module"]],
                    cwd=self.project_root,
                    env=env,  # ← AGREGADO: Pasar environment con PYTHONPATH
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    bufsize=1,
                    universal_newlines=True
                )
            else:
                logger.error(f"❌ Componente {name} sin script ni module")
                return
            
            self.processes[name] = process
            self.retry_counts[name] = 0
            
            logger.info(f"✅ {component['description']} iniciado (PID: {process.pid})")
            
        except Exception as e:
            logger.error(f"❌ Error iniciando {name}: {e}")
    
    def check_health(self):
        """Verificar health de todos los procesos"""
        for name, process in list(self.processes.items()):
            if process.poll() is not None:
                # Proceso terminó
                exit_code = process.returncode
                
                # Capturar últimas líneas de stderr
                try:
                    stderr_output = process.stderr.read() if process.stderr else ""
                    error_lines = stderr_output.split('\n')[-10:] if stderr_output else []
                    error_msg = '\n'.join(error_lines) if error_lines else "No error output"
                except:
                    error_msg = "Could not read error output"
                
                logger.warning(f"⚠️  {name} terminó (exit code: {exit_code})")
                if error_msg and error_msg != "No error output":
                    logger.warning(f"   Error: {error_msg[:500]}")  # Aumentado de 200 a 500
                
                # Detectar errores conocidos que no deben reiniciar inmediatamente
                should_delay_restart = False
                delay_seconds = 5
                
                if "Rate limit" in error_msg or "429" in error_msg:
                    logger.warning(f"   ⏳ Rate limit detectado - Esperando 60s antes de reiniciar")
                    should_delay_restart = True
                    delay_seconds = 60
                elif "ModuleNotFoundError" in error_msg:
                    logger.error(f"   ❌ Error de importación - Verificar PYTHONPATH y dependencias")
                    # No reintentar inmediatamente en errores de módulo
                    delay_seconds = 30
                
                # Intentar reiniciar
                if self.retry_counts[name] < self.max_retries:
                    self.retry_counts[name] += 1
                    logger.info(f"🔄 Reiniciando {name} (intento {self.retry_counts[name]}/{self.max_retries})")
                    
                    # Esperar antes de reiniciar
                    if should_delay_restart or delay_seconds > 5:
                        logger.info(f"   ⏳ Esperando {delay_seconds}s...")
                    time.sleep(delay_seconds)
                    
                    # Buscar componente config
                    component = next(c for c in self.components if c["name"] == name)
                    self.start_component(component)
                else:
                    logger.error(f"❌ {name} alcanzó límite de reintentos ({self.max_retries})")
                    logger.error(f"   Componente {name} detenido permanentemente")
                    logger.error(f"   Revisar logs en: {self.data_dir / 'logs'}")
    
    def stop_all(self):
        """Detener todos los procesos limpiamente"""
        logger.info("🛑 Deteniendo todos los procesos...")
        
        for name, process in self.processes.items():
            if process.poll() is None:
                logger.info(f"   Deteniendo {name} (PID: {process.pid})...")
                
                try:
                    # Intentar SIGTERM primero (graceful)
                    process.terminate()
                    
                    # Esperar hasta 10 segundos
                    try:
                        process.wait(timeout=10)
                        logger.info(f"   ✅ {name} detenido limpiamente")
                    except subprocess.TimeoutExpired:
                        # Forzar con SIGKILL
                        logger.warning(f"   ⚠️ {name} no responde, forzando...")
                        process.kill()
                        process.wait()
                        logger.info(f"   ✅ {name} forzado a detenerse")
                        
                except Exception as e:
                    logger.error(f"   ❌ Error deteniendo {name}: {e}")
        
        # Eliminar lockfile
        if self.lockfile.exists():
            self.lockfile.unlink()
            logger.info("🗑️  Lockfile eliminado")
        
        logger.info("✅ Todos los procesos detenidos")
    
    def run(self):
        """Loop principal del supervisor"""
        # Verificar lockfile
        if not self.check_lockfile():
            logger.error("❌ No se puede iniciar supervisor (ya corriendo)")
            return 1
        
        # Registrar signal handlers
        signal.signal(signal.SIGINT, self._handle_sigint)
        signal.signal(signal.SIGTERM, self._handle_sigterm)
        
        logger.info("=" * 60)
        logger.info("🔄 D8 SUPERVISOR INICIADO")
        logger.info("=" * 60)
        
        # Iniciar todos los componentes
        for component in self.components:
            if component.get("enabled", True):
                self.start_component(component)
                time.sleep(3)  # Delay entre inicios
        
        logger.info("=" * 60)
        logger.info("✅ Todos los componentes iniciados")
        logger.info("🔄 Supervisor activo - Presiona Ctrl+C para detener")
        logger.info("=" * 60)
        
        # Loop de supervisión
        check_interval = 10  # segundos
        
        try:
            while self.running:
                time.sleep(check_interval)
                self.check_health()
        except KeyboardInterrupt:
            pass  # Manejado por _handle_sigint
        
        return 0
    
    def _handle_sigint(self, signum, frame):
        """Handler para Ctrl+C"""
        logger.info("\n🛑 Ctrl+C detectado - Cerrando sistema...")
        self.running = False
        self.stop_all()
        sys.exit(0)
    
    def _handle_sigterm(self, signum, frame):
        """Handler para SIGTERM"""
        logger.info("🛑 SIGTERM recibido - Cerrando sistema...")
        self.running = False
        self.stop_all()
        sys.exit(0)


def main():
    """Punto de entrada del supervisor"""
    try:
        supervisor = ProcessSupervisor()
        return supervisor.run()
    except Exception as e:
        logger.error(f"❌ Error fatal en supervisor: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
