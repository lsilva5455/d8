# 🛡️ Sistema Hiper Robusto de Fallback de LLMs

**Fecha de implementación:** 2025-11-21  
**Estado:** ✅ OPERACIONAL  
**Componentes:** 3 archivos nuevos, 2 modificados

---

## 🎯 Objetivo

Crear un sistema **completamente autónomo** que:
1. ✅ **Maneje fallos de IA automáticamente** (rate limit, timeout, etc.)
2. ✅ **Fallback automático** entre providers (Groq → Gemini → DeepSeek)
3. ✅ **Derive al Congreso** cuando todo falla
4. ✅ **No requiera intervención humana**

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    BASE AGENT                           │
│  (act() method)                                         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│            LLM FALLBACK MANAGER (Singleton)             │
│  - Detección inteligente de errores                     │
│  - Cooldowns adaptativos                                │
│  - Health tracking                                      │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
    ┌────────┐    ┌────────┐    ┌──────────┐
    │  GROQ  │    │ GEMINI │    │ DEEPSEEK │
    └────────┘    └────────┘    └──────────┘
         │             │             │
         └─────────────┼─────────────┘
                       │
                 ¿Todo falló?
                       │
                       ▼
              ┌──────────────────┐
              │  CONGRESO        │
              │  AUTÓNOMO        │
              │  (Escalación)    │
              └──────────────────┘
```

---

## 📦 Componentes Implementados

### 1. **LLMFallbackManager** 
**Archivo:** `lib/llm/fallback_manager.py` (750+ líneas)

**Características:**
- ✅ Fallback automático: Groq → Gemini → DeepSeek
- ✅ Detección inteligente de 6 tipos de errores:
  - `RATE_LIMIT` (429) → Cooldown 60s
  - `TIMEOUT` → Cooldown 30s
  - `AUTH` → Marcar provider no disponible
  - `UNAVAILABLE` (503) → Cooldown adaptativo
  - `INVALID_RESPONSE` → Cooldown adaptativo
  - `UNKNOWN` → Backoff exponencial (5s → 80s)
- ✅ Health tracking por provider
- ✅ Persistencia de estado en `~/Documents/d8_data/llm_fallback/fallback_state.json`
- ✅ Historial de errores (últimos 50)
- ✅ Derivación automática al Congreso

**Métodos principales:**
```python
llm_manager.chat(
    messages=[...],
    temperature=0.7,
    max_tokens=2000,
    json_mode=True,
    context="Descripción del contexto"
)
# Returns: (response, provider_used) o (None, "failed")
```

---

### 2. **Singleton Global**
**Archivo:** `app/llm_manager_singleton.py`

**Uso:**
```python
from app.llm_manager_singleton import get_llm_manager

llm_manager = get_llm_manager()
# Instancia única compartida por todo el sistema
```

---

### 3. **BaseAgent Actualizado**
**Archivo:** `app/agents/base_agent.py`

**Cambios:**
- ❌ **Removed:** Dependencia directa de `groq.Groq`
- ✅ **Added:** Usa `LLMFallbackManager` via singleton
- ✅ **Added:** Parámetro `llm_manager` en `__init__`
- ✅ **Added:** Info de provider usado en respuesta: `result["llm_provider"]`
- ✅ **Added:** Detección de escalación al Congreso: `result["escalated_to_congress"]`

**Compatibilidad:**
- Parámetro `groq_api_key` deprecated pero mantenido para no romper código existente
- Se ignora si se pasa, el manager usa las keys del `.env`

---

### 4. **Endpoint de Monitoreo**
**Archivo:** `app/orchestrator_app.py`

**Nuevo endpoint:**
```bash
GET http://localhost:7001/api/llm/health
```

**Response:**
```json
{
  "timestamp": "2025-11-21T10:00:00",
  "total_requests": 123,
  "congress_escalations": 5,
  "providers": {
    "groq": {
      "is_available": true,
      "consecutive_failures": 0,
      "total_requests": 100,
      "total_failures": 5,
      "success_rate": 95.0,
      "in_cooldown": false,
      "last_error_type": null
    },
    "gemini": {...},
    "deepseek": {...}
  },
  "recent_errors": [...]
}
```

---

## 🚀 Uso

### Opción A: Automático (Recomendado)
```python
from app.agents.base_agent import BaseAgent
from app.evolution.darwin import Genome

