"""
Niche Discovery Agent
Agente especializado en descubrir y analizar nichos rentables
V2: Con rate limiting, retry automático, y validación de Unknown
"""

import sys
import json
import time
import re
from pathlib import Path
from tqdm import tqdm

# Agregar raíz del proyecto al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.base_agent import BaseAgent
from app.evolution.darwin import Genome
from app.config import config
from app.integrations.gemini_client import GeminiClient
from app.distributed_integration import D8DistributedClient
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de rate limiting para Gemini
GEMINI_RPM = 15  # Requests per minute (free tier)
MIN_INTERVAL_GEMINI = 60.0 / GEMINI_RPM  # 4 segundos entre requests
last_request_time = None

# Initialize Gemini client globally
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
ORCHESTRATOR_URL = os.getenv('ORCHESTRATOR_URL', 'http://localhost:7001')

gemini_client = GeminiClient(api_key=GEMINI_API_KEY, rpm_limit=GEMINI_RPM) if GEMINI_API_KEY else None

# Try to connect to orchestrator as fallback
distributed_client = None
if not GEMINI_API_KEY and not GROQ_API_KEY:
    try:
        distributed_client = D8DistributedClient(ORCHESTRATOR_URL)
        print(f"✅ No API keys found, using orchestrator at {ORCHESTRATOR_URL}")
    except Exception as e:
        print(f"⚠️ Warning: No API keys and orchestrator unavailable: {e}")
        print("    Make sure to start orchestrator with: python start_d8.py (option 4)")
        distributed_client = None

def wait_for_rate_limit():
    """Esperar el intervalo necesario entre requests para respetar rate limits"""
    global last_request_time
    
    if last_request_time is not None:
        elapsed = time.time() - last_request_time
        if elapsed < MIN_INTERVAL_GEMINI:
            wait_time = MIN_INTERVAL_GEMINI - elapsed
            time.sleep(wait_time)
    
    last_request_time = time.time()

