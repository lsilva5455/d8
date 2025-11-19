#!/usr/bin/env python3
"""
D8 Worker Setup Script
======================
Configura automáticamente un nodo worker de D8 en cualquier máquina Linux.
Especializado para Raspberry Pi 4 con DeepSeek, pero soporta otros tipos.

Uso:
    python setup_worker.py --type deepseek --orchestrator http://192.168.1.100:5000
    python setup_worker.py --type groq --api-key gsk_xxx --orchestrator http://192.168.1.100:5000
"""

import os
import sys
import argparse
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Optional, Dict
import json


class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(text: str):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text: str):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text: str):
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def run_command(cmd: str, check: bool = True) -> tuple[int, str, str]:
    """Execute shell command and return (returncode, stdout, stderr)"""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True
    )
    
    if check and result.returncode != 0:
        print_error(f"Command failed: {cmd}")
        print_error(f"Error: {result.stderr}")
        sys.exit(1)
    
    return result.returncode, result.stdout, result.stderr


def check_requirements():
    """Check system requirements"""
    print_header("Verificando Requisitos del Sistema")
    
    # Check OS
    if platform.system() != "Linux":
        print_error("Este script solo funciona en Linux")
        print_info(f"Sistema detectado: {platform.system()}")
        sys.exit(1)
    
    print_success(f"Sistema operativo: {platform.system()} {platform.release()}")
    
    # Check architecture
    arch = platform.machine()
    print_success(f"Arquitectura: {arch}")
    
    if arch not in ['x86_64', 'aarch64', 'armv7l']:
        print_warning(f"Arquitectura no probada: {arch}")
    
    # Check Docker
    if shutil.which('docker') is None:
        print_error("Docker no está instalado")
        print_info("Instala Docker: https://docs.docker.com/engine/install/")
        sys.exit(1)
    
    print_success("Docker instalado")
    
    # Check Docker Compose
    ret, stdout, _ = run_command("docker compose version", check=False)
    if ret != 0:
        print_error("Docker Compose no está instalado")
        print_info("Instala Docker Compose: https://docs.docker.com/compose/install/")
        sys.exit(1)
    
    print_success(f"Docker Compose instalado: {stdout.strip()}")
    
    # Check Docker daemon
    ret, _, _ = run_command("docker ps", check=False)
    if ret != 0:
        print_error("Docker daemon no está corriendo")
        print_info("Inicia Docker: sudo systemctl start docker")
        sys.exit(1)
    
    print_success("Docker daemon corriendo")
    
    # Check available memory
    with open('/proc/meminfo', 'r') as f:
        meminfo = f.read()
        for line in meminfo.split('\n'):
            if 'MemTotal' in line:
                mem_kb = int(line.split()[1])
                mem_gb = mem_kb / 1024 / 1024
                print_success(f"Memoria disponible: {mem_gb:.1f} GB")
                
                if mem_gb < 4:
                    print_warning("Se recomienda al menos 4GB RAM para DeepSeek")
                break


def detect_device():
    """Detect if running on Raspberry Pi"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'Raspberry Pi' in cpuinfo:
                # Extract model
                for line in cpuinfo.split('\n'):
                    if 'Model' in line:
                        model = line.split(':')[1].strip()
                        print_info(f"Dispositivo detectado: {model}")
                        return 'raspberry_pi'
    except:
        pass
    
    return 'generic'


def create_env_file(worker_type: str, orchestrator_url: str, api_key: Optional[str] = None) -> Path:
    """Create .env file for worker"""
    print_header(f"Creando Configuración para Worker {worker_type.upper()}")
    
    template_file = Path(f"docker/.env.worker-{worker_type}.template")
    if not template_file.exists():
        print_error(f"Template no encontrado: {template_file}")
        sys.exit(1)
    
    # Read template
    with open(template_file, 'r') as f:
        content = f.read()
    
    # Replace placeholders
    content = content.replace(
        'ORCHESTRATOR_URL=http://192.168.1.100:5000',
        f'ORCHESTRATOR_URL={orchestrator_url}'
    )
    
    if api_key:
        if worker_type == 'groq':
            content = content.replace('GROQ_API_KEY=your_groq_api_key_here', f'GROQ_API_KEY={api_key}')
        elif worker_type == 'gemini':
            content = content.replace('GEMINI_API_KEY=your_gemini_api_key_here', f'GEMINI_API_KEY={api_key}')
    
    # Generate unique worker ID
    import socket
    worker_id = f"{worker_type}-{socket.gethostname()}"
    content = content.replace(f'{worker_type}-worker-1', worker_id)
    
    # Write .env file
    env_file = Path('.env.worker')
    with open(env_file, 'w') as f:
        f.write(content)
    
    print_success(f"Configuración creada: {env_file}")
    print_info(f"Worker ID: {worker_id}")
    
    return env_file


def build_worker_image(worker_type: str):
    """Build Docker image for worker"""
    print_header(f"Construyendo Imagen Docker para {worker_type.upper()}")
    
    if worker_type == 'deepseek':
        dockerfile = 'docker/Dockerfile.worker-deepseek'
    else:
        dockerfile = 'docker/Dockerfile.worker'
    
    image_name = f"d8-worker-{worker_type}"
    
    print_info(f"Construyendo imagen: {image_name}")
    print_info("Esto puede tomar varios minutos...")
    
    cmd = f"docker build -f {dockerfile} -t {image_name}"
    if worker_type != 'deepseek':
        cmd += f" --build-arg WORKER_TYPE={worker_type}"
    cmd += " ."
    
    ret, stdout, stderr = run_command(cmd, check=False)
    
    if ret != 0:
        print_error("Falló la construcción de la imagen")
        print(stderr)
        sys.exit(1)
    
    print_success(f"Imagen construida: {image_name}")


def start_worker(worker_type: str):
    """Start worker container"""
    print_header(f"Iniciando Worker {worker_type.upper()}")
    
    profile = f"worker-{worker_type}"
    
    print_info(f"Iniciando con perfil: {profile}")
    
    cmd = f"docker compose --profile {profile} up -d"
    ret, stdout, stderr = run_command(cmd, check=False)
    
    if ret != 0:
        print_error("Falló el inicio del worker")
        print(stderr)
        sys.exit(1)
    
    print_success("Worker iniciado correctamente")
    
    # Show logs
    print_info("\nMostrando logs (Ctrl+C para salir):")
    container_name = f"d8-worker-{worker_type}"
    os.system(f"docker logs -f {container_name}")


def create_systemd_service(worker_type: str):
    """Create systemd service for auto-start on boot"""
    print_header("Creando Servicio Systemd (Opcional)")
    
    response = input("¿Deseas crear un servicio systemd para inicio automático? (y/N): ")
    if response.lower() != 'y':
        print_info("Saltando creación de servicio systemd")
        return
    
    service_content = f"""[Unit]
