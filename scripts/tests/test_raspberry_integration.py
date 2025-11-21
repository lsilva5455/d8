#!/usr/bin/env python3
"""
Script de prueba completa de integración con Raspberry Pi
Prueba opciones 6/4 (Generar instalador) y 6/5 (Agregar slave)
"""
import sys
import subprocess
import time
import requests
from pathlib import Path
from datetime import datetime

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Configuración
RASPBERRY_IP = "192.168.4.38"
RASPBERRY_USER = "admin"  # Usuario del Raspberry Pi
RASPBERRY_PORT = 7600
INSTALLER_DIR = Path(__file__).parent / "scripts" / "setup"

def print_section(title):
    """Imprime una sección con formato"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70 + "\n")

def test_connectivity():
    """Verifica conectividad con el Raspberry Pi"""
    print_section("🔌 PRUEBA 1: Verificar Conectividad")
    
    try:
        # Ping
        result = subprocess.run(
            ["ping", "-n", "2", RASPBERRY_IP],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"✅ Raspberry Pi {RASPBERRY_IP} está online")
            return True
        else:
            print(f"❌ No se puede alcanzar {RASPBERRY_IP}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando conectividad: {e}")
        return False

def test_generate_installer():
    """Prueba la generación de instaladores (opción 6/4)"""
    print_section("📄 PRUEBA 2: Generar Instalador Manual (Opción 6/4)")
    
    try:
        from scripts.setup.generate_slave_installer import SlaveInstallerGenerator
        
        generator = SlaveInstallerGenerator()
        INSTALLER_DIR.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generar script bash para Raspberry Pi (Linux)
        bash_script = INSTALLER_DIR / f"install_slave_{timestamp}.sh"
        generator.generate_bash_script(bash_script)
        
        print(f"✅ Script Linux generado: {bash_script.name}")
        print(f"   Ubicación: {bash_script}")
        print(f"   Tamaño: {bash_script.stat().st_size} bytes")
        
        # Verificar contenido
        content = bash_script.read_text()
        if "D8 Slave Server" in content and "#!/bin/bash" in content:
            print("✅ Contenido del script verificado")
        else:
            print("⚠️  El script no tiene el formato esperado")
        
        return bash_script
        
    except Exception as e:
        print(f"❌ Error generando instalador: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_check_slave_server():
    """Verifica si el slave server ya está corriendo en el Raspberry Pi"""
    print_section("🔍 PRUEBA 3: Verificar Slave Server en Raspberry Pi")
    
    try:
        print(f"Intentando conectar a http://{RASPBERRY_IP}:{RASPBERRY_PORT}/api/health")
        
        response = requests.get(
            f"http://{RASPBERRY_IP}:{RASPBERRY_PORT}/api/health",
            timeout=3
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Slave server está corriendo!")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Hostname: {data.get('hostname')}")
            return True
        else:
            print(f"⚠️  Slave server respondió con código: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ No hay slave server corriendo en {RASPBERRY_IP}:{RASPBERRY_PORT}")
        print(f"   Esto es normal si no lo has iniciado aún.")
        return False
    except Exception as e:
        print(f"❌ Error verificando slave server: {e}")
        return False

def test_add_slave():
    """Prueba agregar el slave remoto (opción 6/5)"""
    print_section("➕ PRUEBA 4: Agregar Slave Remoto (Opción 6/5)")
    
    try:
        # Verificar si el script add_slave.py existe
        add_slave_script = Path(__file__).parent / "scripts" / "add_slave.py"
        
        if not add_slave_script.exists():
            print(f"❌ Script no encontrado: {add_slave_script}")
            return False
        
        print(f"📝 Simulando agregar slave {RASPBERRY_IP}:{RASPBERRY_PORT}")
        print(f"   En el sistema real, ejecutarías:")
        print(f"   python scripts/add_slave.py")
        print(f"   Y proporcionarías:")
        print(f"     - Host: {RASPBERRY_IP}")
        print(f"     - Port: {RASPBERRY_PORT}")
        
        # Verificar configuración actual
        config_file = Path.home() / "Documents" / "d8_data" / "slaves" / "config.json"
        
        if config_file.exists():
            import json
            slaves = json.loads(config_file.read_text())
            
            # Buscar si ya existe este slave
            raspberry_slave = None
            for slave_id, info in slaves.items():
                if info.get('host') == RASPBERRY_IP:
                    raspberry_slave = slave_id
                    break
            
            if raspberry_slave:
                print(f"\n✅ Slave ya registrado: {raspberry_slave}")
                print(f"   Host: {slaves[raspberry_slave].get('host')}")
                print(f"   Port: {slaves[raspberry_slave].get('port')}")
                print(f"   Status: {slaves[raspberry_slave].get('status', 'unknown')}")
            else:
                print(f"\n⚠️  Slave {RASPBERRY_IP} no está registrado aún")
                print(f"   Para registrarlo, ejecuta start_d8.py y selecciona:")
                print(f"   Opción 6 → Opción 2 (Agregar Slave Remoto)")
        else:
            print(f"\n📭 No hay slaves registrados en el sistema")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando slave: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_check_slaves():
    """Verifica todos los slaves registrados"""
    print_section("📋 PRUEBA 5: Verificar Todos los Slaves")
    
    try:
        check_slaves_script = Path(__file__).parent / "scripts" / "check_slaves.py"
        
        if check_slaves_script.exists():
            print("Ejecutando check_slaves.py...\n")
            result = subprocess.run(
                [sys.executable, str(check_slaves_script)],
                capture_output=True,
                text=True
            )
            print(result.stdout)
            return result.returncode == 0
        else:
            print(f"⚠️  Script no encontrado: {check_slaves_script}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def generate_instructions(installer_path):
    """Genera instrucciones para instalar en el Raspberry Pi"""
    print_section("📝 INSTRUCCIONES DE INSTALACIÓN")
    
    print("Para instalar D8 en el Raspberry Pi, sigue estos pasos:\n")
    
    print("OPCIÓN A: Manual (sin SSH desde este script)")
    print("-" * 70)
    print(f"1. Copia el instalador al Raspberry Pi:")
    print(f"   scp {installer_path.name} admin@{RASPBERRY_IP}:~/")
    print(f"\n2. Conéctate al Raspberry Pi:")
    print(f"   ssh admin@{RASPBERRY_IP}")
    print(f"\n3. Dale permisos de ejecución:")
    print(f"   chmod +x {installer_path.name}")
    print(f"\n4. Ejecuta el instalador:")
    print(f"   ./{installer_path.name}")
    print(f"\n5. Una vez instalado, inicia el slave server:")
    print(f"   cd ~/d8")
    print(f"   python start_d8.py slave")
    
    print("\n\nOPCIÓN B: Automático (desde start_d8.py)")
    print("-" * 70)
    print("1. Ejecuta: python start_d8.py")
    print("2. Selecciona: Opción 6 (Gestión de Slaves)")
    print("3. Selecciona: Opción 3 (Instalar D8 en Slave Remoto)")
    print("4. Proporciona:")
    print(f"   - Host: {RASPBERRY_IP}")
    print(f"   - Usuario SSH: admin")
    print("   - Contraseña SSH")
    
    print("\n\nOPCIÓN C: Agregar slave existente")
    print("-" * 70)
    print("Si D8 ya está instalado y el slave server está corriendo:")
    print("1. Ejecuta: python start_d8.py")
    print("2. Selecciona: Opción 6 (Gestión de Slaves)")
    print("3. Selecciona: Opción 2 (Agregar Slave Remoto)")
    print(f"4. Proporciona:")
    print(f"   - Host: {RASPBERRY_IP}")
    print(f"   - Port: {RASPBERRY_PORT}")

def main():
    print("\n" + "=" * 70)
    print(" PRUEBA COMPLETA DE INTEGRACIÓN CON RASPBERRY PI")
    print(" Opciones 6/4 (Generar instalador) y 6/5 (Agregar slave)")
    print("=" * 70)
    print(f"\n📍 Raspberry Pi: {RASPBERRY_IP}")
    print(f"📍 Puerto esperado: {RASPBERRY_PORT}")
    
    results = {}
    
    # Prueba 1: Conectividad
    results['connectivity'] = test_connectivity()
    
    # Prueba 2: Generar instalador
    installer_path = test_generate_installer()
    results['generate_installer'] = installer_path is not None
    
    # Prueba 3: Verificar si slave server está corriendo
    results['slave_running'] = test_check_slave_server()
    
    # Prueba 4: Verificar registro de slave
    results['check_slave'] = test_add_slave()
    
    # Prueba 5: Ver todos los slaves
    results['check_all_slaves'] = test_check_slaves()
    
    # Resumen
    print_section("📊 RESUMEN DE PRUEBAS")
    
    print(f"{'✅' if results['connectivity'] else '❌'} Conectividad con Raspberry Pi")
    print(f"{'✅' if results['generate_installer'] else '❌'} Generar instalador (Opción 6/4)")
    print(f"{'✅' if results['slave_running'] else '⚠️ '} Slave server corriendo")
    print(f"{'✅' if results['check_slave'] else '❌'} Verificar slave")
    print(f"{'✅' if results['check_all_slaves'] else '❌'} Listar todos los slaves")
    
    # Instrucciones
    if installer_path and results['connectivity']:
        generate_instructions(installer_path)
    
    # Conclusión
    print_section("🎯 CONCLUSIÓN")
    
    if results['connectivity'] and results['generate_installer']:
        if results['slave_running']:
            print("🎉 ¡El Raspberry Pi ya tiene el slave server corriendo!")
            print("   Próximo paso: Agregarlo al sistema con opción 6/2")
        else:
            print("✅ El instalador está listo para ser usado")
            print("   Próximo paso: Seguir las instrucciones anteriores")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los detalles arriba.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
