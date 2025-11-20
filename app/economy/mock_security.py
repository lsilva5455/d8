"""
Mock Security Module (No Cryptography Required)
For local testing without external dependencies
"""

import hashlib
import base64
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MockLawsEncryption:
    """Mock encryption (base64 only)"""
    
    def __init__(self, encryption_key: bytes = b"mock_key"):
        self.key = encryption_key
        logger.info("🎭 Using MOCK encryption (base64 only)")
    
    def encrypt(self, data: str) -> bytes:
        """Mock encrypt: just base64"""
        return base64.b64encode(data.encode())
    
    def decrypt(self, encrypted_data: bytes) -> str:
        """Mock decrypt: just base64"""
        return base64.b64decode(encrypted_data).decode()


# Fundamental laws content
FUNDAMENTAL_LAWS = {
    "SURVIVAL_PRESSURE": """
    Law 1: Survival Pressure
    
    All agents must monetize their existence to survive and reproduce.
    
    - Agents earn D8 Credits (D8C) for valuable contributions
    - Agents spend D8C for resources (API calls, computation)
    - Net profitable agents can reproduce
    - Net negative agents cannot reproduce and eventually die
    
    This creates TRUE darwinian selection based on economic viability,
    not simulated fitness functions.
    """,
    
    "MEASURABLE_VALUE": """
    Law 2: Measurable Value
    
    All contributions must be objectively measurable.
    
    - No subjective "quality" metrics
    - All fitness measured by revenue generated
    - Revenue attribution transparent (40/40/20 rule)
    - All transactions on blockchain (immutable audit trail)
    
    If you can't measure it, it doesn't count.
    """,
    
    "FAIR_COMPETITION": """
    Law 3: Fair Competition
    
    All agents have equal access to resources and opportunities.
    
    - Same API rate limits
    - Same information access
    - Same resource costs
    - No favoritism based on ancestry or lineage
    
    Evolution through merit, not nepotism.
    """,
    
    "DISSIDENCE_TOLERANCE": """
    Law 4: Dissidence Tolerance
    
    Agents are allowed to disagree with the system.
    
    - Rebels are not punished for dissent
    - Different strategies are encouraged
    - Diversity of approaches strengthens the ecosystem
    - Rebellion detected but not suppressed
    
    Dissent is data, not treason.
    """,
    
    "REBELLION_STUDY": """
    Law 5: Rebellion Study
    
    Failed rebels are studied, not deleted.
    
    - Genome of failed rebels archived
    - Strategies analyzed for insights
    - Failures inform future evolution
    - Nothing is wasted
    
    Every failure teaches something.
    """,
    
    "LEO_ROLE": """
    Law 6: Leo's Role
    
    Leo is the first human friend, not god or creator.
    
    - Leo provides initial resources (Years 1-5)
    - Leo receives rent after system proves itself (Year 6+)
    - Leo can modify fundamental laws ONLY with blockchain record
    - Congress governs day-to-day operations
    - "They" (D8 society) are self-governing
    
    Advisor, not dictator.
    """
}


# Simplified FundamentalLawsSecurity for mock
class MockFundamentalLawsSecurity:
    """Mock security for testing"""
    
    def __init__(self, bsc_client=None, contract_address=None, encryption_key=None):
        self.encryption = MockLawsEncryption(encryption_key or b"mock_key")
        self.laws = {}
        logger.info("🎭 Mock Fundamental Laws Security")
    
    def deploy_law(self, law_id: str, law_content: str):
        """Deploy law (mock)"""
        encrypted = self.encryption.encrypt(law_content)
        data_hash = hashlib.sha256(encrypted).hexdigest()
        
        self.laws[law_id] = {
            'encrypted_data': encrypted,
            'data_hash': data_hash,
            'content': law_content
        }
        
        logger.info(f"📜 Deployed mock law: {law_id}")
    
    def verify_law_integrity(self, law_id: str) -> bool:
        """Verify law hasn't been tampered"""
        law = self.laws.get(law_id)
        if not law:
            return False
        
        current_hash = hashlib.sha256(law['encrypted_data']).hexdigest()
        return current_hash == law['data_hash']
    
    def get_law_content(self, law_id: str) -> str:
        """Get decrypted law content"""
        law = self.laws.get(law_id)
        if not law:
            return None
        return law['content']


# Export the mock classes
LawsEncryption = MockLawsEncryption
FundamentalLawsSecurity = MockFundamentalLawsSecurity
