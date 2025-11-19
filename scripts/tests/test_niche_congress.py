"""
Test de Niche Discovery - Congreso de Agentes
Múltiples agentes analizan nichos y debaten sobre los mejores
"""

import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.base_agent import BaseAgent
from app.evolution.darwin import Genome
from app.config import config

def create_niche_analyst_genome(specialty: str) -> Genome:
    """Create a genome for a niche analyst with specific specialty"""
    
    specialties = {
        "tech": """You are a tech niche discovery expert. You identify emerging technologies, 
        developer tools, AI products, and tech trends with high monetization potential.""",
        
        "lifestyle": """You are a lifestyle niche expert. You identify wellness, productivity, 
        personal development, and lifestyle trends that resonate with modern audiences.""",
        
        "business": """You are a business niche expert. You identify B2B opportunities, 
        startup trends, entrepreneurship niches, and business automation opportunities.""",
        
        "creative": """You are a creative niche expert. You identify content creation tools, 
        design trends, creative automation, and artistic niches with commercial potential.""",
        
        "finance": """You are a finance niche expert. You identify fintech, investment tools, 
        crypto opportunities, and financial automation niches."""
    }
    
    base_prompt = specialties.get(specialty, specialties["tech"])
    
    prompt = f"""{base_prompt}

Your task is to analyze potential niches and provide detailed insights.

CRITICAL: You MUST respond with ONLY a valid JSON object. Do not include any other text.

The JSON format MUST be exactly:
{{
  "niche_name": "specific niche name",
  "description": "what it is",
  "target_audience": "who wants this",
  "monetization": ["method1", "method2", "method3"],
  "competition": "low/medium/high",
  "potential_revenue": "estimated monthly in USD",
  "content_ideas": ["idea1", "idea2", "idea3"],
  "keywords": ["kw1", "kw2", "kw3"],
  "urgency": "why now",
  "confidence_score": 0.85
}}

Example valid response:
{{
  "niche_name": "AI-Powered Email Automation for Small E-commerce",
  "description": "Automated email marketing tools specifically designed for small online stores",
  "target_audience": "E-commerce owners with 10-100 orders per month",
  "monetization": ["SaaS subscription", "Affiliate marketing", "Done-for-you services"],
  "competition": "medium",
  "potential_revenue": "$5,000-15,000 per month",
  "content_ideas": ["Email automation tutorials", "Case studies", "Template library"],
  "keywords": ["email automation", "e-commerce", "small business", "AI marketing"],
  "urgency": "Small e-commerce is booming post-pandemic and owners need automation",
  "confidence_score": 0.88
}}

Remember: ONLY return the JSON object, nothing else."""
    
    return Genome(prompt=prompt, fitness=0.0, generation=1)

