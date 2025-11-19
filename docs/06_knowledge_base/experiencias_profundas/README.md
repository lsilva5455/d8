# 🧠 EXPERIENCIAS - Conocimiento Específico de D8

> **Lecciones aprendidas durante el desarrollo de D8**

---

## 🎯 Qué es Experiencia

Las **Experiencias** documentan decisiones, problemas y soluciones específicas del proyecto D8.

**Características:**
- ✅ Específicas de D8
- ✅ Contexto temporal (fechas)
- ✅ Decisiones arquitectónicas
- ✅ Problemas encontrados y soluciones

---

## 📚 Índice de Experiencias

### 🏛️ Arquitectura y Diseño

#### [Congreso Autónomo](congreso_autonomo.md)
Sistema de mejora continua sin intervención humana
- **Fecha:** 2025-11-19
- **Decisión:** 5 agentes especializados en ciclo Research → Test → Implement
- **Resultado:** Mejora automática del sistema

#### [Sistema Evolutivo](sistema_evolutivo.md)
Selección natural de agentes mediante algoritmos genéticos
- **Fecha:** 2025-11-17
- **Decisión:** Mutación 10%, crossover 70%, elite 20%
- **Resultado:** Evolución continua de agentes

#### [Niche Discovery](niche_discovery.md)
Descubrimiento automático de nichos rentables
- **Fecha:** 2025-11-19
- **Decisión:** Agente especializado con genome fijo
- **Resultado:** Análisis de mercados automático

#### [Segmentación Geográfica Multi-Mercado](segmentacion_geografica.md)
Sistema de marketing digital enfocado en 3 mercados: USA, España, Chile
- **Fecha:** 2025-11-19
- **Decisión:** Segmentación en 3 geografías con configuración específica por mercado
- **Resultado:** Análisis multi-geo automático con insights culturales, económicos y de plataforma
- **Tags:** `#geografia` `#marketing` `#usa` `#españa` `#chile` `#localizacion`

---

### 🔧 Configuración y Setup

#### [Migración a Estructura lib/](migracion_lib.md)
Separación de código reutilizable en `lib/` vs lógica de D8 en `app/`
- **Fecha:** 2025-11-19
- **Problema:** LLM clients mezclados con lógica de D8, no reutilizables
- **Solución:** Crear `lib/llm/` con `BaseLLMClient` abstracto y clients concretos
- **Resultado:** ✅ Código reutilizable separado, interface unificada

#### [Consolidación de Configuración en d8_data](consolidacion_config_d8_data.md)
Consolidar configuraciones bajo `~/Documents/d8_data/`
- **Fecha:** 2025-11-19
- **Problema:** Configuraciones dispersas (agentes/, workers/ en ~/Documents/)
- **Solución:** Consolidar bajo `~/Documents/d8_data/` con script de migración
- **Resultado:** ✅ Estructura escalable, 1 sola carpeta, fácil backup

#### [Migración a Configuración Dual](configuracion_dual.md)
De .env monolítico a .env + JSON en ~/Documents/d8_data
- **Fecha:** 2025-11-18
- **Problema:** Secretos en repo, configs no flexibles
- **Solución:** .env para API keys, JSON para configs funcionales
- **Resultado:** ✅ Cero secretos en repo, configs per-user

#### [Worker Groq vs Gemini](worker_comparacion.md)
Cambio de Gemini a Groq por rate limits
- **Fecha:** 2025-11-18
- **Problema:** Gemini 429 errors (15 req/min)
- **Solución:** Worker Groq (30 req/min, 14,400/día)
- **Resultado:** ✅ 100% success rate

---

### 🐛 Problemas y Soluciones

#### [Error 429 con Gemini](error_429_gemini.md)
Rate limiting agresivo de Google AI Studio
- **Problema:** 429 TooManyRequests incluso con 5 requests
- **Diagnóstico:** Gemini free tier es 15 req/min, muy bajo
- **Solución:** Migrar a Groq (2x rate limit)
- **Lección:** Verificar rate limits ANTES de arquitectura

