"""
Darwin - Genetic Evolution Engine for Agent Prompts
Uses DeepSeek (local) for crossover and mutation operations
Optimized for cost: All evolution operations run locally, zero API cost
"""

from typing import List, Tuple
import random
import json
import logging
from dataclasses import dataclass
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Genome:
    """Represents an agent's genetic material (system prompt)"""
    prompt: str
    fitness: float = 0.0
    generation: int = 0
    parent_ids: List[str] = None
    mutations: List[str] = None
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.parent_ids is None:
            self.parent_ids = []
        if self.mutations is None:
            self.mutations = []


class DeepSeekEvolutionEngine:
    """Handles genetic operations using local DeepSeek model"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "deepseek-coder:33b"):
        self.base_url = base_url
        self.model = model
        self._validate_connection()
    
    def _validate_connection(self) -> None:
        """Verify DeepSeek/Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info(f"✅ Connected to DeepSeek at {self.base_url}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ DeepSeek not reachable: {e}")
            raise ConnectionError(
                f"Cannot connect to DeepSeek at {self.base_url}. "
                "Make sure Ollama is running: ollama serve"
            )
    
    def _call_deepseek(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call local DeepSeek model via Ollama API"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "max_tokens": max_tokens,
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            logger.error(f"DeepSeek call failed: {e}")
            raise
    
    def crossover(self, parent_a: Genome, parent_b: Genome) -> Genome:
        """
        Genetic crossover: Combine two parent prompts into a superior child
        
        Strategy: Use DeepSeek to intelligently merge the best traits
        of both parents, not just concatenate or randomly splice.
        """
        logger.info(f"🧬 Crossover: Parent A (fitness={parent_a.fitness:.2f}) × Parent B (fitness={parent_b.fitness:.2f})")
        
        meta_prompt = f"""You are a genetic engineer for AI agent prompts. Your task is to create a SUPERIOR child prompt by combining the best strategic elements from two parent prompts.

PARENT A (Fitness: {parent_a.fitness:.2f}):
{parent_a.prompt}

PARENT B (Fitness: {parent_b.fitness:.2f}):
{parent_b.prompt}

INSTRUCTIONS:
1. Analyze what makes each parent successful (high fitness = better performance)
2. Identify unique strengths in each parent
3. Synthesize a NEW prompt that:
   - Combines the best traits of both parents
   - Maintains coherence and clarity
   - Is innovative, not just a copy-paste
   - Is optimized for content generation and monetization

OUTPUT FORMAT (JSON):
{{
    "child_prompt": "The new synthesized system prompt",
    "reasoning": "Why this combination is superior",
    "inherited_traits": ["trait from parent A", "trait from parent B"]
}}

Generate the child prompt now:"""

        response = self._call_deepseek(meta_prompt, max_tokens=1500)
        
        try:
            # Parse JSON response
            result = json.loads(response)
            child_prompt = result.get("child_prompt", "")
            
            if not child_prompt:
                raise ValueError("DeepSeek returned empty child prompt")
            
            child = Genome(
                prompt=child_prompt,
                generation=max(parent_a.generation, parent_b.generation) + 1,
                parent_ids=[id(parent_a), id(parent_b)],
                mutations=[]
            )
            
            logger.info(f"✅ Child created (Gen {child.generation})")
            logger.debug(f"Reasoning: {result.get('reasoning', 'N/A')}")
            
            return child
            
        except json.JSONDecodeError:
            logger.warning("DeepSeek didn't return valid JSON, using raw response")
            # Fallback: Use raw response as prompt
            child = Genome(
                prompt=response.strip(),
                generation=max(parent_a.generation, parent_b.generation) + 1,
                parent_ids=[id(parent_a), id(parent_b)]
            )
            return child
    
    def mutate(self, genome: Genome, mutation_rate: float = 0.1) -> Genome:
        """
        Genetic mutation: Introduce controlled variations to a prompt
        
        Mutation types:
        - Tone shift (formal ↔ casual)
        - Focus change (niche specialization)
        - Strategy tweak (SEO, engagement, conversion)
        """
        if random.random() > mutation_rate:
            logger.debug(f"No mutation (rate={mutation_rate})")
            return genome  # No mutation
        
        mutation_types = [
            "tone_shift",
            "niche_specialization", 
            "strategy_optimization",
            "creative_twist"
        ]
        
        mutation_type = random.choice(mutation_types)
        logger.info(f"🧪 Mutation: {mutation_type} on Gen {genome.generation}")
        
        meta_prompt = f"""You are a genetic mutator for AI agent prompts. Introduce a controlled variation to improve the prompt.

ORIGINAL PROMPT:
{genome.prompt}

MUTATION TYPE: {mutation_type}
- tone_shift: Change writing style (formal/casual/technical/creative)
- niche_specialization: Focus on a specific sub-niche
- strategy_optimization: Enhance SEO, engagement, or monetization strategy
- creative_twist: Add unexpected but valuable element

INSTRUCTIONS:
1. Apply the mutation type to create a variant
2. Keep 80% of the original, change 20%
3. The mutation should potentially improve fitness
4. Maintain coherence

OUTPUT FORMAT (JSON):
{{
    "mutated_prompt": "The new prompt with mutation applied",
    "mutation_description": "What was changed and why"
}}

Generate the mutated prompt now:"""

        response = self._call_deepseek(meta_prompt, max_tokens=1500)
        
        try:
            result = json.loads(response)
            mutated_prompt = result.get("mutated_prompt", "")
            
            if not mutated_prompt:
                raise ValueError("DeepSeek returned empty mutated prompt")
            
            mutated = Genome(
                prompt=mutated_prompt,
                generation=genome.generation + 1,
                parent_ids=[id(genome)],
                mutations=genome.mutations + [mutation_type]
            )
            
            logger.info(f"✅ Mutation applied: {result.get('mutation_description', 'N/A')}")
            return mutated
            
        except json.JSONDecodeError:
            logger.warning("DeepSeek didn't return valid JSON for mutation")
            # Fallback: Minor random change
            mutated = Genome(
                prompt=genome.prompt,  # Keep original if parsing fails
                generation=genome.generation,
                mutations=genome.mutations
            )
            return mutated


class EvolutionOrchestrator:
    """Manages the full evolutionary cycle: selection, crossover, mutation"""
    
    def __init__(self, 
                 engine: DeepSeekEvolutionEngine,
                 population_size: int = 20,
                 elite_size: int = 2,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.7):
        self.engine = engine
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generation = 0
    
    def select_parents(self, population: List[Genome]) -> Tuple[Genome, Genome]:
        """Tournament selection: Pick best from random sample"""
        tournament_size = 3
        tournament = random.sample(population, min(tournament_size, len(population)))
        tournament.sort(key=lambda g: g.fitness, reverse=True)
        return tournament[0], tournament[1] if len(tournament) > 1 else tournament[0]
    
    def evolve_generation(self, population: List[Genome]) -> List[Genome]:
        """
        Evolve one generation using genetic algorithm
        
        Process:
        1. Select elite (top performers) → pass unchanged
        2. Generate offspring via crossover
        3. Apply mutations
        4. Return new population
        """
        # Sort by fitness
        population.sort(key=lambda g: g.fitness, reverse=True)
        
        logger.info(f"\n🧬 GENERATION {self.generation} EVOLUTION")
        logger.info(f"Population size: {len(population)}")
        logger.info(f"Best fitness: {population[0].fitness:.2f}")
        logger.info(f"Avg fitness: {sum(g.fitness for g in population) / len(population):.2f}")
        
        # Elitism: Keep top performers
        new_population = population[:self.elite_size]
        logger.info(f"✅ Elite preserved: {self.elite_size} agents")
        
        # Generate offspring
        offspring_count = self.population_size - self.elite_size
        
        for i in range(offspring_count):
            # Crossover
            if random.random() < self.crossover_rate:
                parent_a, parent_b = self.select_parents(population)
                child = self.engine.crossover(parent_a, parent_b)
            else:
                # Clone a parent
                child = random.choice(population[:self.population_size // 2])
            
            # Mutation
            child = self.engine.mutate(child, self.mutation_rate)
            
            new_population.append(child)
        
        self.generation += 1
        logger.info(f"✅ Generation {self.generation} created: {len(new_population)} agents\n")
        
        return new_population


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize evolution engine
    engine = DeepSeekEvolutionEngine()
    orchestrator = EvolutionOrchestrator(engine)
    
    # Create initial population
    initial_prompts = [
        "You are an SEO content writer focused on tech reviews.",
        "You are a lifestyle blogger creating engaging social media posts.",
        "You are a financial advisor writing investment guides."
    ]
    
    population = [Genome(prompt=p, fitness=random.uniform(0, 1)) for p in initial_prompts]
    
    # Evolve for 3 generations
    for gen in range(3):
        population = orchestrator.evolve_generation(population)
        
        # In real scenario, agents would act and get fitness scores here
        for agent in population:
            agent.fitness = random.uniform(0, 1)  # Simulated fitness
    
    print("\n🏆 Final Population:")
    for i, agent in enumerate(sorted(population, key=lambda g: g.fitness, reverse=True)[:5]):
        print(f"\n{i+1}. Fitness: {agent.fitness:.2f} | Gen: {agent.generation}")
        print(f"   Prompt: {agent.prompt[:100]}...")
