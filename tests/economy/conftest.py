"""
Pytest Configuration & Fixtures - D8 Economy Tests
===================================================

Fixtures reutilizables para tests del sistema económico.

Este archivo define fixtures compartidas entre:
- test_economy_system.py (sistema real con blockchain)
- test_mock_economy.py (sistema mock sin dependencias)

Fixtures disponibles:
- mock_economy: Sistema mock completo
- fresh_blockchain: Blockchain limpio
- three_agents: 3 agentes pre-registrados
- sample_contributions: Contribuciones de ejemplo
- funded_agent: Agente con balance inicial

Uso:
    def test_example(mock_economy, three_agents):
        # Fixtures inyectadas automáticamente
        assert len(three_agents) == 3

Autor: D8 System
Fecha: 2025-11-20
"""

import pytest
from app.economy.mock_blockchain import (
    create_mock_economy_system,
    MockBSCClient,
    MockD8TokenClient,
    MockBlockchain
)


# ============================================================
# FIXTURES PRINCIPALES
# ============================================================

@pytest.fixture
def mock_economy():
    """
    Fixture: Sistema económico mock completo
    
    Incluye:
    - Credits System (D8CreditsSystem)
    - Attribution System (RevenueAttribution)
    - Accounting System (AutonomousAccounting)
    - Mock Blockchain (sin web3)
    - Mock Security (sin cryptography)
    
    Returns:
        MockEconomySystem: Sistema completo inicializado
        
    Ejemplo:
        def test_balance(mock_economy):
            wallet = mock_economy.credits.create_wallet("agent")
            balance = mock_economy.credits.get_balance(wallet)
            assert balance == 0.0
    """
    return create_mock_economy_system()


@pytest.fixture
def fresh_blockchain():
    """
    Fixture: Blockchain mock limpio sin transacciones previas
    
    Útil para tests que requieren estado inicial limpio.
    
    Returns:
        MockBlockchain: Blockchain vacío sin transacciones
        
    Ejemplo:
        def test_first_transaction(fresh_blockchain):
            assert len(fresh_blockchain.transactions) == 0
    """
    blockchain = MockBlockchain()
    blockchain.transactions = []
    blockchain.balances = {}
    return blockchain


@pytest.fixture
def mock_bsc_client():
    """
    Fixture: Cliente BSC mock
    
    Returns:
        MockBSCClient: Cliente para crear cuentas y enviar transacciones
        
    Ejemplo:
        def test_account_creation(mock_bsc_client):
            account = mock_bsc_client.create_account()
            assert account['address'].startswith('0x')
    """
    return MockBSCClient()


@pytest.fixture
def mock_token_client(mock_bsc_client):
    """
    Fixture: Cliente D8Token mock
    
    Args:
        mock_bsc_client: Cliente BSC inyectado automáticamente
    
    Returns:
        MockD8TokenClient: Cliente para operaciones con D8Token
        
    Ejemplo:
        def test_token_transfer(mock_token_client):
            agent = mock_token_client.bsc_client.create_account()['address']
            mock_token_client.register_agent(agent, "test_agent")
    """
    return MockD8TokenClient(mock_bsc_client, "0xMOCKTOKEN")


# ============================================================
# FIXTURES DE AGENTES
# ============================================================

@pytest.fixture
def three_agents(mock_economy):
    """
    Fixture: 3 agentes registrados con roles típicos
    
    Roles:
    - researcher: Agente de investigación
    - optimizer: Agente de optimización
    - validator: Agente de validación
    
    Args:
        mock_economy: Sistema económico mock
    
    Returns:
        dict: {"researcher": "0x...", "optimizer": "0x...", "validator": "0x..."}
        
    Ejemplo:
        def test_distribution(mock_economy, three_agents):
            researcher_id = three_agents["researcher"]
            balance = mock_economy.credits.get_balance(researcher_id)
    """
    agents = {}
    roles = ["researcher", "optimizer", "validator"]
    
    for role in roles:
        agent_id = mock_economy.credits.create_wallet(role)
        agents[role] = agent_id
    
    return agents


@pytest.fixture
def funded_agent(mock_economy):
    """
    Fixture: Agente con balance inicial de 1000 D8C
    
    Args:
        mock_economy: Sistema económico mock
    
    Returns:
        str: Agent ID con 1000 D8C en balance
        
    Ejemplo:
        def test_spending(mock_economy, funded_agent):
            balance = mock_economy.credits.get_balance(funded_agent)
            assert balance == 1000.0
    """
    agent_id = mock_economy.credits.create_wallet("funded_agent")
    mock_economy.credits.token_client.distribute_reward(
        agent_id, 
        1000.0, 
        "Initial funding"
    )
    return agent_id