Description=D8 Worker {worker_type.upper()}
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory={Path.cwd()}
ExecStart=/usr/bin/docker compose --profile worker-{worker_type} up -d
ExecStop=/usr/bin/docker compose --profile worker-{worker_type} down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path(f"/tmp/d8-worker-{worker_type}.service")
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print_info(f"Servicio creado en: {service_file}")
    print_info("\nPara instalar, ejecuta:")
    print(f"    sudo cp {service_file} /etc/systemd/system/")
    print(f"    sudo systemctl daemon-reload")
    print(f"    sudo systemctl enable d8-worker-{worker_type}")
    print(f"    sudo systemctl start d8-worker-{worker_type}")


def main():
    parser = argparse.ArgumentParser(
        description='D8 Worker Setup - Configuración automática de nodo worker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Worker DeepSeek en Raspberry Pi 4
  python setup_worker.py --type deepseek --orchestrator http://192.168.1.100:5000
  
  # Worker Groq (requiere API key)
  python setup_worker.py --type groq --api-key gsk_xxx --orchestrator http://192.168.1.100:5000
  
  # Worker Gemini
  python setup_worker.py --type gemini --api-key AIza_xxx --orchestrator http://192.168.1.100:5000
"""
    )
    
    parser.add_argument(
        '--type',
        choices=['deepseek', 'groq', 'gemini'],
        required=True,
        help='Tipo de worker a configurar'
    )
    
    parser.add_argument(
        '--orchestrator',
        required=True,
        help='URL del orchestrator (ej: http://192.168.1.100:5000)'
    )
    
    parser.add_argument(
        '--api-key',
        help='API key (requerido para groq y gemini)'
    )
    
    parser.add_argument(
        '--skip-build',
        action='store_true',
        help='Saltar construcción de imagen (usar imagen existente)'
    )
    
    parser.add_argument(
        '--no-start',
        action='store_true',
        help='No iniciar el worker automáticamente'
    )
    
    args = parser.parse_args()
    
    # Validate API key requirement
    if args.type in ['groq', 'gemini'] and not args.api_key:
        print_error(f"--api-key es requerido para worker tipo {args.type}")
        sys.exit(1)
    
    # Print header
    print_header("D8 Worker Setup")
    print(f"{Colors.BOLD}Worker Type:{Colors.ENDC} {args.type}")
    print(f"{Colors.BOLD}Orchestrator:{Colors.ENDC} {args.orchestrator}")
    print()
    
    # Check requirements
    check_requirements()
    
    # Detect device
    device = detect_device()
    if device == 'raspberry_pi' and args.type == 'deepseek':
        print_success("Raspberry Pi detectada - Configuración optimizada para DeepSeek")
    
    # Create .env file
    env_file = create_env_file(args.type, args.orchestrator, args.api_key)
    
    # Build image
    if not args.skip_build:
        build_worker_image(args.type)
    else:
        print_info("Saltando construcción de imagen")
    
    # Start worker
    if not args.no_start:
        start_worker(args.type)
    else:
        print_info("Worker configurado pero no iniciado")
        print_info(f"Para iniciar: docker compose --profile worker-{args.type} up -d")
    
    # Create systemd service
    create_systemd_service(args.type)
    
    # Final message
    print_header("Setup Completado")
    print_success("Worker configurado exitosamente")
    print_info("\nComandos útiles:")
    print(f"  Ver logs:    docker logs -f d8-worker-{args.type}")
    print(f"  Detener:     docker compose --profile worker-{args.type} down")
    print(f"  Reiniciar:   docker compose --profile worker-{args.type} restart")
    print(f"  Estado:      docker compose --profile worker-{args.type} ps")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
