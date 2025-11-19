"""
Niche Discovery Agent usando Gemini con JSON mode
Agent especializado con output estructurado garantizado
"""

import sys
import json
import time
import re
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.integrations.gemini_client import GeminiClient
from app.config import config
import os

class GeminiNicheAgent:
    """Niche discovery agent usando Gemini con JSON mode"""
    
    def __init__(self):
        # Get Gemini API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no encontrado en .env")
        
        self.client = GeminiClient(api_key=api_key, model="gemini-2.0-flash-exp")
        self.agent_id = "niche-gemini"
    
    def discover_niche(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Discover niche with structured JSON output"""
        
        prompt = f"""You are an elite niche discovery AI analyzing: {market_data['area']}

TARGET GEOGRAPHY: {market_data.get('target_geography', 'USA')}
CONTEXT: {market_data.get('context', '')}
TARGET REVENUE: {market_data.get('target_revenue', '$5k-15k/month')}

Analyze this market and return a COMPLETE niche analysis in JSON format with ALL these fields:

{{
  "niche_name": "Specific focused name",
  "description": "Clear 1-sentence description",
  "target_geography": "{market_data.get('target_geography', 'USA')}",
  "geo_specific_insights": {{
    "USA": "Insights for US market",
    "España": "Insights for Spanish market",
    "Chile": "Insights for Chilean market"
  }},
  "target_audience": "Specific demographic",
  "pain_points": ["pain1", "pain2", "pain3"],
  "monetization_methods": [
    {{
      "method": "subscription or ads or affiliate or saas",
      "potential_USA": "$X-Y/month",
      "potential_España": "€X-Y/month",
      "potential_Chile": "$XM-YM CLP/month",
      "difficulty": "low or medium or high"
    }}
  ],
  "competition": {{
    "level": "low or medium or high",
    "main_players": ["Competitor 1", "Competitor 2"],
    "opportunities": "Market gaps"
  }},
  "content_strategy": {{
    "platforms": ["Instagram", "TikTok", "YouTube"],
    "content_types": ["videos", "posts", "stories"],
    "posting_frequency": "5 times per week",
    "language_strategy": "English-only or Spanish-only or Multi-language"
  }},
  "keywords": {{
    "USA": ["keyword1", "keyword2"],
    "España": ["palabra1", "palabra2"],
    "Chile": ["palabra1", "palabra2"]
  }},
  "market_urgency": "Why this niche is hot right now",
  "entry_barriers": "low or medium or high",
  "success_probability": 0.85,
  "confidence_score": 0.90,
  "launch_priority": "Start with [country] because [reason]"
}}

Return ONLY the JSON object."""

        try:
            # Use Gemini JSON mode
            response = self.client.generate_json(
                prompt=prompt,
                temperature=0.4
            )
            
            return response
            
        except Exception as e:
            print(f"Error: {e}")
            return {
                "niche_name": "Unknown",
                "confidence_score": 0,
                "error": str(e)
            }

if __name__ == "__main__":
    print("🔍 GEMINI NICHE DISCOVERY - Testing")
    print("=" * 70)
    
    agent = GeminiNicheAgent()
    
    test_market = {
        "area": "Automatización de ventas para emprendedores chilenos",
        "context": "Emprendedores chilenos venden por Instagram/WhatsApp pero pierden ventas por desorganización",
        "target_revenue": "$2M-6M CLP/month",
        "target_geography": "CL"
    }
    
    result = agent.discover_niche(test_market)
    
    print("\\nRESULTADO:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
