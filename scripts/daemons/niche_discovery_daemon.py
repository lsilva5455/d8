#!/usr/bin/env python3
"""
🔬 Niche Discovery Daemon - FASE 3
Descubrimiento continuo de nichos rentables 24/7
"""

import schedule
import time
import logging
from datetime import datetime
from pathlib import Path
import json
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.agents.base_agent import BaseAgent
from lib.llm import GroqClient
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/niche_discovery_daemon.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()


class NicheDiscoveryAgent:
    """Agente especializado en descubrir nichos rentables"""
    
    def __init__(self):
        self.llm = GroqClient(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.3-70b-versatile"
        )
        self.results_dir = Path("data/niche_discovery")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
    def discover_opportunities(self, markets=None):
        """Descubrir oportunidades en mercados específicos"""
        if markets is None:
            markets = ["usa", "spain", "chile"]
        
        logger.info(f"🔍 Starting niche discovery for markets: {markets}")
        
        opportunities = []
        
        for market in markets:
            prompt = f"""Analiza el mercado de {market} y encuentra 3 nichos de contenido digital rentables.

Para cada nicho proporciona:
1. Nombre del nicho
2. Demanda estimada (alta/media/baja)
3. Competencia (alta/media/baja)
4. ROI estimado (porcentaje)
5. Tipo de contenido ideal (blog, video, infográfico, etc.)
6. Keywords principales (3-5)

Responde en formato JSON:
{{
  "nichos": [
    {{
      "nombre": "...",
      "demanda": "alta",
      "competencia": "baja",
      "roi_estimado": 35,
      "tipo_contenido": "blog",
      "keywords": ["keyword1", "keyword2", "keyword3"]
    }}
  ]
}}"""

            try:
                response = self.llm.generate(prompt, temperature=0.7)
                
                # Parse JSON response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    nichos = data.get("nichos", [])
                    
                    for nicho in nichos:
                        nicho["market"] = market
                        nicho["discovered_at"] = datetime.now().isoformat()
                        opportunities.append(nicho)
                    
                    logger.info(f"✅ Found {len(nichos)} opportunities in {market}")
                else:
                    logger.warning(f"⚠️ No valid JSON in response for {market}")
                    
            except Exception as e:
                logger.error(f"❌ Error discovering nichos in {market}: {e}")
                
        return opportunities
    
    def prioritize(self, opportunities, top_n=5):
        """Priorizar oportunidades por ROI"""
        logger.info(f"📊 Prioritizing {len(opportunities)} opportunities")
        
        # Ordenar por ROI estimado
        sorted_opps = sorted(
            opportunities,
            key=lambda x: x.get("roi_estimado", 0),
            reverse=True
        )
        
        top_niches = sorted_opps[:top_n]
        
        logger.info(f"🎯 Top {len(top_niches)} niches selected")
        for i, niche in enumerate(top_niches, 1):
            logger.info(f"  {i}. {niche['nombre']} - ROI: {niche['roi_estimado']}% ({niche['market']})")
        
        return top_niches
    
    def save_results(self, niches):
        """Guardar resultados del descubrimiento"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.results_dir / f"discovery_{timestamp}.json"
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "niches_found": len(niches),
            "niches": niches
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Results saved to {filename}")
        return filename


def run_discovery():
    """Ejecutar ciclo de descubrimiento"""
    logger.info("="*60)
    logger.info("🚀 Starting Niche Discovery Cycle")
    logger.info("="*60)
    
    try:
        agent = NicheDiscoveryAgent()
        
        # 1. Descubrir oportunidades
        opportunities = agent.discover_opportunities(
            markets=["usa", "spain", "chile"]
        )
        
        if not opportunities:
            logger.warning("⚠️ No opportunities found in this cycle")
            return
        
        # 2. Priorizar por ROI
        top_niches = agent.prioritize(opportunities, top_n=5)
        
        # 3. Guardar resultados
        agent.save_results(top_niches)
        
        # 4. TODO: Asignar agentes especializados
        # assign_agents_to_niches(top_niches)
        
        logger.info("✅ Niche Discovery Cycle completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error in discovery cycle: {e}", exc_info=True)


def main():
    """Main daemon loop"""
    logger.info("🏁 Niche Discovery Daemon starting...")
    logger.info(f"📅 Schedule: Every 24 hours")
    
    # Ejecutar inmediatamente al inicio
    run_discovery()
    
    # Programar ejecución cada 24 horas
    schedule.every(24).hours.do(run_discovery)
    
    logger.info("⏰ Daemon is running. Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("🛑 Daemon stopped by user")


if __name__ == "__main__":
    main()
