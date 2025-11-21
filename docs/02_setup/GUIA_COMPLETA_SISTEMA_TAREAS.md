# 📋 Guía Completa del Sistema de Gestión de Tareas

**Fecha:** 2025-11-21  
**Estado:** ✅ Operacional  
**Versión:** 2.0 (con IDs temporales y edición)

---

## 🎯 Objetivo

Sistema robusto para trabajar PENDIENTES.md con múltiples agentes en paralelo, con:
- ✅ IDs temporales amigables (A1-Z9)
- ✅ Comandos de edición (split/merge)
- ✅ Integración con Telegram
- ✅ Búsqueda inteligente
- ✅ Tracking interno persistente

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│  PENDIENTES.md (2342 líneas, 105 tareas)               │
└────────────────────┬────────────────────────────────────┘
                     │
            ┌────────▼────────┐
            │  TaskParser     │  → Extrae tareas con metadata
            │  (parser.py)    │  → Genera IDs hash internos
            └────────┬────────┘
                     │
            ┌────────▼────────┐
            │  TaskProcessor  │  → Asignaciones y tracking
            │  (processor.py) │  → IDs temporales A1-Z9
            └────────┬────────┘  → Formateo para Telegram
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼────┐  ┌───▼───┐  ┌────▼────┐
   │ Editor  │  │ Bot   │  │ Congress│
   │ (editar)│  │(Tele) │  │(ejecutar)│
   └─────────┘  └───────┘  └─────────┘
```

---

## 🔑 Sistema de IDs

### IDs Temporales (Display)
- **Formato:** A1 - Z9 (2 caracteres alfanuméricos)
- **Rango:** 234 IDs posibles (26 letras × 9 números)
- **Uso:** Interfaz de usuario (Telegram, CLI)
- **Persistencia:** ❌ NO - Se regeneran cada sesión
- **Ejemplo:** A1, B5, Z9

### IDs Internos (Hash)
- **Formato:** SHA256 truncado (16 caracteres)
- **Ejemplo:** `UJ6b8f4e2a1c3d5e`
- **Uso:** Tracking interno, asignaciones
- **Persistencia:** ✅ SÍ - Permanente
- **Almacenamiento:** `~/Documents/d8_data/tasks/assignments.json`

### Conversión

```python
# Index → Display ID
index = 0  → "A1"
index = 8  → "A9"
index = 9  → "B1"
index = 233 → "Z9"

# Display ID → Index
"A1" → 0 (A = 0, offset 1 → 0*9 + 0 = 0)
"B5" → 13 (B = 1, offset 5 → 1*9 + 4 = 13)
```

---

## 📱 Comandos de Telegram

### Visualización

```bash
/tasks          # Lista top 10 tareas con IDs A1-A9
/tasks 20       # Lista top 20 tareas (A1-B2)
/pending        # Alias de /tasks
```

**Salida:**
```
📋 TAREAS PENDIENTES (top 10)

A1. 🔥 ⏳ Experiencias Profundas (D8-Specific)
     ⏱️ ~3h
     📝 Ubicación: docs/06_knowledge_base...

A2. 🔥 ⏳ Sistema de Instalación Automatizado
     ⏱️ ~5h
     📝 Estado: PENDIENTE, Prioridad: CRÍTICA...

💡 Usa /assign <ID> para asignar (ej: /assign A1)
```

### Asignación

```bash
/assign A1      # Asigna tarea A1 al congreso
/details A1     # Ver detalles completos de A1
/progress       # Estadísticas generales
```

### Búsqueda

```bash
/search_tasks telegram    # Busca "telegram" en títulos/descripciones
/search_tasks api         # Busca "api"
```

### Edición (Opción A)

```bash
# Dividir tarea en subtareas
/split A1 | Setup database | Create models | Add migrations

# Fusionar múltiples tareas
/merge A1,A2,A3 | Combined Task | This merges all three tasks into one

# Ejemplos reales
/split B5 | Frontend component | Backend API | Tests
/merge C1,C2 | Unified Feature | Combines login and auth flows
```

---

## 🔧 API Programática

### Listar Tareas

```python
from app.tasks.processor import TaskProcessor

