#!/usr/bin/env python3
"""
Build D8 Slave - Sistema inteligente de instalación remota
Ejecuta comandos via HTTP, prueba múltiples estrategias, escala al Congreso si falla
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BuildD8Slave:
    """
    Gestor inteligente de instalación de slaves
    Estrategias: Docker → VEnv → Python directo
    Escalamiento: Congreso → HumanRequest
    """
    
    def __init__(self, slave_host: str, slave_port: int = 7600, token: str = "default-dev-token-change-in-production"):
        self.slave_host = slave_host
        self.slave_port = slave_port
        self.token = token
        self.base_url = f"http://{slave_host}:{slave_port}"
        
        # Logs
        self.logs_dir = Path.home() / "Documents" / "d8_data" / "build_logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.build_log = []
        self.current_strategy = None
        
    def execute_command(self, command: str, working_dir: Optional[str] = None, timeout: int = 300) -> Dict:
        """
        Ejecuta comando en el slave via HTTP
        
        Returns:
            {
                "success": bool,
                "stdout": str,
                "stderr": str,
                "exit_code": int
            }
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/execute",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "command": command,
                    "working_dir": working_dir
                },
                timeout=timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Log
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "command": command,
                    "result": result
                }
                self.build_log.append(log_entry)
                
                return result
            else:
                error_result = {
                    "success": False,
                    "stdout": "",
                    "stderr": f"HTTP {response.status_code}: {response.text}",
                    "exit_code": -1
                }
                self.build_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "command": command,
                    "result": error_result
                })
                return error_result
                
        except Exception as e:
            error_result = {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1
            }
            self.build_log.append({
                "timestamp": datetime.now().isoformat(),
                "command": command,
                "result": error_result
            })
            return error_result
    
    def check_connectivity(self) -> bool:
        """Verifica que el slave responda"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def verify_prerequisites(self) -> Tuple[bool, List[str]]:
        """Verifica Python y Git"""
        logger.info("🔍 Verificando prerequisitos...")
        
        missing = []
        
        # Python
        result = self.execute_command("python3 --version")
        if not result["success"]:
            missing.append("python3")
            logger.warning("⚠️  Python 3 no encontrado")
        else:
            logger.info(f"✅ Python: {result['stdout'].strip()}")
        
        # Git
        result = self.execute_command("git --version")
        if not result["success"]:
            missing.append("git")
            logger.warning("⚠️  Git no encontrado")
        else:
            logger.info(f"✅ Git: {result['stdout'].strip()}")
        
        return len(missing) == 0, missing
    
    def install_prerequisites(self, missing: List[str]) -> bool:
        """Instala Python/Git según el OS"""
        logger.info("📦 Instalando prerequisitos...")
        
        # Detectar OS
        os_result = self.execute_command("cat /etc/os-release || uname -s")
        os_info = os_result["stdout"].lower()
        
        install_commands = []
        
        if "debian" in os_info or "ubuntu" in os_info or "raspbian" in os_info:
            if "python3" in missing:
                install_commands.append("sudo apt-get update")
                install_commands.append("sudo apt-get install -y python3 python3-pip python3-venv")
            if "git" in missing:
                install_commands.append("sudo apt-get install -y git")
        elif "fedora" in os_info or "centos" in os_info or "rhel" in os_info:
            if "python3" in missing:
                install_commands.append("sudo dnf install -y python3 python3-pip")
            if "git" in missing:
                install_commands.append("sudo dnf install -y git")
        else:
            logger.error(f"❌ OS no soportado: {os_info}")
            return False
        
        # Ejecutar instalación
        for cmd in install_commands:
            logger.info(f"⏳ Ejecutando: {cmd}")
            result = self.execute_command(cmd, timeout=600)
            if not result["success"]:
                logger.error(f"❌ Falló: {result['stderr']}")
                return False
        
        return True
    
    def clone_repository(self, git_token: str, branch: str = "docker-workers") -> bool:
        """Clona repositorio D8"""
        logger.info("📥 Clonando repositorio D8...")
        
        d8_dir = "~/d8"
        
        # Verificar si el directorio existe y tiene .git
        check = self.execute_command(f"[ -d {d8_dir}/.git ] && echo 'exists' || echo 'not_exists'")
        
        if "exists" in check["stdout"]:
            logger.info("ℹ️  Repositorio d8 ya existe, actualizando...")
            # Actualizar repositorio existente
            pull_result = self.execute_command(
                f"cd {d8_dir} && git fetch origin && git checkout {branch} && git pull origin {branch}",
                working_dir=d8_dir,
                timeout=600
            )
            
            if pull_result["success"]:
                logger.info("✅ Repositorio actualizado")
                return True
            else:
                logger.warning(f"⚠️  Error al actualizar, intentando clonar desde cero: {pull_result['stderr']}")
                # Si falla el pull, eliminar y clonar desde cero
                self.execute_command(f"rm -rf {d8_dir}")
        
        # Clonar repositorio
        repo_url = f"https://{git_token}@github.com/lsilva5455/d8.git"
        clone_result = self.execute_command(
            f"git clone --branch {branch} {repo_url} {d8_dir}",
            timeout=600
        )
        
        if clone_result["success"]:
            logger.info("✅ Repositorio clonado")
            return True
        else:
            logger.error(f"❌ Error al clonar: {clone_result['stderr']}")
            return False
    
    def strategy_docker(self) -> Tuple[bool, str]:
        """ESTRATEGIA A: Instalación con Docker"""
        logger.info("🐳 ESTRATEGIA A: Docker")
        self.current_strategy = "docker"
        
        # Verificar Docker
        result = self.execute_command("docker --version")
        if not result["success"]:
            logger.info("📦 Docker no instalado, instalando...")
            
            # Instalar Docker
            install_result = self.execute_command(
                "curl -fsSL https://get.docker.com | sh",
                timeout=900
            )
            
            if not install_result["success"]:
                return False, "No se pudo instalar Docker"
            
            # Agregar usuario a grupo docker
            self.execute_command("sudo usermod -aG docker $USER")
            logger.info("✅ Docker instalado")
        
        # Docker Compose
        result = self.execute_command("docker-compose --version")
        if not result["success"]:
            logger.info("📦 Instalando docker-compose...")
            self.execute_command(
                "sudo apt-get install -y docker-compose || sudo pip3 install docker-compose",
                timeout=600
            )
        
        # Levantar servicios
        logger.info("🚀 Iniciando servicios con docker-compose...")
        result = self.execute_command(
            "cd $HOME/d8 && docker-compose up -d",
            timeout=900
        )
        
        if result["success"]:
            logger.info("✅ Servicios Docker iniciados")
            return True, "Docker funcionando correctamente"
        else:
            return False, f"Error al iniciar Docker: {result['stderr']}"
    
    def strategy_venv(self) -> Tuple[bool, str]:
        """ESTRATEGIA B: Instalación con venv"""
        logger.info("🐍 ESTRATEGIA B: VEnv")
        self.current_strategy = "venv"
        
        # Obtener directorio home absoluto
        home_result = self.execute_command("echo $HOME")
        if not home_result["success"]:
            return False, "No se pudo obtener $HOME"
        
        home_dir = home_result["stdout"].strip()
        d8_dir = f"{home_dir}/d8"
        
        # Crear venv
        logger.info("📦 Creando entorno virtual...")
        result = self.execute_command(f"python3 -m venv venv", working_dir=d8_dir, timeout=300)
        
        if not result["success"]:
            return False, f"No se pudo crear venv: {result['stderr']}"
        
        # Instalar dependencias (sin --upgrade para ser más rápido)
        logger.info("📦 Instalando dependencias...")
        result = self.execute_command(
            f"./venv/bin/pip install -r requirements.txt",
            working_dir=d8_dir,
            timeout=300
        )
        
        if not result["success"]:
            return False, f"Error instalando dependencias: {result['stderr']}"
        
        # Configurar .env (básico)
        logger.info("⚙️  Configurando .env...")
        self.execute_command("""cat > .env << 'EOF'
