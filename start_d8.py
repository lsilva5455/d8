#!/usr/bin/env python3
"""
D8 System Launcher
Punto de entrada único para iniciar el sistema D8
"""
import sys
import subprocess
import json
import os
from pathlib import Path
from datetime import datetime

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
    print("4. 🎯 Orchestrator (Servidor central)")
    print("5. 🔧 Gestión de Slaves (Agregar/Instalar/Ver)")
    print("6. 🔄 Supervisor D8 (Auto-restart de componentes)")
    print("7. ❌ Salir")
    print("\n" + "="*60)
    
    choice = input("\nSelecciona una opción (1-7): ").strip()
    return choice

def parse_arguments():
    """
    Parse command line arguments for direct component launch
    
    Uso:
        python start_d8.py                    # Menú interactivo
        python start_d8.py congress           # Lanzar congreso directamente
        python start_d8.py niche              # Lanzar niche discovery
        python start_d8.py evolution          # Lanzar evolución
        python start_d8.py orchestrator       # Lanzar orchestrator
        python start_d8.py slave              # Ejecutar slave server local
        python start_d8.py slaves             # Menú de gestión de slaves
        python start_d8.py supervisor         # Lanzar supervisor
    """
    if len(sys.argv) < 2:
        return None  # Modo interactivo
    
    command = sys.argv[1].lower()
    
    command_map = {
        'congress': '1',
        'niche': '2',
        'evolution': '3',
        'orchestrator': '4',
        'slave': 'slave_server',    # Ejecutar servidor directamente
        'slaves': '5',              # Menú de gestión
        'supervisor': '6',
        'quit': '7'
    }
    
    return command_map.get(command)

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

def run_orchestrator():
    """Ejecuta el orquestador de forma independiente"""
    print("\n🎯 Iniciando Orchestrator...")
    print("El orquestador gestiona workers y asigna tareas.\n")
    print("Endpoints disponibles:")
    print("  - POST /api/tasks/submit")
    print("  - GET /api/workers/list")
    print("  - GET /api/stats")
    print("  - GET /health\n")
    
    subprocess.run([sys.executable, "-m", "app.orchestrator_app"])

def run_slave_management():
    """
    Menú de gestión de slaves
    
    Opciones:
    - Ejecutar slave server local
    - Agregar nuevo slave remoto
    - Instalar D8 en slave remoto
    - Ver slaves registrados
    - Eliminar slave registrado
    """
    print("\n🔧 GESTIÓN DE SLAVES")
    print("=" * 60)
    print("\n¿Qué operación deseas realizar?\n")
    print("1. 🚀 Ejecutar Slave Server (local)")
    print("2. ➕ Agregar Slave Remoto")
    print("3. 📦 Instalar D8 en Slave Remoto (SSH automático)")
    print("4. 📄 Generar Instalador Manual (.sh/.bat)")
    print("5. 📋 Ver Slaves Registrados")
    print("6. 🗑️  Eliminar Slave Registrado")
    print("7. 🔙 Volver al menú principal")
    print("\n" + "=" * 60)
    
    choice = input("\nSelecciona una opción (1-7): ").strip()
    
    if choice == "1":
        run_slave_server()
    elif choice == "2":
        add_remote_slave()
    elif choice == "3":
        install_slave_remote()
    elif choice == "4":
        generate_slave_installer()
    elif choice == "5":
        check_slaves()
    elif choice == "6":
        remove_slave()
    elif choice == "7":
        return
    else:
        print("\n❌ Opción inválida.\n")

def run_slave_server():
    """
    Ejecuta el slave server local
    
    Este componente:
    - Expone API REST en puerto 7600
    - Recibe comandos del master (Raspberry Pi)
    - Ejecuta tareas distribuidas
    - Reporta health status
    """
    print("\n🚀 Iniciando Slave Server...")
    print("El slave server escucha en puerto 7600")
    print("Esperando comandos del master (Orchestrator)\n")
    print("Endpoints disponibles:")
    print("  - GET  /api/health")
    print("  - POST /api/execute")
    print("  - GET  /api/version\n")
    
    # Variables de entorno necesarias
    port = os.getenv("SLAVE_PORT", "7600")
    host = os.getenv("SLAVE_HOST", "0.0.0.0")
    
    print(f"📡 Listening on {host}:{port}")
    print("\nPresiona Ctrl+C para detener el slave server\n")
    
    # Lanzar slave server
    subprocess.run([sys.executable, "-m", "app.distributed.slave_server"])

def add_remote_slave():
    """Agregar un slave remoto al sistema"""
    print("\n➕ Agregar Slave Remoto")
    print("=" * 60)
    print("\nEste asistente te ayudará a registrar un slave remoto.")
    print("Asegúrate de que el slave ya tenga D8 instalado y slave_server corriendo.\n")
    
    # Mostrar nota sobre persistencia
    print("💾 NOTA: Los slaves se guardan automáticamente en:")
    print("   ~/Documents/d8_data/slaves/config.json")
    print("   No necesitas agregarlos cada vez que inicies el sistema.\n")
    
    script_path = Path(__file__).parent / "scripts" / "add_slave.py"
    subprocess.run([sys.executable, str(script_path)])

