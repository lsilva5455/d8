# 🧠 GitHub Copilot Integration - Setup Guide

## 🎯 Propósito

Integrar GitHub Copilot API con el bot de Telegram para darle **inteligencia completa del proyecto D8**.

Con esta integración, el bot puede:
- ✅ Responder preguntas sobre arquitectura del proyecto
- ✅ Explicar código específico
- ✅ Consultar documentación automáticamente
- ✅ Entender contexto completo del repositorio
- ✅ Buscar archivos y snippets de código
- ✅ Dar respuestas contextuales inteligentes

---

## 🚀 Setup (5 minutos)

### 1. Obtener GitHub Personal Access Token

#### Opción A: Desde GitHub.com (Recomendado)

1. Ve a: https://github.com/settings/tokens
2. Click en "Generate new token" → "Generate new token (classic)"
3. Configuración:
   ```
   Note: D8 Telegram Bot
   Expiration: No expiration (o 1 year)
   
   Scopes a marcar:
   ✅ repo (Full control of private repositories)
   ✅ read:org (Read org and team membership)
   ```
4. Click "Generate token"
5. **Copia el token** (solo se muestra una vez)

#### Opción B: Desde CLI (GitHub CLI)

```bash
# Instalar GitHub CLI si no lo tienes
# Windows: winget install GitHub.cli

# Login
gh auth login

# Crear token
gh auth token
```

### 2. Configurar en .env

Edita `c:\Users\PcDos\d8\.env`:

```bash
# GitHub Copilot (for intelligent bot responses with project context)
GITHUB_TOKEN=ghp_tu_token_aqui
```

### 3. Verificar Integración

```powershell
# Lanzar bot
python scripts/launch_congress_telegram.py
```

Deberías ver en los logs:
```
🧠 GitHub Copilot client initialized for lsilva5455/d8
```

Si ves:
```
⚠️  GITHUB_TOKEN not found. Bot will have limited intelligence.
```

→ Verifica que el token esté en `.env`

---

## 💬 Uso en Telegram

### Antes (Sin GitHub Integration)

**Leo:** "¿Qué es el sistema evolutivo Darwin?"

**Bot:** 🤔 No estoy seguro de qué necesitas. Intenta /help

### Después (Con GitHub Integration)

**Leo:** "¿Qué es el sistema evolutivo Darwin?"

**Bot:** 🧠 Consultando con conocimiento del proyecto...

**Bot:** 💡 Darwin es el sistema evolutivo de D8 ubicado en `app/evolution/darwin.py`. 

Implementa algoritmos genéticos para evolucionar agentes:
- **Selección natural**: Los agentes con mejor fitness sobreviven
- **Mutación**: Modifica prompts aleatoriamente (MUTATION_RATE)
- **Crossover**: Combina prompts de padres exitosos
- **Elitismo**: Los mejores 2 agentes siempre pasan a siguiente generación

Usa fitness basado en:
- 60% revenue generado
- 30% efficiency (tokens/resultado)
- 10% satisfaction del usuario

El sistema está integrado con la economía (FASE 2 completada) y distribuye revenue 40/40/20.

---

## 📚 Ejemplos de Preguntas Inteligentes

### Arquitectura

**Leo:** "¿Cuál es la diferencia entre app/ y lib/?"

**Bot:** 💡 `app/` contiene lógica específica de D8 (agents, evolution, congress, economy). `lib/` tiene utilities reutilizables (llm clients, parsers, validation). Pattern: Separación de concerns documentado en `docs/06_knowledge_base/memoria/patrones_arquitectura.md`

### Estado del Proyecto

**Leo:** "¿Qué fases están completadas?"

**Bot:** 💡 Según `PENDIENTES.md`:
- ✅ FASE 1: Economy Mock (34/34 tests)
- ✅ FASE 2: Integration (15/15 tests)
- 🔮 FASE 3: Autonomous System (ready to start)

### Código Específico

**Leo:** "¿Cómo funciona el Congreso Autónomo?"

**Bot:** 💡 El Congreso (`scripts/autonomous_congress.py`) tiene 5 agentes especializados:
1. Researcher - Descubre oportunidades
2. Experimenter - Diseña tests A/B
3. Optimizer - Optimiza parámetros
4. Implementer - Deploya cambios
5. Validator - Aprueba si mejora > 10%

Ejecuta ciclos automáticos cada 1 hora: Research → Design → Execute → Validate → Implement

### Troubleshooting

**Leo:** "¿Por qué falla el bot de Telegram?"

