"""
Niche Scoring System
Multi-factor scoring to evaluate niche opportunities
"""

from typing import Dict, Any, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScoringFactors:
    """Factors used in niche scoring"""
    market_size: float = 0.0          # 0-100
    growth_rate: float = 0.0          # 0-100
    competition: float = 0.0          # 0-100 (higher = less competition)
    monetization: float = 0.0         # 0-100
    trend_strength: float = 0.0       # 0-100
    entry_barriers: float = 0.0       # 0-100 (higher = lower barriers)
    content_difficulty: float = 0.0   # 0-100 (higher = easier)
    seo_opportunity: float = 0.0      # 0-100


@dataclass
class NicheScore:
    """Complete niche score with breakdown"""
    niche_id: str
    total_score: float  # Weighted average of all factors
    factors: ScoringFactors
    weights: Dict[str, float]
    confidence: float  # How confident we are in the scoring
    recommendation: str  # high_priority, medium_priority, low_priority, reject
    reasoning: List[str]


class ScoringSystem:
    """
    Scores niche opportunities on multiple factors
    
    Scoring weights (customizable):
    - Market Size: 20%
    - Growth Rate: 15%
    - Competition: 25% (most important - low competition is key)
    - Monetization: 20%
    - Trend Strength: 10%
    - Entry Barriers: 5%
    - Content Difficulty: 3%
    - SEO Opportunity: 2%
    """
    
    DEFAULT_WEIGHTS = {
        "market_size": 0.20,
        "growth_rate": 0.15,
        "competition": 0.25,
        "monetization": 0.20,
        "trend_strength": 0.10,
        "entry_barriers": 0.05,
        "content_difficulty": 0.03,
        "seo_opportunity": 0.02
    }
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize scoring system
        
        Args:
            weights: Custom weights for scoring factors (must sum to 1.0)
        """
        self.weights = weights or self.DEFAULT_WEIGHTS
        
        # Validate weights sum to 1.0
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        
        logger.info("📊 Niche Scoring System initialized")
    
    def score_niche(
        self,
        niche_id: str,
        market_data: Dict[str, Any],
        competition_data: Dict[str, Any],
        trend_data: Dict[str, Any]
    ) -> NicheScore:
        """
        Calculate comprehensive score for a niche
        
        Args:
            niche_id: ID of niche
            market_data: Market size, revenue potential, etc.
            competition_data: Competition level, top players, etc.
            trend_data: Trend direction, momentum, etc.
            
        Returns:
            NicheScore with breakdown
        """
        logger.info(f"📊 Scoring niche: {niche_id}")
        
        # Calculate individual factor scores
        factors = ScoringFactors(
            market_size=self._score_market_size(market_data),
            growth_rate=self._score_growth_rate(market_data),
            competition=self._score_competition(competition_data),
            monetization=self._score_monetization(market_data),
            trend_strength=self._score_trend(trend_data),
            entry_barriers=self._score_entry_barriers(market_data, competition_data),
            content_difficulty=self._score_content_difficulty(market_data),
            seo_opportunity=self._score_seo(market_data)
        )
        
        # Calculate weighted total score
        total_score = (
            factors.market_size * self.weights["market_size"] +
            factors.growth_rate * self.weights["growth_rate"] +
            factors.competition * self.weights["competition"] +
            factors.monetization * self.weights["monetization"] +
            factors.trend_strength * self.weights["trend_strength"] +
            factors.entry_barriers * self.weights["entry_barriers"] +
            factors.content_difficulty * self.weights["content_difficulty"] +
            factors.seo_opportunity * self.weights["seo_opportunity"]
        )
        
        # Determine confidence based on data quality
        confidence = self._calculate_confidence(market_data, competition_data, trend_data)
        
        # Generate recommendation
        recommendation, reasoning = self._generate_recommendation(total_score, factors)
        
        score = NicheScore(
            niche_id=niche_id,
            total_score=total_score,
            factors=factors,
            weights=self.weights,
            confidence=confidence,
            recommendation=recommendation,
            reasoning=reasoning
        )
        
        logger.info(
            f"✅ Score calculated: {total_score:.1f}/100 "
            f"({recommendation}, confidence: {confidence:.0%})"
        )
        
        return score
    
    def _score_market_size(self, market_data: Dict[str, Any]) -> float:
        """Score market size (0-100)"""
        search_volume = market_data.get("search_volume", 0)
        
        # Scoring thresholds
        if search_volume >= 100000:
            return 100.0
        elif search_volume >= 50000:
            return 85.0
        elif search_volume >= 10000:
            return 70.0
        elif search_volume >= 5000:
            return 50.0
        elif search_volume >= 1000:
            return 30.0
        else:
            return 10.0
    
    def _score_growth_rate(self, market_data: Dict[str, Any]) -> float:
        """Score growth rate (0-100)"""
        growth = market_data.get("growth_rate_percent", 0)
        
        # Convert growth rate to score
        if growth >= 50:
            return 100.0
        elif growth >= 30:
            return 85.0
        elif growth >= 15:
            return 70.0
        elif growth >= 5:
            return 50.0
        elif growth > 0:
            return 30.0
        else:
            return 10.0  # Declining market
    
    def _score_competition(self, competition_data: Dict[str, Any]) -> float:
        """Score competition level (0-100, higher = less competition)"""
        level = competition_data.get("level", "unknown")
        
        # Lower competition = higher score
        competition_scores = {
            "very_low": 100.0,
            "low": 85.0,
            "medium": 60.0,
            "high": 35.0,
            "very_high": 10.0,
            "unknown": 40.0
        }
        
        return competition_scores.get(level, 40.0)
    
    def _score_monetization(self, market_data: Dict[str, Any]) -> float:
        """Score monetization potential (0-100)"""
        revenue_models = market_data.get("revenue_models", [])
        avg_cpc = market_data.get("avg_cpc", 0)
        affiliate_available = market_data.get("affiliate_programs", False)
        
        score = 0.0
        
        # Multiple revenue models is good
        score += min(len(revenue_models) * 20, 40)
        
        # High CPC is good
        if avg_cpc >= 5:
            score += 40
        elif avg_cpc >= 2:
            score += 25
        elif avg_cpc >= 1:
            score += 15
        
        # Affiliate programs available
        if affiliate_available:
            score += 20
        
        return min(score, 100.0)
    
    def _score_trend(self, trend_data: Dict[str, Any]) -> float:
        """Score trend strength (0-100)"""
        direction = trend_data.get("direction", "flat")
        momentum = trend_data.get("momentum", 0)  # 0-100
        
        if direction == "rising":
            base_score = 70.0
        elif direction == "stable":
            base_score = 50.0
        elif direction == "declining":
            base_score = 20.0
        else:
            base_score = 40.0
        
        # Adjust for momentum
        return min(base_score + (momentum * 0.3), 100.0)
    
    def _score_entry_barriers(
        self,
        market_data: Dict[str, Any],
        competition_data: Dict[str, Any]
    ) -> float:
        """Score entry barriers (0-100, higher = lower barriers)"""
        technical_complexity = market_data.get("technical_complexity", "medium")
        capital_required = market_data.get("capital_required", "medium")
        
        score = 50.0  # baseline
        
        # Lower technical complexity = easier entry
        if technical_complexity == "low":
            score += 25
        elif technical_complexity == "high":
            score -= 25
        
        # Lower capital required = easier entry
        if capital_required == "low":
            score += 25
        elif capital_required == "high":
            score -= 25
        
        return max(0, min(score, 100.0))
    
    def _score_content_difficulty(self, market_data: Dict[str, Any]) -> float:
        """Score content creation difficulty (0-100, higher = easier)"""
        content_type = market_data.get("content_type", "standard")
        expertise_required = market_data.get("expertise_required", "medium")
        
        score = 50.0
        
        # Easier content types
        if content_type in ["listicle", "how-to", "review"]:
            score += 30
        elif content_type in ["research", "technical"]:
            score -= 20
        
        # Lower expertise required = easier
        if expertise_required == "low":
            score += 20
        elif expertise_required == "high":
            score -= 20
        
        return max(0, min(score, 100.0))
    
    def _score_seo(self, market_data: Dict[str, Any]) -> float:
        """Score SEO opportunity (0-100)"""
        keyword_difficulty = market_data.get("keyword_difficulty", 50)
        backlink_required = market_data.get("backlinks_required", 100)
        
        # Lower difficulty = better SEO opportunity
        seo_score = 100 - keyword_difficulty
        
        # Adjust for backlink requirements
        if backlink_required < 50:
            seo_score += 10
        elif backlink_required > 200:
            seo_score -= 10
        
        return max(0, min(seo_score, 100.0))
    
    def _calculate_confidence(
        self,
        market_data: Dict[str, Any],
        competition_data: Dict[str, Any],
        trend_data: Dict[str, Any]
    ) -> float:
        """Calculate confidence in the scoring (0-1)"""
        confidence = 0.5  # baseline
        
        # More data = higher confidence
        if market_data.get("search_volume"):
            confidence += 0.1
        if market_data.get("growth_rate_percent") is not None:
            confidence += 0.1
        if competition_data.get("level"):
            confidence += 0.1
        if trend_data.get("direction"):
            confidence += 0.1
        if market_data.get("revenue_models"):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_recommendation(
        self,
        total_score: float,
        factors: ScoringFactors
    ) -> tuple[str, List[str]]:
        """
        Generate recommendation based on score
        
        Returns:
            (recommendation_level, reasoning_list)
        """
        reasoning = []
        
        # Analyze score
        if total_score >= 80:
            recommendation = "high_priority"
            reasoning.append(f"Excellent overall score: {total_score:.1f}/100")
        elif total_score >= 65:
            recommendation = "medium_priority"
            reasoning.append(f"Good overall score: {total_score:.1f}/100")
        elif total_score >= 50:
            recommendation = "low_priority"
            reasoning.append(f"Moderate score: {total_score:.1f}/100")
        else:
            recommendation = "reject"
            reasoning.append(f"Score too low: {total_score:.1f}/100")
        
        # Add factor-specific reasoning
        if factors.competition >= 80:
            reasoning.append("Low competition - great opportunity")
        elif factors.competition <= 30:
            reasoning.append("High competition - challenging market")
        
        if factors.monetization >= 80:
            reasoning.append("Strong monetization potential")
        elif factors.monetization <= 30:
            reasoning.append("Limited monetization options")
        
        if factors.growth_rate >= 80:
            reasoning.append("Rapid growth market")
        elif factors.growth_rate <= 30:
            reasoning.append("Slow or declining growth")
        
        return recommendation, reasoning


# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize scoring system
    scorer = ScoringSystem()
    
    # Example niche data
    market_data = {
        "search_volume": 50000,
        "growth_rate_percent": 25,
        "revenue_models": ["affiliate", "ads", "courses"],
        "avg_cpc": 3.5,
        "affiliate_programs": True,
        "technical_complexity": "low",
        "capital_required": "low",
        "content_type": "how-to",
        "expertise_required": "medium",
        "keyword_difficulty": 35
    }
    
    competition_data = {
        "level": "medium",
        "top_players": 5,
        "market_share_concentrated": False
    }
    
    trend_data = {
        "direction": "rising",
        "momentum": 75
    }
    
    # Score the niche
    score = scorer.score_niche(
        niche_id="TEST-001",
        market_data=market_data,
        competition_data=competition_data,
        trend_data=trend_data
    )
    
    print(f"\n📊 Niche Score: {score.total_score:.1f}/100")
    print(f"📈 Recommendation: {score.recommendation}")
    print(f"🎯 Confidence: {score.confidence:.0%}")
    print("\n💡 Reasoning:")
    for reason in score.reasoning:
        print(f"   - {reason}")
    
    print("\n📋 Factor Breakdown:")
    print(f"   Market Size: {score.factors.market_size:.1f}")
    print(f"   Growth Rate: {score.factors.growth_rate:.1f}")
    print(f"   Competition: {score.factors.competition:.1f}")
    print(f"   Monetization: {score.factors.monetization:.1f}")
