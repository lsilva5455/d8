# 🗄️ Sistema de Archivado Automático de Tareas

**Fecha:** 2025-11-21  
**Estado:** ✅ Operacional

---

## Problema

PENDIENTES.md se llena de tareas completadas, haciendo difícil ver qué falta por hacer.

## Solución

Sistema automático que archiva tareas completadas después de N días (default: 2).

---

## Funcionamiento

### Detección Automática

Identifica tareas completadas por:
- ✅ Checkmark en título
- `**Estado:** ✅ COMPLETADO`
- `Completado: YYYY-MM-DD`

### Período de Espera

Las tareas completadas permanecen en PENDIENTES.md por **2 días** (configurable), permitiendo:
- Revisión visual de trabajo reciente
- Correcciones si es necesario
- Historial inmediato accesible

### Archivado

Después de N días:
1. 📦 Tarea se mueve a `ARCHIVADOS.md`
2. 💾 Se crea backup `PENDIENTES.md.bak`
3. ✅ PENDIENTES.md queda limpio

---

## Comandos de Telegram

### `/archive_preview [días]`

Preview de qué se archivaría sin modificar archivos.

```
/archive_preview
/archive_preview 3  # Cambiar umbral a 3 días
```

**Output:**
```
📊 TAREAS COMPLETADAS

Total: 15
Archivables (>2 días): 8

🗄️ Tareas a archivar:

• ✅ Sistema de Gestión de Tareas
  Completado: 2025-11-18 (3 días atrás)

• ✅ Integración Telegram Bot
  Completado: 2025-11-17 (4 días atrás)
```

### `/archive_stats [días]`

Estadísticas detalladas de archivado.

```
/archive_stats
```

**Output:**
```
📊 ESTADÍSTICAS DE ARCHIVADO

Total completadas: 15
Archivables ahora: 8
En período de espera: 7
Umbral: 2 días

Distribución por días:
  1 días: 3 tareas - ⏳ Esperando
  2 días: 4 tareas - ✅ Archivable
  5 días: 6 tareas - ✅ Archivable
  10 días: 2 tareas - ✅ Archivable
```

### `/archive_now [días]`

Ejecuta archivado con confirmación interactiva.

```
/archive_now
/archive_now 5  # Solo archivar tareas >5 días
```

**Flow:**
1. Bot muestra preview
2. Botones: ✅ Sí, archivar | ❌ Cancelar
3. Si confirmas → Archivado ejecutado
4. Reporte final con lista de archivadas

---

## CLI para Testing

```bash
# Preview
python -m app.tasks.archiver --preview

# Estadísticas
python -m app.tasks.archiver --stats

# Ejecutar archivado
python -m app.tasks.archiver --execute --days 2

# Cambiar umbral
python -m app.tasks.archiver --execute --days 5
```

---

## Uso Programático

```python
from app.tasks.archiver import TaskArchiver

# Crear archiver
archiver = TaskArchiver(
    pendientes_file=Path("PENDIENTES.md"),
    archivados_file=Path("ARCHIVADOS.md"),
    days_before_archive=2
)

# Preview (sin modificar)
result = archiver.archive_tasks(dry_run=True)
print(f"Archivables: {result['archivable']}")

# Ejecutar archivado
result = archiver.archive_tasks(dry_run=False)
print(f"Archivadas: {result['archived']}")

# Estadísticas
stats = archiver.get_stats()
print(f"Total completadas: {stats['total_completed']}")
print(f"Archivables: {stats['archivable_now']}")
```

---

## Formato de ARCHIVADOS.md

```markdown
# 📦 TAREAS ARCHIVADAS D8

**Tareas completadas que fueron archivadas automáticamente**  
**Período de retención en PENDIENTES.md:** 2 días

---

## Archivado: 2025-11-21 10:30:00

### ✅ Sistema de Gestión de Tareas
**Estado:** ✅ COMPLETADO  
**Completado:** 2025-11-18  
**Prioridad:** Alta

[contenido completo de la tarea]

---

### ✅ Integración Telegram Bot
**Estado:** ✅ COMPLETADO  
**Completado:** 2025-11-17  
**Prioridad:** Media

[contenido completo de la tarea]

---
```

---

## Configuración Recomendada

### Para Proyectos Activos
```python
days_before_archive = 2  # Archiva rápido, mantiene vista limpia
```

### Para Proyectos con Revisión
```python
days_before_archive = 7  # Una semana de historial visible
```

### Para Archivado Agresivo
```python
days_before_archive = 0  # Archiva inmediatamente al completar
```

---

## Seguridad

### Backup Automático
Antes de archivar, se crea `PENDIENTES.md.bak`.

### Recuperación Manual
```bash
# Si algo salió mal
cp PENDIENTES.md.bak PENDIENTES.md
```

### Git Integration
Puedes commitear archivados periódicamente:

```bash
git add PENDIENTES.md ARCHIVADOS.md
git commit -m "chore: Archivar tareas completadas"
```

---

## Tests

```bash
# Ejecutar tests
pytest scripts/tests/test_archiver.py -v

# Tests incluidos:
# ✅ Detección de tareas completadas
# ✅ Extracción de fechas de completado
# ✅ Cálculo de días desde completado
# ✅ Archivado con dry_run
# ✅ Archivado real
# ✅ Creación de backup
# ✅ Estadísticas
# ✅ Diferentes umbrales
```

---

## Integración con Congreso

El sistema de archivado puede ser automatizado por el Congreso:

```python
# En autonomous_congress.py
def cleanup_tasks():
    archiver = TaskArchiver(days_before_archive=2)
    result = archiver.archive_tasks(dry_run=False)
    
    if result['archived'] > 0:
        log_event(f"Archivadas {result['archived']} tareas")

# Ejecutar diariamente
schedule.every().day.at("00:00").do(cleanup_tasks)
```

---

## Archivos

- **Código:** `app/tasks/archiver.py` (461 líneas)
- **Tests:** `scripts/tests/test_archiver.py` (262 líneas)
- **Telegram:** `app/integrations/telegram_bot.py` (3 comandos nuevos)

---

## Ejemplo Real

**Antes:**
```
PENDIENTES.md (2620 líneas)
- 105 tareas
- 15 completadas mezcladas
- Difícil ver qué falta
```

**Después de /archive_now:**
```
PENDIENTES.md (2100 líneas)
- 90 tareas activas
- Vista limpia

ARCHIVADOS.md (500 líneas)
- 15 tareas archivadas
- Organizadas por fecha
- Búsqueda fácil
```

---

## Próximos Pasos

### Automatización
- [ ] Cron job diario para archivado automático
- [ ] Congreso ejecuta archivado sin supervisión

### Búsqueda en Archivados
- [ ] `/search_archived <keyword>`
- [ ] Full-text search en ARCHIVADOS.md

### Reportes
- [ ] Velocidad de completado (tareas/día)
- [ ] Tiempo promedio en estado completado

---

**Última actualización:** 2025-11-21  
**Versión:** 1.0.0
