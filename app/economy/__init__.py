"""
D8 Economy - Integrated System
Connects all economic components
"""

# Try to import blockchain client, use mock if web3 not available
try:
    from app.economy.blockchain_client import BSCClient, D8TokenClient
    BLOCKCHAIN_AVAILABLE = True
except ImportError:
    BLOCKCHAIN_AVAILABLE = False
    BSCClient = None
    D8TokenClient = None

# Try to import security, use mock if cryptography not available
try:
    from app.economy.security import FundamentalLawsSecurity
    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False
    from app.economy.mock_security import FundamentalLawsSecurity
from app.economy.d8_credits import D8CreditsSystem
from app.economy.revenue_attribution import RevenueAttributionSystem, AgentContribution
from app.economy.accounting import AutonomousAccountingSystem, ExpenseCategory

import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class D8EconomySystem:
    """
    Integrated D8 Economy System
    
    Manages:
    - Blockchain connection
    - Smart contracts (D8Token, FundamentalLaws)
    - Agent wallets and balances
    - Revenue attribution
    - Autonomous accounting
    """
    
    def __init__(
        self,
        bsc_rpc_url: str,
        d8_token_address: str,
        fundamental_laws_address: str,
        congress_address: str,
        congress_private_key: str,
        leo_encryption_key: Optional[bytes] = None
    ):
        """
        Initialize D8 Economy System
        
        Args:
            bsc_rpc_url: BSC RPC endpoint
            d8_token_address: Deployed D8Token contract address
            fundamental_laws_address: Deployed FundamentalLaws contract address
            congress_address: Congress wallet address
            congress_private_key: Congress wallet private key
            leo_encryption_key: Leo's encryption key for laws
        """
        logger.info("🏗️  Initializing D8 Economy System...")
        
        # 1. Blockchain connection
        self.bsc = BSCClient(bsc_rpc_url)
        logger.info(f"✅ Connected to BSC: Chain ID {self.bsc.get_chain_id()}")
        
        # 2. Smart contracts
        self.token = D8TokenClient(self.bsc, d8_token_address)
        logger.info(f"✅ D8Token contract: {d8_token_address}")
        
        self.laws = FundamentalLawsSecurity(
            bsc_client=self.bsc,
            contract_address=fundamental_laws_address,
            encryption_key=leo_encryption_key
        )
        logger.info(f"✅ FundamentalLaws contract: {fundamental_laws_address}")
        
        # 3. Credits system
        self.credits = D8CreditsSystem(
            d8_token_client=self.token,
            bsc_client=self.bsc
        )
        self.credits.set_congress_wallet(congress_address, congress_private_key)
        logger.info("✅ D8 Credits System ready")
        
        # 4. Revenue attribution
        self.attribution = RevenueAttributionSystem(self.credits)
        logger.info("✅ Revenue Attribution System ready")
        
        # 5. Autonomous accounting
        self.accounting = AutonomousAccountingSystem(self.credits, self.attribution)
        self.accounting.initialize_monthly_budget()
        logger.info("✅ Autonomous Accounting System ready")
        
        logger.info("🎉 D8 Economy System fully initialized!")
    
    def create_agent_account(self, agent_id: str) -> dict:
        """
        Create complete account for new agent
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Dictionary with wallet info
        """
        wallet = self.credits.create_wallet(agent_id)
        
        return {
            'agent_id': agent_id,
            'address': wallet.address,
            'balance': wallet.balance,
            'created_at': wallet.created_at.isoformat()
        }
    
    def record_agent_contribution(
        self,
        agent_id: str,
        role: str,
        fitness_score: float,
        revenue_generated: float,
        contribution_score: float = 1.0,
        actions_performed: int = 1,
        niche: Optional[str] = None
    ):
        """
        Record agent contribution and distribute revenue
        
        Args:
            agent_id: Contributing agent
            role: Role performed
            fitness_score: Fitness achieved
            revenue_generated: Revenue from fitness
            contribution_score: Quality of contribution (0.0-1.0)
            actions_performed: Number of actions
            niche: Optional niche identifier
        """
        contribution = AgentContribution(
            agent_id=agent_id,
            role=role,
            contribution_score=contribution_score,
            actions_performed=actions_performed,
            timestamp=datetime.now()
        )
        
        self.attribution.record_fitness_event(
            fitness_score=fitness_score,
            revenue_generated=revenue_generated,
            contributors=[contribution],
            niche=niche
        )
    
    def pay_api_cost(
        self,
        amount: float,
        provider: str,
        description: str
    ):
        """
        Pay API cost (LLM provider)
        
        Args:
            amount: Cost in D8C
            provider: Provider name (Groq, Gemini, DeepSeek)
            description: Description of usage
        """
        self.accounting.record_expense(
            category=ExpenseCategory.API_COSTS,
            amount=amount,
            description=f"{provider}: {description}"
        )
    
    def get_agent_stats(self, agent_id: str) -> dict:
        """
        Get comprehensive stats for an agent
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Dictionary with all stats
        """
        wallet = self.credits.get_wallet(agent_id)
        contribution_stats = self.attribution.get_agent_contribution_stats(agent_id)
        
        return {
            'wallet': wallet.to_dict() if wallet else None,
            'contributions': contribution_stats,
            'rank_by_earnings': self._get_agent_rank(agent_id, 'earnings'),
            'rank_by_contributions': self._get_agent_rank(agent_id, 'contributions')
        }
    
    def _get_agent_rank(self, agent_id: str, metric: str) -> Optional[int]:
        """Get agent's rank in leaderboard"""
        leaderboard = self.attribution.get_leaderboard(metric=metric, limit=1000)
        for i, (aid, _) in enumerate(leaderboard, 1):
            if aid == agent_id:
                return i
        return None
    
    def get_system_health(self) -> dict:
        """
        Get overall system health metrics
        
        Returns:
            Dictionary with health indicators
        """
        financial_report = self.accounting.generate_financial_report()
        credits_stats = self.credits.get_stats()
        collective_fitness = self.attribution.get_collective_fitness()
        
        congress_balance = self.credits.get_balance("congress")
        
        # Determine health status
        if congress_balance < self.accounting.critical_balance_threshold:
            health_status = "CRITICAL"
        elif congress_balance < self.accounting.low_balance_threshold:
            health_status = "WARNING"
        else:
            health_status = "HEALTHY"
        
        return {
            'status': health_status,
            'congress_balance': congress_balance,
            'total_agents': credits_stats['total_agents'],
            'total_supply': credits_stats['total_supply'],
            'total_fitness': collective_fitness['total_fitness'],
            'total_revenue': collective_fitness['total_revenue'],
            'unpaid_expenses': financial_report['summary']['unpaid_expenses'],
            'active_alerts': financial_report['alerts'],
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_full_report(self) -> dict:
        """
        Generate comprehensive system report
        
        Returns:
            Complete report dictionary
        """
        return {
            'system_health': self.get_system_health(),
            'financial_report': self.accounting.generate_financial_report(),
            'credits_stats': self.credits.get_stats(),
            'collective_fitness': self.attribution.get_collective_fitness(),
            'top_earners': self.attribution.get_leaderboard('earnings', 10),
            'top_contributors': self.attribution.get_leaderboard('contributions', 10),
            'richest_agents': self.credits.get_richest_agents(10)
        }