@pytest.fixture
def agent_pair(mock_economy):
    """
    Fixture: Par de agentes para tests de transferencias
    
    Returns:
        tuple: (sender_id, receiver_id)
        - sender tiene 500 D8C
        - receiver tiene 0 D8C
        
    Ejemplo:
        def test_transfer(mock_economy, agent_pair):
            sender, receiver = agent_pair
            mock_economy.credits.transfer(sender, receiver, 100.0)
    """
    sender = mock_economy.credits.create_wallet("sender")
    receiver = mock_economy.credits.create_wallet("receiver")
    
    # Dar fondos al sender
    mock_economy.credits.token_client.distribute_reward(
        sender, 
        500.0, 
        "Initial funds"
    )
    
    return (sender, receiver)


# ============================================================
# FIXTURES DE DATOS DE PRUEBA
# ============================================================

@pytest.fixture
def sample_contributions(three_agents):
    """
    Fixture: Lista de contribuciones de ejemplo para tests de attribution
    
    Args:
        three_agents: Dict con 3 agentes registrados
    
    Returns:
        list: Contribuciones con scores y action counts
        
    Ejemplo:
        def test_distribution(mock_economy, sample_contributions):
            event = mock_economy.attribution.record_fitness_event(
                event_type="test",
                fitness_score=90.0,
                niche="test_niche",
                contributions=sample_contributions
            )
    """
    return [
        {
            "agent_id": three_agents["researcher"],
            "contribution_score": 0.95,
            "actions_count": 10
        },
        {
            "agent_id": three_agents["optimizer"],
            "contribution_score": 0.60,
            "actions_count": 5
        },
        {
            "agent_id": three_agents["validator"],
            "contribution_score": 0.30,
            "actions_count": 2
        }
    ]


@pytest.fixture
def fitness_event(mock_economy, sample_contributions):
    """
    Fixture: Fitness event pre-registrado
    
    Args:
        mock_economy: Sistema económico mock
        sample_contributions: Contribuciones de ejemplo
    
    Returns:
        dict: Fitness event con event_id y metadata
        
    Ejemplo:
        def test_revenue_distribution(mock_economy, fitness_event):
            distribution = mock_economy.attribution.distribute_revenue(
                event_id=fitness_event['event_id'],
                revenue_amount=100.0
            )
    """
    event = mock_economy.attribution.record_fitness_event(
        event_type="twitter_thread",
        fitness_score=85.0,
        niche="twitter_threads",
        contributions=sample_contributions
    )
    return event


@pytest.fixture
def sample_expenses(mock_economy):
    """
    Fixture: Lista de gastos registrados para tests de accounting
    
    Args:
        mock_economy: Sistema económico mock
    
    Returns:
        list: IDs de expenses registrados
        
    Ejemplo:
        def test_financial_report(mock_economy, sample_expenses):
            report = mock_economy.accounting.get_financial_report()
            assert len(report['expenses_by_category']) > 0
    """
    expenses = []
    
    expense_data = [
        ("api_costs", 50.0, "Groq API: 1000 requests"),
        ("api_costs", 30.0, "Gemini API: 500 requests"),
        ("infrastructure", 20.0, "Server hosting"),
        ("research", 15.0, "Model evaluation")
    ]
    
    for category, amount, description in expense_data:
        expense_id = mock_economy.accounting.record_expense(
            category=category,
            amount=amount,
            description=description
        )
        expenses.append(expense_id)
    
    return expenses


# ============================================================
# FIXTURES DE CONFIGURACIÓN
# ============================================================

@pytest.fixture
def mock_config():
    """
    Fixture: Configuración mock para tests
    
    Returns:
        dict: Configuración de sistema mock
        
    Ejemplo:
        def test_with_config(mock_config):
            assert mock_config['initial_congress_balance'] == 10000.0
    """
    return {
        "initial_congress_balance": 10000.0,
        "monthly_budget": {
            "api_costs": 500.0,
            "infrastructure": 200.0,
            "blockchain": 150.0,
            "congress_operations": 100.0,
            "research": 150.0,
            "development": 75.0,
            "emergency": 25.0
        },
        "attribution_rule": "40_40_20",
        "revenue_mode": "revenue_to_leo"
    }


# ============================================================
# FIXTURES DE UTILIDADES
# ============================================================

