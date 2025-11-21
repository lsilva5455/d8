# 🤖 D8 - Sistema de IA Completamente Autónomo

**Sistema de inteligencia artificial que evoluciona, descubre nichos y se mejora a sí mismo sin intervención humana.**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-34%2F34%20passing-brightgreen.svg)]()
[![Economy](https://img.shields.io/badge/economy-mock%20ready-blue.svg)]()
[![Status](https://img.shields.io/badge/status-READY%20FASE%202-orange.svg)]()

---

## 🎯 ¿Qué es D8?

D8 es un sistema de IA **completamente autónomo** con tres subsistemas independientes:

1. **🔬 Niche Discovery**: Descubre oportunidades rentables automáticamente
2. **🏛️ Autonomous Congress**: Investiga, experimenta y mejora técnicas
3. **🧬 Darwin Evolution**: Selección natural de mejores agentes

**Principio fundacional:** **Cero intervención humana** después del setup inicial.

---

## 🏗️ Arquitectura

```
┌──────────────────────────────────────┐
│      NICHE DISCOVERY                 │
│  Descubre nichos rentables           │
│  → Análisis de mercado automático    │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│      AUTONOMOUS CONGRESS              │
│  Investiga y experimenta técnicas    │
│  → Research → Experiment → Validate   │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│      DARWIN EVOLUTION                │
│  Selección natural de agentes        │
│  → Mutación → Crossover → Fitness    │
└──────────────────────────────────────┘
```

### Estado Actual

| Componente | Estado | Tests |
|------------|--------|-------|
| Niche Discovery | ✅ Diseñado | - |
| Autonomous Congress | ✅ Operacional | Manual |
| Darwin Evolution | ✅ Operacional | Manual |
| Mock Economy | ✅ Validado | 34/34 ✅ |
| **FASE 2** | ⏳ Pendiente | - |

**Próxima tarea:** Integrar economía mock con sistema autónomo (FASE 2)

---

## 🚀 Quick Start

---

## 🚀 Instalación

### 1. Requisitos

- Python 3.10+
- Groq API Key (gratis: https://console.groq.com/)
- Windows PowerShell o Linux/Mac terminal

### 2. Clonar e Instalar

```bash
git clone https://github.com/lsilva5455/d8.git
cd d8

# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# O en Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar

Crear archivo `.env` en la raíz:
```bash
GROQ_API_KEY=gsk_tu_api_key_aqui
```

**IMPORTANTE**: La configuración de agentes y workers ahora está en:
- `C:\Users\TuUsuario\Documents\d8_data\agentes\config.json`
- `C:\Users\TuUsuario\Documents\d8_data\workers\groq\worker_config.json`
- `C:\Users\TuUsuario\Documents\d8_data\workers\groq\credentials.json`

Estos archivos se crean automáticamente la primera vez que ejecutas el sistema.

### 4. Ejecutar

#### Método 1: Launcher Unificado (Recomendado)

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1  # Windows
# o
source venv/bin/activate     # Linux/Mac

# Ejecutar launcher
python start_d8.py

# Menú interactivo:
# 1. 🏛️  Congreso Autónomo
# 2. 💎 Niche Discovery
# 3. 🧬 Sistema Evolutivo
# 4. 🎯 Orchestrator
# 5. 🔧 Slave Server
# 6. 🔄 Supervisor D8 (Auto-restart)
# 7. ❌ Salir
```

#### Método 2: CLI Directo (Para Scripts)

```bash
# Lanzar componentes directamente
python start_d8.py congress       # Congreso Autónomo
python start_d8.py niche          # Niche Discovery
python start_d8.py evolution      # Sistema Evolutivo
python start_d8.py orchestrator   # Orchestrator
python start_d8.py slave          # Slave Server (ejecutar)
python start_d8.py slaves         # Gestión de Slaves (agregar/instalar/ver)
python start_d8.py supervisor     # Supervisor (Auto-restart)
```

#### Método 3: Supervisor (Producción 24/7)

```bash
# Activar entorno virtual
.\venv\Scripts\Activate.ps1

# Iniciar supervisor con auto-restart
python start_d8.py supervisor

# El supervisor automáticamente:
# ✅ Inicia: Congreso, Niche Discovery, Orchestrator
# ✅ Monitorea health cada 10 segundos
# ✅ Reinicia automáticamente si fallan
# ✅ Límite: 5 reintentos por componente
# ✅ Ctrl+C: Cierre limpio de todos los procesos

# Ver logs en tiempo real (otra terminal):
Get-Content "$env:USERPROFILE\Documents\d8_data\logs\supervisor.log" -Wait -Tail 20
```

#### Método 4: Manual (Desarrollo)

```bash
# Ejecutar componentes individuales
python -m app.main                          # Sistema completo
python scripts\autonomous_congress.py       # Solo congreso
python scripts\niche_discovery_agent.py     # Solo niche discovery
python -m app.evolution.groq_evolution      # Solo evolución
```

---

---

## 📊 Uso del Sistema

### Orchestrator API

```bash
# Verificar estado
curl http://localhost:5000/

# Listar workers activos
curl http://localhost:5000/api/workers

# Enviar tarea
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "analyze",
    "data": {"text": "ejemplo"}
  }'
```

### Congreso Autónomo

```bash
# Ejecutar ciclo de mejora continua
python scripts\autonomous_congress.py

# El congreso automáticamente:
# 1. Investiga nuevas técnicas
# 2. Diseña experimentos
# 3. Ejecuta pruebas A/B
# 4. Valida resultados
# 5. Implementa mejoras
# 6. Repite el ciclo
```

### Niche Discovery

```bash
# Descubrir nichos rentables
python scripts\niche_discovery_agent.py

# Analiza mercados y genera reporte en:
# data/test_results/niche_discovery.json
```

---

## 🧬 Cómo Funciona la Evolución

### Función de Fitness

```python
fitness = (
    0.5 * revenue_generated +      # Métrica principal
    0.3 * success_rate * 100 +     # Confiabilidad
    0.2 * engagement_score         # Calidad
)
```

### Operadores Genéticos

**Crossover (Reproducción):**
```
Padre A: "Eres un analista de tendencias..."
Padre B: "Eres un creador de contenido viral..."
         ↓ [Groq analiza y combina]
Hijo:    "Eres un estratega de contenido que analiza 
          tendencias y crea narrativas virales..."
```

**Mutación (Variación):**
```
Original: "Escribe de forma técnica y formal..."
          ↓ [Mutación: cambio de tono]
Mutado:   "Explica conceptos complejos de forma casual..."
```

### Estrategia de Selección

1. **Torneo:** Selecciona 3 agentes aleatorios, elige los 2 mejores
2. **Elitismo:** Top 20% siempre sobrevive
3. **Tasa de Crossover:** 70% híbridos, 30% clones
4. **Tasa de Mutación:** 10% de variación genética

---

## 💰 Estrategia de Monetización

Ver [docs/03_operaciones/monetizacion.md](docs/03_operaciones/monetizacion.md) para análisis completo.

**Sistema Autónomo:**
- Niche Discovery: Descubrimiento automático de oportunidades
- Autonomous Congress: Investigación y experimentación continua
- Darwin Evolution: Selección natural de mejores agentes
- Self-Healing: Auto-corrección sin intervención humana

---

## 📂 Estructura del Proyecto

```
d8/
├── app/                     # Código principal
│   ├── agents/              # Implementaciones de agentes
│   │   └── base_agent.py    # Clase base de agente
│   ├── evolution/           # Algoritmos genéticos
│   │   ├── darwin.py        # Crossover y mutación
│   │   └── groq_evolution.py # Evolución con Groq
│   ├── distributed/         # Sistema distribuido
│   │   ├── orchestrator.py  # Orquestador central
│   │   └── worker_groq.py   # Worker Groq
│   ├── integrations/        # APIs externas
│   │   ├── groq_client.py   # Cliente Groq
│   │   └── gemini_client.py # Cliente Gemini
│   ├── memory/              # Sistema de memoria
│   ├── utils/               # Utilidades
│   ├── config.py            # Configuración
│   └── main.py              # Servidor Flask
├── scripts/                 # Scripts de ejecución
│   ├── autonomous_congress.py  # Congreso autónomo
│   ├── niche_discovery_agent.py # Descubrimiento de nichos
│   ├── tests/               # Scripts de prueba
│   ├── setup/               # Scripts de configuración
│   └── launch/              # Scripts de lanzamiento
├── data/                    # Datos del sistema
│   ├── genomes/             # Genomas guardados
│   ├── metrics/             # Datos de rendimiento
│   ├── logs/                # Logs de aplicación
│   └── congress_experiments/ # Resultados del congreso
├── tests/                   # Suite de tests
│   ├── economy/             # Tests de economía mock
│   ├── integration/         # Tests de integración
│   └── unit/                # Tests unitarios
├── docs/                    # Documentación (organizada por categoría)
│   ├── 01_arquitectura/     # Arquitectura del sistema
│   ├── 02_setup/            # Configuración e instalación
│   ├── 03_operaciones/      # Operaciones y monetización
│   ├── 04_desarrollo/       # Guías de desarrollo
│   ├── 05_troubleshooting/  # Resolución de problemas
│   ├── 06_knowledge_base/   # Base de conocimiento acumulativo
│   └── 07_reportes/         # Reportes y resultados
├── config/                  # Configuraciones adicionales
├── .env                     # Variables de entorno
├── .gitignore              # Git ignore
├── requirements.txt         # Dependencias
├── PENDIENTES.md           # Tareas pendientes (FASE 2 activa)
├── LEER_PRIMERO.md         # Guía de inicio rápido
└── README.md               # Este archivo
```

**Nota:** La configuración de agentes y workers está en `~/Documents/d8_data/`:
- `~/Documents/d8_data/agentes/config.json` - Configuración del ecosistema
- `~/Documents/d8_data/workers/groq/` - Configuración de workers Groq

---

## 🔧 Configuración

Variables en `.env`:

```bash
# API Keys
GROQ_API_KEY=gsk_tu_key_aqui

# Parámetros de Evolución (en ~/Documents/d8_data/agentes/config.json)
# - population_size: 20
# - mutation_rate: 0.1
# - generations: 100
# - elite_size: top 20%
```

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=app tests/

# Test específico
pytest tests/unit/test_agent.py

# Validar economía mock (FASE 1)
python scripts/tests/validate_mock_economy.py
pytest tests/economy/test_mock_economy.py -v
```

**Estado actual:** ✅ 34/34 tests passing | ✅ Mock economy validated

---

## 📈 Monitoreo

**Por Agente:**
- `total_actions`: Acciones ejecutadas
- `success_rate`: % de éxito
- `revenue`: Ingresos generados
- `fitness`: Score combinado

**Por Generación:**
- `best_fitness`: Mejor performer
- `avg_fitness`: Promedio poblacional
- `generation`: Número de generación

**Resultados del Congreso:**
- Guardados en `data/congress_experiments/`
- Cada ciclo genera reporte JSON con mejoras implementadas

---

## 🛣️ Roadmap

### ✅ Fase 1: Economía Interna (COMPLETADA)
- [x] Sistema de créditos D8
- [x] Revenue attribution
- [x] Autonomous accounting
- [x] 34 tests + validación completa

### 🚀 Fase 2: Integración con Sistema Autónomo (EN PROGRESO)
- [ ] Conectar D8CreditsSystem con agentes reales
- [ ] Integrar RevenueAttributionSystem con Darwin
- [ ] Desplegar AutonomousAccounting en producción
- [ ] Validación end-to-end

### 🔮 Fase 3: Escalado
- [ ] Múltiples workers distribuidos
- [ ] Memoria vectorial (ChromaDB)
- [ ] Colaboración entre agentes
- [ ] Auto-escalado según demanda

---

## 🤝 Contribuir

Proyecto personal, pero ideas son bienvenidas!

1. Fork del repositorio
2. Crear rama (`git checkout -b feature/mejora`)
3. Commit cambios (`git commit -m 'Add mejora'`)
4. Push a rama (`git push origin feature/mejora`)
5. Crear Pull Request

---

## ⚠️ Notas Importantes

### Optimización de Costos
- **Groq (Gratis):** 30 req/min, 14,400 req/día
- **Llama-3.3-70b:** Modelo gratuito de alta calidad
- **Costo:** $0/mes en tier gratuito

### Legal y Ética
- El sistema es completamente autónomo pero debe usarse responsablemente
- Respetar TOS de plataformas
- Software experimental - usar bajo tu responsabilidad

### Rendimiento
- Groq: ~500ms por inferencia
- Congreso autónomo: ~2-5 ciclos/hora
- Recomendado: Ejecución 24/7 para máximo aprendizaje

---

## 📚 Documentación Adicional

- [Copilot Instructions](.github/copilot-instructions.md) - Contexto fundacional del proyecto
- [Knowledge Base](docs/06_knowledge_base/README.md) - Memoria y experiencias profundas
- [Autonomous Congress](docs/06_knowledge_base/experiencias_profundas/congreso_autonomo.md) - Sistema de mejora continua
- [PENDIENTES](PENDIENTES.md) - **FASE 2 en progreso**
- [Auditoría Pre-FASE 2](docs/06_knowledge_base/experiencias_profundas/auditoria_pre_fase2.md) - Estado actual validado

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- **Groq** for lightning-fast inference
- **DeepSeek** for powerful local models
- **Ollama** for making local LLMs accessible

---

**Built with 🧠 by evolutionary AI**

For questions or support, open an issue on GitHub.
