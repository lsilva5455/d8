# 🤖 D8 - Sistema de IA Completamente Autónomo

**Sistema de inteligencia artificial que se mejora a sí mismo sin intervención humana.**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![Groq](https://img.shields.io/badge/groq-llama--3.3-orange.svg)](https://groq.com/)

---

## 🎯 ¿Qué es D8?

D8 es un ecosistema de IA con tres sistemas autónomos:

1. **🧬 Sistema Evolutivo**: Selección natural de agentes mediante algoritmos genéticos
2. **💎 Niche Discovery**: Descubrimiento automático de nichos rentables
3. **🏛️ Congreso Autónomo**: Investigación, experimentación y mejora continua del sistema

**Característica principal:** Cero intervención humana. D8 evoluciona, experimenta y se optimiza automáticamente.

---

## 🏗️ Arquitectura

```
┌──────────────────────────────────────┐
│     SISTEMA EVOLUTIVO (Darwin)       │
│  Evolución genética de agentes       │
│  → Mutación, Crossover, Selección    │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│      NICHE DISCOVERY                 │
│  Descubrimiento de nichos rentables  │
│  → Análisis de mercado automático    │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│      CONGRESO AUTÓNOMO               │
│  Mejora continua del sistema         │
│  → Research → Test → Implement       │
└──────────────────────────────────────┘
```

### Componentes Principales

1. **Sistema Evolutivo** (`app/evolution/darwin.py`)
   - Selección natural mediante fitness
   - Operadores genéticos: mutación (10%), crossover, elite
   - Población de 20 agentes por generación

2. **Niche Discovery** (`scripts/niche_discovery_agent.py`)
   - Agente especializado en descubrir nichos
   - Análisis automático de mercados
   - Genera reportes de oportunidades

3. **Congreso Autónomo** (`scripts/autonomous_congress.py`)
   - 5 miembros: Researcher, Experimenter, Optimizer, Implementer, Validator
   - Ciclo completo: Investiga → Experimenta → Valida → Implementa
   - Mejora el sistema automáticamente sin intervención humana

4. **Base Agent** (`app/agents/base_agent.py`)
   - Genoma (system prompt) que define comportamiento
   - Usa Groq LLM (llama-3.3-70b-versatile)
   - Tracking de métricas de fitness

5. **Orchestrator + Workers** (`app/distributed/`)
   - Arquitectura distribuida para escalar
   - Orchestrator Flask en puerto 5000
   - Workers Groq para procesamiento
   - Endpoints for agent management and evolution
   - D8-GENESIS integration endpoints

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

```bash
# Opción 1: Sistema completo (orchestrator + worker)
python -m app.main

# Opción 2: Congreso autónomo (mejora continua)
python scripts\autonomous_congress.py

# Opción 3: Niche Discovery
python scripts\niche_discovery_agent.py

# Opción 4: Sistema evolutivo
python -m app.evolution.groq_evolution
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

**Fase 1: Content Empire**
- Generación de contenido para redes sociales
- Gestión de múltiples nichos
- ROI predecible

**Fase 2: Niche Discovery**
- Descubrimiento automático de oportunidades
- Análisis de mercados emergentes
- Escalado inteligente

---

## 📊 Project Structure

```
d8/
├── app/
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
├── docs/                    # Documentación
│   ├── ARQUITECTURA_D8.md   # Arquitectura completa
│   ├── ESTRATEGIA_MONETIZACION.md
│   └── ...
├── config/                  # Configuraciones adicionales
├── .env                     # Variables de entorno
├── .gitignore              # Git ignore
├── requirements.txt         # Dependencias
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
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app tests/

# Test específico
pytest tests/unit/test_agent.py

# Scripts de prueba del sistema
python scripts/tests/test_content_empire.py
python scripts/tests/test_device_farm.py
```

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

### ✅ Fase 1: Sistema Base
- [x] Implementación de agentes
- [x] Motor de evolución (crossover, mutación)
- [x] API Flask
- [x] Sistema de configuración
- [x] Congreso autónomo

### 🚧 Fase 2: Optimización
- [x] Niche Discovery automático
- [x] Congreso de mejora continua
- [ ] Integración con APIs de monetización
- [ ] Dashboard de métricas

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

- [D8-GENESIS Module](docs/02_setup/genesis_module.md) - Self-coding & healing system
- [Strategic Analysis](ESTRATEGIA_MONETIZACION.md) - Full monetization comparison
- [Experiences Base](documentacion/experiencias_profundas/EXPERIENCIAS_BASE.md) - Development methodology
- [Groq API Docs](https://console.groq.com/docs)
- [Ollama Docs](https://ollama.ai/docs)

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
