# 📜 Scripts de D8

**Scripts ejecutables organizados por categoría**

---

## 📂 Estructura

```
scripts/
├── autonomous_congress.py      # Congreso autónomo (principal)
├── niche_discovery_agent.py    # Descubrimiento de nichos (principal)
├── setup/                      # Scripts de instalación y configuración
├── launch/                     # Scripts de lanzamiento de componentes
└── tests/                      # Scripts de testing automatizado
```

---

## 🚀 Scripts Principales

### `autonomous_congress.py`
**Congreso Autónomo** - Sistema de mejora continua

```bash
python scripts/autonomous_congress.py
```

**Qué hace:**
- 5 agentes especializados (Researcher, Experimenter, Optimizer, Implementer, Validator)
- Ciclo completo: Investiga → Experimenta → Valida → Implementa
- Guarda resultados en `data/congress_experiments/`

**Documentación:** [Congreso Autónomo](../docs/01_arquitectura/sistema_completo.md#congreso-autónomo)

### `niche_discovery_agent.py`
**Niche Discovery** - Descubrimiento de nichos rentables

```bash
python scripts/niche_discovery_agent.py
```

**Qué hace:**
- Analiza mercados automáticamente
- Identifica oportunidades rentables
- Genera reportes estructurados en `data/test_results/`

**Documentación:** [Niche Discovery](../docs/03_operaciones/monetizacion.md)

---

## ⚙️ Scripts de Setup (`setup/`)

Scripts para instalación inicial y configuración.

### `setup_project.ps1`
Setup completo del proyecto (Windows PowerShell)

```powershell
.\scripts\setup\setup_project.ps1
```

**Qué hace:**
- Crea virtual environment
- Instala dependencias
- Configura .env
- Verifica instalación

### `setup_project.sh`
Setup completo del proyecto (Linux/Mac)

```bash
bash scripts/setup/setup_project.sh
```

### `setup_groq.ps1`
Configuración específica de Groq workers

```powershell
.\scripts\setup\setup_groq.ps1
```

**Documentación:** [Groq Worker Setup](../docs/02_setup/groq_worker.md)

### `FIX_API_KEY.ps1`
Fix rápido para problemas de API keys

```powershell
.\scripts\setup\FIX_API_KEY.ps1
```

---

## 🚀 Scripts de Launch (`launch/`)

Scripts para lanzar componentes del sistema.

### `launch_distributed.bat`
Lanza sistema distribuido completo (Orchestrator + Workers)

```bash
.\scripts\launch\launch_distributed.bat
```

**Qué hace:**
- Lanza Orchestrator en puerto 5000
- Lanza Workers configurados
- Monitorea heartbeats

### `launch_resilient.bat`
Lanza sistema con workers resilientes (retry logic)

```bash
.\scripts\launch\launch_resilient.bat
```

### `restart_orchestrator.bat`
Reinicia el Orchestrator manteniendo workers

```bash
.\scripts\launch\restart_orchestrator.bat
```

---

## 🧪 Scripts de Testing (`tests/`)

Scripts para testing automatizado del sistema.

### `FULL_AUTOMATED_TEST.bat`
Test completo del sistema end-to-end

```bash
.\scripts\tests\FULL_AUTOMATED_TEST.bat
```

**Qué hace:**
- Ejecuta todos los tests
- Genera reporte de resultados
- Guarda en `data/test_results/`

### `test_distributed.bat` / `test_distributed.ps1`
Test del sistema distribuido

```bash
.\scripts\tests\test_distributed.bat
```

### `test_groq_system.ps1`
Test específico de integración Groq

```powershell
.\scripts\tests\test_groq_system.ps1
```

### Test Especializados (Python)

```bash
# Test del congreso con optimización
python scripts/tests/test_congress_optimization.py

# Test de niche congress
python scripts/tests/test_niche_congress.py

# Test del sistema evolutivo
python scripts/tests/test_simple_niche.py
```

---

## 🔄 Coherencia con Documentación

La estructura de `scripts/` refleja las categorías de `docs/`:

| Scripts | Documentación |
|---------|---------------|
| `scripts/setup/` | `docs/02_setup/` |
| `scripts/launch/` | `docs/03_operaciones/` |
| `scripts/tests/` | `docs/04_desarrollo/` |
| `scripts/[raíz]` | Scripts principales (congress, niche discovery) |

---

## 📝 Cómo Agregar Nuevo Script

### 1. Identifica la categoría:
- **Setup/instalación** → `scripts/setup/`
- **Lanzamiento de componente** → `scripts/launch/`
- **Testing** → `scripts/tests/`
- **Script principal usado frecuentemente** → `scripts/` (raíz)

### 2. Crea el script con header:
```python
#!/usr/bin/env python3
"""
Nombre del Script

Descripción breve de qué hace.

Usage:
    python scripts/categoria/mi_script.py [args]
    
Examples:
    python scripts/categoria/mi_script.py --config test.json
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Imports del proyecto
from app.config import Config

def main():
    """Main function."""
    pass

if __name__ == "__main__":
    main()
```

### 3. Hazlo ejecutable (Linux/Mac):
```bash
chmod +x scripts/categoria/mi_script.py
```

### 4. Documenta en README.md:
Actualiza este README.md con descripción del nuevo script.

### 5. Documenta en docs:
Agrega documentación en la categoría correspondiente de `docs/`.

---

## ⚠️ Reglas Importantes

1. **NO scripts en la raíz de `docs/`** - Documentación ≠ Scripts
2. **Paths relativos** - Usar `Path(__file__).parent` para portabilidad
3. **Cross-platform** - Preferir `.py` sobre `.bat` cuando sea posible
4. **Docstrings** - Todo script debe tener docstring explicativo
5. **Shebang** - Agregar `#!/usr/bin/env python3` en primera línea

---

**Volver al [Índice de Documentación](../docs/README.md)**
