# 💭 MEMORIA - Conocimiento Genérico Reutilizable

> **Patrones, técnicas y soluciones aplicables a cualquier proyecto**

---

## 🎯 Qué es la Memoria

La **Memoria** contiene conocimiento **generalizable** extraído de experiencias exitosas en D8 que puede aplicarse a otros proyectos.

**Criterios de inclusión:**
- ✅ Independiente de D8
- ✅ Probado en producción
- ✅ Bien documentado
- ✅ Reutilizable sin modificaciones mayores

---

## 📚 Índice de Patrones

### 🏗️ Arquitectura

#### [Configuración Dual: .env + JSON](patrones_arquitectura.md#configuracion-dual)
Separar secretos (.env) de configuraciones (JSON en ~/Documents/)
- **Tags:** #configuration #security #dx
- **Cuándo usar:** Proyectos con múltiples entornos y usuarios

#### [Worker Distribuido con Heartbeat](patrones_arquitectura.md#worker-heartbeat)
Sistema de workers con monitoreo de vida
- **Tags:** #distributed #monitoring #resilience
- **Cuándo usar:** Procesamiento distribuido con alta disponibilidad

#### [Orchestrator Pattern](patrones_arquitectura.md#orchestrator)
Coordinación centralizada de múltiples workers
- **Tags:** #distributed #coordination #scalability
- **Cuándo usar:** Sistemas con múltiples procesadores

#### [Separación app/ + lib/](patrones_arquitectura.md#separacion-app-lib)
Estructura para separar lógica de negocio de utilities reutilizables
- **Tags:** #arquitectura #organizacion #reutilizacion
- **Cuándo usar:** Proyectos que necesitan código portable y claro

---

### ⚡ Performance y Optimización

#### [Rate Limiting con Backoff Exponencial](tecnicas_optimizacion.md#rate-limiting)
Manejo inteligente de límites de API
- **Tags:** #performance #api #resilience
- **Cuándo usar:** Integración con APIs externas

#### [Lazy Loading de Configuración](tecnicas_optimizacion.md#lazy-loading)
Cargar configs solo cuando se necesitan
- **Tags:** #performance #memory
- **Cuándo usar:** Apps con muchas configuraciones opcionales

---

### 🛡️ Mejores Prácticas

#### [Validación de Entradas con Schemas](mejores_practicas.md#validacion-schemas)
Validar datos con Pydantic/JSON Schema
- **Tags:** #validation #reliability #dx
- **Cuándo usar:** APIs con datos complejos

#### [Logging Estructurado](mejores_practicas.md#logging-estructurado)
Logs en JSON para mejor análisis
- **Tags:** #observability #debugging
- **Cuándo usar:** Sistemas en producción

#### [Path Handling Cross-Platform](mejores_practicas.md#path-handling)
Usar pathlib para compatibilidad Windows/Linux
- **Tags:** #compatibility #portability
- **Cuándo usar:** Aplicaciones multiplataforma

---

### 🐛 Errores Comunes y Soluciones

#### [Error 429: Too Many Requests](errores_comunes.md#error-429)
Soluciones para rate limiting
- **Problema:** APIs rechazan requests
- **Solución:** Backoff exponencial + queue

#### [Environment Variables Not Found](errores_comunes.md#env-not-found)
Variables de entorno no cargadas
- **Problema:** .env no se lee correctamente
- **Solución:** python-dotenv + validación temprana

#### [JSON Decode Error](errores_comunes.md#json-decode)
Responses no JSON de LLMs
- **Problema:** LLM retorna texto en vez de JSON
- **Solución:** Prompts explícitos + fallback parsing

---

## 🔍 Búsqueda por Tag

### Por Categoría
```bash
# Arquitectura
grep -r "#arquitectura" docs/memoria/

# Performance  
grep -r "#performance" docs/memoria/

# Seguridad
grep -r "#security" docs/memoria/
```

### Por Tecnología
```bash
# Python
grep -r "#python" docs/memoria/

# APIs
grep -r "#api" docs/memoria/

# Distributed Systems
grep -r "#distributed" docs/memoria/
```

---

## ➕ Cómo Agregar Nueva Memoria

### 1. Verificar que sea generalizable
- ¿Funciona fuera de D8?
- ¿Está probado en producción?
- ¿Es autocontenido?

### 2. Usar el template
```markdown
# [NOMBRE_DEL_PATRÓN]

## Contexto
¿Cuándo surge?

## Problema
¿Qué necesidad resuelve?

## Solución
Implementación concreta

## Ejemplo
```python
# Código real
```

## Resultado
Qué se logra

## Tags
#tag1 #tag2 #tag3
```

### 3. Agregar al índice
Actualizar este README.md con el nuevo patrón

### 4. Referenciar desde experiencia
Agregar link desde `experiencias_profundas/` si aplica

---

## 📊 Estadísticas

| Categoría | Patrones | Última Actualización |
|-----------|----------|---------------------|
| Arquitectura | 3 | 2025-11-19 |
| Performance | 2 | 2025-11-19 |
| Mejores Prácticas | 3 | 2025-11-19 |
| Errores Comunes | 3 | 2025-11-19 |
| **TOTAL** | **11** | **2025-11-19** |

---

## 🔗 Referencias Externas

### Recursos Recomendados
- [Python Design Patterns](https://refactoring.guru/design-patterns/python)
- [Distributed Systems Patterns](https://www.microsoft.com/en-us/research/publication/patterns-distributed-systems/)
- [API Design Best Practices](https://swagger.io/resources/articles/best-practices-in-api-design/)

### Libros
- "Design Patterns" - Gang of Four
- "Building Microservices" - Sam Newman
- "Site Reliability Engineering" - Google

---

**Mantenido por:** Sistema D8 + Congreso Autónomo  
**Última revisión:** 2025-11-19  
**Próxima revisión:** Automática por Congreso