processor = TaskProcessor()

# Obtener top 20 tareas pendientes
tasks = processor.list_pending_tasks(max_tasks=20)

for i, task in enumerate(tasks):
    display_id = processor._generate_display_id(i)
    print(f"{display_id}: {task.title} (prioridad: {task.priority})")
```

### Obtener Tarea por ID

```python
# Por ID temporal
task = processor.get_task_by_id("A1")

# Por ID interno
task = processor.get_task_by_id("UJ6b8f4e2a1c3d5e")

# Ambos funcionan con el método unificado
if task:
    print(f"Título: {task.title}")
    print(f"Prioridad: {task.priority}")
    print(f"Archivos: {task.files_mentioned}")
```

### Asignar Tarea

```python
# Asignar tarea
success = processor.assign_task("A1", assigned_to="Congress")

if success:
    print("Tarea asignada exitosamente")
else:
    print("Error: tarea no encontrada o ya asignada")
```

### Buscar Tareas

```python
# Buscar por palabra clave
results = processor.search_tasks("telegram")

print(f"Encontradas {len(results)} tareas:")
for task in results[:5]:
    print(f"- {task.title}")
```

### Editar Tareas

```python
from app.tasks.editor import TaskEditor
from pathlib import Path

pendientes = Path("PENDIENTES.md")
editor = TaskEditor(pendientes)

# Dividir tarea
success, msg = editor.split_task(
    task_id="A1",
    subtask_titles=[
        "Setup database",
        "Create models",
        "Add migrations"
    ],
    subtask_descriptions=[
        "Configure PostgreSQL connection",
        "Define User and Task models",
        "Create initial migration scripts"
    ]
)

print(msg)  # "✅ Tarea dividida en 3 subtareas"

# Fusionar tareas
success, msg = editor.merge_tasks(
    task_ids=["A1", "A2", "A3"],
    new_title="Unified Authentication System",
    new_description="Complete auth flow with login, signup, and password reset"
)

print(msg)  # "✅ 3 tareas fusionadas en una"
```

---

## 📊 Estadísticas y Progreso

```python
# Obtener estadísticas
stats = processor.get_completion_stats()

print(f"Total: {stats['total_tasks']}")
print(f"Pendientes: {stats['pending']}")
print(f"En proceso: {stats['in_progress']}")
print(f"Completadas: {stats['completed']}")
print(f"Tasa: {stats['completion_rate']:.1f}%")

# Tareas activas
active = processor.get_active_assignments()

for assignment in active:
    print(f"{assignment['task']['title']} → {assignment['assigned_to']}")
    print(f"  Inicio: {assignment['assigned_at']}")
```

---

## 🧪 Testing

### Ejecutar Tests Completos

```bash
python scripts/tests/test_task_editor.py
```

**Tests incluidos:**
1. ✅ Generación de IDs temporales (A1-Z9)
2. ✅ Recuperación por display ID
3. ✅ Método unificado get_task_by_id()
4. ✅ Formateo para Telegram
5. ✅ Detalles de tareas
6. ✅ Búsqueda de tareas
7. ✅ Editor (instanciación y búsqueda en contenido)

### Test Individual

```python
from app.tasks.processor import TaskProcessor

processor = TaskProcessor()

# Test display ID generation
assert processor._generate_display_id(0) == "A1"
assert processor._generate_display_id(8) == "A9"
assert processor._generate_display_id(9) == "B1"
assert processor._generate_display_id(233) == "Z9"

# Test task retrieval
task_a1 = processor.get_task_by_id("A1")
task_a1_lower = processor.get_task_by_id("a1")  # Case-insensitive
assert task_a1 == task_a1_lower

