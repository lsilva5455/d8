"""
Supreme Council
The governing body of The Hive - makes strategic decisions and allocates resources
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import uuid

from app.congress.committee_base import CommitteeBase, CommitteeRole, CommitteeReport
from app.congress.voting_system import VotingSystem, VoteType, VoteChoice
from app.congress.proposal_system import ProposalSystem, ProposalStatus
from app.congress.session_manager import SessionManager, SessionType

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of decisions the council makes"""
    STRATEGIC_DIRECTION = "strategic_direction"
    RESOURCE_ALLOCATION = "resource_allocation"
    NICHE_APPROVAL = "niche_approval"
    TECHNOLOGY_ADOPTION = "technology_adoption"
    POLICY_CHANGE = "policy_change"
    EMERGENCY = "emergency"


@dataclass
class OKR:
    """Objectives and Key Results"""
    okr_id: str
    quarter: str  # e.g., "Q1-2024"
    objective: str
    key_results: List[Dict[str, Any]]
    owner: str
    status: str = "active"  # active, completed, cancelled
    progress: float = 0.0  # 0-100
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    due_date: Optional[str] = None


@dataclass
class Decision:
    """Record of a council decision"""
    decision_id: str
    decision_type: DecisionType
    title: str
    description: str
    rationale: str
    proposal_id: Optional[str] = None
    votes_for: int = 0
    votes_against: int = 0
    passed: bool = False
    implementation_plan: Optional[str] = None
    decided_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    implemented_at: Optional[str] = None


@dataclass
class ResourceAllocation:
    """Resource allocation decision"""
    allocation_id: str
    target: str  # Committee or agent
    resource_type: str  # compute, budget, agents
    amount: float
    duration_days: int
    justification: str
    allocated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None


