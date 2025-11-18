"""
Groq-based Evolution Engine
Lightweight alternative to DeepSeek for resource-constrained environments (Raspberry Pi)
"""

from app.integrations.groq_client import GroqClient
from app.evolution.darwin import Genome
from dataclasses import dataclass
import logging
import random

logger = logging.getLogger(__name__)


@dataclass
class GroqEvolutionEngine:
    """
    Evolution engine using Groq API instead of local DeepSeek
    Perfect for Raspberry Pi deployment where local LLMs are not feasible
    """
    
    groq_client: GroqClient
    model: str = "llama-3.1-8b-instant"
    temperature: float = 0.9
    
    def crossover(self, parent1: Genome, parent2: Genome) -> Genome:
        """
        Intelligently merge two parent genomes using Groq
        Cost: ~$0.0001 per crossover
        """
        meta_prompt = f"""You are an expert in genetic algorithms for AI agents.

TASK: Merge two parent system prompts to create a superior offspring.

PARENT 1:
{parent1.prompt}

PARENT 2:
{parent2.prompt}

INSTRUCTIONS:
1. Identify the best traits from each parent
2. Combine them intelligently (not just concatenation)
3. Maintain coherent agent identity
4. Preserve successful strategies
5. Introduce synergy between parent traits

OUTPUT: Write the complete system prompt for the offspring agent.
Keep it under 200 words, focused and actionable."""

        try:
            offspring_prompt = self.groq_client.chat(
                messages=[{"role": "user", "content": meta_prompt}],
                model=self.model,
                temperature=self.temperature,
                max_tokens=300
            )
            
            logger.info(f"✅ Crossover complete via Groq")
            
            return Genome(
                prompt=offspring_prompt.strip(),
                generation=parent1.generation + 1,
                parent_ids=[parent1.genome_id, parent2.genome_id]
            )
            
        except Exception as e:
            logger.error(f"Crossover failed: {e}")
            # Fallback: simple concatenation
            return Genome(
                prompt=f"{parent1.prompt[:100]} {parent2.prompt[:100]}",
                generation=parent1.generation + 1
            )
    
    def mutate(self, genome: Genome) -> Genome:
        """
        Introduce beneficial mutations using Groq
        Cost: ~$0.00005 per mutation
        """
        mutation_types = [
            "tone_shift",
            "niche_specialization", 
            "strategy_optimization",
            "creative_variation"
        ]
        
        mutation_type = random.choice(mutation_types)
        
        mutation_prompts = {
            "tone_shift": f"""Modify this AI agent prompt by changing its communication tone.

ORIGINAL:
{genome.prompt}

Make it more: {random.choice(['professional', 'casual', 'persuasive', 'authoritative'])}
Keep core strategy intact. Output the modified prompt only.""",

            "niche_specialization": f"""Specialize this AI agent for a specific niche.

ORIGINAL:
{genome.prompt}

Add expertise in: {random.choice(['tech reviews', 'lifestyle', 'finance', 'health', 'travel'])}
Keep output under 150 words.""",

            "strategy_optimization": f"""Optimize this agent's strategy for higher engagement.

ORIGINAL:
{genome.prompt}

Add techniques for: {random.choice(['SEO', 'viral content', 'storytelling', 'data-driven insights'])}
Output optimized prompt only.""",

            "creative_variation": f"""Add creative flair to this agent.

ORIGINAL:
{genome.prompt}

Introduce: {random.choice(['humor', 'emotion', 'controversy', 'uniqueness'])}
Keep it professional. Output new prompt."""
        }
        
        try:
            mutated_prompt = self.groq_client.chat(
                messages=[{"role": "user", "content": mutation_prompts[mutation_type]}],
                model=self.model,
                temperature=1.0,  # Higher for creativity
                max_tokens=200
            )
            
            logger.info(f"✅ Mutation ({mutation_type}) complete via Groq")
            
            return Genome(
                prompt=mutated_prompt.strip(),
                generation=genome.generation + 1,
                parent_ids=[genome.genome_id]
            )
            
        except Exception as e:
            logger.error(f"Mutation failed: {e}")
            # Fallback: minor text mutation
            words = genome.prompt.split()
            if len(words) > 10:
                insert_pos = random.randint(0, len(words))
                words.insert(insert_pos, random.choice([
                    "innovative", "strategic", "engaging", "data-driven"
                ]))
            
            return Genome(
                prompt=" ".join(words),
                generation=genome.generation + 1
            )


class LightweightEvolutionOrchestrator:
    """
    Simplified orchestrator for Raspberry Pi
    Reduces memory footprint and CPU usage
    """
    
    def __init__(
        self,
        engine: GroqEvolutionEngine,
        population_size: int = 3,
        elite_size: int = 1,
        mutation_rate: float = 0.15,
        crossover_rate: float = 0.7
    ):
        self.engine = engine
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generation = 0
        
        logger.info(f"🧬 Lightweight Evolution Engine initialized (Groq-powered)")
        logger.info(f"   Population: {population_size}, Elite: {elite_size}")
    
    def evolve_generation(self, current_population: list[Genome]) -> list[Genome]:
        """
        Evolve one generation with minimal resource usage
        """
        self.generation += 1
        logger.info(f"🔄 Generation {self.generation} starting...")
        
        # Sort by fitness
        sorted_pop = sorted(current_population, key=lambda g: g.fitness or 0, reverse=True)
        
        # Elitism: Keep top performers
        new_population = sorted_pop[:self.elite_size]
        logger.info(f"   Elite preserved: {[f'{g.fitness:.2f}' for g in new_population]}")
        
        # Fill rest via crossover and mutation
        while len(new_population) < self.population_size:
            if random.random() < self.crossover_rate:
                # Crossover
                parent1 = self._tournament_select(sorted_pop)
                parent2 = self._tournament_select(sorted_pop)
                child = self.engine.crossover(parent1, parent2)
            else:
                # Mutation only
                parent = self._tournament_select(sorted_pop)
                child = self.engine.mutate(parent)
            
            # Random mutation chance
            if random.random() < self.mutation_rate:
                child = self.engine.mutate(child)
            
            new_population.append(child)
        
        avg_fitness = sum(g.fitness or 0 for g in sorted_pop) / len(sorted_pop)
        logger.info(f"✅ Generation {self.generation} complete")
        logger.info(f"   Best: {sorted_pop[0].fitness:.2f}, Avg: {avg_fitness:.2f}")
        
        return new_population
    
    def _tournament_select(self, population: list[Genome], tournament_size: int = 2) -> Genome:
        """Select parent via tournament (low memory)"""
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda g: g.fitness or 0)
