"""
Test del Sistema de Fallback Automático de LLMs
================================================

Este script demuestra el sistema robusto de fallback automático:
1. Groq → Gemini → DeepSeek
2. Detección inteligente de errores
3. Derivación al Congreso cuando todo falla

Author: D8 System
Date: 2025-11-21
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from app.agents.base_agent import BaseAgent
from app.evolution.darwin import Genome
from app.llm_manager_singleton import get_llm_manager
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_fallback_system():
    """Probar sistema de fallback"""
    
    print("\n" + "="*70)
    print("🧪 TEST: Sistema de Fallback Automático de LLMs")
    print("="*70)
    
    # Crear genome de prueba
    genome = Genome(
        prompt="""You are a test agent for the D8 fallback system.
        Respond with JSON containing your analysis.""",
        generation=1
    )
    
    # Crear agente (usará LLM Manager automáticamente)
    print("\n📝 Creando agente de prueba...")
    agent = BaseAgent(genome=genome)
    print(f"✅ Agente creado: {agent.agent_id[:8]}")
    
    # Obtener LLM Manager
    llm_manager = get_llm_manager()
    
    # Mostrar estado inicial
    print("\n📊 Estado inicial de providers:")
    health = llm_manager.get_health_report()
    for provider, status in health["providers"].items():
        available = "✅" if status["is_available"] else "❌"
        print(f"   {available} {provider.upper()}: {status['success_rate']:.1f}% éxito")
    
    # Test 1: Request normal
    print("\n" + "-"*70)
    print("TEST 1: Request normal (debería usar Groq primero)")
    print("-"*70)
    
    result = agent.act(
        input_data={"task": "Analyze the D8 fallback system"},
        action_type="analyze"
    )
    
    if result.get("success") != False:
        provider = result.get("llm_provider", "unknown")
        print(f"✅ Request exitoso usando: {provider.upper()}")
    else:
        print(f"❌ Request falló: {result.get('error')}")
        if result.get("escalated_to_congress"):
            print("🏛️  Problema derivado al Congreso")
    
    time.sleep(2)
    
    # Test 2: Request con rate limit simulado (si Groq falló)
    print("\n" + "-"*70)
    print("TEST 2: Segundo request (puede usar fallback si Groq en cooldown)")
    print("-"*70)
    
    result2 = agent.act(
        input_data={"task": "Test fallback mechanism"},
        action_type="test"
    )
    
    if result2.get("success") != False:
        provider2 = result2.get("llm_provider", "unknown")
        print(f"✅ Request exitoso usando: {provider2.upper()}")
    else:
        print(f"❌ Request falló: {result2.get('error')}")
        if result2.get("escalated_to_congress"):
            print("🏛️  Problema derivado al Congreso")
    
    # Mostrar estado final
    print("\n" + "-"*70)
    print("📊 Estado final de providers:")
    print("-"*70)
    
    health_final = llm_manager.get_health_report()
    print(f"\n📈 Total requests: {health_final['total_requests']}")
    print(f"🏛️  Escalaciones al Congreso: {health_final['congress_escalations']}")
    
    print("\nDetalle por provider:")
    for provider, status in health_final["providers"].items():
        available = "✅" if status["is_available"] else "❌"
        cooldown = "⏳ EN COOLDOWN" if status.get("in_cooldown") else ""
        
        print(f"\n{available} {provider.upper()} {cooldown}")
        print(f"   Requests: {status['total_requests']}")
        print(f"   Fallos: {status['total_failures']}")
        print(f"   Tasa de éxito: {status['success_rate']:.1f}%")
        print(f"   Fallos consecutivos: {status['consecutive_failures']}")
        
        if status.get("last_error_type"):
            print(f"   Último error: {status['last_error_type']}")
    
    # Mostrar escalaciones al Congreso
    if health_final['congress_escalations'] > 0:
        print("\n" + "="*70)
        print("🏛️  ESCALACIONES AL CONGRESO")
        print("="*70)
        
        from pathlib import Path
        escalation_dir = Path.home() / "Documents" / "d8_data" / "llm_fallback"
        
        if escalation_dir.exists():
            escalations = list(escalation_dir.glob("congress_escalation_*.json"))
            print(f"\n📁 {len(escalations)} archivos de escalación encontrados:")
            for file in sorted(escalations)[-3:]:  # Últimas 3
                print(f"   📄 {file.name}")
            
            if escalations:
                print(f"\n💡 Ver detalles en: {escalation_dir}")
    
    print("\n" + "="*70)
    print("✅ Test completado")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        test_fallback_system()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrumpido por usuario")
    except Exception as e:
        logger.error(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
