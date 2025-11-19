# 🛡️ Mejores Prácticas

> **Recomendaciones probadas para código robusto y mantenible**

---

## 📋 Índice

1. [Validación de Entradas con Schemas](#validacion-schemas)
2. [Logging Estructurado](#logging-estructurado)
3. [Path Handling Cross-Platform](#path-handling)

---

## Validación de Entradas con Schemas {#validacion-schemas}

### Contexto
APIs que reciben datos complejos de clientes o servicios externos.

### Problema
- Datos malformados causan crashes
- Difícil debuggear qué campo falló
- No hay contrato claro de lo que se espera

### Solución

Usar **Pydantic** para validación automática con schemas.

### Ejemplo

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class TaskRequest(BaseModel):
    """Schema para solicitud de tarea"""
    task_type: str = Field(..., description="Tipo de tarea")
    priority: int = Field(1, ge=1, le=5, description="Prioridad 1-5")
    data: dict = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    timeout: Optional[int] = Field(None, gt=0)
    
    @validator('task_type')
    def validate_task_type(cls, v):
        allowed = ['generate', 'analyze', 'optimize']
        if v not in allowed:
            raise ValueError(f'task_type debe ser uno de {allowed}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "task_type": "generate",
                "priority": 3,
                "data": {"prompt": "Escribir un tweet"},
                "tags": ["social", "twitter"]
            }
        }

# Uso en Flask
from flask import request, jsonify

@app.route("/api/tasks", methods=["POST"])
def create_task():
    try:
        # Validación automática
        task = TaskRequest(**request.json)
        
        # Si llega aquí, los datos son válidos
        result = process_task(task)
        return jsonify({"status": "ok", "result": result})
        
    except ValidationError as e:
        # Error detallado de qué falló
        return jsonify({"error": e.errors()}), 400
```

### Resultado

✅ **Seguridad:** Rechaza datos inválidos antes de procesarlos  
✅ **Debugging:** Errores claros y específicos  
✅ **Documentación:** Schema auto-documenta la API  
✅ **Type Safety:** IDE autocomplete y type checking

### Tags
`#validation` `#reliability` `#dx` `#python` `#pydantic`

---

## Logging Estructurado {#logging-estructurado}

### Contexto
Aplicaciones en producción que necesitan debugging rápido y análisis de logs.

### Problema
- Logs en texto plano son difíciles de parsear
- No hay contexto estructurado
- Difícil hacer queries y análisis

### Solución

**JSON logs** con campos estructurados.

### Ejemplo

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Formatter para logs en JSON"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Agregar campos extras si existen
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        # Agregar exception si existe
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Setup
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Uso
logger.info("Usuario creó tarea", extra={
    "user_id": "user123",
    "request_id": "req456",
    "task_type": "generate"
})

# Output:
# {"timestamp": "2025-11-19T10:30:00", "level": "INFO", 
#  "logger": "app", "message": "Usuario creó tarea",
#  "user_id": "user123", "request_id": "req456", 
#  "task_type": "generate"}
```

### Ejemplo de Análisis

```bash
# Filtrar por nivel
cat app.log | jq 'select(.level == "ERROR")'

# Contar errores por módulo
cat app.log | jq -r '.module' | sort | uniq -c

# Encontrar requests lentos
cat app.log | jq 'select(.duration > 5000)'
```

### Resultado

✅ **Parseabilidad:** Logs fáciles de procesar automáticamente  
✅ **Contexto Rico:** Información estructurada en cada log  
✅ **Análisis:** Queries complejas con jq/grep  
✅ **Integración:** Compatible con ELK, Datadog, etc.

### Tags
`#observability` `#debugging` `#production` `#python` `#json`

---

## Path Handling Cross-Platform {#path-handling}

### Contexto
Aplicaciones que deben funcionar en Windows, Linux y macOS.

### Problema
- Hardcoded paths con `/` o `\` fallan en otros OS
- `os.path.join` es verbose
- Concatenación de strings no funciona siempre

### Solución

Usar **pathlib.Path** para manejo cross-platform.

### Ejemplo

```python
from pathlib import Path

# ❌ MAL: Hardcoded
config_file = "C:\\Users\\user\\config.json"  # Solo Windows

# ❌ MAL: Concatenación manual
data_dir = base_path + "/data/genomes"  # Puede fallar

# ✅ BIEN: pathlib
config_file = Path.home() / "Documents" / "d8_data" / "config.json"
data_dir = Path(__file__).parent / "data" / "genomes"

# Beneficios de pathlib
file_path = Path("data") / "logs" / "app.log"

# Crear directorios
file_path.parent.mkdir(parents=True, exist_ok=True)

# Leer/escribir
content = file_path.read_text()
file_path.write_text("nuevo contenido")

# Información
if file_path.exists():
    size = file_path.stat().st_size
    modified = file_path.stat().st_mtime

# Glob patterns
for log_file in Path("logs").glob("*.log"):
    process(log_file)

# Iterar recursivamente
for py_file in Path("app").rglob("*.py"):
    analyze(py_file)
```

### Comparación

```python
# os.path (viejo)
import os
config_path = os.path.join(os.path.expanduser("~"), "Documents", "app", "config.json")
if not os.path.exists(os.path.dirname(config_path)):
    os.makedirs(os.path.dirname(config_path))

# pathlib (moderno)
config_path = Path.home() / "Documents" / "app" / "config.json"
config_path.parent.mkdir(parents=True, exist_ok=True)
```

### Resultado

✅ **Portabilidad:** Funciona en Windows/Linux/macOS  
✅ **Legibilidad:** Código más claro con `/` operator  
✅ **Funcionalidad:** Métodos útiles integrados  
✅ **Type Safety:** Path es un tipo específico

### Tags
`#compatibility` `#portability` `#python` `#filesystem`

---

**Última actualización:** 2025-11-19  
**Fuente:** Experiencias D8
