# 🤝 Contributing to D8

**Guía obligatoria para contribuir al proyecto D8**

---

## 🎯 Principios Fundamentales

### 1. Autonomía Total
- **TODO** en D8 debe funcionar sin intervención humana
- Si tu cambio requiere input manual, reconsidéralo
- Los agentes deben poder entender y usar tu código

### 2. Documentación Primero
- Documenta **ANTES** de implementar
- Si no está documentado, no existe
- Usa el sistema de memoria y experiencia

### 3. Tests Obligatorios
- Todo código nuevo debe tener tests
- Coverage mínimo: 80%
- Tests deben ser determinísticos

---

## 📁 Estructura de Carpetas

### Documentación: `docs/`

**REGLA DE ORO:** Ningún `.md` debe estar en la raíz de `docs/`

#### Categorías (numeradas para orden lógico):

```
docs/
├── README.md                    # Índice maestro (único archivo en raíz)
├── 01_arquitectura/             # Diseño del sistema
├── 02_setup/                    # Instalación y configuración
├── 03_operaciones/              # Guías de uso diario
├── 04_desarrollo/               # Testing y contribución
├── 05_troubleshooting/          # Solución de problemas
├── 06_knowledge_base/           # Memoria y experiencias
│   ├── memoria/                 # Patrones genéricos
│   └── experiencias_profundas/  # Conocimiento específico D8
└── 07_reportes/                 # Resultados de tests y experimentos
```

#### Cómo Categorizar Nueva Documentación:

**¿Qué estás documentando?**

| Tipo | Categoría | Ejemplo |
|------|-----------|---------|
| Diseño de componente | `01_arquitectura/` | `nuevo_sistema.md` |
| Cómo instalar/configurar | `02_setup/` | `setup_nueva_api.md` |
| Cómo usar algo | `03_operaciones/` | `ejecutar_componente.md` |
| Testing o dev | `04_desarrollo/` | `testing_nuevo_modulo.md` |
| Solución de error | `05_troubleshooting/` | `fix_error_xyz.md` |
| Patrón reutilizable | `06_knowledge_base/memoria/` | `patron_xyz.md` |
| Experiencia específica D8 | `06_knowledge_base/experiencias_profundas/` | `aprendizaje_xyz.md` |
| Resultados de test | `07_reportes/` | `benchmark_xyz.md` |

### Scripts: `scripts/`

**COHERENCIA CON DOCS:** La estructura refleja las categorías de documentación

```
scripts/
├── setup/              # Scripts de instalación (↔️ docs/02_setup/)
├── launch/             # Scripts de lanzamiento (↔️ docs/03_operaciones/)
├── tests/              # Scripts de testing (↔️ docs/04_desarrollo/)
└── [raíz]              # Solo scripts principales (congress, niche_discovery)
```

#### Reglas para Scripts:

1. **Scripts principales** (usados frecuentemente): `scripts/` raíz
   - `autonomous_congress.py`
   - `niche_discovery_agent.py`

2. **Scripts de setup**: `scripts/setup/`
   - Instalación de dependencias
   - Configuración inicial
   - Setup de servicios

3. **Scripts de lanzamiento**: `scripts/launch/`
   - Batch files para Windows
   - Shell scripts para Linux
   - Launchers de componentes

4. **Scripts de testing**: `scripts/tests/`
   - Test runners
   - Test automatizados
   - Benchmarks

### Código: `app/`

```
app/
├── agents/            # Implementación de agentes
├── evolution/         # Sistema evolutivo
├── distributed/       # Orchestrator y workers
├── integrations/      # Clientes de APIs externas
├── knowledge/         # Code vault y gestión de conocimiento
├── memory/            # Episodic buffer y vector store
└── utils/             # Utilidades compartidas
```

---

## ✍️ Naming Conventions

### Archivos y Carpetas
- **Snake case:** `mi_archivo.py`, `mi_carpeta/`
- **Descriptivo:** `groq_evolution.py` > `ge.py`
- **Sin espacios:** `niche_discovery.md` > `Niche Discovery.md`

### Python
- **Clases:** `PascalCase` → `BaseAgent`, `GroqClient`
- **Funciones/métodos:** `snake_case` → `run_evolution()`, `get_fitness()`
- **Constantes:** `UPPER_SNAKE_CASE` → `MAX_WORKERS`, `API_TIMEOUT`
- **Privado:** `_underscore` → `_internal_method()`

### Markdown
- **Títulos:** Sentence case → `# Cómo contribuir` > `# COMO CONTRIBUIR`
- **Enlaces:** Descriptivos → `[Setup Guide](02_setup/)` > `[click aquí](02_setup/)`

---

## 📝 Proceso de Documentación

### Al Agregar Nuevo Documento:

1. **Identifica la categoría correcta**
   ```bash
   # ¿Es arquitectura? → docs/01_arquitectura/
   # ¿Es setup? → docs/02_setup/
   # etc.
   ```

2. **Usa nombre descriptivo en snake_case**
   ```bash
   docs/01_arquitectura/sistema_de_recompensas.md
   ```

3. **Agrega frontmatter (opcional pero recomendado)**
   ```markdown
   ---
   title: Sistema de Recompensas
   category: Arquitectura
   tags: [rewards, fitness, evolution]
   last_updated: 2025-11-19
   ---
   ```

