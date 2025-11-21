"""
Remote Installer - Instala D8 Slave remotamente desde el Master
Ejecuta build_d8_slave.sh o .bat en máquina remota via SSH y captura output
"""

import sys
from pathlib import Path
import subprocess
import logging
from typing import Dict, Optional, Tuple
import time
import re

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class RemoteInstaller:
    """
    Instala D8 Slave en máquina remota via SSH
    
    Soporta:
    - Linux (SSH directo)
    - Windows (SSH con OpenSSH o PuTTY)
    - Raspberry Pi (SSH directo)
    """
    
    def __init__(self):
        self.install_log = []
    
    def _escape_special_chars(self, text: str) -> str:
        """Escapa caracteres problemáticos para transmisión"""
        # Escapar caracteres especiales que pueden causar problemas
        problematic_chars = {
            '\r\n': '\n',  # Normalizar line endings
            '\r': '\n',
            '\x00': '',    # Null bytes
        }
        
        for old, new in problematic_chars.items():
            text = text.replace(old, new)
        
        return text
    
    def _parse_ansi_colors(self, text: str) -> str:
        """Remueve códigos ANSI de colores para logging limpio"""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def check_ssh_connection(self, host: str, user: str, port: int = 22) -> Tuple[bool, str]:
        """
        Verifica si se puede conectar via SSH
        
        Returns:
            (success, message)
        """
        logger.info(f"🔍 Verificando conexión SSH a {user}@{host}:{port}...")
        
        try:
            result = subprocess.run(
                ["ssh", "-p", str(port), f"{user}@{host}", "echo", "SSH_OK"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "SSH_OK" in result.stdout:
                logger.info(f"✅ Conexión SSH exitosa")
                return True, "Conexión SSH OK"
            else:
                error_msg = result.stderr or "No se pudo conectar"
                logger.error(f"❌ Falló conexión SSH: {error_msg}")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Timeout conectando via SSH")
            return False, "Timeout"
        except FileNotFoundError:
            logger.error("❌ Cliente SSH no encontrado")
            return False, "SSH client not found"
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False, str(e)
    
    def detect_remote_os(self, host: str, user: str, port: int = 22) -> Optional[str]:
        """
        Detecta sistema operativo de máquina remota
        
        Returns:
            "linux", "windows", "darwin", "raspberry", o None
        """
        logger.info(f"🔍 Detectando sistema operativo remoto...")
        
        try:
            # Intentar comando Unix
            result = subprocess.run(
                ["ssh", "-p", str(port), f"{user}@{host}", "uname", "-a"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                uname_output = result.stdout.lower()
                
                if "raspberry" in uname_output or "armv" in uname_output:
                    logger.info("✅ Detectado: Raspberry Pi")
                    return "raspberry"
                elif "linux" in uname_output:
                    logger.info("✅ Detectado: Linux")
                    return "linux"
                elif "darwin" in uname_output:
                    logger.info("✅ Detectado: macOS")
                    return "darwin"
            
            # Intentar comando Windows
            result = subprocess.run(
                ["ssh", "-p", str(port), f"{user}@{host}", "ver"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and "Windows" in result.stdout:
                logger.info("✅ Detectado: Windows")
                return "windows"
            
            logger.warning("⚠️  No se pudo detectar el sistema operativo")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error detectando OS: {e}")
            return None
    
    def install_via_ssh_linux(
        self,
        host: str,
        user: str,
        port: int = 22,
        github_token: Optional[str] = None
    ) -> Dict:
        """
        Instala D8 Slave en Linux/Raspberry Pi via SSH
        
        Args:
            host: IP o hostname
            user: Usuario SSH
            port: Puerto SSH (default 22)
            github_token: Token de GitHub para clonar repo privado (opcional)
        
        Returns:
            Dict con success, output, errors
        """
        logger.info(f"🚀 Iniciando instalación remota en {user}@{host}...")
        
        result = {
            "success": False,
            "output": [],
            "errors": [],
            "duration": 0
        }
        
        start_time = time.time()
        
        try:
            # Paso 1: Transferir script
            logger.info("📤 Transfiriendo script de instalación...")
            
            local_script = Path(__file__).parent / "build_d8_slave.sh"
            remote_script = "/tmp/build_d8_slave.sh"
            
            scp_result = subprocess.run(
                [
                    "scp",
                    "-P", str(port),
                    str(local_script),
                    f"{user}@{host}:{remote_script}"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if scp_result.returncode != 0:
                error_msg = f"Falló transferencia SCP: {scp_result.stderr}"
                logger.error(f"❌ {error_msg}")
                result["errors"].append(error_msg)
                return result
            
            logger.info("✅ Script transferido")
            
            # Paso 2: Dar permisos de ejecución
            logger.info("🔧 Configurando permisos...")
            
            chmod_result = subprocess.run(
                ["ssh", "-p", str(port), f"{user}@{host}", f"chmod +x {remote_script}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if chmod_result.returncode != 0:
                logger.warning(f"⚠️  Falló chmod: {chmod_result.stderr}")
            
            # Paso 3: Ejecutar instalación
            logger.info("⚙️  Ejecutando instalación...")
            logger.info("📝 Capturando output en tiempo real...")
            print()
            print("=" * 70)
            print("OUTPUT DE INSTALACIÓN REMOTA:")
            print("=" * 70)
            print()
            
            # Ejecutar con pseudo-terminal para capturar todo
            cmd = [
                "ssh",
                "-tt",  # Force pseudo-terminal
                "-p", str(port),
                f"{user}@{host}",
                f"bash {remote_script}"
            ]
            
            # Usar subprocess.Popen para capturar en tiempo real
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Capturar línea por línea
            for line in iter(process.stdout.readline, ''):
                if line:
                    # Limpiar y escapar
                    clean_line = self._escape_special_chars(line.rstrip())
                    clean_line = self._parse_ansi_colors(clean_line)
                    
                    # Mostrar en consola
                    print(clean_line)
                    
                    # Guardar en log
                    result["output"].append(clean_line)
                    self.install_log.append(clean_line)
                    
                    # Detectar errores
                    if "[ERROR]" in clean_line or "error:" in clean_line.lower():
                        result["errors"].append(clean_line)
            
            process.wait()
            
            print()
            print("=" * 70)
            print()
            
            if process.returncode == 0:
                logger.info("✅ Instalación completada exitosamente")
                result["success"] = True
            else:
                logger.error(f"❌ Instalación falló con código {process.returncode}")
                result["errors"].append(f"Exit code: {process.returncode}")
            
        except subprocess.TimeoutExpired:
            error_msg = "Timeout durante instalación (>5 minutos)"
            logger.error(f"❌ {error_msg}")
            result["errors"].append(error_msg)
            
        except Exception as e:
            error_msg = f"Error durante instalación: {e}"
            logger.error(f"❌ {error_msg}")
            result["errors"].append(error_msg)
        
        result["duration"] = time.time() - start_time
        
        return result
    
    def install_via_ssh_windows(
        self,
        host: str,
        user: str,
        port: int = 22
    ) -> Dict:
        """
        Instala D8 Slave en Windows via SSH
        Similar a Linux pero ejecuta .bat
        """
        logger.info(f"🚀 Iniciando instalación remota en Windows {user}@{host}...")
        
        result = {
            "success": False,
            "output": [],
            "errors": [],
            "duration": 0
        }
        
        start_time = time.time()
        
        try:
            # Transferir script .bat
            logger.info("📤 Transfiriendo script de instalación...")
            
            local_script = Path(__file__).parent / "build_d8_slave.bat"
            remote_script = "C:\\Temp\\build_d8_slave.bat"
            
            # Crear directorio remoto
            subprocess.run(
                ["ssh", "-p", str(port), f"{user}@{host}", "mkdir", "C:\\Temp"],
                capture_output=True,
                timeout=10
            )
            
            # Transferir
            scp_result = subprocess.run(
                [
                    "scp",
                    "-P", str(port),
                    str(local_script),
                    f"{user}@{host}:{remote_script}"
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if scp_result.returncode != 0:
                error_msg = f"Falló transferencia SCP: {scp_result.stderr}"
                logger.error(f"❌ {error_msg}")
                result["errors"].append(error_msg)
                return result
            
            logger.info("✅ Script transferido")
            
            # Ejecutar
            logger.info("⚙️  Ejecutando instalación...")
            print()
            print("=" * 70)
            print("OUTPUT DE INSTALACIÓN REMOTA (Windows):")
            print("=" * 70)
            print()
            
            cmd = [
                "ssh",
                "-tt",
                "-p", str(port),
                f"{user}@{host}",
                remote_script
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    clean_line = self._escape_special_chars(line.rstrip())
                    clean_line = self._parse_ansi_colors(clean_line)
                    
                    print(clean_line)
                    result["output"].append(clean_line)
                    self.install_log.append(clean_line)
                    
                    if "[ERROR]" in clean_line:
                        result["errors"].append(clean_line)
            
            process.wait()
            
            print()
            print("=" * 70)
            print()
            
            if process.returncode == 0:
                logger.info("✅ Instalación completada exitosamente")
                result["success"] = True
            else:
                logger.error(f"❌ Instalación falló con código {process.returncode}")
                result["errors"].append(f"Exit code: {process.returncode}")
        
        except Exception as e:
            error_msg = f"Error durante instalación: {e}"
            logger.error(f"❌ {error_msg}")
            result["errors"].append(error_msg)
        
        result["duration"] = time.time() - start_time
        
        return result
    
    def save_install_log(self, filename: str = "remote_install.log"):
        """Guarda log completo de instalación"""
        log_path = Path.home() / "Documents" / "d8_data" / "logs" / filename
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.install_log))
        
        logger.info(f"📝 Log guardado en: {log_path}")
        return log_path


def main():
    """CLI para instalación remota"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Instalar D8 Slave remotamente via SSH')
    parser.add_argument('host', help='IP o hostname del slave')
    parser.add_argument('user', help='Usuario SSH')
    parser.add_argument('--port', type=int, default=22, help='Puerto SSH (default: 22)')
    parser.add_argument('--github-token', help='Token de GitHub (opcional)')
    
    args = parser.parse_args()
    
    installer = RemoteInstaller()
    
    # Verificar conexión
    success, msg = installer.check_ssh_connection(args.host, args.user, args.port)
    if not success:
        logger.error(f"❌ No se pudo conectar: {msg}")
        return 1
    
    # Detectar OS
    remote_os = installer.detect_remote_os(args.host, args.user, args.port)
    if not remote_os:
        logger.error("❌ No se pudo detectar sistema operativo remoto")
        return 1
    
    # Instalar según OS
    if remote_os in ["linux", "raspberry", "darwin"]:
        result = installer.install_via_ssh_linux(
            args.host,
            args.user,
            args.port,
            args.github_token
        )
    elif remote_os == "windows":
        result = installer.install_via_ssh_windows(
            args.host,
            args.user,
            args.port
        )
    else:
        logger.error(f"❌ OS no soportado: {remote_os}")
        return 1
    
    # Guardar log
    log_path = installer.save_install_log(
        f"install_{args.host}_{int(time.time())}.log"
    )
    
    # Resumen
    print()
    print("=" * 70)
    print("RESUMEN DE INSTALACIÓN")
    print("=" * 70)
    print()
    print(f"Host: {args.user}@{args.host}:{args.port}")
    print(f"OS: {remote_os}")
    print(f"Duración: {result['duration']:.1f} segundos")
    print(f"Éxito: {'✅ SÍ' if result['success'] else '❌ NO'}")
    print(f"Líneas de output: {len(result['output'])}")
    print(f"Errores: {len(result['errors'])}")
    print(f"Log: {log_path}")
    print()
    
    if result['errors']:
        print("⚠️  ERRORES ENCONTRADOS:")
        for error in result['errors'][:10]:  # Mostrar primeros 10
            print(f"   • {error}")
        print()
    
    return 0 if result['success'] else 1


if __name__ == "__main__":
    sys.exit(main())