def install_slave_remote():
    """Instalar D8 en una máquina remota como slave"""
    print("\n📦 Instalar D8 en Slave Remoto")
    print("=" * 60)
    print("\nEste asistente instalará D8 automáticamente en una máquina remota.")
    print("Requiere acceso SSH a la máquina destino.\n")
    
    # Importar y ejecutar el instalador
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from app.distributed.build_d8_slave import main as build_slave_main
        build_slave_main()
    except ImportError as e:
        print(f"❌ Error importando build_d8_slave: {e}")
        print("\n💡 Verifica que el archivo exista en: app/distributed/build_d8_slave.py")
    except Exception as e:
        print(f"❌ Error ejecutando instalador: {e}")

def generate_slave_installer():
    """Genera instaladores manuales .sh (Linux) o .bat (Windows)"""
    print("\n📄 Generar Instalador Manual")
    print("=" * 60)
    print("\nEste asistente genera scripts de instalación para máquinas sin acceso SSH.")
    print("Los archivos generados incluyen toda la configuración necesaria.\n")
    
    print("Selecciona el tipo de instalador:")
    print("1. Linux (.sh)")
    print("2. Windows (.bat)")
    print("3. Ambos")
    print("4. Cancelar\n")
    
    choice = input("Opción (1-4): ").strip()
    
    if choice == "4":
        print("\n❌ Operación cancelada.\n")
        return
    
    # Importar y ejecutar el generador
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from scripts.setup.generate_slave_installer import SlaveInstallerGenerator
        
        generator = SlaveInstallerGenerator()
        output_dir = Path(__file__).parent / "scripts" / "setup"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if choice in ["1", "3"]:
            bash_script = output_dir / f"install_slave_{timestamp}.sh"
            generator.generate_bash_script(bash_script)
            print(f"\n✅ Script Linux generado: {bash_script}")
            print(f"\n📋 Para usar:")
            print(f"   1. Copia el archivo a la máquina remota (USB, SCP, etc.)")
            print(f"   2. Dale permisos: chmod +x install_slave_{timestamp}.sh")
            print(f"   3. Ejecuta: ./install_slave_{timestamp}.sh")
        
        if choice in ["2", "3"]:
            bat_script = output_dir / f"install_slave_{timestamp}.bat"
            generator.generate_batch_script(bat_script)
            print(f"\n✅ Script Windows generado: {bat_script}")
            print(f"\n📋 Para usar:")
            print(f"   1. Copia el archivo a la máquina remota (USB, red, etc.)")
            print(f"   2. Ejecuta como administrador: install_slave_{timestamp}.bat")
        
        print(f"\n💡 Los scripts incluyen:")
        print(f"   - Clonación del repositorio D8")
        print(f"   - Instalación de dependencias")
        print(f"   - Configuración de API keys")
        print(f"   - Registro automático con el master")
        print(f"   - Script de inicio automático\n")
        
    except ImportError as e:
        print(f"❌ Error importando generador: {e}")
        print("\n💡 Verifica que el archivo exista en: scripts/setup/generate_slave_installer.py")
    except Exception as e:
        print(f"❌ Error generando instalador: {e}")
        import traceback
        traceback.print_exc()

def check_slaves():
    """Ver estado de slaves registrados"""
    print("\n📋 Slaves Registrados")
    print("=" * 60)
    
    script_path = Path(__file__).parent / "scripts" / "check_slaves.py"
    if script_path.exists():
        subprocess.run([sys.executable, str(script_path)])
    else:
        print("\n⚠️  Script check_slaves.py no encontrado.")
        print("Verificando configuración manual...\n")
        
        # Mostrar slaves desde config
        config_file = Path.home() / "Documents" / "d8_data" / "slaves" / "config.json"
        if config_file.exists():
            try:
                import json
                slaves = json.loads(config_file.read_text())
                
                if not slaves:
                    print("📭 No hay slaves registrados aún.\n")
                    print("💡 Usa la opción 2 (Agregar Slave Remoto) para registrar uno.\n")
                    return
                
                print(f"Total de slaves: {len(slaves)}\n")
                for slave_id, info in slaves.items():
                    status = info.get('status', 'unknown')
                    status_icon = {
                        "alive": "✅",
                        "dead": "❌",
                        "version_mismatch": "⚠️",
                        "unknown": "❓"
                    }.get(status, "❓")
                    
                    print(f"{status_icon} ID: {slave_id}")
                    print(f"   Host: {info.get('host')}")
                    print(f"   Port: {info.get('port')}")
                    print(f"   Estado: {status}")
                    print(f"   Método: {info.get('install_method', 'unknown')}")
                    print()
            except Exception as e:
                print(f"❌ Error leyendo configuración: {e}")
        else:
            print("📭 No hay slaves registrados aún.\n")
            print("💡 Usa la opción 2 (Agregar Slave Remoto) para registrar uno.\n")

