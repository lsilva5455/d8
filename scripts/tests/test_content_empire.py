"""
Test local para Opción A: Content Empire
Prueba de generación de contenido con agentes D8
"""

import sys
import json
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.base_agent import BaseAgent
from app.evolution.darwin import Genome
from app.config import config

def test_content_generation():
    """Test de generación de contenido"""
    
    print("🎨 TEST: CONTENT EMPIRE")
    print("=" * 60)
    
    # Create agent genome for content creation
    genome = Genome(
        prompt="""You are a creative content AI agent specialized in viral social media posts.

Your capabilities:
- Generate engaging Twitter/X posts (280 chars max)
- Create LinkedIn articles with professional tone
- Write catchy TikTok/Instagram captions
- Generate email marketing copy
- Create trending hashtags

Always respond in JSON format with these fields:
{
  "content": "the generated content",
  "platform": "target platform",
  "hashtags": ["list", "of", "hashtags"],
  "estimated_engagement": "low/medium/high",
  "call_to_action": "CTA text"
}""",
        fitness=0.0,
        generation=1
    )
    
    # Initialize agent
    agent = BaseAgent(
        genome=genome,
        groq_api_key=config.api.groq_api_key,
        agent_id="content-agent-001"
    )
    
    print(f"✅ Agent initialized: {agent.agent_id[:12]}")
    print()
    
    # Test different content types
    tests = [
        {
            "name": "Twitter Post - AI Tools",
            "input": {
                "task": "create_tweet",
                "topic": "New AI coding assistant that writes tests automatically",
                "tone": "excited",
                "target_audience": "developers"
            }
        },
        {
            "name": "LinkedIn Article - Startup",
            "input": {
                "task": "create_linkedin_post",
                "topic": "How to validate your startup idea in 48 hours",
                "tone": "professional",
                "target_audience": "entrepreneurs"
            }
        },
        {
            "name": "TikTok Caption - Tech",
            "input": {
                "task": "create_tiktok_caption",
                "topic": "5 coding shortcuts that will blow your mind",
                "tone": "casual",
                "target_audience": "young developers"
            }
        },
        {
            "name": "Email Marketing - SaaS",
            "input": {
                "task": "create_email",
                "topic": "New feature launch: Real-time collaboration",
                "tone": "friendly",
                "target_audience": "existing customers"
            }
        },
        {
            "name": "Instagram Hashtags",
            "input": {
                "task": "generate_hashtags",
                "topic": "AI automation tools for small business",
                "count": 10
            }
        }
    ]
    
    results = []
    
    for i, test in enumerate(tests, 1):
        print(f"[{i}/{len(tests)}] {test['name']}")
        print("-" * 60)
        
        try:
            start_time = time.time()
            
            # Execute action
            result = agent.act(
                input_data=test['input'],
                action_type="generate_content"
            )
            
            elapsed = time.time() - start_time
            
            print(f"✅ Generated in {elapsed:.2f}s")
            print(f"📝 Content preview:")
            print(json.dumps(result, indent=2)[:500] + "...")
            print()
            
            results.append({
                "test": test['name'],
                "success": True,
                "elapsed": elapsed,
                "result": result
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
            results.append({
                "test": test['name'],
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    successful = sum(1 for r in results if r.get('success'))
    total = len(results)
    success_rate = (successful / total) * 100 if total > 0 else 0
    
    print(f"Tests ejecutados: {total}")
    print(f"Exitosos: {successful}")
    print(f"Fallidos: {total - successful}")
    print(f"Success rate: {success_rate:.1f}%")
    print()
    
    # Agent metrics
    print("📈 MÉTRICAS DEL AGENTE")
    print(f"Total acciones: {agent.metrics.total_actions}")
    print(f"Acciones exitosas: {agent.metrics.successful_actions}")
    print(f"Fitness score: {agent.metrics.get_fitness():.2f}")
    print()
    
    # Save results
    results_path = Path("data/test_results/content_empire_test.json")
    results_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(results_path, 'w') as f:
        json.dump({
            "timestamp": time.time(),
            "agent_id": agent.agent_id,
            "summary": {
                "total": total,
                "successful": successful,
                "success_rate": success_rate
            },
            "tests": results,
            "agent_metrics": {
                "total_actions": agent.metrics.total_actions,
                "successful_actions": agent.metrics.successful_actions,
                "fitness": agent.metrics.get_fitness()
            }
        }, f, indent=2)
    
    print(f"💾 Resultados guardados en: {results_path}")
    
    return success_rate == 100.0

if __name__ == "__main__":
    try:
        success = test_content_generation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
