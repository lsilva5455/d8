"""
Proposal System for Congress
Manages proposal creation, submission, and tracking
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class ProposalStatus(Enum):
    """Status of a proposal"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    VOTING = "voting"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    ARCHIVED = "archived"


class ProposalCategory(Enum):
    """Categories of proposals"""
    NICHE_DISCOVERY = "niche_discovery"
    RESOURCE_ALLOCATION = "resource_allocation"
    TECHNOLOGY_ADOPTION = "technology_adoption"
    STRATEGIC_DIRECTION = "strategic_direction"
    PROCESS_IMPROVEMENT = "process_improvement"
    MONETIZATION = "monetization"
    OPERATIONAL = "operational"


@dataclass
class Proposal:
    """Represents a proposal in the Congress system"""
    proposal_id: str
    title: str
    description: str
    category: ProposalCategory
    proposed_by: str  # Agent ID or committee name
    status: ProposalStatus = ProposalStatus.DRAFT
    priority: int = 3  # 1=critical, 5=low
    expected_roi: Optional[float] = None
    estimated_cost: Optional[float] = None
    implementation_plan: Optional[str] = None
    success_metrics: Optional[Dict[str, Any]] = None
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    reviewed_by: List[str] = field(default_factory=list)
    votes_for: int = 0
    votes_against: int = 0
    approval_date: Optional[str] = None
    rejection_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProposalComment:
    """Comment/feedback on a proposal"""
    comment_id: str
    proposal_id: str
    author_id: str
    author_name: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    is_recommendation: bool = False


