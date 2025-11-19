"""
Gemini API Client
Free tier: 1500 requests/day, 1M tokens/min
"""

import google.generativeai as genai
from typing import List, Dict, Optional
import logging
import json
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Google Gemini API client
    Free for Raspberry Pi deployment
    """
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp", rpm_limit: int = 15):
        """
        Initialize Gemini client
        
        Models:
        - gemini-2.0-flash-exp: Latest, fastest, FREE (15 RPM)
        - gemini-1.5-flash: Stable, fast, FREE (15 RPM)
        - gemini-1.5-pro: More capable, FREE (2 RPM)
        
        Args:
            rpm_limit: Requests per minute limit (default 15 for free tier)
        """
        genai.configure(api_key=api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)
        self.rpm_limit = rpm_limit
        self.min_interval = 60.0 / rpm_limit  # Seconds between requests
        self.last_request_time = None
        logger.info(f"🤖 Gemini client initialized: {model} (Rate: {rpm_limit} RPM, interval: {self.min_interval:.1f}s)")
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.8,
        max_tokens: int = 1000
    ) -> str:
        """
        Send chat completion request
        
        Args:
            messages: List of {"role": "user/model", "content": "..."}
            model: Override default model
            temperature: 0.0-2.0
            max_tokens: Max response length
            
        Returns:
            Generated text
        """
        self._wait_for_rate_limit()
        
        try:
            # Convert messages to Gemini format
            chat = self.model.start_chat(history=[])
            
            # Send messages
            for msg in messages[:-1]:  # History
                if msg['role'] == 'system':
                    continue  # Gemini doesn't have system role
                elif msg['role'] == 'user':
                    chat.send_message(msg['content'])
            
            # Final message
            final_message = messages[-1]['content']
            
            # Add system message to final prompt if exists
            system_msgs = [m['content'] for m in messages if m['role'] == 'system']
            if system_msgs:
                final_message = f"{system_msgs[0]}\n\n{final_message}"
            
            # Generate
            response = chat.send_message(
                final_message,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        max_tokens: int = 1000
    ) -> str:
        """
        Simple text generation
        
        Args:
            prompt: Input text
            temperature: 0.0-2.0
            max_tokens: Max response length
            
        Returns:
            Generated text
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise
    
    def generate_json(
        self,
        prompt: str,
        temperature: float = 0.4,
        max_tokens: int = 2500
    ) -> dict:
        """
        Generate structured JSON output
        
        Args:
            prompt: Input text (should request JSON)
            temperature: 0.0-2.0 (lower for more structured)
            max_tokens: Max response length
            
        Returns:
            Parsed JSON dict
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    response_mime_type="application/json"  # Force JSON mode
                )
            )
            
            # Parse JSON response
            return json.loads(response.text)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            logger.error(f"Raw response: {response.text}")
            
            # Try to extract JSON from response
            import re
            first_brace = response.text.find('{')
            last_brace = response.text.rfind('}')
            if first_brace != -1 and last_brace != -1:
                try:
                    return json.loads(response.text[first_brace:last_brace+1])
                except:
                    pass
            
            raise
            
        except Exception as e:
            logger.error(f"Gemini JSON generation error: {e}")
            raise


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Test chat
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    response = client.chat(messages)
    print(response)