**Bot:** 💡 Posibles causas según documentación:
1. TELEGRAM_TOKEN incorrecto en .env
2. TELEGRAM_CHAT_ID incorrecto (verifica con @userinfobot)
3. No iniciaste conversación con el bot primero
4. Chequea logs en `data/logs/congress_telegram.log`

Ver guía completa: `docs/03_operaciones/telegram_integration.md`

---

## 🔧 Funciones Disponibles

El bot ahora tiene estas capacidades inteligentes:

### `ask_about_project(question)`

Responde preguntas usando contexto completo del proyecto:
- Visión (VISION_COMPLETA_D8.md)
- Roadmap (ROADMAP_7_FASES.md)
- Estado actual (PENDIENTES.md)
- Estructura del código
- Documentación

### `search_code(query)`

Busca código específico en el repositorio:

```python
results = copilot.search_code("BaseAgent")
# Retorna: [
#   {"path": "app/agents/base_agent.py", "name": "base_agent.py"},
#   ...
# ]
```

### `get_file_content(path)`

Obtiene contenido de archivo específico:

```python
content = copilot.get_file_content("app/agents/base_agent.py")
# Retorna: contenido completo del archivo
```

### `get_project_context()`

Contexto completo del proyecto:

```python
context = copilot.get_project_context()
# Retorna: {
#   "structure": {...},
#   "key_files": {...},
#   "documentation": [...],
#   "recent_commits": [...]
# }
```

---

## 🎯 Ventajas

### Antes
- Bot limitado a comandos predefinidos
- No entiende preguntas complejas
- Routing básico por keywords
- No tiene contexto del proyecto

### Después
- Bot entiende arquitectura completa
- Responde preguntas técnicas
- Consulta documentación automáticamente
- Acceso a todo el código del repo
- Respuestas contextuales inteligentes

---

## 🔐 Seguridad

### ✅ Buenas Prácticas

1. **Token en .env**: Nunca commitear el token
2. **Expiration**: Configurar expiración (1 año recomendado)
3. **Scopes mínimos**: Solo `repo` y `read:org`
4. **Regenerar**: Si el token se compromete, regenerarlo inmediatamente

### ⚠️ Importante

El token da acceso de **lectura** al repositorio. No puede:
- ❌ Modificar código
- ❌ Hacer commits
- ❌ Crear/borrar ramas
- ❌ Cambiar settings del repo

Solo puede:
- ✅ Leer archivos
- ✅ Ver estructura
- ✅ Buscar código
- ✅ Ver commits

---

## 🧪 Testing

### Test 1: Verificar Integración

```powershell
python scripts/tests/test_telegram_bot.py
```

Deberías ver:
```
🧠 GitHub Copilot client initialized for lsilva5455/d8
```

### Test 2: Pregunta Inteligente

En Telegram:

**Leo:** "¿Qué hace el Congreso Autónomo?"

**Bot:** 🧠 Consultando con conocimiento del proyecto...

**Bot:** 💡 [Respuesta detallada con contexto]

### Test 3: Buscar Código

En Telegram:

**Leo:** "¿Dónde está el código del sistema evolutivo?"

**Bot:** 💡 El sistema evolutivo está en `app/evolution/darwin.py`. Implementa clase `EvolutionOrchestrator` con métodos de mutación, crossover y selección natural.

---

## 📊 Comparación

| Feature | Sin GitHub Integration | Con GitHub Integration |
|---------|------------------------|------------------------|
| Comandos básicos | ✅ | ✅ |
| Preguntas sobre proyecto | ❌ | ✅ |
| Explicar código | ❌ | ✅ |
| Buscar archivos | ❌ | ✅ |
| Contexto de documentación | ❌ | ✅ |
| Respuestas inteligentes | ❌ | ✅ |
| Entender arquitectura | ❌ | ✅ |

---

## 🔮 Próximos Pasos

Con esta integración, el bot puede evolucionar a:

### FASE 3: Bot Super Inteligente

1. **Análisis de código en tiempo real**
   - Leo pregunta por bug → Bot busca código → Sugiere fix

2. **Generación de documentación**
   - Leo: "Documenta el módulo X" → Bot genera doc completa

3. **Code review automático**
   - Bot revisa commits y notifica issues

4. **Sugerencias proactivas**
   - Bot detecta patterns anti-pattern → Sugiere mejora

---

## 📚 Referencias

### Código
- `app/integrations/github_copilot.py` - Cliente GitHub API
- `app/integrations/telegram_bot.py` - Integración con bot

### Documentación
- [GitHub API Docs](https://docs.github.com/en/rest)
- [Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)

---

**Última actualización:** 2025-11-20  
**Estado:** ✅ Operacional  
**Requiere:** GITHUB_TOKEN en .env
