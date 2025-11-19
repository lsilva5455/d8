"""
Base Agent - The Protagonist
Autonomous AI agent with genetic material (genome) that can act and evolve
Uses Groq for fast, low-cost decision making
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import uuid
from groq import Groq
from app.evolution.darwin import Genome

logger = logging.getLogger(__name__)


@dataclass
class AgentAction:
    """Represents an action taken by an agent"""
    action_type: str  # e.g., "generate_content", "publish_post", "analyze_niche"
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    success: bool = False
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tokens_used: int = 0
    execution_time_ms: int = 0


@dataclass
class AgentMetrics:
    """Performance metrics for fitness evaluation"""
    total_actions: int = 0
    successful_actions: int = 0
    revenue_generated: float = 0.0
    content_published: int = 0
    traffic_generated: int = 0
    engagement_score: float = 0.0
    cost_tokens: float = 0.0
    
    def get_fitness(self) -> float:
        """
        Calculate fitness score based on metrics
        Formula: Revenue weighted by success rate and efficiency
        """
        if self.total_actions == 0:
            return 0.0
        
        success_rate = self.successful_actions / self.total_actions
        roi = (self.revenue_generated - self.cost_tokens) if self.cost_tokens > 0 else self.revenue_generated
        
        fitness = (
            0.5 * roi +                    # Revenue is primary
            0.3 * success_rate * 100 +     # Success rate (0-100)
            0.2 * self.engagement_score    # Engagement matters
        )
        
        return max(0.0, fitness)  # Non-negative


class BaseAgent:
    """
    Base Agent with genome-based behavior
    
    The agent:
    1. Loads its genetic material (system prompt)
    2. Uses Groq for fast decision-making
    3. Returns structured JSON responses
    4. Tracks metrics for fitness evaluation
    """
    
    def __init__(self, 
                 genome: Genome,
                 groq_api_key: str,
                 agent_id: Optional[str] = None,
                 model: str = "llama-3.3-70b-versatile"):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.genome = genome
        self.model = model
        self.metrics = AgentMetrics()
        self.action_history: List[AgentAction] = []
        
        # Initialize Groq client
        self.groq = Groq(api_key=groq_api_key)
        
        logger.info(f"🤖 Agent {self.agent_id[:8]} initialized (Gen {genome.generation})")
    
    def act(self, input_data: Dict[str, Any], action_type: str = "generic") -> Dict[str, Any]:
        """
        Main action method - agent decides what to do based on input
        
        Args:
            input_data: Context and information for the agent
            action_type: Type of action to perform
        
        Returns:
            Structured JSON response with action details
        """
        start_time = datetime.utcnow()
        
        logger.info(f"🎯 Agent {self.agent_id[:8]} acting: {action_type}")
        
        # Construct messages for Groq
        messages = [
            {
                "role": "system",
                "content": self.genome.prompt  # Agent's genetic material
            },
            {
                "role": "user",
                "content": self._format_input(input_data, action_type)
            }
        ]
        
        try:
            # Call Groq API (fast and cheap)
            response = self.groq.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
                # Note: llama-3.3 doesn't support response_format yet
            )
            
            # Try to parse response as JSON
            content = response.choices[0].message.content
            try:
                result = json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, wrap in generic format
                result = {
                    "action": action_type,
                    "response": content,
                    "success": True
                }
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Track action
            action = AgentAction(
                action_type=action_type,
                parameters=input_data,
                result=result,
                success=True,
                tokens_used=response.usage.total_tokens,
                execution_time_ms=int(execution_time)
            )
            
            self._record_action(action)
            
            logger.info(f"✅ Action completed in {execution_time:.0f}ms ({response.usage.total_tokens} tokens)")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Groq returned invalid JSON: {e}")
            error_action = AgentAction(
                action_type=action_type,
                parameters=input_data,
                success=False
            )
            self._record_action(error_action)
            
            return {
                "success": False,
                "error": "Invalid JSON response from model",
                "action_type": action_type
            }
            
        except Exception as e:
            logger.error(f"❌ Action failed: {e}")
            error_action = AgentAction(
                action_type=action_type,
                parameters=input_data,
                success=False
            )
            self._record_action(error_action)
            
            return {
                "success": False,
                "error": str(e),
                "action_type": action_type
            }
    
    def _format_input(self, input_data: Dict[str, Any], action_type: str) -> str:
        """Format input data into a prompt for the agent"""
        prompt = f"""You are performing action: {action_type}

