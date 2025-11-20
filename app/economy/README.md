# D8 Economy System

**Autonomous economic system for D8 agent society**

---

## Quick Start

### Installation

```bash
pip install web3 eth-account py-solc-x cryptography
```

### Basic Usage

```python
from app.economy import D8EconomySystem

# Initialize (after deployment)
economy = D8EconomySystem(
    bsc_rpc_url="https://data-seed-prebsc-1-s1.binance.org:8545/",
    d8_token_address="0x...",
    fundamental_laws_address="0x...",
    congress_address="0x...",
    congress_private_key="0x..."
)

# Create agent
economy.create_agent_account("agent_001")

# Record contribution
economy.record_agent_contribution(
    agent_id="agent_001",
    role="researcher",
    fitness_score=95.0,
    revenue_generated=500.0
)

# Pay expense
economy.pay_api_cost(50.0, "Groq", "API usage")

# Get stats
stats = economy.get_agent_stats("agent_001")
```

---

## Components

### Smart Contracts (`contracts/`)

- **D8Token.sol**: BEP-20 token for D8 credits
- **FundamentalLaws.sol**: Encrypted laws storage

### Python Modules

- **blockchain_client.py**: BSC connection and transactions
- **security.py**: Laws encryption and integrity
- **d8_credits.py**: Agent wallets and transfers
- **revenue_attribution.py**: 40/40/20 distribution
- **accounting.py**: Autonomous expense management
- **__init__.py**: Integrated system

---

## Architecture

```
BSC Blockchain
    │
    ├─► D8Token (BEP-20)
    │   └─► Agent credits
    │
    └─► FundamentalLaws
        └─► Encrypted rules

        ▼

D8 Economy System
    │
    ├─► D8CreditsSystem
    │   └─► Wallets, transfers, rewards
    │
    ├─► RevenueAttribution
    │   └─► 40/40/20 rule
    │
    └─► AutonomousAccounting
        └─► Expenses, budgets, alerts
```

---

## Revenue Model

### Years 1-5: Revenue to Leo
- External revenue → Leo
- Congress budget → Funded by Leo
- Agents earn D8C (no external value yet)

### Year 6+: Rent from Agents
- External revenue → Congress
- Agents pay 10% rent → Leo
- Survival pressure: Unprofitable agents die

---

## Testing

```bash
# Run all tests
pytest tests/economy/ -v

# With coverage
pytest tests/economy/ --cov=app.economy --cov-report=html
```

---

## Deployment

```bash
# Get testnet BNB
# https://testnet.binance.org/faucet-smart

# Configure environment
echo "LEO_ADDRESS=0x..." >> .env
echo "LEO_PRIVATE_KEY=0x..." >> .env

# Deploy
python scripts/deploy_economy.py
```

---

## Documentation

- [Full Architecture](../../docs/01_arquitectura/economia.md)
- [FASE 1 Report](../../docs/07_reportes/FASE_1_COMPLETADA.md)
- [Visual Report](../../docs/07_reportes/visualizations/FASE_1_VISUAL_REPORT.md)

---

## API Reference

### D8EconomySystem

```python
economy.create_agent_account(agent_id: str) -> dict
economy.record_agent_contribution(**kwargs)
economy.pay_api_cost(amount: float, provider: str, description: str)
economy.get_agent_stats(agent_id: str) -> dict
economy.get_system_health() -> dict
economy.generate_full_report() -> dict
```

### D8CreditsSystem

```python
credits.create_wallet(agent_id: str) -> AgentWallet
credits.transfer(from_agent, to_agent, amount, reason) -> Transaction
credits.reward_agent(agent_id, amount, reason) -> Transaction
credits.get_balance(agent_id: str) -> float
```

### RevenueAttributionSystem

```python
attribution.record_fitness_event(fitness_score, revenue, contributors) -> FitnessEvent
attribution.get_agent_contribution_stats(agent_id) -> dict
attribution.get_leaderboard(metric='earnings', limit=10) -> List[tuple]
```

### AutonomousAccountingSystem

```python
accounting.record_expense(category, amount, description) -> Expense
accounting.initialize_monthly_budget()
accounting.collect_rent() -> float
accounting.generate_financial_report() -> dict
```

---

**Version**: 1.0.0  
**Status**: Production Ready (Testnet)  
**License**: MIT
