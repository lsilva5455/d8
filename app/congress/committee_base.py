"""
Committee Base Class
Foundation for all specialized committees in the Congress system
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
import logging

from app.congress.voting_system import VotingSystem, VoteType, VoteChoice
from app.congress.proposal_system import ProposalSystem, ProposalCategory
from app.congress.session_manager import SessionManager, SessionType

logger = logging.getLogger(__name__)


class CommitteeRole(Enum):
    """Roles within a committee"""
    CHAIR = "chair"
    VICE_CHAIR = "vice_chair"
    MEMBER = "member"
    OBSERVER = "observer"


@dataclass
class CommitteeMember:
    """Represents a member of a committee"""
    agent_id: str
    name: str
    role: CommitteeRole
    expertise_areas: List[str] = field(default_factory=list)
    reputation: float = 0.0  # 0-100
    joined_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    contributions: int = 0
    votes_cast: int = 0


@dataclass
class CommitteeReport:
    """Report produced by a committee"""
    report_id: str
    committee_name: str
    title: str
    summary: str
    findings: List[str]
    recommendations: List[str]
    proposed_actions: List[str]
    confidence_level: float  # 0-1
    created_by: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class CommitteeBase(ABC):
    """
    Abstract base class for all committees
    
    All committees inherit from this and implement:
    - analyze(): Analyze a topic/situation
    - debate(): Conduct internal debate
    - decide(): Make a decision
    - report(): Generate a report
    """
    
    def __init__(
        self,
        committee_name: str,
        description: str,
        voting_system: Optional[VotingSystem] = None,
        proposal_system: Optional[ProposalSystem] = None,
        session_manager: Optional[SessionManager] = None
    ):
        self.committee_name = committee_name
        self.description = description
        self.members: Dict[str, CommitteeMember] = {}
        self.reports: List[CommitteeReport] = []
        
        # Shared systems
        self.voting_system = voting_system or VotingSystem()
        self.proposal_system = proposal_system or ProposalSystem()
        self.session_manager = session_manager or SessionManager()
        
        logger.info(f"🏛️ Committee initialized: {committee_name}")
    
    def add_member(
        self,
        agent_id: str,
        name: str,
        role: CommitteeRole = CommitteeRole.MEMBER,
        expertise_areas: Optional[List[str]] = None
    ) -> CommitteeMember:
        """
        Add a member to the committee
        
        Args:
            agent_id: ID of the agent
            name: Name/role of the agent
            role: Committee role
            expertise_areas: Areas of expertise
            
        Returns:
            CommitteeMember object
        """
        if agent_id in self.members:
            logger.warning(f"⚠️ {agent_id} already member of {self.committee_name}")
            return self.members[agent_id]
        
        member = CommitteeMember(
            agent_id=agent_id,
            name=name,
            role=role,
            expertise_areas=expertise_areas or []
        )
        
        self.members[agent_id] = member
        
        logger.info(
            f"👤 Added {name} ({role.value}) to {self.committee_name}"
        )
        
        return member
    
    def remove_member(self, agent_id: str) -> None:
        """Remove a member from the committee"""
        if agent_id in self.members:
            member = self.members[agent_id]
            del self.members[agent_id]
            logger.info(f"👋 Removed {member.name} from {self.committee_name}")
        else:
            logger.warning(f"⚠️ {agent_id} not found in {self.committee_name}")
    
    def get_chair(self) -> Optional[CommitteeMember]:
        """Get the committee chair"""
        for member in self.members.values():
            if member.role == CommitteeRole.CHAIR:
                return member
        return None
    
    def get_members_by_role(self, role: CommitteeRole) -> List[CommitteeMember]:
        """Get all members with a specific role"""
        return [m for m in self.members.values() if m.role == role]
    
    @abstractmethod
    def analyze(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a topic or situation (must be implemented by subclass)
        
        Each member analyzes independently, then results are aggregated
        
        Args:
            topic: Information about what to analyze
            
        Returns:
            Analysis results
        """
        pass
    
    @abstractmethod
    def debate(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Conduct internal debate on analysis (must be implemented by subclass)
        
        Members discuss findings and reach consensus
        
        Args:
            analysis: Results from analyze()
            
        Returns:
            Debate outcomes and refined analysis
        """
        pass
    
    def vote(
        self,
        proposal_id: str,
        vote_type: VoteType = VoteType.SIMPLE_MAJORITY
    ) -> Dict[str, Any]:
        """
        Vote on a proposal
        
        Args:
            proposal_id: ID of proposal to vote on
            vote_type: Type of majority required
            
        Returns:
            Voting results
        """
        # Start vote
        self.voting_system.start_vote(proposal_id)
        
        # Each member votes (in practice, this would be done by agents)
        # For now, simulate automatic voting based on member count
        logger.info(
            f"🗳️ {self.committee_name} voting on {proposal_id} "
            f"({len(self.members)} members)"
        )
        
        # Tally and return results
        result = self.voting_system.tally_votes(
            proposal_id=proposal_id,
            vote_type=vote_type,
            total_eligible_voters=len(self.members)
        )
        
        return {
            "proposal_id": proposal_id,
            "committee": self.committee_name,
            "passed": result.passed,
            "votes_for": result.yes_count,
            "votes_against": result.no_count,
            "percentage": result.yes_percentage
        }
    
    def create_proposal(
        self,
        title: str,
        description: str,
        category: ProposalCategory,
        expected_roi: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Create a proposal to submit to council
        
        Args:
            title: Proposal title
            description: Detailed description
            category: Category of proposal
            expected_roi: Expected ROI
            **kwargs: Additional arguments for proposal
            
        Returns:
            Proposal ID
        """
        proposal = self.proposal_system.create_proposal(
            title=title,
            description=description,
            category=category,
            proposed_by=self.committee_name,
            expected_roi=expected_roi,
            **kwargs
        )
        
        logger.info(
            f"📝 {self.committee_name} created proposal: {proposal.proposal_id}"
        )
        
        return proposal.proposal_id
    
    def schedule_session(
        self,
        title: str,
        description: str,
        duration_minutes: int = 60,
        agenda_items: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Schedule a committee session
        
        Args:
            title: Session title
            description: Session description
            duration_minutes: Duration in minutes
            agenda_items: List of agenda items
            
        Returns:
            Session ID
        """
        participant_ids = list(self.members.keys())
        
        session = self.session_manager.schedule_session(
            session_type=SessionType.COMMITTEE_MEETING,
            title=title,
            description=description,
            organizer=self.committee_name,
            participants=participant_ids,
            duration_minutes=duration_minutes,
            agenda_items=agenda_items
        )
        
        logger.info(
            f"📅 {self.committee_name} scheduled session: {session.session_id}"
        )
        
        return session.session_id
    
    def generate_report(
        self,
        report_id: str,
        title: str,
        summary: str,
        findings: List[str],
        recommendations: List[str],
        proposed_actions: List[str],
        confidence_level: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CommitteeReport:
        """
        Generate a committee report
        
        Args:
            report_id: Unique report ID
            title: Report title
            summary: Executive summary
            findings: Key findings
            recommendations: Recommendations
            proposed_actions: Proposed actions
            confidence_level: Confidence in findings (0-1)
            metadata: Additional metadata
            
        Returns:
            CommitteeReport object
        """
        chair = self.get_chair()
        created_by = chair.name if chair else self.committee_name
        
        report = CommitteeReport(
            report_id=report_id,
            committee_name=self.committee_name,
            title=title,
            summary=summary,
            findings=findings,
            recommendations=recommendations,
            proposed_actions=proposed_actions,
            confidence_level=confidence_level,
            created_by=created_by,
            metadata=metadata or {}
        )
        
        self.reports.append(report)
        
        logger.info(
            f"📄 {self.committee_name} generated report: {report_id}"
        )
        
        return report
    
    def get_committee_info(self) -> Dict[str, Any]:
        """Get information about the committee"""
        chair = self.get_chair()
        
        return {
            "name": self.committee_name,
            "description": self.description,
            "total_members": len(self.members),
            "chair": chair.name if chair else None,
            "total_reports": len(self.reports),
            "members": [
                {
                    "name": m.name,
                    "role": m.role.value,
                    "expertise": m.expertise_areas,
                    "reputation": m.reputation,
                    "contributions": m.contributions
                }
                for m in self.members.values()
            ]
        }


# Example concrete implementation
class ExampleCommittee(CommitteeBase):
    """Example committee implementation"""
    
    def analyze(self, topic: Dict[str, Any]) -> Dict[str, Any]:
        """Example analysis implementation"""
        logger.info(f"🔍 {self.committee_name} analyzing: {topic.get('title', 'Unknown')}")
        
        # In practice, each member (agent) would analyze independently
        # and results would be aggregated
        
        return {
            "topic": topic,
            "committee": self.committee_name,
            "analyzed_by": [m.name for m in self.members.values()],
            "findings": ["Example finding 1", "Example finding 2"],
            "confidence": 0.85
        }
    
    def debate(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Example debate implementation"""
        logger.info(f"💬 {self.committee_name} debating analysis")
        
        # In practice, members would discuss via prompts
        # and reach consensus
        
        return {
            "analysis": analysis,
            "consensus": "Example consensus reached",
            "dissenting_opinions": [],
            "next_steps": ["Action 1", "Action 2"]
        }


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create example committee
    committee = ExampleCommittee(
        committee_name="Example Committee",
        description="A test committee for demonstration"
    )
    
    # Add members
    committee.add_member(
        agent_id="agent-1",
        name="Expert Analyst",
        role=CommitteeRole.CHAIR,
        expertise_areas=["market analysis", "trends"]
    )
    
    committee.add_member(
        agent_id="agent-2",
        name="Data Scientist",
        role=CommitteeRole.MEMBER,
        expertise_areas=["data analysis", "statistics"]
    )
    
    # Analyze something
    analysis = committee.analyze({
        "title": "New Market Opportunity",
        "data": {"search_volume": 50000}
    })
    
    # Debate
    debate = committee.debate(analysis)
    
    # Create proposal
    proposal_id = committee.create_proposal(
        title="Explore New Market",
        description="Based on analysis, we should explore this market",
        category=ProposalCategory.NICHE_DISCOVERY,
        expected_roi=200.0
    )
    
    # Get committee info
    info = committee.get_committee_info()
    print(f"\n🏛️ Committee: {info['name']}")
    print(f"👥 Members: {info['total_members']}")
    print(f"📝 Proposal created: {proposal_id}")
