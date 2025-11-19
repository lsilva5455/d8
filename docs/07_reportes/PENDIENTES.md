# 📋 TAREAS PENDIENTES - D8

**Última actualización:** 19 Noviembre 2025

---

## Estado General

| Prioridad | Cantidad | Estado |
|-----------|----------|--------|
| 🔴 Alta | 1 | Pendiente |
| 🟡 Media | 0 | - |
| 🟢 Baja | 0 | - |

---

## [PENDIENTE] Groq llama-3.3 no devuelve JSON consistentemente

**Fecha de registro:** 2025-11-19  
**Prioridad:** 🔴 Alta  
**Estado:** Pendiente  
**Reportado por:** Usuario (día de mañana lo necesitará)

### Contexto

Durante la implementación del sistema de segmentación geográfica para niche discovery, se detectó que **Groq llama-3.3-70b-versatile NO devuelve JSON puro** como se esperaba.

**Síntomas originales:**
- Respuestas envueltas en texto explicativo antes/después del JSON
- Resultados con `"niche_name": "Unknown"` y `"confidence": 0`
- 100% de fallos en 8 mercados probados (USA, España, Chile)

**Error actual (Rate Limit - 2025-11-19):**
Al intentar ejecutar el sistema completo, se alcanzó el límite de tokens diarios de Groq:

```json
{
  "error": "Error code: 429 - {'error': {'message': 'Rate limit reached for model `llama-3.3-70b-versatile` in organization `org_01k7xj7tz7efgbawsh0vkhcgr4` service tier `on_demand` on tokens per day (TPD): Limit 100000, Used 99384, Requested 760. Please try again in 2m4.416s. Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing', 'type': 'tokens', 'code': 'rate_limit_exceeded'}}"
}
```

**Límites actuales (tier gratuito):**
- **Límite:** 100,000 tokens por día (TPD)
- **Usado:** 99,384 tokens
- **Restante:** 616 tokens
- **Estado:** 99.4% consumido

**Decisión tomada:**
Se implementó **Gemini Flash 2.0** como solución temporal porque tiene `response_mime_type="application/json"` garantizado. Sin embargo, el usuario quiere **resolver el problema con Groq** para uso futuro.

### Problema

**Problema 1: JSON inconsistente**  
**Groq llama-3.3-70b-versatile no soporta `response_format={"type": "json_object"}`** como otros modelos (GPT-4, Claude, Gemini).

**Intentos fallidos:**
1. ✅ **Reducción de temperatura** (0.7 → 0.3): Mejoró determinismo pero NO forzó JSON puro
2. ✅ **Simplificación de prompt**: "OUTPUT ONLY JSON, NO TEXT BEFORE OR AFTER" → Ignorado
3. ✅ **Extracción agresiva con regex**: Funciona para encontrar JSON pero datos son `"Unknown"`
4. ❌ **llama-3.1-70b-versatile**: Modelo deprecado (HTTP 400)

**Evidencia:**
```python
# Respuesta típica de llama-3.3
"Here's the JSON analysis you requested:

{
  \"niche_name\": \"Unknown\",
  \"confidence\": 0,
  ...
}

This analysis considers the Chilean market specifically."
```

---

**Problema 2: Rate Limit alcanzado (Error 429)**  
El tier gratuito de Groq tiene un límite de **100,000 tokens por día**, que se agota rápidamente con pruebas exhaustivas.

**Impacto:**
- ❌ Sistema no puede ejecutar análisis de 8 mercados completos
- ❌ Cada request de niche discovery usa ~760-804 tokens
- ❌ Bloqueo de 2+ minutos entre requests cuando se alcanza el límite
- ❌ Desarrollo e iteración extremadamente lentos

**Cálculo:**
- 8 mercados × ~780 tokens/mercado = **6,240 tokens por ejecución**
- 100,000 tokens / 6,240 = **~16 ejecuciones completas al día**
- Con testing e iteración: límite se alcanza en 2-3 horas de trabajo

**Solución inmediata:**  
⭐ **Upgrade a Dev Tier en Groq:**
- Link: https://console.groq.com/settings/billing
- Costo estimado: Variable según plan
- Elimina el bloqueo de desarrollo