#### [BaseAgent Response Format](baseagent_format.md)
Agentes retornan meta-análisis en vez de resultados directos
- **Problema:** `{"action": "...", "reasoning": "..."}` en vez de JSON específico
- **Causa:** BaseAgent diseñado para sistema evolutivo
- **Solución:** Separar modos: evolutionary vs direct execution
- **Estado:** En progreso

---

### 📊 Metodología

#### [EXPERIENCIAS_BASE.md](EXPERIENCIAS_BASE.md)
Metodología de desarrollo profundo
- **Principios:** Map Before Modify, Sistemas > Disciplina
- **Heurísticas:** Test de Pregunta Obvia, Regla de 3 Capas
- **Checklists:** Debugging sistemático
- **Origen:** Proyecto mapeo_pool

---

## 🔄 Promoción a Memoria

### Candidatos Actuales

✅ **Configuración Dual** → Ya promovido a `memoria/patrones_arquitectura.md`  
✅ **Worker con Heartbeat** → Ya promovido a `memoria/patrones_arquitectura.md`  
✅ **Orchestrator Pattern** → Ya promovido a `memoria/patrones_arquitectura.md`

⏳ **Pendientes de evaluación:**
- Sistema de validación con Groq
- Manejo de rate limits con backoff
- JSON parsing robusto de LLM responses

---

## 📝 Cómo Documentar Nueva Experiencia

### Template

```markdown
# [COMPONENTE/CARACTERÍSTICA]

## Fecha
YYYY-MM-DD

## Contexto D8
Situación específica del proyecto

## Problema
Qué necesitábamos resolver

## Decisión
Qué decidimos y por qué

## Implementación
Dónde está el código (archivos, líneas)

## Resultado
Qué funcionó / qué no

## Métricas
Números concretos si aplican

## Lecciones
Qué aprendimos para el futuro

## Artefactos
- archivo.py (líneas X-Y)
- config.json (parámetro Z)

## Tags
#categoria #tecnologia #tipo
```

### Ejemplo Mínimo

```markdown
# Rate Limiting con Groq

## Fecha
2025-11-19

## Contexto D8
Necesitábamos manejo robusto de rate limits.

## Decisión
Usar rate limits de Groq (30/min) con margin de seguridad.

## Implementación
- app/integrations/groq_client.py (líneas 45-67)
- Implementado throttling con sleep automático

## Resultado
✅ 100% success rate, 0 errores 429

## Lecciones
Implementar throttling desde el inicio, no reactivo.

## Tags
#rate-limiting #groq #api
```

---

## 🔍 Búsqueda

### Por Fecha
```bash
grep -r "## Fecha" docs/experiencias_profundas/
```

### Por Componente
```bash
# Congreso
cat docs/experiencias_profundas/congreso_autonomo.md

# Configuración
grep -l "configuracion" docs/experiencias_profundas/*.md
```

### Por Tag
```bash
grep -r "#arquitectura" docs/experiencias_profundas/
```

---

## 📊 Estadísticas

| Categoría | Experiencias | Última Actualización |
|-----------|-------------|---------------------|
| Arquitectura | 3 | 2025-11-19 |
| Configuración | 2 | 2025-11-18 |
| Problemas | 2 | 2025-11-19 |
| Metodología | 1 | 2025-11-17 |
| **TOTAL** | **8** | **2025-11-19** |

| Promovidas a Memoria | 3 |
| Candidatas | 3 |
| Específicas D8 | 2 |

---

## 🔗 Referencias

- [Sistema de Memoria y Experiencia](../SISTEMA_MEMORIA_EXPERIENCIA.md)
- [Memoria Genérica](../memoria/README.md)
- [Arquitectura D8](../ARQUITECTURA_D8.md)

---

**Mantenido por:** Congreso Autónomo D8  
**Última revisión:** 2025-11-19  
**Próxima revisión:** Automática por Congreso
