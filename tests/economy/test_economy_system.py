"""
Tests for D8 Economy System
"""

import pytest
from datetime import datetime
from app.economy import D8EconomySystem
from app.economy.d8_credits import AgentWallet
from app.economy.revenue_attribution import AgentContribution
from app.economy.accounting import ExpenseCategory


class TestD8CreditsSystem:
    """Test D8 Credits and wallet management"""
    
    def test_wallet_creation(self, mock_economy):
        """Test creating agent wallet"""
        wallet_info = mock_economy.create_agent_account("test_agent_001")
        
        assert wallet_info['agent_id'] == "test_agent_001"
        assert 'address' in wallet_info
        assert wallet_info['balance'] == 0.0
    
    def test_transfer_between_agents(self, mock_economy):
        """Test D8C transfer between agents"""
        # Create two agents
        mock_economy.create_agent_account("agent_a")
        mock_economy.create_agent_account("agent_b")
        
        # Give agent_a some credits
        mock_economy.credits.reward_agent("agent_a", 100.0, "Initial funding")
        
        # Transfer
        tx = mock_economy.credits.transfer(
            from_agent="agent_a",
            to_agent="agent_b",
            amount=30.0,
            reason="Test transfer"
        )
        
        assert tx is not None
        assert tx.amount == 30.0
        assert mock_economy.credits.get_balance("agent_a") == 70.0
        assert mock_economy.credits.get_balance("agent_b") == 30.0
    
    def test_insufficient_balance(self, mock_economy):
        """Test transfer with insufficient balance"""
        mock_economy.create_agent_account("agent_a")
        mock_economy.create_agent_account("agent_b")
        
        # Try to transfer without balance
        tx = mock_economy.credits.transfer(
            from_agent="agent_a",
            to_agent="agent_b",
            amount=100.0,
            reason="Should fail"
        )
        
        assert tx is None


class TestRevenueAttribution:
    """Test revenue attribution and fitness events"""
    
    def test_single_agent_gets_100_percent(self, mock_economy):
        """Test solo agent gets 100% of revenue"""
        mock_economy.create_agent_account("solo_agent")
        
        mock_economy.record_agent_contribution(
            agent_id="solo_agent",
            role="researcher",
            fitness_score=85.0,
            revenue_generated=100.0,
            contribution_score=1.0
        )
        
        balance = mock_economy.credits.get_balance("solo_agent")
        assert balance == 100.0
    
    def test_40_40_20_distribution(self, mock_economy):
        """Test 40/40/20 revenue split"""
        # Create three agents
        agents = ["agent_best", "agent_mid", "agent_worst"]
        for agent_id in agents:
            mock_economy.create_agent_account(agent_id)
        
        # Record contributions
        contributions = [
            AgentContribution(
                agent_id="agent_best",
                role="optimizer",
                contribution_score=0.95,
                actions_performed=10,
                timestamp=datetime.now()
            ),
            AgentContribution(
                agent_id="agent_mid",
                role="researcher",
                contribution_score=0.60,
                actions_performed=5,
                timestamp=datetime.now()
            ),
            AgentContribution(
                agent_id="agent_worst",
                role="validator",
                contribution_score=0.30,
                actions_performed=2,
                timestamp=datetime.now()
            )
        ]
        
        mock_economy.attribution.record_fitness_event(
            fitness_score=100.0,
            revenue_generated=100.0,
            contributors=contributions
        )
        
        # Check distribution
        assert mock_economy.credits.get_balance("agent_best") == 40.0
        assert mock_economy.credits.get_balance("agent_mid") == 40.0
        assert mock_economy.credits.get_balance("agent_worst") == 20.0
    
    def test_leaderboard(self, mock_economy):
        """Test leaderboard generation"""
        # Create agents and give earnings
        for i in range(5):
            agent_id = f"agent_{i}"
            mock_economy.create_agent_account(agent_id)
            mock_economy.record_agent_contribution(
                agent_id=agent_id,
                role="worker",
                fitness_score=50.0 + i * 10,
                revenue_generated=100.0 + i * 20,
                contribution_score=0.5 + i * 0.1
            )
        
        leaderboard = mock_economy.attribution.get_leaderboard('earnings', limit=5)
        
        # Agent_4 should be richest
        assert leaderboard[0][0] == "agent_4"
        assert len(leaderboard) == 5


class TestAutonomousAccounting:
    """Test autonomous accounting system"""
    
    def test_expense_recording(self, mock_economy):
        """Test recording an expense"""
        # Initialize budget
        mock_economy.accounting.initialize_monthly_budget()
        
        expense = mock_economy.accounting.record_expense(
            category=ExpenseCategory.API_COSTS,
            amount=50.0,
            description="Groq API usage",
            auto_pay=False
        )
        
        assert expense is not None
        assert expense.amount == 50.0
        assert expense.paid == False
    
    def test_budget_exceeded_warning(self, mock_economy):
        """Test warning when budget exceeded"""
        mock_economy.accounting.initialize_monthly_budget()
        
        # Exceed API costs budget (default: 500)
        for i in range(11):
            mock_economy.accounting.record_expense(
                category=ExpenseCategory.API_COSTS,
                amount=50.0,
                description=f"API call {i}",
                auto_pay=False
            )
        
        # Check alerts
        assert len(mock_economy.accounting.alerts_sent) > 0
    
    def test_financial_report(self, mock_economy):
        """Test financial report generation"""
        mock_economy.accounting.initialize_monthly_budget()
        
        # Record some expenses
        mock_economy.pay_api_cost(100.0, "Groq", "Test usage")
        mock_economy.pay_api_cost(50.0, "Gemini", "Test usage")
        
        report = mock_economy.accounting.generate_financial_report()
        
        assert 'summary' in report
        assert 'expenses_by_category' in report
        assert 'budget_status' in report
        assert report['summary']['total_expenses'] == 150.0


