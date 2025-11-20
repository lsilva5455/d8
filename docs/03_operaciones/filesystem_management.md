# 📁 Sistema de Gestión de Archivos y Git para el Congreso

**Fecha:** 2025-11-20  
**Estado:** ✅ Operacional

---

## 🎯 Visión General

El Congreso Autónomo ahora tiene acceso completo al sistema de archivos local y capacidades de Git/GitHub para:

1. **Leer y modificar código** del proyecto D8
2. **Gestionar datos** en `~/Documents/d8_data`
3. **Hacer commits** y crear **Pull Requests** automáticamente
4. **Buscar archivos** y analizar el código
5. **Interactuar con Leo** vía Telegram para aprobar cambios

---

## 🏗️ Arquitectura

### Componentes

```
┌─────────────────────────────────────────────────┐
│           Telegram Bot (Leo)                    │
│  Comandos: /ls, /read, /write, /commit, /pr    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│       FileSystemManager                         │
│  - Validación de rutas (seguridad)             │
│  - Operaciones CRUD en archivos                 │
│  - Búsqueda de archivos                         │
│  - Git operations (commit, push, PR)            │
└────────────────┬────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────┐
│   c:/d8/     │  │ ~/Documents/ │
│  (Proyecto)  │  │   d8_data/   │
│              │  │   (Datos)    │
└──────────────┘  └──────────────┘
```

### Seguridad

**Rutas permitidas:**
- ✅ `c:/Users/PcDos/d8/` - Proyecto principal
- ✅ `~/Documents/d8_data/` - Datos y configuración
- ❌ Cualquier otra ruta → **Acceso denegado**

**Validación automática:**
- Todas las rutas se resuelven a absolutas
- Se verifica que estén dentro de las rutas permitidas
- Se rechaza acceso a sistema, otros proyectos, etc.

---

## 🤖 Comandos de Telegram

### Gestión de Archivos

#### `/ls [directorio]`
Lista contenido de un directorio

**Ejemplos:**
```
/ls                    # Lista raíz del proyecto
/ls app                # Lista directorio app
/ls ~/Documents/d8_data # Lista datos
```

**Respuesta:**
```
📁 c:\Users\PcDos\d8\app

Directorios:
📁 agents
📁 evolution
📁 integrations
📁 economy

Archivos:
📄 __init__.py (2.1KB)
📄 config.py (5.3KB)
📄 main.py (8.7KB)
```

---

#### `/read <archivo>`
Lee contenido de un archivo

**Ejemplos:**
```
/read README.md
/read app/config.py
/read ~/Documents/d8_data/config.json
```

**Respuesta:**
```
📄 c:\Users\PcDos\d8\app\config.py
Tamaño: 5432 bytes | Líneas: 156

```python
# Configuration for D8 system
from pydantic import BaseSettings

class Config(BaseSettings):
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    ...
```
```

---

#### `/write <archivo> <contenido>`
Escribe contenido a un archivo

⚠️ **Crea backup automático** antes de sobrescribir

**Ejemplos:**
```
/write test.txt Hola mundo
/write app/test.py print("Hello from Congress")
```

**Respuesta:**
```
✅ Archivo escrito

📄 c:\Users\PcDos\d8\test.txt
📝 11 bytes escritos
💾 Backup: test_20251120_194523.txt
```

---

#### `/search <patrón>`
Busca archivos por nombre

**Ejemplos:**
```
/search *.py           # Todos los archivos Python
/search test_          # Archivos que empiezan con test_
/search config         # Archivos con "config" en el nombre
```

**Respuesta:**
```
🔍 Resultados para: *.py

📄 app/__init__.py
📄 app/config.py
📄 app/main.py
📄 app/agents/base_agent.py
📄 app/evolution/darwin.py
... y 87 más

Total: 92 archivos
```

---

### Operaciones Git

#### `/git_status`
Ver estado de Git (cambios, staged, etc.)

**Respuesta:**
```
🔀 Git Status

Branch: `docker-workers...origin/docker-workers`

Modificados:
📝 app/integrations/telegram_bot.py
📝 app/integrations/filesystem_manager.py

Sin seguimiento:
❓ scripts/tests/test_filesystem_manager.py

✨ Total: 3 archivos
```

---

#### `/commit <archivos> -m '<mensaje>'`
Hacer commit de cambios

**Ejemplos:**
```
/commit app/config.py -m 'feat: Update config'
/commit . -m 'docs: Update all documentation'
/commit app/integrations/*.py -m 'refactor: Improve integrations'
```

**Respuesta:**
```
✅ Commit exitoso

Hash: `a7f3c8d2`
Mensaje: feat: Update config

Usa /pr para crear Pull Request
```

---

#### `/pr '<título>' -d '<descripción>'`
Crear Pull Request en GitHub

⚠️ **Hace push automático** antes de crear PR

**Ejemplos:**
```
/pr 'feat: Add file management' -d 'Adds filesystem operations to Congress'
/pr 'fix: Bug in evolution' -d 'Fixes selection algorithm'
```

**Respuesta:**
```
✅ Pull Request creado

Número: #47
Título: feat: Add file management
Estado: open

🔗 https://github.com/lsilva5455/d8/pull/47
```

---

## 🗣️ Lenguaje Natural

El bot interpreta comandos en lenguaje natural:

**Ejemplos:**

```
"Lee el archivo app/config.py"
→ Ejecuta /read app/config.py

"Lista archivos en app/agents"
→ Ejecuta /ls app/agents

"Busca archivos Python"
→ Ejecuta /search *.py

"¿Qué cambió en git?"
→ Ejecuta /git_status

"Muestra el README"
→ Ejecuta /read README.md
```

