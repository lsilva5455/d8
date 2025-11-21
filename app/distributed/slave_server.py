"""
Slave Server - Flask API for remote task execution
Runs on each slave machine, receives commands from master
"""

from flask import Flask, request, jsonify
import subprocess
import sys
import os
from pathlib import Path
import logging
import json
from typing import Dict, Any
import shutil

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token de autenticación
SLAVE_TOKEN = os.getenv("SLAVE_TOKEN", "default-dev-token-change-in-production")


def get_version_info() -> Dict[str, str]:
    """Lee version_info.json del directorio raíz"""
    version_file = Path(__file__).parent.parent.parent / "version_info.json"
    
    if version_file.exists():
        try:
            return json.loads(version_file.read_text())
        except Exception as e:
            logger.error(f"Error leyendo version_info.json: {e}")
            return {"commit": "unknown", "version": "unknown", "branch": "unknown"}
    else:
        return {"commit": "unknown", "version": "unknown", "branch": "unknown"}


def _validate_token(token: str) -> bool:
    """Valida token de autenticación"""
    return token == SLAVE_TOKEN


def _get_available_methods() -> Dict[str, bool]:
    """Detecta métodos de ejecución disponibles"""
    methods = {
        "docker": False,
        "venv": False,
        "python": False
    }
    
    # Docker
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            timeout=5
        )
        methods["docker"] = result.returncode == 0
    except:
        pass
    
    # venv
    venv_path = Path(__file__).parent.parent.parent / "venv"
    methods["venv"] = venv_path.exists()
    
    # Python
    methods["python"] = True  # Siempre disponible
    
    return methods


def _execute_in_docker(command: str, working_dir: str = "/app") -> Dict[str, Any]:
    """Ejecuta comando en Docker"""
    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{Path(__file__).parent.parent.parent}:/app",
                "-w", working_dir,
                "d8-slave",
                "python", "-c", command
            ],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos máximo
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "method": "docker"
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "method": "docker"
        }


def _execute_in_venv(command: str, working_dir: str = None) -> Dict[str, Any]:
    """Ejecuta comando en venv"""
    try:
        venv_python = Path(__file__).parent.parent.parent / "venv" / "Scripts" / "python.exe"
        if not venv_python.exists():
            venv_python = Path(__file__).parent.parent.parent / "venv" / "bin" / "python"
        
        work_dir = working_dir or str(Path(__file__).parent.parent.parent)
        
        result = subprocess.run(
            [str(venv_python), "-c", command],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=work_dir
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "method": "venv"
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "method": "venv"
        }


def _execute_in_python(command: str, working_dir: str = None) -> Dict[str, Any]:
    """Ejecuta comando en Python nativo"""
    try:
        work_dir = working_dir or str(Path(__file__).parent.parent.parent)
        
        result = subprocess.run(
            [sys.executable, "-c", command],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=work_dir
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "method": "python"
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "method": "python"
        }


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint"""
    version_info = get_version_info()
    return jsonify({
        "status": "healthy",
        "python_version": sys.version,
        "execution_methods": _get_available_methods(),
        "version": version_info["version"],
        "commit": version_info["commit"],
        "branch": version_info["branch"]
    })


@app.route("/api/version", methods=["GET"])
def version():
    """Endpoint específico para verificación de versiones"""
    return jsonify(get_version_info())


@app.route("/api/execute", methods=["POST"])
def execute():
    """Ejecuta tarea enviada por el master"""
    # Validar token
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not _validate_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    command = data.get("command")
    working_dir = data.get("working_dir")
    
    if not command:
        return jsonify({"error": "No command provided"}), 400
    
    # Detectar métodos disponibles
    methods = _get_available_methods()
    
    # Prioridad: Docker > venv > Python nativo
    result = None
    
    if methods["docker"]:
        logger.info("🐳 Ejecutando en Docker...")
        result = _execute_in_docker(command, working_dir)
    elif methods["venv"]:
        logger.info("🐍 Ejecutando en venv...")
        result = _execute_in_venv(command, working_dir)
    else:
        logger.info("🔧 Ejecutando en Python nativo...")
        result = _execute_in_python(command, working_dir)
    
    return jsonify(result)


@app.route("/api/install", methods=["POST"])
def install():
    """Endpoint para instalación remota (placeholder)"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not _validate_token(token):
        return jsonify({"error": "Unauthorized"}), 401
    
    # TODO: Implementar instalación remota
    return jsonify({
        "message": "Remote installation not yet implemented",
        "status": "pending"
    })


def main():
    """Inicia servidor Flask"""
    port = int(os.getenv("SLAVE_PORT", 7600))
    host = os.getenv("SLAVE_HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting Slave Server on {host}:{port}")
    logger.info(f"🔖 Version: {get_version_info()}")
    logger.info(f"🔧 Available methods: {_get_available_methods()}")
    
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
