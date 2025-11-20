// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * Fundamental Laws Contract
 * Stores encrypted fundamental laws of D8 society
 * Only Leo (owner) can modify
 * Immutable on blockchain, traceable modifications
 */

contract FundamentalLaws {
    address public owner;
    address public congress;
    
    struct Law {
        bytes encryptedContent;
        bytes32 contentHash;
        uint256 timestamp;
        uint256 version;
    }
    
    struct ModificationAttempt {
        address attemptedBy;
        uint256 timestamp;
        string reason;
    }
    
    Law[] public laws;
    ModificationAttempt[] public tamperingAttempts;
    
    mapping(uint256 => bool) public isActive;
    mapping(address => uint256) public attemptCount;
    
    event LawCreated(uint256 indexed lawId, bytes32 contentHash, uint256 version);
    event LawModified(uint256 indexed lawId, bytes32 newHash, uint256 newVersion);
    event TamperingDetected(address indexed agent, uint256 timestamp);
    event SecurityAudit(string message, uint256 timestamp);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only Leo can modify laws");
        _;
    }
    
    modifier onlyCongress() {
        require(msg.sender == congress || msg.sender == owner, "Only congress can call");
        _;
    }
    
    constructor() {
        owner = msg.sender;
        congress = msg.sender;
    }
    
    // Create new fundamental law
    function createLaw(bytes memory encryptedContent, bytes32 contentHash) public onlyOwner returns (uint256) {
        Law memory newLaw = Law({
            encryptedContent: encryptedContent,
            contentHash: contentHash,
            timestamp: block.timestamp,
            version: 1
        });
        
        laws.push(newLaw);
        uint256 lawId = laws.length - 1;
        isActive[lawId] = true;
        
        emit LawCreated(lawId, contentHash, 1);
        return lawId;
    }
    
    // Modify existing law (only Leo)
    function modifyLaw(uint256 lawId, bytes memory newEncryptedContent, bytes32 newContentHash) public onlyOwner {
        require(lawId < laws.length, "Law does not exist");
        require(isActive[lawId], "Law is not active");
        
        Law storage law = laws[lawId];
        law.encryptedContent = newEncryptedContent;
        law.contentHash = newContentHash;
        law.timestamp = block.timestamp;
        law.version += 1;
        
        emit LawModified(lawId, newContentHash, law.version);
        emit SecurityAudit("Law modified by owner", block.timestamp);
    }
    
    // Verify law integrity
    function verifyLawIntegrity(uint256 lawId) public view returns (bool) {
        require(lawId < laws.length, "Law does not exist");
        
        Law memory law = laws[lawId];
        bytes32 computedHash = keccak256(law.encryptedContent);
        
        return computedHash == law.contentHash;
    }
    
    // Get law (encrypted)
    function getLaw(uint256 lawId) public view returns (bytes memory, bytes32, uint256, uint256) {
        require(lawId < laws.length, "Law does not exist");
        require(isActive[lawId], "Law is not active");
        
        Law memory law = laws[lawId];
        return (law.encryptedContent, law.contentHash, law.timestamp, law.version);
    }
    
    // Get all laws count
    function getLawsCount() public view returns (uint256) {
        return laws.length;
    }
    
    // Report tampering attempt (called by agents or congress)
    function reportTamperingAttempt(address agent, string memory reason) public onlyCongress {
        ModificationAttempt memory attempt = ModificationAttempt({
            attemptedBy: agent,
            timestamp: block.timestamp,
            reason: reason
        });
        
        tamperingAttempts.push(attempt);
        attemptCount[agent] += 1;
        
        emit TamperingDetected(agent, block.timestamp);
        emit SecurityAudit(reason, block.timestamp);
    }
    
    // Get tampering attempts count for agent
    function getAgentTamperingCount(address agent) public view returns (uint256) {
        return attemptCount[agent];
    }
    
    // Get total tampering attempts
    function getTotalTamperingAttempts() public view returns (uint256) {
        return tamperingAttempts.length;
    }
    
    // Update congress address
    function updateCongress(address newCongress) public onlyOwner {
        require(newCongress != address(0), "Invalid congress address");
        congress = newCongress;
    }
    
    // Deactivate law (not delete, for historical record)
    function deactivateLaw(uint256 lawId) public onlyOwner {
        require(lawId < laws.length, "Law does not exist");
        isActive[lawId] = false;
        emit SecurityAudit("Law deactivated", block.timestamp);
    }
}
