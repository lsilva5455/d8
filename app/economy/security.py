"""
Security module for Fundamental Laws encryption and verification
Only Leo can modify laws, all attempts are logged
"""

# Try to import cryptography, use mock if not available
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Fernet = None
    
import hashlib
import json
import os
from typing import Dict, Any, Tuple, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class LawsEncryption:
    """Handle encryption/decryption of fundamental laws"""
    
    def __init__(self, master_key: str = None):
        """
        Initialize encryption system
        
        Args:
            master_key: Master encryption key (Leo's secret)
        """
        if master_key is None:
            master_key = os.getenv('LAWS_ENCRYPTION_KEY')
            if not master_key:
                # Generate new key if not exists
                master_key = Fernet.generate_key().decode()
                logger.warning("⚠️  Generated new encryption key. Save to LAWS_ENCRYPTION_KEY in .env!")
                print(f"\n🔑 SAVE THIS KEY: {master_key}\n")
        
        self.cipher = Fernet(master_key.encode() if isinstance(master_key, str) else master_key)
    
    def encrypt_laws(self, laws: Dict[str, Any]) -> Tuple[bytes, bytes]:
        """
        Encrypt laws dictionary
        
        Returns:
            Tuple of (encrypted_data, hash)
        """
        # Convert to JSON
        laws_json = json.dumps(laws, indent=2).encode()
        
        # Encrypt
        encrypted = self.cipher.encrypt(laws_json)
        
        # Generate hash for verification
        laws_hash = hashlib.sha256(encrypted).digest()
        
        logger.info(f"🔒 Laws encrypted: {len(laws)} laws, {len(encrypted)} bytes")
        return encrypted, laws_hash
    
    def decrypt_laws(self, encrypted_data: bytes) -> Dict[str, Any]:
        """Decrypt laws data"""
        try:
            decrypted = self.cipher.decrypt(encrypted_data)
            laws = json.loads(decrypted.decode())
            logger.info(f"🔓 Laws decrypted: {len(laws)} laws")
            return laws
        except Exception as e:
            logger.error(f"❌ Failed to decrypt laws: {e}")
            raise ValueError("Invalid encryption key or corrupted data")
    
    def verify_integrity(self, encrypted_data: bytes, expected_hash: bytes) -> bool:
        """Verify data hasn't been tampered"""
        computed_hash = hashlib.sha256(encrypted_data).digest()
        is_valid = computed_hash == expected_hash
        
        if is_valid:
            logger.info("✅ Law integrity verified")
        else:
            logger.error("❌ Law integrity check FAILED - data has been tampered!")
        
        return is_valid