class SupremeCouncil:
    """
    Supreme Council - Governing body of The Hive
    
    Responsibilities:
    - Quarterly strategic planning
    - Weekly decision-making sessions
    - OKR definition and tracking
    - Resource allocation
    - Proposal approval/rejection
    - Emergency decisions
    
    Size: 5-7 senior agents with diverse expertise
    """
    
    def __init__(
        self,
        council_size: int = 7,
        voting_threshold: float = 0.66,  # Supermajority
        voting_system: Optional[VotingSystem] = None,
        proposal_system: Optional[ProposalSystem] = None,
        session_manager: Optional[SessionManager] = None
    ):
        self.council_size = council_size
        self.voting_threshold = voting_threshold
        
        # Shared systems
        self.voting_system = voting_system or VotingSystem()
        self.proposal_system = proposal_system or ProposalSystem()
        self.session_manager = session_manager or SessionManager()
        
        # Council state
        self.council_members: Dict[str, Dict[str, Any]] = {}
        self.decisions: List[Decision] = []
        self.okrs: List[OKR] = []
        self.allocations: List[ResourceAllocation] = []
        
        logger.info(f"🏛️ Supreme Council initialized (size: {council_size}, threshold: {voting_threshold:.0%})")
    
    def add_council_member(
        self,
        agent_id: str,
        name: str,
        expertise: List[str],
        seniority: int = 5
    ) -> None:
        """
        Add a member to the Supreme Council
        
        Args:
            agent_id: Agent ID
            name: Member name/title
            expertise: Areas of expertise
            seniority: Years of experience/seniority level
        """
        if len(self.council_members) >= self.council_size:
            raise ValueError(f"Council is full ({self.council_size} members)")
        
        member = {
            "agent_id": agent_id,
            "name": name,
            "expertise": expertise,
            "seniority": seniority,
            "joined_at": datetime.utcnow().isoformat(),
            "decisions_participated": 0,
            "proposals_sponsored": 0
        }
        
        self.council_members[agent_id] = member
        
        logger.info(f"👤 Added council member: {name} (expertise: {', '.join(expertise)})")
    
    def remove_council_member(self, agent_id: str) -> None:
        """Remove a member from the council"""
        if agent_id in self.council_members:
            member = self.council_members[agent_id]
            del self.council_members[agent_id]
            logger.info(f"👋 Removed council member: {member['name']}")
    
    def schedule_strategic_planning(
        self,
        quarter: str,
        scheduled_time: Optional[datetime] = None
    ) -> str:
        """
        Schedule quarterly strategic planning session
        
        Args:
            quarter: Quarter identifier (e.g., "Q1-2024")
            scheduled_time: When to hold session
            
        Returns:
            Session ID
        """
        logger.info(f"📅 Scheduling strategic planning for {quarter}")
        
        participants = list(self.council_members.keys())
        
        session = self.session_manager.schedule_session(
            session_type=SessionType.STRATEGIC_PLANNING,
            title=f"{quarter} Strategic Planning",
            description=f"Quarterly strategic planning session for {quarter}",
            organizer="supreme-council",
            participants=participants,
            scheduled_time=scheduled_time or datetime.utcnow() + timedelta(days=1),
            duration_minutes=240,  # 4 hours
            agenda_items=[
                {"title": "Review previous quarter", "duration_minutes": 60},
                {"title": "Set OKRs for quarter", "duration_minutes": 90},
                {"title": "Resource allocation planning", "duration_minutes": 60},
                {"title": "Strategic initiatives", "duration_minutes": 30}
            ]
        )
        
        logger.info(f"✅ Strategic planning scheduled: {session.session_id}")
        
        return session.session_id
    
    def schedule_weekly_session(
        self,
        scheduled_time: Optional[datetime] = None
    ) -> str:
        """
        Schedule weekly decision-making session
        
        Args:
            scheduled_time: When to hold session
            
        Returns:
            Session ID
        """
        participants = list(self.council_members.keys())
        
        session = self.session_manager.schedule_session(
            session_type=SessionType.COUNCIL_SESSION,
            title="Weekly Council Session",
            description="Regular weekly session for decisions and updates",
            organizer="supreme-council",
            participants=participants,
            scheduled_time=scheduled_time or datetime.utcnow() + timedelta(days=7),
            duration_minutes=120,
            agenda_items=[
                {"title": "Committee reports", "duration_minutes": 40},
                {"title": "Proposal review and voting", "duration_minutes": 50},
                {"title": "Resource allocation requests", "duration_minutes": 20},
                {"title": "Open discussion", "duration_minutes": 10}
            ]
        )
        
        logger.info(f"📅 Weekly session scheduled: {session.session_id}")
        
        return session.session_id
    
    def review_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """
        Review a proposal from a committee
        
        Args:
            proposal_id: ID of proposal to review
            
        Returns:
            Review summary
        """
        proposal = self.proposal_system.get_proposal(proposal_id)
        
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        logger.info(f"🔍 Council reviewing proposal: {proposal.title}")
        
        # Move to voting if not already
        if proposal.status == ProposalStatus.UNDER_REVIEW:
            self.proposal_system.move_to_voting(proposal_id)
        
        # Analyze proposal
        review = {
            "proposal_id": proposal_id,
            "title": proposal.title,
            "category": proposal.category.value,
            "proposed_by": proposal.proposed_by,
            "expected_roi": proposal.expected_roi,
            "estimated_cost": proposal.estimated_cost,
            "priority": proposal.priority,
            "council_analysis": {
                "strategic_alignment": self._assess_strategic_alignment(proposal),
                "resource_feasibility": self._assess_resource_feasibility(proposal),
                "risk_assessment": self._assess_risks(proposal),
                "recommendation": "approve"  # Simplified - in production, use agent analysis
            }
        }
        
        logger.info(f"✅ Proposal reviewed: {review['council_analysis']['recommendation']}")
        
        return review
    
    def vote_on_proposal(
        self,
        proposal_id: str,
        member_votes: Optional[Dict[str, VoteChoice]] = None
    ) -> Decision:
        """
        Council votes on a proposal
        
        Args:
            proposal_id: ID of proposal
            member_votes: Dictionary of agent_id -> vote choice (for testing)
            
        Returns:
            Decision object
        """
        proposal = self.proposal_system.get_proposal(proposal_id)
        
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        logger.info(f"🗳️ Council voting on: {proposal.title}")
        
        # Start vote
        self.voting_system.start_vote(proposal_id)
        
        # Cast votes (in production, each agent would vote independently)
        if member_votes:
            for agent_id, choice in member_votes.items():
                if agent_id in self.council_members:
                    member = self.council_members[agent_id]
                    self.voting_system.cast_vote(
                        proposal_id=proposal_id,
                        voter_id=agent_id,
                        voter_name=member["name"],
                        choice=choice,
                        reasoning=f"Vote from {member['name']}"
                    )
        
        # Tally votes
        result = self.voting_system.tally_votes(
            proposal_id=proposal_id,
            vote_type=VoteType.SUPERMAJORITY,
            total_eligible_voters=len(self.council_members)
        )
        
        # Create decision record
        decision = Decision(
            decision_id=f"DEC-{uuid.uuid4().hex[:8].upper()}",
            decision_type=DecisionType.NICHE_APPROVAL if "niche" in proposal.category.value else DecisionType.STRATEGIC_DIRECTION,
            title=f"Decision on: {proposal.title}",
            description=proposal.description,
            rationale=f"Voted with {result.yes_percentage:.1f}% approval",
            proposal_id=proposal_id,
            votes_for=result.yes_count,
            votes_against=result.no_count,
            passed=result.passed
        )
        
        self.decisions.append(decision)
        
        # Update proposal status
        if result.passed:
            self.proposal_system.approve_proposal(
                proposal_id=proposal_id,
                votes_for=result.yes_count,
                votes_against=result.no_count
            )
            logger.info(f"✅ Proposal APPROVED: {proposal.title}")
        else:
            self.proposal_system.reject_proposal(
                proposal_id=proposal_id,
                votes_for=result.yes_count,
                votes_against=result.no_count,
                reason="Failed to achieve supermajority"
            )
            logger.info(f"❌ Proposal REJECTED: {proposal.title}")
        
        # Update member stats
        for agent_id in self.council_members:
            self.council_members[agent_id]["decisions_participated"] += 1
        
        return decision
    
    def create_okr(
        self,
        quarter: str,
        objective: str,
        key_results: List[Dict[str, Any]],
        owner: str,
        due_date: Optional[str] = None
    ) -> OKR:
        """
        Create a new OKR for the quarter
        
        Args:
            quarter: Quarter (e.g., "Q1-2024")
            objective: High-level objective
            key_results: List of measurable key results
            owner: Who owns this OKR
            due_date: When it should be completed
            
        Returns:
            OKR object
        """
        okr = OKR(
            okr_id=f"OKR-{uuid.uuid4().hex[:8].upper()}",
            quarter=quarter,
            objective=objective,
            key_results=key_results,
            owner=owner,
            due_date=due_date
        )
        
        self.okrs.append(okr)
        
        logger.info(f"🎯 OKR created for {quarter}: {objective}")
        
        return okr
    
    def allocate_resources(
        self,
        target: str,
        resource_type: str,
        amount: float,
        duration_days: int,
        justification: str
    ) -> ResourceAllocation:
        """
        Allocate resources to a committee or initiative
        
        Args:
            target: Committee or agent to receive resources
            resource_type: Type of resource (compute, budget, agents)
            amount: Amount to allocate
            duration_days: How long allocation lasts
            justification: Why these resources are needed
            
        Returns:
            ResourceAllocation object
        """
        expires_at = datetime.utcnow() + timedelta(days=duration_days)
        
        allocation = ResourceAllocation(
            allocation_id=f"ALLOC-{uuid.uuid4().hex[:8].upper()}",
            target=target,
            resource_type=resource_type,
            amount=amount,
            duration_days=duration_days,
            justification=justification,
            expires_at=expires_at.isoformat()
        )
        
        self.allocations.append(allocation)
        
        logger.info(
            f"💰 Resources allocated to {target}: {amount} {resource_type} "
            f"for {duration_days} days"
        )
        
        return allocation
    
    def _assess_strategic_alignment(self, proposal: Any) -> str:
        """Assess if proposal aligns with strategy"""
        # Simplified - in production, use agent analysis
        return "high" if proposal.priority <= 2 else "medium" if proposal.priority <= 3 else "low"
    
    def _assess_resource_feasibility(self, proposal: Any) -> str:
        """Assess if we have resources for proposal"""
        # Simplified
        return "feasible" if proposal.estimated_cost else "needs_assessment"
    
    def _assess_risks(self, proposal: Any) -> List[str]:
        """Identify risks in proposal"""
        # Simplified
        risks = []
        if proposal.expected_roi and proposal.expected_roi < 100:
            risks.append("Low ROI projection")
        if proposal.dependencies:
            risks.append(f"Has {len(proposal.dependencies)} dependencies")
        return risks
    
    def get_council_stats(self) -> Dict[str, Any]:
        """Get statistics about council activity"""
        total_decisions = len(self.decisions)
        approved = sum(1 for d in self.decisions if d.passed)
        
        return {
            "members": len(self.council_members),
            "total_decisions": total_decisions,
            "approved": approved,
            "rejected": total_decisions - approved,
            "approval_rate": approved / total_decisions * 100 if total_decisions > 0 else 0,
            "active_okrs": len([okr for okr in self.okrs if okr.status == "active"]),
            "resource_allocations": len(self.allocations)
        }
    
    def get_recent_decisions(self, limit: int = 10) -> List[Decision]:
        """Get recent decisions"""
        return sorted(
            self.decisions,
            key=lambda d: d.decided_at,
            reverse=True
        )[:limit]


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Supreme Council
    council = SupremeCouncil(council_size=5)
    
    # Add council members
    council.add_council_member(
        agent_id="council-1",
        name="Strategic Director",
        expertise=["strategy", "business development"],
        seniority=10
    )
    
    council.add_council_member(
        agent_id="council-2",
        name="Tech Leader",
        expertise=["technology", "innovation"],
        seniority=8
    )
    
    council.add_council_member(
        agent_id="council-3",
        name="Operations Chief",
        expertise=["operations", "efficiency"],
        seniority=7
    )
    
    # Create OKR
    okr = council.create_okr(
        quarter="Q1-2024",
        objective="Discover and validate 50 profitable niches",
        key_results=[
            {"kr": "Validate 50 niches with >60% confidence", "target": 50, "current": 0},
            {"kr": "Generate $10,000 revenue from top 10 niches", "target": 10000, "current": 0}
        ],
        owner="niche-discovery-committee"
    )
    
    print(f"\n🎯 OKR Created: {okr.objective}")
    
    # Allocate resources
    allocation = council.allocate_resources(
        target="niche-discovery-committee",
        resource_type="compute_hours",
        amount=1000,
        duration_days=30,
        justification="Need compute for 24/7 discovery engine"
    )
    
    print(f"💰 Allocated: {allocation.amount} {allocation.resource_type}")
    
    # Get stats
    stats = council.get_council_stats()
    print(f"\n📊 Council Stats:")
    print(f"   Members: {stats['members']}")
    print(f"   Active OKRs: {stats['active_okrs']}")
    print(f"   Decisions: {stats['total_decisions']}")
