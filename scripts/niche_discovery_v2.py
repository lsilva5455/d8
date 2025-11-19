"""
Niche Discovery Agent - Multi-GEO con Rate Limiting y Retry
Versión mejorada con:
- Detección automática de 429 (rate limits)
- Retry automático con exponential backoff
- Validación de "Unknown" como error
- Barra de progreso con tiempo estimado
- Rate limiting de Gemini (15 RPM)
"""

import sys
import json
import time
import re
from pathlib import Path
from datetime import datetime, timedelta
from tqdm import tqdm

# Agregar raíz del proyecto al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.base_agent import BaseAgent
from app.evolution.darwin import Genome
from app.config import config

# Configuración de rate limiting
GEMINI_RPM = 15  # Requests per minute
MIN_INTERVAL_GEMINI = 60.0 / GEMINI_RPM  # 4 segundos entre requests

last_request_time = None

def wait_for_rate_limit():
    """Esperar el intervalo necesario entre requests para respetar rate limits"""
    global last_request_time
    
    if last_request_time is not None:
        elapsed = time.time() - last_request_time
        if elapsed < MIN_INTERVAL_GEMINI:
            wait_time = MIN_INTERVAL_GEMINI - elapsed
            print(f"   ⏳ Rate limiting: waiting {wait_time:.1f}s")
            time.sleep(wait_time)
    
    last_request_time = time.time()

