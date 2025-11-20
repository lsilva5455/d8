"""
Quick test for GitHub Copilot integration
Tests the ask_about_project function with Groq
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from app.integrations.github_copilot import get_copilot_client

def test_copilot_integration():
    """Test the GitHub Copilot integration"""
    
    print("🧪 Testing GitHub Copilot Integration")
    print("=" * 60)
    print()
    
    # Initialize client
    print("1. Initializing Copilot client...")
    copilot = get_copilot_client()
    print(f"   ✅ Client initialized (enabled: {copilot.enabled})")
    print()
    
    # Test question
    question = "¿Qué es D8?"
    print(f"2. Testing question: '{question}'")
    print("   🧠 Processing...")
    print()
    
    try:
        response = copilot.ask_about_project(question)
        
        print("3. Response received:")
        print("-" * 60)
        print(response)
        print("-" * 60)
        print()
        
        # Validar que la respuesta sea sustancial (>100 caracteres)
        if len(response) < 100:
            print(f"❌ Test FAILED - Response too short ({len(response)} chars)")
            return False
        
        # Verificar errores críticos (no palabras comunes como "error" que pueden estar en contexto)
        critical_errors = ["traceback", "exception occurred", "modulenotfounderror", "has been decommissioned", "lo siento, no puedo"]
        if any(error in response.lower() for error in critical_errors):
            print("❌ Test FAILED - Critical error in response")
            return False
        
        print("✅ Test PASSED - Valid intelligent response received")
        return True
            
    except Exception as e:
        print(f"❌ Test FAILED - Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_copilot_integration()
    sys.exit(0 if success else 1)