SLAVE_HOST=0.0.0.0
SLAVE_PORT=7600
LOG_LEVEL=INFO
EOF""", working_dir=d8_dir)
        
        # Iniciar slave_server
        logger.info("🚀 Iniciando slave server...")
        result = self.execute_command(
            f"nohup ./venv/bin/python app/distributed/slave_server.py > slave.log 2>&1 &",
            working_dir=d8_dir,
            timeout=30
        )
        
        # Verificar que inició
        time.sleep(3)
        check = self.execute_command("pgrep -f slave_server.py")
        
        if check["success"] and check["stdout"].strip():
            logger.info("✅ Slave server iniciado con venv")
            return True, "VEnv funcionando correctamente"
        else:
            return False, "Slave server no se inició correctamente"
    
    def strategy_native(self) -> Tuple[bool, str]:
        """ESTRATEGIA C: Instalación nativa (sin venv)"""
        logger.info("🔧 ESTRATEGIA C: Python Nativo")
        self.current_strategy = "native"
        
        d8_dir = "$HOME/d8"
        
        # Instalar dependencias sin venv
        logger.info("📦 Instalando dependencias (--user)...")
        result = self.execute_command(
            f"cd {d8_dir} && pip3 install --user -r requirements.txt",
            timeout=900
        )
        
        if not result["success"]:
            return False, f"Error instalando dependencias: {result['stderr']}"
        
        # Configurar .env
        self.execute_command(f"""cd {d8_dir} && cat > .env << 'EOF'
