#!/usr/bin/env python3
"""
D8 System Launcher
Punto de entrada único para iniciar el sistema D8

"""
import sys
import subprocess
import json
from pathlib import Path

# Cargar información de versión desde archivo
def load_version_info():
    """Carga versión y branch desde version_info.json"""
    version_file = Path(__file__).parent / "version_info.json"
    
    if version_file.exists():
        try:
            info = json.loads(version_file.read_text(encoding='utf-8'))
            return info.get('version', '0.0.5'), info.get('branch', 'main')
        except:
            pass
    
    # Valores por defecto si no existe el archivo
    return "0.0.0.0.0", "main"

VERSION, BRANCH = load_version_info()

def show_menu():
    """Muestra menú de opciones"""
    print("\n" + "="*60)
    print(f"🤖 D8 - SISTEMA DE IA AUTÓNOMO v{VERSION} [{BRANCH}]")
    print("="*60)
    print("\n¿Qué componente quieres ejecutar?\n")
    print("1. 🏛️  Congreso Autónomo (Mejora continua)")
    print("2. 💎 Niche Discovery (Descubrir nichos)")
    print("3. 🧬 Sistema Evolutivo (Darwin)")
    print("4. 🌐 Orchestrator + Worker (Sistema completo)")
    print("5. ❌ Salir")
    print("\n" + "="*60)
    
    choice = input("\nSelecciona una opción (1-5): ").strip()
    return choice

def run_congress():
    """Ejecuta el congreso autónomo"""
    print("\n🏛️  Iniciando Congreso Autónomo...")
    print("El congreso investigará, experimentará y mejorará el sistema.\n")
    
    script_path = Path(__file__).parent / "scripts" / "autonomous_congress.py"
    subprocess.run([sys.executable, str(script_path)])

def run_niche_discovery():
    """Ejecuta niche discovery"""
    print("\n💎 Iniciando Niche Discovery...")
    print("Analizando mercados y descubriendo oportunidades...\n")
    
    script_path = Path(__file__).parent / "scripts" / "niche_discovery_agent.py"
    subprocess.run([sys.executable, str(script_path)])

def run_evolution():
    """Ejecuta sistema evolutivo"""
    print("\n🧬 Iniciando Sistema Evolutivo...")
    print("Evolucionando agentes mediante selección natural...\n")
    
    subprocess.run([sys.executable, "-m", "app.evolution.groq_evolution"])

def run_distributed():
    """Ejecuta sistema completo"""
    print("\n🌐 Iniciando Sistema Distribuido...")
    print("\nIMPORTANTE: Debes ejecutar en terminales separadas:")
    print("\nTerminal 1 (Orchestrator):")
    print("  python -m app.main")
    print("\nTerminal 2 (Worker):")
    print("  python -m app.distributed.worker_groq")
    print("\nO usa el launcher automático:")
    print("  .\\scripts\\launch\\launch_distributed.bat")
    print()

def main():
    """Función principal"""
    while True:
        choice = show_menu()
        
        if choice == "1":
            run_congress()
        elif choice == "2":
            run_niche_discovery()
        elif choice == "3":
            run_evolution()
        elif choice == "4":
            run_distributed()
        elif choice == "5":
            print("\n👋 ¡Hasta luego!\n")
            sys.exit(0)
        else:
            print("\n❌ Opción inválida. Selecciona 1-5.\n")
            continue
        
        # Preguntar si quiere continuar
        again = input("\n¿Ejecutar otro componente? (s/n): ").strip().lower()
        if again != 's':
            print("\n👋 ¡Hasta luego!\n")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrumpido por el usuario. ¡Hasta luego!\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)
