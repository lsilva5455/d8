# 🚀 Guía Rápida: Sistema de Gestión de Tareas

## ✅ Implementación Completa

**Fecha:** 2025-11-21  
**Status:** ✅ Operacional

---

## 📱 Uso desde Telegram

### 1. Iniciar/Reiniciar el Bot
```bash
python scripts/launch_congress_telegram.py
```

### 2. Comandos Disponibles

#### Listar Tareas Pendientes
```
/tasks           → Top 10 tareas
/tasks 20        → Top 20 tareas
/pending         → Alias de /tasks
```

**Ejemplo de salida:**
```
📋 TAREAS PENDIENTES (top 10)

1. 🔥 ⏳ Sistema de Instalación Automatizado
   ID: 83989e98
   ⏱️ ~5h
   📝 Durante la instalación del primer slave...

2. 🔴 ⏳ Sistema de Gestión de Tareas
   ID: 03e82192
   📝 Crear un sistema profesional y robusto...
```

#### Asignar Tarea al Congreso
```
/assign 83989e98
```

**Respuesta:**
```
✅ Tarea asignada al congreso

**Sistema de Instalación Automatizado**

ID: 83989e98
Prioridad: 🔥🔥🔥🔥🔥
Estimación: 5h

El congreso comenzará a trabajar en esto.
Te notificaré cuando complete la tarea.
```

#### Ver Detalles de una Tarea
```
/details 83989e98
```

**Respuesta:**
```
📋 DETALLES DE TAREA

**Título:** Sistema de Instalación Completamente Automatizado

**Prioridad:** 🔥 CRÍTICA
**Estado:** PENDIENTE
**ID:** 83989e98
**Estimación:** 5 horas

**Archivos mencionados:**
- `app/distributed/build_d8_slave.py`
- `scripts/install_new_slave.py`

**Descripción:**
[contenido completo de la sección]
```

#### Ver Progreso General
```
/progress
```

**Respuesta:**
```
📊 PROGRESO DE TAREAS

📋 Total: 105
⏳ Pendientes: 104
⚙️ En proceso: 1
✅ Completadas: 0

📈 Tasa de completitud: 0.0%

**Tareas activas:**
• Sistema de Instalación Completamente Automatizado...
```

---

## 🖥️ Uso desde CLI

### Test del Sistema
```bash
python scripts/test_task_system.py
```

### Uso Programático
```python
from app.tasks.processor import TaskProcessor
from scripts.autonomous_congress import AutonomousCongress

# Listar tareas
processor = TaskProcessor()
tasks = processor.list_pending_tasks(max_tasks=5)

for task in tasks:
    print(f"{task.title} (ID: {task.task_id[:8]})")

# Asignar al congreso
congress = AutonomousCongress()
congress.assign_manual_task("83989e98", requested_by="Leo")

# El congreso procesará automáticamente
```

---

## 🔄 Flujo Completo

```
1. Leo abre Telegram
         ↓
2. /tasks → Ve lista de pendientes
         ↓
3. /assign 83989e98 → Asigna tarea crítica
         ↓
4. Bot: "✅ Tarea asignada al congreso"
         ↓
5. Congreso trabaja automáticamente:
   - Researcher analiza el problema
   - Experimenter diseña approach
   - Implementer codea solución
   - Validator verifica resultado
         ↓
6. Bot notifica: "✅ Tarea completada"
         ↓
7. Leo: /progress → Ve actualización
```

---

## 📊 Estadísticas Actuales

**Parseadas:** 105 tareas desde PENDIENTES.md  
**Pendientes:** 105 tareas (0% completadas)  
**Top Priority:** 🔥 Sistema de Instalación Automatizado (5h)  

---

## 💡 Tips

### IDs de Tareas
- Los IDs son hash únicos de 12 caracteres
- Solo necesitas los primeros 8 para identificar: `83989e98`
- Usa `/tasks` para ver IDs disponibles

### Prioridades
- 🔥🔥🔥🔥🔥 = CRÍTICA (5)
- 🔥🔥🔥🔥 = ALTA (4)
- 🔥🔥🔥 = MEDIA (3)
- 🔥🔥 = BAJA (2)
- 🔥 = OPCIONAL (1)

### Estados
- ⏳ PENDIENTE - No iniciada
- ⚙️ EN_PROCESO - Asignada al congreso
- ✅ COMPLETADO - Finalizada

---

## 🎯 Comandos Rápidos

```bash
# Ver tareas
/tasks

# Asignar la más crítica
/tasks
/assign <primer_id>

# Ver progreso
/progress

# Buscar por tema
/search telegram
/search supervisor
/search slave
```

---

## 🔗 Referencias

- **Documentación completa:** `docs/03_operaciones/sistema_gestion_tareas.md`
- **Reporte de implementación:** `docs/07_reportes/implementacion_gestion_tareas_2025-11-21.md`
- **Plan completo (Phase 2):** `PENDIENTES.md` → "Sistema de Gestión de Tareas con Agentes Paralelos"

---

## ✅ Checklist de Inicio

- [ ] Bot de Telegram corriendo (`python scripts/launch_congress_telegram.py`)
- [ ] Test ejecutado exitosamente (`python scripts/test_task_system.py`)
- [ ] Congreso operacional
- [ ] Primeros comandos probados en Telegram

---

**¡Listo para usar!** 🎉

Ahora puedes gestionar todos tus pendientes desde Telegram de forma natural e inteligente.