**Solución alternativa:**  
Usar Gemini (ya integrado) que tiene límites más generosos en tier gratuito:
- **1,500 requests/día** vs 100K tokens/día de Groq
- Menos restrictivo para desarrollo

### Opciones de Solución

#### **⭐ Opción 0: Upgrade Groq Dev Tier (SOLUCIÓN INMEDIATA AL RATE LIMIT)**

**Descripción:** Comprar plan de pago en Groq para eliminar límite de 100K tokens/día.

**Implementación:**
1. Ir a: https://console.groq.com/settings/billing
2. Elegir plan Dev Tier o superior
3. Configurar método de pago
4. Límites se actualizan automáticamente

**Planes disponibles (verificar precios actuales):**
- **Free:** 100K tokens/día (actual)
- **Dev Tier:** Límites más altos + prioridad
- **Production:** Sin límites de quota

**Pros:**
- ✅ Solución inmediata al error 429
- ✅ Permite desarrollo e iteración sin interrupciones
- ✅ No requiere cambios en código
- ✅ Mantiene velocidad de Groq (más rápido que Gemini)

**Contras:**
- ❌ Costo mensual recurrente
- ❌ No resuelve el problema de JSON inconsistente (Problema 1)

**Esfuerzo estimado:** 10 minutos (solo configuración de billing)

**⚠️ IMPORTANTE:** Esta opción solo resuelve el rate limit (Error 429). El problema de JSON inconsistente persiste y requiere una de las opciones A-E abajo.

---

#### **Opción A: Prompt Engineering Avanzado**

**Descripción:** Usar técnicas más agresivas de prompt engineering específicas para Groq.

**Estrategia:**
1. **System message explícito**:
   ```python
   messages = [
       {
           "role": "system",
           "content": "You are a JSON API. You ONLY output valid JSON. Never add explanations."
       },
       {
           "role": "user",
           "content": prompt
       }
   ]
   ```

2. **Few-shot examples**:
   ```python
   prompt = """Previous examples:
   
   INPUT: Analyze market X
   OUTPUT: {"niche_name": "AI Writing Tools", "confidence": 85, ...}
   
   INPUT: Analyze market Y
   OUTPUT: {"niche_name": "Eco Products", "confidence": 72, ...}
   
   Now analyze: [tu prompt actual]
   OUTPUT:"""
   ```

3. **JSON schema en prompt**:
   ```python
   prompt = f"""Respond with ONLY this exact JSON structure:
   {{
     "niche_name": "string (specific niche name, NOT 'Unknown')",
     "confidence": number (0-100),
     ...
   }}
   
   Market: {market_info}
   
   JSON:"""
   ```

**Pros:**
- ✅ No requiere cambios en infraestructura
- ✅ Mantiene uso de Groq (más rápido que Gemini)
- ✅ Sin costo adicional

**Contras:**
- ❌ No garantiza JSON puro (Groq no tiene modo JSON nativo)
- ❌ Puede requerir múltiples iteraciones de prueba
- ❌ Frágil (cambios en modelo pueden romperlo)

**Esfuerzo estimado:** 2-4 horas de experimentación

---

#### **Opción B: Modelo alternativo de Groq**

**Descripción:** Probar otros modelos de Groq que podrían tener mejor adherencia a JSON.

**Modelos a probar:**
1. **mixtral-8x7b-32768**: Mixtral suele ser mejor con estructuras
2. **llama-3.2-90b-text-preview**: Preview models a veces tienen mejores capacidades
3. **gemma2-9b-it**: Más pequeño pero potencialmente más obediente

**Implementación:**
```python
# En base_agent.py
model_options = [
    "mixtral-8x7b-32768",
    "llama-3.2-90b-text-preview",
    "gemma2-9b-it"
]

for model in model_options:
    response = groq_client.chat.completions.create(
        model=model,
        messages=[...],
        temperature=0.2
    )
    # Test si devuelve JSON limpio
```

**Pros:**
- ✅ Mantiene infraestructura Groq
- ✅ Rápido de probar (cambiar parámetro `model`)
- ✅ Mixtral tiene buena reputación con JSON

**Contras:**
- ❌ No garantiza solución (problema puede ser de Groq en general)
- ❌ Modelos más pequeños = potencialmente menor calidad
- ❌ Puede requerir ajustes de temperatura por modelo

