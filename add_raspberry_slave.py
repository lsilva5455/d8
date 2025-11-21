#!/usr/bin/env python3
"""
Script para agregar automáticamente el Raspberry Pi como slave
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# Configuración
RASPBERRY_IP = "192.168.4.38"
RASPBERRY_PORT = 7600
SLAVE_ID = "raspberry-pi-slave"

def add_raspberry_slave():
    """Agrega el Raspberry Pi al sistema de slaves"""
    print("\n🤖 Agregando Raspberry Pi al sistema de slaves...")
    print("=" * 60)
    
    # Ruta del archivo de configuración
    config_dir = Path.home() / "Documents" / "d8_data" / "slaves"
    config_file = config_dir / "config.json"
    
    # Crear directorio si no existe
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Cargar configuración actual
    if config_file.exists():
        slaves = json.loads(config_file.read_text())
        print(f"\n📋 Slaves actuales: {len(slaves)}")
    else:
        slaves = {}
        print("\n📭 No hay slaves registrados aún")
    
    # Verificar si ya existe
    if SLAVE_ID in slaves:
        print(f"\n⚠️  El slave '{SLAVE_ID}' ya existe:")
        print(f"   Host: {slaves[SLAVE_ID].get('host')}")
        print(f"   Port: {slaves[SLAVE_ID].get('port')}")
        print(f"\n¿Deseas actualizarlo? (s/n): ", end="")
        
        # En modo automático, asumimos 's'
        print("s (automático)")
        update = True
    else:
        update = False
    
    # Crear/actualizar configuración del slave
    slaves[SLAVE_ID] = {
        "host": RASPBERRY_IP,
        "port": RASPBERRY_PORT,
        "status": "alive",
        "install_method": "manual",
        "registered_at": datetime.now().isoformat(),
        "last_seen": datetime.now().isoformat()
    }
    
    # Guardar configuración
    config_file.write_text(json.dumps(slaves, indent=2))
    
    if update:
        print(f"\n✅ Slave '{SLAVE_ID}' actualizado exitosamente")
    else:
        print(f"\n✅ Slave '{SLAVE_ID}' agregado exitosamente")
    
    print(f"\n📝 Configuración:")
    print(f"   ID: {SLAVE_ID}")
    print(f"   Host: {RASPBERRY_IP}")
    print(f"   Port: {RASPBERRY_PORT}")
    print(f"   Status: alive")
    print(f"   Archivo: {config_file}")
    
    # Verificar conectividad
    print(f"\n🔍 Verificando conectividad...")
    
    try:
        import requests
        response = requests.get(
            f"http://{RASPBERRY_IP}:{RASPBERRY_PORT}/api/health",
            timeout=3
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conexión exitosa!")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Hostname: {data.get('hostname', 'N/A')}")
        else:
            print(f"⚠️  Respuesta inesperada: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print(f"   El slave será registrado, pero verifica que esté corriendo.")
    
    return True

def verify_all_slaves():
    """Verifica todos los slaves registrados"""
    print("\n\n" + "=" * 60)
    print("📋 VERIFICANDO TODOS LOS SLAVES")
    print("=" * 60 + "\n")
    
    import subprocess
    check_slaves_script = Path(__file__).parent / "scripts" / "check_slaves.py"
    
    if check_slaves_script.exists():
        subprocess.run([sys.executable, str(check_slaves_script)])
    else:
        # Verificación manual
        config_file = Path.home() / "Documents" / "d8_data" / "slaves" / "config.json"
        if config_file.exists():
            import json
            slaves = json.loads(config_file.read_text())
            
            print(f"Total de slaves: {len(slaves)}\n")
            for slave_id, info in slaves.items():
                print(f"🖥️  {slave_id}")
                print(f"   Host: {info.get('host')}:{info.get('port')}")
                print(f"   Status: {info.get('status', 'unknown')}")
                print()

def main():
    print("\n" + "=" * 60)
    print(" AGREGAR RASPBERRY PI AL SISTEMA D8")
    print("=" * 60)
    
    success = add_raspberry_slave()
    
    if success:
        verify_all_slaves()
        
        print("\n" + "=" * 60)
        print(" ✅ COMPLETADO")
        print("=" * 60)
        print("\n🎯 El Raspberry Pi ha sido agregado al sistema")
        print("📝 Ahora puedes:")
        print("   1. Ver todos los slaves: python start_d8.py → Opción 6 → Opción 5")
        print("   2. Enviar tareas al slave desde el orchestrator")
        print("   3. Monitorear su salud con check_slaves.py\n")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
