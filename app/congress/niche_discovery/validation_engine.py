"""
Validation Engine
Validates niche viability with real data and criteria
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

from app.congress.niche_discovery.data_sources import DataSources
from app.congress.niche_discovery.scoring_system import ScoringSystem, NicheScore

logger = logging.getLogger(__name__)


@dataclass
class ValidationCriteria:
    """Criteria for validating a niche"""
    min_search_volume: int = 1000
    max_competition_level: str = "high"  # won't accept "very_high"
    min_monetization_score: float = 50.0
    min_total_score: float = 60.0
    required_trend_direction: List[str] = None  # None = any, else ["rising", "stable"]
    
    def __post_init__(self):
        if self.required_trend_direction is None:
            self.required_trend_direction = ["rising", "stable"]


@dataclass
class ValidationResult:
    """Result of niche validation"""
    niche_id: str
    niche_name: str
    validated: bool
    score: NicheScore
    criteria_met: Dict[str, bool]
    issues: List[str]
    strengths: List[str]
    recommendation: str
    confidence: float
    validated_at: str


class ValidationEngine:
    """
    Validates niche opportunities with real data
    
    Process:
    1. Fetch real data from multiple sources
    2. Score the niche using scoring system
    3. Check against validation criteria
    4. Generate validation report
    """
    
    def __init__(
        self,
        data_sources: Optional[DataSources] = None,
        scoring_system: Optional[ScoringSystem] = None,
        criteria: Optional[ValidationCriteria] = None
    ):
        self.data_sources = data_sources or DataSources()
        self.scoring_system = scoring_system or ScoringSystem()
        self.criteria = criteria or ValidationCriteria()
        
        logger.info("✅ Validation Engine initialized")
    
    def validate_niche(
        self,
        niche_id: str,
        niche_name: str,
        keywords: List[str],
        use_cached_data: bool = False,
        cached_data: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate a niche with real market data
        
        Args:
            niche_id: Unique niche identifier
            niche_name: Human-readable name
            keywords: Keywords to analyze
            use_cached_data: Use cached data instead of fetching
            cached_data: Cached data if available
            
        Returns:
            ValidationResult with verdict and details
        """
        logger.info(f"🔍 Validating niche: {niche_name}")
        
        # Step 1: Fetch or use cached data
        if use_cached_data and cached_data:
            logger.info("📦 Using cached data")
            aggregated_data = cached_data
        else:
            logger.info("📡 Fetching fresh data from sources")
            # Use primary keyword for data fetching
            primary_keyword = keywords[0] if keywords else niche_name
            aggregated_data = self.data_sources.aggregate_niche_data(primary_keyword)
        
        # Step 2: Score the niche
        score = self.scoring_system.score_niche(
            niche_id=niche_id,
            market_data=aggregated_data["market_data"],
            competition_data=aggregated_data["competition_data"],
            trend_data=aggregated_data["trend_data"]
        )
        
        # Step 3: Check criteria
        criteria_met = self._check_criteria(aggregated_data, score)
        
        # Step 4: Identify issues and strengths
        issues = self._identify_issues(aggregated_data, score, criteria_met)
        strengths = self._identify_strengths(aggregated_data, score)
        
        # Step 5: Make validation decision
        validated = all(criteria_met.values()) and score.total_score >= self.criteria.min_total_score
        
        # Step 6: Generate recommendation
        recommendation = self._generate_recommendation(validated, score, issues, strengths)
        
        # Import here to avoid circular dependency
        from datetime import datetime
        
        result = ValidationResult(
            niche_id=niche_id,
            niche_name=niche_name,
            validated=validated,
            score=score,
            criteria_met=criteria_met,
            issues=issues,
            strengths=strengths,
            recommendation=recommendation,
            confidence=score.confidence,
            validated_at=datetime.utcnow().isoformat()
        )
        
        logger.info(
            f"{'✅ VALIDATED' if validated else '❌ REJECTED'}: {niche_name} "
            f"(score: {score.total_score:.1f}, confidence: {score.confidence:.0%})"
        )
        
        return result
    
    def _check_criteria(
        self,
        aggregated_data: Dict[str, Any],
        score: NicheScore
    ) -> Dict[str, bool]:
        """Check if niche meets validation criteria"""
        market_data = aggregated_data["market_data"]
        competition_data = aggregated_data["competition_data"]
        trend_data = aggregated_data["trend_data"]
        
        criteria_met = {
            "min_search_volume": (
                market_data.get("search_volume", 0) >= self.criteria.min_search_volume
            ),
            "competition_acceptable": (
                competition_data.get("level", "very_high") != "very_high"
            ),
            "min_monetization_score": (
                score.factors.monetization >= self.criteria.min_monetization_score
            ),
            "min_total_score": (
                score.total_score >= self.criteria.min_total_score
            ),
            "trend_direction_acceptable": (
                trend_data.get("direction", "unknown") in self.criteria.required_trend_direction
            )
        }
        
        return criteria_met
    
    def _identify_issues(
        self,
        aggregated_data: Dict[str, Any],
        score: NicheScore,
        criteria_met: Dict[str, bool]
    ) -> List[str]:
        """Identify potential issues with the niche"""
        issues = []
        
        market_data = aggregated_data["market_data"]
        competition_data = aggregated_data["competition_data"]
        
        # Check each criterion
        if not criteria_met["min_search_volume"]:
            issues.append(
                f"Search volume ({market_data.get('search_volume', 0)}) below minimum "
                f"({self.criteria.min_search_volume})"
            )
        
        if not criteria_met["competition_acceptable"]:
            issues.append(
                f"Competition level ({competition_data.get('level', 'unknown')}) too high"
            )
        
        if not criteria_met["min_monetization_score"]:
            issues.append(
                f"Monetization score ({score.factors.monetization:.1f}) below minimum "
                f"({self.criteria.min_monetization_score})"
            )
        
        if not criteria_met["min_total_score"]:
            issues.append(
                f"Total score ({score.total_score:.1f}) below minimum "
                f"({self.criteria.min_total_score})"
            )
        
        if not criteria_met["trend_direction_acceptable"]:
            trend = aggregated_data["trend_data"].get("direction", "unknown")
            issues.append(
                f"Trend direction ({trend}) not in acceptable list "
                f"({', '.join(self.criteria.required_trend_direction)})"
            )
        
        # Additional issues from low scores
        if score.factors.market_size < 30:
            issues.append("Market size is very small")
        
        if score.factors.competition < 30:
            issues.append("Competition is extremely high")
        
        if score.factors.growth_rate < 30:
            issues.append("Market is declining or stagnant")
        
        return issues
    
    def _identify_strengths(
        self,
        aggregated_data: Dict[str, Any],
        score: NicheScore
    ) -> List[str]:
        """Identify strengths of the niche"""
        strengths = []
        
        market_data = aggregated_data["market_data"]
        competition_data = aggregated_data["competition_data"]
        
        # High scores indicate strengths
        if score.factors.market_size >= 80:
            strengths.append(
                f"Large market: {market_data.get('search_volume', 0):,} monthly searches"
            )
        
        if score.factors.competition >= 80:
            strengths.append(
                f"Low competition: {competition_data.get('level', 'unknown')} competition level"
            )
        
        if score.factors.monetization >= 80:
            strengths.append(
                f"Strong monetization: Multiple revenue streams available"
            )
        
        if score.factors.growth_rate >= 80:
            strengths.append(
                f"Rapid growth: {market_data.get('growth_rate_percent', 0):.1f}% annual growth"
            )
        
        if score.factors.trend_strength >= 80:
            strengths.append(
                f"Strong trend: {aggregated_data['trend_data'].get('direction', 'unknown')} with high momentum"
            )
        
        if score.factors.entry_barriers >= 70:
            strengths.append("Low entry barriers: Easy to enter market")
        
        # Add from aggregated data
        if len(market_data.get("revenue_models", [])) >= 3:
            strengths.append(
                f"Diverse monetization: {len(market_data['revenue_models'])} revenue models"
            )
        
        community_data = aggregated_data.get("community_data", {})
        if community_data.get("reddit_sentiment") == "positive":
            strengths.append("Positive community sentiment")
        
        return strengths
    
    def _generate_recommendation(
        self,
        validated: bool,
        score: NicheScore,
        issues: List[str],
        strengths: List[str]
    ) -> str:
        """Generate final recommendation"""
        if validated:
            if score.total_score >= 80 and len(strengths) >= 4:
                return "HIGHLY RECOMMEND - Excellent opportunity with multiple strengths"
            elif score.total_score >= 70:
                return "RECOMMEND - Good opportunity worth pursuing"
            else:
                return "APPROVE WITH CAUTION - Meets criteria but monitor closely"
        else:
            if len(issues) == 1:
                return f"REJECT - Single critical issue: {issues[0]}"
            elif len(issues) <= 2:
                return f"REJECT - {len(issues)} issues prevent validation"
            else:
                return f"STRONGLY REJECT - Multiple issues ({len(issues)}) identified"
    
    def batch_validate(
        self,
        niches: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """
        Validate multiple niches in batch
        
        Args:
            niches: List of niche dictionaries with id, name, keywords
            
        Returns:
            List of ValidationResult objects
        """
        logger.info(f"🔍 Batch validating {len(niches)} niches")
        
        results = []
        for niche in niches:
            result = self.validate_niche(
                niche_id=niche["id"],
                niche_name=niche["name"],
                keywords=niche.get("keywords", [])
            )
            results.append(result)
        
        validated_count = sum(1 for r in results if r.validated)
        logger.info(
            f"✅ Batch validation complete: {validated_count}/{len(niches)} validated"
        )
        
        return results
    
    def get_validation_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate summary statistics from validation results"""
        total = len(results)
        validated = sum(1 for r in results if r.validated)
        
        avg_score = sum(r.score.total_score for r in results) / total if total > 0 else 0
        avg_confidence = sum(r.confidence for r in results) / total if total > 0 else 0
        
        return {
            "total_validated": total,
            "validated": validated,
            "rejected": total - validated,
            "validation_rate": validated / total * 100 if total > 0 else 0,
            "average_score": avg_score,
            "average_confidence": avg_confidence,
            "top_validated": sorted(
                [r for r in results if r.validated],
                key=lambda r: r.score.total_score,
                reverse=True
            )[:5],
            "common_issues": self._aggregate_issues(results)
        }
    
    def _aggregate_issues(self, results: List[ValidationResult]) -> Dict[str, int]:
        """Aggregate common issues across validation results"""
        issue_counts = {}
        
        for result in results:
            for issue in result.issues:
                # Simplify issue text for grouping
                key = issue.split(":")[0] if ":" in issue else issue.split("(")[0]
                issue_counts[key] = issue_counts.get(key, 0) + 1
        
        return dict(sorted(issue_counts.items(), key=lambda x: x[1], reverse=True))


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize validation engine
    validator = ValidationEngine()
    
    # Validate a single niche
    result = validator.validate_niche(
        niche_id="AI-TOOLS-001",
        niche_name="AI Productivity Tools",
        keywords=["ai productivity tools", "ai automation", "ai workflow"]
    )
    
    print(f"\n{'✅ VALIDATED' if result.validated else '❌ REJECTED'}: {result.niche_name}")
    print(f"📊 Score: {result.score.total_score:.1f}/100")
    print(f"🎯 Confidence: {result.confidence:.0%}")
    print(f"💡 Recommendation: {result.recommendation}")
    
    if result.strengths:
        print("\n💪 Strengths:")
        for strength in result.strengths:
            print(f"   ✓ {strength}")
    
    if result.issues:
        print("\n⚠️ Issues:")
        for issue in result.issues:
            print(f"   ✗ {issue}")
    
    print("\n📋 Criteria Met:")
    for criterion, met in result.criteria_met.items():
        status = "✅" if met else "❌"
        print(f"   {status} {criterion}")