# Crear genome
genome = Genome(prompt="You are an AI agent...", generation=1)

# Crear agente (usa LLM Manager automáticamente)
agent = BaseAgent(genome=genome)

# Actuar (fallback automático incluido)
result = agent.act(
    input_data={"task": "Analyze market trends"},
    action_type="analyze"
)

# Verificar resultado
if result.get("success") == False and result.get("escalated_to_congress"):
    print("🏛️ Problema derivado al Congreso")
else:
    provider = result.get("llm_provider", "unknown")
    print(f"✅ Completado con {provider}")
```

### Opción B: Uso Directo del Manager
```python
from app.llm_manager_singleton import get_llm_manager

llm_manager = get_llm_manager()

messages = [
    {"role": "system", "content": "You are..."},
    {"role": "user", "content": "Task..."}
]

response, provider = llm_manager.chat(
    messages=messages,
    context="Descripción del contexto"
)

if response is None:
    print("❌ Todos los providers fallaron")
else:
    print(f"✅ Éxito con {provider}")
```

---

## 🧪 Testing

### Script de prueba:
```bash
python scripts/tests/test_llm_fallback.py
```

**Output esperado:**
```
🧪 TEST: Sistema de Fallback Automático de LLMs
===============================================

📝 Creando agente de prueba...
✅ Agente creado: a3b4c5d6

📊 Estado inicial de providers:
   ✅ GROQ: 0.0% éxito
   ✅ GEMINI: 0.0% éxito
   ✅ DEEPSEEK: 0.0% éxito

TEST 1: Request normal
----------------------------------------------------------------------
✅ Request exitoso usando: GROQ

TEST 2: Segundo request
----------------------------------------------------------------------
✅ Request exitoso usando: GEMINI  # ← Fallback automático!

📊 Estado final de providers:
----------------------------------------------------------------------
📈 Total requests: 2
🏛️  Escalaciones al Congreso: 0

✅ GROQ ⏳ EN COOLDOWN
   Requests: 1
   Fallos: 1
   Tasa de éxito: 0.0%
   Último error: rate_limit

✅ GEMINI
   Requests: 1
   Fallos: 0
   Tasa de éxito: 100.0%
```

---

## 🏛️ Derivación al Congreso

### ¿Cuándo se deriva?

1. **Todos los providers fallaron** después de reintentos
2. **Mismo error se repite 5+ veces** (configurable)
3. **10+ fallos totales** en ventana de tiempo

### Archivos generados:

**Directorio:** `~/Documents/d8_data/llm_fallback/`

**Archivos:**
- `congress_escalation_YYYYMMDD_HHMMSS.json` - Detalles de cada escalación
- `fallback_state.json` - Estado persistente del sistema

### Formato de escalación:
```json
{
  "timestamp": "2025-11-21T10:30:00",
  "escalation_number": 1,
  "context": "Agent abc123 - Action: analyze",
  "messages": [...],
  "provider_status": {
    "groq": {
      "is_available": false,
      "consecutive_failures": 5,
      "last_error": "Rate limit reached",
      "error_type": "rate_limit"
    },
    ...
  },
  "error_history": [...],
  "proposal_description": "## 🚨 ESCALACIÓN AUTOMÁTICA..."
}
```

### Propuesta al Congreso:

Si el `ProposalSystem` está disponible, se crea automáticamente:

```python
Propuesta:
  - Título: "🚨 Fallo Crítico LLM - Escalación #1"
  - Categoría: TECHNICAL
  - Prioridad: 1 (CRÍTICA)
  - Tags: ["llm", "infrastructure", "auto-escalation"]
  - Metadata: {providers_failed, error_types, ...}
