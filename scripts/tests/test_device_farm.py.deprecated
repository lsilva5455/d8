"""
Test local para Opción B: Device Farm
Simulación de automatización de dispositivos Android
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

def test_device_automation():
    """Test de automatización de dispositivos"""
    
    print("📱 TEST: DEVICE FARM")
    print("=" * 60)
    
    # Create agent genome for device automation
    genome = Genome(
        prompt="""You are a mobile device automation AI agent specialized in Android automation.

Your capabilities:
- Plan multi-step automation sequences
- Generate Appium commands
- Coordinate actions across multiple devices
- Validate UI elements and states
- Handle errors and retries

Always respond in JSON format with these fields:
{
  "action_plan": ["step1", "step2", "step3"],
  "device_id": "target device",
  "commands": [{"action": "click", "element": "id", "params": {}}],
  "validation": {"expected_state": "...", "timeout": 30},
  "estimated_duration": 45
}""",
        fitness=0.0,
        generation=1
    )
    
    # Initialize agent
    agent = BaseAgent(
        genome=genome,
        groq_api_key=config.api.groq_api_key,
        agent_id="device-agent-001"
    )
    
    print(f"✅ Agent initialized: {agent.agent_id[:12]}")
    print()
    
    # Test different automation scenarios
    tests = [
        {
            "name": "Instagram - Login + Post Photo",
            "input": {
                "task": "instagram_automation",
                "actions": ["login", "navigate_to_camera", "upload_photo", "add_caption", "post"],
                "device": "emulator-5554",
                "credentials": {"username": "test_user", "password": "****"},
                "photo_path": "/sdcard/test.jpg",
                "caption": "Testing automation 🤖"
            }
        },
        {
            "name": "WhatsApp - Send Bulk Messages",
            "input": {
                "task": "whatsapp_bulk_send",
                "actions": ["open_app", "search_contact", "send_message", "repeat"],
                "device": "emulator-5555",
                "contacts": ["Contact1", "Contact2", "Contact3"],
                "message": "Hello! This is an automated message."
            }
        },
        {
            "name": "TikTok - View + Like Loop",
            "input": {
                "task": "tiktok_engagement",
                "actions": ["open_app", "scroll_feed", "like_video", "repeat"],
                "device": "emulator-5554",
                "iterations": 20,
                "target_hashtags": ["#ai", "#automation", "#tech"]
            }
        },
        {
            "name": "Multi-Device - Coordinated Posts",
            "input": {
                "task": "multi_device_post",
                "actions": ["login_all", "prepare_content", "post_simultaneously"],
                "devices": ["emulator-5554", "emulator-5555", "emulator-5556"],
                "platforms": ["instagram", "tiktok", "twitter"],
                "content": {"text": "New post!", "media": "/sdcard/image.jpg"}
            }
        },
        {
            "name": "App Testing - E2E Flow",
            "input": {
                "task": "app_testing",
                "actions": ["launch_app", "login", "navigate_features", "perform_actions", "validate", "logout"],
                "device": "emulator-5554",
                "app_package": "com.example.testapp",
                "test_scenarios": ["happy_path", "error_handling", "edge_cases"]
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
                action_type="device_automation"
            )
            
            elapsed = time.time() - start_time
            
            print(f"✅ Plan generated in {elapsed:.2f}s")
            print(f"📋 Automation plan:")
            
            # Show action plan
            if 'action_plan' in result:
                for step_num, step in enumerate(result['action_plan'], 1):
                    print(f"   {step_num}. {step}")
            
            print(f"⏱️  Estimated duration: {result.get('estimated_duration', 'N/A')}s")
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
    results_path = Path("data/test_results/device_farm_test.json")
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
        success = test_device_automation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
