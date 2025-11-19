# 🔌 Guía de Integración con Complementos de LLM

> **Cómo alimentar GitHub Copilot, Gemini Gems, Claude Projects con conocimiento de D8**

---

## 🎯 Objetivo

Hacer que los LLMs asistentes (Copilot, Claude, Gemini) tengan acceso al conocimiento acumulado de D8 para:
- ✅ Sugerir patrones ya probados
- ✅ Evitar errores documentados
- ✅ Mantener consistencia arquitectónica
- ✅ Documentar automáticamente nuevas experiencias

---

## 📋 Contenido a Incluir

### Conocimiento Esencial (Siempre)

1. **Contexto del Proyecto**
   - `docs/01_arquitectura/sistema_completo.md` (arquitectura de 3 sistemas)
   - `.github/copilot-instructions.md` (instrucciones básicas)

2. **Memoria Genérica**
   - `docs/06_knowledge_base/memoria/README.md` (índice de patrones)
   - `docs/06_knowledge_base/memoria/patrones_arquitectura.md`
   - `docs/06_knowledge_base/memoria/mejores_practicas.md`

3. **Experiencia D8**
   - `docs/experiencias_profundas/README.md` (índice)
   - `docs/experiencias_profundas/congreso_autonomo.md`
   - `docs/experiencias_profundas/EXPERIENCIAS_BASE.md`

### Conocimiento Avanzado (Opcional)

- Experiencias específicas según componente
- Errores comunes documentados
- Técnicas de optimización

---

## 🔧 GitHub Copilot

### Método 1: Custom Instructions (Workspace)

**Ubicación:** `.github/copilot-instructions.md`

**Ya configurado:** ✅ Este archivo existe y Copilot lo lee automáticamente

**Contenido actual:**
- Overview del proyecto
- Sistema de memoria/experiencia
- Reglas de desarrollo
- Patrones clave

### Método 2: Copilot Chat Context

En Copilot Chat, usar comandos para incluir archivos:

```
@workspace /explain usando el contexto de:
- docs/memoria/patrones_arquitectura.md
- docs/experiencias_profundas/congreso_autonomo.md

¿Cómo implemento un nuevo worker distribuido?
```

### Método 3: Workspace Instructions

**Archivo:** `.vscode/settings.json`

```json
{
  "github.copilot.chat.codeGeneration.instructions": [
    {
      "text": "Consulta docs/memoria/ antes de sugerir arquitectura"
    },
    {
      "text": "Documenta decisiones en docs/experiencias_profundas/"
    },
    {
      "text": "Usa pathlib.Path para paths cross-platform"
    }
  ]
}
```

---

## 💎 Gemini Gems

### Crear Gem "D8 Expert"

**Paso 1: Crear el Gem**

1. Ve a: https://gemini.google.com/gems
2. Click "Create Gem"
3. Nombre: `D8 Expert`

**Paso 2: Configurar Instrucciones**

```
You are an expert in the D8 autonomous AI system.

ARCHITECTURE:
D8 has 3 independent systems:
1. Evolutionary System (Darwin) - Natural selection via genetic algorithms
2. Niche Discovery - Automated market analysis
3. Autonomous Congress - Self-improvement through research & experimentation

KNOWLEDGE SYSTEM:
- Generic Memory (docs/memoria/): Reusable patterns for any project
- D8 Experience (docs/experiencias_profundas/): D8-specific lessons

RULES:
1. Consult memory before suggesting solutions
2. Update experiences after significant changes
3. Promote generalizable experiences to memory
4. Always use pathlib.Path for cross-platform compatibility
5. Maintain system autonomy - no human intervention

KEY PATTERNS:
- Configuration: .env for secrets, JSON in ~/Documents/ for configs
- Distributed: Orchestrator + Workers with heartbeat monitoring
- Validation: Pydantic schemas for API inputs

When asked about architecture, reference:
- Dual configuration pattern for secrets management
- Worker heartbeat for distributed resilience
- Orchestrator pattern for task distribution

When implementing, always:
- Check if pattern exists in docs/memoria/
- Document new decisions in docs/experiencias_profundas/
- Consider if experience should be promoted to memory
```

**Paso 3: Agregar Knowledge Base**

Subir archivos como contexto:
- `docs/01_arquitectura/sistema_completo.md`
- `docs/06_knowledge_base/memoria/README.md`
- `docs/06_knowledge_base/experiencias_profundas/README.md`

**Paso 4: Usar el Gem**

```
@D8Expert ¿Cómo implemento un nuevo tipo de worker?
```

---

## 🤖 Claude Projects

### Crear Project "D8"

**Paso 1: Configurar Project**

1. Click "Projects" en Claude
2. "New Project" → Nombre: `D8`

**Paso 2: Agregar Custom Instructions**

```markdown
# D8 Autonomous AI System

You're working on D8, a fully autonomous AI system with 3 independent subsystems.

## Before suggesting code:
1. Check if pattern exists in memoria/ (generic patterns)
2. Review similar decisions in experiencias_profundas/ (D8-specific)
3. Ensure solution maintains system autonomy

## Key principles:
- Zero human intervention after setup
- Consult memory before implementing
- Document experiences after changes
- Use pathlib.Path for cross-platform paths
- Validate inputs with Pydantic schemas

## Architecture patterns to use:
- Dual config: .env (secrets) + ~/Documents/ (functional config)
- Worker heartbeat for distributed systems
- Orchestrator for task coordination

## After implementing:
1. Update experiencias_profundas/ with decision and result
2. If generalizable, add to memoria/
3. Update relevant README.md indices
```

