# 📚 D8 Documentation Hub

**Sistema de IA Completamente Autónomo** - Índice Maestro de Documentación

> **Última actualización:** 2025-11-19  
> **Versión del sistema:** 1.0  
> **Principio fundamental:** Cero intervención humana

---

## 🎯 Inicio Rápido

**¿Primera vez con D8?** Sigue este orden:

1. 📖 Lee [`../LEER_PRIMERO.md`](../LEER_PRIMERO.md) (raíz del proyecto)
2. 🏗️ Revisa [Arquitectura Principal](01_arquitectura/sistema_completo.md)
3. ⚙️ Configura el sistema: [Setup Guide](02_setup/README.md)
4. 🚀 Ejecuta tu primer componente: [Operaciones](03_operaciones/README.md)

---

## 📂 Estructura de Documentación

### 01. 🏗️ [Arquitectura](01_arquitectura/)
**Diseño del sistema, componentes principales y flujos**

- [Sistema Completo](01_arquitectura/sistema_completo.md) - Visión holística de D8
- [Sistema Evolutivo](01_arquitectura/evolutivo.md) - Darwin y selección natural
- [Congreso Autónomo](01_arquitectura/congreso.md) - Mejora continua
- [Sistema Distribuido](01_arquitectura/distribuido.md) - Orchestrator + Workers
- [Integraciones LLM](01_arquitectura/integraciones_llm.md) - Groq, Gemini, DeepSeek

### 02. ⚙️ [Setup y Configuración](02_setup/)
**Instalación, configuración inicial y despliegue**

- [Setup Groq Worker](02_setup/groq_worker.md) - Configuración workers Groq
- [Raspberry Pi Setup](02_setup/raspberry_pi.md) - Despliegue en edge devices
- [D8 Genesis Module](02_setup/genesis_module.md) - Módulo de generación
- [Genesis Quickstart](02_setup/genesis_quickstart.md) - Inicio rápido Genesis

### 03. 🚀 [Operaciones](03_operaciones/)
**Guías de uso diario y ejecución de componentes**

- [Guía de Inicio](03_operaciones/inicio.md) - Cómo ejecutar D8
- [Congreso Autónomo](03_operaciones/congreso_autonomo.md) - Ejecutar mejora continua
- [Niche Discovery](03_operaciones/niche_discovery.md) - Descubrir nichos
- [Sistema Evolutivo](03_operaciones/evolutivo.md) - Ejecutar evolución
- [Estrategia de Monetización](03_operaciones/monetizacion.md) - Monetizar nichos

### 04. 🛠️ [Desarrollo](04_desarrollo/)
**Testing, contribución y mejores prácticas para developers**

- [Testing Guide](04_desarrollo/testing.md) - Ejecutar y escribir tests
- [Contributing Guide](04_desarrollo/CONTRIBUTING.md) - Cómo contribuir
- [Código de Estándares](04_desarrollo/standards.md) - Convenciones del proyecto

### 05. 🚨 [Troubleshooting](05_troubleshooting/)
**Solución de problemas comunes y debugging**

- [Solución 429 Errors](05_troubleshooting/error_429.md) - Rate limits de APIs
- [Errores Comunes](05_troubleshooting/common_errors.md) - FAQ de errores
- [Debug Guide](05_troubleshooting/debug_guide.md) - Cómo debuggear D8

### 06. 🧠 [Knowledge Base](06_knowledge_base/)
**Memoria acumulativa del sistema (CRÍTICO para agentes IA)**

#### 💭 [Memoria](06_knowledge_base/memoria/)
Patrones genéricos reutilizables en cualquier proyecto

- [Patrones de Arquitectura](06_knowledge_base/memoria/patrones_arquitectura.md)
- [Mejores Prácticas](06_knowledge_base/memoria/mejores_practicas.md)

#### 🧠 [Experiencias Profundas](06_knowledge_base/experiencias_profundas/)
Conocimiento específico acumulado de D8

- [Congreso Autónomo](06_knowledge_base/experiencias_profundas/congreso_autonomo.md)
- [Experiencias Base](06_knowledge_base/experiencias_profundas/EXPERIENCIAS_BASE.md)

