"""
Script para probar el sistema de tareas desde línea de comandos
"""

import sys
from pathlib import Path

# Agregar raíz del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.tasks.parser import TaskParser
from app.tasks.processor import TaskProcessor


def main():
    print("="*70)
    print("🧪 TEST: Sistema de Gestión de Tareas")
    print("="*70)
    print()
    
    # Test parser
    print("📋 Parseando PENDIENTES.md...")
    parser = TaskParser()
    tasks = parser.parse_file()
    
    print(f"✅ Parseadas {len(tasks)} tareas\n")
    
    # Mostrar top 5 por prioridad
    print("🔥 TOP 5 TAREAS POR PRIORIDAD:")
    print("-"*70)
    for i, task in enumerate(tasks[:5], 1):
        priority_emoji = {5: "🔥", 4: "🔴", 3: "🟡", 2: "🟢", 1: "⚪"}.get(task.priority, "📋")
        print(f"{i}. {priority_emoji} {task.title}")
        print(f"   ID: {task.task_id[:8]} | Status: {task.status}")
        if task.estimated_hours:
            print(f"   Estimación: {task.estimated_hours}h")
        print()
    
    # Test processor
    print("\n📊 Estadísticas generales:")
    print("-"*70)
    processor = TaskProcessor()
    stats = processor.get_completion_stats()
    
    print(f"Total: {stats['total_tasks']}")
    print(f"Pendientes: {stats['pending']}")
    print(f"En proceso: {stats['in_progress']}")
    print(f"Completadas: {stats['completed']}")
    print(f"Tasa de completitud: {stats['completion_rate']:.1f}%")
    
    # Test búsqueda
    print("\n\n🔍 TEST: Búsqueda de tareas")
    print("-"*70)
    query = "telegram"
    results = processor.search_tasks(query)
    print(f"Búsqueda: '{query}' → {len(results)} resultados")
    
    for i, task in enumerate(results[:3], 1):
        print(f"{i}. {task.title[:60]}...")
    
    print("\n✅ Tests completados exitosamente\n")


if __name__ == "__main__":
    main()
