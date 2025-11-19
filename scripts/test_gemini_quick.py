"""
Test rápido - Niche Discovery con Gemini
Sin Unknown, con rate limiting
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.integrations.gemini_client import GeminiClient
from app.evolution.darwin import Genome
from dotenv import load_dotenv
import json
import time

load_dotenv()

# Initialize Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not found in .env")
    sys.exit(1)

gemini = GeminiClient(api_key=GEMINI_API_KEY, rpm_limit=15)

# Genome prompt
genome = Genome(
    prompt="""You are an elite niche discovery AI.

RESPONSE RULES:
1. Output ONLY valid JSON
2. No explanations before or after
3. NEVER use "Unknown" as niche_name

REQUIRED JSON STRUCTURE:
{
  "niche_name": "Specific Niche Name Here",
  "description": "Clear 1-sentence description",
  "target_geography": "USA/ES/CL",
  "confidence_score": 0.85,
  "competition": {
    "level": "low/medium/high"
  }
}

OUTPUT ONLY JSON.""",
    fitness=0.0,
    generation=1
)

# Test markets
markets = [
    {"area": "Automatización de ventas para emprendedores chilenos", "geo": "CL"},
    {"area": "Automatización de marketing para PYMEs españolas", "geo": "ES"},
    {"area": "AI automation for small e-commerce stores", "geo": "USA"}
]

print("🧪 TESTING GEMINI NICHE DISCOVERY")
print("=" * 80)
print()

for i, market in enumerate(markets, 1):
    print(f"[{i}/{len(markets)}] {market['area']}")
    print("-" * 80)
    
    prompt = f"""{genome.prompt}

MARKET TO ANALYZE: {market['area']}
TARGET GEOGRAPHY: {market['geo']}

Analyze this market and return ONLY valid JSON."""
    
    try:
        start = time.time()
        result = gemini.generate_json(prompt=prompt, temperature=0.3, max_tokens=1500)
        elapsed = time.time() - start
        
        niche_name = result.get('niche_name', 'Unknown')
        confidence = result.get('confidence_score', 0)
        
        print(f"✅ Completed in {elapsed:.1f}s")
        print(f"   📌 Nicho: {niche_name}")
        print(f"   📊 Confianza: {confidence:.0%}")
        print(f"   🎯 Competencia: {result.get('competition', {}).get('level', 'N/A')}")
        print()
        
        if niche_name.lower() in ['unknown', 'unknownniche']:
            print("⚠️  WARNING: Got 'Unknown' - this should not happen with Gemini!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()

print("=" * 80)
print("✅ Test completed")