**📌 Obligatorio para agentes IA:** Consultar Knowledge Base antes de modificar D8

### 07. 📊 [Reportes](07_reportes/)
**Resultados de tests, experimentos y snapshots del sistema**

- [Resultados de Tests](07_reportes/resultados_tests.md) - Tests automatizados
- [Estado del Sistema](07_reportes/estado_sistema.txt) - Snapshot actual
- [Experimentos del Congreso](07_reportes/experimentos_congreso/) - Resultados de ciclos

---

## 🔍 Navegación Rápida por Tema

### Para Nuevos Usuarios
1. [LEER_PRIMERO.md](../LEER_PRIMERO.md) (obligatorio)
2. [Sistema Completo](01_arquitectura/sistema_completo.md)
3. [Setup Guide](02_setup/README.md)

### Para Desarrolladores
1. [Contributing Guide](04_desarrollo/CONTRIBUTING.md)
2. [Testing Guide](04_desarrollo/testing.md)
3. [Knowledge Base](06_knowledge_base/)

### Para Agentes IA
1. [Sistema de Memoria y Experiencia](06_knowledge_base/README.md)
2. [Experiencias Base](06_knowledge_base/experiencias_profundas/EXPERIENCIAS_BASE.md)
3. [Patrones de Arquitectura](06_knowledge_base/memoria/patrones_arquitectura.md)

### Para Troubleshooting
1. [Errores Comunes](05_troubleshooting/common_errors.md)
2. [Solución 429](05_troubleshooting/error_429.md)
3. [Debug Guide](05_troubleshooting/debug_guide.md)

---

## 📋 Cómo Agregar Nueva Documentación

**Sigue estas reglas al crear nuevos documentos:**

1. **Identifica la categoría correcta:**
   - ¿Diseño del sistema? → `01_arquitectura/`
   - ¿Configuración o instalación? → `02_setup/`
   - ¿Cómo usar algo? → `03_operaciones/`
   - ¿Testing o desarrollo? → `04_desarrollo/`
   - ¿Solución de error? → `05_troubleshooting/`
   - ¿Conocimiento acumulativo? → `06_knowledge_base/`
   - ¿Resultados de tests? → `07_reportes/`

2. **Usa nombres descriptivos en snake_case:**
   - ✅ `distributed_architecture.md`
   - ❌ `DIST-ARCH.md`

3. **Actualiza el README.md de la categoría:**
   - Cada carpeta tiene su propio README.md
   - Agrega un link con descripción breve

4. **Si no es markdown, considera si debe estar en docs:**
   - Scripts → `scripts/` (no en `docs/`)
   - Logs → `data/logs/` (no en `docs/`)
   - Configs → `config/` (no en `docs/`)

5. **Consulta [CONTRIBUTING.md](04_desarrollo/CONTRIBUTING.md) para detalles**

---

## 🎯 Principios de Organización

### Numeración de Carpetas
Las carpetas están numeradas para forzar un orden lógico:
1. Entender arquitectura primero
2. Luego configurar
3. Después operar
4. Desarrollar con conocimiento
5. Troubleshoot cuando falle
6. Consultar knowledge base siempre
7. Revisar reportes para métricas

### Coherencia con Scripts
La estructura de `scripts/` refleja la de `docs/`:
- `scripts/setup/` ↔️ `docs/02_setup/`
- `scripts/tests/` ↔️ `docs/04_desarrollo/`
- `scripts/launch/` ↔️ `docs/03_operaciones/`

### Jerarquía de READMEs
- **docs/README.md** (este archivo) - Índice maestro
- **docs/XX_categoria/README.md** - Resumen de la categoría
- **docs/XX_categoria/archivo.md** - Documento específico

---

## 📞 Contacto y Contribuciones

**Repositorio:** [github.com/lsilva5455/d8](https://github.com/lsilva5455/d8)  
**Autor:** lsilva5455  
**Licencia:** MIT

Para contribuir, lee [CONTRIBUTING.md](04_desarrollo/CONTRIBUTING.md)

---

**🤖 Hecho por D8 - Sistema de IA Autónomo**
