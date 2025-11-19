#!/usr/bin/env python3
"""
Captura información de versión desde Git y la guarda en version_info.json
Ejecutar esto antes de hacer commit/push para deployment
"""
import subprocess
import json
from pathlib import Path
from datetime import datetime

def get_git_info():
    """Obtiene información actual de Git"""
    info = {}
    
    try:
        # Branch actual
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, check=True
        )
        info['branch'] = result.stdout.strip() or "main"
    except:
        info['branch'] = "unknown"
    
    try:
        # Commit hash (corto)
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True
        )
        info['commit'] = result.stdout.strip()
    except:
        info['commit'] = "unknown"
    
    try:
        # Intentar obtener tag (versión)
        result = subprocess.run(
            ["git", "describe", "--tags", "--exact-match"],
            capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            info['version'] = result.stdout.strip()
        else:
            # Si no hay tag exacto, leer de version_info.json existente o usar default
            version_file = Path(__file__).parent.parent.parent / "version_info.json"
            if version_file.exists():
                existing = json.loads(version_file.read_text())
                info['version'] = existing.get('version', '0.0.5')
            else:
                info['version'] = '0.0.5'
    except:
        info['version'] = '0.0.5'
    
    info['deployed_at'] = datetime.utcnow().isoformat() + 'Z'
    
    return info

def save_version_info(info):
    """Guarda información en version_info.json"""
    version_file = Path(__file__).parent.parent.parent / "version_info.json"
    
    with open(version_file, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2)
    
    print("✅ Información de versión capturada:")
    print(f"   Version: {info['version']}")
    print(f"   Branch:  {info['branch']}")
    print(f"   Commit:  {info['commit']}")
    print(f"   Fecha:   {info['deployed_at']}")
    print(f"\n📁 Guardado en: {version_file}")

def main():
    """Función principal"""
    print("\n🔖 Capturando información de versión desde Git...\n")
    
    info = get_git_info()
    save_version_info(info)
    
    print("\n💡 TIP: Ejecuta este script antes de hacer push para deployment")
    print("   Ejemplo: python scripts/setup/capture_version.py")

if __name__ == "__main__":
    main()
