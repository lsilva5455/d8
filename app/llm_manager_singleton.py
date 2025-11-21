"""
Global LLM Manager Singleton
Instancia única del LLMFallbackManager para todo el sistema D8
"""

import os
from typing import Optional, Any
from lib.llm import LLMFallbackManager, FallbackConfig
import logging

logger = logging.getLogger(__name__)

# Singleton instance
_llm_manager_instance: Optional[LLMFallbackManager] = None


def get_llm_manager(congress_system: Optional[Any] = None) -> LLMFallbackManager:
    """
    Obtener instancia única del LLM Manager
    
    Args:
        congress_system: Sistema de propuestas del Congreso (opcional)
    
    Returns:
        Instancia global de LLMFallbackManager
    """
    global _llm_manager_instance
    
    if _llm_manager_instance is None:
        logger.info("🔧 Inicializando LLM Fallback Manager global...")
        
        # Cargar API keys desde environment
        groq_key = os.getenv("GROQ_API_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        deepseek_url = os.getenv("DEEPSEEK_BASE_URL", "http://localhost:7100")
        
        # Configuración personalizada
        config = FallbackConfig(
            provider_priority=["groq", "gemini", "deepseek"],
            max_retries_per_provider=2,
            congress_threshold_failures=10,
            congress_threshold_repeated_error=5,
            enable_congress_escalation=True
        )
        
        _llm_manager_instance = LLMFallbackManager(
            groq_api_key=groq_key,
            gemini_api_key=gemini_key,
            deepseek_base_url=deepseek_url,
            config=config,
            congress_proposal_system=congress_system
        )
        
        logger.info("✅ LLM Fallback Manager global inicializado")
    
    # Actualizar congreso si se pasa uno nuevo
    if congress_system and _llm_manager_instance.congress_system is None:
        _llm_manager_instance.congress_system = congress_system
        logger.info("✅ Sistema de Congreso vinculado al LLM Manager")
    
    return _llm_manager_instance


def reset_llm_manager():
    """Resetear instancia (útil para tests)"""
    global _llm_manager_instance
    _llm_manager_instance = None
    logger.info("🔄 LLM Manager reseteado")
