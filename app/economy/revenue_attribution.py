"""
Revenue Attribution System
Distributes fitness credits among contributing agents

Implements the 40/40/20 rule:
- 40% to best agent
- 40% to mediocre agent  
- 20% to worst agent

Handles collective fitness scenarios
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentContribution:
    """Record of agent's contribution to a fitness event"""
    agent_id: str
    role: str
    contribution_score: float  # 0.0 to 1.0
    actions_performed: int
    timestamp: datetime


@dataclass
class FitnessEvent:
    """Event that generated fitness/revenue"""
    event_id: str
    fitness_score: float
    revenue_generated: float
    contributors: List[AgentContribution]
    timestamp: datetime
    niche: Optional[str] = None
    
    def get_contribution_distribution(self) -> Dict[str, float]:
        """
        Calculate revenue distribution based on contributions
        
        Returns:
            Dict mapping agent_id to revenue share
        """
        if not self.contributors:
            return {}
        
        # Sort contributors by contribution score
        sorted_contributors = sorted(
            self.contributors,
            key=lambda x: x.contribution_score,
            reverse=True
        )
        
        distribution = {}
        
        if len(sorted_contributors) == 1:
            # Solo agent gets 100%
            distribution[sorted_contributors[0].agent_id] = self.revenue_generated
            
        elif len(sorted_contributors) == 2:
            # Split 70/30
            distribution[sorted_contributors[0].agent_id] = self.revenue_generated * 0.70
            distribution[sorted_contributors[1].agent_id] = self.revenue_generated * 0.30
            
        else:
            # 40/40/20 rule
            best = sorted_contributors[0]
            mid = sorted_contributors[len(sorted_contributors) // 2]
            worst = sorted_contributors[-1]
            
            distribution[best.agent_id] = self.revenue_generated * 0.40
            distribution[mid.agent_id] = self.revenue_generated * 0.40
            distribution[worst.agent_id] = self.revenue_generated * 0.20
            
            # If there are more than 3 contributors, remaining agents get small bonus
            if len(sorted_contributors) > 3:
                remaining_agents = [
                    c for c in sorted_contributors 
                    if c.agent_id not in [best.agent_id, mid.agent_id, worst.agent_id]
                ]
                
                # Distribute small bonus from congress budget
                bonus_per_agent = self.revenue_generated * 0.05 / len(remaining_agents)
                for contributor in remaining_agents:
                    distribution[contributor.agent_id] = bonus_per_agent
        
        return distribution


class RevenueAttributionSystem:
    """
    Manages attribution of fitness/revenue to contributing agents
    """
    
    def __init__(self, credits_system):
        """
        Initialize attribution system
        
        Args:
            credits_system: D8CreditsSystem instance
        """
        self.credits_system = credits_system
        self.fitness_events: List[FitnessEvent] = []
        self.event_counter = 0
        
        logger.info("📊 Revenue Attribution System initialized")
    
    def record_fitness_event(
        self,
        fitness_score: float,
        revenue_generated: float,
        contributors: List[AgentContribution],
        niche: Optional[str] = None
    ) -> FitnessEvent:
        """
        Record a fitness event and attribute revenue
        
        Args:
            fitness_score: Fitness achieved
            revenue_generated: Revenue from this fitness
            contributors: List of contributing agents
            niche: Optional niche identifier
            
        Returns:
            Created FitnessEvent
        """
        self.event_counter += 1
        
        event = FitnessEvent(
            event_id=f"FIT{self.event_counter:06d}",
            fitness_score=fitness_score,
            revenue_generated=revenue_generated,
            contributors=contributors,
            timestamp=datetime.now(),
            niche=niche
        )
        
        self.fitness_events.append(event)
        
        # Calculate distribution
        distribution = event.get_contribution_distribution()
        
        # Distribute rewards
        for agent_id, amount in distribution.items():
            reason = f"Fitness event {event.event_id}: {fitness_score:.2f} fitness"
            if niche:
                reason += f" (niche: {niche})"
            
            self.credits_system.reward_agent(
                agent_id=agent_id,
                amount=amount,
                reason=reason
            )
            
            logger.info(f"💰 {agent_id}: {amount:.2f} D8C from {event.event_id}")
        
        logger.info(f"📊 Fitness event {event.event_id} distributed to {len(distribution)} agents")
        
        return event
    
    def get_agent_total_earnings(self, agent_id: str) -> float:
        """
        Calculate total earnings for an agent from fitness events
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Total earnings
        """
        total = 0.0
        
        for event in self.fitness_events:
            distribution = event.get_contribution_distribution()
            total += distribution.get(agent_id, 0.0)
        
        return total
    
    def get_agent_contribution_stats(self, agent_id: str) -> dict:
        """
        Get contribution statistics for an agent
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Dictionary of statistics
        """
        contributions = []
        earnings = []
        roles = []
        
        for event in self.fitness_events:
            for contributor in event.contributors:
                if contributor.agent_id == agent_id:
                    contributions.append(contributor.contribution_score)
                    roles.append(contributor.role)
                    
            distribution = event.get_contribution_distribution()
            if agent_id in distribution:
                earnings.append(distribution[agent_id])
        
        if not contributions:
            return {
                'total_contributions': 0,
                'average_contribution_score': 0.0,
                'total_earnings': 0.0,
                'average_earnings': 0.0,
                'roles_played': []
            }
        
        return {
            'total_contributions': len(contributions),
            'average_contribution_score': sum(contributions) / len(contributions),
            'total_earnings': sum(earnings),
            'average_earnings': sum(earnings) / len(earnings) if earnings else 0.0,
            'roles_played': list(set(roles)),
            'best_contribution': max(contributions),
            'worst_contribution': min(contributions)
        }
    
    def get_niche_performance(self, niche: str) -> dict:
        """
        Get performance statistics for a niche
        
        Args:
            niche: Niche identifier
            
        Returns:
            Dictionary of statistics
        """
        niche_events = [e for e in self.fitness_events if e.niche == niche]
        
        if not niche_events:
            return {
                'total_events': 0,
                'total_fitness': 0.0,
                'total_revenue': 0.0,
                'average_fitness': 0.0,
                'average_revenue': 0.0
            }
        
        return {
            'total_events': len(niche_events),
            'total_fitness': sum(e.fitness_score for e in niche_events),
            'total_revenue': sum(e.revenue_generated for e in niche_events),
            'average_fitness': sum(e.fitness_score for e in niche_events) / len(niche_events),
            'average_revenue': sum(e.revenue_generated for e in niche_events) / len(niche_events),
            'unique_contributors': len(set(
                c.agent_id 
                for e in niche_events 
                for c in e.contributors
            ))
        }
    
    def get_collective_fitness(self) -> dict:
        """
        Calculate collective fitness metrics
        
        Returns:
            Dictionary with collective metrics
        """
        if not self.fitness_events:
            return {
                'total_fitness': 0.0,
                'total_revenue': 0.0,
                'total_events': 0,
                'average_fitness_per_event': 0.0,
                'total_contributors': 0
            }
        
        all_contributors = set()
        for event in self.fitness_events:
            for contributor in event.contributors:
                all_contributors.add(contributor.agent_id)
        
        return {
            'total_fitness': sum(e.fitness_score for e in self.fitness_events),
            'total_revenue': sum(e.revenue_generated for e in self.fitness_events),
            'total_events': len(self.fitness_events),
            'average_fitness_per_event': sum(e.fitness_score for e in self.fitness_events) / len(self.fitness_events),
            'total_contributors': len(all_contributors),
            'average_contributors_per_event': sum(len(e.contributors) for e in self.fitness_events) / len(self.fitness_events)
        }
    
    def get_leaderboard(self, metric: str = 'earnings', limit: int = 10) -> List[tuple]:
        """
        Get leaderboard of agents
        
        Args:
            metric: 'earnings', 'contributions', or 'average_contribution'
            limit: Number of agents to return
            
        Returns:
            List of (agent_id, value) tuples
        """
        agents = {}
        
        for event in self.fitness_events:
            distribution = event.get_contribution_distribution()
            
            for contributor in event.contributors:
                agent_id = contributor.agent_id
                
                if agent_id not in agents:
                    agents[agent_id] = {
                        'earnings': 0.0,
                        'contributions': 0,
                        'contribution_scores': []
                    }
                
                agents[agent_id]['earnings'] += distribution.get(agent_id, 0.0)
                agents[agent_id]['contributions'] += 1
                agents[agent_id]['contribution_scores'].append(contributor.contribution_score)
        
        # Calculate metric
        if metric == 'earnings':
            leaderboard = [(aid, data['earnings']) for aid, data in agents.items()]
        elif metric == 'contributions':
            leaderboard = [(aid, data['contributions']) for aid, data in agents.items()]
        elif metric == 'average_contribution':
            leaderboard = [
                (aid, sum(data['contribution_scores']) / len(data['contribution_scores']))
                for aid, data in agents.items()
            ]
        else:
            raise ValueError(f"Unknown metric: {metric}")
        
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        return leaderboard[:limit]