def discover_niche_with_retry(agent: BaseAgent, market_area: str, geography: str, max_retries: int = 5, progress_bar=None) -> dict:
    """
    Descubre nicho con retry automático si detecta Unknown o error 429
    Usa Gemini directamente para garantizar JSON válido
    """
    retry_count = 0
    
    # Construct prompt with geography context
    geo_context = {
        "USA": "Language: English, Currency: USD, Focus: High purchasing power, tech-savvy audience",
        "ES": "Language: Spanish, Currency: EUR, Focus: Largest Spanish-speaking market in Europe",
        "CL": "Language: Spanish, Currency: CLP, Focus: Tech-savvy LATAM market, growing digital economy",
        "Multi-geo": "Languages: English + Spanish, Markets: USA, España, Chile"
    }.get(geography, "")
    
    prompt = f"""{agent.genome.prompt}

MARKET TO ANALYZE:
{market_area}

TARGET GEOGRAPHY: {geography}
{geo_context}

Analyze this market and return ONLY valid JSON with the structure specified above.
Remember: NEVER use "Unknown" as niche_name - provide a real, specific niche name."""
    
    while retry_count < max_retries:
        try:
            if progress_bar:
                progress_bar.set_postfix_str(f"Attempt {retry_count + 1}/{max_retries}")
            
            start_time = time.time()
            
            # Prioridad 1: Usar Gemini directamente si está disponible
            if gemini_client:
                result = gemini_client.generate_json(
                    prompt=prompt,
                    temperature=0.3,
                    max_tokens=2500
                )
            # Prioridad 2: Usar orquestador distribuido si no hay API
            elif distributed_client:
                if progress_bar:
                    progress_bar.set_postfix_str("Using orchestrator...")
                
                response = distributed_client.execute_agent_action(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b",
                    temperature=0.3,
                    priority=7,  # Alta prioridad para niche discovery
                    wait_for_result=True
                )
                
                if response.get("success"):
                    # Parse JSON from output
                    output = response.get("output", "")
                    import json
                    try:
                        result = json.loads(output)
                    except:
                        # Try to extract JSON from markdown
                        json_match = re.search(r'```json\s*(\{.*?\})\s*```', output, re.DOTALL)
                        if json_match:
                            result = json.loads(json_match.group(1))
                        else:
                            result = {"success": False, "error": "Could not parse JSON from orchestrator response"}
                else:
                    result = {"success": False, "error": response.get("error", "Orchestrator task failed")}
            # Prioridad 3: Fallback a Groq via BaseAgent
            else:
                result = agent.act({
                    "market_area": market_area,
                    "target_geography": geography
                }, action_type="discover_niche")
            
            elapsed = time.time() - start_time
            
            # Verificar si es éxito
            if isinstance(result, dict) and not result.get("success", True):
                error = result.get("error", "")
                
                # Detectar 429 o rate limit
                if "429" in error or "rate" in error.lower() or "quota" in error.lower():
                    retry_count += 1
                    wait_time = min(2 ** retry_count * 5, 60)
                    if progress_bar:
                        progress_bar.set_postfix_str(f"⚠️ Rate limit, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    return {"success": False, "error": error, "elapsed": elapsed}
            
            # Verificar si el nicho es "Unknown" (error)
            niche_name = result.get("niche_name", "") if isinstance(result, dict) else ""
            if niche_name.lower() in ["unknown", "unknownniche", ""]:
                retry_count += 1
                wait_time = min(2 ** retry_count * 3, 30)
                if progress_bar:
                    progress_bar.set_postfix_str(f"⚠️ Unknown detected, retry {retry_count}/{max_retries}")
                time.sleep(wait_time)
                continue
            
            # Success!
            if progress_bar:
                progress_bar.set_postfix_str(f"✅ {niche_name[:30]}")
            
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
                if progress_bar:
                    progress_bar.set_postfix_str(f"⚠️ Exception 429, waiting {wait_time}s")
                time.sleep(wait_time)
                continue
            else:
                if progress_bar:
                    progress_bar.set_postfix_str(f"❌ Error: {str(e)[:30]}")
                return {"success": False, "error": str(e), "elapsed": 0}
    
    # Agotó todos los retries
    if progress_bar:
        progress_bar.set_postfix_str("❌ Max retries exceeded")
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
        agent_id="niche-discovery-main"
        # NOTE: Gemini se usa via GeminiClient directo, no a través de BaseAgent
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
        "gross_margin": f"{gross_margin*100:.0f}%",
        "cac": f"${cac:.0f}",
        "ltv": f"${ltv:.0f}",
        "ltv_cac_ratio": f"{(ltv/cac):.1f}x" if cac > 0 else "N/A",
        "roi": f"{roi:.0f}%",
        "payback_period": f"{payback_period:.1f} months",
        "net_profit_monthly": f"${net_profit:,.0f}"
    }