SLAVE_HOST=0.0.0.0
SLAVE_PORT=7600
LOG_LEVEL=INFO
EOF""")
        
        # Iniciar slave_server
        logger.info("🚀 Iniciando slave server...")
        result = self.execute_command(
            f"cd {d8_dir} && nohup python3 app/distributed/slave_server.py > slave.log 2>&1 &",
            timeout=30
        )
        
        # Verificar
        time.sleep(3)
        check = self.execute_command("pgrep -f slave_server.py")
        
        if check["success"] and check["stdout"].strip():
            logger.info("✅ Slave server iniciado nativamente")
            return True, "Python nativo funcionando correctamente"
        else:
            return False, "Slave server no se inició correctamente"
    
    def save_build_log(self, slave_id: str, status: str, error_msg: Optional[str] = None):
        """Guarda log completo de la instalación"""
        log_file = self.logs_dir / f"{slave_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_data = {
            "slave_id": slave_id,
            "slave_host": self.slave_host,
            "slave_port": self.slave_port,
            "status": status,
            "strategy_used": self.current_strategy,
            "error": error_msg,
            "build_log": self.build_log,
            "timestamp": datetime.now().isoformat()
        }
        
        log_file.write_text(json.dumps(log_data, indent=2))
        logger.info(f"📝 Log guardado en: {log_file}")
        
        return log_file
    
    def escalate_to_congress(self, slave_id: str, log_file: Path):
        """Escala el problema al Congreso Autónomo"""
        logger.info("📢 Escalando al Congreso Autónomo...")
        
        try:
            from app.congress.human_request import HumanRequestManager
            
            manager = HumanRequestManager()
            
            request_id = manager.create_request(
                title=f"Fallo en instalación de slave: {slave_id}",
                description=f"""
La instalación del slave {slave_id} ({self.slave_host}) falló después de intentar todas las estrategias.

**Estrategias probadas:**
1. Docker - Falló
2. VEnv - Falló  
3. Python Nativo - Falló

**Log completo:** {log_file}

**Acción requerida:**
1. Analizar logs de instalación
2. Identificar causa raíz del fallo
3. Proponer solución alternativa
4. Si no es posible resolver, notificar a Leo via Telegram

