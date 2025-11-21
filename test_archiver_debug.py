"""Debug del archivador"""
from app.tasks.archiver import TaskArchiver
from pathlib import Path
from datetime import datetime, timedelta

# Crear test data con fechas dinámicas
FIVE_DAYS_AGO = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
ONE_DAY_AGO = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

TEST_CONTENT = f"""# TEST

## ✅ Tarea Hace 5 Días
**Estado:** ✅ COMPLETADO  
**Completado:** {FIVE_DAYS_AGO}  

Esta tarea debe archivarse.
"""

print(f"Fecha hace 5 días: {FIVE_DAYS_AGO}")
print(f"Fecha hace 1 día: {ONE_DAY_AGO}")
print(f"Hoy: {datetime.now().strftime('%Y-%m-%d')}")

archiver = TaskArchiver(days_before_archive=2)
tasks = archiver.find_completed_tasks(TEST_CONTENT)

print(f"\nTareas encontradas: {len(tasks)}")
for task in tasks:
    print(f"\nTarea: {task['title']}")
    print(f"  Completado: {task['completed_date']}")
    print(f"  Días: {task.get('days_since_completion')}")
    print(f"  Archivable: {task['archivable']}")
