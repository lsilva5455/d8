"""
Discovery Engine
24/7 automated niche discovery loop - CORE of the system
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import asyncio
from datetime import datetime
import uuid

from app.congress.niche_discovery.data_sources import DataSources
from app.congress.niche_discovery.validation_engine import ValidationEngine
from app.congress.niche_discovery.scoring_system import ScoringSystem

logger = logging.getLogger(__name__)


@dataclass
class DiscoverySession:
    """Represents a discovery session"""
    session_id: str
    started_at: str
    completed_at: Optional[str] = None
    candidates_generated: int = 0
    candidates_filtered: int = 0
    candidates_analyzed: int = 0
    niches_validated: int = 0
    status: str = "running"  # running, completed, failed


class DiscoveryEngine:
    """
    24/7 Niche Discovery Engine
    
    Loop:
    1. Every 6 hours: Brainstorm new candidates from multiple sources
    2. Continuous: Preliminary filter candidates
    3. Deep analysis: 3 at a time
    4. Validate with real data
    5. Present to Supreme Council
    """
    
    def __init__(
        self,
        data_sources: Optional[DataSources] = None,
        validation_engine: Optional[ValidationEngine] = None,
        scoring_system: Optional[ScoringSystem] = None,
        discovery_frequency_hours: int = 6,
        candidates_per_cycle: int = 10,
        deep_analysis_batch_size: int = 3
    ):
        self.data_sources = data_sources or DataSources()
        self.validation_engine = validation_engine or ValidationEngine()
        self.scoring_system = scoring_system or ScoringSystem()
        
        # Configuration
        self.discovery_frequency_hours = discovery_frequency_hours
        self.candidates_per_cycle = candidates_per_cycle
        self.deep_analysis_batch_size = deep_analysis_batch_size
        
        # State
        self.running = False
        self.candidate_queue: List[Dict[str, Any]] = []
        self.filtered_queue: List[Dict[str, Any]] = []
        self.validated_niches: List[Dict[str, Any]] = []
        self.sessions: List[DiscoverySession] = []
        
        logger.info("🔍 Discovery Engine initialized")
    
    async def run_discovery_loop(self) -> None:
        """
        Main 24/7 discovery loop
        
        Runs continuously:
        - Brainstorms new candidates every N hours
        - Filters and analyzes continuously
        - Validates promising candidates
        """
        self.running = True
        logger.info("🚀 Starting 24/7 discovery loop")
        
        last_brainstorm = datetime.utcnow()
        
        while self.running:
            try:
                # Check if it's time to brainstorm new candidates
                hours_since_brainstorm = (datetime.utcnow() - last_brainstorm).total_seconds() / 3600
                
                if hours_since_brainstorm >= self.discovery_frequency_hours:
                    logger.info("💡 Time to brainstorm new candidates")
                    await self.brainstorm_candidates()
                    last_brainstorm = datetime.utcnow()
                
                # Continuously process queue
                if self.candidate_queue:
                    logger.info(f"📋 Processing {len(self.candidate_queue)} candidates in queue")
                    await self.filter_candidates()
                
                if self.filtered_queue:
                    logger.info(f"🔬 Deep analyzing {min(self.deep_analysis_batch_size, len(self.filtered_queue))} candidates")
                    await self.deep_analysis_batch()
                
                # Sleep for 1 hour before next check
                logger.info("💤 Sleeping for 1 hour until next cycle")
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"❌ Error in discovery loop: {e}")
                await asyncio.sleep(300)  # Sleep 5 minutes on error
        
        logger.info("🛑 Discovery loop stopped")
    
    async def brainstorm_candidates(self) -> List[Dict[str, Any]]:
        """
        Brainstorm new niche candidates from multiple sources
        
        Sources:
        - Trending keywords
        - Reddit discussions
        - Related niche analysis
        - AI-generated ideas
        
        Returns:
            List of candidate niches
        """
        session = DiscoverySession(
            session_id=f"DISCOVER-{uuid.uuid4().hex[:8].upper()}",
            started_at=datetime.utcnow().isoformat()
        )
        
        logger.info(f"💡 Brainstorming session: {session.session_id}")
        
        candidates = []
        
        # Source 1: Trending topics (mock - replace with real trend analysis)
        trending_keywords = await self._get_trending_keywords()
        for keyword in trending_keywords[:self.candidates_per_cycle // 2]:
            candidate = {
                "id": f"NICHE-{uuid.uuid4().hex[:8].upper()}",
                "name": keyword,
                "description": f"Niche focused on {keyword}",
                "source": "trending_analysis",
                "keywords": [keyword],
                "generated_at": datetime.utcnow().isoformat(),
                "status": "candidate"
            }
            candidates.append(candidate)
        
        # Source 2: Reddit hot topics
        reddit_topics = await self._get_reddit_hot_topics()
        for topic in reddit_topics[:self.candidates_per_cycle // 4]:
            candidate = {
                "id": f"NICHE-{uuid.uuid4().hex[:8].upper()}",
                "name": topic,
                "description": f"Community-driven niche: {topic}",
                "source": "reddit_discovery",
                "keywords": [topic.lower()],
                "generated_at": datetime.utcnow().isoformat(),
                "status": "candidate"
            }
            candidates.append(candidate)
        
        # Source 3: AI-generated ideas (mock - replace with real AI brainstorming)
        ai_ideas = await self._generate_ai_ideas()
        for idea in ai_ideas[:self.candidates_per_cycle // 4]:
            candidate = {
                "id": f"NICHE-{uuid.uuid4().hex[:8].upper()}",
                "name": idea["name"],
                "description": idea["description"],
                "source": "ai_generation",
                "keywords": idea["keywords"],
                "generated_at": datetime.utcnow().isoformat(),
                "status": "candidate"
            }
            candidates.append(candidate)
        
        # Add to queue
        self.candidate_queue.extend(candidates)
        session.candidates_generated = len(candidates)
        
        logger.info(f"✅ Generated {len(candidates)} new candidates")
        
        session.status = "completed"
        session.completed_at = datetime.utcnow().isoformat()
        self.sessions.append(session)
        
        return candidates
    
    async def filter_candidates(self) -> List[Dict[str, Any]]:
        """
        Preliminary filter of candidates
        
        Quick checks:
        - Minimum search volume
        - Not oversaturated
        - Basic monetization potential
        
        Returns:
            Filtered candidates that pass initial checks
        """
        if not self.candidate_queue:
            return []
        
        logger.info(f"🔍 Filtering {len(self.candidate_queue)} candidates")
        
        filtered = []
        
        for candidate in self.candidate_queue[:]:
            # Quick check with basic data
            primary_keyword = candidate["keywords"][0] if candidate["keywords"] else candidate["name"]
            
            # Get basic data (lightweight check)
            try:
                keyword_data = self.data_sources.get_keyword_data(primary_keyword)
                
                # Apply filters
                passes_filter = (
                    keyword_data["search_volume"] >= 1000 and
                    keyword_data["competition"] != "very_high" and
                    keyword_data["cpc"] >= 0.5
                )
                
                if passes_filter:
                    candidate["preliminary_data"] = keyword_data
                    candidate["status"] = "filtered"
                    filtered.append(candidate)
                    self.filtered_queue.append(candidate)
                else:
                    candidate["status"] = "rejected_filter"
                
                # Remove from candidate queue
                self.candidate_queue.remove(candidate)
                
            except Exception as e:
                logger.error(f"Error filtering {candidate['name']}: {e}")
                self.candidate_queue.remove(candidate)
        
        logger.info(f"✅ Filtered: {len(filtered)} passed, {len(self.candidate_queue)} remaining")
        
        return filtered
    
    async def deep_analysis_batch(self) -> List[Dict[str, Any]]:
        """
        Deep analysis of top candidates (batch of 3)
        
        For each:
        - Fetch comprehensive data
        - Score with full system
        - Generate detailed analysis
        
        Returns:
            List of deeply analyzed candidates
        """
        if not self.filtered_queue:
            return []
        
        # Take batch
        batch = self.filtered_queue[:self.deep_analysis_batch_size]
        
        logger.info(f"🔬 Deep analyzing batch of {len(batch)} candidates")
        
        analyzed = []
        
        for candidate in batch:
            try:
                logger.info(f"🔬 Analyzing: {candidate['name']}")
                
                # Fetch comprehensive data
                aggregated_data = self.data_sources.aggregate_niche_data(
                    candidate["keywords"][0] if candidate["keywords"] else candidate["name"]
                )
                
                # Score the niche
                score = self.scoring_system.score_niche(
                    niche_id=candidate["id"],
                    market_data=aggregated_data["market_data"],
                    competition_data=aggregated_data["competition_data"],
                    trend_data=aggregated_data["trend_data"]
                )
                
                # Add analysis to candidate
                candidate["analysis"] = {
                    "score": score.total_score,
                    "recommendation": score.recommendation,
                    "factors": {
                        "market_size": score.factors.market_size,
                        "competition": score.factors.competition,
                        "monetization": score.factors.monetization,
                        "growth_rate": score.factors.growth_rate,
                        "trend_strength": score.factors.trend_strength
                    },
                    "reasoning": score.reasoning,
                    "confidence": score.confidence
                }
                candidate["aggregated_data"] = aggregated_data
                candidate["status"] = "analyzed"
                
                analyzed.append(candidate)
                
                # Remove from filtered queue
                self.filtered_queue.remove(candidate)
                
                # If high priority, validate immediately
                if score.recommendation == "high_priority":
                    logger.info(f"⚡ High priority candidate - validating immediately")
                    await self.validate_candidate(candidate)
                
            except Exception as e:
                logger.error(f"Error analyzing {candidate['name']}: {e}")
                self.filtered_queue.remove(candidate)
        
        logger.info(f"✅ Deep analysis complete: {len(analyzed)} analyzed")
        
        return analyzed
    
    async def validate_candidate(self, candidate: Dict[str, Any]) -> bool:
        """
        Validate a candidate with full validation engine
        
        Args:
            candidate: Candidate to validate
            
        Returns:
            True if validated, False otherwise
        """
        logger.info(f"✅ Validating: {candidate['name']}")
        
        try:
            # Use cached aggregated data if available
            cached_data = candidate.get("aggregated_data")
            
            result = self.validation_engine.validate_niche(
                niche_id=candidate["id"],
                niche_name=candidate["name"],
                keywords=candidate["keywords"],
                use_cached_data=cached_data is not None,
                cached_data=cached_data
            )
            
            candidate["validation"] = {
                "validated": result.validated,
                "score": result.score.total_score,
                "confidence": result.confidence,
                "recommendation": result.recommendation,
                "strengths": result.strengths,
                "issues": result.issues,
                "validated_at": result.validated_at
            }
            
            if result.validated:
                candidate["status"] = "validated"
                self.validated_niches.append(candidate)
                logger.info(f"🎉 VALIDATED: {candidate['name']} (score: {result.score.total_score:.1f})")
            else:
                candidate["status"] = "rejected_validation"
                logger.info(f"❌ REJECTED: {candidate['name']} - {result.recommendation}")
            
            return result.validated
            
        except Exception as e:
            logger.error(f"Error validating {candidate['name']}: {e}")
            return False
    
    async def _get_trending_keywords(self) -> List[str]:
        """Get trending keywords (mock - replace with real trend API)"""
        # In production, integrate with Google Trends, Twitter API, etc.
        trending = [
            "ai productivity tools",
            "sustainable living tips",
            "remote work setup",
            "crypto tax software",
            "fitness tracker apps",
            "meal prep containers",
            "home automation devices",
            "online course platforms",
            "podcast editing software",
            "digital nomad resources"
        ]
        return trending
    
    async def _get_reddit_hot_topics(self) -> List[str]:
        """Get hot topics from Reddit (mock - replace with Reddit API)"""
        # In production, use PRAW to fetch trending topics
        topics = [
            "AI image generation",
            "Side hustle ideas 2024",
            "Budget travel hacks",
            "Passive income streams"
        ]
        return topics
    
    async def _generate_ai_ideas(self) -> List[Dict[str, Any]]:
        """Generate niche ideas using AI (mock - replace with real AI)"""
        # In production, use Groq/DeepSeek to brainstorm niches
        ideas = [
            {
                "name": "Senior Tech Training",
                "description": "Tech tutorials specifically for seniors",
                "keywords": ["senior tech training", "technology for seniors", "elder tech help"]
            },
            {
                "name": "Pet Tech Gadgets",
                "description": "Smart devices and apps for pet owners",
                "keywords": ["pet tech", "smart pet devices", "pet monitoring"]
            }
        ]
        return ideas
    
    def stop_discovery_loop(self) -> None:
        """Stop the discovery loop"""
        logger.info("🛑 Stopping discovery loop")
        self.running = False
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get statistics about discovery process"""
        return {
            "running": self.running,
            "candidate_queue_size": len(self.candidate_queue),
            "filtered_queue_size": len(self.filtered_queue),
            "validated_niches": len(self.validated_niches),
            "total_sessions": len(self.sessions),
            "configuration": {
                "frequency_hours": self.discovery_frequency_hours,
                "candidates_per_cycle": self.candidates_per_cycle,
                "batch_size": self.deep_analysis_batch_size
            }
        }
    
    def get_validated_niches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get validated niches sorted by score"""
        sorted_niches = sorted(
            self.validated_niches,
            key=lambda n: n.get("validation", {}).get("score", 0),
            reverse=True
        )
        return sorted_niches[:limit]


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    async def test_discovery():
        """Test discovery engine"""
        # Initialize engine
        engine = DiscoveryEngine(
            discovery_frequency_hours=6,
            candidates_per_cycle=10,
            deep_analysis_batch_size=3
        )
        
        # Test brainstorming
        print("\n💡 Testing brainstorming...")
        candidates = await engine.brainstorm_candidates()
        print(f"Generated {len(candidates)} candidates")
        
        # Test filtering
        print("\n🔍 Testing filtering...")
        filtered = await engine.filter_candidates()
        print(f"Filtered {len(filtered)} candidates")
        
        # Test deep analysis
        print("\n🔬 Testing deep analysis...")
        analyzed = await engine.deep_analysis_batch()
        print(f"Analyzed {len(analyzed)} candidates")
        
        # Get stats
        stats = engine.get_discovery_stats()
        print(f"\n📊 Stats:")
        print(f"   Validated niches: {stats['validated_niches']}")
        print(f"   Queue sizes: {stats['candidate_queue_size']} -> {stats['filtered_queue_size']}")
    
    # Run test
    asyncio.run(test_discovery())
