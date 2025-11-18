"""
Gemini API Client
Free tier: 1500 requests/day, 1M tokens/min
"""

import google.generativeai as genai
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Google Gemini API client
    Free for Raspberry Pi deployment
    """
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini client
        
        Models:
        - gemini-2.0-flash-exp: Latest, fastest, FREE
        - gemini-1.5-flash: Stable, fast, FREE
        - gemini-1.5-pro: More capable, FREE (lower limits)
        """
        genai.configure(api_key=api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)
        logger.info(f"🤖 Gemini client initialized: {model}")
    
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
