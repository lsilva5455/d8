"""Test simple de Groq para verificar respuesta JSON"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.integrations.groq_client import GroqClient
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = GroqClient(os.getenv('GROQ_API_KEY'), 'llama-3.3-70b-versatile')

# Test 1: JSON simple
print("=" * 60)
print("TEST 1: JSON Simple")
print("=" * 60)

prompt = """Respond with ONLY this JSON structure, no explanations:
{
  "niche_name": "AI Writing Tools",
  "confidence": 85
}"""

try:
    response = client.chat([{'role': 'user', 'content': prompt}], temperature=0.1, max_tokens=500)
    print("\n📥 RESPUESTA RAW:")
    print(response)
    print("\n" + "=" * 60)
    
    # Intentar parsear
    try:
        parsed = json.loads(response)
        print("✅ JSON VÁLIDO")
        print(json.dumps(parsed, indent=2))
    except:
        print("❌ NO ES JSON VÁLIDO")
        print("Intentando extraer...")
        
        # Buscar primer { hasta último }
        first = response.find('{')
        last = response.rfind('}')
        if first != -1 and last != -1:
            extracted = response[first:last+1]
            print(f"\n🔧 EXTRAÍDO: {extracted}")
            try:
                parsed = json.loads(extracted)
                print("✅ EXTRACCIÓN EXITOSA")
                print(json.dumps(parsed, indent=2))
            except:
                print("❌ EXTRACCIÓN FALLÓ")
                
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Niche discovery para Chile
print("\n" + "=" * 60)
print("TEST 2: Niche Discovery - Chile")
print("=" * 60)

prompt2 = """You are a niche discovery expert. Analyze the Chilean market.

Market: "Automatización de ventas para emprendedores chilenos"

OUTPUT ONLY THIS JSON STRUCTURE (no text before or after):
{
  "niche_name": "specific niche name here",
  "confidence": 85,
  "target_geography": "CL",
  "description": "one sentence description"
}"""

try:
    response2 = client.chat([{'role': 'user', 'content': prompt2}], temperature=0.2, max_tokens=500)
    print("\n📥 RESPUESTA RAW:")
    print(response2)
    print("\n" + "=" * 60)
    
    # Intentar parsear
    try:
        parsed2 = json.loads(response2)
        print("✅ JSON VÁLIDO")
        print(json.dumps(parsed2, indent=2))
        
        if parsed2.get("niche_name") == "Unknown":
            print("⚠️ PROBLEMA: niche_name es 'Unknown'")
        else:
            print(f"✅ NICHE REAL: {parsed2.get('niche_name')}")
            
    except:
        print("❌ NO ES JSON VÁLIDO")
        
        # Buscar primer { hasta último }
        first = response2.find('{')
        last = response2.rfind('}')
        if first != -1 and last != -1:
            extracted = response2[first:last+1]
            print(f"\n🔧 EXTRAÍDO:\n{extracted}")
            try:
                parsed2 = json.loads(extracted)
                print("\n✅ EXTRACCIÓN EXITOSA")
                print(json.dumps(parsed2, indent=2, ensure_ascii=False))
                
                if parsed2.get("niche_name") == "Unknown":
                    print("⚠️ PROBLEMA: niche_name es 'Unknown'")
                else:
                    print(f"✅ NICHE REAL: {parsed2.get('niche_name')}")
            except Exception as e:
                print(f"❌ EXTRACCIÓN FALLÓ: {e}")
                
except Exception as e:
    print(f"❌ ERROR: {e}")
