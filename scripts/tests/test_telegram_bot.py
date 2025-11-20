"""
Test Telegram Bot Integration (Mock Mode)

This tests the bot without actually running the full congress.
Useful for verifying Telegram credentials and bot functionality.
"""

import os
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.integrations.telegram_bot import CongressTelegramBot
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class MockCongress:
    """Mock congress for testing bot without running actual experiments"""
    
    def __init__(self):
        self.paused = False
        self.telegram_bot = None
        self.current_generation = 3
        self.total_experiments = 42
        self.improvements_implemented = 15
        self.experiments = [
            {
                'id': 'exp_001',
                'experiment': {'finding': {'opportunity': 'Optimize prompt templates'}},
                'improvement': 18.5,
                'timestamp': 1700000000
            },
            {
                'id': 'exp_002',
                'experiment': {'finding': {'opportunity': 'Use few-shot examples'}},
                'improvement': 12.3,
                'timestamp': 1700000100
            },
            {
                'id': 'exp_003',
                'experiment': {'finding': {'opportunity': 'Parallel API calls'}},
                'improvement': 7.8,
                'timestamp': 1700000200
            }
        ]
    
    def set_telegram_bot(self, bot):
        self.telegram_bot = bot
    
    def get_status(self):
        return {
            'generation': self.current_generation,
            'total_experiments': self.total_experiments,
            'improvements_implemented': self.improvements_implemented,
            'paused': self.paused,
            'last_experiment': 'Optimize prompt templates',
            'avg_improvement': 12.8
        }
    
    def get_recent_experiments(self, limit=5):
        import time
        return [
            {
                'title': exp['experiment']['finding']['opportunity'],
                'improvement': exp['improvement'],
                'approved': exp['improvement'] > 10,
                'date': time.strftime('%Y-%m-%d', time.localtime(exp['timestamp']))
            }
            for exp in self.experiments[:limit]
        ]
    
    def assign_manual_task(self, description, requested_by):
        task_id = f"task_{hash(description) % 10000}"
        logger.info(f"✅ Task assigned: {task_id} - {description} (by {requested_by})")
        return task_id
    
    def pause(self):
        self.paused = True
        logger.info("⏸️  Congress paused")
    
    def resume(self):
        self.paused = False
        logger.info("▶️  Congress resumed")
    
    def approve_experiment(self, exp_id):
        logger.info(f"✅ Experiment {exp_id} approved")
    
    def reject_experiment(self, exp_id):
        logger.info(f"❌ Experiment {exp_id} rejected")

def main():
    """Test bot with mock congress"""
    
    print("=" * 70)
    print("🧪 TELEGRAM BOT TEST (Mock Mode)")
    print("=" * 70)
    print()
    
    # Check credentials
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token:
        print("❌ TELEGRAM_TOKEN not found in .env")
        print()
        print("Setup:")
        print("1. Habla con @BotFather en Telegram")
        print("2. Crea bot: /newbot")
        print("3. Copia token a .env: TELEGRAM_TOKEN=tu_token")
        sys.exit(1)
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID not found in .env")
        print()
        print("Setup:")
        print("1. Habla con @userinfobot en Telegram")
        print("2. Envía /start")
        print("3. Copia tu Chat ID a .env: TELEGRAM_CHAT_ID=tu_id")
        sys.exit(1)
    
    print("✅ Credentials found")
    print(f"   Token: {token[:20]}...")
    print(f"   Chat ID: {chat_id}")
    print()
    
    # Create mock congress
    print("📦 Creating mock congress...")
    mock_congress = MockCongress()
    print("✅ Mock congress ready")
    print()
    
    # Create bot
    print("🤖 Initializing Telegram bot...")
    try:
        bot = CongressTelegramBot(mock_congress)
        print("✅ Bot initialized")
        print()
    except Exception as e:
        print(f"❌ Error initializing bot: {e}")
        sys.exit(1)
    
    # Test status
    print("📊 Testing get_status()...")
    status = mock_congress.get_status()
    print(f"   Generation: {status['generation']}")
    print(f"   Experiments: {status['total_experiments']}")
    print(f"   Improvements: {status['improvements_implemented']}")
    print("✅ Status OK")
    print()
    
    # Test experiments
    print("🧪 Testing get_recent_experiments()...")
    experiments = mock_congress.get_recent_experiments(limit=3)
    for i, exp in enumerate(experiments, 1):
        print(f"   {i}. {exp['title']} (+{exp['improvement']:.1f}%)")
    print("✅ Experiments OK")
    print()
    
    # Test task assignment
    print("📝 Testing assign_manual_task()...")
    task_id = mock_congress.assign_manual_task(
        "Test task from pytest",
        "test_script"
    )
    print(f"   Task ID: {task_id}")
    print("✅ Task assignment OK")
    print()
    
    # Run bot
    print("=" * 70)
    print("🚀 STARTING BOT")
    print("=" * 70)
    print()
    print("El bot está corriendo. Abre Telegram y envía:")
    print()
    print("   /start")
    print("   /status")
    print("   /experiments")
    print("   /task Test desde Telegram")
    print()
    print("Presiona Ctrl+C para detener")
    print()
    print("-" * 70)
    print()
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("👋 Bot stopped")
        print("=" * 70)

if __name__ == "__main__":
    main()
