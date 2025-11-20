"""
The Hive - Main Entry Point
Evolutionary AI Agent Ecosystem
Integrated with D8 Economy System (FASE 2)
"""

from flask import Flask, jsonify, request
from app.config import config
from app.agents.base_agent import BaseAgent
from app.evolution.darwin import Genome, DeepSeekEvolutionEngine, EvolutionOrchestrator
from app.knowledge.code_vault import CodeVault
from app.agents.coder_agent import CoderAgent
from app.evolution.self_healing import SelfHealingOrchestrator
from app.utils.code_ingestor import CodeIngestor
from app.distributed.orchestrator import orchestrator_bp, orchestrator
from typing import List
import logging
import os

# FASE 2: Import economy systems
try:
    from app.economy.d8_credits import D8CreditsSystem
    from app.economy.accounting import AutonomousAccountingSystem
    from app.economy.revenue_attribution import RevenueAttributionSystem
    ECONOMY_AVAILABLE = True
except ImportError:
    ECONOMY_AVAILABLE = False
    logging.warning("Economy system not available - running without economic integration")

# Setup logging
os.makedirs("data/logs", exist_ok=True)
logging.basicConfig(
    level=getattr(logging, config.logging.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.logging.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Register distributed orchestrator blueprint
app.register_blueprint(orchestrator_bp)

# Global state (in production, use proper state management)
population: List[BaseAgent] = []
evolution_engine: DeepSeekEvolutionEngine = None
orchestrator_evo: EvolutionOrchestrator = None

# FASE 2: Economy system instances
credits_system: D8CreditsSystem = None
accounting_system: AutonomousAccountingSystem = None
revenue_attribution: RevenueAttributionSystem = None

# D8-GENESIS components
code_vault: CodeVault = None
coder_agent: CoderAgent = None
healer: SelfHealingOrchestrator = None


def initialize_economy_systems():
    """Initialize D8 economy systems (FASE 2)"""
    global credits_system, accounting_system, revenue_attribution
    
    if not ECONOMY_AVAILABLE:
        logger.warning("Economy systems not available - skipping initialization")
        return False
    
    try:
        # Initialize D8 Credits
        credits_system = D8CreditsSystem()
        logger.info("✅ D8 Credits System initialized")
        
        # Initialize Autonomous Accounting
        accounting_system = AutonomousAccountingSystem()
        
        # Set initial budgets
        accounting_system.set_monthly_budget("api_calls", 500.0)
        accounting_system.set_monthly_budget("infrastructure", 200.0)
        accounting_system.set_monthly_budget("research", 100.0)
        logger.info("✅ Autonomous Accounting initialized with budgets")
        
        # Initialize Revenue Attribution
        revenue_attribution = RevenueAttributionSystem()
        logger.info("✅ Revenue Attribution System initialized")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize economy systems: {e}")
        return False


# Global state (in production, use proper state management)
population: List[BaseAgent] = []
evolution_engine: DeepSeekEvolutionEngine = None
orchestrator_evo: EvolutionOrchestrator = None

# D8-GENESIS components
code_vault: CodeVault = None
coder_agent: CoderAgent = None
healer: SelfHealingOrchestrator = None


@app.route('/')
def index():
    """API health check"""
    return jsonify({
        "status": "online",
        "project": "The Hive",
        "version": "0.2.0 - FASE 2",
        "population_size": len(population),
        "economy": {
            "credits_system_ready": credits_system is not None,
            "accounting_ready": accounting_system is not None,
            "revenue_attribution_ready": revenue_attribution is not None,
            "total_revenue": credits_system.get_total_revenue() if credits_system else 0,
            "active_wallets": len(credits_system.wallets) if credits_system else 0
        },
        "d8_genesis": {
            "code_vault_ready": code_vault is not None,
            "coder_agent_ready": coder_agent is not None,
            "healer_ready": healer is not None
        },
        "congress_system": {
            "supreme_council_ready": supreme_council is not None,
            "niche_discovery_ready": niche_discovery_committee is not None,
            "discovery_engine_ready": discovery_engine is not None,
            "roi_tracker_ready": roi_tracker is not None
        },
        "endpoints": {
            "/": "This health check",
            "/api/agents": "List all agents",
            "/api/agents/<id>": "Get agent details",
            "/api/evolve": "Trigger evolution cycle",
            "/api/economy/status": "Economy system status",
            "/api/economy/report": "Generate accounting report",
            "/api/genesis/ingest": "Ingest legacy code",
            "/api/genesis/generate": "Generate polymorphic code",
            "/api/genesis/heal": "Self-heal broken code",
            "/api/genesis/stats": "D8-GENESIS statistics",
            "/api/congress/status": "Congress system status",
            "/api/congress/council/*": "Supreme Council endpoints",
            "/api/congress/discovery/*": "Niche Discovery endpoints",
            "/api/congress/roi/*": "ROI Tracking endpoints"
        }
    })


@app.route('/api/agents', methods=['GET'])
def list_agents():
    """List all agents with their status"""
    agents_status = [agent.get_status() for agent in population]
    agents_status.sort(key=lambda a: a['fitness'], reverse=True)
    
    return jsonify({
        "total": len(population),
        "agents": agents_status
    })


@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id: str):
    """Get detailed information about specific agent"""
    agent = next((a for a in population if a.agent_id == agent_id), None)
    
    if not agent:
        return jsonify({"error": "Agent not found"}), 404
    
    return jsonify(agent.get_status())


@app.route('/api/evolve', methods=['POST'])
def evolve_population():
    """
    Trigger one evolution cycle
    Returns new population status
    """
    global population, orchestrator_evo
    
    if not population:
        return jsonify({"error": "No population to evolve"}), 400
    
    logger.info("🧬 Starting evolution cycle...")
    
    try:
        # Convert agents to genomes
        genomes = [agent.genome for agent in population]
        
        # Update fitness scores
        for i, agent in enumerate(population):
            genomes[i].fitness = agent.get_fitness()
        
        # Evolve
        new_genomes = orchestrator_evo.evolve_generation(genomes)
        
        # Create new agent population
        population.clear()
        for genome in new_genomes:
            agent = BaseAgent(
                genome=genome,
                groq_api_key=config.api.groq_api_key,
                model=config.agent.groq_model
            )
            population.append(agent)
        
        logger.info(f"✅ Evolution complete: Generation {orchestrator_evo.generation}")
        
        return jsonify({
            "success": True,
            "generation": orchestrator_evo.generation,
            "population_size": len(population),
            "best_fitness": max(g.fitness for g in new_genomes),
            "avg_fitness": sum(g.fitness for g in new_genomes) / len(new_genomes)
        })
        
    except Exception as e:
        logger.error(f"Evolution failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/<agent_id>/act', methods=['POST'])
def agent_act(agent_id: str):
    """Trigger an agent to perform an action"""
    agent = next((a for a in population if a.agent_id == agent_id), None)
    
    if not agent:
        return jsonify({"error": "Agent not found"}), 404
    
    data = request.json
    action_type = data.get("action_type", "generic")
    input_data = data.get("input_data", {})
    
    result = agent.act(input_data, action_type)
    
    return jsonify({
        "agent_id": agent_id,
        "action_type": action_type,
        "result": result,
        "fitness": agent.get_fitness()
    })


# ==================== D8-GENESIS ENDPOINTS ====================

@app.route('/api/genesis/ingest', methods=['POST'])
def ingest_legacy_code():
    """
    Ingest legacy code from specified path
    
    Request body:
    {
        "path": "/path/to/legacy_code",  # Optional, defaults to ./legacy_code
        "recursive": true                # Optional, defaults to true
    }
    """
    global code_vault
    
    if not code_vault:
        return jsonify({"error": "Code Vault not initialized"}), 500
    
    data = request.json or {}
    path = data.get('path', './legacy_code')
    recursive = data.get('recursive', True)
    
    logger.info(f"📥 Ingesting legacy code from: {path}")
    
    try:
        ingestor = CodeIngestor(path)
        fragments = ingestor.scan_and_parse(recursive=recursive)
        code_vault.ingest_fragments(fragments)
        
        stats = code_vault.get_stats()
        
        logger.info(f"✅ Ingested {len(fragments)} code fragments")
        
        return jsonify({
            "success": True,
            "fragments_ingested": len(fragments),
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/genesis/generate', methods=['POST'])
def generate_code():
    """
    Generate polymorphic code for a task
    
    Request body:
    {
        "task": "Create function to like posts on Instagram",
        "platform": "instagram",  # Optional
        "action": "like"          # Optional
    }
    """
    global coder_agent
    
    if not coder_agent:
        return jsonify({"error": "Coder Agent not initialized"}), 500
    
    data = request.json
    
    if not data or 'task' not in data:
        return jsonify({"error": "Missing 'task' in request body"}), 400
    
    task = data['task']
    platform = data.get('platform')
    action = data.get('action')
    
    logger.info(f"🔧 Generating code for: {task}")
    
    try:
        result = coder_agent.generate_code(
            task_description=task,
            platform=platform,
            action=action
        )
        
        logger.info(f"✅ Code generated with {len(result.get('polymorphism_applied', []))} polymorphic techniques")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/genesis/heal', methods=['POST'])
def heal_code():
    """
    Self-heal broken code
    
    Request body:
    {
        "code": "def my_func(): ...",
        "error": "NameError: name 'x' is not defined",
        "context": "Additional context about the error"  # Optional
    }
    """
    global coder_agent
    
    if not coder_agent:
        return jsonify({"error": "Coder Agent not initialized"}), 500
    
    data = request.json
    
    if not data or 'code' not in data or 'error' not in data:
        return jsonify({"error": "Missing 'code' or 'error' in request body"}), 400
    
    broken_code = data['code']
    error_message = data['error']
    context = data.get('context', '')
    
    logger.info(f"🩹 Healing code with error: {error_message[:50]}...")
    
    try:
        result = coder_agent.self_heal(
            broken_code=broken_code,
            error_message=error_message,
            additional_context=context
        )
        
        logger.info(f"✅ Code healed successfully")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Code healing failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/genesis/stats', methods=['GET'])
def genesis_stats():
    """Get D8-GENESIS statistics"""
    global code_vault, coder_agent, healer
    
    stats = {
        "code_vault": None,
        "coder_agent": None,
        "self_healing": None
    }
    
    if code_vault:
        stats["code_vault"] = code_vault.get_stats()
    
    if coder_agent:
        stats["coder_agent"] = coder_agent.get_status()
    
    if healer:
        stats["self_healing"] = healer.get_stats()
    
    return jsonify(stats)


# ==================== END D8-GENESIS ENDPOINTS ====================


# ==================== CONGRESS SYSTEM ENDPOINTS ====================

# Global Congress components
supreme_council = None
niche_discovery_committee = None
roi_tracker = None
discovery_engine = None


@app.route('/api/congress/status', methods=['GET'])
def congress_status():
    """Get overall Congress system status"""
    global supreme_council, niche_discovery_committee, roi_tracker, discovery_engine
    
    return jsonify({
        "status": "active",
        "components": {
            "supreme_council": supreme_council is not None,
            "niche_discovery": niche_discovery_committee is not None,
            "roi_tracker": roi_tracker is not None,
            "discovery_engine": discovery_engine is not None
        },
        "endpoints": {
            "council": "/api/congress/council/*",
            "discovery": "/api/congress/discovery/*",
            "roi": "/api/congress/roi/*"
        }
    })


@app.route('/api/congress/council/members', methods=['GET'])
def get_council_members():
    """Get Supreme Council members"""
    global supreme_council
    
    if not supreme_council:
        return jsonify({"error": "Supreme Council not initialized"}), 500
    
    return jsonify({
        "members": list(supreme_council.council_members.values()),
        "total": len(supreme_council.council_members),
        "capacity": supreme_council.council_size
    })


@app.route('/api/congress/council/decisions', methods=['GET'])
def get_council_decisions():
    """Get recent council decisions"""
    global supreme_council
    
    if not supreme_council:
        return jsonify({"error": "Supreme Council not initialized"}), 500
    
    limit = request.args.get('limit', 10, type=int)
    decisions = supreme_council.get_recent_decisions(limit)
    
    return jsonify({
        "decisions": [
            {
                "decision_id": d.decision_id,
                "title": d.title,
                "type": d.decision_type.value,
                "passed": d.passed,
                "votes_for": d.votes_for,
                "votes_against": d.votes_against,
                "decided_at": d.decided_at
            }
            for d in decisions
        ],
        "total": len(decisions)
    })


@app.route('/api/congress/council/okrs', methods=['GET'])
def get_council_okrs():
    """Get active OKRs"""
    global supreme_council
    
    if not supreme_council:
        return jsonify({"error": "Supreme Council not initialized"}), 500
    
    active_okrs = [okr for okr in supreme_council.okrs if okr.status == "active"]
    
    return jsonify({
        "okrs": [
            {
                "okr_id": okr.okr_id,
                "quarter": okr.quarter,
                "objective": okr.objective,
                "key_results": okr.key_results,
                "owner": okr.owner,
                "progress": okr.progress,
                "created_at": okr.created_at
            }
            for okr in active_okrs
        ],
        "total": len(active_okrs)
    })


@app.route('/api/congress/council/stats', methods=['GET'])
def get_council_stats():
    """Get council statistics"""
    global supreme_council
    
    if not supreme_council:
        return jsonify({"error": "Supreme Council not initialized"}), 500
    
    return jsonify(supreme_council.get_council_stats())


@app.route('/api/congress/discovery/candidates', methods=['GET'])
def get_discovery_candidates():
    """Get niche discovery candidates"""
    global niche_discovery_committee
    
    if not niche_discovery_committee:
        return jsonify({"error": "Niche Discovery Committee not initialized"}), 500
    
    status = request.args.get('status', None)
    
    candidates = list(niche_discovery_committee.candidates.values())
    
    if status:
        candidates = [c for c in candidates if c.status == status]
    
    return jsonify({
        "candidates": [
            {
                "niche_id": c.niche_id,
                "name": c.name,
                "description": c.description,
                "source": c.source,
                "keywords": c.keywords,
                "status": c.status,
                "initial_score": c.initial_score
            }
            for c in candidates
        ],
        "total": len(candidates)
    })


@app.route('/api/congress/discovery/validated', methods=['GET'])
def get_validated_niches():
    """Get validated niches"""
    global niche_discovery_committee
    
    if not niche_discovery_committee:
        return jsonify({"error": "Niche Discovery Committee not initialized"}), 500
    
    validated_ids = niche_discovery_committee.validated_niches
    validated = [
        niche_discovery_committee.candidates[nid]
        for nid in validated_ids
        if nid in niche_discovery_committee.candidates
    ]
    
    return jsonify({
        "validated_niches": [
            {
                "niche_id": c.niche_id,
                "name": c.name,
                "description": c.description,
                "keywords": c.keywords,
                "monetization_potential": c.monetization_potential
            }
            for c in validated
        ],
        "total": len(validated)
    })


@app.route('/api/congress/discovery/stats', methods=['GET'])
def get_discovery_stats():
    """Get niche discovery statistics"""
    global niche_discovery_committee, discovery_engine
    
    if not niche_discovery_committee:
        return jsonify({"error": "Niche Discovery Committee not initialized"}), 500
    
    committee_stats = niche_discovery_committee.get_discovery_stats()
    
    engine_stats = {}
    if discovery_engine:
        engine_stats = discovery_engine.get_discovery_stats()
    
    return jsonify({
        "committee": committee_stats,
        "engine": engine_stats
    })


@app.route('/api/congress/roi/summary', methods=['GET'])
def get_roi_summary():
    """Get comprehensive ROI summary"""
    global roi_tracker
    
    if not roi_tracker:
        return jsonify({"error": "ROI Tracker not initialized"}), 500
    
    return jsonify(roi_tracker.get_roi_summary())


@app.route('/api/congress/roi/niche/<niche_id>', methods=['GET'])
def get_niche_roi(niche_id: str):
    """Get ROI history for a specific niche"""
    global roi_tracker
    
    if not roi_tracker:
        return jsonify({"error": "ROI Tracker not initialized"}), 500
    
    limit = request.args.get('limit', 30, type=int)
    history = roi_tracker.get_niche_roi_history(niche_id, limit)
    
    return jsonify({
        "niche_id": niche_id,
        "history": [
            {
                "roi_percentage": m.roi_percentage,
                "revenue": m.revenue,
                "costs": m.costs,
                "calculated_at": m.calculated_at
            }
            for m in history
        ],
        "total": len(history)
    })


@app.route('/api/congress/roi/agent/<agent_id>', methods=['GET'])
def get_agent_roi(agent_id: str):
    """Get ROI history for a specific agent"""
    global roi_tracker
    
    if not roi_tracker:
        return jsonify({"error": "ROI Tracker not initialized"}), 500
    
    limit = request.args.get('limit', 30, type=int)
    history = roi_tracker.get_agent_roi_history(agent_id, limit)
    
    return jsonify({
        "agent_id": agent_id,
        "history": [
            {
                "roi_percentage": m.roi_percentage,
                "revenue": m.revenue,
                "costs": m.costs,
                "calculated_at": m.calculated_at
            }
            for m in history
        ],
        "total": len(history)
    })


@app.route('/api/congress/roi/top-niches', methods=['GET'])
def get_top_niches():
    """Get top performing niches"""
    global roi_tracker
    
    if not roi_tracker:
        return jsonify({"error": "ROI Tracker not initialized"}), 500
    
    limit = request.args.get('limit', 10, type=int)
    top_niches = roi_tracker.get_top_performing_niches(limit)
    
    return jsonify({
        "top_niches": top_niches,
        "total": len(top_niches)
    })


@app.route('/api/congress/roi/top-agents', methods=['GET'])
def get_top_agents():
    """Get top performing agents"""
    global roi_tracker
    
    if not roi_tracker:
        return jsonify({"error": "ROI Tracker not initialized"}), 500
    
    limit = request.args.get('limit', 10, type=int)
    top_agents = roi_tracker.get_top_performing_agents(limit)
    
    return jsonify({
        "top_agents": top_agents,
        "total": len(top_agents)
    })


# ==================== END CONGRESS SYSTEM ENDPOINTS ====================


def initialize_hive():
    """Initialize the hive with starting population"""
    global population, evolution_engine, orchestrator_evo
    global code_vault, coder_agent, healer
    global supreme_council, niche_discovery_committee, roi_tracker, discovery_engine
    
    logger.info("🐝 Initializing The Hive...")
    
    # Validate configuration
    config.validate()
    
    # Initialize evolution engine
    evolution_engine = DeepSeekEvolutionEngine(
        base_url=config.api.deepseek_base_url,
        model=config.api.deepseek_model
    )
    
    orchestrator_evo = EvolutionOrchestrator(
        engine=evolution_engine,
        population_size=config.evolution.population_size,
        elite_size=config.evolution.elite_size,
        mutation_rate=config.evolution.mutation_rate,
        crossover_rate=config.evolution.crossover_rate
    )
    
    # Initialize D8-GENESIS components
    logger.info("🧬 Initializing D8-GENESIS module...")
    try:
        code_vault = CodeVault()
        coder_agent = CoderAgent(evolution_engine, code_vault)
        healer = SelfHealingOrchestrator(coder_agent, max_healing_attempts=3)
        logger.info("✅ D8-GENESIS initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ D8-GENESIS initialization failed (non-critical): {e}")
        code_vault = None
        coder_agent = None
        healer = None
    
    # Initialize Congress System
    logger.info("🏛️ Initializing Congress System...")
    try:
        from app.congress.supreme_council import SupremeCouncil
        from app.congress.niche_discovery.committee import NicheDiscoveryCommittee
        from app.congress.niche_discovery.discovery_engine import DiscoveryEngine
        from app.metrics.roi_tracker import ROITracker
        
        # Initialize Supreme Council
        supreme_council = SupremeCouncil(
            council_size=config.congress.council_size,
            voting_threshold=config.congress.council_voting_threshold
        )
        
        # Initialize Niche Discovery Committee
        niche_discovery_committee = NicheDiscoveryCommittee()
        
        # Initialize Discovery Engine
        discovery_engine = DiscoveryEngine(
            discovery_frequency_hours=config.congress.discovery_frequency_hours,
            candidates_per_cycle=config.congress.discovery_candidates_per_cycle,
            deep_analysis_batch_size=config.congress.deep_analysis_batch_size
        )
        
        # Initialize ROI Tracker
        roi_tracker = ROITracker()
        
        logger.info("✅ Congress System initialized successfully")
        logger.info(f"   - Supreme Council: {supreme_council.council_size} members")
        logger.info(f"   - Niche Discovery: Ready for 24/7 operation")
        logger.info(f"   - ROI Tracker: Multi-level tracking enabled")
        
    except Exception as e:
        logger.warning(f"⚠️ Congress System initialization failed (non-critical): {e}")
        supreme_council = None
        niche_discovery_committee = None
        discovery_engine = None
        roi_tracker = None
    
    # Create initial population with diverse prompts
    initial_prompts = [
        "You are an AI content writer specializing in tech product reviews. Focus on SEO optimization and user engagement.",
        "You are a lifestyle blogger creating viral social media content. Prioritize emotional connection and shareability.",
        "You are a financial advisor writing investment guides for beginners. Balance education with monetization.",
        "You are a health and wellness coach creating transformational content. Focus on actionable advice and trust-building.",
        "You are a travel enthusiast documenting unique experiences. Emphasize storytelling and visual appeal."
    ]
    
    # Expand to desired population size
    while len(initial_prompts) < config.evolution.population_size:
        initial_prompts.append(
            f"You are an AI agent specialized in content generation. "
            f"Your unique angle: {['data-driven', 'emotional', 'contrarian', 'practical'][len(initial_prompts) % 4]} approach."
        )
    
    for prompt in initial_prompts[:config.evolution.population_size]:
        genome = Genome(prompt=prompt)
        agent = BaseAgent(
            genome=genome,
            groq_api_key=config.api.groq_api_key,
            model=config.agent.groq_model
        )
        population.append(agent)
    
    logger.info(f"✅ Hive initialized with {len(population)} agents")
    logger.info(f"🎯 Ready to evolve for {config.evolution.generations} generations")
    
    # FASE 2: Initialize economy systems
    if ECONOMY_AVAILABLE:
        economy_ready = initialize_economy_systems()
        if economy_ready:
            logger.info("💰 Economy systems initialized and ready")
            
            # Connect agents to economy
            for agent in population:
                agent.credits_system = credits_system
                agent.accounting_system = accounting_system
                if credits_system:
                    agent.wallet = credits_system.create_wallet(agent.agent_id)
            
            logger.info(f"💰 {len(population)} agent wallets created")
            
            # Connect economy to orchestrator
            if orchestrator_evo:
                orchestrator_evo.revenue_attribution = revenue_attribution
                logger.info("💰 Revenue attribution connected to evolution")


# FASE 2: Economy API Endpoints

@app.route('/api/economy/status', methods=['GET'])
def economy_status():
    """Get current economy system status"""
    if not ECONOMY_AVAILABLE or not credits_system:
        return jsonify({"error": "Economy system not available"}), 503
    
    return jsonify({
        "total_revenue": credits_system.get_total_revenue(),
        "active_wallets": len(credits_system.wallets),
        "total_transactions": sum(len(w.transactions) for w in credits_system.wallets.values()),
        "budget_status": {
            cat: {
                "spent": accounting_system.get_total_expenses(category=cat),
                "budget": accounting_system.budgets.get(cat, {}).get("amount", 0)
            }
            for cat in ["api_calls", "infrastructure", "research"]
        } if accounting_system else {},
        "top_earners": [
            {
                "agent_id": agent.agent_id[:8],
                "revenue": agent.get_total_revenue(),
                "roi": agent.get_roi()
            }
            for agent in sorted(population, key=lambda a: a.get_total_revenue(), reverse=True)[:5]
        ]
    })


@app.route('/api/economy/report', methods=['GET'])
def economy_report():
    """Generate comprehensive accounting report"""
    if not ECONOMY_AVAILABLE or not accounting_system:
        return jsonify({"error": "Accounting system not available"}), 503
    
    try:
        report = accounting_system.generate_daily_report()
        return jsonify(report)
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/economy/wallets', methods=['GET'])
def list_wallets():
    """List all agent wallets"""
    if not ECONOMY_AVAILABLE or not credits_system:
        return jsonify({"error": "Credits system not available"}), 503
    
    wallets_data = []
    for agent_id, wallet in credits_system.wallets.items():
        wallets_data.append({
            "agent_id": agent_id[:8],
            "balance": wallet.balance,
            "total_received": sum(t.amount for t in wallet.transactions if t.amount > 0),
            "total_spent": abs(sum(t.amount for t in wallet.transactions if t.amount < 0)),
            "transaction_count": len(wallet.transactions)
        })
    
    wallets_data.sort(key=lambda w: w['balance'], reverse=True)
    
    return jsonify({
        "total_wallets": len(wallets_data),
        "wallets": wallets_data
    })


if __name__ == "__main__":
    # Initialize
    initialize_hive()
    
    # Start Flask server
    logger.info(f"🚀 Starting Flask server on port {config.flask.flask_port}")
    app.run(
        host='0.0.0.0',
        port=config.flask.flask_port,
        debug=config.flask.flask_debug
    )
