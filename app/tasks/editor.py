"""
Editor de tareas - Permite split/merge/edit de tareas en PENDIENTES.md
"""
import re
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
from .parser import TaskParser, ParsedTask

class TaskEditor:
    """Editor para modificar tareas en PENDIENTES.md"""
    
    def __init__(self, pendientes_file: Path):
        self.file = pendientes_file
        self.parser = TaskParser(pendientes_file)
    
    def split_task(self, task_id: str, subtask_titles: List[str], 
                   subtask_descriptions: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Divide una tarea en múltiples subtareas
        
        Args:
            task_id: ID temporal (A1) o hash de la tarea a dividir
            subtask_titles: Lista de títulos para las nuevas subtareas
            subtask_descriptions: Lista opcional de descripciones (si None, usa "")
            
        Returns:
            (success, message)
        """
        # Leer contenido actual
        content = self.file.read_text(encoding='utf-8')
        
        # Encontrar la tarea
        task = self._find_task_in_content(content, task_id)
        if not task:
            return False, f"❌ Tarea no encontrada: {task_id}"
        
        # Validar
        if len(subtask_titles) < 2:
            return False, "❌ Debes especificar al menos 2 subtareas"
        
        if subtask_descriptions is None:
            subtask_descriptions = [""] * len(subtask_titles)
        elif len(subtask_descriptions) != len(subtask_titles):
            return False, "❌ Número de descripciones no coincide con títulos"
        
        # Construir nuevas subtareas
        new_content = self._build_split_content(
            task, 
            subtask_titles, 
            subtask_descriptions
        )
        
        # Reemplazar en el archivo
        updated_content = self._replace_task_content(content, task, new_content)
        
        # Guardar
        self.file.write_text(updated_content, encoding='utf-8')
        
        # Git commit
        self._git_commit(f"Split task: {task['title'][:50]}")
        
        return True, f"✅ Tarea dividida en {len(subtask_titles)} subtareas"
    
    def merge_tasks(self, task_ids: List[str], new_title: str, 
                    new_description: str) -> Tuple[bool, str]:
        """
        Fusiona múltiples tareas en una sola
        
        Args:
            task_ids: Lista de IDs temporales o hash de tareas a fusionar
            new_title: Título de la tarea resultante
            new_description: Descripción de la tarea resultante
            
        Returns:
            (success, message)
        """
        # Validar
        if len(task_ids) < 2:
            return False, "❌ Debes especificar al menos 2 tareas"
        
        # Leer contenido
        content = self.file.read_text(encoding='utf-8')
        
        # Encontrar todas las tareas
        tasks = []
        for tid in task_ids:
            task = self._find_task_in_content(content, tid)
            if task:
                tasks.append(task)
        
        if len(tasks) < len(task_ids):
            return False, f"❌ Solo se encontraron {len(tasks)} de {len(task_ids)} tareas"
        
        # Construir nueva tarea fusionada
        merged_task = self._build_merged_content(
            tasks,
            new_title,
            new_description
        )
        
        # Reemplazar primera tarea con la fusionada
        updated_content = self._replace_task_content(content, tasks[0], merged_task)
        
        # Eliminar las demás tareas
        for task in tasks[1:]:
            updated_content = self._remove_task_content(updated_content, task)
        
        # Guardar
        self.file.write_text(updated_content, encoding='utf-8')
        
        # Git commit
        self._git_commit(f"Merge {len(tasks)} tasks into: {new_title[:50]}")
        
        return True, f"✅ {len(tasks)} tareas fusionadas en una"
    
    def _find_task_in_content(self, content: str, task_id: str) -> Optional[dict]:
        """
        Encuentra una tarea en el contenido del archivo
        
        Returns:
            dict con 'title', 'content', 'start_pos', 'end_pos', 'level'
        """
        # Si es ID temporal (A1), convertir a tarea real
        from .processor import TaskProcessor
        processor = TaskProcessor()  # Sin argumentos
        
        if len(task_id) == 2 and task_id[0].isalpha() and task_id[1].isdigit():
            parsed_task = processor.get_task_by_display_id(task_id)
        else:
            parsed_task = processor.get_task_by_id(task_id)
        
        if not parsed_task:
            return None
        
        # Buscar en contenido por título y contexto
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # Detectar header markdown
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match and parsed_task.title in match.group(2):
                level = len(match.group(1))
                title = match.group(2).strip()
                
                # Encontrar fin de la sección
                end_line = self._find_section_end(lines, i, level)
                
                return {
                    'title': title,
                    'content': '\n'.join(lines[i:end_line]),
                    'start_line': i,
                    'end_line': end_line,
                    'level': level
                }
        
        return None
    
    def _find_section_end(self, lines: List[str], start: int, level: int) -> int:
        """Encuentra el final de una sección markdown"""
        for i in range(start + 1, len(lines)):
            match = re.match(r'^(#{1,6})\s+', lines[i])
            if match and len(match.group(1)) <= level:
                return i
        return len(lines)
    
    def _build_split_content(self, task: dict, titles: List[str], 
                            descriptions: List[str]) -> str:
        """Construye contenido markdown para tareas divididas"""
        level = task['level']
        sublevel = level + 1
        header_prefix = '#' * sublevel
        
        # Header principal (original marcado como DIVIDIDA)
        result = f"{'#' * level} {task['title']} [DIVIDIDA]\n\n"
        result += "**Nota:** Esta tarea fue dividida en subtareas:\n\n"
        
        # Subtareas
        for title, desc in zip(titles, descriptions):
            result += f"{header_prefix} {title}\n\n"
            
            if desc:
                result += f"{desc}\n\n"
            
            result += f"**Estado:** PENDIENTE\n"
            result += f"**Fecha creación:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        return result
    
    def _build_merged_content(self, tasks: List[dict], title: str, 
                             description: str) -> str:
        """Construye contenido markdown para tarea fusionada"""
        level = tasks[0]['level']
        header = '#' * level
        
        result = f"{header} {title}\n\n"
        result += f"{description}\n\n"
        result += f"**Estado:** PENDIENTE\n"
        result += f"**Fecha fusión:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
        result += "**Tareas originales fusionadas:**\n"
        
        for task in tasks:
            result += f"- {task['title']}\n"
        
        result += "\n"
        
        return result
    
    def _replace_task_content(self, content: str, task: dict, 
                             new_content: str) -> str:
        """Reemplaza contenido de una tarea en el archivo"""
        lines = content.split('\n')
        
        # Reemplazar líneas
        new_lines = (
            lines[:task['start_line']] + 
            new_content.split('\n') + 
            lines[task['end_line']:]
        )
        
        return '\n'.join(new_lines)
    
    def _remove_task_content(self, content: str, task: dict) -> str:
        """Elimina una tarea del contenido"""
        lines = content.split('\n')
        
        # Eliminar líneas de la tarea
        new_lines = lines[:task['start_line']] + lines[task['end_line']:]
        
        return '\n'.join(new_lines)
    
    def _git_commit(self, message: str):
        """Crea commit de git con los cambios"""
        import subprocess
        
        try:
            # git add PENDIENTES.md
            subprocess.run(
                ['git', 'add', str(self.file)],
                cwd=self.file.parent,
                capture_output=True,
                check=True
            )
            
            # git commit
            subprocess.run(
                ['git', 'commit', '-m', f"[TaskEditor] {message}"],
                cwd=self.file.parent,
                capture_output=True,
                check=True
            )
            
        except subprocess.CalledProcessError as e:
            # No fallar si git falla (puede no estar inicializado)
            pass
