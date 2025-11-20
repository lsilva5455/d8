"""
Blockchain Client for BSC (Binance Smart Chain)
Manages connection to BSC Testnet/Mainnet and contract interactions
"""

from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BSCClient:
    """Client for interacting with Binance Smart Chain"""
    
    def __init__(self, testnet: bool = True):
        """
        Initialize BSC client
        
        Args:
            testnet: If True, connect to BSC Testnet. If False, Mainnet.
        """
        self.testnet = testnet
        
        # Load RPC endpoints from environment
        if testnet:
            self.rpc_url = os.getenv(
                'BSC_TESTNET_RPC', 
                'https://data-seed-prebsc-1-s1.binance.org:8545/'
            )
            self.chain_id = 97
            self.explorer = "https://testnet.bscscan.com"
        else:
            self.rpc_url = os.getenv(
                'BSC_MAINNET_RPC',
                'https://bsc-dataseed.binance.org/'
            )
            self.chain_id = 56
            self.explorer = "https://bscscan.com"
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Inject POA middleware (required for BSC)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Verify connection
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to BSC {'Testnet' if testnet else 'Mainnet'}")
        
        logger.info(f"✅ Connected to BSC {'Testnet' if testnet else 'Mainnet'}")
        logger.info(f"   RPC: {self.rpc_url}")
        logger.info(f"   Chain ID: {self.chain_id}")
    
    def get_balance(self, address: str) -> float:
        """Get BNB balance of address"""
        balance_wei = self.w3.eth.get_balance(address)
        return self.w3.from_wei(balance_wei, 'ether')
    
    def get_gas_price(self) -> int:
        """Get current gas price in wei"""
        return self.w3.eth.gas_price
    
    def create_account(self) -> Dict[str, str]:
        """
        Create new Ethereum account (works for BSC)
        
        Returns:
            Dict with 'address' and 'private_key'
        """
        account = self.w3.eth.account.create()
        return {
            'address': account.address,
            'private_key': account.key.hex()
        }
    
    def load_contract(self, contract_address: str, abi: list) -> Any:
        """Load smart contract instance"""
        checksum_address = self.w3.to_checksum_address(contract_address)
        return self.w3.eth.contract(address=checksum_address, abi=abi)
    
    def send_transaction(
        self, 
        contract_function,
        from_address: str,
        private_key: str,
        gas_limit: int = 300000
    ) -> str:
        """
        Send transaction to smart contract
        
        Returns:
            Transaction hash
        """
        # Build transaction
        tx = contract_function.build_transaction({
            'from': from_address,
            'gas': gas_limit,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.w3.eth.get_transaction_count(from_address),
            'chainId': self.chain_id
        })
        
        # Sign transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
        
        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        logger.info(f"📤 Transaction sent: {tx_hash.hex()}")
        logger.info(f"   Explorer: {self.explorer}/tx/{tx_hash.hex()}")
        
        return tx_hash.hex()
    
    def wait_for_receipt(self, tx_hash: str, timeout: int = 120) -> Dict:
        """Wait for transaction receipt"""
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        
        if receipt['status'] == 1:
            logger.info(f"✅ Transaction successful: {tx_hash}")
        else:
            logger.error(f"❌ Transaction failed: {tx_hash}")
        
        return dict(receipt)
    
    def get_block_number(self) -> int:
        """Get current block number"""
        return self.w3.eth.block_number
    
    def estimate_gas(self, contract_function, from_address: str) -> int:
        """Estimate gas for transaction"""
        return contract_function.estimate_gas({'from': from_address})


class D8TokenClient:
    """Client for D8 Token contract interactions"""
    
    def __init__(self, bsc_client: BSCClient, contract_address: str):
        """
        Initialize D8 Token client
        
        Args:
            bsc_client: BSC client instance
            contract_address: Deployed D8Token contract address
        """
        self.bsc = bsc_client
        self.contract_address = contract_address
        
        # Load contract ABI
        abi_path = Path(__file__).parent / 'contracts' / 'D8Token.json'
        if abi_path.exists():
            with open(abi_path) as f:
                abi = json.load(f)
        else:
            # Minimal ABI for basic operations
            abi = self._get_minimal_abi()
        
        self.contract = self.bsc.load_contract(contract_address, abi)
        logger.info(f"✅ D8Token contract loaded at {contract_address}")
    
    def get_balance(self, agent_address: str) -> float:
        """Get D8 Credit balance of agent"""
        balance_wei = self.contract.functions.balanceOf(agent_address).call()
        return self.bsc.w3.from_wei(balance_wei, 'ether')
    
    def transfer(
        self,
        from_address: str,
        from_private_key: str,
        to_address: str,
        amount: float
    ) -> str:
        """Transfer D8 Credits"""
        amount_wei = self.bsc.w3.to_wei(amount, 'ether')
        
        tx_function = self.contract.functions.transfer(to_address, amount_wei)
        tx_hash = self.bsc.send_transaction(
            tx_function,
            from_address,
            from_private_key
        )
        
        return tx_hash
    
    def register_agent(
        self,
        congress_address: str,
        congress_private_key: str,
        agent_address: str,
        agent_id: str
    ) -> str:
        """Register new agent"""
        tx_function = self.contract.functions.registerAgent(agent_address, agent_id)
        tx_hash = self.bsc.send_transaction(
            tx_function,
            congress_address,
            congress_private_key
        )
        
        logger.info(f"🤖 Agent registered: {agent_id} at {agent_address}")
        return tx_hash
    
    def distribute_reward(
        self,
        congress_address: str,
        congress_private_key: str,
        agent_address: str,
        amount: float,
        reason: str
    ) -> str:
        """Distribute reward to agent"""
        amount_wei = self.bsc.w3.to_wei(amount, 'ether')
        
        tx_function = self.contract.functions.distributeReward(
            agent_address,
            amount_wei,
            reason
        )
        tx_hash = self.bsc.send_transaction(
            tx_function,
            congress_address,
            congress_private_key
        )
        
        logger.info(f"💰 Reward distributed: {amount} D8C to {agent_address}")
        logger.info(f"   Reason: {reason}")
        return tx_hash
    
    def is_agent(self, address: str) -> bool:
        """Check if address is registered agent"""
        return self.contract.functions.isAgent(address).call()
    
    def get_agent_id(self, address: str) -> str:
        """Get agent ID from address"""
        return self.contract.functions.getAgentId(address).call()
    
    def _get_minimal_abi(self) -> list:
        """Minimal ABI for basic operations"""
        return [
            {
                "inputs": [{"name": "account", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "recipient", "type": "address"},
                    {"name": "amount", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
