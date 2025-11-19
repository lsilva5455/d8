# 🚨 Errores Comunes en D8

**FAQ de problemas frecuentes y sus soluciones**

---

## 🔑 Problemas de API Keys

### Error: `API key not found` o `Invalid API key`

**Causa:** La API key no está configurada o es inválida.

**Solución:**
```bash
# 1. Verifica que .env existe
ls .env

# 2. Revisa el contenido
cat .env

# 3. Debe contener (sin comillas):
GROQ_API_KEY=gsk_tu_key_aqui

# 4. Si no existe, créalo:
echo "GROQ_API_KEY=gsk_tu_key_aqui" > .env

# 5. Obtén tu key en: https://console.groq.com/
```

---

## 📦 Import Errors

### Error: `ModuleNotFoundError: No module named 'app'`

**Causa:** Virtual environment no activado o mal configurado.

**Solución:**
```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Verificar que está activo (debe mostrar (venv) al inicio)
# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: `ImportError: cannot import name 'X' from 'app.Y'`

**Causa:** Estructura de imports rota o módulo no existe.

**Solución:**
```bash
# Verificar que __init__.py existe en todas las carpetas
ls app/__init__.py
ls app/agents/__init__.py

# Si falta, créalo vacío:
New-Item app/__init__.py -ItemType File
```

---

## 🌐 Problemas de Workers

### Error: Worker no responde o "No workers available"

**Causa:** Worker no registrado o murió sin desregistrarse.

**Solución:**
```bash
# 1. Verificar orchestrator corriendo
curl http://localhost:5000/api/health

# 2. Ver workers registrados
curl http://localhost:5000/api/workers

# 3. Reiniciar worker
python app/distributed/worker_groq.py

# 4. Si persiste, reiniciar orchestrator
taskkill /F /FI "WINDOWTITLE eq *Orchestrator*"
python app/distributed/orchestrator.py
```

### Error: Heartbeat timeout

**Causa:** Worker no envía heartbeat o red lenta.

**Solución:**
1. Aumentar timeout en `orchestrator.py`:
   ```python
   HEARTBEAT_TIMEOUT = 120  # era 60
   ```
2. Verificar conectividad:
   ```bash
   ping localhost
   ```

---

## 🚫 Rate Limit Errors

### Error: `429 Too Many Requests`

**Causa:** API rate limit excedido (muy común con Gemini).

**Solución:**
- Ver guía completa: [Error 429](error_429.md)
- TL;DR: Migrar a Groq (14,400 req/día gratis)

---

## 📂 Path Problems

### Error: `FileNotFoundError: [Errno 2] No such file or directory`

**Causa:** Paths hardcodeados o no cross-platform.

**Solución:**
```python
# ❌ MAL
config_path = "C:\\Users\\User\\Documents\\d8_data\\config.json"

# ✅ BIEN
from pathlib import Path
config_path = Path.home() / "Documents" / "d8_data" / "config.json"
```

### Error: `PermissionError: [Errno 13] Permission denied`

**Causa:** Archivo en uso o sin permisos.

**Solución:**
```powershell
# Ver qué proceso usa el archivo
handle.exe archivo.json  # O usar Process Explorer

# Cambiar permisos (Windows)
icacls archivo.json /grant Users:F
```

---

## 🐍 Python Version Issues

### Error: `SyntaxError: invalid syntax` (con match/case)

**Causa:** Python < 3.10 (match/case requiere 3.10+).

**Solución:**
```bash
# Verificar versión
python --version  # Debe ser >= 3.10

# Si es menor, instalar Python 3.10+
# Luego recrear venv:
python -m venv venv
```

---

## 🧪 Testing Errors

### Error: Tests fallan con `fixture 'X' not found`

**Causa:** Pytest no encuentra fixtures o conftest.py.

**Solución:**
```bash
# Verificar estructura:
tests/
├── __init__.py
├── conftest.py  # ← Debe existir
└── unit/
    └── test_algo.py

# Ejecutar desde raíz del proyecto
pytest tests/
```

---

## 🔧 Dependencias

### Error: `No module named 'groq'` (o similar)

**Causa:** Dependencia no instalada.

**Solución:**
```bash
# Instalar dependencias faltantes
pip install -r requirements.txt

# Si persiste, instalar individual:
pip install groq
```

---

## 🔄 Git Issues

### Error: `fatal: not a git repository`

**Causa:** No estás en un repositorio git.

**Solución:**
```bash
# Inicializar repo
git init

# O clonar desde GitHub
git clone https://github.com/lsilva5455/d8.git
```

---

## 🆘 Último Recurso

Si nada funciona:

1. **Limpieza completa:**
   ```bash
   # Borrar venv
   Remove-Item -Recurse -Force venv

   # Recrear
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Verificar logs:**
   ```bash
   # Ver logs recientes
   Get-Content data/logs/*.log -Tail 50
   ```

3. **Abrir issue en GitHub:**
   - Describe el problema
   - Incluye traceback completo
   - Menciona OS y Python version

---

**Volver a [Troubleshooting](README.md)**
