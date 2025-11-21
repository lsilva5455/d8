#!/usr/bin/env python3
"""
Quick Add Slave - Registro rápido de slave por IP
Uso: python scripts/quick_add_slave.py <IP>
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.distributed.slave_manager import SlaveManager
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def quick_add_slave(slave_ip: str, port: int = 7600):
    """
    Registra un slave rápidamente solo con su IP
    
    Args:
        slave_ip: IP del slave
        port: Puerto del slave (default: 7600)
    """
    
    print("\n" + "=" * 60)
    print("🚀 REGISTRO RÁPIDO DE SLAVE")
    print("=" * 60)
    
    # Auto-generar slave ID basado en IP
    slave_id = f"slave-{slave_ip.replace('.', '-')}"
    
    print(f"\n📋 Configuración:")
    print(f"   IP: {slave_ip}")
    print(f"   Puerto: {port}")
    print(f"   ID auto-generado: {slave_id}")
    print()
    
    # Inicializar manager
    manager = SlaveManager()
    
    # Verificar si ya existe
    if slave_id in manager.slaves:
        print(f"⚠️  Slave {slave_id} ya está registrado")
        print(f"   Host actual: {manager.slaves[slave_id]['host']}:{manager.slaves[slave_id]['port']}")
        
        overwrite = input("\n¿Sobrescribir? (s/n): ").strip().lower()
        if overwrite != 's':
            print("❌ Registro cancelado")
            return False
    
    # Registrar slave
    print(f"\n🔄 Registrando slave...")
    
    try:
        manager.register_slave(
            slave_id=slave_id,
            host=slave_ip,
            port=port
        )
        
        print(f"✅ Slave registrado: {slave_id}")
        
        # Verificar conectividad
        print(f"\n🔍 Verificando conectividad...")
        
        is_healthy, status_msg = manager.check_health(slave_id)
        
        if is_healthy:
            print(f"✅ Conexión exitosa")
            
            # Obtener información del slave
            slave_info = manager.slaves[slave_id]
            
            print(f"\n📊 Información del slave:")
            print(f"   Status: {slave_info.get('status', 'unknown')}")
            print(f"   Version: {slave_info.get('version', 'unknown')}")
            print(f"   Host: {slave_info['host']}:{slave_info['port']}")
            print(f"   Registrado: {slave_info.get('registered_at', 'unknown')}")
        else:
            print(f"⚠️  No se pudo conectar: {status_msg}")
            print(f"\n💡 Verifica que:")
            print(f"   1. El slave esté ejecutándose")
            print(f"   2. El puerto {port} esté abierto")
            print(f"   3. No haya firewall bloqueando")
            
            keep = input(f"\n¿Mantener el registro de todas formas? (s/n): ").strip().lower()
            if keep != 's':
                manager.remove_slave(slave_id)
                print("❌ Registro eliminado")
                return False
        
        print("\n" + "=" * 60)
        print("✅ REGISTRO COMPLETADO")
        print("=" * 60)
        
        print(f"\n💡 Comandos útiles:")
        print(f"   Ver status: python scripts/check_slaves.py")
        print(f"   Ejecutar tarea: manager.execute_on_slave('{slave_id}', task)")
        print(f"   Remover: manager.remove_slave('{slave_id}')")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al registrar slave: {e}")
        return False


def main():
    """CLI para registro rápido"""
    
    parser = argparse.ArgumentParser(
        description="Registro rápido de slave D8 por IP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python scripts/quick_add_slave.py 192.168.1.100
  python scripts/quick_add_slave.py 192.168.1.100 --port 7601
  python scripts/quick_add_slave.py 10.0.0.50 -p 7600

El slave debe estar ejecutándose antes de registrarlo.
        """
    )
    
    parser.add_argument(
        'ip',
        help='IP del slave a registrar'
    )
    
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=7600,
        help='Puerto del slave (default: 7600)'
    )
    
    args = parser.parse_args()
    
    # Validar IP básica
    parts = args.ip.split('.')
    if len(parts) != 4:
        print(f"❌ IP inválida: {args.ip}")
        print("   Formato esperado: XXX.XXX.XXX.XXX")
        sys.exit(1)
    
    # Ejecutar registro
    success = quick_add_slave(args.ip, args.port)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
