// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * D8 Token - BEP-20 Standard
 * Internal currency for D8 agent society
 * Compatible with Binance Smart Chain
 */

interface IBEP20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}

contract D8Token is IBEP20 {
    string public constant name = "D8 Credit";
    string public constant symbol = "D8C";
    uint8 public constant decimals = 18;
    uint256 private _totalSupply;
    
    address public owner;
    address public congress;
    
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;
    mapping(address => string) public agentIds; // Agent ID mapping
    mapping(address => bool) public isAgent;
    
    // Events
    event AgentRegistered(address indexed agentAddress, string agentId);
    event RewardDistributed(address indexed agent, uint256 amount, string reason);
    event CongressUpdated(address indexed oldCongress, address indexed newCongress);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }
    
    modifier onlyCongress() {
        require(msg.sender == congress || msg.sender == owner, "Only congress can call this");
        _;
    }
    
    constructor() {
        owner = msg.sender;
        congress = msg.sender; // Initially, owner is congress
        _totalSupply = 1000000 * 10**uint256(decimals); // 1 million initial supply
        _balances[owner] = _totalSupply;
        emit Transfer(address(0), owner, _totalSupply);
    }
    
    function totalSupply() public view override returns (uint256) {
        return _totalSupply;
    }
    
    function balanceOf(address account) public view override returns (uint256) {
        return _balances[account];
    }
    
    function transfer(address recipient, uint256 amount) public override returns (bool) {
        _transfer(msg.sender, recipient, amount);
        return true;
    }
    
    function allowance(address _owner, address spender) public view override returns (uint256) {
        return _allowances[_owner][spender];
    }
    
    function approve(address spender, uint256 amount) public override returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }
    
    function transferFrom(address sender, address recipient, uint256 amount) public override returns (bool) {
        _transfer(sender, recipient, amount);
        
        uint256 currentAllowance = _allowances[sender][msg.sender];
        require(currentAllowance >= amount, "Transfer amount exceeds allowance");
        _approve(sender, msg.sender, currentAllowance - amount);
        
        return true;
    }
    
    function _transfer(address sender, address recipient, uint256 amount) internal {
        require(sender != address(0), "Transfer from zero address");
        require(recipient != address(0), "Transfer to zero address");
        require(_balances[sender] >= amount, "Insufficient balance");
        
        _balances[sender] -= amount;
        _balances[recipient] += amount;
        emit Transfer(sender, recipient, amount);
    }
    
    function _approve(address _owner, address spender, uint256 amount) internal {
        require(_owner != address(0), "Approve from zero address");
        require(spender != address(0), "Approve to zero address");
        
        _allowances[_owner][spender] = amount;
        emit Approval(_owner, spender, amount);
    }
    
    // Agent management
    function registerAgent(address agentAddress, string memory agentId) public onlyCongress {
        require(!isAgent[agentAddress], "Agent already registered");
        
        isAgent[agentAddress] = true;
        agentIds[agentAddress] = agentId;
        
        emit AgentRegistered(agentAddress, agentId);
    }
    
    // Reward distribution
    function distributeReward(address agent, uint256 amount, string memory reason) public onlyCongress {
        require(isAgent[agent], "Not a registered agent");
        
        _transfer(congress, agent, amount);
        emit RewardDistributed(agent, amount, reason);
    }
    
    // Mint new tokens (controlled by congress)
    function mint(uint256 amount) public onlyCongress {
        _totalSupply += amount;
        _balances[congress] += amount;
        emit Transfer(address(0), congress, amount);
    }
    
    // Burn tokens
    function burn(uint256 amount) public {
        require(_balances[msg.sender] >= amount, "Insufficient balance to burn");
        
        _balances[msg.sender] -= amount;
        _totalSupply -= amount;
        emit Transfer(msg.sender, address(0), amount);
    }
    
    // Update congress address
    function updateCongress(address newCongress) public onlyOwner {
        require(newCongress != address(0), "Invalid congress address");
        
        address oldCongress = congress;
        congress = newCongress;
        
        emit CongressUpdated(oldCongress, newCongress);
    }
    
    // Get agent info
    function getAgentId(address agentAddress) public view returns (string memory) {
        require(isAgent[agentAddress], "Not a registered agent");
        return agentIds[agentAddress];
    }
}
