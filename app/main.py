"""
The Hive - Main Entry Point
Evolutionary AI Agent Ecosystem
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
        "version": "0.1.0",
        "population_size": len(population),
        "d8_genesis": {
            "code_vault_ready": code_vault is not None,
            "coder_agent_ready": coder_agent is not None,
            "healer_ready": healer is not None
        },
        "endpoints": {
            "/": "This health check",
            "/api/agents": "List all agents",
            "/api/agents/<id>": "Get agent details",
            "/api/evolve": "Trigger evolution cycle",
            "/api/genesis/ingest": "Ingest legacy code",
            "/api/genesis/generate": "Generate polymorphic code",
            "/api/genesis/heal": "Self-heal broken code",
            "/api/genesis/stats": "D8-GENESIS statistics"
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


def initialize_hive():
    """Initialize the hive with starting population"""
    global population, evolution_engine, orchestrator_evo
    global code_vault, coder_agent, healer
    
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
