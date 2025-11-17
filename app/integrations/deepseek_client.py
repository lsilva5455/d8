"""
DeepSeek Client Integration
Local LLM for evolution (crossover & mutation) - Zero API cost
"""

import requests
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """Client for DeepSeek running locally via Ollama"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "deepseek-coder:33b"):
        self.base_url = base_url
        self.model = model
        self._validate_connection()
    
    def _validate_connection(self) -> None:
        """Verify Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info(f"✅ Connected to DeepSeek at {self.base_url}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Cannot connect to Ollama: {e}")
            raise ConnectionError(
                f"Ollama not reachable at {self.base_url}. "
                "Start it with: ollama serve"
            )
    
    def generate(self, 
                 prompt: str, 
                 max_tokens: int = 1000,
                 temperature: float = 0.7) -> str:
        """
        Generate completion from DeepSeek
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        
        Returns:
            Generated text
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                },
                timeout=120  # Evolution can take time
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        
        except Exception as e:
            logger.error(f"DeepSeek generation failed: {e}")
            raise
    
    def check_model_exists(self) -> bool:
        """Check if DeepSeek model is downloaded"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            models = response.json().get("models", [])
            return any(self.model in m.get("name", "") for m in models)
        except:
            return False