**Esfuerzo estimado:** 1-2 horas de testing

---

#### **Opción C: Post-procesamiento inteligente**

**Descripción:** Asumir que Groq SIEMPRE devolverá texto + JSON, crear parser robusto.

**Implementación:**
```python
# lib/parsers/json_extractor.py
import re
import json

class RobustJSONExtractor:
    """Extrae JSON de respuestas de LLM con texto adicional"""
    
    @staticmethod
    def extract(text: str) -> dict:
        """
        Estrategias en cascada:
        1. Parse directo
        2. Buscar entre ``` ``` o ```json ```
        3. Buscar primer { hasta último }
        4. Regex para encontrar objeto JSON más grande
        5. Intentar reparar JSON malformado
        """
        
        # 1. Parse directo
        try:
            return json.loads(text.strip())
        except:
            pass
        
        # 2. Extraer de code blocks
        code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(code_block_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        
        # 3. Primer { hasta último }
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        if first_brace != -1 and last_brace != -1:
            try:
                return json.loads(text[first_brace:last_brace+1])
            except:
                pass
        
        # 4. Regex agresivo
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, text, re.DOTALL)
        for match in reversed(matches):  # Empezar por el más largo
            try:
                return json.loads(match)
            except:
                continue
        
        # 5. Reparación (remover trailing commas, etc.)
        # ... implementar con demjson o similar
        
        raise ValueError("No se pudo extraer JSON válido")

# Uso en base_agent.py
from lib.parsers.json_extractor import RobustJSONExtractor

response = groq_client.chat(...)
result = RobustJSONExtractor.extract(response.content)
```

**Pros:**
- ✅ Solución robusta y definitiva
- ✅ Maneja edge cases automáticamente
- ✅ Reutilizable en todo el proyecto
- ✅ Testeable unitariamente

**Contras:**
- ❌ No soluciona la calidad de datos ("Unknown" puede persistir)
- ❌ Agrega complejidad al código
- ❌ Mantiene dependencia de comportamiento no garantizado de Groq

**Esfuerzo estimado:** 3-4 horas (incluyendo tests)

---

#### **Opción D: Dual-LLM Strategy**

**Descripción:** Usar Groq para generación rápida, Gemini para validación/refinamiento.

**Arquitectura:**
```python
# 1. Groq genera respuesta rápida (barata, rápida)
groq_response = groq_client.chat(prompt)
extracted_json = extract_json_best_effort(groq_response)

# 2. Validar calidad de respuesta
if extracted_json.get("niche_name") == "Unknown" or extracted_json.get("confidence") < 50:
    # 3. Usar Gemini para refinamiento (más cara, mejor calidad)
    gemini_response = gemini_client.generate_json(prompt)
    return gemini_response
else:
    return extracted_json
```

**Pros:**
- ✅ Mejor de ambos mundos: velocidad de Groq + calidad de Gemini
- ✅ Gemini solo se usa cuando es necesario (costo optimizado)
- ✅ Fallback automático
- ✅ Ya tienes ambas integraciones implementadas

**Contras:**
- ❌ Mayor complejidad en lógica de negocio
- ❌ Costos variables (difícil predecir)
- ❌ Latencia adicional en casos de fallback

**Esfuerzo estimado:** 2-3 horas

---

#### **Opción E: Function Calling con Groq**

**Descripción:** Usar feature de "function calling" de Groq para forzar estructura JSON.

**Investigación necesaria:**
- ¿Groq soporta function calling como OpenAI?
- Documentación: https://console.groq.com/docs/function-calling

**Implementación conceptual:**
```python
tools = [{
    "type": "function",
    "function": {
        "name": "report_niche_analysis",
        "description": "Report the niche discovery analysis",
        "parameters": {
            "type": "object",
            "properties": {
                "niche_name": {"type": "string"},
                "confidence": {"type": "number"},
                # ... resto de schema
            },
            "required": ["niche_name", "confidence", ...]
        }
    }
}]

response = groq_client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[...],
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "report_niche_analysis"}}
)

# Extraer de tool_calls
result = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
```

**Pros:**
- ✅ Si funciona, es la solución nativa más robusta
- ✅ Groq garantiza el esquema
- ✅ No requiere Gemini

