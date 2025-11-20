"""
Mock Blockchain for Local Testing
Simulates BSC blockchain without real network connection
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MockTransaction:
    """Mock blockchain transaction"""
    def __init__(self, from_addr: str, to_addr: str, value: float, data: str = ""):
        self.hash = '0x' + uuid.uuid4().hex[:64]
        self.from_address = from_addr
        self.to_address = to_addr
        self.value = value
        self.data = data
        self.block_number = MockBlockchain.current_block
        self.timestamp = datetime.now()
        self.status = 1  # Success


class MockBlockchain:
    """Mock blockchain state"""
    current_block = 1000000
    transactions: List[MockTransaction] = []
    balances: Dict[str, float] = {}
    
    @classmethod
    def add_transaction(cls, tx: MockTransaction):
        cls.transactions.append(tx)
        cls.current_block += 1
        
        # Update balances
        if tx.from_address in cls.balances:
            cls.balances[tx.from_address] -= tx.value
        if tx.to_address in cls.balances:
            cls.balances[tx.to_address] += tx.value
        else:
            cls.balances[tx.to_address] = tx.value


class MockBSCClient:
    """Mock BSC client that simulates blockchain without network"""
    
    def __init__(self, rpc_url: str = "mock://localhost"):
        self.rpc_url = rpc_url
        self.chain_id = 97  # Testnet
        logger.info("🎭 Mock BSC Client initialized (no real blockchain)")
    
    def get_chain_id(self) -> int:
        return self.chain_id
    
    def is_connected(self) -> bool:
        return True
    
    def create_account(self) -> dict:
        """Generate mock wallet"""
        account_id = uuid.uuid4().hex
        return {
            'address': '0x' + account_id[:40],
            'private_key': '0x' + account_id[40:] + uuid.uuid4().hex[:24]
        }
    
    def get_balance(self, address: str) -> float:
        """Get mock balance"""
        return MockBlockchain.balances.get(address, 0.0)
    
    def send_transaction(
        self,
        from_address: str,
        private_key: str,
        to_address: str,
        value: float,
        data: str = ""
    ) -> str:
        """Send mock transaction"""
        tx = MockTransaction(from_address, to_address, value, data)
        MockBlockchain.add_transaction(tx)
        
        logger.info(f"📝 Mock TX: {from_address[:10]}...→{to_address[:10]}... {value} D8C")
        return tx.hash
    
    def wait_for_receipt(self, tx_hash: str, timeout: int = 120) -> dict:
        """Mock transaction receipt"""
        # Find transaction
        tx = next((t for t in MockBlockchain.transactions if t.hash == tx_hash), None)
        
        if not tx:
            return {'status': 0, 'blockNumber': 0}
        
        return {
            'status': tx.status,
            'blockNumber': tx.block_number,
            'transactionHash': tx.hash,
            'from': tx.from_address,
            'to': tx.to_address
        }
    
    def fund_account(self, address: str, amount: float):
        """Fund account with mock tokens"""
        MockBlockchain.balances[address] = MockBlockchain.balances.get(address, 0.0) + amount
        logger.info(f"💰 Funded {address[:10]}... with {amount} D8C")


class MockD8TokenClient:
    """Mock D8Token contract client"""
    
    def __init__(self, bsc_client: MockBSCClient, contract_address: str):
        self.bsc = bsc_client
        self.contract_address = contract_address
        self.registered_agents: Dict[str, str] = {}  # address -> agent_id
        logger.info(f"🪙 Mock D8Token at {contract_address[:10]}...")
    
    def register_agent(
        self,
        congress_address: str,
        congress_private_key: str,
        agent_address: str,
        agent_id: str
    ) -> str:
        """Register agent (mock)"""
        self.registered_agents[agent_address] = agent_id
        
        tx_hash = self.bsc.send_transaction(
            congress_address,
            congress_private_key,
            self.contract_address,
            0.0,
            f"registerAgent({agent_id})"
        )
        
        logger.info(f"🤖 Registered agent {agent_id}: {agent_address[:10]}...")
        return tx_hash
    
    def distribute_reward(
        self,
        congress_address: str,
        congress_private_key: str,
        agent_address: str,
        amount: float,
        reason: str
    ) -> str:
        """Distribute reward (mock)"""
        # Transfer from congress to agent
        tx_hash = self.bsc.send_transaction(
            congress_address,
            congress_private_key,
            agent_address,
            amount,
            f"distributeReward({reason})"
        )
        
        logger.info(f"🎁 Reward: {agent_address[:10]}... +{amount} D8C ({reason})")
        return tx_hash
    
    def transfer(
        self,
        from_address: str,
        private_key: str,
        to_address: str,
        amount: float
    ) -> str:
        """Transfer tokens (mock)"""
        tx_hash = self.bsc.send_transaction(
            from_address,
            private_key,
            to_address,
            amount,
            "transfer()"
        )
        
        logger.info(f"💸 Transfer: {from_address[:10]}...→{to_address[:10]}... {amount} D8C")
        return tx_hash
    
    def get_balance(self, address: str) -> float:
        """Get token balance (mock)"""
        return self.bsc.get_balance(address)
    
    def mint(
        self,
        congress_address: str,
        congress_private_key: str,
        amount: float
    ) -> str:
        """Mint new tokens (mock)"""
        # Add to congress balance
        self.bsc.fund_account(congress_address, amount)
        
        tx_hash = '0x' + uuid.uuid4().hex[:64]
        logger.info(f"🏦 Minted {amount} D8C to congress")
        return tx_hash


class MockFundamentalLawsClient:
    """Mock FundamentalLaws contract client"""
    
    def __init__(self, bsc_client: MockBSCClient, contract_address: str):
        self.bsc = bsc_client
        self.contract_address = contract_address
        self.laws: Dict[str, dict] = {}  # law_id -> {encrypted_data, hash, description}
        logger.info(f"📜 Mock FundamentalLaws at {contract_address[:10]}...")
    
    def create_law(
        self,
        owner_address: str,
        owner_private_key: str,
        law_id: str,
        encrypted_data: bytes,
        data_hash: str,
        description: str
    ) -> str:
        """Create law (mock)"""
        self.laws[law_id] = {
            'encrypted_data': encrypted_data,
            'data_hash': data_hash,
            'description': description,
            'version': 1,
            'created_at': datetime.now()
        }
        
        tx_hash = self.bsc.send_transaction(
            owner_address,
            owner_private_key,
            self.contract_address,
            0.0,
            f"createLaw({law_id})"
        )
        
        logger.info(f"📜 Created law: {law_id}")
        return tx_hash
    
    def get_law(self, law_id: str) -> Optional[dict]:
        """Get law (mock)"""
        return self.laws.get(law_id)
    
    def verify_law_integrity(self, law_id: str, expected_hash: str) -> bool:
        """Verify law integrity (mock)"""
        law = self.laws.get(law_id)
        if not law:
            return False
        return law['data_hash'] == expected_hash


def create_mock_economy_system():
    """
    Create complete mock economy system for local testing
    
    Returns:
        D8EconomySystem configured with mock blockchain
    """
    logger.info("🎭 Creating MOCK Economy System (no real blockchain)")
    logger.info("=" * 60)
    
    # 1. Mock blockchain
    mock_bsc = MockBSCClient()
    
    # 2. Mock contracts
    token_address = '0x' + uuid.uuid4().hex[:40]
    laws_address = '0x' + uuid.uuid4().hex[:40]
    
    mock_token = MockD8TokenClient(mock_bsc, token_address)
    
    logger.info(f"✅ Mock D8Token: {token_address}")
    logger.info(f"✅ Mock FundamentalLaws: {laws_address}")
    
    # 3. Create congress wallet
    congress_account = mock_bsc.create_account()
    congress_address = congress_account['address']
    congress_private_key = congress_account['private_key']
    
    # Fund congress with initial supply
    mock_bsc.fund_account(congress_address, 10000.0)
    # Also initialize in MockBlockchain for token transfers
    MockBlockchain.balances[congress_address] = 10000.0
    
    logger.info(f"💰 Funded {congress_address[:10]}... with 10000.0 D8C")
    logger.info(f"✅ Congress wallet: {congress_address}")
    logger.info(f"   Initial balance: {mock_bsc.get_balance(congress_address)} D8C")
    
    # 4. Import and create economy system
    from app.economy.d8_credits import D8CreditsSystem
    from app.economy.revenue_attribution import RevenueAttributionSystem
    from app.economy.accounting import AutonomousAccountingSystem
    
    credits = D8CreditsSystem(mock_token, mock_bsc)
    credits.set_congress_wallet(congress_address, congress_private_key)
    
    attribution = RevenueAttributionSystem(credits)
    accounting = AutonomousAccountingSystem(credits, attribution)
    accounting.initialize_monthly_budget()
    
    logger.info("✅ D8 Credits System ready")
    logger.info("✅ Revenue Attribution ready")
    logger.info("✅ Autonomous Accounting ready")
    logger.info("")
    logger.info("🎉 MOCK Economy System fully operational!")
    logger.info("=" * 60)
    logger.info("")
    
    # Create integrated object
    class MockEconomySystem:
        def __init__(self):
            self.bsc = mock_bsc
            self.token = mock_token
            self.credits = credits
            self.attribution = attribution
            self.accounting = accounting
        
        def create_agent_account(self, agent_id: str) -> dict:
            wallet = self.credits.create_wallet(agent_id)
            return {
                'agent_id': agent_id,
                'address': wallet.address,
                'balance': wallet.balance,
                'created_at': wallet.created_at.isoformat()
            }
        
        def record_agent_contribution(self, **kwargs):
            from app.economy.revenue_attribution import AgentContribution
            from datetime import datetime
            
            contribution = AgentContribution(
                agent_id=kwargs['agent_id'],
                role=kwargs['role'],
                contribution_score=kwargs.get('contribution_score', 1.0),
                actions_performed=kwargs.get('actions_performed', 1),
                timestamp=datetime.now()
            )
            
            self.attribution.record_fitness_event(
                fitness_score=kwargs['fitness_score'],
                revenue_generated=kwargs['revenue_generated'],
                contributors=[contribution],
                niche=kwargs.get('niche')
            )
        
        def pay_api_cost(self, amount: float, provider: str, description: str):
            from app.economy.accounting import ExpenseCategory
            self.accounting.record_expense(
                category=ExpenseCategory.API_COSTS,
                amount=amount,
                description=f"{provider}: {description}",
                auto_pay=False  # Don't actually pay in mock
            )
        
        def get_agent_stats(self, agent_id: str) -> dict:
            wallet = self.credits.get_wallet(agent_id)
            contribution_stats = self.attribution.get_agent_contribution_stats(agent_id)
            
            return {
                'wallet': wallet.to_dict() if wallet else None,
                'contributions': contribution_stats
            }
        
        def get_system_health(self) -> dict:
            financial_report = self.accounting.generate_financial_report()
            credits_stats = self.credits.get_stats()
            collective_fitness = self.attribution.get_collective_fitness()
            
            congress_balance = self.credits.get_balance("congress")
            
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
            return {
                'system_health': self.get_system_health(),
                'financial_report': self.accounting.generate_financial_report(),
                'credits_stats': self.credits.get_stats(),
                'collective_fitness': self.attribution.get_collective_fitness(),
                'top_earners': self.attribution.get_leaderboard('earnings', 10),
                'top_contributors': self.attribution.get_leaderboard('contributions', 10),
                'richest_agents': self.credits.get_richest_agents(10)
            }
    
    return MockEconomySystem()
