"""
Integration Tests for FASE 2: Economy + Autonomous System
Tests the complete flow: Agent → Action → Cost → Revenue → Fitness → Distribution
"""

import pytest
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.economy.d8_credits import D8CreditsSystem
from app.economy.accounting import AutonomousAccountingSystem
from app.economy.revenue_attribution import RevenueAttributionSystem
from app.agents.base_agent import BaseAgent
from app.evolution.darwin import Genome, DeepSeekEvolutionEngine, EvolutionOrchestrator


@pytest.fixture
def groq_api_key():
    """Get Groq API key from environment"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        pytest.skip("GROQ_API_KEY not found in environment")
    return api_key


@pytest.fixture
def credits_system():
    """Initialize D8 Credits System"""
    return D8CreditsSystem()


@pytest.fixture
def accounting_system():
    """Initialize Autonomous Accounting"""
    system = AutonomousAccountingSystem()
    system.set_monthly_budget("api_calls", 100.0)
    system.set_monthly_budget("infrastructure", 50.0)
    return system


@pytest.fixture
def revenue_attribution():
    """Initialize Revenue Attribution"""
    return RevenueAttributionSystem()


@pytest.fixture
def test_agent(groq_api_key, credits_system, accounting_system):
    """Create a test agent with economy integration"""
    genome = Genome(
        prompt="You are a test agent for integration testing. Generate simple responses."
    )
    
    agent = BaseAgent(
        genome=genome,
        groq_api_key=groq_api_key,
        credits_system=credits_system,
        accounting_system=accounting_system
    )
    
    return agent


class TestAgentEconomyIntegration:
    """Test agent integration with economy systems"""
    
    def test_agent_has_wallet(self, test_agent, credits_system):
        """Agent should have a wallet upon creation"""
        assert test_agent.wallet is not None
        assert test_agent.agent_id in credits_system.wallets
        
    def test_agent_records_api_cost(self, test_agent, accounting_system):
        """Agent should record API costs when acting"""
        initial_expenses = len(accounting_system.expenses)
        
        # Perform action
        result = test_agent.act(
            input_data={"task": "say hello"},
            action_type="test_action"
        )
        
        assert result['success'] == True
        
        # Check expense recorded
        api_expenses = [e for e in accounting_system.expenses if e.category == "api_calls"]
        assert len(api_expenses) > 0
        
    def test_agent_records_revenue(self, test_agent, credits_system):
        """Agent should record revenue when generated"""
        initial_revenue = test_agent.get_total_revenue()
        
        # Simulate revenue
        test_agent._record_revenue(100.0, "test_sale")
        
        assert test_agent.get_total_revenue() == initial_revenue + 100.0
        
    def test_agent_calculates_roi(self, test_agent):
        """Agent should calculate ROI correctly"""
        # Record some revenue and costs
        test_agent._record_revenue(100.0, "sales")
        test_agent.metrics.cost_tokens = 10.0
        
        roi = test_agent.get_roi()
        expected_roi = (100.0 - 10.0) / 10.0
        
        assert roi == expected_roi


class TestEvolutionEconomyIntegration:
    """Test evolution system integration with economy"""
    
    def test_fitness_based_on_revenue(self, revenue_attribution):
        """Fitness calculation should incorporate revenue"""
        # Create mock orchestrator (without DeepSeek dependency)
        class MockEngine:
            pass
        
        orchestrator = EvolutionOrchestrator(
            engine=MockEngine(),
            revenue_attribution=revenue_attribution
        )
        
        agent_data = {
            'agent_id': 'test_001',
            'revenue': 100.0,
            'efficiency': 0.8,
            'satisfaction': 0.7
        }
        
        fitness = orchestrator.calculate_fitness_with_revenue(agent_data)
        
        # Fitness formula: 0.6*revenue + 0.3*efficiency*100 + 0.1*satisfaction*100
        expected = 0.6 * 100.0 + 0.3 * 0.8 * 100 + 0.1 * 0.7 * 100
        
        assert abs(fitness - expected) < 0.01
        
    def test_revenue_distribution_40_40_20(self, revenue_attribution):
        """Revenue should be distributed according to 40/40/20 rule"""
        orchestrator = EvolutionOrchestrator(
            engine=None,
            revenue_attribution=revenue_attribution
        )
        
        agents_data = [
            {'agent_id': 'agent_best', 'revenue': 100, 'efficiency': 0.9, 'satisfaction': 0.8},
            {'agent_id': 'agent_mid', 'revenue': 50, 'efficiency': 0.7, 'satisfaction': 0.6},
            {'agent_id': 'agent_worst', 'revenue': 10, 'efficiency': 0.5, 'satisfaction': 0.4},
        ]
        
        total_revenue = 1000.0
        distribution = orchestrator.distribute_generation_revenue(agents_data, total_revenue)
        
        # Verify distribution sums to total
        assert abs(sum(distribution.values()) - total_revenue) < 0.01
        
        # Best agent should get most
        amounts = sorted(distribution.values(), reverse=True)
        assert amounts[0] >= amounts[1] >= amounts[2]


class TestFullCycleIntegration:
    """Test complete end-to-end cycle"""
    
    def test_full_agent_lifecycle(self, groq_api_key, credits_system, accounting_system, revenue_attribution):
        """Test complete lifecycle: create → act → record costs → generate revenue → calculate fitness"""
        
        # 1. Create agent with economy
        genome = Genome(
            prompt="You are a content creator. Generate valuable content."
        )
        
        agent = BaseAgent(
            genome=genome,
            groq_api_key=groq_api_key,
            credits_system=credits_system,
            accounting_system=accounting_system
        )
        
        # 2. Agent performs action (incurs cost)
        result = agent.act(
            input_data={"topic": "AI testing"},
            action_type="generate_content"
        )
        
        assert result['success'] == True
        
        # 3. Verify API cost recorded
        api_expenses = [e for e in accounting_system.expenses if e.category == "api_calls"]
        assert len(api_expenses) > 0
        initial_cost = agent.get_total_costs()
        assert initial_cost > 0
        
        # 4. Simulate revenue generation
        agent._record_revenue(150.0, "content_monetization")
        
        # 5. Verify revenue recorded
        assert agent.get_total_revenue() == 150.0
        
        # 6. Calculate fitness
        fitness = agent.get_fitness()
        assert fitness > 0
        
        # 7. Verify ROI
        roi = agent.get_roi()
        assert roi > 0  # Should be profitable
        
        # 8. Verify wallet balance (in real implementation)
        balance = agent.get_wallet_balance()
        assert balance >= 0
        
    def test_multi_agent_generation_cycle(self, groq_api_key, credits_system, accounting_system, revenue_attribution):
        """Test full generation with multiple agents and revenue distribution"""
        
        # Create 3 agents
        agents = []
        for i in range(3):
            genome = Genome(prompt=f"You are agent {i}")
            agent = BaseAgent(
                genome=genome,
                groq_api_key=groq_api_key,
                credits_system=credits_system,
                accounting_system=accounting_system
            )
            agents.append(agent)
        
        # Agents perform actions and generate different revenues
        revenues = [100.0, 50.0, 10.0]
        for agent, revenue in zip(agents, revenues):
            # Act (incur costs)
            result = agent.act(
                input_data={"task": "work"},
                action_type="perform_task"
            )
            
            # Generate revenue
            agent._record_revenue(revenue, "earnings")
        
        # Calculate fitness for all
        agents_data = []
        for agent in agents:
            agents_data.append({
                'agent_id': agent.agent_id,
                'revenue': agent.get_total_revenue(),
                'efficiency': 0.8,
                'satisfaction': 0.7
            })
        
        # Distribute revenue
        orchestrator = EvolutionOrchestrator(
            engine=None,
            revenue_attribution=revenue_attribution
        )
        
        total_revenue = sum(revenues)
        distribution = orchestrator.distribute_generation_revenue(agents_data, total_revenue)
        
        # Verify distribution
        assert len(distribution) == 3
        assert abs(sum(distribution.values()) - total_revenue) < 0.01
        
        # Best performer should get most
        best_agent_id = agents[0].agent_id
        worst_agent_id = agents[2].agent_id
        assert distribution[best_agent_id] > distribution[worst_agent_id]


class TestAccountingAutomation:
    """Test autonomous accounting features"""
    
    def test_budget_tracking(self, accounting_system):
        """Accounting should track budget usage"""
        # Set budget
        accounting_system.set_monthly_budget("api_calls", 100.0)
        
        # Record expense
        accounting_system.record_expense(
            amount=25.0,
            category="api_calls",
            description="Test expense"
        )
        
        # Check budget status
        usage = accounting_system.get_budget_usage("api_calls")
        assert usage == 0.25  # 25/100
        
    def test_budget_alert(self, accounting_system):
        """Should alert when budget exceeded"""
        accounting_system.set_monthly_budget("api_calls", 100.0)
        
        # Spend within budget
        accounting_system.record_expense(50.0, "api_calls", "Test 1")
        assert not accounting_system.check_budget_exceeded("api_calls")
        
        # Exceed budget
        accounting_system.record_expense(60.0, "api_calls", "Test 2")
        assert accounting_system.check_budget_exceeded("api_calls")
        
    def test_daily_report_generation(self, accounting_system):
        """Should generate comprehensive daily report"""
        # Record some activity
        accounting_system.record_expense(50.0, "api_calls", "API usage")
        accounting_system.record_revenue(200.0, "sales", "Product sales")
        
        report = accounting_system.generate_daily_report()
        
        assert 'total_revenue' in report
        assert 'total_expenses' in report
        assert 'net_profit' in report
        assert report['total_revenue'] == 200.0
        assert report['total_expenses'] == 50.0
        assert report['net_profit'] == 150.0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
