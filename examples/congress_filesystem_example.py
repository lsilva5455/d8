"""
Example: Congress uses FileSystemManager to implement improvements
Demonstrates autonomous code modification by Congress
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.integrations.filesystem_manager import get_filesystem_manager
from datetime import datetime

def example_congress_workflow():
    """
    Simula cómo el Congreso usaría FileSystemManager para implementar mejoras
    """
    
    print("🏛️  AUTONOMOUS CONGRESS - FILE OPERATION EXAMPLE")
    print("=" * 70)
    
    fs = get_filesystem_manager()
    
    # FASE 1: RESEARCH - Analizar código actual
    print("\n📚 FASE 1: RESEARCH")
    print("-" * 70)
    
    print("Congress: 'Necesito analizar la configuración actual'")
    config_result = fs.read_file("app/config.py")
    
    if "error" not in config_result:
        print(f"✅ Leído app/config.py ({config_result['size']} bytes)")
        print(f"📄 Primeras líneas:")
        lines = config_result['content'].split('\n')[:5]
        for line in lines:
            print(f"   {line}")
    
    # FASE 2: EXPERIMENT - Proponer mejora
    print("\n🧪 FASE 2: EXPERIMENT DESIGN")
    print("-" * 70)
    
    print("Congress: 'Propongo actualizar el modelo Groq para mejor performance'")
    experiment = {
        "title": "Upgrade Groq model to llama-3.3-70b-versatile",
        "hypothesis": "Newer model will be faster and more reliable",
        "changes": [
            {
                "file": "app/config.py",
                "description": "Update groq_model parameter"
            }
        ],
        "expected_improvement": "15% faster, -20% cost"
    }
    print(f"✅ Experimento diseñado: {experiment['title']}")
    
    # FASE 3: VALIDATE - Buscar archivos relacionados
    print("\n✓ FASE 3: VALIDATION - Buscar impacto")
    print("-" * 70)
    
    print("Congress: 'Buscando archivos que usan groq_model'")
    related_files = fs.search_files("*groq*", path="app")
    print(f"✅ Encontrados {len(related_files)} archivos relacionados:")
    for f in related_files[:5]:
        print(f"   📄 {f}")
    
    # FASE 4: IMPLEMENT - Crear archivo de prueba (no modificar config real)
    print("\n🚀 FASE 4: IMPLEMENTATION (Test)")
    print("-" * 70)
    
    print("Congress: 'Creando archivo de prueba con nuevo config'")
    
    test_config = """# D8 Configuration - Updated by Autonomous Congress
# Date: """ + datetime.now().isoformat() + """

from pydantic import BaseSettings

class Config(BaseSettings):
    # Groq Configuration
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"  # ← UPDATED
    
    # Evolution parameters
    population_size: int = 20
    mutation_rate: float = 0.1
"""
    
    write_result = fs.write_file(
        "~/Documents/d8_data/test_config.py",
        test_config,
        create_backup=False
    )
    
    if "error" not in write_result:
        print(f"✅ Archivo creado: {write_result['path']}")
        print(f"✅ Bytes escritos: {write_result['bytes_written']}")
    
    # FASE 5: GIT OPERATIONS - Ver estado
    print("\n🔀 FASE 5: GIT STATUS")
    print("-" * 70)
    
    git_status = fs.git_status()
    if "error" not in git_status:
        print(f"✅ Branch: {git_status['branch']}")
        print(f"✅ Modified files: {len(git_status['modified'])}")
        print(f"✅ Untracked files: {len(git_status['untracked'])}")
        
        if git_status['modified']:
            print("\n📝 Modified files:")
            for file in git_status['modified'][:5]:
                print(f"   • {file}")
    
    # FASE 6: SIMULAR COMMIT (no ejecutar realmente)
    print("\n💾 FASE 6: COMMIT (Simulation)")
    print("-" * 70)
    
    print("Congress: 'Si esto fuera real, haría:'")
    print("   1. fs.git_commit(")
    print("      files=['app/config.py'],")
    print("      message='feat: Upgrade to llama-3.3-70b-versatile'")
    print("   )")
    print("   2. fs.push_to_github()")
    print("   3. fs.create_pull_request(")
    print("      title='[Congress] feat: Upgrade Groq model',")
    print("      body='Improves performance by 15%, reduces cost by 20%'")
    print("   )")
    
    print("\n✅ Workflow completado exitosamente")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = example_congress_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
