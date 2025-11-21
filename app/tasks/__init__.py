"""
Task Management System for D8
Allows Congress to understand and process pending tasks from PENDIENTES.md
"""

from app.tasks.parser import TaskParser, ParsedTask
from app.tasks.processor import TaskProcessor

__all__ = [
    'TaskParser',
    'ParsedTask',
    'TaskProcessor'
]
