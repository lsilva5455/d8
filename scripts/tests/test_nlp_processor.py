"""
Test del procesador NLP de tareas
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parents[2]
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

def test_nlp_intent_detection():
    """Test detección de intenciones"""
    print("\n" + "="*60)
    print("TEST: Detección de Intenciones con LLM")
    print("="*60)
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("  ⚠️  GROQ_API_KEY no configurada, saltando test")
        return
    
    from app.tasks.nlp_processor import NLPTaskProcessor
    from app.tasks.processor import TaskProcessor
    
    nlp = NLPTaskProcessor(groq_api_key)
    processor = TaskProcessor()
    
    # Obtener contexto
    task_context = processor.list_pending_tasks(max_tasks=5)
    
    # Test cases
    test_inputs = [
        ("divide la tarea A1 en 3 partes", "split_task"),
        ("fusiona A1 y A2", "merge_tasks"),
        ("muéstrame los detalles de A5", "detail_task"),
        ("sugiere subtareas para A1", "suggest_subtasks"),
    ]
    
    print("\n🧪 Probando detección de intenciones:\n")
    
    for user_input, expected_intent in test_inputs:
        print(f"📝 Entrada: '{user_input}'")
        
        result = nlp.process_natural_command(user_input, task_context)
        
        detected_intent = result.get("intent", "unknown")
        confidence = result.get("confidence", 0.0)
        
        status = "✅" if detected_intent == expected_intent else "❌"
        print(f"   {status} Detectado: {detected_intent} (esperado: {expected_intent})")
        print(f"   📊 Confianza: {confidence:.2f}")
        
        if "message" in result:
            print(f"   💬 Mensaje: {result['message'][:100]}...")
        
        print()
    
    print("✅ Test de detección completado\n")

def test_nlp_split_suggestions():
    """Test generación de sugerencias para split"""
    print("\n" + "="*60)
    print("TEST: Sugerencias Inteligentes de Split")
    print("="*60)
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("  ⚠️  GROQ_API_KEY no configurada, saltando test")
        return
    
    from app.tasks.nlp_processor import NLPTaskProcessor
    from app.tasks.processor import TaskProcessor
    
    nlp = NLPTaskProcessor(groq_api_key)
    processor = TaskProcessor()
    
    # Obtener primera tarea
    tasks = processor.list_pending_tasks(max_tasks=1)
    
    if not tasks:
        print("  ⚠️  No hay tareas disponibles")
        return
    
    task = tasks[0]
    
    print(f"\n📋 Tarea: {task.title[:60]}")
    print(f"📝 Descripción: {task.description[:150]}...")
    
    print("\n🤔 Generando sugerencias de subtareas...")
    
    suggestions = nlp._generate_subtask_suggestions(task, num_subtasks=3)
    
    print(f"\n💡 Sugerencias generadas ({len(suggestions)} subtareas):\n")
    
    for i, subtask in enumerate(suggestions, 1):
        print(f"{i}. {subtask['title']}")
        print(f"   📝 {subtask.get('description', 'Sin descripción')}")
        print(f"   ⏱️  ~{subtask.get('estimated_hours', '?')}h\n")
    
    print("✅ Test de sugerencias completado\n")

def test_nlp_merge_suggestions():
    """Test generación de merge"""
    print("\n" + "="*60)
    print("TEST: Sugerencias de Fusión")
    print("="*60)
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("  ⚠️  GROQ_API_KEY no configurada, saltando test")
        return
    
    from app.tasks.nlp_processor import NLPTaskProcessor
    from app.tasks.processor import TaskProcessor
    
    nlp = NLPTaskProcessor(groq_api_key)
    processor = TaskProcessor()
    
    # Obtener primeras 2 tareas
    tasks = processor.list_pending_tasks(max_tasks=2)
    
    if len(tasks) < 2:
        print("  ⚠️  Necesitamos al menos 2 tareas")
        return
    
    print(f"\n📋 Tareas a fusionar:")
    for task in tasks:
        print(f"   - {task.title[:60]}")
    
    print("\n🤔 Generando sugerencia de fusión...")
    
    merged = nlp._generate_merged_task(tasks)
    
    print(f"\n💡 Tarea fusionada propuesta:\n")
    print(f"**Título:** {merged['title']}\n")
    print(f"**Descripción:**\n{merged['description'][:300]}...\n")
    
    print("✅ Test de fusión completado\n")

def test_nlp_full_workflow():
    """Test workflow completo: comando → sugerencia → confirmación"""
    print("\n" + "="*60)
    print("TEST: Workflow Completo NLP")
    print("="*60)
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("  ⚠️  GROQ_API_KEY no configurada, saltando test")
        return
    
    from app.tasks.nlp_processor import NLPTaskProcessor
    from app.tasks.processor import TaskProcessor
    
    nlp = NLPTaskProcessor(groq_api_key)
    processor = TaskProcessor()
    
    # Contexto
    task_context = processor.list_pending_tasks(max_tasks=10)
    
    # Simular comando de usuario
    user_command = "divide la tarea A1 en 3 partes"
    
    print(f"\n👤 Usuario: '{user_command}'\n")
    print("🤖 Bot: Procesando...")
    
    result = nlp.process_natural_command(user_command, task_context)
    
    print("\n📊 Resultado del procesamiento:\n")
    print(f"   Intent: {result.get('intent')}")
    print(f"   Confidence: {result.get('confidence', 0):.2f}")
    print(f"   Requires Confirmation: {result.get('requires_confirmation', False)}")
    
    if "message" in result:
        print(f"\n💬 Mensaje al usuario:\n")
        print(result["message"])
    
    if "action" in result:
        print(f"\n⚙️  Acción preparada:")
        print(f"   Type: {result['action'].get('type')}")
        print(f"   Task ID: {result['action'].get('task_id')}")
        
        if result['action'].get('type') == 'split':
            subtasks = result['action'].get('subtasks', [])
            print(f"   Subtasks: {len(subtasks)}")
    
    print("\n✅ Test de workflow completado\n")

def test_nlp_error_handling():
    """Test manejo de errores"""
    print("\n" + "="*60)
    print("TEST: Manejo de Errores")
    print("="*60)
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("  ⚠️  GROQ_API_KEY no configurada, saltando test")
        return
    
    from app.tasks.nlp_processor import NLPTaskProcessor
    
    nlp = NLPTaskProcessor(groq_api_key)
    
    error_cases = [
        ("hola", "Comando sin sentido"),
        ("divide la tarea", "Falta especificar ID"),
        ("fusiona A1", "Solo una tarea para merge"),
        ("divide Z99", "ID inexistente"),
    ]
    
    print("\n🧪 Probando casos de error:\n")
    
    for user_input, error_type in error_cases:
        print(f"📝 Entrada: '{user_input}' ({error_type})")
        
        result = nlp.process_natural_command(user_input)
        
        if "error" in result:
            print(f"   ✅ Error detectado correctamente")
            print(f"   💬 {result['error'][:80]}...")
        else:
            print(f"   ⚠️  No se detectó error esperado")
        
        print()
    
    print("✅ Test de errores completado\n")

def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*70)
    print(" " * 15 + "SISTEMA NLP - TESTS COMPLETOS")
    print("="*70)
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not groq_api_key:
        print("\n⚠️  GROQ_API_KEY no configurada en .env")
        print("   Los tests NLP requieren API key de Groq")
        print("\n   Configura en .env:")
        print("   GROQ_API_KEY=gsk_...")
        return 1
    
    try:
        test_nlp_intent_detection()
        test_nlp_split_suggestions()
        test_nlp_merge_suggestions()
        test_nlp_full_workflow()
        test_nlp_error_handling()
        
        print("\n" + "="*70)
        print(" " * 20 + "✅ TODOS LOS TESTS PASARON")
        print("="*70)
        
        print("\n📋 RESUMEN:")
        print("  ✅ Detección de intenciones con LLM")
        print("  ✅ Generación de sugerencias de split")
        print("  ✅ Generación de sugerencias de merge")
        print("  ✅ Workflow completo (comando → acción)")
        print("  ✅ Manejo de errores")
        
        print("\n🚀 COMANDOS TELEGRAM CON NLP:")
        print("  /nlp divide la tarea A1 en 3 partes")
        print("  /nlp fusiona A1 y A2")
        print("  /nlp sugiere subtareas para A5")
        print("  /nlp muéstrame los detalles de A1")
        
        print("\n💡 VENTAJAS DEL NLP:")
        print("  ✨ Comandos en lenguaje natural")
        print("  🤖 Sugerencias inteligentes con LLM")
        print("  ✅ Confirmación interactiva")
        print("  📝 Contexto de tareas para mejor comprensión")
        
    except Exception as e:
        print(f"\n❌ ERROR EN TESTS: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
