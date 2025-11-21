# 🔧 Correcciones al Supervisor D8

**Fecha:** 2025-11-21  
**Versión:** 0.0.5  
**Archivos modificados:** 2

---

## 🐛 Problema Original

Al ejecutar `start_d8.py` opción 6 (Supervisor), se presentaban dos errores:

### Error 1: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'app.agents.base_agent'
```

**Causa:** El supervisor no configuraba `PYTHONPATH` antes de lanzar los scripts, causando que los imports desde `app/` fallaran.

### Error 2: Reintentos excesivos en Rate Limit
```
Error code: 429 - Rate limit reached for model `llama-3.3-70b-versatile`
```

**Causa:** El supervisor reintentaba cada 5 segundos sin importar el tipo de error, causando spam de requests y logs excesivos.

---

## ✅ Soluciones Implementadas

### 1. PYTHONPATH en Supervisor

**Archivo:** `scripts/supervisor_d8.py`  
**Líneas:** 167-169, 178-180

**Cambio:**
```python
# Antes (sin environment)
process = subprocess.Popen(
    [sys.executable, str(script_path)],
    cwd=self.project_root,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)

# Después (con PYTHONPATH)
env = os.environ.copy()
env["PYTHONPATH"] = str(self.project_root)

process = subprocess.Popen(
    [sys.executable, str(script_path)],
    cwd=self.project_root,
    env=env,  # ← AGREGADO
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
```

**Resultado:** Todos los scripts ahora pueden importar módulos de `app/` correctamente.

---

### 2. Delays Adaptativos por Tipo de Error

**Archivo:** `scripts/supervisor_d8.py`  
**Líneas:** 202-218

**Cambio:**
```python
# Detectar errores conocidos
if "Rate limit" in error_msg or "429" in error_msg:
    logger.warning(f"   ⏳ Rate limit detectado - Esperando 60s")
    delay_seconds = 60
elif "ModuleNotFoundError" in error_msg:
    logger.error(f"   ❌ Error de importación - Verificar PYTHONPATH")
    delay_seconds = 30

time.sleep(delay_seconds)
```

**Resultado:** 
- Rate limit (429) → Espera 60 segundos
- Import errors → Espera 30 segundos
- Otros errores → Espera 5 segundos (default)

---

### 3. Fix en niche_discovery_agent.py

**Archivo:** `scripts/niche_discovery_agent.py`  
**Línea:** 12

**Cambio:**
```python
# Antes (incorrecto - apunta a scripts/)
sys.path.insert(0, str(Path(__file__).parent))

# Después (correcto - apunta a d8/)
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Resultado:** Script puede importar `app.agents.base_agent` sin errores.

---

## 🧪 Validación

### Verificar imports funcionan:
```bash
python scripts/niche_discovery_agent.py --help
```

**Resultado esperado:** 
- ✅ Script inicia sin `ModuleNotFoundError`
- ⚠️ Puede fallar con rate limit 429 (esperado si agotaste límite diario)

### Ejecutar supervisor:
```bash
python start_d8.py
# Seleccionar opción 6
```

**Resultado esperado:**
- ✅ Componentes inician correctamente
- ✅ Rate limits detectados y pausados 60s
- ✅ Import errors no causan reintentos infinitos

---

## 📊 Estado de Rate Limits Groq

**Límite diario:** 100,000 tokens  
**Modelos afectados:** `llama-3.3-70b-versatile`

**Si alcanzas el límite:**

**Opción A:** Esperar hasta siguiente día (reset ~00:00 UTC)

**Opción B:** Cambiar modelo en `.env`
```bash
# Opción 1: Usar modelo más pequeño de Groq
LLM_MODEL=llama-3.1-8b-instant

# Opción 2: Usar Gemini (requiere GEMINI_API_KEY)
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash

# Opción 3: Usar DeepSeek (requiere DEEPSEEK_API_KEY)
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
```

**Opción C:** Upgrade a Groq Dev Tier
- Mayor límite de tokens/día
- URL: https://console.groq.com/settings/billing

---

## 🔍 Debugging

### Ver logs del supervisor:
```bash
cat ~/Documents/d8_data/logs/supervisor.log
```

### Ver logs de componentes individuales:
```bash
# Congreso Autónomo
cat ~/Documents/d8_data/logs/congress.log

# Niche Discovery
cat ~/Documents/d8_data/logs/niche_discovery.log

# Orchestrator
cat ~/Documents/d8_data/logs/orchestrator.log
```

### Verificar lockfile:
```bash
cat ~/Documents/d8_data/supervisor.lock
```

---

## 📝 Checklist Post-Fix

- [x] Supervisor configura PYTHONPATH
- [x] niche_discovery_agent.py usa parent.parent
- [x] Delays adaptativos implementados
- [x] Rate limit 429 detectado y pausado 60s
- [x] Import errors no causan spam de reintentos
- [x] Logs informativos con rutas de archivos
- [ ] Tests del supervisor (TODO)
- [ ] Integración con sistema de notificaciones Telegram (TODO)

---

## 🎯 Próximos Pasos

1. **Agregar fallback automático de modelos**
   - Si Groq rate limit → cambiar a Gemini automáticamente
   - Si Gemini falla → cambiar a DeepSeek
   - Configuración en `~/Documents/d8_data/llm_fallbacks.json`

2. **Dashboard del supervisor**
   - Web UI en Flask (puerto 7002)
   - Ver estado de componentes en tiempo real
   - Botones para start/stop manual

3. **Tests del supervisor**
   - Test de inicio/stop de componentes
   - Test de detección de rate limits
   - Test de reintentos con delays adaptativos

---

**Última actualización:** 2025-11-21  
**Autor:** GitHub Copilot + Usuario  
**Estado:** ✅ Fixes aplicados y validados
