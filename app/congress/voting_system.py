"""
Voting System for Congress
Implements different voting mechanisms and thresholds
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class VoteType(Enum):
    """Types of votes"""
    SIMPLE_MAJORITY = "simple_majority"  # 51%
    SUPERMAJORITY = "supermajority"       # 66%
    QUALIFIED_MAJORITY = "qualified_majority"  # 75%
    UNANIMOUS = "unanimous"               # 100%


class VoteChoice(Enum):
    """Vote choices"""
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"


@dataclass
class Vote:
    """Represents a single vote"""
    voter_id: str
    voter_name: str
    choice: VoteChoice
    reasoning: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    weight: float = 1.0  # For weighted voting (e.g., by expertise)


@dataclass
class VotingResult:
    """Result of a voting session"""
    proposal_id: str
    vote_type: VoteType
    votes: List[Vote]
    passed: bool
    yes_count: int
    no_count: int
    abstain_count: int
    yes_percentage: float
    total_eligible_voters: int
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class VotingSystem:
    """
    Manages voting sessions for proposals
    
    Supports different voting thresholds:
    - Simple Majority: >50%
    - Supermajority: >=66%
    - Qualified Majority: >=75%
    - Unanimous: 100%
    """
    
    def __init__(self):
        self.active_votes: Dict[str, List[Vote]] = {}
        self.vote_results: List[VotingResult] = []
        logger.info("🗳️ Voting System initialized")
    
    def start_vote(self, proposal_id: str) -> None:
        """Start a new voting session"""
        if proposal_id in self.active_votes:
            raise ValueError(f"Vote already in progress for proposal {proposal_id}")
        
        self.active_votes[proposal_id] = []
        logger.info(f"🗳️ Voting started for proposal: {proposal_id}")
    
    def cast_vote(
        self,
        proposal_id: str,
        voter_id: str,
        voter_name: str,
        choice: VoteChoice,
        reasoning: Optional[str] = None,
        weight: float = 1.0
    ) -> None:
        """
        Cast a vote on an active proposal
        
        Args:
            proposal_id: ID of the proposal
            voter_id: ID of the voter (agent)
            voter_name: Name/role of voter
            choice: YES, NO, or ABSTAIN
            reasoning: Optional explanation of vote
            weight: Vote weight (for expertise-based voting)
        """
        if proposal_id not in self.active_votes:
            raise ValueError(f"No active vote for proposal {proposal_id}")
        
        # Check if voter already voted
        existing_vote = next(
            (v for v in self.active_votes[proposal_id] if v.voter_id == voter_id),
            None
        )
        
        if existing_vote:
            logger.warning(f"⚠️ {voter_name} already voted on {proposal_id}, updating vote")
            self.active_votes[proposal_id].remove(existing_vote)
        
        vote = Vote(
            voter_id=voter_id,
            voter_name=voter_name,
            choice=choice,
            reasoning=reasoning,
            weight=weight
        )
        
        self.active_votes[proposal_id].append(vote)
        logger.info(f"✅ {voter_name} voted {choice.value} on {proposal_id}")
    
    def tally_votes(
        self,
        proposal_id: str,
        vote_type: VoteType,
        total_eligible_voters: int
    ) -> VotingResult:
        """
        Tally votes and determine if proposal passed
        
        Args:
            proposal_id: ID of the proposal
            vote_type: Type of majority required
            total_eligible_voters: Total number of eligible voters
            
        Returns:
            VotingResult with outcome
        """
        if proposal_id not in self.active_votes:
            raise ValueError(f"No active vote for proposal {proposal_id}")
        
        votes = self.active_votes[proposal_id]
        
        # Count votes (considering weights)
        yes_count = sum(v.weight for v in votes if v.choice == VoteChoice.YES)
        no_count = sum(v.weight for v in votes if v.choice == VoteChoice.NO)
        abstain_count = sum(v.weight for v in votes if v.choice == VoteChoice.ABSTAIN)
        
        total_votes = yes_count + no_count
        
        # Calculate percentage (excluding abstentions)
        yes_percentage = (yes_count / total_votes * 100) if total_votes > 0 else 0
        
        # Determine if passed based on vote type
        thresholds = {
            VoteType.SIMPLE_MAJORITY: 50,
            VoteType.SUPERMAJORITY: 66,
            VoteType.QUALIFIED_MAJORITY: 75,
            VoteType.UNANIMOUS: 100
        }
        
        required_threshold = thresholds[vote_type]
        passed = yes_percentage > required_threshold
        
        # Special case for unanimous - must be exactly 100%
        if vote_type == VoteType.UNANIMOUS:
            passed = yes_percentage == 100 and no_count == 0
        
        result = VotingResult(
            proposal_id=proposal_id,
            vote_type=vote_type,
            votes=votes,
            passed=passed,
            yes_count=int(yes_count),
            no_count=int(no_count),
            abstain_count=int(abstain_count),
            yes_percentage=yes_percentage,
            total_eligible_voters=total_eligible_voters
        )
        
        # Store result and clear active vote
        self.vote_results.append(result)
        del self.active_votes[proposal_id]
        
        logger.info(
            f"📊 Vote tallied for {proposal_id}: "
            f"{yes_percentage:.1f}% YES ({yes_count}/{total_votes}), "
            f"{'PASSED' if passed else 'FAILED'} ({vote_type.value})"
        )
        
        return result
    
    def get_vote_status(self, proposal_id: str) -> Dict[str, Any]:
        """Get current status of a vote"""
        if proposal_id not in self.active_votes:
            # Check completed votes
            result = next(
                (r for r in self.vote_results if r.proposal_id == proposal_id),
                None
            )
            if result:
                return {
                    "status": "completed",
                    "result": result
                }
            return {
                "status": "not_found",
                "message": f"No vote found for {proposal_id}"
            }
        
        votes = self.active_votes[proposal_id]
        yes_count = len([v for v in votes if v.choice == VoteChoice.YES])
        no_count = len([v for v in votes if v.choice == VoteChoice.NO])
        abstain_count = len([v for v in votes if v.choice == VoteChoice.ABSTAIN])
        
        return {
            "status": "in_progress",
            "votes_cast": len(votes),
            "yes": yes_count,
            "no": no_count,
            "abstain": abstain_count
        }
    
    def get_voting_history(self, limit: int = 10) -> List[VotingResult]:
        """Get recent voting results"""
        return self.vote_results[-limit:]


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize voting system
    voting = VotingSystem()
    
    # Start a vote
    proposal_id = "PROP-001"
    voting.start_vote(proposal_id)
    
    # Cast votes
    voting.cast_vote(proposal_id, "agent-1", "Market Analyst", VoteChoice.YES, "Strong market potential")
    voting.cast_vote(proposal_id, "agent-2", "Risk Analyst", VoteChoice.NO, "High competition risk")
    voting.cast_vote(proposal_id, "agent-3", "Trend Predictor", VoteChoice.YES, "Aligns with trends")
    
    # Tally votes
    result = voting.tally_votes(proposal_id, VoteType.SIMPLE_MAJORITY, total_eligible_voters=3)
    
    print(f"\n📊 Result: {'PASSED' if result.passed else 'FAILED'}")
    print(f"   YES: {result.yes_count}, NO: {result.no_count}")
    print(f"   Percentage: {result.yes_percentage:.1f}%")
