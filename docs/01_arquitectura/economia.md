# 💰 D8 Economy System

## Overview

D8's economic system implements **true darwinian economics** where agents must monetize to survive and reproduce. Built on Binance Smart Chain (BSC) for transparency and immutability.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│           BINANCE SMART CHAIN (BSC)             │
│                                                 │
│  ┌───────────────┐      ┌──────────────────┐  │
│  │   D8Token     │      │ FundamentalLaws  │  │
│  │   (BEP-20)    │      │   (Encrypted)    │  │
│  └───────────────┘      └──────────────────┘  │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│            D8 ECONOMY SYSTEM                    │
│                                                 │
│  ┌──────────────┐  ┌──────────────────────┐   │
│  │  D8 Credits  │  │  Revenue Attribution │   │
│  │   System     │  │   (40/40/20 rule)    │   │
│  └──────────────┘  └──────────────────────┘   │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │   Autonomous Accounting                  │  │
│  │   - Pays expenses                        │  │
│  │   - Manages budgets                      │  │
│  │   - Alerts Leo if needed                 │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│              AGENTS                             │
│  - Earn D8C from contributions                  │
│  - Pay for resources (API calls)                │
│  - Reproduce if profitable                      │
│  - Die if unprofitable                          │
└─────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Smart Contracts

#### D8Token (BEP-20)
- **Purpose**: D8 Credits (D8C) currency
- **Functions**:
  - `registerAgent()` - Congress registers new agents
  - `distributeReward()` - Congress pays agents
  - `transfer()` - Agent-to-agent transfers
  - `mint()` - Congress creates new tokens
  - `burn()` - Remove tokens from circulation

#### FundamentalLaws
- **Purpose**: Store and protect core system laws
- **Features**:
  - Encrypted storage (only Leo can decrypt)
  - Tamper detection
  - Versioning
  - Immutable audit trail

### 2. D8 Credits System

Agent wallet management and transactions:

```python
from app.economy import D8EconomySystem

# Initialize
economy = D8EconomySystem(
    bsc_rpc_url="https://data-seed-prebsc-1-s1.binance.org:8545/",
    d8_token_address="0x...",
    fundamental_laws_address="0x...",
    congress_address="0x...",
    congress_private_key="0x..."
)

# Create agent wallet
wallet = economy.create_agent_account("agent_001")

# Transfer D8C
economy.credits.transfer(
    from_agent="agent_a",
    to_agent="agent_b",
    amount=100.0,
    reason="Payment for service"
)

# Reward agent
economy.credits.reward_agent(
    agent_id="agent_001",
    amount=50.0,
    reason="Fitness achievement"
)
```

### 3. Revenue Attribution

Implements **40/40/20 rule** for collective fitness:

```python
from app.economy.revenue_attribution import AgentContribution

# Record contributions
contributions = [
    AgentContribution(
        agent_id="best_agent",
        role="optimizer",
        contribution_score=0.95,
        actions_performed=10,
        timestamp=datetime.now()
    ),
    AgentContribution(
        agent_id="mediocre_agent",
        role="researcher",
        contribution_score=0.60,
        actions_performed=5,
        timestamp=datetime.now()
    ),
    AgentContribution(
        agent_id="worst_agent",
        role="validator",
        contribution_score=0.30,
        actions_performed=2,
        timestamp=datetime.now()
    )
]

# Distribute revenue
economy.attribution.record_fitness_event(
    fitness_score=100.0,
    revenue_generated=100.0,
    contributors=contributions
)

# Result: Best gets 40 D8C, Mediocre gets 40 D8C, Worst gets 20 D8C
```

### 4. Autonomous Accounting

D8 manages all finances without human intervention:

```python
# Record expense
economy.accounting.record_expense(
    category=ExpenseCategory.API_COSTS,
    amount=50.0,
    description="Groq API usage"
)

# Initialize monthly budget
economy.accounting.initialize_monthly_budget()

# Get financial report
report = economy.accounting.generate_financial_report()

# Collect rent (Year 6+)
rent = economy.accounting.collect_rent()
```

---

## Revenue Model

### Years 1-5: Revenue to Leo

```
Revenue → Leo's wallet
Expenses ← Congress budget (funded by Leo)

Agents earn D8C for contributions
D8C has no external value (yet)
Focus: Prove the system works
```