def discover_niche_with_retry(agent: BaseAgent, market_area: str, geography: str, max_retries: int = 5) -> dict:
    """
    Descubre nicho con retry automático si detecta Unknown o error 429
    
    Args:
        agent: BaseAgent configurado
        market_area: Área de mercado a analizar
        geography: Geografía objetivo (USA, ES, CL, Multi-geo)
        max_retries: Máximo número de intentos
    
    Returns:
        dict con result o error
    """
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Esperar rate limit antes de hacer request
            wait_for_rate_limit()
            
            start_time = time.time()
            
            # Hacer la consulta
            result = agent.act({
                "market_area": market_area,
                "target_geography": geography,
                "action": "discover_profitable_niche"
            }, action_type="discover_niche")
            
            elapsed = time.time() - start_time
            
            # Verificar si es éxito
            if not result.get("success", True):
                error = result.get("error", "")
                
                # Detectar 429 o rate limit
                if "429" in error or "rate" in error.lower() or "quota" in error.lower():
                    retry_count += 1
                    wait_time = min(2 ** retry_count * 5, 60)  # Exponential backoff: 5s, 10s, 20s, 40s, 60s
                    print(f"   ⚠️  Rate limit detected (429), retry {retry_count}/{max_retries}")
                    print(f"   ⏳ Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return {"success": False, "error": error, "elapsed": elapsed}
            
            # Verificar si el nicho es "Unknown" (error)
            niche_name = result.get("niche_name", "")
            if niche_name.lower() in ["unknown", "unknownniche", ""]:
                retry_count += 1
                wait_time = min(2 ** retry_count * 3, 30)  # Exponential backoff más suave
                print(f"   ⚠️  Detected 'Unknown' niche (likely rate limit), retry {retry_count}/{max_retries}")
                print(f"   ⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            
            # Success!
            return {
                "success": True,
                "discovery": result,
                "elapsed": elapsed
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # Detectar 429 en exception
            if "429" in error_msg or "rate" in error_msg.lower() or "quota" in error_msg.lower():
                retry_count += 1
                wait_time = min(2 ** retry_count * 5, 60)
                print(f"   ⚠️  Exception with rate limit (429), retry {retry_count}/{max_retries}")
                print(f"   ⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            else:
                return {"success": False, "error": str(e), "elapsed": 0}
    
    # Agotó todos los retries
    return {
        "success": False,
        "error": f"Failed after {max_retries} retries (Unknown or rate limit)",
        "elapsed": 0
    }

def create_niche_discovery_agent():
    """Create specialized niche discovery agent with multi-geographic focus"""
    
    genome = Genome(
        prompt="""You are an elite niche discovery AI. You analyze markets and find profitable opportunities.

TARGET MARKETS:
- USA: English, USD, high purchasing power
- España: Spanish, EUR, strong digital adoption  
- Chile: Spanish, CLP, tech-savvy LATAM

RESPONSE RULES:
1. Output ONLY valid JSON
2. No explanations before or after
3. Start with { and end with }
4. Fill ALL required fields
5. NEVER use "Unknown" as niche_name - analyze properly

REQUIRED JSON STRUCTURE:
{
  "niche_name": "Specific Niche Name Here",
  "description": "Clear 1-sentence description",
  "target_geography": "USA",
  "geo_specific_insights": {
    "USA": "Market insights for USA",
    "España": "Market insights for Spain",
    "Chile": "Market insights for Chile"
  },
  "target_audience": "Specific demographic: age, income, profession",
  "pain_points": ["pain point 1", "pain point 2", "pain point 3"],
  "monetization_methods": [
    {
      "method": "subscription",
      "potential_USA": "$5k-15k/month",
      "potential_España": "€3k-10k/month",
      "potential_Chile": "$2M-6M CLP/month",
      "difficulty": "medium"
    }
  ],
  "competition": {
    "level": "low",
    "main_players": ["Competitor 1", "Competitor 2"],
    "opportunities": "Market gaps and opportunities"
  },
  "content_strategy": {
    "platforms": ["Instagram", "TikTok", "YouTube"],
    "content_types": ["short videos", "tutorials", "testimonials"],
    "posting_frequency": "5 times per week",
    "language_strategy": "Spanish-only"
  },
  "keywords": {
    "USA": ["keyword1 en", "keyword2 en"],
    "España": ["palabra clave 1", "palabra clave 2"],
    "Chile": ["palabra clave 1 cl", "palabra clave 2 cl"]
  },
  "market_urgency": "Why this niche is hot right now",
  "entry_barriers": "low",
  "success_probability": 0.85,
  "confidence_score": 0.90,
  "launch_priority": "Start with [country] because [reason]"
}

OUTPUT ONLY THE JSON. NO OTHER TEXT.""",
        fitness=0.0,
        generation=1
    )
    
    agent = BaseAgent(
        genome=genome,
        groq_api_key=config.api.groq_api_key,
        agent_id="niche-discovery-main",
        use_gemini=True  # Use Gemini by default (better JSON support)
    )
    
    return agent

def calculate_economic_indicators(niche_data: dict, geography: str) -> dict:
    """Calculate economic indicators for a niche"""
    
    # Extract revenue potential
    revenue_str = niche_data.get("target_revenue", "$5k-15k/month")
    
    # Parse revenue range (handle different currencies)
    import re
    revenue_match = re.findall(r'[\d,]+', revenue_str.replace('M', '000').replace('k', '000'))
    
    if len(revenue_match) >= 2:
        revenue_low = int(revenue_match[0].replace(',', ''))
        revenue_high = int(revenue_match[1].replace(',', ''))
        avg_revenue = (revenue_low + revenue_high) / 2
    else:
        avg_revenue = 10000  # Default
    
    # Calculate indicators based on geography and competition
    competition_level = niche_data.get("competition", {}).get("level", "medium")
    
    # Gross Margin (typical for digital products/services)
    gross_margin = {
        "low": 0.75,
        "medium": 0.65,
        "high": 0.55
    }.get(competition_level, 0.65)
    
    # CAC (Customer Acquisition Cost) varies by geography and competition
    cac_multiplier = {
        "USA": 1.0,
        "ES": 0.6,
        "CL": 0.4,
        "Multi-geo": 0.8
    }.get(geography, 1.0)
    
    competition_cac = {
        "low": 50,
        "medium": 100,
        "high": 200
    }.get(competition_level, 100)
    
    cac = competition_cac * cac_multiplier
    
    # LTV (Lifetime Value) - assuming 12 month average retention
    monthly_value = avg_revenue / 20  # Assume 20 customers
    ltv = monthly_value * 12
    
    # ROI calculation
    gross_profit = avg_revenue * gross_margin
    marketing_cost = cac * 20  # For 20 customers
    net_profit = gross_profit - marketing_cost
    roi = (net_profit / marketing_cost * 100) if marketing_cost > 0 else 0
    
    # Payback period (months)
    payback_period = (cac / monthly_value) if monthly_value > 0 else 12
    
    return {
        "monthly_revenue": f"${avg_revenue:,.0f}",
        "cac": f"${cac:.0f}",
        "ltv": f"${ltv:.0f}",
        "ltv_cac_ratio": f"{(ltv / cac):.1f}x" if cac > 0 else "N/A",
        "payback_period": f"{payback_period:.1f} months",
        "roi": f"{roi:.0f}%",
        "gross_margin": f"{gross_margin * 100:.0f}%",
        "net_profit": f"${net_profit:,.0f}"
    }

def generate_implementation_strategy(niche_data: dict) -> str:
    """Generate executive summary and implementation strategy using D8 agents"""
    
    niche_name = niche_data.get("niche_name", "Unknown Niche")
    geography = niche_data.get("target_geography", "USA")
    confidence = niche_data.get("confidence_score", 0) * 100
    
    # Domain recommendation
    domains = {
        "USA": [".com", ".io", ".ai"],
        "ES": [".es", ".com", ".eu"],
        "CL": [".cl", ".com", ".lat"],
        "Multi-geo": [".com", ".global", ".world"]
    }
    
    recommended_tlds = domains.get(geography, [".com"])
    niche_slug = re.sub(r'[^a-z0-9]+', '', niche_name.lower().replace(' ', ''))
    domain_suggestions = [f"{niche_slug}{tld}" for tld in recommended_tlds]
    
    strategy = f"""
🎯 NICHO: {niche_name}
📊 CONFIANZA: {confidence:.0f}%
🌐 DOMINIO RECOMENDADO: {domain_suggestions[0]}

────────────────────────────────────────────────────────────────────────────────
📋 ESTRATEGIA DE IMPLEMENTACIÓN AUTOMATIZADA CON D8
────────────────────────────────────────────────────────────────────────────────

🤖 AGENTES DEL ECOSISTEMA D8 (11 agents):

1. 📝 Content Generator Agent
   - Genera contenido adaptado a la audiencia del nicho
   - Output: Blog posts, social media content, email copy
   - Frecuencia: Diaria (5-10 pieces/day)

2. 🎨 Design Agent
   - Crea gráficos, banners, infografías
   - Output: Visual content para todas las plataformas
   - Frecuencia: 3-5 designs/day

3. 📱 Social Media Agent
   - Publica en Instagram, TikTok, YouTube, Twitter/X
   - Output: Scheduled posts, engagement responses
   - Frecuencia: Continua (24/7 monitoring)

4. 🔍 SEO Agent
   - Optimiza contenido para búsqueda
   - Output: Keyword research, meta tags, backlinks
   - Frecuencia: Análisis semanal

5. ✉️ Email Marketing Agent
   - Construye lista y envía campaigns
   - Output: Welcome sequences, nurture emails, promos
   - Frecuencia: Diaria

6. 💰 Conversion Optimizer Agent
   - A/B testing de landing pages, CTAs, precios
   - Output: Optimized funnels, conversion reports
   - Frecuencia: Iteración continua

7. 🤝 Customer Service Agent
   - Responde preguntas, maneja objeciones
   - Output: Automated responses, ticket resolution
   - Frecuencia: 24/7

8. 📊 Analytics Agent
   - Monitorea métricas, identifica oportunidades
   - Output: Daily dashboards, weekly reports
   - Frecuencia: Real-time tracking

9. 💸 Paid Ads Agent
   - Gestiona campañas en Google, Facebook, TikTok
   - Output: Ad creation, budget optimization, ROI tracking
   - Frecuencia: Diaria

10. 🔗 Partnership Agent
    - Busca colaboraciones con influencers y brands
    - Output: Partnership proposals, collaboration deals
    - Frecuencia: Semanal

11. 🚀 Product Evolution Agent
    - Mejora el producto basado en feedback
    - Output: Feature requests, product iterations
    - Frecuencia: Sprint de 2 semanas

────────────────────────────────────────────────────────────────────────────────
⏱️ ROADMAP DE IMPLEMENTACIÓN
────────────────────────────────────────────────────────────────────────────────

📅 SEMANA 1: Setup y Foundation
   - Registro de dominio: {domain_suggestions[0]}
   - Hosting setup (Vercel/Netlify para frontend, Railway/Render para backend)
   - Content Agent genera primeros 20 posts
   - Design Agent crea brand assets
   - Social Media Agent configura perfiles

📅 SEMANA 2-4: Content y Audiencia
   - Publicación diaria de contenido (Content + Social Media Agents)
   - SEO Agent optimiza para keywords objetivo
   - Email Agent construye lista con lead magnets
   - Analytics Agent trackea métricas tempranas

📅 SEMANA 5-8: Monetización
   - Lanzamiento de producto/servicio principal
   - Paid Ads Agent inicia campañas con presupuesto pequeño ($10-20/día)
   - Conversion Optimizer prueba diferentes funnels
   - Customer Service Agent maneja primeras ventas

📅 MES 3+: Scale
   - Partnership Agent busca colaboraciones
   - Product Evolution Agent mejora basado en feedback
   - Paid Ads Agent escala presupuesto según ROI
   - Todo el ecosistema D8 opera autónomamente

────────────────────────────────────────────────────────────────────────────────
👤 INTERVENCIÓN HUMANA REQUERIDA
────────────────────────────────────────────────────────────────────────────────

⚠️ ÚNICO INPUT HUMANO:
   1. Registro de dominio ({domain_suggestions[0]}) - 15 min
   2. Configuración inicial de cuentas (Google, socials) - 1 hora
   3. Aprobación de estrategia inicial - 30 min
   4. Review semanal de métricas - 1 hora/semana

TOTAL: ~5-10 horas de trabajo humano para setup
DESPUÉS: 100% automatizado con D8

────────────────────────────────────────────────────────────────────────────────
💰 PROYECCIÓN FINANCIERA
────────────────────────────────────────────────────────────────────────────────

Mes 1: $0-500 (building audience)
Mes 2: $500-2,000 (first sales)
Mes 3: $2,000-5,000 (optimization)
Mes 4-6: $5,000-15,000 (scale)
Mes 7-12: $15,000-50,000+ (mature)

🎯 Objetivo: $10k/mes MRR en 6 meses con 92% automatización D8

────────────────────────────────────────────────────────────────────────────────
"""
    
    return strategy

# Resto del código sigue igual...
# (market_areas, main logic, etc - copiar del archivo original desde línea ~290 hasta el final)

if __name__ == "__main__":
    # Continúa aquí con el resto del script original
    pass
