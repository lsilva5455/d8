#!/usr/bin/env python3
"""
D8 Docker Setup Validation
===========================
Verifica que la configuración Docker esté lista para deployment
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")

def print_check(passed: bool, message: str):
    icon = "✅" if passed else "❌"
    color = Colors.GREEN if passed else Colors.RED
    print(f"{color}{icon} {message}{Colors.ENDC}")

def check_file_exists(path: Path, description: str) -> bool:
    exists = path.exists()
    print_check(exists, f"{description}: {path}")
    return exists

def validate_structure() -> List[bool]:
    """Validate Docker directory structure"""
    print_header("Validando Estructura de Archivos")
    
    checks = []
    
    # Dockerfiles
    checks.append(check_file_exists(Path("docker/Dockerfile.orchestrator"), "Dockerfile Orchestrator"))
    checks.append(check_file_exists(Path("docker/Dockerfile.worker"), "Dockerfile Worker"))
    checks.append(check_file_exists(Path("docker/Dockerfile.worker-deepseek"), "Dockerfile Worker DeepSeek"))
    
    # Entrypoints
    checks.append(check_file_exists(Path("docker/entrypoint-orchestrator.sh"), "Entrypoint Orchestrator"))
    checks.append(check_file_exists(Path("docker/entrypoint-worker.sh"), "Entrypoint Worker"))
    checks.append(check_file_exists(Path("docker/entrypoint-worker-deepseek.sh"), "Entrypoint Worker DeepSeek"))
    
    # Config templates
    checks.append(check_file_exists(Path("docker/.env.orchestrator.template"), "Template Orchestrator"))
    checks.append(check_file_exists(Path("docker/.env.worker-groq.template"), "Template Worker Groq"))
    checks.append(check_file_exists(Path("docker/.env.worker-gemini.template"), "Template Worker Gemini"))
    checks.append(check_file_exists(Path("docker/.env.worker-deepseek.template"), "Template Worker DeepSeek"))
    
    # Docker Compose
    checks.append(check_file_exists(Path("docker-compose.yml"), "Docker Compose"))
    
    # Scripts
    checks.append(check_file_exists(Path("scripts/setup/setup_worker.py"), "Setup Script Python"))
    checks.append(check_file_exists(Path("scripts/setup/setup_worker.sh"), "Setup Script Bash"))
    
    # Documentation
    checks.append(check_file_exists(Path("docs/02_setup/docker_deployment.md"), "Documentación Docker"))
    checks.append(check_file_exists(Path("docker/README.md"), "Docker README"))
    
    # Support files
    checks.append(check_file_exists(Path(".dockerignore"), "Docker Ignore"))
    checks.append(check_file_exists(Path("Makefile"), "Makefile"))
    
    return checks

def validate_dockerfiles() -> List[bool]:
    """Validate Dockerfile syntax"""
    print_header("Validando Dockerfiles")
    
    checks = []
    dockerfiles = [
        "docker/Dockerfile.orchestrator",
        "docker/Dockerfile.worker",
        "docker/Dockerfile.worker-deepseek"
    ]
    
    for dockerfile in dockerfiles:
        path = Path(dockerfile)
        if not path.exists():
            print_check(False, f"No existe: {dockerfile}")
            checks.append(False)
            continue
        
        content = path.read_text()
        
        # Check for FROM
        has_from = "FROM" in content
        print_check(has_from, f"{dockerfile}: Tiene FROM")
        checks.append(has_from)
        
        # Check for WORKDIR
        has_workdir = "WORKDIR" in content
        print_check(has_workdir, f"{dockerfile}: Tiene WORKDIR")
        checks.append(has_workdir)
        
        # Check for COPY
        has_copy = "COPY" in content
        print_check(has_copy, f"{dockerfile}: Tiene COPY")
        checks.append(has_copy)
    
    return checks

def validate_compose() -> List[bool]:
    """Validate docker-compose.yml"""
    print_header("Validando Docker Compose")
    
    checks = []
    compose_file = Path("docker-compose.yml")
    
    if not compose_file.exists():
        print_check(False, "docker-compose.yml no existe")
        return [False]
    
    content = compose_file.read_text()
    
    # Check services
    services = ["orchestrator", "worker-groq", "worker-gemini", "worker-deepseek"]
    for service in services:
        exists = service in content
        print_check(exists, f"Servicio definido: {service}")
        checks.append(exists)
    
    # Check profiles
    profiles = ["orchestrator", "worker-groq", "worker-gemini", "worker-deepseek", "full-system"]
    for profile in profiles:
        exists = profile in content
        print_check(exists, f"Perfil definido: {profile}")
        checks.append(exists)
    
    # Check networks
    has_networks = "networks:" in content
    print_check(has_networks, "Tiene definición de networks")
    checks.append(has_networks)
    
    # Check volumes
    has_volumes = "volumes:" in content
    print_check(has_volumes, "Tiene definición de volumes")
    checks.append(has_volumes)
    
    return checks

def validate_scripts() -> List[bool]:
    """Validate setup scripts"""
    print_header("Validando Scripts de Setup")
    
    checks = []
    
    # Python script
    py_script = Path("scripts/setup/setup_worker.py")
    if py_script.exists():
        content = py_script.read_text()
        
        has_shebang = content.startswith("#!/usr/bin/env python3")
        print_check(has_shebang, "setup_worker.py: Tiene shebang")
        checks.append(has_shebang)
        
        has_argparse = "argparse" in content
        print_check(has_argparse, "setup_worker.py: Usa argparse")
        checks.append(has_argparse)
        
        has_main = "def main()" in content
        print_check(has_main, "setup_worker.py: Tiene función main")
        checks.append(has_main)
    else:
        checks.append(False)
    
    # Bash script
    sh_script = Path("scripts/setup/setup_worker.sh")
    if sh_script.exists():
        content = sh_script.read_text()
        
        has_shebang = content.startswith("#!/bin/bash")
        print_check(has_shebang, "setup_worker.sh: Tiene shebang")
        checks.append(has_shebang)
        
        has_set_e = "set -e" in content
        print_check(has_set_e, "setup_worker.sh: Tiene set -e")
        checks.append(has_set_e)
    else:
        checks.append(False)
    
    return checks

def validate_permissions() -> List[bool]:
    """Validate file permissions (Unix only)"""
    if os.name != 'posix':
        print(f"{Colors.YELLOW}⚠️  Validación de permisos omitida (no es sistema Unix){Colors.ENDC}")
        return []
    
    print_header("Validando Permisos de Archivos")
    
    checks = []
    executable_files = [
        "scripts/setup/setup_worker.sh",
        "docker/entrypoint-orchestrator.sh",
        "docker/entrypoint-worker.sh",
        "docker/entrypoint-worker-deepseek.sh",
        "docker/init-ollama.sh"
    ]
    
    for file_path in executable_files:
        path = Path(file_path)
        if path.exists():
            is_executable = os.access(path, os.X_OK)
            print_check(is_executable, f"{file_path}: Ejecutable")
            checks.append(is_executable)
            
            if not is_executable:
                print(f"   💡 Solución: chmod +x {file_path}")
        else:
            checks.append(False)
    
    return checks

def main():
    print(f"\n{Colors.BOLD}D8 Docker Setup Validation{Colors.ENDC}")
    print(f"{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")
    
    all_checks = []
    
    # Run validations
    all_checks.extend(validate_structure())
    all_checks.extend(validate_dockerfiles())
    all_checks.extend(validate_compose())
    all_checks.extend(validate_scripts())
    all_checks.extend(validate_permissions())
    
    # Summary
    print_header("Resumen")
    
    total = len(all_checks)
    passed = sum(all_checks)
    failed = total - passed
    
    print(f"Total de verificaciones: {total}")
    print(f"{Colors.GREEN}✅ Pasadas: {passed}{Colors.ENDC}")
    
    if failed > 0:
        print(f"{Colors.RED}❌ Fallidas: {failed}{Colors.ENDC}")
    
    percentage = (passed / total * 100) if total > 0 else 0
    print(f"\n{Colors.BOLD}Completitud: {percentage:.1f}%{Colors.ENDC}")
    
    if percentage == 100:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ¡Configuración Docker lista para deployment!{Colors.ENDC}")
        return 0
    elif percentage >= 90:
        print(f"\n{Colors.YELLOW}⚠️  Casi listo. Revisa los elementos fallidos.{Colors.ENDC}")
        return 1
    else:
        print(f"\n{Colors.RED}❌ Configuración incompleta. Revisa los errores.{Colors.ENDC}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
