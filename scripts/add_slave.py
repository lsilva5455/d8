"""
Script para agregar un slave a la red D8
Uso rápido para registrar slaves disponibles
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.distributed.slave_manager import SlaveManager
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """
    Script interactivo para agregar slaves
    """
    
    print("=" * 60)
    print("🌐 AGREGAR SLAVE A LA RED D8")
    print("=" * 60)
    print()
    
    # Inicializar manager
    manager = SlaveManager()
    
    # Mostrar slaves existentes
    print("📋 SLAVES REGISTRADOS:")
    if not manager.slaves:
        print("   (ninguno)")
    else:
        for slave_id, info in manager.slaves.items():
            status_icon = {
                "alive": "✅",
                "dead": "❌",
                "version_mismatch": "⚠️",
                "unknown": "❓"
            }.get(info.get("status", "unknown"), "❓")
            
            print(f"   {status_icon} {slave_id}: {info['host']}:{info['port']} - {info['status']}")
    
    print()
    print("=" * 60)
    print()
    
    # Modo interactivo o argumentos
    if len(sys.argv) >= 3:
        # Modo argumentos: python add_slave.py <id> <host> [port]
        slave_id = sys.argv[1]
        host = sys.argv[2]
        port = int(sys.argv[3]) if len(sys.argv) >= 4 else 7600
        
        print(f"📝 Registrando slave desde argumentos...")
        
    else:
        # Modo interactivo
        print("📝 DATOS DEL NUEVO SLAVE:")
        print()
        
        slave_id = input("ID del slave (ej: pc-leo, vps-us, raspi-backup): ").strip()
        if not slave_id:
            print("❌ ID no puede estar vacío")
            return
        
        if slave_id in manager.slaves:
            print(f"⚠️  Slave '{slave_id}' ya existe")
            overwrite = input("¿Sobrescribir? (s/N): ").strip().lower()
            if overwrite != 's':
                print("❌ Operación cancelada")
                return
            manager.unregister_slave(slave_id)
        
        host = input("Host/IP del slave (ej: 192.168.1.100, slave.midominio.com): ").strip()
        if not host:
            print("❌ Host no puede estar vacío")
            return
        
        port_input = input("Puerto [7600]: ").strip()
        port = int(port_input) if port_input else 7600
    
    print()
    print("-" * 60)
    print(f"🔍 VERIFICANDO CONECTIVIDAD...")
    print(f"   Slave ID: {slave_id}")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print("-" * 60)
    print()
    
    # Intentar conexión antes de registrar
    import requests
    try:
        response = requests.get(
            f"http://{host}:{port}/api/health",
            timeout=5
        )
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Slave respondió correctamente!")
            print()
            print("📊 INFORMACIÓN DEL SLAVE:")
            print(f"   Estado: {health_data.get('status')}")
            print(f"   Python: {health_data.get('python_version', 'unknown')[:50]}...")
            print(f"   Commit: {health_data.get('commit', 'unknown')[:8]}")
            print(f"   Branch: {health_data.get('branch', 'unknown')}")
            print()
            
            methods = health_data.get('execution_methods', {})
            print("   Métodos disponibles:")
            for method, available in methods.items():
                icon = "✅" if available else "❌"
                print(f"      {icon} {method}")
            
            print()
            
            # Detectar método principal
            if methods.get('docker'):
                install_method = 'docker'
            elif methods.get('venv'):
                install_method = 'venv'
            else:
                install_method = 'python'
            
        else:
            print(f"⚠️  Slave respondió pero con código {response.status_code}")
            install_method = 'unknown'
            
    except requests.exceptions.Timeout:
        print(f"❌ Timeout conectando a {host}:{port}")
        print("💡 Verifica que:")
        print("   1. El slave server esté corriendo")
        print("   2. El firewall permita conexiones en el puerto")
        print("   3. La IP/host sea correcta")
        return
        
    except requests.exceptions.ConnectionError:
        print(f"❌ No se pudo conectar a {host}:{port}")
        print("💡 Verifica que:")
        print("   1. El slave server esté corriendo: python app/distributed/slave_server.py")
        print("   2. La IP/host sea correcta")
        print("   3. Estén en la misma red (o haya port forwarding)")
        return
        
    except Exception as e:
        print(f"❌ Error verificando conectividad: {e}")
        install_method = 'unknown'
    
    # Registrar
    print("-" * 60)
    print("💾 REGISTRANDO SLAVE...")
    print("-" * 60)
    print()
    
    success = manager.register_slave(
        slave_id=slave_id,
        host=host,
        port=port,
        install_method=install_method
    )
    
    if success:
        print("✅ SLAVE REGISTRADO EXITOSAMENTE!")
        print()
        print(f"📝 Configuración guardada en:")
        print(f"   {manager.config_path}")
        print()
        print("🚀 PRÓXIMOS PASOS:")
        print("   1. El slave ya está disponible para recibir tareas")
        print("   2. El SlaveManager lo monitoreará cada 30s")
        print("   3. Si la versión no coincide, recibirás alerta")
        print()
        print("🔧 COMANDOS ÚTILES:")
        print(f"   Ver estado: python scripts/check_slaves.py")
        print(f"   Test rápido: python scripts/tests/test_fase4_complete.py")
        
    else:
        print("❌ Error al registrar slave")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Operación cancelada por usuario")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
