#!/usr/bin/env python3
"""
Script de prueba para opciones de gestión de slaves
"""
import sys
from pathlib import Path
from datetime import datetime

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

def test_generate_installer():
    """Prueba la generación de instaladores"""
    print("\n🧪 PRUEBA: Generar Instalador Manual")
    print("=" * 60)
    
    try:
        from scripts.setup.generate_slave_installer import SlaveInstallerGenerator
        
        generator = SlaveInstallerGenerator()
        output_dir = Path(__file__).parent / "scripts" / "setup"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generar script bash
        bash_script = output_dir / f"install_slave_{timestamp}.sh"
        generator.generate_bash_script(bash_script)
        print(f"\n✅ Script Linux generado: {bash_script}")
        print(f"   Tamaño: {bash_script.stat().st_size} bytes")
        
        # Generar script batch
        bat_script = output_dir / f"install_slave_{timestamp}.bat"
        generator.generate_batch_script(bat_script)
        print(f"\n✅ Script Windows generado: {bat_script}")
        print(f"   Tamaño: {bat_script.stat().st_size} bytes")
        
        print("\n📋 Instrucciones de uso:")
        print("\nLinux:")
        print(f"  1. scp {bash_script.name} usuario@raspberry:~/")
        print(f"  2. ssh usuario@raspberry")
        print(f"  3. chmod +x {bash_script.name}")
        print(f"  4. ./{bash_script.name}")
        
        print("\nWindows:")
        print(f"  1. Copiar {bat_script.name} a la máquina remota")
        print(f"  2. Ejecutar como administrador")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_check_slaves():
    """Prueba la verificación de slaves"""
    print("\n\n🧪 PRUEBA: Verificar Slaves")
    print("=" * 60)
    
    try:
        import subprocess
        
        script_path = Path(__file__).parent / "scripts" / "check_slaves.py"
        if script_path.exists():
            print("\n📡 Ejecutando check_slaves.py...\n")
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print("Errores:", result.stderr)
            return result.returncode == 0
        else:
            print(f"\n⚠️  Script no encontrado: {script_path}")
            
            # Verificar configuración manual
            config_file = Path.home() / "Documents" / "d8_data" / "slaves" / "config.json"
            if config_file.exists():
                import json
                slaves = json.loads(config_file.read_text())
                print(f"\n📋 Slaves en config.json: {len(slaves)}")
                for slave_id, info in slaves.items():
                    print(f"   - {slave_id}: {info.get('host')}:{info.get('port')}")
                return True
            else:
                print("\n📭 No hay slaves registrados.")
                return True
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 60)
    print(" PRUEBAS DE OPCIONES DE GESTIÓN DE SLAVES")
    print("=" * 60)
    
    # Test 1: Generar instaladores
    success1 = test_generate_installer()
    
    # Test 2: Verificar slaves
    success2 = test_check_slaves()
    
    # Resumen
    print("\n\n" + "=" * 60)
    print(" RESUMEN DE PRUEBAS")
    print("=" * 60)
    print(f"\n{'✅' if success1 else '❌'} Generar Instalador Manual")
    print(f"{'✅' if success2 else '❌'} Verificar Slaves")
    
    if success1 and success2:
        print("\n🎉 Todas las pruebas pasaron exitosamente!")
        print("\n📝 Próximo paso:")
        print("   Para probar con el Raspberry Pi, proporciona su IP")
        print("   y ejecutaremos:")
        print("   1. Copiar instalador al Raspberry")
        print("   2. Ejecutarlo remotamente")
        print("   3. Agregar el slave al sistema")
        print("   4. Verificar conectividad\n")
        return 0
    else:
        print("\n⚠️  Algunas pruebas fallaron.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