**Contras:**
- ❌ Requiere investigación (no confirmado si Groq lo soporta bien)
- ❌ Puede tener limitaciones de tokens o modelos soportados
- ❌ Si no funciona, tiempo perdido

**Esfuerzo estimado:** 3-5 horas (incluyendo investigación)

---

### Recomendación del Sistema

**Para resolver Rate Limit (Error 429) HOY:**
- ⭐ **Opción 0** - Upgrade Groq Dev Tier (10 min)

**Para resolver JSON inconsistente (Problema 1) - Orden sugerido:**

1. **Primero: Opción B** (1-2h) - Probar mixtral-8x7b-32768, es rápido y puede resolver el problema
2. **Si falla: Opción A** (2-4h) - Few-shot prompting con ejemplos concretos
3. **Si falla: Opción E** (3-5h) - Investigar function calling (solución potencialmente definitiva)
4. **Si falla: Opción C** (3-4h) - Parser robusto como fallback permanente
5. **Como último recurso: Opción D** - Dual-LLM (ya tienes Gemini funcionando)

**Estrategia recomendada:**
1. ✅ **Corto plazo:** Usar Gemini (ya funciona) para continuar desarrollo
2. ⏳ **Mediano plazo:** Upgrade Groq cuando necesites mayor volumen
3. 🔬 **Largo plazo:** Resolver JSON inconsistente con opciones B→A→E→C

**Criterio de éxito:**
- ✅ Al menos 80% de requests devuelven `niche_name` real (no "Unknown")
- ✅ `confidence` > 0 en respuestas
- ✅ JSON válido sin envoltorios de texto
- ✅ Sin errores 429 durante desarrollo

### Referencias

**Archivos relacionados:**
- `app/agents/base_agent.py` (líneas 117-230) - Lógica actual de parsing
- `scripts/niche_discovery_agent.py` - Script que usa el agent
- `app/integrations/groq_client.py` - Cliente de Groq
- `app/integrations/gemini_client.py` - Cliente de Gemini (solución temporal)
- `docs/06_knowledge_base/experiencias_profundas/segmentacion_geografica.md` - Contexto completo

**Commits relacionados:**
- Implementación de extracción JSON agresiva (2025-11-19)
- Integración de Gemini como solución temporal (2025-11-19)

**Documentación externa:**
- [Groq Function Calling Docs](https://console.groq.com/docs/function-calling)
- [Groq Supported Models](https://console.groq.com/docs/models)

### Notas Adicionales

**Por qué es importante:**
- Usuario necesitará Groq en el futuro para otras tareas
- Gemini tiene límites de quota más estrictos (gratuito: 1500 req/día)
- Groq es más rápido (útil para evolución genética con muchas evaluaciones)

**Contexto adicional:**
- El problema NO afecta la arquitectura del sistema
- Solo afecta la calidad de datos devueltos (JSON) y volumen (rate limit)
- Sistema completo de segmentación geográfica funciona (USA, España, Chile)
- Tablas profesionales, indicadores económicos, estrategia de implementación: TODO OK

**Estado actual:**
- ✅ Sistema funcional con Gemini
- ⏸️ Groq pendiente de optimización
- ⚠️ Rate limit alcanzado (99.4% del límite diario usado)
- ⏰ Se resetea en: 2-3 minutos (según mensaje de error)

**Impacto en desarrollo:**
- **Sin upgrade:** Solo 16 ejecuciones completas/día (muy limitante)
- **Con upgrade:** Desarrollo fluido sin interrupciones
- **Con Gemini:** 1,500 requests/día (suficiente para desarrollo)

**Costos estimados (verificar precios actuales):**
- Groq Free: $0/mes → 100K tokens/día
- Groq Dev: $XX/mes → Límites superiores
- Gemini Free: $0/mes → 1,500 req/día (más generoso para desarrollo)

### Tags

`#groq` `#llm` `#json` `#parsing` `#niche-discovery` `#alta-prioridad` `#investigacion` `#rate-limit` `#error-429` `#billing` `#quota`

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2025-11-19 | Creación del pendiente | Sistema D8 |

---

**Última revisión:** 2025-11-19  
**Próxima revisión sugerida:** Cuando el usuario lo solicite
