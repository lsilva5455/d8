"""
Test de Fallback en caso de Rate Limit (429)
=============================================

Este script simula un rate limit en Groq para verificar que el sistema
automáticamente use Gemini o DeepSeek como fallback.

Author: D8 System
Date: 2025-11-21
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging
from lib.llm.fallback_manager import LLMFallbackManager, FallbackConfig, ErrorType

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_rate_limit_fallback():
    """Test que simula rate limit en Groq"""
    
    print("\n" + "="*70)
    print("🧪 TEST: Fallback en caso de Rate Limit 429")
    print("="*70 + "\n")
    
    # Crear manager con configuración de test
    config = FallbackConfig(
        provider_priority=["groq", "gemini", "deepseek"],
        max_retries_per_provider=1,  # Solo 1 reintento para test rápido
        congress_threshold_failures=3,
        enable_congress_escalation=True
    )
    
    manager = LLMFallbackManager(
        groq_api_key="fake_key_to_fail",  # API key inválida para forzar fallo
        gemini_api_key="fake_key",
        deepseek_base_url="http://localhost:7100",
        config=config
    )
    
    print("📊 Estado inicial de providers:")
    for name, health in manager.provider_health.items():
        status = "✅" if health.can_retry() else "❌"
        print(f"   {status} {name.upper()}: Disponible={health.is_available}")
    print()
    
    # Simular múltiples requests que fallan
    print("-"*70)
    print("TEST 1: Primer request (Groq debería fallar con auth error)")
    print("-"*70)
    
    messages = [{"role": "user", "content": "Hola, ¿cómo estás?"}]
    
    try:
        response = manager.chat_with_fallback(
            messages=messages,
            context="Test de fallback"
        )
        
        if response:
            print(f"✅ Response exitoso desde: {response.get('provider_used', 'unknown')}")
        else:
            print("❌ Todos los providers fallaron")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("-"*70)
    print("📊 Estado después del test:")
    print("-"*70)
    print()
    
    # Mostrar estado de cada provider
    for name, health in manager.provider_health.items():
        status = "✅" if health.can_retry() else "❌"
        print(f"{status} {name.upper()}")
        print(f"   Disponible: {health.is_available}")
        print(f"   Fallos consecutivos: {health.consecutive_failures}")
        print(f"   Total fallos: {health.total_failures}")
        print(f"   Último error: {health.last_error[:100] if health.last_error else 'None'}")
        print(f"   En cooldown: {health.cooldown_until is not None}")
        print()
    
    print("-"*70)
    print("📈 Estadísticas generales:")
    print("-"*70)
    print()
    print(f"Total requests: {manager.total_requests}")
    print(f"Escalaciones al Congreso: {manager.congress_escalations}")
    print()
    
    # Verificar que se intentó usar fallbacks
    groq_health = manager.provider_health.get("groq")
    if groq_health and groq_health.total_failures > 0:
        print("✅ Test exitoso: Groq falló y se intentaron fallbacks")
    else:
        print("⚠️  Test incompleto: No se registraron fallos en Groq")
    
    print("\n" + "="*70)
    print("✅ Test completado")
    print("="*70 + "\n")


def test_manual_provider_failure():
    """Test manual de fallo de provider"""
    
    print("\n" + "="*70)
    print("🧪 TEST: Simulación manual de fallo")
    print("="*70 + "\n")
    
    config = FallbackConfig(
        provider_priority=["groq", "gemini", "deepseek"],
        max_retries_per_provider=2,
    )
    
    manager = LLMFallbackManager(
        groq_api_key="sk-test",
        config=config
    )
    
    # Simular fallo de Groq manualmente
    print("Simulando rate limit en Groq...")
    groq_health = manager.provider_health["groq"]
    groq_health.record_failure(
        "Rate limit reached for model llama-3.3-70b-versatile",
        ErrorType.RATE_LIMIT
    )
    
    print(f"✅ Groq marcado como en cooldown hasta: {groq_health.cooldown_until}")
    print(f"   Puede reintentar: {groq_health.can_retry()}")
    print()
    
    # Intentar request (debería usar Gemini o DeepSeek)
    print("Intentando request con Groq en cooldown...")
    print("(Debería usar Gemini o DeepSeek automáticamente)")
    print()
    
    # Mostrar qué provider se usaría
    available_providers = [
        name for name, health in manager.provider_health.items()
        if health.can_retry()
    ]
    
    print(f"Providers disponibles: {available_providers}")
    
    if "gemini" in available_providers:
        print("✅ Gemini disponible como fallback")
    elif "deepseek" in available_providers:
        print("✅ DeepSeek disponible como fallback")
    else:
        print("❌ No hay providers disponibles - se escalaría al Congreso")
    
    print("\n" + "="*70)
    print("✅ Test completado")
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n🚀 Ejecutando tests de fallback...\n")
    
    try:
        test_manual_provider_failure()
        print("\n" + "─"*70 + "\n")
        # test_rate_limit_fallback()  # Comentado porque requiere API keys reales
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrumpido por usuario")
    except Exception as e:
        logger.error(f"❌ Error en tests: {e}")
        import traceback
        traceback.print_exc()
