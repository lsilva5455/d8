"""
Session Manager for Congress
Schedules and manages committee meetings and council sessions
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging
import asyncio

logger = logging.getLogger(__name__)


class SessionType(Enum):
    """Types of congress sessions"""
    COMMITTEE_MEETING = "committee_meeting"
    COUNCIL_SESSION = "council_session"
    STRATEGIC_PLANNING = "strategic_planning"
    EMERGENCY_SESSION = "emergency_session"
    VOTING_SESSION = "voting_session"


class SessionStatus(Enum):
    """Status of a session"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class SessionAgenda:
    """Agenda items for a session"""
    items: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_item(self, title: str, description: str, duration_minutes: int = 30) -> None:
        """Add an agenda item"""
        self.items.append({
            "title": title,
            "description": description,
            "duration_minutes": duration_minutes,
            "completed": False
        })


@dataclass
class Session:
    """Represents a congress session"""
    session_id: str
    session_type: SessionType
    title: str
    description: str
    organizer: str  # Committee or council name
    participants: List[str] = field(default_factory=list)  # Agent IDs
    scheduled_time: Optional[str] = None
    duration_minutes: int = 60
    agenda: SessionAgenda = field(default_factory=SessionAgenda)
    status: SessionStatus = SessionStatus.SCHEDULED
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)  # Proposal IDs
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """
    Manages scheduling and execution of congress sessions
    
    Features:
    - Schedule regular and emergency sessions
    - Track session participation
    - Record decisions and outcomes
    - Support recurring sessions
    """
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.recurring_sessions: List[Dict[str, Any]] = []
        logger.info("📅 Session Manager initialized")
    
    def schedule_session(
        self,
        session_type: SessionType,
        title: str,
        description: str,
        organizer: str,
        participants: List[str],
        scheduled_time: Optional[datetime] = None,
        duration_minutes: int = 60,
        agenda_items: Optional[List[Dict[str, Any]]] = None
    ) -> Session:
        """
        Schedule a new session
        
        Args:
            session_type: Type of session
            title: Session title
            description: Session description
            organizer: Who is organizing (committee/council)
            participants: List of participant agent IDs
            scheduled_time: When to hold session (None = immediate)
            duration_minutes: How long session should last
            agenda_items: List of agenda items
            
        Returns:
            Created Session object
        """
        session_id = f"SESSION-{uuid.uuid4().hex[:8].upper()}"
        
        # Create agenda
        agenda = SessionAgenda()
        if agenda_items:
            for item in agenda_items:
                agenda.add_item(
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    duration_minutes=item.get("duration_minutes", 30)
                )
        
        session = Session(
            session_id=session_id,
            session_type=session_type,
            title=title,
            description=description,
            organizer=organizer,
            participants=participants,
            scheduled_time=scheduled_time.isoformat() if scheduled_time else None,
            duration_minutes=duration_minutes,
            agenda=agenda
        )
        
        self.sessions[session_id] = session
        
        logger.info(
            f"📅 Session scheduled: {session_id} - {title} "
            f"({session_type.value}) by {organizer}"
        )
        
        return session
    
    def schedule_recurring(
        self,
        session_type: SessionType,
        title: str,
        description: str,
        organizer: str,
        participants: List[str],
        frequency_days: int,  # How often to repeat
        start_date: datetime,
        duration_minutes: int = 60
    ) -> str:
        """
        Schedule a recurring session
        
        Args:
            session_type: Type of session
            title: Session title
            description: Session description
            organizer: Who is organizing
            participants: List of participants
            frequency_days: Days between sessions
            start_date: When to start
            duration_minutes: Session duration
            
        Returns:
            ID of recurring session schedule
        """
        schedule_id = f"RECURRING-{uuid.uuid4().hex[:8].upper()}"
        
        recurring = {
            "schedule_id": schedule_id,
            "session_type": session_type,
            "title": title,
            "description": description,
            "organizer": organizer,
            "participants": participants,
            "frequency_days": frequency_days,
            "start_date": start_date.isoformat(),
            "duration_minutes": duration_minutes,
            "last_scheduled": None
        }
        
        self.recurring_sessions.append(recurring)
        
        logger.info(
            f"🔁 Recurring session scheduled: {title} "
            f"(every {frequency_days} days)"
        )
        
        return schedule_id
    
    def start_session(self, session_id: str) -> None:
        """Start a scheduled session"""
        session = self._get_session(session_id)
        
        if session.status != SessionStatus.SCHEDULED:
            raise ValueError(f"Can only start SCHEDULED sessions")
        
        session.status = SessionStatus.IN_PROGRESS
        session.start_time = datetime.utcnow().isoformat()
        
        logger.info(f"▶️ Session started: {session_id} - {session.title}")
    
    def end_session(
        self,
        session_id: str,
        notes: Optional[List[str]] = None,
        decisions: Optional[List[str]] = None
    ) -> None:
        """
        End a session and record outcomes
        
        Args:
            session_id: ID of session to end
            notes: Session notes/summary
            decisions: List of proposal IDs decided upon
        """
        session = self._get_session(session_id)
        
        if session.status != SessionStatus.IN_PROGRESS:
            raise ValueError(f"Can only end IN_PROGRESS sessions")
        
        session.status = SessionStatus.COMPLETED
        session.end_time = datetime.utcnow().isoformat()
        
        if notes:
            session.notes.extend(notes)
        
        if decisions:
            session.decisions.extend(decisions)
        
        logger.info(
            f"⏹️ Session ended: {session_id} - {session.title} "
            f"({len(decisions or [])} decisions made)"
        )
    
    def cancel_session(self, session_id: str, reason: Optional[str] = None) -> None:
        """Cancel a scheduled session"""
        session = self._get_session(session_id)
        
        if session.status != SessionStatus.SCHEDULED:
            raise ValueError(f"Can only cancel SCHEDULED sessions")
        
        session.status = SessionStatus.CANCELLED
        if reason:
            session.notes.append(f"Cancelled: {reason}")
        
        logger.info(f"❌ Session cancelled: {session_id}")
    
    def add_note(self, session_id: str, note: str) -> None:
        """Add a note to a session"""
        session = self._get_session(session_id)
        session.notes.append(note)
        logger.info(f"📝 Note added to session {session_id}")
    
    def record_decision(self, session_id: str, proposal_id: str) -> None:
        """Record a decision made during session"""
        session = self._get_session(session_id)
        
        if proposal_id not in session.decisions:
            session.decisions.append(proposal_id)
            logger.info(f"✅ Decision recorded in {session_id}: {proposal_id}")
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        return self.sessions.get(session_id)
    
    def list_sessions(
        self,
        status: Optional[SessionStatus] = None,
        session_type: Optional[SessionType] = None,
        organizer: Optional[str] = None,
        limit: int = 50
    ) -> List[Session]:
        """
        List sessions with optional filtering
        
        Args:
            status: Filter by status
            session_type: Filter by type
            organizer: Filter by organizer
            limit: Maximum number to return
            
        Returns:
            List of matching sessions
        """
        sessions = list(self.sessions.values())
        
        # Apply filters
        if status:
            sessions = [s for s in sessions if s.status == status]
        
        if session_type:
            sessions = [s for s in sessions if s.session_type == session_type]
        
        if organizer:
            sessions = [s for s in sessions if s.organizer == organizer]
        
        # Sort by scheduled time (most recent first)
        sessions.sort(
            key=lambda s: s.scheduled_time or s.created_at,
            reverse=True
        )
        
        return sessions[:limit]
    
    def get_upcoming_sessions(self, days: int = 7) -> List[Session]:
        """Get sessions scheduled in the next N days"""
        now = datetime.utcnow()
        future = now + timedelta(days=days)
        
        upcoming = []
        for session in self.sessions.values():
            if session.status == SessionStatus.SCHEDULED and session.scheduled_time:
                scheduled = datetime.fromisoformat(session.scheduled_time)
                if now <= scheduled <= future:
                    upcoming.append(session)
        
        upcoming.sort(key=lambda s: s.scheduled_time)
        return upcoming
    
    def check_recurring_sessions(self) -> List[Session]:
        """
        Check if any recurring sessions need to be scheduled
        Returns list of newly scheduled sessions
        """
        now = datetime.utcnow()
        newly_scheduled = []
        
        for recurring in self.recurring_sessions:
            last_scheduled = recurring.get("last_scheduled")
            
            # Check if we need to schedule next occurrence
            should_schedule = False
            
            if not last_scheduled:
                # First time - schedule if start date has passed
                start_date = datetime.fromisoformat(recurring["start_date"])
                should_schedule = now >= start_date
            else:
                # Check if enough time has passed since last scheduling
                last_date = datetime.fromisoformat(last_scheduled)
                days_passed = (now - last_date).days
                should_schedule = days_passed >= recurring["frequency_days"]
            
            if should_schedule:
                # Schedule next occurrence
                next_time = now + timedelta(hours=1)  # Schedule 1 hour from now
                
                session = self.schedule_session(
                    session_type=recurring["session_type"],
                    title=recurring["title"],
                    description=recurring["description"],
                    organizer=recurring["organizer"],
                    participants=recurring["participants"],
                    scheduled_time=next_time,
                    duration_minutes=recurring["duration_minutes"]
                )
                
                recurring["last_scheduled"] = now.isoformat()
                newly_scheduled.append(session)
                
                logger.info(
                    f"🔁 Recurring session scheduled: {session.session_id} "
                    f"for {next_time.isoformat()}"
                )
        
        return newly_scheduled
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about sessions"""
        total = len(self.sessions)
        
        by_status = {}
        by_type = {}
        
        for session in self.sessions.values():
            # Count by status
            status_key = session.status.value
            by_status[status_key] = by_status.get(status_key, 0) + 1
            
            # Count by type
            type_key = session.session_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1
        
        return {
            "total_sessions": total,
            "by_status": by_status,
            "by_type": by_type,
            "recurring_schedules": len(self.recurring_sessions)
        }
    
    def _get_session(self, session_id: str) -> Session:
        """Internal helper to get session or raise error"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return session


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize manager
    sm = SessionManager()
    
    # Schedule a committee meeting
    session = sm.schedule_session(
        session_type=SessionType.COMMITTEE_MEETING,
        title="Niche Discovery Weekly Review",
        description="Review newly discovered niches and validate candidates",
        organizer="niche-discovery-committee",
        participants=["market-analyst-1", "market-analyst-2", "trend-predictor"],
        scheduled_time=datetime.utcnow() + timedelta(hours=2),
        duration_minutes=90,
        agenda_items=[
            {"title": "Review new candidates", "duration_minutes": 30},
            {"title": "Validate top 3 niches", "duration_minutes": 40},
            {"title": "Vote on proposals", "duration_minutes": 20}
        ]
    )
    
    print(f"\n✅ Scheduled: {session.session_id}")
    print(f"📋 Agenda items: {len(session.agenda.items)}")
    
    # Schedule recurring weekly meeting
    recurring_id = sm.schedule_recurring(
        session_type=SessionType.COUNCIL_SESSION,
        title="Supreme Council Weekly Session",
        description="Weekly strategic decisions and resource allocation",
        organizer="supreme-council",
        participants=["council-member-1", "council-member-2", "council-member-3"],
        frequency_days=7,
        start_date=datetime.utcnow(),
        duration_minutes=120
    )
    
    print(f"🔁 Recurring scheduled: {recurring_id}")
    
    # Get stats
    stats = sm.get_session_stats()
    print(f"\n📊 Stats: {stats}")
