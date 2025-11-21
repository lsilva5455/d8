"""
Base Agent - The Protagonist
Autonomous AI agent with genetic material (genome) that can act and evolve
Uses LLM Fallback Manager for robust AI calls with automatic fallback
Integrated with D8 Economy System for revenue tracking
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
import logging
import uuid
from app.evolution.darwin import Genome

# Import economy system components
try:
    from app.economy.d8_credits import D8CreditsSystem
    from app.economy.accounting import AutonomousAccountingSystem
    ECONOMY_AVAILABLE = True
except ImportError:
    ECONOMY_AVAILABLE = False
    logging.warning("Economy system not available - agent will run without economic integration")

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
    2. Uses LLM Fallback Manager for robust AI calls
    3. Returns structured JSON responses
    4. Tracks metrics for fitness evaluation
    5. Manages wallet and economic transactions (FASE 2)
    """
    
    def __init__(self, 
                 genome: Genome,
                 groq_api_key: str = None,  # Deprecated, kept for compatibility
                 agent_id: Optional[str] = None,
                 model: str = "llama-3.3-70b-versatile",
                 credits_system: Optional[Any] = None,
                 accounting_system: Optional[Any] = None,
                 llm_manager: Optional[Any] = None):
        self.agent_id = agent_id or str(uuid.uuid4())
        self.genome = genome
        self.model = model
        self.metrics = AgentMetrics()
        self.action_history: List[AgentAction] = []
        
        # Use LLM Fallback Manager (singleton)
        if llm_manager is None:
            from app.llm_manager_singleton import get_llm_manager
            self.llm_manager = get_llm_manager()
        else:
            self.llm_manager = llm_manager
        
        # FASE 2: Initialize economy integration
        self.credits_system = credits_system
        self.accounting_system = accounting_system
        self.wallet = None
        
        if ECONOMY_AVAILABLE and credits_system:
            try:
                # Create wallet for this agent
                self.wallet = self.credits_system.create_wallet(self.agent_id)
                logger.info(f"💰 Wallet created for agent {self.agent_id[:8]}")
            except Exception as e:
                logger.warning(f"Could not create wallet: {e}")
        
        logger.info(f"🤖 Agent {self.agent_id[:8]} initialized (Gen {genome.generation})")
    
    def act(self, input_data: Dict[str, Any], action_type: str = "generic") -> Dict[str, Any]:
        """
        Main action method - agent decides what to do based on input
        Uses LLM Fallback Manager for robust execution with automatic fallback
        
        Args:
            input_data: Context and information for the agent
            action_type: Type of action to perform
        
        Returns:
            Structured JSON response with action details
        """
        start_time = datetime.utcnow()
        
        logger.info(f"🎯 Agent {self.agent_id[:8]} acting: {action_type}")
        
        # Construct messages for LLM
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
            # Use LLM Fallback Manager (automatic fallback Groq → Gemini → DeepSeek)
            response, provider_used = self.llm_manager.chat(
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                json_mode=True,
                context=f"Agent {self.agent_id[:8]} - Action: {action_type}"
            )
            
            # Check if all providers failed
            if response is None:
                logger.error(f"❌ Todos los LLM providers fallaron - acción derivada al Congreso")
                error_action = AgentAction(
                    action_type=action_type,
                    parameters=input_data,
                    success=False
                )
                self._record_action(error_action)
                
                return {
                    "success": False,
                    "error": "All LLM providers failed - escalated to Congress",
                    "action_type": action_type,
                    "escalated_to_congress": True
                }
            
            # Parse response content
            content = response.get("content", "")
            tokens_used = response.get("tokens_used", 0)
            
            try:
                # Si content ya es un dict, usarlo directamente
                if isinstance(content, dict):
                    result = content
                else:
                    # Si es string, intentar parsear como JSON
                    result = json.loads(content)
            except (json.JSONDecodeError, TypeError):
                # If not JSON, wrap in generic format
                result = {
                    "action": action_type,
                    "response": str(content),
                    "success": True
                }
            
            # Add provider info to result
            result["llm_provider"] = provider_used
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Track action
            action = AgentAction(
                action_type=action_type,
                parameters=input_data,
                result=result,
                success=True,
                tokens_used=tokens_used,
                execution_time_ms=int(execution_time)
            )
            
            self._record_action(action)
            
            # FASE 2: Record API cost
            self._record_api_cost(tokens_used)
            
            # FASE 2: Check for revenue in result
            if result.get('revenue', 0) > 0:
                self._record_revenue(result['revenue'], f"{action_type}_generated")
            
            logger.info(
                f"✅ Action completed in {execution_time:.0f}ms "
                f"({tokens_used} tokens via {provider_used})"
            )
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ LLM returned invalid JSON: {e}")
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
    
    # FASE 2: Economic Integration Methods
    
    def _record_api_cost(self, tokens: int) -> None:
        """Record cost of API call"""
        if not self.credits_system or not self.accounting_system:
            return
        
        # Groq pricing: ~$0.10 per 1M tokens for Mixtral/Llama
        cost_per_token = 0.0000001
        cost = tokens * cost_per_token
        
        try:
            # Record expense in accounting system
            self.accounting_system.record_expense(
                amount=cost,
                category="api_calls",
                description=f"Agent {self.agent_id[:8]} - Groq API ({tokens} tokens)",
                metadata={"agent_id": self.agent_id, "tokens": tokens}
            )
            
            # Deduct from wallet
            if self.wallet:
                # This would deduct from wallet balance in real implementation
                pass
            
            logger.debug(f"💸 API cost recorded: ${cost:.6f} ({tokens} tokens)")
            
        except Exception as e:
            logger.warning(f"Could not record API cost: {e}")
    
    def _record_revenue(self, amount: float, source: str) -> None:
        """Record revenue generated by agent"""
        if not self.credits_system:
            return
        
        try:
            # Update metrics
            self.metrics.revenue_generated += amount
            
            # Record in credits system
            self.credits_system.record_revenue(
                agent_id=self.agent_id,
                amount=amount,
                source=source,
                metadata={"timestamp": datetime.utcnow().isoformat()}
            )
            
            # Record in accounting
            if self.accounting_system:
                self.accounting_system.record_revenue(
                    amount=amount,
                    source=source,
                    description=f"Agent {self.agent_id[:8]} - {source}",
                    metadata={"agent_id": self.agent_id}
                )
            
            logger.info(f"💰 Revenue recorded: ${amount:.2f} from {source}")
            
        except Exception as e:
            logger.warning(f"Could not record revenue: {e}")
    
    def get_wallet_balance(self) -> float:
        """Get current wallet balance"""
        if not self.wallet:
            return 0.0
        
        try:
            return self.wallet.balance
        except:
            return 0.0
    
    def get_total_revenue(self) -> float:
        """Get total revenue generated"""
        return self.metrics.revenue_generated
    
    def get_total_costs(self) -> float:
        """Get total costs incurred"""
        return self.metrics.cost_tokens
    
    def get_roi(self) -> float:
        """Calculate Return on Investment"""
        if self.metrics.cost_tokens == 0:
            return self.metrics.revenue_generated if self.metrics.revenue_generated > 0 else 0.0
        
        return (self.metrics.revenue_generated - self.metrics.cost_tokens) / self.metrics.cost_tokens


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