class ProposalSystem:
    """
    Manages the lifecycle of proposals
    
    Flow:
    1. Create proposal (draft)
    2. Submit for review
    3. Review by committee/council
    4. Vote on proposal
    5. Approve/Reject
    6. Implement
    """
    
    def __init__(self):
        self.proposals: Dict[str, Proposal] = {}
        self.comments: Dict[str, List[ProposalComment]] = {}
        logger.info("📋 Proposal System initialized")
    
    def create_proposal(
        self,
        title: str,
        description: str,
        category: ProposalCategory,
        proposed_by: str,
        priority: int = 3,
        expected_roi: Optional[float] = None,
        estimated_cost: Optional[float] = None,
        implementation_plan: Optional[str] = None,
        success_metrics: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Proposal:
        """
        Create a new proposal
        
        Args:
            title: Brief title of proposal
            description: Detailed description
            category: Category of proposal
            proposed_by: ID of proposer (agent or committee)
            priority: 1-5 (1=critical, 5=low)
            expected_roi: Expected return on investment
            estimated_cost: Estimated cost to implement
            implementation_plan: How to implement
            success_metrics: How to measure success
            tags: Optional tags for categorization
            metadata: Additional metadata
            
        Returns:
            Created Proposal object
        """
        proposal_id = f"PROP-{uuid.uuid4().hex[:8].upper()}"
        
        proposal = Proposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            category=category,
            proposed_by=proposed_by,
            priority=priority,
            expected_roi=expected_roi,
            estimated_cost=estimated_cost,
            implementation_plan=implementation_plan,
            success_metrics=success_metrics or {},
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self.proposals[proposal_id] = proposal
        self.comments[proposal_id] = []
        
        logger.info(
            f"📝 New proposal created: {proposal_id} - {title} "
            f"({category.value}) by {proposed_by}"
        )
        
        return proposal
    
    def submit_proposal(self, proposal_id: str) -> None:
        """Submit proposal for review"""
        proposal = self._get_proposal(proposal_id)
        
        if proposal.status != ProposalStatus.DRAFT:
            raise ValueError(f"Can only submit proposals in DRAFT status")
        
        proposal.status = ProposalStatus.SUBMITTED
        proposal.updated_at = datetime.utcnow().isoformat()
        
        logger.info(f"📤 Proposal {proposal_id} submitted for review")
    
    def start_review(self, proposal_id: str, reviewer_id: str) -> None:
        """Start reviewing a proposal"""
        proposal = self._get_proposal(proposal_id)
        
        if proposal.status != ProposalStatus.SUBMITTED:
            raise ValueError(f"Can only review SUBMITTED proposals")
        
        proposal.status = ProposalStatus.UNDER_REVIEW
        if reviewer_id not in proposal.reviewed_by:
            proposal.reviewed_by.append(reviewer_id)
        proposal.updated_at = datetime.utcnow().isoformat()
        
        logger.info(f"🔍 Review started for {proposal_id} by {reviewer_id}")
    
    def add_comment(
        self,
        proposal_id: str,
        author_id: str,
        author_name: str,
        content: str,
        is_recommendation: bool = False
    ) -> ProposalComment:
        """Add a comment/feedback to a proposal"""
        if proposal_id not in self.proposals:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        comment = ProposalComment(
            comment_id=f"COMMENT-{uuid.uuid4().hex[:8].upper()}",
            proposal_id=proposal_id,
            author_id=author_id,
            author_name=author_name,
            content=content,
            is_recommendation=is_recommendation
        )
        
        self.comments[proposal_id].append(comment)
        
        logger.info(
            f"💬 Comment added to {proposal_id} by {author_name}"
            f"{' (recommendation)' if is_recommendation else ''}"
        )
        
        return comment
    
    def move_to_voting(self, proposal_id: str) -> None:
        """Move proposal to voting stage"""
        proposal = self._get_proposal(proposal_id)
        
        if proposal.status != ProposalStatus.UNDER_REVIEW:
            raise ValueError(f"Can only vote on proposals UNDER_REVIEW")
        
        proposal.status = ProposalStatus.VOTING
        proposal.updated_at = datetime.utcnow().isoformat()
        
        logger.info(f"🗳️ Proposal {proposal_id} moved to voting")
    
    def approve_proposal(
        self,
        proposal_id: str,
        votes_for: int,
        votes_against: int
    ) -> None:
        """Approve a proposal after successful vote"""
        proposal = self._get_proposal(proposal_id)
        
        if proposal.status != ProposalStatus.VOTING:
            raise ValueError(f"Can only approve proposals in VOTING status")
        
        proposal.status = ProposalStatus.APPROVED
        proposal.votes_for = votes_for
        proposal.votes_against = votes_against
        proposal.approval_date = datetime.utcnow().isoformat()
        proposal.updated_at = datetime.utcnow().isoformat()
        
        logger.info(
            f"✅ Proposal {proposal_id} APPROVED "
            f"({votes_for} for, {votes_against} against)"
        )
    
    def reject_proposal(
        self,
        proposal_id: str,
        votes_for: int,
        votes_against: int,
        reason: Optional[str] = None
    ) -> None:
        """Reject a proposal after failed vote"""
        proposal = self._get_proposal(proposal_id)
        
        if proposal.status != ProposalStatus.VOTING:
            raise ValueError(f"Can only reject proposals in VOTING status")
        
        proposal.status = ProposalStatus.REJECTED
        proposal.votes_for = votes_for
        proposal.votes_against = votes_against
        proposal.rejection_reason = reason
        proposal.updated_at = datetime.utcnow().isoformat()
        
        logger.info(
            f"❌ Proposal {proposal_id} REJECTED "
            f"({votes_for} for, {votes_against} against)"
        )
    
    def mark_implemented(self, proposal_id: str) -> None:
        """Mark proposal as implemented"""
        proposal = self._get_proposal(proposal_id)
        
        if proposal.status != ProposalStatus.APPROVED:
            raise ValueError(f"Can only implement APPROVED proposals")
        
        proposal.status = ProposalStatus.IMPLEMENTED
        proposal.updated_at = datetime.utcnow().isoformat()
        
        logger.info(f"🎉 Proposal {proposal_id} marked as IMPLEMENTED")
    
    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """Get a proposal by ID"""
        return self.proposals.get(proposal_id)
    
    def get_comments(self, proposal_id: str) -> List[ProposalComment]:
        """Get all comments for a proposal"""
        return self.comments.get(proposal_id, [])
    
    def list_proposals(
        self,
        status: Optional[ProposalStatus] = None,
        category: Optional[ProposalCategory] = None,
        limit: int = 50
    ) -> List[Proposal]:
        """
        List proposals with optional filtering
        
        Args:
            status: Filter by status
            category: Filter by category
            limit: Maximum number to return
            
        Returns:
            List of matching proposals
        """
        proposals = list(self.proposals.values())
        
        # Apply filters
        if status:
            proposals = [p for p in proposals if p.status == status]
        
        if category:
            proposals = [p for p in proposals if p.category == category]
        
        # Sort by priority and creation date
        proposals.sort(
            key=lambda p: (p.priority, p.created_at),
            reverse=False
        )
        
        return proposals[:limit]
    
    def get_proposal_stats(self) -> Dict[str, Any]:
        """Get statistics about proposals"""
        total = len(self.proposals)
        
        by_status = {}
        by_category = {}
        
        for proposal in self.proposals.values():
            # Count by status
            status_key = proposal.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1
            
            # Count by category
            cat_key = proposal.category.value
            by_category[cat_key] = by_category.get(cat_key, 0) + 1
        
        return {
            "total_proposals": total,
            "by_status": by_status,
            "by_category": by_category,
            "total_comments": sum(len(c) for c in self.comments.values())
        }
    
    def _get_proposal(self, proposal_id: str) -> Proposal:
        """Internal helper to get proposal or raise error"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        return proposal


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize system
    ps = ProposalSystem()
    
    # Create a proposal
    proposal = ps.create_proposal(
        title="Explore AI Tools Niche",
        description="Research and validate AI tools as a profitable niche",
        category=ProposalCategory.NICHE_DISCOVERY,
        proposed_by="niche-discovery-committee",
        priority=1,
        expected_roi=150.0,
        estimated_cost=20.0,
        success_metrics={
            "traffic": 10000,
            "revenue": 150
        },
        tags=["ai", "tools", "high-priority"]
    )
    
    print(f"\n✅ Created: {proposal.proposal_id}")
    
    # Submit for review
    ps.submit_proposal(proposal.proposal_id)
    
    # Start review
    ps.start_review(proposal.proposal_id, "supreme-council")
    
    # Add comments
    ps.add_comment(
        proposal.proposal_id,
        "market-analyst-1",
        "Market Analyst",
        "Strong market potential with 50k monthly searches",
        is_recommendation=True
    )
    
    # Move to voting
    ps.move_to_voting(proposal.proposal_id)
    
    # Approve
    ps.approve_proposal(proposal.proposal_id, votes_for=5, votes_against=1)
    
    print(f"📊 Status: {proposal.status.value}")
    print(f"💬 Comments: {len(ps.get_comments(proposal.proposal_id))}")
