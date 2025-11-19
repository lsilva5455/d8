"""
Test simplificado de Niche Discovery
Prueba rápida con un solo agente
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.agents.base_agent import BaseAgent
from app.evolution.darwin import Genome
from app.config import config

# Create simple niche analyst
genome = Genome(
    prompt="""You are an AI niche discovery expert.

Analyze the given niche opportunity and return insights in this exact JSON format:
{
  "niche_name": "specific name",
  "description": "what it is",
  "target_audience": "who needs this",
  "monetization": ["method1", "method2"],
  "competition": "low/medium/high",
  "revenue_potential": "$X-Y per month",
  "why_now": "urgency reason",
  "confidence": 0.85
}""",
    fitness=0.0,
    generation=1
)

agent = BaseAgent(
    genome=genome,
    groq_api_key=config.api.groq_api_key,
    agent_id="niche-tester"
)

print("🔍 NICHE DISCOVERY - TEST SIMPLE")
print("=" * 60)
print()

# Test niche
result = agent.act(
    input_data={
        "niche": "AI automation tools for small businesses",
        "context": "Post-GPT era, businesses want automation without coding",
        "analyze": "competition, revenue potential, target audience"
    },
    action_type="analyze_niche"
)

print("📊 RESULTADO:")
print(json.dumps(result, indent=2))
print()

# Check if response key exists
if "response" in result:
    print("✅ Agent está respondiendo (revisar formato)")
else:
    print("✅ Test completado")