---

## 🔧 API Programática

### Python API

```python
from app.integrations.filesystem_manager import get_filesystem_manager

# Inicializar
fs = get_filesystem_manager()

# Listar directorio
result = fs.list_directory("app")
print(result['files'])
print(result['directories'])

# Leer archivo
result = fs.read_file("app/config.py")
print(result['content'])

# Escribir archivo (con backup)
result = fs.write_file(
    "test.txt",
    "Contenido del archivo",
    create_backup=True
)

# Buscar archivos
matches = fs.search_files("*.py", path="app")

# Git status
status = fs.git_status()
print(status['modified'])
print(status['branch'])

# Commit
result = fs.git_commit(
    files=["app/config.py"],
    message="feat: Update config",
    author_name="D8 Congress",
    author_email="congress@d8.ai"
)
print(result['commit_hash'])

# Push
result = fs.push_to_github()

# Create PR
result = fs.create_pull_request(
    title="feat: New feature",
    body="Description of changes",
    base_branch="main"
)
print(result['pr_url'])
```

---

## 🛡️ Seguridad

### Validación de Rutas

```python
# ✅ Permitido
fs.read_file("app/config.py")
fs.read_file("~/Documents/d8_data/config.json")

# ❌ Rechazado
fs.read_file("C:/Windows/System32/config")
fs.read_file("../../../etc/passwd")
fs.read_file("~/Desktop/secreto.txt")
```

**Error:**
```
ValueError: Access denied: C:\Windows\System32 is outside allowed directories
```

### Backups Automáticos

Antes de sobrescribir un archivo, se crea backup:

```
Original: app/config.py
Backup:   ~/Documents/d8_data/backups/config_20251120_194523.py
```

Los backups se guardan en: `~/Documents/d8_data/backups/`

---

## 🧪 Testing

### Test Completo

```bash
# Ejecutar test suite
python scripts/tests/test_filesystem_manager.py
```

**Output esperado:**
```
🧪 Testing FileSystem Manager
============================================================

1. Initializing FileSystemManager...
   ✅ Project root: c:\Users\PcDos\d8
   ✅ Data root: C:\Users\PcDos\Documents\d8_data

2. Testing list_directory('.')...
   ✅ Path: C:\Users\PcDos\d8
   ✅ Files: 12
   ✅ Directories: 15

3. Testing read_file('README.md')...
   ✅ Size: 12849 bytes
   ✅ Lines: 420

4. Testing search_files('*.py', path='app')...
   ✅ Found 92 Python files

5. Testing git_status()...
   ✅ Branch: docker-workers
   ✅ Modified: 2
   ✅ Untracked: 1

6. Testing write_file...
   ✅ Wrote 54 bytes

7. Verifying write...
   ✅ Content verified

8. Testing path validation...
   ✅ Correctly rejected unauthorized path

============================================================
✅ All tests completed
```

---

## 📊 Casos de Uso

### Caso 1: Congreso Modifica Configuración

```
1. Congress: "Necesito optimizar el modelo Groq"
2. Leo (Telegram): "¿Qué cambios propones?"
3. Congress: "Cambiar a llama-3.3-70b-versatile"
4. Leo: /read app/config.py
   [Ve configuración actual]
5. Leo: /write app/config.py [nuevo contenido]
6. Leo: /commit app/config.py -m 'feat: Upgrade to llama-3.3'
7. Leo: /pr 'feat: Upgrade Groq model' -d 'Better performance'
8. GitHub: PR creado → Leo revisa y mergea
```

### Caso 2: Congreso Descubre Bug

```
1. Congress detecta error en darwin.py
2. Congress notifica a Leo vía Telegram
3. Leo: /read app/evolution/darwin.py
4. Leo revisa el código
5. Congress propone fix
6. Leo: /write app/evolution/darwin.py [código fixed]
7. Leo: /git_status (verifica cambios)
8. Leo: /commit app/evolution/darwin.py -m 'fix: Selection algorithm'
9. Tests automáticos pasan
10. Leo: /pr 'fix: Darwin selection bug' -d 'Fixed edge case'
```

### Caso 3: Análisis de Código

```
1. Leo: "Busca todos los archivos de tests"
2. Bot: /search test_*.py
3. Leo: "Lee el test de economía"
4. Bot: /read tests/economy/test_mock_economy.py
5. Leo analiza coverage
6. Leo: "Lista experimentos del congreso"
7. Bot: /ls data/congress_experiments
8. Leo: "Lee el último experimento"
9. Bot: /read data/congress_experiments/cycle_003.json
```

---

## 🚀 Próximos Pasos

### Mejoras Planificadas

1. **Diff Viewer** - Ver cambios antes de commit
2. **Code Review** - Congress puede comentar en PRs
3. **Auto-merge** - Merge automático si tests pasan
4. **File Watcher** - Detectar cambios externos
5. **Syntax Validation** - Validar Python antes de escribir
6. **Embeddings Search** - Búsqueda semántica de código

---

## 📚 Referencias

**Archivos:**
- `app/integrations/filesystem_manager.py` - Implementación principal
- `app/integrations/telegram_bot.py` - Comandos de Telegram
- `scripts/tests/test_filesystem_manager.py` - Tests

**Configuración:**
- `GITHUB_TOKEN` - Token para GitHub API (PRs)
- `GITHUB_REPO_OWNER` - Owner del repo (lsilva5455)
- `GITHUB_REPO_NAME` - Nombre del repo (d8)
- `GITHUB_REPO_BRANCH` - Branch actual (docker-workers)

---

**Última actualización:** 2025-11-20  
**Autor:** D8 Autonomous System  
**Estado:** ✅ Operacional y probado
