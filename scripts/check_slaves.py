"""
Script para verificar estado de todos los slaves
Muestra información detallada de conectividad, versión, y capacidades
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.distributed.slave_manager import SlaveManager
import logging
from datetime import datetime

logging.basicConfig(level=logging.WARNING)


def main():
    """Verifica estado de todos los slaves"""
    
    print("=" * 70)
    print("🌐 ESTADO DE SLAVES EN LA RED D8")
    print("=" * 70)
    print()
    
    manager = SlaveManager()
    
    if not manager.slaves:
        print("📋 No hay slaves registrados")
        print()
        print("💡 Para agregar un slave:")
        print("   python scripts/add_slave.py")
        print()
        return
    
    print(f"📊 MASTER VERSION: {manager.master_version[:8]}")
    print()
    print(f"📋 SLAVES REGISTRADOS: {len(manager.slaves)}")
    print()
    
    # Verificar cada slave
    alive_count = 0
    dead_count = 0
    version_mismatch_count = 0
    
    for slave_id, slave_info in manager.slaves.items():
        print("-" * 70)
        print(f"🖥️  SLAVE: {slave_id}")
        print("-" * 70)
        
        print(f"   Host: {slave_info['host']}:{slave_info['port']}")
        print(f"   Método: {slave_info.get('install_method', 'unknown')}")
        print(f"   Registrado: {slave_info.get('registered_at', 'unknown')}")
        print(f"   Última vez visto: {slave_info.get('last_seen', 'never')}")
        print()
        
        # Health check
        print(f"   🔍 Verificando salud...")
        is_healthy = manager.check_health(slave_id)
        
        # Obtener info actualizada
        slave_info = manager.slaves[slave_id]
        status = slave_info.get('status', 'unknown')
        
        status_icons = {
            "alive": "✅",
            "dead": "❌",
            "version_mismatch": "⚠️",
            "unknown": "❓"
        }
        
        icon = status_icons.get(status, "❓")
        print(f"   {icon} Estado: {status.upper()}")
        
        if status == "alive":
            alive_count += 1
            print(f"   ✅ Commit: {slave_info.get('commit', 'unknown')[:8]}")
            
            capabilities = slave_info.get('capabilities', {})
            if capabilities:
                print(f"   📦 Capacidades:")
                for cap, available in capabilities.items():
                    cap_icon = "✅" if available else "❌"
                    print(f"      {cap_icon} {cap}")
        
        elif status == "version_mismatch":
            version_mismatch_count += 1
            print(f"   ⚠️  Versión incorrecta!")
            print(f"      Master: {manager.master_version[:8]}")
            print(f"      Slave:  {slave_info.get('commit', 'unknown')[:8]}")
            print(f"   💡 Sincroniza el slave con: git pull")
        
        elif status == "dead":
            dead_count += 1
            print(f"   ❌ No responde")
            print(f"   💡 Verifica que el slave server esté corriendo:")
            print(f"      python app/distributed/slave_server.py")
        
        print()
    
    # Resumen
    print("=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    print()
    print(f"   Total slaves: {len(manager.slaves)}")
    print(f"   ✅ Vivos: {alive_count}")
    print(f"   ❌ Muertos: {dead_count}")
    print(f"   ⚠️  Version mismatch: {version_mismatch_count}")
    print()
    
    if alive_count == len(manager.slaves):
        print("🎉 ¡Todos los slaves están operacionales!")
    elif dead_count > 0:
        print("⚠️  Algunos slaves no responden. Verifica que estén corriendo.")
    
    if version_mismatch_count > 0:
        print("⚠️  Algunos slaves tienen versión incorrecta. Sincroniza con git pull.")
    
    print()
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Operación cancelada")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