@pytest.fixture
def transaction_validator():
    """
    Fixture: Validador de transacciones
    
    Returns:
        callable: Función para validar estructura de transacciones
        
    Ejemplo:
        def test_transaction(mock_economy, transaction_validator):
            tx = mock_economy.credits.token_client.bsc_client.send_transaction(...)
            assert transaction_validator(tx)
    """
    def validate(tx):
        """Valida que una transacción tenga estructura correcta"""
        required_fields = ['hash', 'from', 'to', 'amount', 'timestamp', 'status']
        return all(field in tx for field in required_fields)
    
    return validate


@pytest.fixture
def balance_checker(mock_economy):
    """
    Fixture: Helper para verificar balances
    
    Args:
        mock_economy: Sistema económico mock
    
    Returns:
        callable: Función para verificar balances de múltiples agentes
        
    Ejemplo:
        def test_balances(balance_checker, three_agents):
            balances = balance_checker(three_agents.values())
            assert all(b >= 0 for b in balances.values())
    """
    def check_balances(agent_ids):
        """
        Retorna dict con balances de múltiples agentes
        
        Args:
            agent_ids: Lista de agent IDs
        
        Returns:
            dict: {agent_id: balance}
        """
        return {
            agent_id: mock_economy.credits.get_balance(agent_id)
            for agent_id in agent_ids
        }
    
    return check_balances


# ============================================================
# HOOKS DE PYTEST
# ============================================================

def pytest_configure(config):
    """
    Configuración de pytest al inicio de la sesión de tests
    
    Registra markers custom para categorizar tests.
    """
    config.addinivalue_line(
        "markers", 
        "mock: Tests que usan sistema mock (sin dependencias externas)"
    )
    config.addinivalue_line(
        "markers", 
        "real: Tests que requieren blockchain real y dependencias externas"
    )
    config.addinivalue_line(
        "markers", 
        "slow: Tests que toman más de 5 segundos"
    )
    config.addinivalue_line(
        "markers", 
        "integration: Tests de integración entre múltiples componentes"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modifica items de test después de colección
    
    Auto-marca tests basándose en su ubicación:
    - test_mock_economy.py → marca como 'mock'
    - test_economy_system.py → marca como 'real'
    """
    for item in items:
        if "test_mock_economy" in item.nodeid:
            item.add_marker(pytest.mark.mock)
        elif "test_economy_system" in item.nodeid:
            item.add_marker(pytest.mark.real)


# ============================================================
# DOCUMENTACIÓN
# ============================================================

"""
GUÍA DE USO DE FIXTURES
========================

Fixtures Básicas:
-----------------
mock_economy:           Sistema económico completo
fresh_blockchain:       Blockchain limpio
mock_bsc_client:        Cliente BSC para transacciones
mock_token_client:      Cliente D8Token

Fixtures de Agentes:
--------------------
three_agents:           3 agentes (researcher, optimizer, validator)
funded_agent:           1 agente con 1000 D8C
agent_pair:             2 agentes (sender con 500 D8C, receiver con 0)

Fixtures de Datos:
------------------
sample_contributions:   Contribuciones de ejemplo
fitness_event:          Fitness event pre-registrado
sample_expenses:        Gastos registrados

Fixtures de Utilidades:
-----------------------
transaction_validator:  Validador de estructura de TX
balance_checker:        Helper para verificar balances

Markers Disponibles:
--------------------
@pytest.mark.mock:          Test usa sistema mock
@pytest.mark.real:          Test requiere blockchain real
@pytest.mark.slow:          Test toma >5 segundos
@pytest.mark.integration:   Test de integración

Ejemplos:
---------

# Test simple con mock_economy
def test_wallet_creation(mock_economy):
    wallet = mock_economy.credits.create_wallet("test")
    assert wallet.startswith('0x')

# Test con múltiples fixtures
def test_transfer(mock_economy, agent_pair, balance_checker):
    sender, receiver = agent_pair
    mock_economy.credits.transfer(sender, receiver, 100.0)
    balances = balance_checker([sender, receiver])
    assert balances[sender] == 400.0
    assert balances[receiver] == 100.0

# Test con marker
@pytest.mark.slow
def test_performance(mock_economy):
    # Test que toma tiempo...
    pass

Ejecutar:
---------
# Todos los tests
pytest tests/economy/ -v

# Solo tests mock (rápidos)
pytest tests/economy/ -m mock -v

# Solo tests real (requieren dependencias)
pytest tests/economy/ -m real -v

# Excluir tests lentos
pytest tests/economy/ -m "not slow" -v
"""