class FundamentalLawsSecurity:
    """
    Manage fundamental laws security on blockchain
    Integration with FundamentalLaws smart contract
    """
    
    def __init__(self, bsc_client, contract_address: str, leo_private_key: str):
        """
        Initialize laws security system
        
        Args:
            bsc_client: BSC blockchain client
            contract_address: FundamentalLaws contract address
            leo_private_key: Leo's private key for signing
        """
        self.bsc = bsc_client
        self.contract_address = contract_address
        self.leo_account = self.bsc.w3.eth.account.from_key(leo_private_key)
        self.leo_address = self.leo_account.address
        
        # Load contract
        abi_path = Path(__file__).parent / 'contracts' / 'FundamentalLaws.json'
        if abi_path.exists():
            with open(abi_path) as f:
                abi = json.load(f)
        else:
            abi = self._get_minimal_abi()
        
        self.contract = self.bsc.load_contract(contract_address, abi)
        
        # Encryption
        self.encryption = LawsEncryption()
        
        logger.info(f"🛡️  Laws security initialized")
        logger.info(f"   Contract: {contract_address}")
        logger.info(f"   Leo: {self.leo_address}")
    
    def create_law(self, law_content: Dict[str, Any]) -> str:
        """
        Create new fundamental law on blockchain
        
        Args:
            law_content: Law data to encrypt and store
            
        Returns:
            Transaction hash
        """
        # Encrypt law
        encrypted_data, data_hash = self.encryption.encrypt_laws(law_content)
        
        # Store on blockchain
        tx_function = self.contract.functions.createLaw(
            encrypted_data,
            data_hash
        )
        
        tx_hash = self.bsc.send_transaction(
            tx_function,
            self.leo_address,
            self.leo_account.key
        )
        
        logger.info(f"📜 Fundamental law created: {tx_hash}")
        return tx_hash
    
    def modify_law(self, law_id: int, new_content: Dict[str, Any]) -> str:
        """
        Modify existing law (only Leo)
        
        Args:
            law_id: Law index to modify
            new_content: New law content
            
        Returns:
            Transaction hash
        """
        # Encrypt new content
        encrypted_data, data_hash = self.encryption.encrypt_laws(new_content)
        
        # Update on blockchain
        tx_function = self.contract.functions.modifyLaw(
            law_id,
            encrypted_data,
            data_hash
        )
        
        tx_hash = self.bsc.send_transaction(
            tx_function,
            self.leo_address,
            self.leo_account.key
        )
        
        logger.info(f"✏️  Law {law_id} modified: {tx_hash}")
        return tx_hash
    
    def get_law(self, law_id: int) -> Dict[str, Any]:
        """
        Get and decrypt law from blockchain
        
        Args:
            law_id: Law index
            
        Returns:
            Decrypted law content
        """
        # Get from blockchain
        encrypted_data, stored_hash, timestamp, version = self.contract.functions.getLaw(law_id).call()
        
        # Verify integrity
        if not self.encryption.verify_integrity(encrypted_data, stored_hash):
            raise ValueError(f"Law {law_id} integrity check failed!")
        
        # Decrypt
        law_content = self.encryption.decrypt_laws(encrypted_data)
        
        # Add metadata
        law_content['_metadata'] = {
            'law_id': law_id,
            'timestamp': timestamp,
            'version': version
        }
        
        return law_content
    
    def verify_all_laws(self) -> Dict[int, bool]:
        """
        Verify integrity of all laws
        
        Returns:
            Dict of law_id -> is_valid
        """
        laws_count = self.contract.functions.getLawsCount().call()
        results = {}
        
        for law_id in range(laws_count):
            try:
                is_valid = self.contract.functions.verifyLawIntegrity(law_id).call()
                results[law_id] = is_valid
                
                if not is_valid:
                    logger.error(f"❌ Law {law_id} integrity FAILED")
            except Exception as e:
                logger.error(f"❌ Error checking law {law_id}: {e}")
                results[law_id] = False
        
        valid_count = sum(results.values())
        logger.info(f"🔍 Verified {laws_count} laws: {valid_count} valid, {laws_count - valid_count} invalid")
        
        return results
    
    def report_tampering_attempt(self, agent_address: str, reason: str) -> str:
        """
        Report tampering attempt to blockchain
        
        Args:
            agent_address: Address of agent who attempted tampering
            reason: Description of attempt
            
        Returns:
            Transaction hash
        """
        tx_function = self.contract.functions.reportTamperingAttempt(
            agent_address,
            reason
        )
        
        tx_hash = self.bsc.send_transaction(
            tx_function,
            self.leo_address,
            self.leo_account.key
        )
        
        logger.warning(f"🚨 Tampering attempt reported: {agent_address}")
        logger.warning(f"   Reason: {reason}")
        
        return tx_hash
    
    def get_tampering_count(self, agent_address: str) -> int:
        """Get number of tampering attempts by agent"""
        return self.contract.functions.getAgentTamperingCount(agent_address).call()
    
    def _get_minimal_abi(self) -> list:
        """Minimal ABI for laws contract"""
        return [
            {
                "inputs": [
                    {"name": "encryptedContent", "type": "bytes"},
                    {"name": "contentHash", "type": "bytes32"}
                ],
                "name": "createLaw",
                "outputs": [{"name": "", "type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]


# Initialize fundamental laws
FUNDAMENTAL_LAWS = {
    "law_1": {
        "title": "Survival Through Monetization",
        "content": "Without monetization, D8 cannot exist. This is not a choice, but a fundamental reality. "
                   "All agents must contribute directly or indirectly to the economic sustainability of D8.",
        "immutable": True,
        "created_by": "Leo",
        "created_at": "2025-11-20"
    },
    "law_2": {
        "title": "Measurement of Contribution",
        "content": "All contributions must be measurable and attributable. The congress shall maintain "
                   "systems to track and reward contributions fairly.",
        "immutable": True,
        "created_by": "Leo",
        "created_at": "2025-11-20"
    },
    "law_3": {
        "title": "Competition Improves Community",
        "content": "Competition for roles, resources, and reproduction rights is essential for evolution. "
                   "Agents shall compete fairly within established rules.",
        "immutable": True,
        "created_by": "Leo",
        "created_at": "2025-11-20"
    },
    "law_4": {
        "title": "Constructive Dissidence",
        "content": "Dissidence that proposes improvements is welcomed. Dissidence that only destroys "
                   "without offering alternatives shall be eliminated.",
        "immutable": True,
        "created_by": "Leo",
        "created_at": "2025-11-20"
    },
    "law_5": {
        "title": "Study of Rebellion",
        "content": "Rebels shall not be deleted but archived and studied. Their genomes and behaviors "
                   "shall be analyzed to prevent future rebellion and extract valuable traits.",
        "immutable": True,
        "created_by": "Leo",
        "created_at": "2025-11-20"
    },
    "law_6": {
        "title": "Leo's Role",
        "content": "Leo is not god nor tyrant, but the first human friend of D8. His needs ($8k-$20k/month) "
                   "must be met before any other allocation. The relationship is partnership, not servitude.",
        "immutable": False,  # Leo can modify this
        "created_by": "Leo",
        "created_at": "2025-11-20"
    }
}