**Prioridad:** ALTA (infraestructura crítica)
                """,
                priority="high",
                category="infrastructure"
            )
            
            logger.info(f"✅ HumanRequest creada: {request_id}")
            logger.info("💡 El Congreso procesará esto cuando esté disponible")
            
            return request_id
            
        except Exception as e:
            logger.error(f"❌ Error al crear HumanRequest: {e}")
            logger.error("⚠️  Guarda manualmente el log y revísalo")
            return None
    
    def build(self, slave_id: str, git_token: str, max_retries: int = 3) -> Dict:
        """
        Ejecuta proceso completo de instalación
        
        Returns:
            {
                "success": bool,
                "strategy": str,
                "message": str,
                "log_file": str
            }
        """
        logger.info("="*60)
        logger.info(f"🚀 BUILD D8 SLAVE: {slave_id}")
        logger.info(f"📍 Host: {self.slave_host}:{self.slave_port}")
        logger.info("="*60)
        
        # 1. Verificar conectividad
        logger.info("\n1️⃣  Verificando conectividad...")
        if not self.check_connectivity():
            error_msg = "No se puede conectar al slave. Verifica que esté encendido y accesible."
            logger.error(f"❌ {error_msg}")
            log_file = self.save_build_log(slave_id, "failed_connectivity", error_msg)
            return {
                "success": False,
                "strategy": None,
                "message": error_msg,
                "log_file": str(log_file)
            }
        
        logger.info("✅ Slave responde correctamente")
        
        # 2. Verificar prerequisitos
        logger.info("\n2️⃣  Verificando prerequisitos...")
        has_prereqs, missing = self.verify_prerequisites()
        
        if not has_prereqs:
            logger.info(f"📦 Faltan: {', '.join(missing)}")
            if not self.install_prerequisites(missing):
                error_msg = f"No se pudieron instalar prerequisitos: {missing}"
                logger.error(f"❌ {error_msg}")
                log_file = self.save_build_log(slave_id, "failed_prerequisites", error_msg)
                self.escalate_to_congress(slave_id, log_file)
                return {
                    "success": False,
                    "strategy": None,
                    "message": error_msg,
                    "log_file": str(log_file)
                }
        
        # 3. Clonar repositorio
        logger.info("\n3️⃣  Clonando repositorio...")
        if not self.clone_repository(git_token):
            error_msg = "No se pudo clonar el repositorio D8"
            logger.error(f"❌ {error_msg}")
            log_file = self.save_build_log(slave_id, "failed_clone", error_msg)
            self.escalate_to_congress(slave_id, log_file)
            return {
                "success": False,
                "strategy": None,
                "message": error_msg,
                "log_file": str(log_file)
            }
        
        # 4. Probar estrategias secuencialmente
        strategies = [
            ("docker", self.strategy_docker),
            ("venv", self.strategy_venv),
            ("native", self.strategy_native)
        ]
        
        for strategy_name, strategy_func in strategies:
            logger.info(f"\n4️⃣  Probando estrategia: {strategy_name.upper()}")
            
            for attempt in range(max_retries):
                logger.info(f"   Intento {attempt + 1}/{max_retries}")
                
                success, message = strategy_func()
                
                if success:
                    logger.info(f"✅ {message}")
                    log_file = self.save_build_log(slave_id, "success", None)
                    return {
                        "success": True,
                        "strategy": strategy_name,
                        "message": message,
                        "log_file": str(log_file)
                    }
                else:
                    logger.warning(f"⚠️  Intento {attempt + 1} falló: {message}")
                    if attempt < max_retries - 1:
                        logger.info("⏳ Esperando 1s antes de reintentar...")
                        time.sleep(1)
            
            logger.error(f"❌ Estrategia {strategy_name} falló después de {max_retries} intentos")
        
        # 5. TODAS las estrategias fallaron
        error_msg = "Todas las estrategias de instalación fallaron"
        logger.error(f"\n❌ {error_msg}")
        logger.info("📢 Escalando al Congreso Autónomo...")
        
        log_file = self.save_build_log(slave_id, "failed_all_strategies", error_msg)
        request_id = self.escalate_to_congress(slave_id, log_file)
        
        return {
            "success": False,
            "strategy": None,
            "message": error_msg,
            "log_file": str(log_file),
            "escalated": True,
            "request_id": request_id
        }


def main():
    """CLI para testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build D8 Slave via HTTP")
    parser.add_argument("slave_host", help="IP del slave")
    parser.add_argument("--port", type=int, default=7600, help="Puerto del slave")
    parser.add_argument("--slave-id", help="ID del slave")
    parser.add_argument("--git-token", required=True, help="Token de GitHub")
    
    args = parser.parse_args()
    
    slave_id = args.slave_id or f"slave-{args.slave_host.replace('.', '-')}"
    
    builder = BuildD8Slave(args.slave_host, args.port)
    result = builder.build(slave_id, args.git_token)
    
    print("\n" + "="*60)
    print("📊 RESULTADO FINAL")
    print("="*60)
    print(json.dumps(result, indent=2))
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    exit(main())
