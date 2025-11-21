"""
Task Parser - Extrae tareas estructuradas desde PENDIENTES.md
"""

import re
import hashlib
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ParsedTask:
    """Tarea extraída y estructurada"""
    task_id: str                        # ID único de 3 chars (ej: A1B, X3Z)
    title: str                          # Título de la sección
    description: str                    # Contenido completo
    priority: int                       # 1-5 (5=CRÍTICA)
    status: str                         # PENDIENTE, EN_PROCESO, COMPLETADO
    estimated_hours: Optional[int] = None
    files_mentioned: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    assignable: bool = True
    created_date: Optional[str] = None
    section_level: int = 2              # Nivel de header (## = 2)
    raw_markdown: str = ""
    line_start: int = 0                 # Línea de inicio en PENDIENTES.md
    line_end: int = 0                   # Línea de fin en PENDIENTES.md
    
    def to_dict(self) -> Dict:
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description[:500] + '...' if len(self.description) > 500 else self.description,
            'priority': self.priority,
            'status': self.status,
            'estimated_hours': self.estimated_hours,
            'files_mentioned': self.files_mentioned,
            'assignable': self.assignable,
            'created_date': self.created_date
        }
    
    def to_telegram_summary(self) -> str:
        """Formato para Telegram"""
        priority_emoji = {
            5: "🔥",
            4: "🔴",
            3: "🟡",
            2: "🟢",
            1: "⚪"
        }.get(self.priority, "📋")
        
        status_emoji = {
            "PENDIENTE": "⏳",
            "EN_PROCESO": "⚙️",
            "COMPLETADO": "✅"
        }.get(self.status, "❓")
        
        summary = f"{priority_emoji} {status_emoji} **{self.title}**\n"
        summary += f"ID: `{self.task_id}`\n"
        
        if self.estimated_hours:
            summary += f"⏱️ ~{self.estimated_hours}h\n"
        
        # Preview de descripción (primeras 100 chars)
        desc_preview = self.description[:100].replace('\n', ' ').strip()
        if len(self.description) > 100:
            desc_preview += "..."
        summary += f"📝 {desc_preview}\n"
        
        return summary