# Test search
results = processor.search_tasks("telegram")
assert len(results) > 0
```

---

## 🚀 Uso en Producción

### 1. Iniciar Bot de Telegram

```bash
python scripts/launch_congress_telegram.py
```

### 2. Usar Comandos

En Telegram:
```
/tasks          # Ver primeras 10 tareas
/assign A1      # Asignar tarea A1
/details A1     # Ver detalles
/progress       # Ver estadísticas
```

### 3. Editar Tareas

```
/split A5 | Part 1 | Part 2 | Part 3
/merge A1,A2 | Combined | New description
```

### 4. Monitorear Progreso

```python
# Script de monitoreo
from app.tasks.processor import TaskProcessor
import time

processor = TaskProcessor()

while True:
    stats = processor.get_completion_stats()
    active = len(processor.get_active_assignments())
    
    print(f"Progreso: {stats['completion_rate']:.1f}%")
    print(f"Activas: {active}")
    
    time.sleep(60)  # Cada minuto
```

---

## 📂 Estructura de Archivos

```
app/tasks/
├── __init__.py
├── parser.py           # Parseo de PENDIENTES.md
├── processor.py        # Lógica de asignación y IDs
└── editor.py           # Edición de tareas (split/merge)

scripts/tests/
└── test_task_editor.py # Suite completa de tests

docs/02_setup/
├── GUIA_RAPIDA_GESTION_TAREAS.md  # Quick start
└── GUIA_COMPLETA_SISTEMA_TAREAS.md # Este archivo

~/Documents/d8_data/tasks/
├── assignments.json    # Tareas asignadas (con IDs internos)
└── completed.json      # Tareas completadas
```

---

## ⚙️ Configuración

### Ubicación de PENDIENTES.md

Por defecto: `./PENDIENTES.md` (raíz del proyecto)

Cambiar:
```python
from pathlib import Path
from app.tasks.processor import TaskProcessor

custom_path = Path("/ruta/custom/tareas.md")
processor = TaskProcessor()
processor.parser.pendientes_file = custom_path
```

### Límite de IDs Temporales

Máximo: 234 tareas (A1-Z9)

Si necesitas más:
- Reduce número de tareas mostradas
- Usa búsqueda específica
- O modifica formato de IDs (ej: AA1-ZZ9)

---

## 🐛 Troubleshooting

### "Tarea no encontrada: A1"

**Causa:** IDs temporales se regeneran cada sesión.

**Solución:**
```bash
/tasks    # Ver IDs actuales
/assign A1  # Usar ID actualizado
```

### "TaskProcessor.__init__() takes 1 positional argument"

**Causa:** Código antiguo pasando argumento a TaskProcessor.

**Solución:**
```python
# ❌ Antiguo
processor = TaskProcessor(pendientes_file)

# ✅ Nuevo
processor = TaskProcessor()  # Sin argumentos
```

### Git commit falla en editor

**Causa:** Git no inicializado o sin permisos.

**Solución:**
```bash
cd /ruta/proyecto
git init
git config user.email "bot@d8.ai"
git config user.name "D8 TaskEditor"
```

---

## 🔜 Próximas Funcionalidades (Opción B)

### Edición con Lenguaje Natural

```
Usuario: "Divide la tarea A1 en 3 partes"
Bot: [LLM analiza tarea y genera 3 subtareas inteligentes]
     ¿Confirmar división?
     1. Setup inicial
     2. Implementación core
     3. Tests y documentación
     [Sí] [No] [Modificar]

Usuario: "Sí"
Bot: ✅ Tarea A1 dividida exitosamente
```

### Intenciones Soportadas

- "Divide esta tarea"
- "Fusiona A1 y A2"
- "Reorganiza las subtareas de B3"
- "Prioriza las tareas de API"
- "Agrupa tareas similares"

---

## 📚 Referencias

- **Parser:** `app/tasks/parser.py` (líneas 1-346)
- **Processor:** `app/tasks/processor.py` (líneas 1-347)
- **Editor:** `app/tasks/editor.py` (líneas 1-250)
- **Tests:** `scripts/tests/test_task_editor.py` (líneas 1-260)
- **Telegram Bot:** `app/integrations/telegram_bot.py` (líneas 814-1100)

---

**Última actualización:** 2025-11-21  
**Estado:** ✅ Operacional  
**Próximo paso:** Implementar Opción B (NLP con LLM)
