# 🐝 The Hive - Evolutionary AI Agent Ecosystem

**An autonomous system where AI agents evolve through genetic algorithms to maximize real-world revenue.**

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🎯 Overview

The Hive is an evolutionary AI agent ecosystem where:
- **Agents** act autonomously using Groq (fast, cheap inference)
- **Evolution** happens via DeepSeek (local, zero API cost)
- **Fitness** is measured by real revenue and engagement metrics
- **Natural Selection** ensures only profitable agents survive

**Think of it as:** Pokémon breeding meets AI agents meets real business.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         THE HIVE                            │
│                    (Flask API Server)                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─────────────────┐
                              │                 │
                    ┌─────────▼────────┐  ┌────▼──────────┐
                    │   Agent Pool     │  │   Evolution   │
                    │   (Population)   │  │   Engine      │
                    └─────────┬────────┘  └────┬──────────┘
                              │                 │
                    ┌─────────▼─────────────────▼─────┐
                    │        Base Agent                │
                    │  - Genome (System Prompt)        │
                    │  - act() → Groq API             │
                    │  - Fitness Metrics              │
                    └──────────┬──────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
      ┌───────▼──────┐  ┌─────▼─────┐  ┌──────▼──────┐
      │ Groq         │  │ DeepSeek  │  │  ChromaDB   │
      │ (Fast Action)│  │ (Evolution)│  │  (Memory)   │
      └──────────────┘  └───────────┘  └─────────────┘
                                              │
                                    ┌─────────▼──────────┐
                                    │   D8-GENESIS       │
                                    │  (Self-Coding)     │
                                    │  - Code Vault      │
                                    │  - Coder Agent     │
                                    │  - Self-Healing    │
                                    └────────────────────┘
```

### Key Components

1. **Base Agent** (`app/agents/base_agent.py`)
   - Contains genetic material (system prompt)
   - Uses Groq for fast decision-making
   - Tracks fitness metrics (revenue, engagement, success rate)

2. **Evolution Engine** (`app/evolution/darwin.py`)
   - **Crossover:** Merges two parent prompts intelligently
   - **Mutation:** Introduces controlled variations
   - **Selection:** Tournament selection for parents

3. **D8-GENESIS Module** 🆕 (`docs/D8_GENESIS_MODULE.md`)
   - **Code Vault:** RAG system for legacy code retrieval
   - **Coder Agent:** Polymorphic code generation
   - **Self-Healing:** Autonomous error detection and repair
   - **Anti-Fingerprinting:** Evades detection systems

4. **Flask API** (`app/main.py`)
   - RESTful interface to control the hive
   - Endpoints for agent management and evolution
   - D8-GENESIS integration endpoints

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.10+
python --version

# Ollama (for DeepSeek local)
curl https://ollama.ai/install.sh | sh
ollama pull deepseek-coder:33b
ollama serve
```

### 2. Installation

```bash
# Clone repository
git clone https://github.com/lsilva5455/d8.git
cd d8

# Run setup script
bash setup_project.sh

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### 3. Configure API Keys

Edit `.env`:
```bash
GROQ_API_KEY=gsk_your_groq_api_key_here
DEEPSEEK_BASE_URL=http://localhost:11434
DEEPSEEK_MODEL=deepseek-coder:33b
```

Get your Groq API key: https://console.groq.com/

### 4. Run The Hive

```bash
python app/main.py
```

The server will start on `http://localhost:5000`

---

## 📡 API Usage

### Health Check
```bash
curl http://localhost:5000/
```

### List All Agents
```bash
curl http://localhost:5000/api/agents
```

Response:
```json
{
  "total": 20,
  "agents": [
    {
      "agent_id": "abc123...",
      "generation": 0,
      "fitness": 45.2,
      "metrics": {
        "total_actions": 100,
        "success_rate": 0.95,
        "revenue": 50.0
      }
    }
  ]
}
```

### Trigger Agent Action
```bash
curl -X POST http://localhost:5000/api/agents/<agent_id>/act \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "generate_content",
    "input_data": {
      "niche": "AI tools",
      "target_audience": "developers"
    }
  }'
```

### Evolve Population
```bash
curl -X POST http://localhost:5000/api/evolve
```

This will:
1. Evaluate fitness of all agents
2. Select elite performers
3. Breed new generation via crossover
4. Apply mutations
5. Return new population stats

---

## 🧬 How Evolution Works

### Fitness Function

```python
fitness = (
    0.5 * revenue_generated +      # Primary metric
    0.3 * success_rate * 100 +     # Reliability
    0.2 * engagement_score         # Quality
)
```

### Genetic Operations

**Crossover (Breeding):**
```
Parent A: "You are a tech blogger focused on AI tools..."
Parent B: "You are a product reviewer specializing in SaaS..."
          ↓ [DeepSeek analyzes and merges]
Child:    "You are an AI-focused product analyst reviewing 
           SaaS tools with technical depth and user perspective..."
```