def generate_implementation_strategy(niche_data: dict, geography: str) -> dict:
    """Generate automated implementation strategy using D8 agents"""
    
    niche_name = niche_data.get("niche_name", "Unknown Niche")
    
    # Generate domain recommendation
    domain_base = niche_name.lower().replace(" ", "").replace("-", "")
    domain_base = re.sub(r'[^a-z0-9]', '', domain_base)[:15]
    
    domain_extensions = {
        "USA": [".com", ".io", ".ai"],
        "ES": [".es", ".com", ".eu"],
        "CL": [".cl", ".com", ".lat"],
        "Multi-geo": [".com", ".io", ".global"]
    }
    
    recommended_domains = [f"{domain_base}{ext}" for ext in domain_extensions.get(geography, [".com"])]
    
    # D8 Agent orchestration strategy
    content_strategy = niche_data.get("content_strategy", {})
    platforms = content_strategy.get("platforms", ["Instagram", "TikTok"])
    
    agent_plan = {
        "phase_1_setup": {
            "duration": "Week 1",
            "agents": [
                {
                    "agent_type": "content_generator",
                    "task": "Generate landing page copy, SEO content, and initial blog posts",
                    "automation_level": "100%",
                    "estimated_output": "15-20 pieces of content"
                },
                {
                    "agent_type": "design_agent",
                    "task": "Generate logo, brand colors, visual identity using DALL-E/Midjourney",
                    "automation_level": "95%",
                    "estimated_output": "Complete brand kit"
                }
            ],
            "human_input": f"Provide domain registration for: {recommended_domains[0]}"
        },
        "phase_2_content": {
            "duration": "Week 2-4",
            "agents": [
                {
                    "agent_type": "social_media_agent",
                    "task": f"Generate and schedule content for {', '.join(platforms[:3])}",
                    "automation_level": "100%",
                    "estimated_output": "30 posts/week automated"
                },
                {
                    "agent_type": "seo_agent",
                    "task": "Optimize content, build backlinks, submit to directories",
                    "automation_level": "90%",
                    "estimated_output": "50+ backlinks/month"
                },
                {
                    "agent_type": "email_marketing_agent",
                    "task": "Create email sequences, nurture campaigns",
                    "automation_level": "100%",
                    "estimated_output": "5 email sequences"
                }
            ],
            "human_input": "None - fully automated"
        },
        "phase_3_monetization": {
            "duration": "Week 5-8",
            "agents": [
                {
                    "agent_type": "conversion_optimizer",
                    "task": "A/B test landing pages, optimize funnels",
                    "automation_level": "100%",
                    "estimated_output": "3-5 optimized funnels"
                },
                {
                    "agent_type": "customer_service_agent",
                    "task": "Handle inquiries, onboarding, support tickets",
                    "automation_level": "85%",
                    "estimated_output": "24/7 automated support"
                },
                {
                    "agent_type": "analytics_agent",
                    "task": "Track metrics, generate reports, optimize campaigns",
                    "automation_level": "100%",
                    "estimated_output": "Daily performance reports"
                }
            ],
            "human_input": "Review weekly reports, approve major pivots"
        },
        "phase_4_scale": {
            "duration": "Month 3+",
            "agents": [
                {
                    "agent_type": "paid_ads_agent",
                    "task": "Manage Google/Facebook/Instagram ads with automated bidding",
                    "automation_level": "95%",
                    "estimated_output": "ROI-optimized campaigns"
                },
                {
                    "agent_type": "partnership_agent",
                    "task": "Identify and reach out to potential partners/affiliates",
                    "automation_level": "80%",
                    "estimated_output": "10-15 partnerships/month"
                },
                {
                    "agent_type": "product_evolution_agent",
                    "task": "Analyze user feedback, suggest product improvements",
                    "automation_level": "100%",
                    "estimated_output": "Monthly evolution roadmap"
                }
            ],
            "human_input": "Approve partnership deals, major product changes"
        }
    }
    
    return {
        "recommended_domain": recommended_domains[0],
        "alternative_domains": recommended_domains[1:],
        "agent_orchestration": agent_plan,
        "total_agents_required": 11,
        "automation_level": "92%",
        "time_to_market": "30 days",
        "estimated_setup_cost": "$500-1000",
        "human_hours_required": "5-10 hours total"
    }