def remove_slave():
    """Eliminar un slave registrado"""
    print("\n🗑️  Eliminar Slave Registrado")
    print("=" * 60)
    
    # Cargar slaves existentes
    config_file = Path.home() / "Documents" / "d8_data" / "slaves" / "config.json"
    
    if not config_file.exists():
        print("\n📭 No hay slaves registrados.\n")
        return
    
    try:
        import json
        slaves = json.loads(config_file.read_text())
        
        if not slaves:
            print("\n📭 No hay slaves registrados.\n")
            return
        
        # Mostrar slaves disponibles
        print("\n📋 SLAVES DISPONIBLES PARA ELIMINAR:\n")
        slave_list = list(slaves.keys())
        
        for idx, slave_id in enumerate(slave_list, 1):
            info = slaves[slave_id]
            status = info.get('status', 'unknown')
            status_icon = {
                "alive": "✅",
                "dead": "❌",
                "version_mismatch": "⚠️",
                "unknown": "❓"
            }.get(status, "❓")
            
            print(f"{idx}. {status_icon} {slave_id} ({info.get('host')}:{info.get('port')})")
        
        print(f"\n0. ❌ Cancelar\n")
        print("=" * 60)
        
        # Solicitar selección
        choice = input("\nSelecciona el número del slave a eliminar: ").strip()
        
        if choice == "0":
            print("\n❌ Operación cancelada.\n")
            return
        
        try:
            choice_idx = int(choice) - 1
            if choice_idx < 0 or choice_idx >= len(slave_list):
                print("\n❌ Opción inválida.\n")
                return
            
            slave_id = slave_list[choice_idx]
            info = slaves[slave_id]
            
            # Confirmar eliminación
            print(f"\n⚠️  CONFIRMAR ELIMINACIÓN:")
            print(f"   ID: {slave_id}")
            print(f"   Host: {info.get('host')}:{info.get('port')}")
            print()
            
            confirm = input("¿Estás seguro? (s/N): ").strip().lower()
            
            if confirm != 's':
                print("\n❌ Operación cancelada.\n")
                return
            
            # Eliminar del diccionario
            del slaves[slave_id]
            
            # Guardar cambios
            config_file.write_text(json.dumps(slaves, indent=2))
            
            print(f"\n✅ Slave '{slave_id}' eliminado exitosamente!")
            print(f"💾 Configuración actualizada en: {config_file}\n")
            
        except (ValueError, IndexError):
            print("\n❌ Opción inválida.\n")
            
    except Exception as e:
        print(f"\n❌ Error al eliminar slave: {e}\n")

def run_supervisor():
    """
    Ejecuta supervisor de procesos D8
    
    Supervisa y reinicia automáticamente:
    - Congreso Autónomo
    - Niche Discovery
    - Orchestrator
    """
    print("\n🔄 Iniciando Supervisor D8...")
    print("=" * 60)
    print("Componentes supervisados (auto-restart):")
    print("  - 🏛️  Congreso Autónomo")
    print("  - 💎 Niche Discovery")
    print("  - 🎯 Orchestrator")
    print("=" * 60)
    print("\n⚠️  IMPORTANTE:")
    print("  - Los procesos se reinician automáticamente si fallan")
    print("  - Límite: 5 reintentos por componente")
    print("  - Logs: ~/Documents/d8_data/logs/supervisor.log")
    print("\n🛑 Presiona Ctrl+C para detener TODO el sistema\n")
    
    script_path = Path(__file__).parent / "scripts" / "supervisor_d8.py"
    subprocess.run([sys.executable, str(script_path)])

def execute_choice(choice: str):
    """Ejecuta opción seleccionada"""
    if choice == "1":
        run_congress()
    elif choice == "2":
        run_niche_discovery()
    elif choice == "3":
        run_evolution()
    elif choice == "4":
        run_orchestrator()
    elif choice == "5":
        run_slave_management()  # Abre submenú de gestión
    elif choice == "6":
        run_supervisor()
    elif choice == "7":
        print("\n👋 ¡Hasta luego!\n")
        sys.exit(0)
    elif choice == "slave_server":
        # Caso especial: ejecutar slave server directamente desde CLI
        run_slave_server()
    else:
        print("\n❌ Opción inválida.\n")

def main():
    """Función principal con soporte CLI"""
    # Check for command line arguments
    choice = parse_arguments()
    
    if choice:
        # Modo directo (non-interactive)
        execute_choice(choice)
        return
    
    # Modo interactivo (menú)
    while True:
        choice = show_menu()
        execute_choice(choice)
        
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
