#!/usr/bin/env python3
"""
D8 Slave Supervisor - Auto-recovery for slave servers
======================================================
Supervises and automatically restarts the slave server component.

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
from typing import Optional
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
        logging.FileHandler(log_dir / "supervisor_slave.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SlaveSupervisor:
    """
    Supervisor simplificado para slave server
    
    Características:
    - Supervisa solo slave_server
    - Auto-restart en caso de crash
    - Lockfile para prevenir duplicados
    - Ctrl+C para cierre limpio
    """
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.retry_count = 0
        self.max_retries = 5
        self.running = True
        self.data_dir = Path.home() / "Documents" / "d8_data"
        self.lockfile = self.data_dir / "supervisor_slave.lock"
        self.project_root = Path(__file__).parent.parent
        
        # Crear directorio de logs
        (self.data_dir / "logs").mkdir(parents=True, exist_ok=True)
        
        logger.info("🔄 Slave Supervisor initialized")
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
                                logger.error(f"❌ Slave Supervisor ya corriendo (PID: {pid})")
                                logger.error(f"   Iniciado: {lock_data.get('started_at')}")
                                return False
                        else:
                            # En Linux/Mac, verificar /proc
                            os.kill(pid, 0)
                            logger.error(f"❌ Slave Supervisor ya corriendo (PID: {pid})")
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
            "component": "slave_server"
        }
        self.lockfile.write_text(json.dumps(lock_data, indent=2))
        logger.info(f"✅ Lockfile creado (PID: {os.getpid()})")
        
        return True
    
    def start_slave_server(self):
        """Iniciar slave server"""
        if self.process and self.process.poll() is None:
            logger.info("⏭️  Slave server ya está corriendo")
            return
        
        logger.info("🚀 Iniciando Slave Server...")
        
        try:
            self.process = subprocess.Popen(
                [sys.executable, "-m", "app.distributed.slave_server"],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True
            )
            
            self.retry_count = 0
            logger.info(f"✅ Slave Server iniciado (PID: {self.process.pid})")
            
        except Exception as e:
            logger.error(f"❌ Error iniciando slave server: {e}")
    
    def check_health(self):
        """Verificar health del proceso"""
        if not self.process:
            return
        
        if self.process.poll() is not None:
            # Proceso terminó
            exit_code = self.process.returncode
            
            # Capturar últimas líneas de stderr
            try:
                stderr_output = self.process.stderr.read() if self.process.stderr else ""
                error_lines = stderr_output.split('\n')[-10:] if stderr_output else []
                error_msg = '\n'.join(error_lines) if error_lines else "No error output"
            except:
                error_msg = "Could not read error output"
            
            logger.warning(f"⚠️  Slave server terminó (exit code: {exit_code})")
            if error_msg and error_msg != "No error output":
                logger.warning(f"   Error: {error_msg[:200]}")
            
            # Intentar reiniciar
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                logger.info(f"🔄 Reiniciando slave server (intento {self.retry_count}/{self.max_retries})")
                
                # Esperar 5 segundos antes de reiniciar
                time.sleep(5)
                self.start_slave_server()
            else:
                logger.error(f"❌ Slave server alcanzó límite de reintentos ({self.max_retries})")
                logger.error("   Slave server detenido permanentemente")
    
    def stop(self):
        """Detener el proceso limpiamente"""
        if not self.process:
            return
        
        logger.info("🛑 Deteniendo slave server...")
        
        if self.process.poll() is None:
            logger.info(f"   Deteniendo slave server (PID: {self.process.pid})...")
            
            try:
                # Intentar SIGTERM primero (graceful)
                self.process.terminate()
                
                # Esperar hasta 10 segundos
                try:
                    self.process.wait(timeout=10)
                    logger.info("   ✅ Slave server detenido limpiamente")
                except subprocess.TimeoutExpired:
                    # Forzar con SIGKILL
                    logger.warning("   ⚠️ Slave server no responde, forzando...")
                    self.process.kill()
                    self.process.wait()
                    logger.info("   ✅ Slave server forzado a detenerse")
                    
            except Exception as e:
                logger.error(f"   ❌ Error deteniendo slave server: {e}")
        
        # Eliminar lockfile
        if self.lockfile.exists():
            self.lockfile.unlink()
            logger.info("🗑️  Lockfile eliminado")
        
        logger.info("✅ Slave server detenido")
    
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
        logger.info("🔄 D8 SLAVE SUPERVISOR INICIADO")
        logger.info("=" * 60)
        
        # Iniciar slave server
        self.start_slave_server()
        
        logger.info("=" * 60)
        logger.info("✅ Slave server iniciado")
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
        self.stop()
        sys.exit(0)
    
    def _handle_sigterm(self, signum, frame):
        """Handler para SIGTERM"""
        logger.info("🛑 SIGTERM recibido - Cerrando sistema...")
        self.running = False
        self.stop()
        sys.exit(0)


def main():
    """Punto de entrada del supervisor"""
    try:
        supervisor = SlaveSupervisor()
        return supervisor.run()
    except Exception as e:
        logger.error(f"❌ Error fatal en supervisor: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
