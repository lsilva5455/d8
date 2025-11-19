# D8 Project Context for GitHub Copilot

## Project Overview

D8 is a fully autonomous AI system that improves itself without human intervention through three independent systems:

1. **Evolutionary System (Darwin)**: Natural selection of agents via genetic algorithms
2. **Niche Discovery**: Automated discovery of profitable market niches
3. **Autonomous Congress**: Research, experimentation, and continuous system improvement

**Core Principle**: Zero human intervention after initial setup.

---

## Knowledge System

D8 maintains cumulative knowledge in two levels:

### 💭 Generic Memory (`docs/06_knowledge_base/memoria/`)
Reusable patterns applicable to any project:
- [Architecture Patterns](../docs/06_knowledge_base/memoria/patrones_arquitectura.md)
- [Best Practices](../docs/06_knowledge_base/memoria/mejores_practicas.md)

### 🧠 D8-Specific Experience (`docs/06_knowledge_base/experiencias_profundas/`)
Lessons learned specific to D8:
- [Autonomous Congress](../docs/06_knowledge_base/experiencias_profundas/congreso_autonomo.md)
- [Base Experiences](../docs/06_knowledge_base/experiencias_profundas/EXPERIENCIAS_BASE.md)

---

## Development Rules

### Before Implementation

1. ✅ **Consult Memory** - Check if a pattern exists for this problem
2. ✅ **Check Experience** - Review similar past decisions in D8
3. ✅ **Validate Approach** - Ensure it aligns with autonomy principle

### After Implementation

1. ✅ **Document Experience** - Update `docs/experiencias_profundas/`
2. ✅ **Consider Promotion** - If generalizable, add to `docs/memoria/`
3. ✅ **Update Index** - Keep README.md files current

---

## Key Patterns

### Configuration: Dual System
- `.env` for API keys (gitignored)
- JSON in `~/Documents/d8_data/` for functional configs
- Auto-generation if not exists

### Distributed Workers
- Orchestrator pattern with heartbeat monitoring
- Workers poll for tasks, report results
- Automatic dead worker detection

### Path Handling
Always use `pathlib.Path` for cross-platform compatibility:
```python
config_path = Path.home() / "Documents" / "app" / "config.json"
```

---

## Architecture

```
d8/
├── app/                   # Core code (D8-specific logic)
│   ├── agents/            # Agent implementations
│   ├── evolution/         # Genetic algorithms
│   ├── distributed/       # Orchestrator + Workers
│   ├── knowledge/         # Code vault
│   └── memory/            # Episodic memory
├── lib/                   # Reusable libraries (generic)
│   ├── llm/               # LLM clients (Groq, Gemini, DeepSeek)
│   ├── validation/        # Pydantic schemas
│   └── parsers/           # Text processing utilities
├── scripts/               # Executable scripts
│   ├── setup/             # Installation scripts
│   ├── launch/            # Launch scripts
│   └── tests/             # Test scripts
├── docs/                  # Documentation (organized by category)
│   ├── 01_arquitectura/   # System architecture
│   ├── 02_setup/          # Setup and configuration
│   ├── 03_operaciones/    # Operations guides
│   ├── 04_desarrollo/     # Development and testing
│   ├── 05_troubleshooting/  # Problem solving
│   ├── 06_knowledge_base/   # Cumulative knowledge
│   │   ├── memoria/           # Generic patterns
│   │   └── experiencias_profundas/  # D8-specific experiences
│   └── 07_reportes/       # Reports and results
└── data/                  # Generated data
```

---

## Critical Reminders

- ⚠️ **Autonomy First**: No human intervention in system operation
- ⚠️ **Consult Memory**: Don't reinvent solved problems
- ⚠️ **Document Decisions**: Update experiences after significant changes
- ⚠️ **Cross-Platform**: Use pathlib, not hardcoded paths
- ⚠️ **Validate Early**: Use Pydantic schemas for API inputs

---

## Useful Commands

```bash
# Start autonomous congress
python scripts/autonomous_congress.py

# Run niche discovery
python scripts/niche_discovery_agent.py

# Launch full system
python -m app.main
```

---

**Last Updated**: 2025-11-19  
**For detailed context**: See `docs/06_knowledge_base/README.md`
