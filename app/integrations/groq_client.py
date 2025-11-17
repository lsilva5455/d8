"""
Groq Client Integration
Fast, low-cost inference for agent actions
"""

from groq import Groq
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class GroqClient:
    """Wrapper for Groq API with error handling and retries"""
    
    def __init__(self, api_key: str, model: str = "mixtral-8x7b-32768"):
        self.client = Groq(api_key=api_key)
        self.model = model
        logger.info(f"✅ Groq client initialized with model: {model}")
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             temperature: float = 0.7,
             max_tokens: int = 2000,
             json_mode: bool = True) -> Dict[str, Any]:
        """
        Send chat completion request to Groq
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            json_mode: Force JSON output
        
        Returns:
            Dict with 'content', 'tokens_used', 'model'
        """
        try:
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if json_mode:
                params["response_format"] = {"type": "json_object"}
            
            response = self.client.chat.completions.create(**params)
            
            content = response.choices[0].message.content
            
            # Parse JSON if json_mode is enabled
            if json_mode:
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON response, returning raw text")
            
            return {
                "content": content,
                "tokens_used": response.usage.total_tokens,
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            raise
    
    def estimate_cost(self, tokens: int) -> float:
        """
        Estimate cost in USD for given token count
        Mixtral pricing: ~$0.24 per 1M tokens (input) / $0.24 per 1M (output)
        """
        cost_per_million = 0.24
        return (tokens / 1_000_000) * cost_per_million
