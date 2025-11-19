# 📏 Standards y Convenciones - D8

**Estándares de código para mantener consistencia**

---

## 🐍 Python Conventions

### PEP 8 Compliance
- Seguir [PEP 8](https://pep8.org/)
- Líneas máximo 100 caracteres (no 79)
- 4 espacios de indentación (no tabs)

### Naming
```python
# Classes: PascalCase
class BaseAgent:
    pass

# Functions/methods: snake_case
def calculate_fitness(genome: str) -> float:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_WORKERS = 10
API_TIMEOUT = 30

# Private: _underscore
def _internal_helper():
    pass

# Protected (subclasses): _single_underscore
class Agent:
    def _process_task(self):
        pass

# Name mangling: __double_underscore
class Agent:
    def __private_method(self):
        pass
```

---

## 📝 Docstrings

### Formato: Google Style
```python
def evolve_population(
    population: List[Agent],
    generations: int,
    mutation_rate: float = 0.1
) -> List[Agent]:
    """
    Evoluciona una población de agentes mediante selección natural.
    
    Args:
        population: Lista de agentes a evolucionar
        generations: Número de generaciones a ejecutar
        mutation_rate: Probabilidad de mutación (0.0 a 1.0)
    
    Returns:
        Lista de agentes evolucionados, ordenados por fitness
    
    Raises:
        ValueError: Si mutation_rate no está entre 0 y 1
        
    Example:
        >>> agents = [Agent(genome=g) for g in initial_genomes]
        >>> evolved = evolve_population(agents, 100)
        >>> print(f"Best fitness: {evolved[0].fitness}")
    """
    if not 0 <= mutation_rate <= 1:
        raise ValueError("mutation_rate debe estar entre 0 y 1")
    
    # ...
```

### Docstrings de Clase:
```python
class GroqClient:
    """
    Cliente para interactuar con la API de Groq.
    
    Maneja autenticación, rate limiting y retry logic para requests
    a la API de Groq. Soporta múltiples modelos y streaming.
    
    Attributes:
        api_key: API key de Groq
        model: Nombre del modelo a usar (default: llama-3.3-70b-versatile)
        timeout: Timeout en segundos para requests
        
    Example:
        >>> client = GroqClient(api_key="gsk_...", model="llama-3.3-70b")
        >>> response = client.chat("Hola, ¿cómo estás?")
        >>> print(response.content)
    """
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        """Inicializa el cliente de Groq."""
        self.api_key = api_key
        self.model = model
```

---

## 🔤 Type Hints

**OBLIGATORIO** en todas las funciones públicas:

```python
from typing import List, Dict, Optional, Tuple, Union
from pathlib import Path

# ✅ BIEN
def process_genome(
    genome: str,
    mutations: List[str],
    config: Optional[Dict[str, any]] = None
) -> Tuple[str, float]:
    """Procesa un genoma con mutaciones."""
    # ...
    return mutated_genome, fitness_score

# ❌ MAL
def process_genome(genome, mutations, config=None):
    """Procesa un genoma con mutaciones."""
    # ...
    return mutated_genome, fitness_score
```

### Type Aliases
```python
from typing import TypeAlias

# Definir aliases para tipos complejos
Genome: TypeAlias = str
Fitness: TypeAlias = float
AgentConfig: TypeAlias = Dict[str, Union[str, int, float]]

def evaluate_agent(genome: Genome) -> Fitness:
    """Evalúa fitness de un agente."""
    pass
```

---

## 🪵 Logging

### Usar logger centralizado:
```python
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Niveles:
logger.debug("Detalle para debugging")
logger.info("Información general")
logger.warning("Algo sospechoso pero no crítico")
logger.error("Error que afecta funcionalidad")
logger.critical("Error crítico, sistema en riesgo")

# Con contexto:
logger.info(f"Worker {worker_id} registrado exitosamente")
logger.error(f"Error al procesar task {task_id}", exc_info=True)
```

### NO usar print():
```python
# ❌ MAL
print(f"Procesando task: {task_id}")

# ✅ BIEN
logger.info(f"Procesando task: {task_id}")
```

---

## 🚨 Error Handling

### Try-except específico:
```python
# ✅ BIEN
try:
    result = api_call()
except requests.exceptions.Timeout:
    logger.error("API timeout")
    raise
except requests.exceptions.RequestException as e:
    logger.error(f"API error: {e}")
    raise

# ❌ MAL
try:
    result = api_call()
except:  # Demasiado genérico
    pass
```

### Custom Exceptions:
```python
# app/exceptions.py
class D8Error(Exception):
    """Base exception para D8."""
    pass

class WorkerError(D8Error):
    """Error relacionado con workers."""
    pass

class RateLimitError(D8Error):
    """Rate limit excedido."""
    pass

# Uso:
if rate_limit_exceeded:
    raise RateLimitError(f"Rate limit: {limit} req/min")
```

---

## 🗂️ Imports

### Orden:
```python
# 1. Standard library
import os
import sys
from pathlib import Path
from typing import List, Dict

# 2. Third party
import requests
from flask import Flask
import numpy as np

# 3. Local
from app.agents.base_agent import BaseAgent
from app.utils.logger import get_logger
from app.config import Config
```

### Evitar wildcard imports:
```python
# ❌ MAL
from app.utils import *

# ✅ BIEN
from app.utils import get_logger, load_config
```

---

## 📦 Estructura de Archivos

### Módulo típico:
```python
"""
Breve descripción del módulo.

Descripción más detallada si es necesario.
"""

# Imports
from typing import List
from app.utils.logger import get_logger

# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Module-level logger
logger = get_logger(__name__)

# Classes
class MyClass:
    """Docstring."""
    pass

# Functions
def my_function():
    """Docstring."""
    pass

# Main (solo si es ejecutable)
if __name__ == "__main__":
    main()
```

---

## 🧪 Testing

### Naming:
```python
# Archivo: test_base_agent.py
# Clase: TestBaseAgent
# Método: test_agent_fitness_calculation

class TestBaseAgent:
    """Tests para BaseAgent."""
    
    def test_agent_fitness_calculation(self):
        """Test que fitness se calcula correctamente."""
        agent = BaseAgent(genome="test genome")
        fitness = agent.calculate_fitness(task="test")
        assert fitness > 0
```

### Fixtures:
```python
# conftest.py
import pytest

@pytest.fixture
def sample_agent():
    """Agente de prueba."""
    return BaseAgent(genome="test genome")

# test_base_agent.py
def test_with_fixture(sample_agent):
    """Test usando fixture."""
    assert sample_agent.genome == "test genome"
```

---

## 🔒 Secrets y Config

### NUNCA hardcodear secrets:
```python
# ❌ MAL
api_key = "gsk_12345abcde"

# ✅ BIEN
from app.config import Config
config = Config()
api_key = config.groq_api_key
```

### Usar .env:
```bash
# .env (gitignored)
GROQ_API_KEY=gsk_tu_key_aqui
GEMINI_API_KEY=tu_key_aqui
```

```python
# app/config.py
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not set")
```

---

## 📂 Path Handling

### Usar pathlib.Path:
```python
from pathlib import Path

# ✅ BIEN (cross-platform)
config_path = Path.home() / "Documents" / "d8_data" / "config.json"
data_dir = Path(__file__).parent / "data"

# ❌ MAL (solo Windows)
config_path = "C:\\Users\\User\\Documents\\d8_data\\config.json"

# ❌ MAL (solo Linux/Mac)
config_path = "/home/user/d8/config.json"
```

---

## 🔄 Async/Await

Si usas async (no común en D8 actual):
```python
import asyncio
from typing import List

async def fetch_data(url: str) -> dict:
    """Fetch data asincrónicamente."""
    # ...
    pass

async def main():
    """Main async."""
    urls = ["url1", "url2", "url3"]
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

# Ejecutar
if __name__ == "__main__":
    asyncio.run(main())
```

---

## ✅ Code Review Checklist

Antes de hacer PR:

- [ ] PEP 8 compliant (`flake8 app/`)
- [ ] Type hints en funciones públicas
- [ ] Docstrings (Google style)
- [ ] Logging (no prints)
- [ ] Error handling específico
- [ ] Tests escritos y pasando
- [ ] Secrets en .env, no hardcodeados
- [ ] Paths con pathlib.Path
- [ ] Imports ordenados
- [ ] No código comentado sin explicación

---

**Volver a [Desarrollo](README.md)**