def run_niche_congress():
    """Run a congress of agents to discover and debate niches"""
    
    print("🏛️  CONGRESO DE AGENTES - NICHE DISCOVERY")
    print("=" * 70)
    print()
    
    # Create agents with different specialties
    specialties = ["tech", "lifestyle", "business", "creative", "finance"]
    agents = []
    
    print("🤖 Inicializando agentes del congreso...")
    print()
    
    for specialty in specialties:
        genome = create_niche_analyst_genome(specialty)
        agent = BaseAgent(
            genome=genome,
            groq_api_key=config.api.groq_api_key,
            agent_id=f"niche-analyst-{specialty}"
        )
        agents.append({
            "specialty": specialty,
            "agent": agent
        })
        print(f"   ✅ {specialty.upper()} Analyst: {agent.agent_id[:16]}")
    
    print()
    print("=" * 70)
    print()
    
    # Topics to analyze
    topics = [
        {
            "query": "AI automation tools for small businesses",
            "context": "Post-GPT era, businesses want to automate without coding"
        },
        {
            "query": "Remote work productivity solutions",
            "context": "Hybrid work is permanent, people need better tools"
        },
        {
            "query": "No-code app builders for creators",
            "context": "Content creators want to build apps without developers"
        },
        {
            "query": "Sustainable tech and green automation",
            "context": "Climate awareness is rising, people want eco-friendly tech"
        }
    ]
    
    all_results = []
    
    for topic_num, topic in enumerate(topics, 1):
        print(f"📋 TEMA {topic_num}/{len(topics)}: {topic['query']}")
        print(f"   Contexto: {topic['context']}")
        print("-" * 70)
        print()
        
        topic_results = []
        
        # Each agent analyzes the topic
        for agent_info in agents:
            specialty = agent_info['specialty']
            agent = agent_info['agent']
            
            print(f"   🔍 {specialty.upper()} está analizando...", end=" ")
            
            try:
                start_time = time.time()
                
                result = agent.act(
                    input_data={
                        "task": "Analyze this niche opportunity and provide a complete analysis",
                        "niche_topic": topic['query'],
                        "market_context": topic['context'],
                        "your_specialty": specialty
                    },
                    action_type="niche_analysis"
                )
                
                elapsed = time.time() - start_time
                
                print(f"✅ ({elapsed:.1f}s)")
                
                # Show brief summary
                niche_name = result.get('niche_name', 'Unknown')
                confidence = result.get('confidence_score', 0)
                competition = result.get('competition', 'unknown')
                
                print(f"      → Nicho: {niche_name}")
                print(f"      → Confianza: {confidence:.0%} | Competencia: {competition}")
                print()
                
                topic_results.append({
                    "specialty": specialty,
                    "agent_id": agent.agent_id,
                    "analysis": result,
                    "elapsed": elapsed
                })
                
            except Exception as e:
                print(f"❌ Error: {e}")
                print()
        
        # Consensus analysis
        print("   💬 CONSENSO DEL CONGRESO:")
        print()
        
        # Calculate average confidence
        confidences = [r['analysis'].get('confidence_score', 0) for r in topic_results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Competition analysis
        competitions = [r['analysis'].get('competition', 'medium') for r in topic_results]
        competition_votes = {c: competitions.count(c) for c in set(competitions)}
        
        print(f"      Confianza promedio: {avg_confidence:.0%}")
        print(f"      Competencia: {competition_votes}")
        print()
        
        # Collect all monetization ideas
        all_monetization = []
        for r in topic_results:
            all_monetization.extend(r['analysis'].get('monetization', []))
        
        unique_monetization = list(set(all_monetization))[:5]
        print(f"      Top monetization ideas:")
        for i, idea in enumerate(unique_monetization, 1):
            print(f"         {i}. {idea}")
        
        print()
        print("=" * 70)
        print()
        
        all_results.append({
            "topic": topic,
            "analyses": topic_results,
            "consensus": {
                "avg_confidence": avg_confidence,
                "competition": competition_votes,
                "monetization_ideas": unique_monetization
            }
        })
    
    # Final summary
    print("📊 RESUMEN DEL CONGRESO")
    print("=" * 70)
    print()
    
    total_analyses = sum(len(r['analyses']) for r in all_results)
    total_agents = len(agents)
    
    print(f"Agentes participantes: {total_agents}")
    print(f"Temas analizados: {len(topics)}")
    print(f"Total análisis: {total_analyses}")
    print()
    
    print("🏆 MEJOR NICHO POR CONFIANZA:")
    
    best_niche = None
    best_confidence = 0
    
    for result in all_results:
        for analysis in result['analyses']:
            conf = analysis['analysis'].get('confidence_score', 0)
            if conf > best_confidence:
                best_confidence = conf
                best_niche = {
                    "topic": result['topic']['query'],
                    "niche": analysis['analysis'].get('niche_name', 'Unknown'),
                    "specialty": analysis['specialty'],
                    "confidence": conf,
                    "revenue": analysis['analysis'].get('potential_revenue', 'N/A'),
                    "competition": analysis['analysis'].get('competition', 'unknown')
                }
    
    if best_niche:
        print(f"   📌 {best_niche['niche']}")
        print(f"      Analizado por: {best_niche['specialty'].upper()}")
        print(f"      Tema: {best_niche['topic']}")
        print(f"      Confianza: {best_niche['confidence']:.0%}")
        print(f"      Revenue potencial: {best_niche['revenue']}")
        print(f"      Competencia: {best_niche['competition']}")
    
    print()
    
    # Save results
    results_path = Path("data/test_results/niche_congress.json")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_path, 'w') as f:
        json.dump({
            "timestamp": time.time(),
            "congress_participants": [
                {"specialty": a['specialty'], "agent_id": a['agent'].agent_id}
                for a in agents
            ],
            "topics_analyzed": topics,
            "results": all_results,
            "best_niche": best_niche,
            "summary": {
                "total_agents": total_agents,
                "total_topics": len(topics),
                "total_analyses": total_analyses
            }
        }, f, indent=2)
    
    print(f"💾 Resultados completos guardados en: {results_path}")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = run_niche_congress()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