class TestIntegratedSystem:
    """Test full integrated system"""
    
    def test_complete_workflow(self, mock_economy):
        """Test complete workflow: agent creation → contribution → payment"""
        # 1. Create agent
        agent_info = mock_economy.create_agent_account("worker_001")
        assert agent_info['balance'] == 0.0
        
        # 2. Record contribution
        mock_economy.record_agent_contribution(
            agent_id="worker_001",
            role="content_creator",
            fitness_score=95.0,
            revenue_generated=500.0,
            contribution_score=0.9,
            niche="twitter_threads"
        )
        
        # 3. Check balance
        balance = mock_economy.credits.get_balance("worker_001")
        assert balance == 500.0
        
        # 4. Record API cost
        mock_economy.pay_api_cost(50.0, "Groq", "Generated content")
        
        # 5. Check stats
        stats = mock_economy.get_agent_stats("worker_001")
        assert stats['wallet']['balance'] == 500.0
        assert stats['contributions']['total_contributions'] == 1
    
    def test_system_health(self, mock_economy):
        """Test system health monitoring"""
        health = mock_economy.get_system_health()
        
        assert 'status' in health
        assert 'congress_balance' in health
        assert 'total_agents' in health
    
    def test_full_report(self, mock_economy):
        """Test full system report"""
        # Setup system
        for i in range(3):
            agent_id = f"agent_{i}"
            mock_economy.create_agent_account(agent_id)
            mock_economy.record_agent_contribution(
                agent_id=agent_id,
                role="worker",
                fitness_score=80.0,
                revenue_generated=100.0
            )
        
        report = mock_economy.generate_full_report()
        
        assert 'system_health' in report
        assert 'financial_report' in report
        assert 'credits_stats' in report
        assert 'collective_fitness' in report
        assert 'top_earners' in report


# Fixtures

@pytest.fixture
def mock_economy():
    """
    Create mock economy system for testing
    Uses in-memory storage instead of blockchain
    """
    from unittest.mock import MagicMock
    
    # Mock blockchain clients
    bsc_mock = MagicMock()
    bsc_mock.get_chain_id.return_value = 97
    bsc_mock.create_account.return_value = {
        'address': '0x' + '0' * 40,
        'private_key': '0x' + '1' * 64
    }
    bsc_mock.wait_for_receipt.return_value = {'status': 1, 'blockNumber': 12345}
    
    token_mock = MagicMock()
    token_mock.get_balance.return_value = 0.0
    token_mock.transfer.return_value = '0x' + 'a' * 64
    token_mock.distribute_reward.return_value = '0x' + 'b' * 64
    
    # Create economy with mocks
    from app.economy.d8_credits import D8CreditsSystem
    from app.economy.revenue_attribution import RevenueAttributionSystem
    from app.economy.accounting import AutonomousAccountingSystem
    
    credits = D8CreditsSystem(token_mock, bsc_mock)
    credits.set_congress_wallet('0x' + 'c' * 40, '0x' + 'd' * 64)
    
    attribution = RevenueAttributionSystem(credits)
    accounting = AutonomousAccountingSystem(credits, attribution)
    
    # Create mock economy object
    economy = MagicMock()
    economy.credits = credits
    economy.attribution = attribution
    economy.accounting = accounting
    
    # Add methods
    economy.create_agent_account = lambda agent_id: {
        'agent_id': agent_id,
        'address': credits.create_wallet(agent_id).address,
        'balance': 0.0,
        'created_at': datetime.now().isoformat()
    }
    
    economy.record_agent_contribution = lambda **kwargs: attribution.record_fitness_event(
        fitness_score=kwargs['fitness_score'],
        revenue_generated=kwargs['revenue_generated'],
        contributors=[AgentContribution(
            agent_id=kwargs['agent_id'],
            role=kwargs['role'],
            contribution_score=kwargs.get('contribution_score', 1.0),
            actions_performed=kwargs.get('actions_performed', 1),
            timestamp=datetime.now()
        )],
        niche=kwargs.get('niche')
    )
    
    economy.pay_api_cost = lambda amount, provider, description: accounting.record_expense(
        category=ExpenseCategory.API_COSTS,
        amount=amount,
        description=f"{provider}: {description}"
    )
    
    economy.get_agent_stats = lambda agent_id: {
        'wallet': credits.get_wallet(agent_id).to_dict() if credits.get_wallet(agent_id) else None,
        'contributions': attribution.get_agent_contribution_stats(agent_id)
    }
    
    economy.get_system_health = lambda: {
        'status': 'HEALTHY',
        'congress_balance': credits.get_balance('congress'),
        'total_agents': len(credits.wallets),
        'total_supply': credits.get_total_supply(),
        'total_fitness': attribution.get_collective_fitness()['total_fitness'],
        'total_revenue': attribution.get_collective_fitness()['total_revenue'],
        'unpaid_expenses': 0,
        'active_alerts': 0,
        'timestamp': datetime.now().isoformat()
    }
    
    economy.generate_full_report = lambda: {
        'system_health': economy.get_system_health(),
        'financial_report': accounting.generate_financial_report(),
        'credits_stats': credits.get_stats(),
        'collective_fitness': attribution.get_collective_fitness(),
        'top_earners': attribution.get_leaderboard('earnings', 10),
        'top_contributors': attribution.get_leaderboard('contributions', 10),
        'richest_agents': credits.get_richest_agents(10)
    }
    
    return economy


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
