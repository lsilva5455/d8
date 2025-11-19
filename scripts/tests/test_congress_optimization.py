"""
Congreso de Agentes - Optimización de Niche Discovery
Los agentes debaten y evolucionan el sistema de descubrimiento de nichos
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent))

from app.agents.base_agent import BaseAgent
from app.evolution.darwin import Genome
from app.config import config

def create_congress_member(role: str) -> BaseAgent:
    """Create a congress member with specific optimization role"""
    
    roles = {
        "strategist": """You are a Business Strategy Optimizer for AI agents.
        
Your role: Analyze niche discovery strategies and suggest improvements for:
- Market positioning
- Revenue maximization
- Risk mitigation
- Scalability

Provide strategic recommendations to improve the niche discovery agent's performance.""",
        
        "analyst": """You are a Data Analysis Optimizer for AI agents.

Your role: Analyze niche discovery methodologies and suggest improvements for:
- Market research accuracy
- Competition analysis depth
- Trend identification
- Data validation

Provide analytical improvements to enhance the niche discovery agent's insights.""",
        
        "marketer": """You are a Marketing Optimization Specialist for AI agents.

Your role: Analyze niche monetization strategies and suggest improvements for:
- Content strategy effectiveness
- Platform selection
- Audience targeting
- Conversion optimization

Provide marketing enhancements to boost the niche discovery agent's commercial value.""",
        
        "innovator": """You are an Innovation Architect for AI agents.

Your role: Analyze niche discovery approaches and suggest improvements for:
- Methodology innovation
- Tool integration
- Automation opportunities
- Competitive advantages

Provide innovative ideas to revolutionize the niche discovery agent's capabilities.""",
        
        "validator": """You are a Quality Assurance Specialist for AI agents.

Your role: Analyze niche discovery outputs and suggest improvements for:
- Accuracy verification
- Confidence scoring
- Error detection
- Result validation

Provide quality improvements to ensure the niche discovery agent's reliability."""
    }
    
    base_prompt = roles.get(role, roles["strategist"])
    
    prompt = f"""{base_prompt}

When analyzing a niche discovery result, provide optimization recommendations in JSON format:
{{
  "role": "{role}",
  "analysis": "what you observed in the current discovery",
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "recommendations": [
    {{"priority": "high/medium/low", "suggestion": "specific improvement", "expected_impact": "outcome"}},
    {{"priority": "high/medium/low", "suggestion": "specific improvement", "expected_impact": "outcome"}}
  ],
  "metrics_to_track": ["metric1", "metric2"],
  "implementation_complexity": "low/medium/high",
  "confidence": 0.85
}}"""
    
    genome = Genome(prompt=prompt, fitness=0.0, generation=1)
    
    agent = BaseAgent(
        genome=genome,
        groq_api_key=config.api.groq_api_key,
        agent_id=f"congress-{role}"
    )
    
    return agent

