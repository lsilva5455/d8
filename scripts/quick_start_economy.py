"""
D8 Economy - Quick Start Example
Demonstrates basic usage with MOCK blockchain (no network needed)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)


def quick_start_demo():
    """
    Quick start demo with mock blockchain
    Shows all economy features without real deployment
    """
    
    print("🚀 D8 Economy System - Quick Start Demo")
    print("=" * 60)
    print("🎭 Using MOCK blockchain (no network needed)")
    print()
    
    # Use mock blockchain
    from app.economy.mock_blockchain import create_mock_economy_system
    from app.economy.revenue_attribution import AgentContribution
    from app.economy.accounting import ExpenseCategory
    
    print("📦 Creating mock economy system...")
    economy = create_mock_economy_system()
    print()
    
    # Demo 1: Create agents
    print("👥 DEMO 1: Creating Agents")
    print("-" * 60)
    
    agents = ['researcher', 'optimizer', 'validator']
    
    for agent_id in agents:
        wallet_info = economy.create_agent_account(agent_id)
        print(f"   ✅ Created {agent_id}: {wallet_info['address'][:10]}...{wallet_info['address'][-8:]}")
    
    print()
    
    # Demo 2: Simulate fitness event with 40/40/20 distribution
    print("💰 DEMO 2: Revenue Attribution (40/40/20 Rule)")
    print("-" * 60)
    
    contributions = [
        AgentContribution(
            agent_id='researcher',
            role='research',
            contribution_score=0.95,
            actions_performed=10,
            timestamp=datetime.now()
        ),
        AgentContribution(
            agent_id='optimizer',
            role='optimization',
            contribution_score=0.60,
            actions_performed=5,
            timestamp=datetime.now()
        ),
        AgentContribution(
            agent_id='validator',
            role='validation',
            contribution_score=0.30,
            actions_performed=2,
            timestamp=datetime.now()
        )
    ]
    
    print("   📊 Contributions:")
    for c in contributions:
        print(f"      • {c.agent_id}: {c.contribution_score:.2f} ({c.actions_performed} actions)")
    
    print()
    print("   💸 Distributing 100 D8C revenue...")
    
    event = economy.attribution.record_fitness_event(
        fitness_score=95.0,
        revenue_generated=100.0,
        contributors=contributions,
        niche='twitter_threads'
    )
    
    print()
    print("   🎁 Distribution:")
    distribution = event.get_contribution_distribution()
    for agent_id, amount in sorted(distribution.items(), key=lambda x: x[1], reverse=True):
        balance = economy.credits.get_balance(agent_id)
        print(f"      • {agent_id}: {amount:.1f} D8C (Balance: {balance:.1f} D8C)")
    
    print()
    
    # Demo 3: Record expenses
    print("💳 DEMO 3: Autonomous Accounting")
    print("-" * 60)
    
    expenses = [
        (ExpenseCategory.API_COSTS, 50.0, "Groq API: 1000 requests"),
        (ExpenseCategory.API_COSTS, 30.0, "Gemini API: 500 requests"),
        (ExpenseCategory.INFRASTRUCTURE, 20.0, "Server hosting"),
        (ExpenseCategory.RESEARCH, 15.0, "New model evaluation")
    ]
    
    print("   📝 Recording expenses:")
    for category, amount, desc in expenses:
        expense = economy.accounting.record_expense(
            category=category,
            amount=amount,
            description=desc,
            auto_pay=False
        )
        if expense:
            print(f"      • {expense.expense_id}: {amount} D8C - {desc}")
    
    print()
    
    # Demo 4: Agent stats
    print("📊 DEMO 4: Agent Statistics")
    print("-" * 60)
    
    for agent_id in agents:
        wallet = economy.credits.get_wallet(agent_id)
        stats = economy.attribution.get_agent_contribution_stats(agent_id)
        
        print(f"   🤖 {agent_id.upper()}")
        print(f"      Balance: {wallet.balance:.1f} D8C")
        print(f"      Total Earned: {wallet.total_earned:.1f} D8C")
        print(f"      Contributions: {stats['total_contributions']}")
        print(f"      Avg Contribution Score: {stats['average_contribution_score']:.2f}")
        print()
    
    # Demo 5: Leaderboard
    print("🏆 DEMO 5: Leaderboards")
    print("-" * 60)
    
    earnings_leaderboard = economy.attribution.get_leaderboard('earnings', limit=3)
    
    print("   💰 Top Earners:")
    for i, (agent_id, earnings) in enumerate(earnings_leaderboard, 1):
        medal = ['🥇', '🥈', '🥉'][i-1] if i <= 3 else '  '
        print(f"      {medal} {i}. {agent_id}: {earnings:.1f} D8C")
    
    print()
    
    contributions_leaderboard = economy.attribution.get_leaderboard('contributions', limit=3)
    
    print("   📈 Most Active:")
    for i, (agent_id, count) in enumerate(contributions_leaderboard, 1):
        medal = ['🥇', '🥈', '🥉'][i-1] if i <= 3 else '  '
        print(f"      {medal} {i}. {agent_id}: {count} contributions")
    
    print()
    
    # Demo 6: Financial report
    print("📊 DEMO 6: Financial Report")
    print("-" * 60)
    
    report = economy.accounting.generate_financial_report()
    
    print(f"   Total Expenses: {report['summary']['total_expenses']:.1f} D8C")
    print(f"   Paid: {report['summary']['paid_expenses']:.1f} D8C")
    print(f"   Unpaid: {report['summary']['unpaid_expenses']:.1f} D8C")
    print()
    
    print("   Expenses by Category:")
    for category, data in report['expenses_by_category'].items():
        if data['total'] > 0:
            print(f"      • {category}: {data['total']:.1f} D8C ({data['count']} items)")
    
    print()
    
    print("   Budget Status:")
    for category, budget in report['budget_status'].items():
        if budget['allocated'] > 0:
            utilization = budget['utilization']
            bar = '█' * int(utilization / 10) + '░' * (10 - int(utilization / 10))
            print(f"      • {category}: [{bar}] {utilization:.1f}%")
    
    print()
    
    # Demo 7: Collective fitness
    print("🌍 DEMO 7: Collective Fitness")
    print("-" * 60)
    
    collective = economy.attribution.get_collective_fitness()
    
    print(f"   Total Fitness: {collective['total_fitness']:.1f}")
    print(f"   Total Revenue: {collective['total_revenue']:.1f} D8C")
    print(f"   Total Events: {collective['total_events']}")
    print(f"   Avg Fitness/Event: {collective['average_fitness_per_event']:.1f}")
    print(f"   Active Contributors: {collective['total_contributors']}")
    
    print()
    
    # Summary
    print("=" * 60)
    print("✅ Demo completed successfully!")
    print()
    print("📊 Final Stats:")
    health = economy.get_system_health()
    print(f"   Congress Balance: {health['congress_balance']:.1f} D8C")
    print(f"   Total Agents: {health['total_agents']}")
    print(f"   Total Revenue: {health['total_revenue']:.1f} D8C")
    print(f"   System Status: {health['status']}")
    print()
    print("📚 What We Tested:")
    print("   ✅ Agent wallet creation")
    print("   ✅ Revenue attribution (40/40/20)")
    print("   ✅ Expense tracking")
    print("   ✅ Budget management")
    print("   ✅ Leaderboards")
    print("   ✅ Financial reporting")
    print("   ✅ Collective fitness")
    print()
    print("🎭 Note: This is a MOCK system for testing")
    print("   No real blockchain or network connection needed!")
    print()
    print("📚 Next Steps:")
    print("   1. Review code: app/economy/")
    print("   2. Run tests: pytest tests/economy/ -v")
    print("   3. Read docs: docs/01_arquitectura/economia.md")
    print()


if __name__ == "__main__":
    quick_start_demo()