4. **Actualiza el README.md de la categoría**
   ```markdown
   ### [Sistema de Recompensas](sistema_de_recompensas.md)
   Cómo funciona el sistema de fitness y recompensas en D8.
   ```

5. **Si es muy importante, actualiza el README.md maestro**
   ```markdown
   # docs/README.md
   - [Sistema de Recompensas](01_arquitectura/sistema_de_recompensas.md)
   ```

### Al Agregar Nuevo Script:

1. **Decide su categoría**
   - ¿Setup/instalación? → `scripts/setup/`
   - ¿Lanzamiento? → `scripts/launch/`
   - ¿Testing? → `scripts/tests/`
   - ¿Script principal? → `scripts/` (raíz)

2. **Crea el script con header docstring**
   ```python
   #!/usr/bin/env python3
   """
   Script Name
   
   Descripción breve de qué hace el script.
   
   Usage:
       python scripts/categoria/mi_script.py [args]
   """
   ```

3. **Documenta el script en docs**
   ```markdown
   # docs/03_operaciones/mi_funcionalidad.md
   
   ## Ejecución
   
   \`\`\`bash
   python scripts/categoria/mi_script.py
   \`\`\`
   ```

---

## 🧠 Sistema de Memoria y Experiencia

**OBLIGATORIO:** Consultar antes de modificar D8

### Antes de Implementar:

1. ✅ Lee [`docs/06_knowledge_base/README.md`](../06_knowledge_base/README.md)
2. ✅ Busca si ya existe un patrón: `docs/06_knowledge_base/memoria/`
3. ✅ Revisa experiencias similares: `docs/06_knowledge_base/experiencias_profundas/`

### Después de Implementar:

1. ✅ **Si es específico de D8:** Documenta en `experiencias_profundas/`
   ```markdown
   ## [Título]
   
   ### Fecha
   2025-11-19
   
   ### Contexto
   ¿Qué estábamos haciendo?
   
   ### Problema/Decisión
   ¿Qué decidimos o aprendimos?
   
   ### Implementación
   ¿Cómo se implementa?
   
   ### Resultado
   ¿Qué logramos?
   
   ### Tags
   `#tag1` `#tag2`
   ```

2. ✅ **Si es reutilizable:** Promuévelo a `memoria/`
   - Generaliza el conocimiento
   - Hazlo aplicable a otros proyectos

---

## 🧪 Testing

### Reglas de Testing:

1. **Todo código nuevo debe tener tests**
   ```python
   # tests/unit/test_mi_modulo.py
   def test_mi_funcion():
       assert mi_funcion() == expected
   ```

2. **Organización de tests:**
   ```
   tests/
   ├── unit/           # Tests unitarios
   ├── integration/    # Tests de integración
   └── e2e/            # Tests end-to-end
   ```

3. **Ejecutar tests antes de commit:**
   ```bash
   pytest tests/
   ```

4. **Coverage mínimo: 80%**
   ```bash
   pytest --cov=app --cov-report=html tests/
   ```

---

## 🔄 Workflow de Contribución

### 1. Fork y Clone
```bash
git clone https://github.com/TU_USUARIO/d8.git
cd d8
```

### 2. Crear Branch
```bash
git checkout -b feature/mi-nueva-funcionalidad
```

### 3. Implementar
```python
# 1. Consultar knowledge base
# 2. Escribir tests
# 3. Implementar código
# 4. Documentar
```

### 4. Validar
```bash
# Tests
pytest tests/

# Linting
flake8 app/ scripts/

# Type checking
mypy app/
```

### 5. Commit
```bash
git add .
git commit -m "feat: agregar nueva funcionalidad XYZ"
```

**Formato de commits:**
- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de bug
- `docs:` - Cambios en documentación
- `test:` - Agregar o modificar tests
- `refactor:` - Refactorización sin cambio funcional
- `chore:` - Mantenimiento, dependencias, etc.

### 6. Push y PR
```bash
git push origin feature/mi-nueva-funcionalidad
```

Luego crea Pull Request en GitHub con:
- Descripción clara del cambio
- Link a issue relacionado (si existe)
- Screenshots/logs (si aplica)
- Checklist de validación

---

## ✅ Checklist Pre-Commit

Antes de hacer commit, verifica:

- [ ] Código sigue naming conventions
- [ ] Tests creados y pasando (`pytest tests/`)
- [ ] Documentación actualizada
- [ ] README.md de categoría actualizado (si aplica)
- [ ] Knowledge base consultado y actualizado
- [ ] Sin archivos en raíces incorrectas (`docs/` raíz, etc.)
- [ ] Paths son cross-platform (`pathlib.Path`)
- [ ] Logs usando `app.utils.logger`
- [ ] Secrets en `.env`, no hardcodeados

---

## 📞 ¿Dudas?

1. Busca en documentación existente
2. Revisa issues en GitHub
3. Abre un issue con tag `question`

---

## 📜 Licencia

Al contribuir, aceptas que tu código se licencie bajo MIT.

---

**🤖 D8 - Sistema de IA Autónomo**  
**Contribuciones bienvenidas - Mantengamos el código limpio y autónomo**
