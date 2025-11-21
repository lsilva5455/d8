"""
Niche Discovery Agent
Agente especializado en descubrir y analizar nichos rentables
"""

import sys
import json
import time
from pathlib import Path

# Agregar root del proyecto al PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.base_agent import BaseAgent
from app.evolution.darwin import Genome
from app.config import config

def create_niche_discovery_agent():
    """Create specialized niche discovery agent"""
    
    genome = Genome(
        prompt="""You are an elite AI niche discovery agent.

Your mission: Find highly profitable, low-competition niches with strong monetization potential.

When given a market area or trend, you analyze:
1. Target audience pain points
2. Competition landscape
3. Monetization opportunities
4. Content strategies
5. Market urgency

You provide actionable insights that help entrepreneurs and content creators identify opportunities.

Respond with this JSON structure:
{
  "niche_name": "specific, focused niche name",
  "description": "clear explanation of the niche",
  "target_audience": "specific demographic/psychographic profile",
  "pain_points": ["problem1", "problem2", "problem3"],
  "monetization_methods": [
    {"method": "name", "potential": "$X-Y/month", "difficulty": "easy/medium/hard"},
    {"method": "name2", "potential": "$X-Y/month", "difficulty": "easy/medium/hard"}
  ],
  "competition": {
    "level": "low/medium/high",
    "main_players": ["competitor1", "competitor2"],
    "opportunities": "gaps in the market"
  },
  "content_strategy": {
    "platforms": ["platform1", "platform2"],
    "content_types": ["type1", "type2"],
    "posting_frequency": "X times per week"
  },
  "keywords": ["kw1", "kw2", "kw3", "kw4", "kw5"],
  "market_urgency": "why this niche is hot right now",
  "entry_barriers": "low/medium/high",
  "success_probability": 0.85,
  "confidence_score": 0.90
}""",
        fitness=0.0,
        generation=1
    )
    
    agent = BaseAgent(
        genome=genome,
        groq_api_key=config.api.groq_api_key,
        agent_id="niche-discovery-main"
    )
    
    return agent

def discover_niches(market_areas: list, save_results=True):
    """Run niche discovery on multiple market areas"""
    
    print("🔍 NICHE DISCOVERY AGENT")
    print("=" * 70)
    print()
    
    agent = create_niche_discovery_agent()
    print(f"✅ Agent initialized: {agent.agent_id}")
    print()
    
    discoveries = []
    
    for i, market in enumerate(market_areas, 1):
        print(f"[{i}/{len(market_areas)}] Analyzing: {market['area']}")
        print("-" * 70)
        
        try:
            start_time = time.time()
            
            result = agent.act(
                input_data={
                    "market_area": market['area'],
                    "trend_context": market.get('context', ''),
                    "target_revenue": market.get('target_revenue', '$5k-15k/month'),
                    "time_to_market": market.get('time_to_market', '30-60 days')
                },
                action_type="discover_niche"
            )
            
            elapsed = time.time() - start_time
            
            # Extract niche info
            niche_name = "Unknown"
            confidence = 0
            
            if "response" in result and isinstance(result["response"], str):
                try:
                    # Try to parse JSON from response
                    niche_data = json.loads(result["response"])
                    niche_name = niche_data.get("niche_name", "Unknown")
                    confidence = niche_data.get("confidence_score", 0)
                    result = niche_data  # Use parsed data
                except:
                    pass
            elif "niche_name" in result:
                niche_name = result.get("niche_name", "Unknown")
                confidence = result.get("confidence_score", 0)
            
            print(f"✅ Discovered in {elapsed:.1f}s")
            print(f"   📌 Nicho: {niche_name}")
            print(f"   📊 Confianza: {confidence:.0%}")
            
            if "competition" in result:
                comp = result["competition"]
                if isinstance(comp, dict):
                    print(f"   🎯 Competencia: {comp.get('level', 'unknown')}")
            
            print()
            
            discoveries.append({
                "market_area": market['area'],
                "discovery": result,
                "elapsed": elapsed,
                "timestamp": time.time()
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
            discoveries.append({
                "market_area": market['area'],
                "error": str(e),
                "timestamp": time.time()
            })
    
    # Summary
    print("=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    
    successful = sum(1 for d in discoveries if "discovery" in d)
    total = len(discoveries)
    
    print(f"Áreas analizadas: {total}")
    print(f"Nichos descubiertos: {successful}")
    print(f"Success rate: {(successful/total*100) if total > 0 else 0:.1f}%")
    print()
    
    # Best niches by confidence
    if successful > 0:
        print("🏆 TOP NICHOS DESCUBIERTOS:")
        print()
        
        ranked = []
        for d in discoveries:
            if "discovery" in d:
                disc = d["discovery"]
                conf = 0
                
                if isinstance(disc, dict):
                    conf = disc.get("confidence_score", 0)
                    if conf == 0 and "response" in disc:
                        # Try to parse
                        try:
                            parsed = json.loads(disc["response"])
                            conf = parsed.get("confidence_score", 0)
                        except:
                            pass
                
                ranked.append({
                    "area": d["market_area"],
                    "confidence": conf,
                    "discovery": disc
                })
        
        # Sort by confidence
        ranked.sort(key=lambda x: x["confidence"], reverse=True)
        
        for i, item in enumerate(ranked[:3], 1):
            disc = item["discovery"]
            niche_name = "Unknown"
            
            if isinstance(disc, dict):
                niche_name = disc.get("niche_name", "Unknown")
                if niche_name == "Unknown" and "response" in disc:
                    try:
                        parsed = json.loads(disc["response"])
                        niche_name = parsed.get("niche_name", "Unknown")
                    except:
                        pass
            
            print(f"   {i}. {niche_name}")
            print(f"      Área: {item['area']}")
            print(f"      Confianza: {item['confidence']:.0%}")
            print()
    
    # Save results
    if save_results:
        results_path = Path("data/test_results/niche_discovery.json")
        results_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_path, 'w') as f:
            json.dump({
                "timestamp": time.time(),
                "agent_id": agent.agent_id,
                "market_areas_analyzed": len(market_areas),
                "discoveries": discoveries,
                "agent_metrics": {
                    "total_actions": agent.metrics.total_actions,
                    "successful_actions": agent.metrics.successful_actions,
                    "fitness": agent.metrics.get_fitness()
                }
            }, f, indent=2)
        
        print(f"💾 Resultados guardados en: {results_path}")
    
    print()
    return discoveries

if __name__ == "__main__":
    # Market areas to analyze
    markets = [
        {
            "area": "AI automation for small e-commerce stores",
            "context": "Small online stores need automation but can't afford developers",
            "target_revenue": "$5k-15k/month"
        },
        {
            "area": "No-code tools for content creators",
            "context": "Creators want to build apps, websites, automations without coding",
            "target_revenue": "$10k-30k/month"
        },
        {
            "area": "Remote work productivity for distributed teams",
            "context": "Companies struggle with async communication and productivity tracking",
            "target_revenue": "$15k-50k/month"
        },
        {
            "area": "Sustainable tech and green automation",
            "context": "Climate-conscious consumers want eco-friendly tech solutions",
            "target_revenue": "$8k-25k/month"
        },
        {
            "area": "AI-powered personal finance for millennials",
            "context": "Young professionals need help managing money and building wealth",
            "target_revenue": "$10k-40k/month"
        }
    ]
    
    try:
        discoveries = discover_niches(markets)
        sys.exit(0 if len(discoveries) > 0 else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
