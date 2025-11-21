"""
Tests para Task Archiver
"""
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from app.tasks.archiver import TaskArchiver


# Generar fechas dinámicas
TODAY = datetime.now().strftime('%Y-%m-%d')
FIVE_DAYS_AGO = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
ONE_DAY_AGO = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# Contenido de prueba con tareas completadas en diferentes fechas
SAMPLE_PENDIENTES = f"""# PENDIENTES D8

## ✅ Tarea Completada Hace 5 Días
**Estado:** ✅ COMPLETADO  
**Completado:** {FIVE_DAYS_AGO}  
**Prioridad:** Alta

Esta tarea fue completada hace 5 días y debe archivarse.

## ✅ Tarea Completada Hace 1 Día
**Estado:** ✅ COMPLETADO  
**Completado:** {ONE_DAY_AGO}  
**Prioridad:** Media

Esta tarea fue completada hace 1 día, NO debe archivarse aún.

## 🔄 Tarea En Progreso
**Estado:** EN_PROGRESO  
**Prioridad:** Alta

Esta tarea no está completada.

## ✅ Tarea Sin Fecha
**Estado:** ✅ COMPLETADO  
**Prioridad:** Baja

Esta tarea no tiene fecha de completado.

## Tarea Normal (sin estado)
**Prioridad:** Media

Esta tarea no tiene marcador de estado.
"""


@pytest.fixture
def temp_files(tmp_path):
    """Crea archivos temporales para testing"""
    pendientes = tmp_path / "PENDIENTES.md"
    archivados = tmp_path / "ARCHIVADOS.md"
    
    pendientes.write_text(SAMPLE_PENDIENTES, encoding='utf-8')
    
    return {
        'pendientes': pendientes,
        'archivados': archivados,
        'tmp_path': tmp_path
    }


def test_find_completed_tasks(temp_files):
    """Test: Encontrar tareas completadas"""
    archiver = TaskArchiver(
        pendientes_file=temp_files['pendientes'],
        archivados_file=temp_files['archivados'],
        days_before_archive=2
    )
    
    content = temp_files['pendientes'].read_text(encoding='utf-8')
    completed = archiver.find_completed_tasks(content)
    
    # Debe encontrar 3 tareas completadas
    assert len(completed) == 3
    
    # Verificar títulos
    titles = [t['title'] for t in completed]
    assert '✅ Tarea Completada Hace 5 Días' in titles
    assert '✅ Tarea Completada Hace 1 Día' in titles
    assert '✅ Tarea Sin Fecha' in titles


def test_archivable_detection(temp_files):
    """Test: Detectar cuáles son archivables"""
    archiver = TaskArchiver(
        pendientes_file=temp_files['pendientes'],
        archivados_file=temp_files['archivados'],
        days_before_archive=2
    )
    
    content = temp_files['pendientes'].read_text(encoding='utf-8')
    completed = archiver.find_completed_tasks(content)
    
    # Solo la de hace 5 días debe ser archivable
    archivable = [t for t in completed if t['archivable']]
    assert len(archivable) == 1
    assert '5 Días' in archivable[0]['title']
    assert archivable[0]['days_since_completion'] >= 2


def test_preview_dry_run(temp_files):
    """Test: Preview sin modificar archivos"""
    archiver = TaskArchiver(
        pendientes_file=temp_files['pendientes'],
        archivados_file=temp_files['archivados'],
        days_before_archive=2
    )
    
    result = archiver.archive_tasks(dry_run=True)
    
    assert result['total_completed'] == 3
    assert result['archivable'] == 1
    assert result['archived'] == 0  # Dry run no archiva
    
    # Archivo original no debe modificarse
    original = temp_files['pendientes'].read_text(encoding='utf-8')
    assert '5 Días' in original


def test_archive_execution(temp_files):
    """Test: Archivado real"""
    archiver = TaskArchiver(
        pendientes_file=temp_files['pendientes'],
        archivados_file=temp_files['archivados'],
        days_before_archive=2
    )
    
    result = archiver.archive_tasks(dry_run=False)
    
    assert result['archived'] == 1
    
    # Verificar PENDIENTES.md (debe haberse removido la tarea)
    new_content = temp_files['pendientes'].read_text(encoding='utf-8')
    assert '5 Días' not in new_content
    assert '1 Día' in new_content  # Esta sigue
    
    # Verificar ARCHIVADOS.md (debe haberse creado)
    assert temp_files['archivados'].exists()
    archived_content = temp_files['archivados'].read_text(encoding='utf-8')
    assert '5 Días' in archived_content
    assert 'TAREAS ARCHIVADAS' in archived_content


def test_backup_creation(temp_files):
    """Test: Backup se crea antes de archivar"""
    archiver = TaskArchiver(
        pendientes_file=temp_files['pendientes'],
        archivados_file=temp_files['archivados'],
        days_before_archive=2
    )
    
    archiver.archive_tasks(dry_run=False)
    
    # Verificar backup
    backup = temp_files['pendientes'].with_suffix('.md.bak')
    assert backup.exists()
    
    # Backup debe tener contenido original
    backup_content = backup.read_text(encoding='utf-8')
    assert '5 Días' in backup_content


def test_stats(temp_files):
    """Test: Estadísticas"""
    archiver = TaskArchiver(
        pendientes_file=temp_files['pendientes'],
        archivados_file=temp_files['archivados'],
        days_before_archive=2
    )
    
    stats = archiver.get_stats()
    
    assert stats['total_completed'] == 3
    assert stats['archivable_now'] == 1
    assert stats['waiting_period'] == 2  # Sin fecha + hace 1 día
    assert stats['days_threshold'] == 2


def test_different_thresholds(temp_files):
    """Test: Diferentes umbrales de días"""
    
    # Umbral de 0 días (archiva todo inmediatamente)
    archiver_0 = TaskArchiver(
        pendientes_file=temp_files['pendientes'],
        archivados_file=temp_files['archivados'],
        days_before_archive=0
    )
    
    result = archiver_0.archive_tasks(dry_run=True)
    assert result['archivable'] == 2  # Ambas con fecha (5 días y 1 día)
    
    # Umbral de 10 días (no archiva nada)
    archiver_10 = TaskArchiver(
        pendientes_file=temp_files['pendientes'],
        archivados_file=temp_files['archivados'],
        days_before_archive=10
    )
    
    result = archiver_10.archive_tasks(dry_run=True)
    assert result['archivable'] == 0


def test_no_pendientes_file():
    """Test: Manejo de archivo inexistente"""
    archiver = TaskArchiver(
        pendientes_file=Path("NOEXISTE.md"),
        archivados_file=Path("ARCH.md"),
        days_before_archive=2
    )
    
    result = archiver.archive_tasks()
    
    assert 'error' in result
    assert result['total_completed'] == 0


def test_preview_message(temp_files):
    """Test: Mensaje de preview"""
    archiver = TaskArchiver(
        pendientes_file=temp_files['pendientes'],
        archivados_file=temp_files['archivados'],
        days_before_archive=2
    )
    
    preview = archiver.preview_archivable()
    
    assert 'TAREAS COMPLETADAS' in preview
    assert 'Total: 3' in preview
    assert 'Archivables' in preview
    assert '5 Días' in preview


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
