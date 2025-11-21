#!/usr/bin/env python3
"""
Script para identificar el instalador de slave más actualizado
"""
from pathlib import Path
from datetime import datetime

def check_installers():
    """Verifica todos los instaladores y recomienda el más actualizado"""
    
    setup_dir = Path(__file__).parent / "scripts" / "setup"
    
    # Buscar instaladores .sh
    bash_installers = sorted(
        setup_dir.glob("install_slave_*.sh"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    # Buscar instaladores .bat
    bat_installers = sorted(
        setup_dir.glob("install_slave_*.bat"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    print("\n" + "=" * 70)
    print(" INSTALADORES DE D8 SLAVE SERVER")
    print("=" * 70 + "\n")
    
    if bash_installers:
        print("🐧 INSTALADORES LINUX (.sh)\n")
        for i, installer in enumerate(bash_installers[:5], 1):
            size = installer.stat().st_size
            mtime = datetime.fromtimestamp(installer.stat().st_mtime)
            
            marker = "✅ MÁS RECIENTE" if i == 1 else ""
            print(f"{i}. {installer.name} {marker}")
            print(f"   Fecha: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Tamaño: {size:,} bytes")
            
            # Verificar contenido básico
            try:
                content = installer.read_text(encoding='utf-8', errors='ignore')
                if "D8 Slave Server" in content:
                    print(f"   ✓ Formato válido")
                else:
                    print(f"   ⚠️  Formato no reconocido")
            except:
                print(f"   ⚠️  Error leyendo archivo")
            print()
        
        if len(bash_installers) > 5:
            print(f"... y {len(bash_installers) - 5} instaladores más antiguos\n")
    
    if bat_installers:
        print("\n🪟 INSTALADORES WINDOWS (.bat)\n")
        for i, installer in enumerate(bat_installers[:5], 1):
            size = installer.stat().st_size
            mtime = datetime.fromtimestamp(installer.stat().st_mtime)
            
            marker = "✅ MÁS RECIENTE" if i == 1 else ""
            print(f"{i}. {installer.name} {marker}")
            print(f"   Fecha: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Tamaño: {size:,} bytes\n")
        
        if len(bat_installers) > 5:
            print(f"... y {len(bat_installers) - 5} instaladores más antiguos\n")
    
    # Recomendación
    print("=" * 70)
    print(" 💡 RECOMENDACIÓN")
    print("=" * 70 + "\n")
    
    if bash_installers:
        latest_bash = bash_installers[0]
        print(f"Para Linux/Raspberry Pi, usa:")
        print(f"  {latest_bash.name}")
        print(f"\nCómo usarlo:")
        print(f"  1. scp {latest_bash.name} admin@192.168.4.38:~/")
        print(f"  2. ssh admin@192.168.4.38")
        print(f"  3. chmod +x ~/{latest_bash.name}")
        print(f"  4. ~/{latest_bash.name}")
    
    if bat_installers:
        latest_bat = bat_installers[0]
        print(f"\nPara Windows, usa:")
        print(f"  {latest_bat.name}")
    
    print("\n" + "=" * 70)
    print(" 📝 NOTA")
    print("=" * 70 + "\n")
    print("Todos los instaladores con el mismo tamaño (5589 bytes) contienen")
    print("la misma versión del código. La diferencia es solo el timestamp.")
    print("\nSi necesitas generar uno nuevo con configuración actualizada:")
    print("  python start_d8.py → Opción 6 → Opción 4\n")

if __name__ == "__main__":
    check_installers()
