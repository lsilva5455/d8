"""
The Hive - Main Entry Point
Evolutionary AI Agent Ecosystem
"""

from flask import Flask, jsonify, request
from app.config import config
from app.agents.base_agent import BaseAgent
from app.evolution.darwin import Genome, DeepSeekEvolutionEngine, EvolutionOrchestrator
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

# Global state (in production, use proper state management)
population: List[BaseAgent] = []
evolution_engine: DeepSeekEvolutionEngine = None
orchestrator: EvolutionOrchestrator = None


@app.route('/')
def index():
    """API health check"""
    return jsonify({
        "status": "online",
        "project": "The Hive",
        "version": "0.1.0",
        "population_size": len(population),
        "endpoints": {
            "/": "This health check",
            "/api/agents": "List all agents",
            "/api/agents/<id>": "Get agent details",
            "/api/evolve": "Trigger evolution cycle"
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
    global population, orchestrator
    
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
        new_genomes = orchestrator.evolve_generation(genomes)
        
        # Create new agent population
        population.clear()
        for genome in new_genomes:
            agent = BaseAgent(
                genome=genome,
                groq_api_key=config.api.groq_api_key,
                model=config.agent.groq_model
            )
            population.append(agent)
        
        logger.info(f"✅ Evolution complete: Generation {orchestrator.generation}")
        
        return jsonify({
            "success": True,
            "generation": orchestrator.generation,
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


def initialize_hive():
    """Initialize the hive with starting population"""
    global population, evolution_engine, orchestrator
    
    logger.info("🐝 Initializing The Hive...")
    
    # Validate configuration
    config.validate()
    
    # Initialize evolution engine
    evolution_engine = DeepSeekEvolutionEngine(
        base_url=config.api.deepseek_base_url,
        model=config.api.deepseek_model
    )
    
    orchestrator = EvolutionOrchestrator(
        engine=evolution_engine,
        population_size=config.evolution.population_size,
        elite_size=config.evolution.elite_size,
        mutation_rate=config.evolution.mutation_rate,
        crossover_rate=config.evolution.crossover_rate
    )
    
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
