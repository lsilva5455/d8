"""
Congress Agent
Extended BaseAgent with political capabilities for Congress system
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

from app.agents.base_agent import BaseAgent, AgentMetrics
from app.evolution.darwin import Genome
from app.congress.voting_system import VoteChoice

logger = logging.getLogger(__name__)


@dataclass
class CongressProfile:
    """Political profile for a Congress Agent"""
    expertise_areas: List[str] = field(default_factory=list)
    skill_levels: Dict[str, float] = field(default_factory=dict)  # skill -> level (0-100)
    reputation: float = 50.0  # 0-100
    committee_memberships: List[str] = field(default_factory=list)
    proposals_created: int = 0
    votes_cast: int = 0
    debates_participated: int = 0
    reports_authored: int = 0


class CongressAgent(BaseAgent):
    """
    Enhanced Agent with Congress capabilities
    
    Extends BaseAgent with:
    - Political capabilities (voting, proposing)
    - Expertise areas and skill levels
    - Reputation system
    - Committee membership
    - Debate and analysis functions
    """
    
    def __init__(
        self,
        genome: Genome,
        groq_api_key: str,
        agent_id: Optional[str] = None,
        model: str = "mixtral-8x7b-32768",
        expertise_areas: Optional[List[str]] = None,
        initial_reputation: float = 50.0
    ):
        # Initialize base agent
        super().__init__(genome, groq_api_key, agent_id, model)
        
        # Initialize Congress profile
        self.congress_profile = CongressProfile(
            expertise_areas=expertise_areas or [],
            reputation=initial_reputation
        )
        
        logger.info(
            f"🏛️ Congress Agent {self.agent_id[:8]} initialized "
            f"(expertise: {', '.join(expertise_areas or ['general'])})"
        )
    
    def analyze_topic(
        self,
        topic: str,
        context: Dict[str, Any],
        focus_area: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a topic from agent's expertise perspective
        
        Args:
            topic: Topic to analyze
            context: Contextual information
            focus_area: Specific area to focus on
            
        Returns:
            Analysis results with insights and recommendations
        """
        logger.info(
            f"🔍 Agent {self.agent_id[:8]} analyzing: {topic}"
        )
        
        # Build analysis prompt
        input_data = {
            "task": "analyze_topic",
            "topic": topic,
            "context": context,
            "focus_area": focus_area,
            "your_expertise": self.congress_profile.expertise_areas,
            "instructions": (
                "Provide a thorough analysis from your area of expertise. "
                "Include key insights, potential risks, opportunities, and recommendations."
            )
        }
        
        # Use base agent's act method for LLM interaction
        result = self.act(input_data, action_type="analyze_topic")
        
        # Update profile
        self.congress_profile.debates_participated += 1
        
        return result
    
    def respond_to_debate(
        self,
        debate_context: Dict[str, Any],
        other_viewpoints: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Respond to other members' viewpoints in a debate
        
        Args:
            debate_context: Context of the debate
            other_viewpoints: List of other members' positions
            
        Returns:
            Agent's response with position and reasoning
        """
        logger.info(
            f"💬 Agent {self.agent_id[:8]} responding to debate"
        )
        
        input_data = {
            "task": "debate_response",
            "context": debate_context,
            "other_viewpoints": other_viewpoints,
            "your_expertise": self.congress_profile.expertise_areas,
            "instructions": (
                "Review the other viewpoints and provide your perspective. "
                "Build on good points, respectfully challenge weak arguments, "
                "and contribute unique insights from your expertise."
            )
        }
        
        result = self.act(input_data, action_type="debate_response")
        
        # Update profile
        self.congress_profile.debates_participated += 1
        
        return result
    
    def vote_on_proposal(
        self,
        proposal: Dict[str, Any],
        committee_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Vote on a proposal with reasoning
        
        Args:
            proposal: Proposal to vote on
            committee_context: Additional context from committee
            
        Returns:
            Vote choice and detailed reasoning
        """
        logger.info(
            f"🗳️ Agent {self.agent_id[:8]} voting on proposal: {proposal.get('proposal_id', 'unknown')}"
        )
        
        input_data = {
            "task": "vote_on_proposal",
            "proposal": proposal,
            "committee_context": committee_context,
            "your_expertise": self.congress_profile.expertise_areas,
            "your_reputation": self.congress_profile.reputation,
            "instructions": (
                "Carefully evaluate this proposal based on:\n"
                "1. Alignment with strategic goals\n"
                "2. Expected ROI and feasibility\n"
                "3. Risks and dependencies\n"
                "4. Your expertise assessment\n\n"
                "Decide: YES (support), NO (oppose), or ABSTAIN (neutral)\n"
                "Provide clear reasoning for your decision."
            )
        }
        
        result = self.act(input_data, action_type="vote_on_proposal")
        
        # Update profile
        self.congress_profile.votes_cast += 1
        
        # Parse vote choice from result
        vote_str = result.get("action", "ABSTAIN").upper()
        if "YES" in vote_str or "APPROVE" in vote_str:
            vote_choice = VoteChoice.YES
        elif "NO" in vote_str or "REJECT" in vote_str:
            vote_choice = VoteChoice.NO
        else:
            vote_choice = VoteChoice.ABSTAIN
        
        return {
            "vote": vote_choice,
            "reasoning": result.get("reasoning", ""),
            "confidence": result.get("confidence", 0.5),
            "voter_id": self.agent_id,
            "expertise": self.congress_profile.expertise_areas
        }
    
    def propose_action(
        self,
        situation: Dict[str, Any],
        goal: str
    ) -> Dict[str, Any]:
        """
        Propose an action or solution
        
        Args:
            situation: Current situation analysis
            goal: Desired goal or outcome
            
        Returns:
            Proposal with action plan and expected outcomes
        """
        logger.info(
            f"💡 Agent {self.agent_id[:8]} proposing action for: {goal}"
        )
        
        input_data = {
            "task": "propose_action",
            "situation": situation,
            "goal": goal,
            "your_expertise": self.congress_profile.expertise_areas,
            "instructions": (
                "Based on the situation and goal, propose a specific action plan. "
                "Include: concrete steps, resource requirements, timeline, "
                "expected outcomes, and success metrics."
            )
        }
        
        result = self.act(input_data, action_type="propose_action")
        
        # Update profile
        self.congress_profile.proposals_created += 1
        
        return result
    
    def evaluate_niche(
        self,
        niche_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a niche opportunity (specialized for niche discovery)
        
        Args:
            niche_data: Data about the niche
            
        Returns:
            Evaluation with score and reasoning
        """
        logger.info(
            f"📊 Agent {self.agent_id[:8]} evaluating niche: {niche_data.get('name', 'unknown')}"
        )
        
        input_data = {
            "task": "evaluate_niche",
            "niche_data": niche_data,
            "your_expertise": self.congress_profile.expertise_areas,
            "instructions": (
                "Evaluate this niche opportunity from your expertise perspective. "
                "Consider: market size, competition, monetization potential, "
                "trends, risks, and entry barriers. "
                "Provide a score (0-100) and detailed reasoning."
            )
        }
        
        result = self.act(input_data, action_type="evaluate_niche")
        
        return result
    
    def join_committee(self, committee_name: str) -> None:
        """Join a committee"""
        if committee_name not in self.congress_profile.committee_memberships:
            self.congress_profile.committee_memberships.append(committee_name)
            logger.info(
                f"👤 Agent {self.agent_id[:8]} joined {committee_name}"
            )
    
    def leave_committee(self, committee_name: str) -> None:
        """Leave a committee"""
        if committee_name in self.congress_profile.committee_memberships:
            self.congress_profile.committee_memberships.remove(committee_name)
            logger.info(
                f"👋 Agent {self.agent_id[:8]} left {committee_name}"
            )
    
    def add_expertise(self, area: str, skill_level: float = 50.0) -> None:
        """
        Add an expertise area
        
        Args:
            area: Expertise area (e.g., "market analysis")
            skill_level: Initial skill level (0-100)
        """
        if area not in self.congress_profile.expertise_areas:
            self.congress_profile.expertise_areas.append(area)
        
        self.congress_profile.skill_levels[area] = skill_level
        
        logger.info(
            f"🎓 Agent {self.agent_id[:8]} added expertise: {area} (level {skill_level})"
        )
    
    def update_reputation(self, delta: float) -> None:
        """
        Update agent's reputation
        
        Args:
            delta: Change in reputation (can be positive or negative)
        """
        old_rep = self.congress_profile.reputation
        self.congress_profile.reputation = max(0, min(100, old_rep + delta))
        
        logger.info(
            f"⭐ Agent {self.agent_id[:8]} reputation: "
            f"{old_rep:.1f} -> {self.congress_profile.reputation:.1f}"
        )
    
    def get_congress_status(self) -> Dict[str, Any]:
        """Get Congress-specific status"""
        base_status = self.get_status()
        
        return {
            **base_status,
            "congress_profile": {
                "expertise_areas": self.congress_profile.expertise_areas,
                "skill_levels": self.congress_profile.skill_levels,
                "reputation": self.congress_profile.reputation,
                "committees": self.congress_profile.committee_memberships,
                "proposals_created": self.congress_profile.proposals_created,
                "votes_cast": self.congress_profile.votes_cast,
                "debates_participated": self.congress_profile.debates_participated,
                "reports_authored": self.congress_profile.reports_authored
            }
        }


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create a test genome
    test_genome = Genome(
        prompt="""You are a specialized AI agent focused on market analysis.
Your expertise includes identifying market trends, evaluating competition,
and assessing monetization opportunities. You provide data-driven insights
and strategic recommendations."""
    )
    
    # Initialize Congress Agent (replace with real API key)
    agent = CongressAgent(
        genome=test_genome,
        groq_api_key="your_groq_api_key_here",
        expertise_areas=["market analysis", "trend prediction", "competition assessment"]
    )
    
    # Add to committee
    agent.join_committee("Niche Discovery Committee")
    
    # Analyze a topic
    analysis = agent.analyze_topic(
        topic="AI Tools Market",
        context={
            "search_volume": 50000,
            "competition_level": "medium",
            "growth_rate": "15%"
        },
        focus_area="market opportunity"
    )
    
    print("\n🔍 Analysis Result:")
    print(f"   Confidence: {analysis.get('confidence', 0)}")
    
    # Get status
    status = agent.get_congress_status()
    print(f"\n📊 Agent Status:")
    print(f"   Expertise: {', '.join(status['congress_profile']['expertise_areas'])}")
    print(f"   Reputation: {status['congress_profile']['reputation']}")
    print(f"   Committees: {', '.join(status['congress_profile']['committees'])}")