```

---

## 📊 Configuración

### Variables de entorno (.env):
```bash
# Groq (primario)
GROQ_API_KEY=gsk_xxx

# Gemini (fallback 1)
GEMINI_API_KEY=AIza_xxx

# DeepSeek (fallback 2)
DEEPSEEK_BASE_URL=http://localhost:7100
```

### Configuración avanzada:
```python
from lib.llm import FallbackConfig

config = FallbackConfig(
    provider_priority=["groq", "gemini", "deepseek"],
    max_retries_per_provider=2,  # Reintentos antes de cambiar
    congress_threshold_failures=10,  # Fallos para derivar
    congress_threshold_repeated_error=5,  # Mismo error repetido
    enable_congress_escalation=True  # Habilitar derivación
)
```

---

## 🔍 Monitoreo

### Comando rápido:
```bash
# Ver estado del LLM Manager
curl http://localhost:7001/api/llm/health | jq

# Ver escalaciones recientes
ls -lh ~/Documents/d8_data/llm_fallback/congress_escalation_*.json

# Ver último estado guardado
cat ~/Documents/d8_data/llm_fallback/fallback_state.json | jq
```

### Dashboard (futuro):
- Acceder a `http://localhost:7001/dashboard/llm` (TODO)

---

## 📈 Métricas

| Métrica | Descripción |
|---------|-------------|
| `total_requests` | Total de requests al sistema |
| `congress_escalations` | Cuántas veces se derivó al Congreso |
| `success_rate` | % de éxito por provider |
| `consecutive_failures` | Fallos seguidos (reset al tener éxito) |
| `in_cooldown` | Si provider está en período de espera |

---

## 🎯 Beneficios

✅ **Resiliencia**: Sistema funciona aunque Groq esté en rate limit  
✅ **Autonomía**: Cero intervención humana, deriva al Congreso  
✅ **Visibilidad**: Tracking de salud de cada provider  
✅ **Inteligencia**: Cooldowns adaptativos según tipo de error  
✅ **Persistencia**: Estado guardado entre reinicios  
✅ **Escalabilidad**: Fácil agregar nuevos providers

---

## 🔧 Troubleshooting

### Problema: "Todos los providers fallaron"
**Solución:**
1. Verificar API keys en `.env`
2. Ver endpoint `/api/llm/health` para detalles
3. Revisar archivos de escalación en `~/Documents/d8_data/llm_fallback/`
4. Verificar cooldowns (esperar 60s si rate limit)

### Problema: "Escalaciones frecuentes al Congreso"
**Solución:**
1. Revisar logs del Congreso en `~/Documents/d8_data/logs/congress.log`
2. Verificar propuestas creadas (debería haber 1 por escalación)
3. Ajustar `congress_threshold_failures` en config

### Problema: "Provider siempre en cooldown"
**Solución:**
1. Verificar `consecutive_failures` en health report
2. Si >5, provider se marcó como no disponible
3. Reiniciar sistema para resetear cooldowns
4. Verificar API keys y quotas

---

## 🚀 Próximos Pasos

### Fase 1: Completado ✅
- [x] LLMFallbackManager con detección de errores
- [x] Integración en BaseAgent
- [x] Derivación al Congreso
- [x] Endpoint de monitoreo
- [x] Tests básicos
- [x] Documentación

### Fase 2: Mejoras Futuras
- [ ] Dashboard web para visualizar salud
- [ ] Auto-rotate API keys si múltiples disponibles
- [ ] Cache de respuestas para reducir requests
- [ ] Metrics en Prometheus format
- [ ] Alertas por Telegram cuando hay escalación
- [ ] Auto-resolución de propuestas del Congreso

---

**Última actualización:** 2025-11-21  
**Autor:** GitHub Copilot + Usuario  
**Estado:** ✅ OPERACIONAL - Listo para producción
