"""
D8 Credits System
Manages agent wallets, balances, and transactions
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    """Record of a D8 Credit transaction"""
    tx_id: str
    from_agent: str
    to_agent: str
    amount: float
    reason: str
    timestamp: datetime
    block_number: Optional[int] = None
    tx_hash: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'tx_id': self.tx_id,
            'from_agent': self.from_agent,
            'to_agent': self.to_agent,
            'amount': self.amount,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat(),
            'block_number': self.block_number,
            'tx_hash': self.tx_hash
        }


@dataclass
class AgentWallet:
    """Agent's D8 Credit wallet"""
    agent_id: str
    address: str
    private_key: str  # Encrypted in production
    balance: float = 0.0
    total_earned: float = 0.0
    total_spent: float = 0.0
    transaction_history: List[Transaction] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_transaction(self, transaction: Transaction):
        """Add transaction to history"""
        self.transaction_history.append(transaction)
        
        # Update balance
        if transaction.to_agent == self.agent_id:
            self.balance += transaction.amount
            self.total_earned += transaction.amount
        elif transaction.from_agent == self.agent_id:
            self.balance -= transaction.amount
            self.total_spent += transaction.amount
    
    def get_net_worth(self) -> float:
        """Calculate net worth"""
        return self.total_earned - self.total_spent
    
    def to_dict(self) -> dict:
        return {
            'agent_id': self.agent_id,
            'address': self.address,
            'balance': self.balance,
            'total_earned': self.total_earned,
            'total_spent': self.total_spent,
            'net_worth': self.get_net_worth(),
            'transaction_count': len(self.transaction_history),
            'created_at': self.created_at.isoformat()
        }


