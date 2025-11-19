#!/bin/bash
# Setup script for The Hive - AI Agent Ecosystem
# Generated: 2025-11-17

set -e  # Exit on error

echo "🐝 Setting up The Hive project structure..."

# Create main directories
mkdir -p app/{agents,evolution,memory,integrations,utils}
mkdir -p tests/{unit,integration,e2e}
mkdir -p data/{genomes,metrics,logs}
mkdir -p docs
mkdir -p scripts

echo "📁 Creating directory structure..."

# App structure
touch app/__init__.py
touch app/main.py
touch app/config.py

# Agents
touch app/agents/__init__.py
touch app/agents/base_agent.py
touch app/agents/content_agent.py
touch app/agents/device_agent.py

# Evolution
touch app/evolution/__init__.py
touch app/evolution/darwin.py
touch app/evolution/fitness.py
touch app/evolution/selection.py

# Memory
touch app/memory/__init__.py
touch app/memory/vector_store.py
touch app/memory/episode_buffer.py

# Integrations
touch app/integrations/__init__.py
touch app/integrations/groq_client.py
touch app/integrations/deepseek_client.py
touch app/integrations/wordpress_api.py
touch app/integrations/appium_controller.py

# Utils
touch app/utils/__init__.py
touch app/utils/logger.py
touch app/utils/metrics.py

# Tests
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/e2e/__init__.py

# Config files
touch .env.example
touch .gitignore
touch pytest.ini

# Data directories
touch data/genomes/.gitkeep
touch data/metrics/.gitkeep
touch data/logs/.gitkeep

echo "✅ Project structure created successfully!"
echo ""
echo "📂 Structure:"
echo "."
echo "├── app/"
echo "│   ├── agents/          # Agent implementations"
echo "│   ├── evolution/       # Genetic algorithms"
echo "│   ├── memory/          # Vector DB & memory"
echo "│   ├── integrations/    # External APIs"
echo "│   └── utils/           # Utilities"
echo "├── tests/               # Test suite"
echo "├── data/                # Runtime data"
echo "├── docs/                # Documentation"
echo "└── scripts/             # Utility scripts"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env and configure your API keys"
echo "2. Install dependencies: pip install -r requirements.txt"
echo "3. Run tests: pytest"
echo "4. Start the hive: python app/main.py"