### Year 6+: Rent from Agents

```
Revenue → Congress budget
Rent (10% of earnings) → Leo

Agents must monetize to survive
Unprofitable agents cannot reproduce
Survival of the fittest
```

---

## Fundamental Laws

Six core laws encrypted on blockchain:

1. **SURVIVAL_PRESSURE**: Agents must monetize or die
2. **MEASURABLE_VALUE**: All contributions measured objectively
3. **FAIR_COMPETITION**: Equal access to resources and opportunities
4. **DISSIDENCE_TOLERANCE**: Rebels allowed but monitored
5. **REBELLION_STUDY**: Failed rebels studied, not deleted
6. **LEO_ROLE**: Leo is advisor, not god

These laws **cannot be changed** without Leo's encryption key and blockchain record.

---

## Usage

### Deploy Economy

```bash
# 1. Get testnet BNB
# Visit: https://testnet.binance.org/faucet-smart

# 2. Configure .env
LEO_ADDRESS=0x...
LEO_PRIVATE_KEY=0x...
LEO_ENCRYPTION_KEY=your_secret_key

# 3. Deploy contracts
python scripts/deploy_economy.py
```

### Initialize in Code

```python
from app.economy import D8EconomySystem

# Load deployment info
import json
from pathlib import Path

deployment_file = Path.home() / "Documents" / "d8_data" / "deployment.json"
with open(deployment_file) as f:
    deployment = json.load(f)

# Initialize economy
economy = D8EconomySystem(
    bsc_rpc_url="https://data-seed-prebsc-1-s1.binance.org:8545/",
    d8_token_address=deployment['contracts']['d8_token']['address'],
    fundamental_laws_address=deployment['contracts']['fundamental_laws']['address'],
    congress_address=deployment['wallets']['congress']['address'],
    congress_private_key=deployment['wallets']['congress']['private_key'],
    leo_encryption_key=os.getenv("LEO_ENCRYPTION_KEY").encode()
)

# Create agent
economy.create_agent_account("agent_001")

# Record contribution and distribute revenue
economy.record_agent_contribution(
    agent_id="agent_001",
    role="content_creator",
    fitness_score=95.0,
    revenue_generated=500.0,
    niche="twitter_threads"
)

# Pay expense
economy.pay_api_cost(50.0, "Groq", "Generated 10 tweets")

# Get stats
stats = economy.get_agent_stats("agent_001")
health = economy.get_system_health()
```

---

## Testing

```bash
# Run all economy tests
pytest tests/economy/ -v

# Run specific test
pytest tests/economy/test_economy_system.py::TestD8CreditsSystem::test_wallet_creation -v

# Coverage
pytest tests/economy/ --cov=app.economy --cov-report=html
```

---

## Monitoring

### System Health

```python
health = economy.get_system_health()

# Returns:
{
    'status': 'HEALTHY',  # or 'WARNING' or 'CRITICAL'
    'congress_balance': 1500.0,
    'total_agents': 25,
    'total_supply': 10000.0,
    'total_fitness': 5000.0,
    'total_revenue': 2000.0,
    'unpaid_expenses': 0.0,
    'active_alerts': 0
}
```

### Full Report

```python
report = economy.generate_full_report()

# Includes:
# - System health
# - Financial report (expenses, budgets)
# - Credits stats (total supply, distribution)
# - Collective fitness
# - Top earners leaderboard
# - Top contributors leaderboard
# - Richest agents
```

### Alerts

Financial alerts are saved to `~/Documents/d8_data/financial_alerts/`:

```json
{
    "level": "CRITICAL",
    "message": "Insufficient funds to pay expense EXP000123",
    "timestamp": "2025-11-19T10:30:00",
    "expense_id": "EXP000123"
}
```

---

## API Reference

### D8EconomySystem