**Mutation (Variation):**
```
Original: "Write formal technical documentation..."
          ↓ [Mutation: tone_shift]
Mutated:  "Explain complex topics in casual, accessible language..."
```

### Selection Strategy

1. **Tournament Selection:** Pick 3 random agents, choose best 2 as parents
2. **Elitism:** Top 2 agents always survive unchanged
3. **Crossover Rate:** 70% of offspring are hybrids, 30% are clones
4. **Mutation Rate:** 10% of genes get mutated

---

## 💰 Monetization Strategy

See [ESTRATEGIA_MONETIZACION.md](ESTRATEGIA_MONETIZACION.md) for full analysis.

**Recommended: Content Empire** (Phase 1)
- Lower technical barrier
- Predictable ROI
- Scales horizontally
- 100% legal

**Future: Hybrid Model** (Phase 2+)
- 70% Content Empire (stable revenue)
- 30% Device Farm (high-value opportunities)

---

## 📊 Project Structure

```
d8/
├── app/
│   ├── agents/              # Agent implementations
│   │   └── base_agent.py    # Core agent class
│   ├── evolution/           # Genetic algorithms
│   │   └── darwin.py        # Crossover & mutation
│   ├── integrations/        # External APIs
│   │   ├── groq_client.py   # Fast inference
│   │   └── deepseek_client.py  # Local evolution
│   ├── memory/              # Vector DB (future)
│   ├── utils/               # Utilities
│   ├── config.py            # Configuration
│   └── main.py              # Flask server
├── data/
│   ├── genomes/             # Saved agent genomes
│   ├── metrics/             # Performance data
│   └── logs/                # Application logs
├── tests/                   # Test suite
├── docs/                    # Documentation
├── requirements.txt         # Dependencies
├── setup_project.sh         # Setup script
└── .env.example             # Environment template
```

---

## 🔧 Configuration

All settings in `.env`:

```bash
# Evolution Parameters
POPULATION_SIZE=20           # Number of agents
MUTATION_RATE=0.1           # 10% mutation chance
CROSSOVER_RATE=0.7          # 70% crossover chance
GENERATIONS=100             # Max generations
ELITE_SIZE=2                # Top agents to preserve

# Agent Behavior
MAX_ACTIONS_PER_DAY=1000    # Rate limiting
ACTION_COOLDOWN_SECONDS=60  # Cooldown between actions

# APIs
GROQ_API_KEY=your_key       # Required
DEEPSEEK_BASE_URL=http://localhost:11434  # Local
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/unit/test_agent.py
```

---

## 📈 Monitoring & Metrics

**Per Agent:**
- `total_actions`: Count of actions taken
- `success_rate`: % of successful actions
- `revenue_generated`: Total $ earned
- `fitness`: Combined score

**Per Generation:**
- `best_fitness`: Top performer
- `avg_fitness`: Population average
- `generation`: Current generation number

View in real-time:
```bash
curl http://localhost:5000/api/agents | jq '.agents | sort_by(.fitness) | reverse | .[0:5]'
```

---

## 🛣️ Roadmap

### Phase 1: Core System (✅ Complete)
- [x] Base agent implementation
- [x] Evolution engine (crossover, mutation)
- [x] Flask API
- [x] Configuration system
- [x] D8-GENESIS module (self-coding & healing)

### Phase 2: Content Empire (In Progress)
- [ ] WordPress integration
- [ ] SEO optimization module
- [ ] Content quality scoring
- [ ] Automated publishing

### Phase 3: Intelligence Layer
- [x] ChromaDB memory integration (Code Vault)
- [ ] Agent collaboration protocols
- [ ] Meta-learning from top performers

### Phase 4: Device Farm (Future)
- [ ] Appium integration
- [ ] Device orchestration
- [ ] Bug bounty automation
- [x] Polymorphic code generation (anti-detection)
- [x] Self-healing execution loop

---

## 🤝 Contributing

This is a personal project, but ideas are welcome!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

---

## ⚠️ Important Notes

### Cost Optimization
- **Groq:** ~$0.10 per 1M tokens (Mixtral)
- **DeepSeek:** $0 (runs locally via Ollama)
- **Expected:** $20-50/month for 100 agents at moderate activity

### Legal & Ethics
- Generated content must be original
- Respect platform TOS (WordPress, Medium, etc.)
- Device Farm features may violate app TOS (use carefully)
- This is experimental software, use responsibly

### Performance
- Groq responses: 50-200ms
- DeepSeek evolution: 10-30s per operation
- Recommended: Run on machine with 16GB+ RAM for local DeepSeek

---

## 📚 Additional Resources

- [D8-GENESIS Module](docs/D8_GENESIS_MODULE.md) - Self-coding & healing system
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
