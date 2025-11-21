"""
Task Processor - Integra el parser con el Congreso Autónomo
Permite que el Congreso entienda y procese tareas de PENDIENTES.md
"""

import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
from datetime import datetime

from app.tasks.parser import TaskParser, ParsedTask

logger = logging.getLogger(__name__)


class TaskProcessor:
    """
    Procesador de tareas que conecta el parser con el Congreso
    
    Funcionalidades:
    - Listar tareas disponibles
    - Asignar tareas al Congreso
    - Trackear progreso
    - Generar reportes
    """
    
    def __init__(self):
        self.parser = TaskParser()
        self.data_dir = Path.home() / "Documents" / "d8_data" / "tasks"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.assignments_file = self.data_dir / "assignments.json"
        self.completed_file = self.data_dir / "completed.json"
        
        self.assignments = self._load_assignments()
        self.completed = self._load_completed()
    
    def _load_assignments(self) -> Dict[str, Dict]:
        """Cargar tareas asignadas"""
        if self.assignments_file.exists():
            try:
                return json.loads(self.assignments_file.read_text())
            except:
                return {}
        return {}
    
    def _save_assignments(self):
        """Guardar tareas asignadas"""
        self.assignments_file.write_text(json.dumps(self.assignments, indent=2))
    
    def _load_completed(self) -> List[Dict]:
        """Cargar tareas completadas"""
        if self.completed_file.exists():
            try:
                return json.loads(self.completed_file.read_text())
            except:
                return []
        return []
    
    def _save_completed(self):
        """Guardar tareas completadas"""
        self.completed_file.write_text(json.dumps(self.completed, indent=2))
    
    def list_pending_tasks(self, max_tasks: int = 20) -> List[ParsedTask]:
        """
        Lista tareas pendientes ordenadas por prioridad
        
        Args:
            max_tasks: Máximo de tareas a retornar
            
        Returns:
            Lista de ParsedTask ordenadas por prioridad (mayor primero)
        """
        tasks = self.parser.get_assignable_tasks()
        
        # Filtrar tareas ya asignadas
        tasks = [t for t in tasks if t.task_id not in self.assignments]
        
        return tasks[:max_tasks]
    
    def get_task_by_id(self, task_id: str) -> Optional[ParsedTask]:
        """
        Busca tarea específica por ID (soporta IDs temporales A1-Z9 e IDs internos hash)
        
        Args:
            task_id: ID temporal (A1, B5) o ID interno hash
        """
        # Si es formato A1-Z9, usar get_task_by_display_id
        if len(task_id) == 2 and task_id[0].isalpha() and task_id[1].isdigit():
            return self.get_task_by_display_id(task_id)
        
        # Buscar por ID interno hash
        all_tasks = self.parser.parse_file()
        
        for task in all_tasks:
            if task.task_id == task_id:
                return task
        
        return None
    
    def search_tasks(self, query: str) -> List[ParsedTask]:
        """
        Busca tareas por texto en título o descripción
        
        Args:
            query: Texto a buscar (case-insensitive)
            
        Returns:
            Lista de tareas que coinciden
        """
        all_tasks = self.parser.parse_file()
        query_lower = query.lower()
        
        matches = []
        for task in all_tasks:
            if query_lower in task.title.lower() or query_lower in task.description.lower():
                matches.append(task)
        
        return matches
    
    def assign_task(self, task_id: str, assigned_to: str = "Congress") -> bool:
        """
        Asignar tarea a un agente/congreso
        
        Args:
            task_id: ID de la tarea
            assigned_to: Quién la procesa
            
        Returns:
            True si se asignó exitosamente
        """
        task = self.get_task_by_id(task_id)
        
        if not task:
            logger.error(f"Tarea no encontrada: {task_id}")
            return False
        
        if task.task_id in self.assignments:
            logger.warning(f"Tarea ya asignada: {task_id}")
            return False
        
        # Registrar asignación
        self.assignments[task.task_id] = {
            'task_id': task.task_id,
            'title': task.title,
            'assigned_to': assigned_to,
            'assigned_at': datetime.now().isoformat(),
            'status': 'in_progress'
        }
        
        self._save_assignments()
        logger.info(f"✅ Tarea asignada: {task.title} → {assigned_to}")
        
        return True
    
    def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        """
        Marcar tarea como completada
        
        Args:
            task_id: ID de la tarea
            result: Diccionario con resultados (success, message, artifacts, etc.)
            
        Returns:
            True si se completó exitosamente
        """
        if task_id not in self.assignments:
            logger.error(f"Tarea no está asignada: {task_id}")
            return False
        
        assignment = self.assignments[task_id]
        
        # Registrar completitud
        completion = {
            'task_id': task_id,
            'title': assignment['title'],
            'assigned_to': assignment['assigned_to'],
            'assigned_at': assignment['assigned_at'],
            'completed_at': datetime.now().isoformat(),
            'result': result
        }
        
        self.completed.append(completion)
        self._save_completed()
        
        # Remover de asignaciones activas
        del self.assignments[task_id]
        self._save_assignments()
        
        logger.info(f"✅ Tarea completada: {assignment['title']}")
        
        return True
    
    def get_active_assignments(self) -> List[Dict]:
        """Retorna tareas actualmente asignadas"""
        return list(self.assignments.values())
    
    def get_completion_stats(self) -> Dict[str, Any]:
        """Estadísticas de completitud"""
        all_tasks = self.parser.parse_file()
        pending = [t for t in all_tasks if t.status == 'PENDIENTE']
        
        return {
            'total_tasks': len(all_tasks),
            'pending': len(pending),
            'in_progress': len(self.assignments),
            'completed': len(self.completed),
            'completion_rate': len(self.completed) / len(all_tasks) * 100 if all_tasks else 0
        }
    
    def _generate_display_id(self, index: int) -> str:
        """
        Genera ID temporal alfanumérico de 2 dígitos para display
        
        A1, A2, ... A9, B1, B2, ... Z9 (234 posibles IDs)
        
        Args:
            index: Índice de la tarea (0-based)
            
        Returns:
            ID alfanumérico (ej: "A1", "B5", "Z9")
        """
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        letter = letters[index // 9]
        number = (index % 9) + 1
        return f"{letter}{number}"
    
    def get_task_by_display_id(self, display_id: str) -> Optional[ParsedTask]:
        """
        Obtiene tarea por ID temporal de display
        
        Args:
            display_id: ID temporal (ej: "A1", "B5")
            
        Returns:
            ParsedTask si se encuentra
        """
        # Parsear display_id
        if len(display_id) != 2:
            return None
        
        letter = display_id[0].upper()
        try:
            number = int(display_id[1])
        except:
            return None
        
        # Calcular índice
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if letter not in letters or number < 1 or number > 9:
            return None
        
        index = letters.index(letter) * 9 + (number - 1)
        
        # Obtener tarea en ese índice
        tasks = self.list_pending_tasks(max_tasks=300)  # Suficiente para Z9
        
        if index < len(tasks):
            return tasks[index]
        
        return None
    
    def generate_task_list_for_telegram(self, max_tasks: int = 10) -> str:
        """
        Genera lista formateada para Telegram con IDs temporales
        
        Args:
            max_tasks: Máximo de tareas a mostrar
            
        Returns:
            String formateado en Markdown con IDs temporales (A1, A2, etc.)
        """
        tasks = self.list_pending_tasks(max_tasks)
        
        if not tasks:
            return "📭 No hay tareas pendientes disponibles."
        
        message = f"📋 **TAREAS PENDIENTES** (top {len(tasks)})\n\n"
        
        for i, task in enumerate(tasks):
            display_id = self._generate_display_id(i)
            priority_emoji = {
                5: "🔥",
                4: "🔴",
                3: "🟡",
                2: "🟢",
                1: "⚪"
            }.get(task.priority, "📋")
            
            status_emoji = {
                "PENDIENTE": "⏳",
                "EN_PROCESO": "⚙️",
                "COMPLETADO": "✅"
            }.get(task.status, "❓")
            
            message += f"{display_id}. {priority_emoji} {status_emoji} **{task.title}**\n"
            
            if task.estimated_hours:
                message += f"     ⏱️ ~{task.estimated_hours}h\n"
            
            # Preview de descripción
            desc_preview = task.description[:80].replace('\n', ' ').strip()
            if len(task.description) > 80:
                desc_preview += "..."
            message += f"     📝 {desc_preview}\n\n"
        
        message += f"\n💡 *Usa /assign <ID> para asignar* (ej: /assign A1)"
        
        return message
    
    def get_task_details_for_telegram(self, task_id: str) -> str:
        """Genera detalles completos de una tarea para Telegram"""
        task = self.get_task_by_id(task_id)
        
        if not task:
            return f"❌ Tarea no encontrada: {task_id}"
        
        priority_emoji = {
            5: "🔥 CRÍTICA",
            4: "🔴 ALTA",
            3: "🟡 MEDIA",
            2: "🟢 BAJA",
            1: "⚪ OPCIONAL"
        }.get(task.priority, "📋 NORMAL")
        
        message = f"📋 **DETALLES DE TAREA**\n\n"
        message += f"**Título:** {task.title}\n\n"
        message += f"**Prioridad:** {priority_emoji}\n"
        message += f"**Estado:** {task.status}\n"
        message += f"**ID Temporal:** `{task_id}` (válido solo en esta sesión)\n"
        
        if task.estimated_hours:
            message += f"**Estimación:** {task.estimated_hours} horas\n"
        
        if task.files_mentioned:
            message += f"\n**Archivos mencionados:**\n"
            for file in task.files_mentioned[:5]:
                message += f"- `{file}`\n"
        
        # Descripción (limitada)
        desc = task.description[:800]
        if len(task.description) > 800:
            desc += "..."
        
        message += f"\n**Descripción:**\n{desc}\n"
        
        message += f"\n💡 *Usa /assign {task.task_id} para asignar al congreso*"
        
        return message
