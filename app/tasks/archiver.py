"""
Task Archiver - Archiva tareas completadas automáticamente
Mueve tareas COMPLETADAS de PENDIENTES.md a ARCHIVADOS.md después de N días
"""
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import shutil


class TaskArchiver:
    """Gestiona el archivado automático de tareas completadas"""
    
    def __init__(self, 
                 pendientes_file: Path = None,
                 archivados_file: Path = None,
                 days_before_archive: int = 2):
        """
        Args:
            pendientes_file: Ruta a PENDIENTES.md
            archivados_file: Ruta a ARCHIVADOS.md
            days_before_archive: Días antes de archivar (default: 2)
        """
        self.pendientes_file = pendientes_file or Path("PENDIENTES.md")
        self.archivados_file = archivados_file or Path("ARCHIVADOS.md")
        self.days_before_archive = days_before_archive
        
    def find_completed_tasks(self, content: str) -> List[Dict]:
        """
        Encuentra tareas completadas en el contenido
        
        Returns:
            Lista de dicts con:
            - title: Título de la tarea
            - content: Contenido completo
            - completed_date: Fecha de completado
            - start_line: Línea de inicio
            - end_line: Línea de fin
            - archivable: Si ya pasaron N días
        """
        lines = content.split('\n')
        tasks = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Buscar headers de secciones
            header_match = re.match(r'^(#{2,6})\s+(.+)$', line)
            
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
                # Buscar si es tarea completada
                section_content = []
                section_start = i
                i += 1
                
                # Leer contenido de la sección
                while i < len(lines):
                    next_line = lines[i]
                    
                    # ¿Fin de sección? (header del mismo o menor nivel)
                    next_header = re.match(r'^(#{2,6})\s+', next_line)
                    if next_header and len(next_header.group(1)) <= level:
                        break
                    
                    section_content.append(next_line)
                    i += 1
                
                section_text = '\n'.join(section_content)
                
                # ¿Es tarea completada?
                if self._is_completed_task(title, section_text):
                    completed_date = self._extract_completion_date(section_text)
                    
                    # Reconstruir contenido completo
                    full_content = line + '\n' + section_text
                    
                    # ¿Es archivable?
                    archivable = False
                    if completed_date:
                        days_since = (datetime.now() - completed_date).days
                        archivable = days_since >= self.days_before_archive
                    
                    tasks.append({
                        'title': title,
                        'content': full_content,
                        'completed_date': completed_date,
                        'start_line': section_start,
                        'end_line': i - 1,
                        'archivable': archivable,
                        'days_since_completion': days_since if completed_date else None
                    })
            else:
                i += 1
        
        return tasks
    
    def _is_completed_task(self, title: str, content: str) -> bool:
        """Detecta si una tarea está completada"""
        
        # Check 1: Título tiene checkmark
        if '✅' in title or 'COMPLETADO' in title.upper():
            return True
        
        # Check 2: Estado en contenido
        status_match = re.search(r'\*\*Estado:\*\*\s*✅|Estado:\s*COMPLETADO', content, re.IGNORECASE)
        if status_match:
            return True
        
        # Check 3: Línea de completado
        if re.search(r'(Completado|Finalizado):\s*\d{4}-\d{2}-\d{2}', content):
            return True
        
        return False
    
    def _extract_completion_date(self, content: str) -> Optional[datetime]:
        """Extrae fecha de completado del contenido"""
        
        # Buscar patrones de fecha (con ** markdown)
        patterns = [
            r'\*\*Completado:\*\*\s*(\d{4}-\d{2}-\d{2})',  # **Completado:** YYYY-MM-DD
            r'Completado:\s*(\d{4}-\d{2}-\d{2})',          # Completado: YYYY-MM-DD
            r'\*\*Finalizado:\*\*\s*(\d{4}-\d{2}-\d{2})',  # **Finalizado:** YYYY-MM-DD
            r'Finalizado:\s*(\d{4}-\d{2}-\d{2})',          # Finalizado: YYYY-MM-DD
            r'Fecha.*completado.*:\s*(\d{4}-\d{2}-\d{2})', # Fecha de completado: YYYY-MM-DD
            r'\((\d{4}-\d{2}-\d{2})\)',                    # (YYYY-MM-DD)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    continue
        
        return None
    
    def archive_tasks(self, dry_run: bool = False) -> Dict:
        """
        Archiva tareas completadas elegibles
        
        Args:
            dry_run: Si True, solo reporta qué se archivaría sin modificar archivos
            
        Returns:
            Dict con estadísticas:
            - total_completed: Total de tareas completadas
            - archivable: Tareas que pueden archivarse
            - archived: Tareas archivadas
            - tasks: Lista de tareas procesadas
        """
        # Leer PENDIENTES.md
        if not self.pendientes_file.exists():
            return {
                'error': f"No se encontró {self.pendientes_file}",
                'total_completed': 0,
                'archivable': 0,
                'archived': 0
            }
        
        content = self.pendientes_file.read_text(encoding='utf-8')
        
        # Encontrar tareas completadas
        completed_tasks = self.find_completed_tasks(content)
        
        # Filtrar archivables
        archivable_tasks = [t for t in completed_tasks if t['archivable']]
        
        result = {
            'total_completed': len(completed_tasks),
            'archivable': len(archivable_tasks),
            'archived': 0,
            'tasks': []
        }
        
        if not archivable_tasks:
            return result
        
        if dry_run:
            result['tasks'] = archivable_tasks
            return result
        
        # Crear backup
        backup_file = self.pendientes_file.with_suffix('.md.bak')
        shutil.copy2(self.pendientes_file, backup_file)
        
        # Archivar tareas
        lines = content.split('\n')
        new_lines = []
        archived_content = []
        
        skip_until = -1
        
        for i, line in enumerate(lines):
            if i < skip_until:
                continue
            
            # ¿Esta línea es inicio de tarea archivable?
            task_to_archive = None
            for task in archivable_tasks:
                if i == task['start_line']:
                    task_to_archive = task
                    break
            
            if task_to_archive:
                # Guardar para archivo
                archived_content.append(task_to_archive['content'])
                archived_content.append('\n---\n')
                
                # Saltar hasta el fin de la tarea
                skip_until = task_to_archive['end_line'] + 1
                
                result['archived'] += 1
                result['tasks'].append(task_to_archive)
            else:
                new_lines.append(line)
        
        # Escribir nuevo PENDIENTES.md
        new_content = '\n'.join(new_lines)
        self.pendientes_file.write_text(new_content, encoding='utf-8')
        
        # Agregar a ARCHIVADOS.md
        if archived_content:
            self._append_to_archive(archived_content)
        
        return result
    
    def _append_to_archive(self, tasks_content: List[str]):
        """Agrega tareas al archivo de archivados"""
        
        # Si no existe, crear con header
        if not self.archivados_file.exists():
            header = f"""# 📦 TAREAS ARCHIVADAS D8

**Tareas completadas que fueron archivadas automáticamente**  
**Período de retención en PENDIENTES.md:** {self.days_before_archive} días

---

"""
            self.archivados_file.write_text(header, encoding='utf-8')
        
        # Agregar timestamp de archivado
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        archive_header = f"\n## Archivado: {timestamp}\n\n"
        
        # Append tareas
        existing = self.archivados_file.read_text(encoding='utf-8')
        new_content = existing + archive_header + '\n'.join(tasks_content)
        
        self.archivados_file.write_text(new_content, encoding='utf-8')
    
    def preview_archivable(self) -> str:
        """
        Genera preview de qué se archivaría
        
        Returns:
            String formateado para mostrar al usuario
        """
        result = self.archive_tasks(dry_run=True)
        
        if result['total_completed'] == 0:
            return "✅ No hay tareas completadas"
        
        message = f"📊 **TAREAS COMPLETADAS**\n\n"
        message += f"Total: {result['total_completed']}\n"
        message += f"Archivables (>{self.days_before_archive} días): {result['archivable']}\n\n"
        
        if result['archivable'] > 0:
            message += "🗄️ **Tareas a archivar:**\n\n"
            
            for task in result['tasks']:
                days = task['days_since_completion']
                date = task['completed_date'].strftime('%Y-%m-%d') if task['completed_date'] else 'N/A'
                
                message += f"• **{task['title']}**\n"
                message += f"  Completado: {date} ({days} días atrás)\n\n"
        else:
            message += "⏳ Ninguna tarea lista para archivar todavía\n"
        
        return message
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas de archivado"""
        
        content = self.pendientes_file.read_text(encoding='utf-8') if self.pendientes_file.exists() else ""
        completed_tasks = self.find_completed_tasks(content)
        
        archivable = [t for t in completed_tasks if t['archivable']]
        not_yet = [t for t in completed_tasks if not t['archivable']]
        
        return {
            'total_completed': len(completed_tasks),
            'archivable_now': len(archivable),
            'waiting_period': len(not_yet),
            'days_threshold': self.days_before_archive,
            'archive_file_exists': self.archivados_file.exists(),
            'tasks_by_days': self._group_by_days(completed_tasks)
        }
    
    def _group_by_days(self, tasks: List[Dict]) -> Dict[int, int]:
        """Agrupa tareas por días desde completado"""
        
        groups = {}
        
        for task in tasks:
            days = task.get('days_since_completion')
            if days is not None:
                groups[days] = groups.get(days, 0) + 1
        
        return groups


def main():
    """CLI para testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Archivador de tareas completadas')
    parser.add_argument('--days', type=int, default=2, help='Días antes de archivar (default: 2)')
    parser.add_argument('--preview', action='store_true', help='Solo mostrar qué se archivaría')
    parser.add_argument('--stats', action='store_true', help='Mostrar estadísticas')
    parser.add_argument('--execute', action='store_true', help='Ejecutar archivado')
    
    args = parser.parse_args()
    
    archiver = TaskArchiver(days_before_archive=args.days)
    
    if args.stats:
        stats = archiver.get_stats()
        print(f"\n📊 ESTADÍSTICAS DE ARCHIVADO\n")
        print(f"Total completadas: {stats['total_completed']}")
        print(f"Archivables ahora: {stats['archivable_now']}")
        print(f"En período de espera: {stats['waiting_period']}")
        print(f"Umbral: {stats['days_threshold']} días\n")
        
        if stats['tasks_by_days']:
            print("Distribución por días:")
            for days in sorted(stats['tasks_by_days'].keys()):
                count = stats['tasks_by_days'][days]
                status = "✅ Archivable" if days >= stats['days_threshold'] else "⏳ Esperando"
                print(f"  {days} días: {count} tareas - {status}")
    
    elif args.preview:
        preview = archiver.preview_archivable()
        print(preview)
    
    elif args.execute:
        print("\n🗄️  Ejecutando archivado...\n")
        result = archiver.archive_tasks(dry_run=False)
        
        print(f"✅ Archivado completado")
        print(f"   Tareas archivadas: {result['archived']}")
        print(f"   Total completadas: {result['total_completed']}")
        print(f"   Backup creado: PENDIENTES.md.bak\n")
        
        if result['archived'] > 0:
            print("📦 Tareas archivadas:")
            for task in result['tasks']:
                print(f"   • {task['title']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
