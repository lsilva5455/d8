# 📋 Sistema de Gestión de Tareas Inteligente

**Fecha de implementación:** 2025-11-21  
**Status:** ✅ Operacional

---

## 🎯 Objetivo

Permitir que el Congreso Autónomo entienda y procese pendientes desde `PENDIENTES.md` de forma natural, accesible tanto por Telegram como por línea de comandos.

---

## 🏗️ Arquitectura

```
PENDIENTES.md
      ↓
  TaskParser  → Extrae tareas estructuradas
      ↓
  ParsedTask  → Dataclass con metadata
      ↓
 TaskProcessor → Gestiona asignaciones
      ↓
  AutonomousCongress → Procesa tareas
```

---

## 📦 Componentes

### 1. **TaskParser** (`app/tasks/parser.py`)

**Responsabilidad:** Parsear `PENDIENTES.md` y extraer tareas estructuradas

**Funcionalidades:**
- Detecta headers (## Título)
- Extrae prioridades (🔥 CRÍTICA, 🔴 ALTA, etc.)
- Identifica estados (⏳ PENDIENTE, ✅ COMPLETADO)
- Calcula estimaciones (4-6 horas → 5h)
- Extrae referencias a archivos
- Genera IDs únicos (hash SHA256)

**Ejemplo de uso:**
```python
from app.tasks.parser import TaskParser

parser = TaskParser()
tasks = parser.parse_file()

# Filtrar por estado
pending = parser.get_tasks_by_status("PENDIENTE")

# Filtrar por prioridad
critical = parser.get_tasks_by_priority(min_priority=4)

# Obtener tareas asignables
assignable = parser.get_assignable_tasks()
```

---

### 2. **ParsedTask** (Dataclass)

**Schema:**
```python
@dataclass
class ParsedTask:
    task_id: str                    # Hash único (12 chars)
    title: str                      # Título de la sección
    description: str                # Contenido completo
    priority: int                   # 1-5 (5=CRÍTICA)
    status: str                     # PENDIENTE, EN_PROCESO, COMPLETADO
    estimated_hours: Optional[int]  # Estimación en horas
    files_mentioned: List[str]      # Archivos referenciados
    assignable: bool                # ¿Se puede asignar?
    created_date: Optional[str]     # Fecha de creación
```

---

### 3. **TaskProcessor** (`app/tasks/processor.py`)

**Responsabilidad:** Conectar el parser con el Congreso

**Funcionalidades:**
- Listar tareas pendientes
- Asignar tareas al Congreso
- Trackear progreso
- Buscar tareas por keyword
- Generar reportes

**Persistencia:**
- `~/Documents/d8_data/tasks/assignments.json` - Tareas asignadas
- `~/Documents/d8_data/tasks/completed.json` - Tareas completadas

**Ejemplo de uso:**
```python
from app.tasks.processor import TaskProcessor

processor = TaskProcessor()

# Listar top 10 pendientes
tasks = processor.list_pending_tasks(max_tasks=10)

# Buscar por keyword
results = processor.search_tasks("telegram")

# Asignar tarea
processor.assign_task("a3b5c7d9", assigned_to="Congress")

# Marcar como completada
processor.complete_task("a3b5c7d9", result={
    "success": True,
    "message": "Implementado exitosamente",
    "artifacts": ["app/tasks/parser.py"]
})

# Estadísticas
stats = processor.get_completion_stats()
# → {'total_tasks': 50, 'pending': 30, 'in_progress': 5, 'completed': 15}
```

---

## 🤖 Integración con Congreso Autónomo

El Congreso puede procesar tareas de dos formas:

### 1. Tarea desde PENDIENTES.md
```python
# Leo asigna tarea por ID
congress.assign_manual_task("a3b5c7d9", requested_by="Leo")

# El sistema:
# 1. Identifica que es un ID válido
# 2. Carga contexto completo de la tarea
# 3. Asigna al Congreso
# 4. Congreso ejecuta ciclo autónomo
# 5. Reporta resultados
```

### 2. Tarea libre (legacy)
```python
# Leo asigna descripción libre
congress.assign_manual_task(
    "Optimizar prompts de agentes para SEO",
    requested_by="Leo"
)
```

---

## 📱 Comandos de Telegram

### Listar Tareas
```
/tasks              → Top 10 pendientes
/tasks 20           → Top 20 pendientes
/pending            → Alias de /tasks
```

**Salida:**
```
📋 TAREAS PENDIENTES (top 10)

1. 🔥 ⏳ Sistema de Gestión de Tareas con Agentes Paralelos
   ID: a3b5c7d9
   ⏱️ ~8h
   📝 Crear un sistema profesional y robusto...

2. 🔴 ⏳ Correcciones Críticas para Instalación Automática
   ID: b2f4e1a7
   ⏱️ ~6h
   📝 Durante la instalación del primer slave...
```

---

### Asignar Tarea
```
/assign a3b5c7d9
```

**Salida:**
```
✅ Tarea asignada al congreso

**Sistema de Gestión de Tareas con Agentes Paralelos**

ID: a3b5c7d9
Prioridad: 🔥🔥🔥🔥🔥
Estimación: 8h

El congreso comenzará a trabajar en esto.
Te notificaré cuando complete la tarea.
```

---

### Ver Detalles
```
/details a3b5c7d9
```

**Salida:**
```
📋 DETALLES DE TAREA

**Título:** Sistema de Gestión de Tareas con Agentes Paralelos

**Prioridad:** 🔥 CRÍTICA
**Estado:** PENDIENTE
**ID:** a3b5c7d9
**Estimación:** 8 horas

**Archivos mencionados:**
- `app/tasks/parser.py`
- `app/tasks/processor.py`
- `app/tasks/coordinator.py`

**Descripción:**
Crear un sistema profesional y robusto que permita...
[contenido completo]
```

---

### Buscar Tareas
```
/search telegram
```

**Salida:**
```
🔍 RESULTADOS para 'telegram' (3 encontradas)

1. 🔴 ⏳ GitHub Copilot + Telegram Bot Inteligente
   ID: c5d8a3f1
   
2. 🟡 ⏳ Integración de Telegram con Congreso
   ID: d9e2f4b6
```

---

### Ver Progreso
```
/progress
```

**Salida:**
```
📊 PROGRESO DE TAREAS

📋 Total: 50
⏳ Pendientes: 30
⚙️ En proceso: 5
✅ Completadas: 15

📈 Tasa de completitud: 30.0%

**Tareas activas:**
• Sistema de Gestión de Tareas con Agentes Para...
• Correcciones Críticas para Instalación Automá...
```

---

## 🖥️ Uso desde CLI

### Test del Sistema
```bash
python scripts/test_task_system.py
```

**Salida:**
```
======================================================================
🧪 TEST: Sistema de Gestión de Tareas
======================================================================

📋 Parseando PENDIENTES.md...
✅ Parseadas 50 tareas

🔥 TOP 5 TAREAS POR PRIORIDAD:
----------------------------------------------------------------------
1. 🔥 Sistema de Gestión de Tareas con Agentes Paralelos
   ID: a3b5c7d9 | Status: PENDIENTE
   Estimación: 8h

2. 🔥 Correcciones Críticas para Instalación Automática de Slaves
   ID: b2f4e1a7 | Status: PENDIENTE
   Estimación: 6h
   
...

📊 Estadísticas generales:
----------------------------------------------------------------------
Total: 50
Pendientes: 30
En proceso: 5
Completadas: 15
Tasa de completitud: 30.0%
```

---

### Uso Programático
```python
from app.tasks.processor import TaskProcessor

# Inicializar
processor = TaskProcessor()

# Listar tareas
tasks = processor.list_pending_tasks(max_tasks=5)

for task in tasks:
    print(f"{task.title} (ID: {task.task_id[:8]})")

# Asignar al congreso
from scripts.autonomous_congress import AutonomousCongress

congress = AutonomousCongress()
congress.assign_manual_task("a3b5c7d9", requested_by="Script")

# El congreso ahora procesará esta tarea automáticamente
```

---

## 📊 Detección de Metadata

### Prioridades
```markdown
🔥 CRÍTICA     → priority = 5
🔴 ALTA        → priority = 4
🟡 MEDIA       → priority = 3
🟢 BAJA        → priority = 2
⚪ OPCIONAL    → priority = 1
```

### Estados
```markdown
⏳ PENDIENTE      → status = "PENDIENTE"
⚙️ EN_PROCESO     → status = "EN_PROCESO"
✅ COMPLETADO     → status = "COMPLETADO"
```

### Estimaciones
```markdown
4-6 horas          → estimated_hours = 5
2-3 días           → estimated_hours = 20  (2.5 días * 8h)
Estimación: 8h     → estimated_hours = 8
```

### Archivos
```markdown
`app/tasks/parser.py`              → files_mentioned
**Archivo:** `scripts/test.py`    → files_mentioned
Ubicación: `app/congress/...`     → files_mentioned
```

---

## 🔄 Flujo Completo

### 1. Leo ve pendientes por Telegram
```
Leo: /tasks
Bot: [Lista top 10 tareas]
```

### 2. Leo asigna tarea
```
Leo: /assign a3b5c7d9
Bot: ✅ Tarea asignada al congreso
```

### 3. Congreso procesa automáticamente
- Researcher analiza la tarea
- Experimenter diseña approach
- Implementer codea solución
- Validator verifica resultado

### 4. Congreso notifica completion
```
Bot → Leo: ✅ Tarea completada: Sistema de Gestión de Tareas

Resultados:
- 3 archivos creados
- Tests pasando
- PR #156 creado

¿Aprobar PR?
```

### 5. Leo valida y mergea
```
Leo: /approve
Bot: ✅ PR #156 mergeado
```

---

## 🎯 Ventajas

✅ **Natural:** Leo puede pedir tareas en lenguaje natural  
✅ **Estructurado:** Parser extrae metadata automáticamente  
✅ **Trackeable:** Progreso visible en tiempo real  
✅ **Flexible:** Funciona desde Telegram o CLI  
✅ **Integrado:** Congreso entiende contexto completo  
✅ **Escalable:** Sistema listo para trabajo paralelo (Phase 2)

---

## 📝 Próximos Pasos (Opcional - Phase 2)

1. **Paralelización:** Múltiples agentes trabajando simultáneamente
2. **Git Branches:** Branch automático por tarea
3. **Locks:** Prevenir conflictos entre agentes
4. **Auto-merge:** PRs se mergean automáticamente si pasan tests
5. **Dashboard:** Interface web para monitoreo

Ver: `PENDIENTES.md` → "Sistema de Gestión de Tareas con Agentes Paralelos"

---

## 🔗 Referencias

- **Parser:** `app/tasks/parser.py`
- **Processor:** `app/tasks/processor.py`
- **Test:** `scripts/test_task_system.py`
- **Congreso:** `scripts/autonomous_congress.py`
- **Bot:** `app/integrations/telegram_bot.py`

---

**Última actualización:** 2025-11-21  
**Status:** ✅ Operacional  
**Autor:** GitHub Copilot + Metodología D8