def run_optimization_congress(niche_discovery_results: Dict[str, Any]):
    """Run congress to optimize niche discovery system"""
    
    print("🏛️  CONGRESO DE OPTIMIZACIÓN - NICHE DISCOVERY")
    print("=" * 70)
    print()
    
    # Create congress members
    roles = ["strategist", "analyst", "marketer", "innovator", "validator"]
    members = []
    
    print("🤖 Inicializando miembros del congreso...")
    print()
    
    for role in roles:
        agent = create_congress_member(role)
        members.append({
            "role": role,
            "agent": agent
        })
        print(f"   ✅ {role.upper()}: {agent.agent_id}")
    
    print()
    print("=" * 70)
    print()
    
    # Each member analyzes the niche discovery results
    print("📋 ANÁLISIS DE RESULTADOS ACTUALES")
    print("-" * 70)
    print()
    
    optimizations = []
    
    for member in members:
        role = member['role']
        agent = member['agent']
        
        print(f"   🔍 {role.upper()} analizando...", end=" ")
        
        try:
            start_time = time.time()
            
            result = agent.act(
                input_data={
                    "niche_discovery_results": json.dumps(niche_discovery_results, indent=2)[:1000],  # Truncate for context
                    "system_metrics": {
                        "discoveries": len(niche_discovery_results.get("discoveries", [])),
                        "success_rate": niche_discovery_results.get("agent_metrics", {}).get("successful_actions", 0)
                    }
                },
                action_type="optimize_system"
            )
            
            elapsed = time.time() - start_time
            
            print(f"✅ ({elapsed:.1f}s)")
            
            # Extract recommendations count
            rec_count = 0
            if isinstance(result, dict):
                if "recommendations" in result:
                    rec_count = len(result.get("recommendations", []))
                elif "response" in result:
                    try:
                        parsed = json.loads(result["response"])
                        rec_count = len(parsed.get("recommendations", []))
                    except:
                        pass
            
            print(f"      → {rec_count} recomendaciones propuestas")
            print()
            
            optimizations.append({
                "role": role,
                "agent_id": agent.agent_id,
                "analysis": result,
                "elapsed": elapsed
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
    
    # Consensus and prioritization
    print("=" * 70)
    print("💡 CONSENSO DEL CONGRESO")
    print("=" * 70)
    print()
    
    all_recommendations = []
    
    for opt in optimizations:
        analysis = opt["analysis"]
        if isinstance(analysis, dict):
            recs = analysis.get("recommendations", [])
            if isinstance(recs, list):
                for rec in recs:
                    if isinstance(rec, dict):
                        all_recommendations.append({
                            "from_role": opt["role"],
                            "priority": rec.get("priority", "medium"),
                            "suggestion": rec.get("suggestion", ""),
                            "impact": rec.get("expected_impact", "")
                        })
    
    # Group by priority
    high_priority = [r for r in all_recommendations if r["priority"] == "high"]
    medium_priority = [r for r in all_recommendations if r["priority"] == "medium"]
    low_priority = [r for r in all_recommendations if r["priority"] == "low"]
    
    print(f"Total recomendaciones: {len(all_recommendations)}")
    print(f"   🔴 Alta prioridad: {len(high_priority)}")
    print(f"   🟡 Media prioridad: {len(medium_priority)}")
    print(f"   🟢 Baja prioridad: {len(low_priority)}")
    print()
    
    # Show top recommendations
    print("🎯 TOP RECOMENDACIONES (Alta Prioridad):")
    print()
    
    for i, rec in enumerate(high_priority[:5], 1):
        print(f"   {i}. [{rec['from_role'].upper()}] {rec['suggestion']}")
        print(f"      Impacto esperado: {rec['impact']}")
        print()
    
    # Summary
    print("=" * 70)
    print("📊 RESUMEN DEL CONGRESO")
    print("=" * 70)
    print()
    
    print(f"Miembros participantes: {len(members)}")
    print(f"Análisis completados: {len(optimizations)}")
    print(f"Recomendaciones totales: {len(all_recommendations)}")
    print()
    
    print("📈 SIGUIENTES PASOS:")
    print("   1. Implementar recomendaciones de alta prioridad")
    print("   2. Actualizar el genoma del agente de niche discovery")
    print("   3. Re-ejecutar descubrimiento con mejoras")
    print("   4. Medir impacto de optimizaciones")
    print()
    
    # Save congress results
    results_path = Path("data/test_results/optimization_congress.json")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_path, 'w') as f:
        json.dump({
            "timestamp": time.time(),
            "congress_members": [
                {"role": m['role'], "agent_id": m['agent'].agent_id}
                for m in members
            ],
            "analyzed_system": "niche_discovery",
            "optimizations": optimizations,
            "recommendations": {
                "high_priority": high_priority,
                "medium_priority": medium_priority,
                "low_priority": low_priority,
                "total": len(all_recommendations)
            }
        }, f, indent=2)
    
    print(f"💾 Resultados guardados en: {results_path}")
    print()
    
    return optimizations

if __name__ == "__main__":
    print("⚠️  Este script requiere resultados previos de niche_discovery_agent.py")
    print()
    print("Ejecuta primero:")
    print("   python niche_discovery_agent.py")
    print()
    print("Luego:")
    print("   python test_congress_optimization.py")
    print()
    
    # Try to load previous results
    results_path = Path("data/test_results/niche_discovery.json")
    
    if results_path.exists():
        print("✅ Encontrados resultados previos, ejecutando congreso...")
        print()
        
        with open(results_path, 'r') as f:
            niche_results = json.load(f)
        
        try:
            run_optimization_congress(niche_results)
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        print("❌ No se encontraron resultados previos")
        print(f"   Esperados en: {results_path}")
        sys.exit(1)
