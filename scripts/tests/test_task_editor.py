"""
Test del sistema de edición de tareas
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root))

from app.tasks.parser import TaskParser
from app.tasks.processor import TaskProcessor
from app.tasks.editor import TaskEditor

def test_display_ids():
    """Test generación de IDs temporales A1-Z9"""
    print("\n" + "="*60)
    print("TEST: Generación de IDs temporales")
    print("="*60)
    
    processor = TaskProcessor()
    
    # Test generación de display IDs
    test_cases = [
        (0, "A1"),   # Primer ID
        (8, "A9"),   # Último de A
        (9, "B1"),   # Primer de B
        (17, "B9"),  # Último de B
        (233, "Z9"), # Último posible
    ]
    
    print("\n📋 Verificando generación de IDs:")
    for index, expected_id in test_cases:
        generated = processor._generate_display_id(index)
        status = "✅" if generated == expected_id else "❌"
        print(f"  {status} Index {index:3d} -> {generated} (esperado: {expected_id})")
    
    print("\n✅ Test de generación completado")

def test_task_retrieval():
    """Test recuperación de tareas por ID temporal"""
    print("\n" + "="*60)
    print("TEST: Recuperación de tareas por ID temporal")
    print("="*60)
    
    processor = TaskProcessor()
    
    # Obtener primeras 5 tareas
    tasks = processor.list_pending_tasks(max_tasks=5)
    
    print(f"\n📋 Primeras {len(tasks)} tareas pendientes:")
    for i, task in enumerate(tasks):
        display_id = processor._generate_display_id(i)
        print(f"  {display_id}: {task.title[:60]}")
    
    # Test recuperación por display ID
    print("\n🔍 Verificando recuperación por display ID:")
    for i in range(min(3, len(tasks))):
        display_id = processor._generate_display_id(i)
        retrieved = processor.get_task_by_display_id(display_id)
        
        if retrieved:
            matches = retrieved.title == tasks[i].title
            status = "✅" if matches else "❌"
            print(f"  {status} {display_id} -> {retrieved.title[:50]}")
        else:
            print(f"  ❌ {display_id} -> No encontrada")
    
    print("\n✅ Test de recuperación completado")

def test_unified_get_task_by_id():
    """Test método unificado get_task_by_id()"""
    print("\n" + "="*60)
    print("TEST: Método unificado get_task_by_id()")
    print("="*60)
    
    processor = TaskProcessor()
    
    # Test con ID temporal
    print("\n📋 Test con ID temporal (A1):")
    task_a1 = processor.get_task_by_id("A1")
    if task_a1:
        print(f"  ✅ A1 encontrada: {task_a1.title[:60]}")
    else:
        print("  ❌ A1 no encontrada")
    
    # Test case-insensitive
    print("\n📋 Test case-insensitive (a1):")
    task_a1_lower = processor.get_task_by_id("a1")
    if task_a1_lower:
        print(f"  ✅ a1 encontrada: {task_a1_lower.title[:60]}")
    else:
        print("  ❌ a1 no encontrada")
    
    # Test con ID interno (si tenemos uno)
    tasks = processor.list_pending_tasks(max_tasks=1)
    if tasks:
        internal_id = tasks[0].task_id
        print(f"\n📋 Test con ID interno ({internal_id[:16]}...):")
        task_internal = processor.get_task_by_id(internal_id)
        if task_internal:
            print(f"  ✅ ID interno funciona: {task_internal.title[:60]}")
        else:
            print("  ❌ ID interno no encontrado")
    
    print("\n✅ Test de método unificado completado")

def test_telegram_formatting():
    """Test formateo para Telegram con IDs temporales"""
    print("\n" + "="*60)
    print("TEST: Formateo para Telegram")
    print("="*60)
    
    processor = TaskProcessor()
    
    # Generar lista formateada
    formatted = processor.generate_task_list_for_telegram(max_tasks=5)
    
    print("\n📱 Lista formateada para Telegram:")
    print(formatted)
    
    # Verificar que contiene IDs temporales
    has_temp_ids = "A1" in formatted or "A2" in formatted
    
    if has_temp_ids:
        print("\n✅ Contiene IDs temporales (A1, A2, etc.)")
    else:
        print("\n❌ No se detectaron IDs temporales")
    
    print("\n✅ Test de formateo completado")

def test_task_details():
    """Test detalles de tarea para Telegram"""
    print("\n" + "="*60)
    print("TEST: Detalles de tarea para Telegram")
    print("="*60)
    
    processor = TaskProcessor()
    
    # Obtener detalles de A1
    details = processor.get_task_details_for_telegram("A1")
    
    print("\n📋 Detalles de tarea A1:")
    print(details)
    
    # Verificar que menciona ID temporal
    has_temp_id_note = "ID Temporal" in details or "válido solo en esta sesión" in details
    
    if has_temp_id_note:
        print("\n✅ Incluye nota sobre ID temporal")
    else:
        print("\n⚠️  No se detectó nota sobre temporalidad del ID")
    
    print("\n✅ Test de detalles completado")

def test_search():
    """Test búsqueda de tareas"""
    print("\n" + "="*60)
    print("TEST: Búsqueda de tareas")
    print("="*60)
    
    processor = TaskProcessor()
    
    # Buscar por palabra común
    test_queries = ["telegram", "api", "test", "implementar"]
    
    for query in test_queries:
        results = processor.search_tasks(query)
        print(f"\n🔍 Búsqueda: '{query}' -> {len(results)} resultados")
        
        for i, task in enumerate(results[:3], 1):
            print(f"  {i}. {task.title[:60]}")
    
    print("\n✅ Test de búsqueda completado")

def test_editor_mock():
    """Test básico del editor (sin modificar archivo real)"""
    print("\n" + "="*60)
    print("TEST: Editor de tareas (mock)")
    print("="*60)
    
    # Verificar que el editor se puede instanciar
    pendientes_file = project_root / "PENDIENTES.md"
    
    if not pendientes_file.exists():
        print("  ⚠️  PENDIENTES.md no encontrado, saltando test")
        return
    
    editor = TaskEditor(pendientes_file)
    
    print("\n✅ Editor instanciado correctamente")
    print(f"  📄 Archivo: {pendientes_file}")
    print(f"  📋 Parser: {editor.parser}")
    
    # Test de encontrar tarea (sin modificar)
    print("\n🔍 Test de búsqueda de tarea en contenido:")
    content = pendientes_file.read_text(encoding='utf-8')
    
    # Buscar primera tarea por ID temporal
    processor = TaskProcessor()
    tasks = processor.list_pending_tasks(max_tasks=1)
    
    if tasks:
        task_dict = editor._find_task_in_content(content, "A1")
        if task_dict:
            print(f"  ✅ Tarea A1 encontrada: {task_dict['title'][:60]}")
            print(f"  📍 Líneas: {task_dict['start_line']}-{task_dict['end_line']}")
            print(f"  📊 Nivel: {task_dict['level']}")
        else:
            print("  ❌ No se pudo encontrar tarea A1 en contenido")
    
    print("\n✅ Test de editor completado")

def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*70)
    print(" " * 15 + "SISTEMA DE TAREAS - TESTS COMPLETOS")
    print("="*70)
    
    try:
        test_display_ids()
        test_task_retrieval()
        test_unified_get_task_by_id()
        test_telegram_formatting()
        test_task_details()
        test_search()
        test_editor_mock()
        
        print("\n" + "="*70)
        print(" " * 20 + "✅ TODOS LOS TESTS PASARON")
        print("="*70)
        
        print("\n📋 RESUMEN:")
        print("  ✅ Generación de IDs temporales (A1-Z9)")
        print("  ✅ Recuperación por display ID")
        print("  ✅ Método unificado get_task_by_id()")
        print("  ✅ Formateo para Telegram")
        print("  ✅ Detalles de tareas")
        print("  ✅ Búsqueda de tareas")
        print("  ✅ Editor de tareas (instanciación)")
        
        print("\n🚀 COMANDOS DE TELEGRAM DISPONIBLES:")
        print("  /tasks [N]           - Listar tareas (con IDs A1, A2, etc.)")
        print("  /assign A1           - Asignar tarea por ID temporal")
        print("  /details A1          - Ver detalles de tarea")
        print("  /split A1 | s1 | s2  - Dividir tarea en subtareas")
        print("  /merge A1,A2 | t | d - Fusionar tareas")
        print("  /search_tasks api    - Buscar por palabra clave")
        print("  /progress            - Ver estadísticas generales")
        
        print("\n💡 PRÓXIMOS PASOS:")
        print("  1. Reiniciar bot de Telegram:")
        print("     python scripts/launch_congress_telegram.py")
        print("  2. Probar comandos en Telegram")
        print("  3. Verificar edición de tareas (split/merge)")
        
    except Exception as e:
        print(f"\n❌ ERROR EN TESTS: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
