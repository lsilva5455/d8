"""
Congress with Telegram Integration Launcher

This script launches the Autonomous Congress with Telegram bot for Leo's oversight.

By default:
- Congress runs fully autonomously
- Leo receives notifications of important changes
- Leo can query status, assign tasks, pause/resume via Telegram

Leo's commands:
- /status - Get congress status
- /experiments - See recent experiments
- /task <description> - Assign specific task
- /approve - Toggle manual approval mode
- /stop - Pause congress
- /resume - Resume congress
- Natural language - Chat directly

Congress operates autonomously respecting D8's zero-intervention principle,
but Leo has optional oversight capability via Telegram.
"""

import sys
import asyncio
import logging
from pathlib import Path
import threading

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.autonomous_congress import AutonomousCongress
from app.integrations.telegram_bot import CongressTelegramBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/congress_telegram.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class CongressWithTelegram:
    """
    Wrapper that runs Congress + Telegram bot concurrently
    """
    
    def __init__(self):
        self.congress = AutonomousCongress()
        self.bot = CongressTelegramBot(self.congress)
        
        # Inject bot reference into congress for notifications
        self.congress.set_telegram_bot(self.bot)
        
        logger.info("🏛️  Congress + Telegram system initialized")
    
    def run_congress_loop(self):
        """Run congress in separate thread (blocking)"""
        try:
            logger.info("🔄 Starting autonomous congress cycles...")
            
            # Run infinite cycles (congress never stops unless paused by Leo)
            while True:
                self.congress.run_autonomous_cycle(
                    target_system="niche_discovery",
                    cycles=1  # One cycle at a time
                )
                
                # Wait between cycles (1 hour in production)
                import time
                logger.info("⏳ Waiting 1 hour before next congress cycle...")
                time.sleep(3600)  # 1 hour
                
        except KeyboardInterrupt:
            logger.info("🛑 Congress stopped by user")
        except Exception as e:
            logger.error(f"❌ Congress error: {e}", exc_info=True)
    
    async def run_async(self):
        """Run both Congress and Telegram bot asynchronously"""
        
        # Start Telegram bot
        await self.bot.start_async()
        logger.info("✅ Telegram bot started")
        
        # Start congress in thread (blocking operation)
        congress_thread = threading.Thread(
            target=self.run_congress_loop,
            daemon=True
        )
        congress_thread.start()
        logger.info("✅ Congress thread started")
        
        # Keep bot running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Shutting down...")
            await self.bot.stop_async()
    
    def run(self):
        """Main entry point"""
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            logger.info("👋 Goodbye!")
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}", exc_info=True)
            sys.exit(1)

def main():
    """Entry point"""
    
    print("=" * 70)
    print("🏛️  D8 AUTONOMOUS CONGRESS + TELEGRAM INTERFACE")
    print("=" * 70)
    print()
    print("Características:")
    print("  ✅ Congreso opera autónomamente (principio D8)")
    print("  ✅ Leo recibe notificaciones de cambios importantes")
    print("  ✅ Leo puede consultar estado via Telegram")
    print("  ✅ Leo puede asignar tareas específicas")
    print("  ✅ Leo puede pausar/reanudar si necesario")
    print()
    print("Modo por defecto: AUTONOMO")
    print("Intervención Leo: OPCIONAL")
    print()
    print("Iniciando sistema...")
    print("=" * 70)
    print()
    
    system = CongressWithTelegram()
    system.run()

if __name__ == "__main__":
    main()
