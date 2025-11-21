"""
NLP Task Processor - Procesamiento de lenguaje natural para edición de tareas
Usa LLM para interpretar intenciones de usuario y generar sugerencias inteligentes
"""
import json
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from lib.llm import GroqClient
from .parser import TaskParser, ParsedTask
from .processor import TaskProcessor
from .editor import TaskEditor


class NLPTaskProcessor:
    """Procesa comandos en lenguaje natural para edición de tareas"""
    
    # Intenciones soportadas
    INTENTS = [
        "split_task",      # Dividir tarea
        "merge_tasks",     # Fusionar tareas
        "reorder_tasks",   # Reorganizar prioridades
        "group_similar",   # Agrupar tareas similares
        "detail_task",     # Ver detalles de tarea
        "suggest_subtasks",# Sugerir subtareas
        "unknown"          # Intención no reconocida
    ]
    
    def __init__(self, groq_api_key: str):
        """
        Args:
            groq_api_key: API key de Groq para LLM
        """
        self.llm = GroqClient(
            api_key=groq_api_key,
            model="llama-3.3-70b-versatile"  # Modelo más capaz
        )
        self.processor = TaskProcessor()
        self.parser = TaskParser()
        
        pendientes_file = Path(__file__).parents[2] / "PENDIENTES.md"
        self.editor = TaskEditor(pendientes_file)
    
    def process_natural_command(self, user_input: str, 
                               task_context: Optional[List[ParsedTask]] = None) -> Dict:
        """
        Procesa comando en lenguaje natural
        
        Args:
            user_input: Texto del usuario (ej: "divide la tarea A1 en 3 partes")
            task_context: Lista de tareas para contexto (opcional)
            
        Returns:
            {
                "intent": str,           # Intención detectada
                "confidence": float,     # Confianza (0-1)
                "parameters": dict,      # Parámetros extraídos
                "suggestion": str,       # Sugerencia para el usuario
                "action": dict,          # Acción a ejecutar
                "requires_confirmation": bool
            }
        """
        # Detectar intención
        intent_result = self._detect_intent(user_input, task_context)
        
        if intent_result["intent"] == "unknown":
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "error": "No pude entender qué quieres hacer. Intenta reformular.",
                "suggestions": [
                    "Divide la tarea A1",
                    "Fusiona las tareas A1 y A2",
                    "Muéstrame los detalles de A3"
                ]
            }
        
        # Procesar según intención
        intent = intent_result["intent"]
        
        if intent == "split_task":
            return self._process_split_intent(user_input, intent_result)
        elif intent == "merge_tasks":
            return self._process_merge_intent(user_input, intent_result)
        elif intent == "detail_task":
            return self._process_detail_intent(user_input, intent_result)
        elif intent == "suggest_subtasks":
            return self._process_suggest_subtasks_intent(user_input, intent_result)
        elif intent == "group_similar":
            return self._process_group_similar_intent(user_input, intent_result)
        else:
            return {
                "intent": intent,
                "confidence": intent_result["confidence"],
                "error": f"Intención '{intent}' aún no implementada",
                "suggestion": "Prueba con dividir o fusionar tareas"
            }
    
    def _detect_intent(self, user_input: str, 
                      task_context: Optional[List[ParsedTask]] = None) -> Dict:
        """Detecta intención del usuario usando LLM"""
        
        # Preparar contexto de tareas
        context_str = ""
        if task_context:
            context_str = "\n".join([
                f"- {task.task_id}: {task.title}"
                for task in task_context[:10]
            ])
        
        prompt = f"""Analiza la siguiente solicitud del usuario y determina su intención.

SOLICITUD DEL USUARIO:
"{user_input}"

TAREAS DISPONIBLES:
{context_str if context_str else "(No hay contexto de tareas)"}

INTENCIONES POSIBLES:
1. split_task - Usuario quiere dividir una tarea en subtareas
2. merge_tasks - Usuario quiere fusionar varias tareas
3. detail_task - Usuario quiere ver detalles de una tarea
4. suggest_subtasks - Usuario pide sugerencias de cómo dividir
5. group_similar - Usuario quiere agrupar tareas similares
6. reorder_tasks - Usuario quiere cambiar prioridades
7. unknown - No está claro qué quiere hacer

Responde SOLO con un JSON con este formato:
{{
    "intent": "nombre_intencion",
    "confidence": 0.95,
    "extracted_task_ids": ["A1", "A2"],
    "extracted_params": {{
        "num_subtasks": 3,
        "keywords": ["api", "frontend"]
    }},
    "reasoning": "El usuario menciona 'divide' y 'A1', indica split_task"
}}"""

        try:
            response = self.llm.chat([
                {"role": "system", "content": "Eres un asistente experto en análisis de intenciones. Respondes SOLO con JSON válido."},
                {"role": "user", "content": prompt}
            ], json_mode=True)
            
            # response["content"] ya es un dict parseado cuando json_mode=True
            content = response.get("content", {})
            
            if isinstance(content, dict):
                return content
            else:
                # Fallback: parsear manualmente
                json_match = re.search(r'\{.*\}', str(content), re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return result
                else:
                    return {"intent": "unknown", "confidence": 0.0}
                
        except Exception as e:
            print(f"Error detectando intención: {e}")
            return {"intent": "unknown", "confidence": 0.0, "error": str(e)}
    
    def _process_split_intent(self, user_input: str, intent_result: Dict) -> Dict:
        """Procesa intención de dividir tarea"""
        
        # Extraer task_id
        task_ids = intent_result.get("extracted_task_ids", [])
        if not task_ids:
            return {
                "intent": "split_task",
                "error": "No pude identificar qué tarea quieres dividir",
                "suggestion": "Especifica el ID de la tarea (ej: 'divide la tarea A1')"
            }
        
        task_id = task_ids[0]
        
        # Obtener tarea
        task = self.processor.get_task_by_id(task_id)
        if not task:
            return {
                "intent": "split_task",
                "error": f"No encontré la tarea {task_id}",
                "suggestion": "Usa /tasks para ver IDs disponibles"
            }
        
        # Generar sugerencias de subtareas usando LLM
        num_subtasks = intent_result.get("extracted_params", {}).get("num_subtasks", 3)
        subtask_suggestions = self._generate_subtask_suggestions(task, num_subtasks)
        
        return {
            "intent": "split_task",
            "confidence": intent_result.get("confidence", 0.8),
            "task_id": task_id,
            "task_title": task.title,
            "suggested_subtasks": subtask_suggestions,
            "requires_confirmation": True,
            "action": {
                "type": "split",
                "task_id": task_id,
                "subtasks": subtask_suggestions
            },
            "message": f"💡 **Sugerencia para dividir: {task.title}**\n\n" +
                      "Subtareas propuestas:\n" +
                      "\n".join(f"{i+1}. {st['title']}" for i, st in enumerate(subtask_suggestions)) +
                      "\n\n¿Confirmar división?"
        }
    
    def _process_merge_intent(self, user_input: str, intent_result: Dict) -> Dict:
        """Procesa intención de fusionar tareas"""
        
        task_ids = intent_result.get("extracted_task_ids", [])
        if len(task_ids) < 2:
            return {
                "intent": "merge_tasks",
                "error": "Necesito al menos 2 tareas para fusionar",
                "suggestion": "Especifica los IDs (ej: 'fusiona A1 y A2')"
            }
        
        # Obtener tareas
        tasks = []
        for tid in task_ids:
            task = self.processor.get_task_by_id(tid)
            if task:
                tasks.append(task)
        
        if len(tasks) < 2:
            return {
                "intent": "merge_tasks",
                "error": f"Solo encontré {len(tasks)} de {len(task_ids)} tareas",
                "suggestion": "Verifica los IDs con /tasks"
            }
        
        # Generar título y descripción fusionada usando LLM
        merged_suggestion = self._generate_merged_task(tasks)
        
        return {
            "intent": "merge_tasks",
            "confidence": intent_result.get("confidence", 0.8),
            "task_ids": task_ids,
            "original_tasks": [{"id": t.task_id, "title": t.title} for t in tasks],
            "suggested_merge": merged_suggestion,
            "requires_confirmation": True,
            "action": {
                "type": "merge",
                "task_ids": task_ids,
                "new_title": merged_suggestion["title"],
                "new_description": merged_suggestion["description"]
            },
            "message": f"💡 **Sugerencia para fusionar {len(tasks)} tareas**\n\n" +
                      f"**Nuevo título:** {merged_suggestion['title']}\n\n" +
                      f"**Descripción:**\n{merged_suggestion['description'][:200]}...\n\n" +
                      "¿Confirmar fusión?"
        }
    
    def _process_detail_intent(self, user_input: str, intent_result: Dict) -> Dict:
        """Procesa intención de ver detalles"""
        
        task_ids = intent_result.get("extracted_task_ids", [])
        if not task_ids:
            return {
                "intent": "detail_task",
                "error": "No especificaste qué tarea ver",
                "suggestion": "Usa /details A1"
            }
        
        task_id = task_ids[0]
        details = self.processor.get_task_details_for_telegram(task_id)
        
        return {
            "intent": "detail_task",
            "confidence": 1.0,
            "task_id": task_id,
            "requires_confirmation": False,
            "message": details
        }
    
    def _process_suggest_subtasks_intent(self, user_input: str, 
                                        intent_result: Dict) -> Dict:
        """Procesa solicitud de sugerencias de subtareas"""
        
        task_ids = intent_result.get("extracted_task_ids", [])
        if not task_ids:
            return {
                "intent": "suggest_subtasks",
                "error": "Especifica para qué tarea quieres sugerencias",
                "suggestion": "Ej: 'sugiere subtareas para A1'"
            }
        
        task_id = task_ids[0]
        task = self.processor.get_task_by_id(task_id)
        
        if not task:
            return {
                "intent": "suggest_subtasks",
                "error": f"No encontré la tarea {task_id}"
            }
        
        suggestions = self._generate_subtask_suggestions(task, num_subtasks=5)
        
        return {
            "intent": "suggest_subtasks",
            "confidence": intent_result.get("confidence", 0.8),
            "task_id": task_id,
            "task_title": task.title,
            "suggestions": suggestions,
            "requires_confirmation": False,
            "message": f"💡 **Sugerencias de subtareas para: {task.title}**\n\n" +
                      "\n".join(f"{i+1}. {s['title']}\n   _{s['description']}_" 
                               for i, s in enumerate(suggestions))
        }
    
    def _process_group_similar_intent(self, user_input: str, 
                                     intent_result: Dict) -> Dict:
        """Procesa intención de agrupar tareas similares"""
        
        # Obtener todas las tareas
        all_tasks = self.processor.list_pending_tasks(max_tasks=50)
        
        # Agrupar por similitud usando LLM
        groups = self._group_similar_tasks(all_tasks)
        
        return {
            "intent": "group_similar",
            "confidence": intent_result.get("confidence", 0.7),
            "groups": groups,
            "requires_confirmation": False,
            "message": "📊 **Tareas agrupadas por similitud**\n\n" +
                      "\n\n".join(
                          f"**Grupo: {g['category']}**\n" +
                          "\n".join(f"- {t['id']}: {t['title'][:50]}" 
                                   for t in g['tasks'][:5])
                          for g in groups[:3]
                      )
        }
    
    def _generate_subtask_suggestions(self, task: ParsedTask, 
                                     num_subtasks: int = 3) -> List[Dict]:
        """Genera sugerencias inteligentes de subtareas usando LLM"""
        
        prompt = f"""Analiza esta tarea y sugiere {num_subtasks} subtareas lógicas.

TAREA:
Título: {task.title}
Descripción: {task.description[:500]}
Prioridad: {task.priority}/5
Archivos mencionados: {', '.join(task.files_mentioned[:5])}

INSTRUCCIONES:
- Divide la tarea en pasos lógicos y secuenciales
- Cada subtarea debe ser específica y accionable
- Incluye estimación de horas (0.5 - 8h)
- Mantén el nivel técnico apropiado

Responde SOLO con JSON:
{{
    "subtasks": [
        {{
            "title": "Setup inicial del proyecto",
            "description": "Configurar estructura de directorios y dependencias",
            "estimated_hours": 2
        }},
        ...
    ]
}}"""

        try:
            response = self.llm.chat([
                {"role": "system", "content": "Eres un experto en gestión de proyectos. Respondes SOLO con JSON."},
                {"role": "user", "content": prompt}
            ], json_mode=True)
            
            content = response.get("content", {})
            
            if isinstance(content, dict):
                return content.get("subtasks", [])
            else:
                # Fallback manual
                json_match = re.search(r'\{.*\}', str(content), re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return result.get("subtasks", [])
                else:
                    return self._generate_generic_subtasks(task, num_subtasks)
                
        except Exception as e:
            print(f"Error generando subtareas: {e}")
            return self._generate_generic_subtasks(task, num_subtasks)
    
    def _generate_generic_subtasks(self, task: ParsedTask, num: int) -> List[Dict]:
        """Genera subtareas genéricas como fallback"""
        return [
            {
                "title": f"{task.title} - Parte {i+1}",
                "description": f"Subtarea {i+1} de {num}",
                "estimated_hours": 2
            }
            for i in range(num)
        ]
    
    def _generate_merged_task(self, tasks: List[ParsedTask]) -> Dict:
        """Genera título y descripción fusionada usando LLM"""
        
        tasks_summary = "\n\n".join([
            f"TAREA {i+1}:\n"
            f"Título: {t.title}\n"
            f"Descripción: {t.description[:300]}"
            for i, t in enumerate(tasks)
        ])
        
        prompt = f"""Fusiona estas {len(tasks)} tareas en una sola tarea coherente.

{tasks_summary}

INSTRUCCIONES:
- Crea un título que abarque todas las tareas
- Escribe una descripción que incluya los elementos clave de cada tarea
- Mantén el contexto técnico
- Sé conciso pero completo

Responde SOLO con JSON:
{{
    "title": "Título unificado claro y específico",
    "description": "Descripción completa que integra todos los aspectos..."
}}"""

        try:
            response = self.llm.chat([
                {"role": "system", "content": "Eres un experto en gestión de proyectos. Respondes SOLO con JSON."},
                {"role": "user", "content": prompt}
            ], json_mode=True)
            
            content = response.get("content", {})
            
            if isinstance(content, dict):
                return content
            else:
                # Fallback manual
                json_match = re.search(r'\{.*\}', str(content), re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return self._generate_generic_merge(tasks)
                
        except Exception as e:
            print(f"Error generando merge: {e}")
            return self._generate_generic_merge(tasks)
    
    def _generate_generic_merge(self, tasks: List[ParsedTask]) -> Dict:
        """Genera merge genérico como fallback"""
        titles = " + ".join(t.title[:30] for t in tasks)
        descriptions = "\n\n".join(f"- {t.title}\n{t.description[:100]}" for t in tasks)
        
        return {
            "title": f"Tarea combinada: {titles}",
            "description": f"Esta tarea fusiona {len(tasks)} tareas:\n\n{descriptions}"
        }
    
    def _group_similar_tasks(self, tasks: List[ParsedTask]) -> List[Dict]:
        """Agrupa tareas similares por categoría"""
        
        # Simplificado: agrupar por palabras clave comunes
        groups = {}
        
        for task in tasks:
            # Buscar palabras clave
            keywords = self._extract_keywords(task.title + " " + task.description)
            
            for keyword in keywords:
                if keyword not in groups:
                    groups[keyword] = []
                groups[keyword].append({
                    "id": task.task_id,
                    "title": task.title
                })
        
        # Ordenar por tamaño de grupo
        sorted_groups = sorted(
            [{"category": k, "tasks": v} for k, v in groups.items()],
            key=lambda x: len(x["tasks"]),
            reverse=True
        )
        
        return sorted_groups[:5]  # Top 5 grupos
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrae palabras clave de texto"""
        common_words = {
            "el", "la", "los", "las", "un", "una", "de", "del", "en", "con",
            "por", "para", "que", "como", "es", "son", "está", "están",
            "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or"
        }
        
        words = re.findall(r'\b[a-záéíóúñ]{4,}\b', text.lower())
        keywords = [w for w in words if w not in common_words]
        
        # Contar frecuencias
        from collections import Counter
        counter = Counter(keywords)
        
        return [word for word, count in counter.most_common(3)]
    
    def execute_action(self, action: Dict) -> Tuple[bool, str]:
        """
        Ejecuta una acción confirmada por el usuario
        
        Args:
            action: Dict con tipo de acción y parámetros
            
        Returns:
            (success, message)
        """
        action_type = action.get("type")
        
        if action_type == "split":
            task_id = action["task_id"]
            subtasks = action["subtasks"]
            
            subtask_titles = [st["title"] for st in subtasks]
            subtask_descs = [st.get("description", "") for st in subtasks]
            
            return self.editor.split_task(task_id, subtask_titles, subtask_descs)
            
        elif action_type == "merge":
            task_ids = action["task_ids"]
            new_title = action["new_title"]
            new_desc = action["new_description"]
            
            return self.editor.merge_tasks(task_ids, new_title, new_desc)
            
        else:
            return False, f"❌ Tipo de acción desconocido: {action_type}"