INPUT DATA:
{json.dumps(input_data, indent=2)}

INSTRUCTIONS:
1. Analyze the input data
2. Decide on the best course of action based on your system prompt
3. Return a JSON response with your decision

REQUIRED JSON FORMAT:
{{
    "action": "specific_action_to_take",
    "reasoning": "why this action was chosen",
    "parameters": {{
        "key": "value"
    }},
    "expected_outcome": "what you expect to achieve",
    "confidence": 0.0-1.0
}}

Respond now with your decision in JSON format:"""
        
        return prompt
    
    def _record_action(self, action: AgentAction) -> None:
        """Record action and update metrics"""
        self.action_history.append(action)
        
        self.metrics.total_actions += 1
        if action.success:
            self.metrics.successful_actions += 1
        
        # Update token costs (Groq pricing: ~$0.10 per 1M tokens for Mixtral)
        self.metrics.cost_tokens += action.tokens_used * 0.0000001
    
    def get_fitness(self) -> float:
        """Get current fitness score"""
        return self.metrics.get_fitness()
    
    def update_metrics(self, 
                      revenue: Optional[float] = None,
                      traffic: Optional[int] = None,
                      engagement: Optional[float] = None) -> None:
        """Update agent metrics from external sources"""
        if revenue is not None:
            self.metrics.revenue_generated += revenue
        if traffic is not None:
            self.metrics.traffic_generated += traffic
        if engagement is not None:
            self.metrics.engagement_score = engagement
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        return {
            "agent_id": self.agent_id,
            "generation": self.genome.generation,
            "fitness": self.get_fitness(),
            "metrics": {
                "total_actions": self.metrics.total_actions,
                "success_rate": (
                    self.metrics.successful_actions / self.metrics.total_actions
                    if self.metrics.total_actions > 0 else 0
                ),
                "revenue": self.metrics.revenue_generated,
                "traffic": self.metrics.traffic_generated,
                "cost": self.metrics.cost_tokens
            },
            "last_action": (
                self.action_history[-1].timestamp 
                if self.action_history else None
            )
        }
    
    def save_genome(self, filepath: str) -> None:
        """Save agent's genome to file"""
        genome_data = {
            "agent_id": self.agent_id,
            "prompt": self.genome.prompt,
            "generation": self.genome.generation,
            "fitness": self.get_fitness(),
            "parent_ids": self.genome.parent_ids,
            "mutations": self.genome.mutations,
            "created_at": self.genome.created_at,
            "saved_at": datetime.utcnow().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(genome_data, f, indent=2)
        
        logger.info(f"💾 Genome saved: {filepath}")
    
    @classmethod
    def load_genome(cls, filepath: str, groq_api_key: str) -> 'BaseAgent':
        """Load agent from saved genome"""
        with open(filepath, 'r') as f:
            genome_data = json.load(f)
        
        genome = Genome(
            prompt=genome_data["prompt"],
            fitness=genome_data.get("fitness", 0.0),
            generation=genome_data["generation"],
            parent_ids=genome_data.get("parent_ids", []),
            mutations=genome_data.get("mutations", []),
            created_at=genome_data.get("created_at")
        )
        
        agent = cls(
            genome=genome,
            groq_api_key=groq_api_key,
            agent_id=genome_data.get("agent_id")
        )
        
        logger.info(f"📂 Agent loaded from {filepath}")
        return agent


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create a test genome
    test_genome = Genome(
        prompt="""You are an AI content strategist specialized in tech niches.
Your goal is to generate high-quality, SEO-optimized content that drives traffic and revenue.
Always prioritize user value, originality, and monetization potential."""
    )
    
    # Initialize agent (replace with real API key)
    agent = BaseAgent(
        genome=test_genome,
        groq_api_key="your_groq_api_key_here"
    )
    
    # Test action
    input_data = {
        "niche": "AI tools for developers",
        "target_audience": "software engineers",
        "goal": "generate blog post ideas"
    }
    
    result = agent.act(input_data, action_type="generate_content_ideas")
    
    print("\n🎯 Action Result:")
    print(json.dumps(result, indent=2))
    
    print("\n📊 Agent Status:")
    print(json.dumps(agent.get_status(), indent=2))