class D8CreditsSystem:
    """
    Central system for managing D8 Credits
    Integrates with blockchain for permanent record
    """
    
    def __init__(self, d8_token_client, bsc_client):
        """
        Initialize credits system
        
        Args:
            d8_token_client: D8Token contract client
            bsc_client: BSC blockchain client
        """
        self.token_client = d8_token_client
        self.bsc = bsc_client
        
        # Wallets storage
        self.wallets: Dict[str, AgentWallet] = {}
        
        # Congress wallet (manages rewards distribution)
        self.congress_address = None
        self.congress_private_key = None
        
        # Transaction counter
        self.tx_counter = 0
        
        # Load wallets from file
        self._load_wallets()
        
        logger.info("💰 D8 Credits System initialized")
    
    def create_wallet(self, agent_id: str) -> AgentWallet:
        """
        Create new wallet for agent
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            New AgentWallet instance
        """
        # Generate new blockchain account
        account = self.bsc.create_account()
        
        # Create wallet
        wallet = AgentWallet(
            agent_id=agent_id,
            address=account['address'],
            private_key=account['private_key']
        )
        
        # Register agent on blockchain
        if self.congress_address and self.congress_private_key:
            try:
                tx_hash = self.token_client.register_agent(
                    self.congress_address,
                    self.congress_private_key,
                    wallet.address,
                    agent_id
                )
                logger.info(f"🤖 Agent {agent_id} registered on blockchain: {tx_hash}")
            except Exception as e:
                logger.error(f"❌ Failed to register agent on blockchain: {e}")
        
        # Store wallet
        self.wallets[agent_id] = wallet
        self._save_wallets()
        
        logger.info(f"💼 Wallet created for {agent_id}: {wallet.address}")
        return wallet
    
    def get_wallet(self, agent_id: str) -> Optional[AgentWallet]:
        """Get agent's wallet"""
        return self.wallets.get(agent_id)
    
    def get_balance(self, agent_id: str) -> float:
        """Get agent's current balance"""
        wallet = self.wallets.get(agent_id)
        if not wallet:
            return 0.0
        
        # Sync with blockchain
        try:
            blockchain_balance = self.token_client.get_balance(wallet.address)
            wallet.balance = blockchain_balance
        except Exception as e:
            logger.warning(f"⚠️  Failed to sync balance from blockchain: {e}")
        
        return wallet.balance
    
    def transfer(
        self,
        from_agent: str,
        to_agent: str,
        amount: float,
        reason: str
    ) -> Optional[Transaction]:
        """
        Transfer D8 Credits between agents
        
        Args:
            from_agent: Sender agent ID
            to_agent: Recipient agent ID
            amount: Amount to transfer
            reason: Reason for transfer
            
        Returns:
            Transaction object if successful
        """
        from_wallet = self.wallets.get(from_agent)
        to_wallet = self.wallets.get(to_agent)
        
        if not from_wallet or not to_wallet:
            logger.error(f"❌ Invalid agent IDs: {from_agent} or {to_agent}")
            return None
        
        if from_wallet.balance < amount:
            logger.error(f"❌ Insufficient balance: {from_agent} has {from_wallet.balance}, needs {amount}")
            return None
        
        # Execute blockchain transaction
        try:
            tx_hash = self.token_client.transfer(
                from_wallet.address,
                from_wallet.private_key,
                to_wallet.address,
                amount
            )
            
            # Wait for confirmation
            receipt = self.bsc.wait_for_receipt(tx_hash)
            
            if receipt['status'] != 1:
                logger.error(f"❌ Transaction failed on blockchain")
                return None
            
            # Create transaction record
            self.tx_counter += 1
            transaction = Transaction(
                tx_id=f"D8TX{self.tx_counter:06d}",
                from_agent=from_agent,
                to_agent=to_agent,
                amount=amount,
                reason=reason,
                timestamp=datetime.now(),
                block_number=receipt['blockNumber'],
                tx_hash=tx_hash
            )
            
            # Update wallets
            from_wallet.add_transaction(transaction)
            to_wallet.add_transaction(transaction)
            
            self._save_wallets()
            
            logger.info(f"💸 Transfer: {from_agent} → {to_agent}: {amount} D8C")
            logger.info(f"   Reason: {reason}")
            logger.info(f"   TX: {tx_hash}")
            
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Transfer failed: {e}")
            return None
    
    def reward_agent(
        self,
        agent_id: str,
        amount: float,
        reason: str
    ) -> Optional[Transaction]:
        """
        Reward agent with D8 Credits from congress
        
        Args:
            agent_id: Agent to reward
            amount: Amount to reward
            reason: Reason for reward
            
        Returns:
            Transaction object if successful
        """
        wallet = self.wallets.get(agent_id)
        
        if not wallet:
            logger.error(f"❌ Agent not found: {agent_id}")
            return None
        
        if not self.congress_address or not self.congress_private_key:
            logger.error("❌ Congress wallet not configured")
            return None
        
        # Distribute reward from congress
        try:
            tx_hash = self.token_client.distribute_reward(
                self.congress_address,
                self.congress_private_key,
                wallet.address,
                amount,
                reason
            )
            
            # Wait for confirmation
            receipt = self.bsc.wait_for_receipt(tx_hash)
            
            if receipt['status'] != 1:
                logger.error(f"❌ Reward transaction failed")
                return None
            
            # Create transaction record
            self.tx_counter += 1
            transaction = Transaction(
                tx_id=f"D8TX{self.tx_counter:06d}",
                from_agent="congress",
                to_agent=agent_id,
                amount=amount,
                reason=reason,
                timestamp=datetime.now(),
                block_number=receipt['blockNumber'],
                tx_hash=tx_hash
            )
            
            # Update wallet
            wallet.add_transaction(transaction)
            self._save_wallets()
            
            logger.info(f"🎁 Reward: {agent_id}: {amount} D8C")
            logger.info(f"   Reason: {reason}")
            
            return transaction
            
        except Exception as e:
            logger.error(f"❌ Reward failed: {e}")
            return None
    
    def set_congress_wallet(self, address: str, private_key: str):
        """Set congress wallet for reward distribution"""
        self.congress_address = address
        self.congress_private_key = private_key
        logger.info(f"🏛️  Congress wallet configured: {address}")
    
    def get_total_supply(self) -> float:
        """Get total D8 Credits in circulation"""
        total = sum(wallet.balance for wallet in self.wallets.values())
        return total
    
    def get_richest_agents(self, limit: int = 10) -> List[tuple]:
        """
        Get richest agents by balance
        
        Returns:
            List of (agent_id, balance) tuples
        """
        agents = [(aid, w.balance) for aid, w in self.wallets.items()]
        agents.sort(key=lambda x: x[1], reverse=True)
        return agents[:limit]
    
    def get_stats(self) -> dict:
        """Get system statistics"""
        return {
            'total_agents': len(self.wallets),
            'total_supply': self.get_total_supply(),
            'total_transactions': self.tx_counter,
            'average_balance': self.get_total_supply() / max(len(self.wallets), 1),
            'richest_agents': self.get_richest_agents(5)
        }
    
    def _load_wallets(self):
        """Load wallets from file"""
        wallet_file = Path.home() / "Documents" / "d8_data" / "wallets.json"
        
        if wallet_file.exists():
            try:
                with open(wallet_file) as f:
                    data = json.load(f)
                    
                # Reconstruct wallets
                for agent_id, wallet_data in data.get('wallets', {}).items():
                    transactions = [
                        Transaction(
                            tx_id=tx['tx_id'],
                            from_agent=tx['from_agent'],
                            to_agent=tx['to_agent'],
                            amount=tx['amount'],
                            reason=tx['reason'],
                            timestamp=datetime.fromisoformat(tx['timestamp']),
                            block_number=tx.get('block_number'),
                            tx_hash=tx.get('tx_hash')
                        )
                        for tx in wallet_data.get('transactions', [])
                    ]
                    
                    wallet = AgentWallet(
                        agent_id=wallet_data['agent_id'],
                        address=wallet_data['address'],
                        private_key=wallet_data['private_key'],
                        balance=wallet_data['balance'],
                        total_earned=wallet_data['total_earned'],
                        total_spent=wallet_data['total_spent'],
                        transaction_history=transactions,
                        created_at=datetime.fromisoformat(wallet_data['created_at'])
                    )
                    
                    self.wallets[agent_id] = wallet
                
                self.tx_counter = data.get('tx_counter', 0)
                logger.info(f"📂 Loaded {len(self.wallets)} wallets")
                
            except Exception as e:
                logger.error(f"❌ Failed to load wallets: {e}")
    
    def _save_wallets(self):
        """Save wallets to file"""
        wallet_file = Path.home() / "Documents" / "d8_data" / "wallets.json"
        wallet_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'tx_counter': self.tx_counter,
            'wallets': {}
        }
        
        for agent_id, wallet in self.wallets.items():
            data['wallets'][agent_id] = {
                'agent_id': wallet.agent_id,
                'address': wallet.address,
                'private_key': wallet.private_key,
                'balance': wallet.balance,
                'total_earned': wallet.total_earned,
                'total_spent': wallet.total_spent,
                'created_at': wallet.created_at.isoformat(),
                'transactions': [tx.to_dict() for tx in wallet.transaction_history]
            }
        
        with open(wallet_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.debug(f"💾 Saved {len(self.wallets)} wallets")