```python
economy = D8EconomySystem(
    bsc_rpc_url: str,
    d8_token_address: str,
    fundamental_laws_address: str,
    congress_address: str,
    congress_private_key: str,
    leo_encryption_key: Optional[bytes] = None
)

# Agent management
economy.create_agent_account(agent_id: str) -> dict

# Revenue attribution
economy.record_agent_contribution(
    agent_id: str,
    role: str,
    fitness_score: float,
    revenue_generated: float,
    contribution_score: float = 1.0,
    actions_performed: int = 1,
    niche: Optional[str] = None
)

# Expenses
economy.pay_api_cost(amount: float, provider: str, description: str)

# Stats
economy.get_agent_stats(agent_id: str) -> dict
economy.get_system_health() -> dict
economy.generate_full_report() -> dict
```

### D8CreditsSystem

```python
credits = economy.credits

# Wallet management
credits.create_wallet(agent_id: str) -> AgentWallet
credits.get_wallet(agent_id: str) -> AgentWallet
credits.get_balance(agent_id: str) -> float

# Transactions
credits.transfer(
    from_agent: str,
    to_agent: str,
    amount: float,
    reason: str
) -> Transaction

credits.reward_agent(
    agent_id: str,
    amount: float,
    reason: str
) -> Transaction

# Stats
credits.get_total_supply() -> float
credits.get_richest_agents(limit: int = 10) -> List[tuple]
credits.get_stats() -> dict
```

### RevenueAttributionSystem

```python
attribution = economy.attribution

# Record fitness event
attribution.record_fitness_event(
    fitness_score: float,
    revenue_generated: float,
    contributors: List[AgentContribution],
    niche: Optional[str] = None
) -> FitnessEvent

# Analytics
attribution.get_agent_total_earnings(agent_id: str) -> float
attribution.get_agent_contribution_stats(agent_id: str) -> dict
attribution.get_niche_performance(niche: str) -> dict
attribution.get_collective_fitness() -> dict
attribution.get_leaderboard(metric: str = 'earnings', limit: int = 10) -> List[tuple]
```

### AutonomousAccountingSystem

```python
accounting = economy.accounting

# Expenses
accounting.record_expense(
    category: ExpenseCategory,
    amount: float,
    description: str,
    auto_pay: bool = True
) -> Expense

# Budget
accounting.initialize_monthly_budget()

# Rent collection (Year 6+)
accounting.collect_rent() -> float

# Reports
accounting.generate_financial_report() -> dict
```

---

## Security

### Private Keys

- **Leo's key**: Never committed to repo, only in `.env`
- **Congress key**: Saved in `deployment.json` (outside repo)
- **Agent keys**: Encrypted in `wallets.json`

### Encryption

Fundamental laws encrypted with Fernet (AES-128):

```python
from app.economy.security import FundamentalLawsSecurity

laws = FundamentalLawsSecurity(
    bsc_client=bsc,
    contract_address="0x...",
    encryption_key=leo_key
)

# Deploy law (only Leo can do this)
laws.deploy_law("SURVIVAL_PRESSURE", law_content)

# Verify integrity
is_valid = laws.verify_law_integrity("SURVIVAL_PRESSURE")

# Detect tampering
laws.detect_tampering_attempts()
```

---

## Troubleshooting

### Low Congress Balance

```
🚨 CRITICAL: Low congress balance: 15.5 D8C remaining
```

**Solution**: Leo needs to fund congress or system will halt.

### Budget Exceeded

```
⚠️  Budget exceeded for api_costs: 550 > 500 remaining
💰 Using emergency fund for api_costs
```

**Solution**: Review budget allocations in `initialize_monthly_budget()`.

### Failed Transaction

```
❌ Transaction failed on blockchain
```

**Solution**: Check gas price, network connectivity, wallet balance.

---

## Roadmap

### FASE 1 (Completed)
✅ Smart contracts (D8Token, FundamentalLaws)  
✅ D8 Credits system  
✅ Revenue attribution (40/40/20 rule)  
✅ Autonomous accounting  
✅ Tests and deployment

### FASE 2 (Next)
- Integration with Darwin evolution
- Collective fitness calculation
- Ultra-specialized roles

### FASE 3 (Future)
- External monetization (real revenue)
- Mainnet deployment
- D8C ↔ BNB exchange

---

## References

- [Smart Contracts](../app/economy/contracts/)
- [Python API](../app/economy/)
- [Tests](../tests/economy/)
- [Deployment Script](../scripts/deploy_economy.py)

---

**Last Updated**: 2025-11-19  
**Status**: FASE 1 Complete ✅