class TaskParser:
    """
    Parser inteligente de PENDIENTES.md
    
    Extrae:
    - Títulos y descripciones
    - Prioridades (🔥 CRÍTICA, 🔴 ALTA, etc.)
    - Estados (⏳ PENDIENTE, ✅ COMPLETADO)
    - Estimaciones (4-6 horas, 2-3 días)
    - Referencias a archivos
    - Dependencias entre tareas
    """
    
    def __init__(self, pendientes_path: Optional[Path] = None):
        self.pendientes_path = pendientes_path or Path("PENDIENTES.md")
        
        # Patterns para detectar metadata
        self.priority_patterns = {
            5: [r'🔥\s*CRÍTICA', r'CRÍTICA', r'CRITICAL', r'URGENT'],
            4: [r'🔴\s*ALTA', r'ALTA', r'HIGH'],
            3: [r'🟡\s*MEDIA', r'MEDIA', r'MEDIUM'],
            2: [r'🟢\s*BAJA', r'BAJA', r'LOW'],
            1: [r'⚪\s*OPCIONAL', r'OPCIONAL', r'OPTIONAL']
        }
        
        self.status_patterns = {
            'PENDIENTE': [r'⏳\s*PENDIENTE', r'PENDIENTE', r'TODO', r'PENDING'],
            'EN_PROCESO': [r'⚙️\s*EN\s*PROCESO', r'EN_PROCESO', r'IN_PROGRESS'],
            'COMPLETADO': [r'✅\s*COMPLETADO', r'COMPLETADO', r'DONE']
        }
    
    def parse_file(self) -> List[ParsedTask]:
        """
        Parsea PENDIENTES.md completo
        
        Returns:
            Lista de ParsedTask ordenadas por prioridad
        """
        if not self.pendientes_path.exists():
            logger.error(f"Archivo no encontrado: {self.pendientes_path}")
            return []
        
        content = self.pendientes_path.read_text(encoding='utf-8')
        tasks = self._extract_tasks(content)
        
        logger.info(f"📋 Parseadas {len(tasks)} tareas desde {self.pendientes_path}")
        return sorted(tasks, key=lambda t: (-t.priority, t.title))
    
    def _extract_tasks(self, content: str) -> List[ParsedTask]:
        """Extrae todas las secciones como tareas potenciales"""
        tasks = []
        lines = content.split('\n')
        
        current_section = None
        current_content = []
        current_level = 0
        current_line_start = 0
        
        for line_num, line in enumerate(lines, 1):
            # Detectar headers (## Título)
            header_match = re.match(r'^(#{2,})\s+(.+)$', line)
            
            if header_match:
                # Guardar sección anterior si existe
                if current_section:
                    task = self._parse_section(
                        current_section,
                        '\n'.join(current_content),
                        current_level,
                        current_line_start,
                        line_num - 1
                    )
                    if task:
                        tasks.append(task)
                
                # Iniciar nueva sección
                current_level = len(header_match.group(1))
                current_section = header_match.group(2).strip()
                current_content = []
                current_line_start = line_num
            else:
                if current_section:
                    current_content.append(line)
        
        # Última sección
        if current_section:
            task = self._parse_section(
                current_section,
                '\n'.join(current_content),
                current_level,
                current_line_start,
                len(lines)
            )
            if task:
                tasks.append(task)
        
        return tasks
    
    def _parse_section(self, title: str, content: str, level: int, 
                      line_start: int = 0, line_end: int = 0) -> Optional[ParsedTask]:
        """Parsea una sección individual"""
        
        # Ignorar secciones que claramente no son tareas
        ignore_patterns = [
            r'^📋\s+PENDIENTES',
            r'^Última\s+actualización',
            r'^Estado\s+actual',
            r'^Tags$',
            r'^Referencias$',
            r'^Notas$'
        ]
        
        for pattern in ignore_patterns:
            if re.match(pattern, title, re.IGNORECASE):
                return None
        
        # Detectar prioridad
        priority = self._extract_priority(title, content)
        
        # Detectar estado
        status = self._extract_status(title, content)
        
        # Solo parseamos PENDIENTES o EN_PROCESO
        if status == 'COMPLETADO':
            return None
        
        # Generar ID único
        task_id = self._generate_task_id(title, content)
        
        # Extraer estimación
        estimated_hours = self._extract_estimation(content)
        
        # Extraer archivos mencionados
        files = self._extract_files(content)
        
        # Detectar fecha de creación
        created_date = self._extract_date(content)
        
        return ParsedTask(
            task_id=task_id,
            title=title,
            description=content.strip(),
            priority=priority,
            status=status,
            estimated_hours=estimated_hours,
            files_mentioned=files,
            created_date=created_date,
            section_level=level,
            raw_markdown=f"{'#' * level} {title}\n{content}",
            line_start=line_start,
            line_end=line_end
        )
    
    def _extract_priority(self, title: str, content: str) -> int:
        """Detecta prioridad de la tarea"""
        text = f"{title}\n{content}"
        
        for priority, patterns in self.priority_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return priority
        
        return 3  # Default: MEDIA
    
    def _extract_status(self, title: str, content: str) -> str:
        """Detecta estado de la tarea"""
        text = f"{title}\n{content}"
        
        for status, patterns in self.status_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return status
        
        return 'PENDIENTE'  # Default
    
    def _extract_estimation(self, content: str) -> Optional[int]:
        """Extrae estimación en horas"""
        
        # Patrones: "4-6 horas", "2-3 días", "Estimación: 8h"
        patterns = [
            r'(\d+)-(\d+)\s*horas?',
            r'(\d+)-(\d+)\s*días?',
            r'(\d+)h',
            r'Estimación:\s*(\d+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if 'día' in pattern:
                    # Convertir días a horas (8h por día)
                    avg_days = (int(match.group(1)) + int(match.group(2))) / 2
                    return int(avg_days * 8)
                elif '-' in pattern:
                    # Promedio del rango
                    return int((int(match.group(1)) + int(match.group(2))) / 2)
                else:
                    return int(match.group(1))
        
        return None
    
    def _extract_files(self, content: str) -> List[str]:
        """Extrae referencias a archivos"""
        files = []
        
        # Patrones para archivos
        patterns = [
            r'`([a-zA-Z0-9_/\\\.]+\.[a-zA-Z]{2,5})`',  # `app/tasks/parser.py`
            r'\*\*Archivo:\*\*\s+`([^`]+)`',            # **Archivo:** `...`
            r'Ubicación:\s+`([^`]+)`',                   # Ubicación: `...`
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            files.extend(matches)
        
        return list(set(files))  # Remover duplicados
    
    def _extract_date(self, content: str) -> Optional[str]:
        """Extrae fecha de creación"""
        patterns = [
            r'Fecha\s+de\s+creación:\s*(\d{4}-\d{2}-\d{2})',
            r'(\d{4}-\d{2}-\d{2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
        
        return None
    
    def _generate_task_id(self, title: str, content: str) -> str:
        """Genera ID único alfanumérico de 3 caracteres (A1B, X3Z, etc.)"""
        # Hash del título + primeros 200 chars del contenido
        text = f"{title}{content[:200]}"
        hash_full = hashlib.sha256(text.encode()).hexdigest()
        
        # Convertir a base36 (0-9, A-Z) y tomar 3 chars
        # Esto da 46,656 combinaciones posibles (36^3)
        hash_int = int(hash_full[:8], 16)  # Tomar primeros 8 hex chars
        
        # Convertir a base36
        chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result = ""
        for _ in range(3):
            result = chars[hash_int % 36] + result
            hash_int //= 36
        
        return result
    
    def get_tasks_by_status(self, status: str) -> List[ParsedTask]:
        """Filtra tareas por estado"""
        all_tasks = self.parse_file()
        return [t for t in all_tasks if t.status == status]
    
    def get_tasks_by_priority(self, min_priority: int = 3) -> List[ParsedTask]:
        """Filtra tareas por prioridad mínima"""
        all_tasks = self.parse_file()
        return [t for t in all_tasks if t.priority >= min_priority]
    
    def get_assignable_tasks(self) -> List[ParsedTask]:
        """Retorna tareas que pueden asignarse ahora"""
        all_tasks = self.parse_file()
        return [
            t for t in all_tasks
            if t.assignable and t.status == 'PENDIENTE'
        ]