**Paso 3: Agregar Project Knowledge**

Subir carpetas completas:
- `docs/memoria/` (todos los archivos)
- `docs/experiencias_profundas/` (todos los archivos)
- `docs/ARQUITECTURA_D8.md`
- `docs/SISTEMA_MEMORIA_EXPERIENCIA.md`

**Paso 4: Trabajar en el Project**

Todos los chats dentro del project tendrán contexto automático.

```
¿Cómo manejo rate limits de APIs externas?

[Claude consulta memoria/tecnicas_optimizacion.md]
[Claude sugiere: backoff exponencial + queue]
```

---

## 🔄 Flujo de Trabajo Recomendado

### Al Iniciar Sesión

```
1. Abrir proyecto en IDE
2. Activar Copilot / Abrir Claude Project / Usar Gemini Gem
3. Verificar que LLM tenga contexto:
   
   Pregunta de prueba:
   "¿Cuál es el patrón de configuración usado en D8?"
   
   Respuesta esperada:
   "Dual: .env para secretos, JSON en ~/Documents/ para configs"
```

### Durante Desarrollo

```
ANTES de implementar:
→ Preguntar al LLM: "¿Hay un patrón en memoria/ para [problema]?"
→ Si existe: Usar ese patrón
→ Si no existe: Implementar y documentar

DESPUÉS de implementar:
→ Documentar en experiencias_profundas/[componente].md
→ Evaluar si es generalizable
→ Si sí: Promover a memoria/
→ Actualizar índices README.md
```

### Al Terminar Feature

```
1. Asegurar que experiencia esté documentada
2. Actualizar docs/experiencias_profundas/README.md
3. Si hay patrón nuevo: Agregarlo a docs/memoria/
4. Commit con referencia a experiencia:
   
   git commit -m "feat: nuevo worker
   
   Ver experiencias_profundas/worker_redis.md"
```

---

## 🎯 Ejemplos de Uso

### Ejemplo 1: Implementar Nuevo Worker

**Pregunta:**
```
¿Cómo implemento un worker para Redis?
```

**LLM con contexto responde:**
```
Según memoria/patrones_arquitectura.md#worker-heartbeat:

1. Registrarse con orchestrator:
   POST /api/workers/register
   
2. Implementar heartbeat loop:
   Thread daemon que envía POST /heartbeat cada 30s
   
3. Poll por tareas:
   GET /api/workers/{id}/poll cada 5s
   
4. Reportar resultados:
   POST /api/tasks/{task_id}/result

Código base en app/distributed/worker_groq.py
```

### Ejemplo 2: Debugging

**Pregunta:**
```
Tengo un error 429 con API externa
```

**LLM con contexto responde:**
```
Según experiencias_profundas/error_429_gemini.md:

Error 429 = rate limiting

Soluciones probadas:
1. Verificar rate limits del proveedor
2. Implementar backoff exponencial
3. Considerar cambiar de proveedor (Gemini 15/min → Groq 30/min)

Ver memoria/tecnicas_optimizacion.md#rate-limiting para implementación.
```

### Ejemplo 3: Nueva Funcionalidad

**Pregunta:**
```
Quiero agregar sistema de caché
```

**LLM con contexto responde:**
```
Antes de implementar:

1. ¿Hay patrón en memoria/?
   → No encontrado
   
2. Implementa según principios D8:
   - Debe ser autónomo (invalidación automática)
   - Cross-platform (usar pathlib)
   - Validar inputs (Pydantic)

3. Después de implementar:
   - Documentar en experiencias_profundas/cache_system.md
   - Si es reutilizable: Promover a memoria/patrones_arquitectura.md
```

---

## 📊 Verificación de Integración

### Checklist

✅ **Copilot:**
- [ ] `.github/copilot-instructions.md` existe
- [ ] Copilot sugiere patrones de memoria
- [ ] Copilot menciona experiencias previas

✅ **Gemini:**
- [ ] Gem "D8 Expert" creado
- [ ] Knowledge base cargada
- [ ] Responde con contexto D8

✅ **Claude:**
- [ ] Project "D8" creado
- [ ] Custom instructions configuradas
- [ ] Archivos de docs/ subidos

### Test de Integración

Hacer estas preguntas y verificar respuestas correctas:

1. "¿Cuál es el patrón de configuración en D8?"
   ✅ Esperado: Dual (.env + ~/Documents/)

2. "¿Cómo funciona el congreso autónomo?"
   ✅ Esperado: 5 agentes, ciclo Research → Implement

3. "¿Qué hacer antes de implementar código?"
   ✅ Esperado: Consultar memoria/

---

## 🔮 Futuro: Auto-Documentación

### El Congreso Puede:

1. **Analizar commits**
   ```python
   def analyze_recent_commits():
       # Extraer decisiones de commits
       # Sugerir documentación en experiencias_profundas/
   ```

2. **Promover automáticamente**
   ```python
   def evaluate_promotion(experience):
       if is_generalizable(experience):
           promote_to_memory(experience)
   ```

3. **Mantener índices**
   ```python
   def update_indices():
       # Auto-actualizar README.md files
       # Mantener estadísticas
   ```

---

## 📚 Referencias

- [Sistema de Memoria y Experiencia](../SISTEMA_MEMORIA_EXPERIENCIA.md)
- [GitHub Copilot Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot)
- [Gemini Gems Guide](https://support.google.com/gemini/answer/14244384)
- [Claude Projects](https://www.anthropic.com/claude)

---

**Última actualización:** 2025-11-19  
**Mantenido por:** Sistema D8
