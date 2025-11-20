"""
Autonomous Accounting System
D8 manages all finances, pays expenses, alerts if insufficient funds

Years 1-5: Revenue to Leo (D8 pays expenses from congress budget)
Year 6+: Agents pay rent to Leo (from their earnings)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ExpenseCategory(Enum):
    """Categories of expenses"""
    API_COSTS = "api_costs"  # LLM API costs
    INFRASTRUCTURE = "infrastructure"  # Servers, storage
    BLOCKCHAIN = "blockchain"  # Gas fees
    CONGRESS_OPERATIONS = "congress_operations"  # Congress activities
    RESEARCH = "research"  # Autonomous research
    DEVELOPMENT = "development"  # Self-improvement
    EMERGENCY = "emergency"  # Unexpected costs


@dataclass
class Expense:
    """Record of an expense"""
    expense_id: str
    category: ExpenseCategory
    amount: float
    description: str
    timestamp: datetime
    paid: bool = False
    tx_hash: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'expense_id': self.expense_id,
            'category': self.category.value,
            'amount': self.amount,
            'description': self.description,
            'timestamp': self.timestamp.isoformat(),
            'paid': self.paid,
            'tx_hash': self.tx_hash
        }


@dataclass
class Budget:
    """Budget allocation"""
    category: ExpenseCategory
    allocated: float
    spent: float = 0.0
    period_start: datetime = field(default_factory=datetime.now)
    period_end: Optional[datetime] = None
    
    def get_remaining(self) -> float:
        return max(0.0, self.allocated - self.spent)
    
    def get_utilization(self) -> float:
        """Get budget utilization percentage"""
        if self.allocated == 0:
            return 0.0
        return (self.spent / self.allocated) * 100


class AutonomousAccountingSystem:
    """
    D8's autonomous accounting system
    Manages all finances without human intervention
    """
    
    def __init__(self, credits_system, revenue_attribution):
        """
        Initialize accounting system
        
        Args:
            credits_system: D8CreditsSystem instance
            revenue_attribution: RevenueAttributionSystem instance
        """
        self.credits = credits_system
        self.attribution = revenue_attribution
        
        # Expense tracking
        self.expenses: List[Expense] = []
        self.expense_counter = 0
        
        # Budget management
        self.budgets: Dict[ExpenseCategory, Budget] = {}
        
        # Configuration
        self.launch_year = 2025
        self.current_year = datetime.now().year
        self.years_in_operation = self.current_year - self.launch_year
        
        # Alert thresholds
        self.low_balance_threshold = 100.0  # D8C
        self.critical_balance_threshold = 20.0  # D8C
        self.budget_warning_threshold = 0.8  # 80% utilization
        
        # Alert system
        self.alerts_sent: List[dict] = []
        
        # Load state
        self._load_state()
        
        logger.info("📒 Autonomous Accounting System initialized")
        logger.info(f"   Years in operation: {self.years_in_operation}")
        logger.info(f"   Mode: {'Revenue to Leo' if self.years_in_operation < 6 else 'Rent from Agents'}")
    
    def initialize_monthly_budget(self):
        """Initialize monthly budget allocations"""
        # Default monthly budgets
        default_budgets = {
            ExpenseCategory.API_COSTS: 500.0,
            ExpenseCategory.INFRASTRUCTURE: 200.0,
            ExpenseCategory.BLOCKCHAIN: 50.0,
            ExpenseCategory.CONGRESS_OPERATIONS: 100.0,
            ExpenseCategory.RESEARCH: 150.0,
            ExpenseCategory.DEVELOPMENT: 100.0,
            ExpenseCategory.EMERGENCY: 100.0
        }
        
        period_start = datetime.now()
        period_end = period_start + timedelta(days=30)
        
        for category, allocated in default_budgets.items():
            self.budgets[category] = Budget(
                category=category,
                allocated=allocated,
                spent=0.0,
                period_start=period_start,
                period_end=period_end
            )
        
        logger.info(f"📊 Monthly budget initialized: {sum(default_budgets.values())} D8C total")
    
    def record_expense(
        self,
        category: ExpenseCategory,
        amount: float,
        description: str,
        auto_pay: bool = True
    ) -> Optional[Expense]:
        """
        Record and optionally pay an expense
        
        Args:
            category: Expense category
            amount: Amount to spend
            description: Description of expense
            auto_pay: Whether to automatically pay
            
        Returns:
            Expense object if successful
        """
        self.expense_counter += 1
        
        expense = Expense(
            expense_id=f"EXP{self.expense_counter:06d}",
            category=category,
            amount=amount,
            description=description,
            timestamp=datetime.now()
        )
        
        # Check budget
        budget = self.budgets.get(category)
        if budget and budget.get_remaining() < amount:
            logger.warning(f"⚠️  Budget exceeded for {category.value}: {amount} > {budget.get_remaining()} remaining")
            
            # Can we reallocate from emergency fund?
            emergency_budget = self.budgets.get(ExpenseCategory.EMERGENCY)
            if emergency_budget and emergency_budget.get_remaining() >= amount:
                logger.info(f"💰 Using emergency fund for {category.value}")
                category = ExpenseCategory.EMERGENCY
                budget = emergency_budget
            else:
                logger.error(f"❌ Insufficient budget for expense: {expense.expense_id}")
                self._send_alert(
                    level="CRITICAL",
                    message=f"Budget exceeded: {category.value} needs {amount} D8C",
                    expense=expense
                )
        
        # Auto-pay if enabled
        if auto_pay:
            success = self._pay_expense(expense)
            if not success:
                return None
        
        # Update budget
        if budget:
            budget.spent += amount
            
            # Check utilization
            utilization = budget.get_utilization()
            if utilization >= self.budget_warning_threshold * 100:
                logger.warning(f"⚠️  Budget {category.value} at {utilization:.1f}% utilization")
                self._send_alert(
                    level="WARNING",
                    message=f"Budget {category.value} at {utilization:.1f}% utilization"
                )
        
        self.expenses.append(expense)
        self._save_state()
        
        logger.info(f"📝 Expense recorded: {expense.expense_id} - {amount} D8C ({category.value})")
        return expense
    
    def _pay_expense(self, expense: Expense) -> bool:
        """
        Pay an expense from congress budget
        
        Args:
            expense: Expense to pay
            
        Returns:
            True if payment successful
        """
        # Check congress balance
        congress_balance = self.credits.get_balance("congress")
        
        if congress_balance < expense.amount:
            logger.error(f"❌ Insufficient congress balance: {congress_balance} < {expense.amount}")
            self._send_alert(
                level="CRITICAL",
                message=f"Insufficient funds to pay expense {expense.expense_id}",
                expense=expense
            )
            return False
        
        # Pay expense (transfer to expense account)
        # In production, this would transfer to external provider
        logger.info(f"💸 Paying expense {expense.expense_id}: {expense.amount} D8C")
        
        expense.paid = True
        expense.tx_hash = f"PAID_{expense.expense_id}"
        
        # Check remaining balance
        remaining = congress_balance - expense.amount
        if remaining < self.low_balance_threshold:
            level = "CRITICAL" if remaining < self.critical_balance_threshold else "WARNING"
            self._send_alert(
                level=level,
                message=f"Low congress balance: {remaining} D8C remaining"
            )
        
        return True
    
    def collect_rent(self) -> float:
        """
        Collect rent from agents (Year 6+)
        
        Returns:
            Total rent collected
        """
        if self.years_in_operation < 6:
            logger.info("📅 Not yet collecting rent (Years 1-5: Revenue to Leo)")
            return 0.0
        
        # Calculate rent based on agent earnings
        total_rent = 0.0
        
        for agent_id, wallet in self.credits.wallets.items():
            if agent_id == "congress":
                continue
            
            # Rent = 10% of total earnings
            rent_due = wallet.total_earned * 0.10
            
            if wallet.balance >= rent_due:
                # Collect rent
                transaction = self.credits.transfer(
                    from_agent=agent_id,
                    to_agent="leo",
                    amount=rent_due,
                    reason=f"Monthly rent: 10% of {wallet.total_earned} D8C earned"
                )
                
                if transaction:
                    total_rent += rent_due
                    logger.info(f"🏠 Collected rent from {agent_id}: {rent_due} D8C")
            else:
                logger.warning(f"⚠️  Agent {agent_id} cannot afford rent: {wallet.balance} < {rent_due}")
                # Agent is in debt - survival pressure!
        
        logger.info(f"💰 Total rent collected: {total_rent} D8C")
        return total_rent
    
    def generate_financial_report(self) -> dict:
        """
        Generate comprehensive financial report
        
        Returns:
            Dictionary with financial metrics
        """
        # Calculate totals
        total_expenses = sum(e.amount for e in self.expenses)
        paid_expenses = sum(e.amount for e in self.expenses if e.paid)
        unpaid_expenses = sum(e.amount for e in self.expenses if not e.paid)
        
        # Expenses by category
        expenses_by_category = {}
        for category in ExpenseCategory:
            category_expenses = [e for e in self.expenses if e.category == category]
            expenses_by_category[category.value] = {
                'count': len(category_expenses),
                'total': sum(e.amount for e in category_expenses),
                'paid': sum(e.amount for e in category_expenses if e.paid),
                'unpaid': sum(e.amount for e in category_expenses if not e.paid)
            }
        
        # Budget status
        budget_status = {}
        for category, budget in self.budgets.items():
            budget_status[category.value] = {
                'allocated': budget.allocated,
                'spent': budget.spent,
                'remaining': budget.get_remaining(),
                'utilization': budget.get_utilization()
            }
        
        # Congress balance
        congress_balance = self.credits.get_balance("congress")
        
        # Collective fitness
        collective_metrics = self.attribution.get_collective_fitness()
        
        return {
            'summary': {
                'years_in_operation': self.years_in_operation,
                'mode': 'Revenue to Leo' if self.years_in_operation < 6 else 'Rent from Agents',
                'total_expenses': total_expenses,
                'paid_expenses': paid_expenses,
                'unpaid_expenses': unpaid_expenses,
                'congress_balance': congress_balance,
                'total_revenue': collective_metrics['total_revenue']
            },
            'expenses_by_category': expenses_by_category,
            'budget_status': budget_status,
            'collective_fitness': collective_metrics,
            'alerts': len(self.alerts_sent),
            'timestamp': datetime.now().isoformat()
        }
    
    def _send_alert(
        self,
        level: str,
        message: str,
        expense: Optional[Expense] = None
    ):
        """
        Send alert about financial issue
        
        Args:
            level: Alert level (WARNING, CRITICAL)
            message: Alert message
            expense: Related expense if any
        """
        alert = {
            'level': level,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'expense_id': expense.expense_id if expense else None
        }
        
        self.alerts_sent.append(alert)
        
        # Log alert
        if level == "CRITICAL":
            logger.critical(f"🚨 FINANCIAL ALERT: {message}")
        else:
            logger.warning(f"⚠️  FINANCIAL WARNING: {message}")
        
        # Save alert
        self._save_alert(alert)
    
    def _save_alert(self, alert: dict):
        """Save alert to file for Leo to review"""
        alerts_dir = Path.home() / "Documents" / "d8_data" / "financial_alerts"
        alerts_dir.mkdir(parents=True, exist_ok=True)
        
        alert_file = alerts_dir / f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(alert_file, 'w') as f:
            json.dump(alert, f, indent=2)
    
    def _load_state(self):
        """Load accounting state from file"""
        state_file = Path.home() / "Documents" / "d8_data" / "accounting.json"
        
        if state_file.exists():
            try:
                with open(state_file) as f:
                    data = json.load(f)
                
                # Load expenses
                for exp_data in data.get('expenses', []):
                    expense = Expense(
                        expense_id=exp_data['expense_id'],
                        category=ExpenseCategory(exp_data['category']),
                        amount=exp_data['amount'],
                        description=exp_data['description'],
                        timestamp=datetime.fromisoformat(exp_data['timestamp']),
                        paid=exp_data['paid'],
                        tx_hash=exp_data.get('tx_hash')
                    )
                    self.expenses.append(expense)
                
                # Load budgets
                for cat_str, budget_data in data.get('budgets', {}).items():
                    category = ExpenseCategory(cat_str)
                    self.budgets[category] = Budget(
                        category=category,
                        allocated=budget_data['allocated'],
                        spent=budget_data['spent'],
                        period_start=datetime.fromisoformat(budget_data['period_start']),
                        period_end=datetime.fromisoformat(budget_data['period_end']) if budget_data.get('period_end') else None
                    )
                
                self.expense_counter = data.get('expense_counter', 0)
                self.alerts_sent = data.get('alerts_sent', [])
                
                logger.info(f"📂 Loaded accounting state: {len(self.expenses)} expenses")
                
            except Exception as e:
                logger.error(f"❌ Failed to load accounting state: {e}")
    
    def _save_state(self):
        """Save accounting state to file"""
        state_file = Path.home() / "Documents" / "d8_data" / "accounting.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'expense_counter': self.expense_counter,
            'expenses': [e.to_dict() for e in self.expenses],
            'budgets': {
                cat.value: {
                    'allocated': budget.allocated,
                    'spent': budget.spent,
                    'period_start': budget.period_start.isoformat(),
                    'period_end': budget.period_end.isoformat() if budget.period_end else None
                }
                for cat, budget in self.budgets.items()
            },
            'alerts_sent': self.alerts_sent
        }
        
        with open(state_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.debug("💾 Saved accounting state")