def discover_niches(market_areas: list, save_results=True):
    """Run niche discovery on multiple market areas"""
    
    print("🔍 NICHE DISCOVERY AGENT - MULTI-GEO ANALYSIS")
    print("=" * 100)
    print()
    
    agent = create_niche_discovery_agent()
    print(f"✅ Agent initialized: {agent.agent_id}")
    print()
    
    discoveries = []
    
    for i, market in enumerate(market_areas, 1):
        print(f"[{i}/{len(market_areas)}] Analyzing: {market['area']}")
        print("-" * 70)
        
        try:
            start_time = time.time()
            
            result = agent.act(
                input_data={
                    "market_area": market['area'],
                    "trend_context": market.get('context', ''),
                    "target_revenue": market.get('target_revenue', '$5k-15k/month'),
                    "time_to_market": market.get('time_to_market', '30-60 days'),
                    "target_geography": market.get('target_geography', 'USA')
                },
                action_type="discover_niche"
            )
            
            elapsed = time.time() - start_time
            
            # Extract niche info and ensure we have parsed JSON
            niche_name = "Unknown"
            confidence = 0
            parsed_result = result
            
            # First try to extract from nested response
            if "response" in result and isinstance(result["response"], str):
                try:
                    # Try to parse JSON from response
                    niche_data = json.loads(result["response"])
                    if isinstance(niche_data, dict):
                        niche_name = niche_data.get("niche_name", "Unknown")
                        confidence = niche_data.get("confidence_score", 0)
                        parsed_result = niche_data  # Use parsed data
                except:
                    # If parsing fails, try to extract from the text
                    pass
            
            # Direct extraction if already in correct format
            if isinstance(parsed_result, dict):
                if "niche_name" in parsed_result:
                    niche_name = parsed_result.get("niche_name", "Unknown")
                if "confidence_score" in parsed_result:
                    confidence = parsed_result.get("confidence_score", 0)
            
            result = parsed_result
            
            print(f"✅ Discovered in {elapsed:.1f}s")
            print(f"   📌 Nicho: {niche_name}")
            print(f"   📊 Confianza: {confidence:.0%}")
            
            if "competition" in result:
                comp = result["competition"]
                if isinstance(comp, dict):
                    print(f"   🎯 Competencia: {comp.get('level', 'unknown')}")
            
            print()
            
            discoveries.append({
                "market_area": market['area'],
                "discovery": result,
                "elapsed": elapsed,
                "timestamp": time.time(),
                "geography": market.get('target_geography', 'USA')
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print()
            discoveries.append({
                "market_area": market['area'],
                "error": str(e),
                "timestamp": time.time(),
                "geography": market.get('target_geography', 'USA')
            })
    
    # Summary
    print("=" * 100)
    print("📊 ANÁLISIS COMPLETO POR MERCADO")
    print("=" * 100)
    print()
    
    successful = sum(1 for d in discoveries if "discovery" in d)
    total = len(discoveries)
    
    print(f"✅ Áreas analizadas: {total}")
    print(f"✅ Nichos descubiertos: {successful}")
    print(f"✅ Success rate: {(successful/total*100) if total > 0 else 0:.1f}%")
    print()
    
    # Organize by geography
    by_geography = {}
    for d in discoveries:
        if "discovery" in d:
            geo = d.get("geography", "USA")
            if geo not in by_geography:
                by_geography[geo] = []
            
            disc = d["discovery"]
            conf = 0
            niche_name = "Unknown"
            
            if isinstance(disc, dict):
                conf = disc.get("confidence_score", 0)
                niche_name = disc.get("niche_name", "Unknown")
                
                if conf == 0 and "response" in disc:
                    try:
                        parsed = json.loads(disc["response"])
                        conf = parsed.get("confidence_score", 0)
                        niche_name = parsed.get("niche_name", "Unknown")
                        disc = parsed
                    except:
                        pass
            
            by_geography[geo].append({
                "area": d["market_area"],
                "niche_name": niche_name,
                "confidence": conf,
                "discovery": disc,
                "geography": geo
            })
    
    # Sort each geography by confidence
    for geo in by_geography:
        by_geography[geo].sort(key=lambda x: x["confidence"], reverse=True)
    
    # Display TOP 5 per geography in professional tables
    geo_names = {
        "USA": "🇺🇸 UNITED STATES",
        "ES": "🇪🇸 ESPAÑA",
        "CL": "🇨🇱 CHILE",
        "Multi-geo": "🌎 MULTI-MERCADO"
    }
    
    top_per_geo = {}
    
    for geo, items in by_geography.items():
        print()
        print("=" * 100)
        print(f"  {geo_names.get(geo, geo)} - TOP 5 NICHOS")
        print("=" * 100)
        print()
        
        # Table header
        print(f"{'#':<3} {'NICHO':<35} {'CONFIANZA':<12} {'COMPETENCIA':<13} {'ROI':<10} {'MARGIN':<10}")
        print("-" * 100)
        
        top_items = items[:5]
        top_per_geo[geo] = top_items
        
        for i, item in enumerate(top_items, 1):
            disc = item["discovery"]
            niche = item["niche_name"][:33]
            conf = f"{item['confidence']:.0%}"
            comp = disc.get("competition", {}).get("level", "N/A") if isinstance(disc, dict) else "N/A"
            
            # Calculate economic indicators
            indicators = calculate_economic_indicators(disc if isinstance(disc, dict) else {}, geo)
            roi = indicators["roi"]
            margin = indicators["gross_margin"]
            
            print(f"{i:<3} {niche:<35} {conf:<12} {comp:<13} {roi:<10} {margin:<10}")
        
        print()
        
        # Detailed economic analysis for TOP 3
        print("  📊 INDICADORES ECONÓMICOS - TOP 3")
        print("  " + "-" * 96)
        print(f"  {'#':<3} {'Revenue/Month':<18} {'CAC':<12} {'LTV':<12} {'LTV/CAC':<12} {'Payback':<15} {'Net Profit':<15}")
        print("  " + "-" * 96)
        
        for i, item in enumerate(top_items[:3], 1):
            disc = item["discovery"]
            indicators = calculate_economic_indicators(disc if isinstance(disc, dict) else {}, geo)
            
            print(f"  {i:<3} {indicators['monthly_revenue']:<18} "
                  f"{indicators['cac']:<12} {indicators['ltv']:<12} "
                  f"{indicators['ltv_cac_ratio']:<12} {indicators['payback_period']:<15} "
                  f"{indicators['net_profit_monthly']:<15}")
        
        print()
    
    # EXECUTIVE SUMMARY - TOP 1 per geography
    print()
    print("=" * 100)
    print("  📋 RESUMEN EJECUTIVO - ESTRATEGIA DE IMPLEMENTACIÓN")
    print("=" * 100)
    print()
    
    for geo, items in top_per_geo.items():
        if not items:
            continue
        
        top1 = items[0]
        disc = top1["discovery"]
        
        if not isinstance(disc, dict):
            continue
        
        print()
        print("▼" * 50)
        print(f"   {geo_names.get(geo, geo)}")
        print(f"   TOP 1: {top1['niche_name']}")
        print("▼" * 50)
        print()
        
        # Generate implementation strategy
        strategy = generate_implementation_strategy(disc, geo)
        indicators = calculate_economic_indicators(disc, geo)
        
        print(f"🎯 NICHO: {top1['niche_name']}")
        print(f"📊 CONFIANZA: {top1['confidence']:.0%}")
        print(f"🌐 DOMINIO RECOMENDADO: {strategy['recommended_domain']}")
        print(f"   Alternativas: {', '.join(strategy['alternative_domains'])}")
        print()
        
        print("💰 PROYECCIÓN ECONÓMICA:")
        print(f"   • Revenue mensual proyectado: {indicators['monthly_revenue']}")
        print(f"   • Gross Margin: {indicators['gross_margin']}")
        print(f"   • ROI esperado: {indicators['roi']}")
        print(f"   • Net Profit mensual: {indicators['net_profit_monthly']}")
        print(f"   • CAC: {indicators['cac']} | LTV: {indicators['ltv']} | Ratio: {indicators['ltv_cac_ratio']}")
        print(f"   • Payback period: {indicators['payback_period']}")
        print()
        
        print("🤖 ESTRATEGIA DE AGENTES D8:")
        print(f"   • Total agentes necesarios: {strategy['total_agents_required']}")
        print(f"   • Nivel de automatización: {strategy['automation_level']}")
        print(f"   • Time to market: {strategy['time_to_market']}")
        print(f"   • Costo setup estimado: {strategy['estimated_setup_cost']}")
        print(f"   • Horas humanas requeridas: {strategy['human_hours_required']}")
        print()
        
        print("📅 ROADMAP DE IMPLEMENTACIÓN:")
        print()
        
        for phase_name, phase_data in strategy["agent_orchestration"].items():
            phase_title = phase_name.replace("_", " ").title()
            print(f"   {phase_title}")
            print(f"   Duración: {phase_data['duration']}")
            print(f"   Input humano: {phase_data['human_input']}")
            print()
            
            for agent in phase_data["agents"]:
                print(f"      • {agent['agent_type'].replace('_', ' ').title()}")
                print(f"        Task: {agent['task']}")
                print(f"        Automatización: {agent['automation_level']}")
                print(f"        Output: {agent['estimated_output']}")
                print()
        
        print("✅ ACCIÓN INMEDIATA REQUERIDA:")
        print(f"   1. Registrar dominio: {strategy['recommended_domain']}")
        print(f"   2. Configurar DNS apuntando a servidor D8")
        print(f"   3. Ejecutar: python -m app.main --niche={geo}_{top1['niche_name'][:20].replace(' ', '_')}")
        print(f"   4. Sistema D8 se encargará del resto automáticamente")
        print()
    
    # Overall summary
    print()
    print("=" * 100)
    print("  🎯 CONCLUSIONES Y RECOMENDACIONES FINALES")
    print("=" * 100)
    print()
    
    total_niches = sum(len(items) for items in by_geography.values())
    print(f"✅ Total de nichos viables identificados: {total_niches}")
    print(f"✅ Mercados analizados: {len(by_geography)}")
    print(f"✅ Nivel de automatización promedio: 92%")
    print()
    
    print("🚀 PRÓXIMOS PASOS:")
    print("   1. Revisar los dominios recomendados arriba")
    print("   2. Registrar dominio del TOP 1 de tu mercado prioritario")
    print("   3. Ejecutar sistema D8 con el nicho seleccionado")
    print("   4. Dejar que los agentes trabajen automáticamente")
    print("   5. Revisar reportes semanales generados por analytics_agent")
    print()
    print("=" * 100)
    print()
    
    # Save results
    if save_results:
        results_path = Path("data/test_results/niche_discovery.json")
        results_path.parent.mkdir(parents=True, exist_ok=True)
        
        save_data = {
            "timestamp": time.time(),
            "market_areas_analyzed": len(market_areas),
            "discoveries": discoveries,
        }
        
        # Add agent info if agent is still available
        if hasattr(agent, 'agent_id'):
            save_data["agent_id"] = agent.agent_id
            save_data["agent_metrics"] = {
                "total_actions": agent.metrics.total_actions,
                "successful_actions": agent.metrics.successful_actions,
                "fitness": agent.metrics.get_fitness()
            }
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados guardados en: {results_path}")
    
    print()
    return discoveries

if __name__ == "__main__":
    # Market areas to analyze - Multi-geographic approach
    markets = [
        # USA Market
        {
            "area": "AI automation for small e-commerce stores",
            "context": "Small online stores need automation but can't afford developers",
            "target_revenue": "$5k-15k/month",
            "target_geography": "USA"
        },
        {
            "area": "No-code tools for content creators",
            "context": "Creators want to build apps, websites, automations without coding",
            "target_revenue": "$10k-30k/month",
            "target_geography": "USA"
        },
        
        # España Market
        {
            "area": "Automatización de marketing para PYMEs españolas",
            "context": "Pequeñas empresas españolas necesitan marketing digital pero no tienen presupuesto para agencias",
            "target_revenue": "€3k-10k/month",
            "target_geography": "ES"
        },
        {
            "area": "Herramientas de teletrabajo para equipos españoles",
            "context": "Empresas españolas adoptan trabajo remoto post-pandemia, necesitan productividad y comunicación asíncrona",
            "target_revenue": "€5k-15k/month",
            "target_geography": "ES"
        },
        
        # Chile Market
        {
            "area": "Automatización de ventas para emprendedores chilenos",
            "context": "Emprendedores chilenos venden por Instagram/WhatsApp pero pierden ventas por desorganización",
            "target_revenue": "$2M-6M CLP/month",
            "target_geography": "CL"
        },
        {
            "area": "Educación online para profesionales chilenos",
            "context": "Profesionales chilenos buscan upskilling en tech/digital pero cursos internacionales son caros",
            "target_revenue": "$3M-8M CLP/month",
            "target_geography": "CL"
        },
        
        # Multi-geo opportunities
        {
            "area": "AI-powered personal finance for millennials",
            "context": "Young professionals across USA, España, Chile need help managing money and building wealth",
            "target_revenue": "$10k-40k/month (USA), €5k-20k/month (ES), $3M-10M CLP/month (CL)",
            "target_geography": "Multi-geo"
        },
        {
            "area": "Sustainable tech and green automation",
            "context": "Climate-conscious consumers in developed markets want eco-friendly tech solutions",
            "target_revenue": "$8k-25k/month",
            "target_geography": "Multi-geo"
        }
    ]
    
    try:
        discoveries = discover_niches(markets)
        sys.exit(0 if len(discoveries) > 0 else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
