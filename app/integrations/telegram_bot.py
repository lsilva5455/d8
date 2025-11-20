"""
Telegram Bot for Congress Communication
Leo can communicate with Autonomous Congress via Telegram
"""

import os
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class CongressTelegramBot:
    """
    Telegram bot for Leo to communicate with Autonomous Congress
    
    Features:
    - Query congress status
    - Request specific tasks
    - Approve/reject proposals (optional)
    - Receive notifications of improvements
    - Monitor ongoing experiments
    """
    
    def __init__(self, congress_instance):
        """
        Initialize bot with congress instance
        
        Args:
            congress_instance: Reference to AutonomousCongress
        """
        self.congress = congress_instance
        self.token = os.getenv("TELEGRAM_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.token:
            raise ValueError("TELEGRAM_TOKEN not found in environment")
        
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID not found in environment")
        
        self.app = Application.builder().token(self.token).build()
        self._setup_handlers()
        
        # Pending approvals (if Leo wants manual approval)
        self.pending_approvals = {}
        self.auto_approve = True  # Default: automatic execution
        
        logger.info(f"🤖 Telegram Bot initialized for chat {self.chat_id}")
    
    def _setup_handlers(self):
        """Setup command and message handlers"""
        
        # Commands
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        self.app.add_handler(CommandHandler("experiments", self.cmd_experiments))
        self.app.add_handler(CommandHandler("approve", self.cmd_toggle_approval))
        self.app.add_handler(CommandHandler("task", self.cmd_assign_task))
        self.app.add_handler(CommandHandler("stop", self.cmd_stop_congress))
        self.app.add_handler(CommandHandler("resume", self.cmd_resume_congress))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        
        # Callback queries (buttons)
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Text messages (natural language)
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        ))
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command - welcome message"""
        await update.message.reply_text(
            "🏛️ *Congress Communication System*\n\n"
            "Hola Leo! Este bot te conecta con el Congreso Autónomo.\n\n"
            "*Modo actual:* Ejecución automática\n"
            "El congreso opera sin intervención, pero puedes:\n\n"
            "• Ver estado: /status\n"
            "• Ver experimentos: /experiments\n"
            "• Asignar tarea: /task <descripción>\n"
            "• Toggle aprobación manual: /approve\n"
            "• Pausar congreso: /stop\n"
            "• Reanudar: /resume\n"
            "• Ayuda: /help\n\n"
            "También puedes escribir en lenguaje natural y te responderé.",
            parse_mode='Markdown'
        )
    
    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get current congress status"""
        try:
            status = self.congress.get_status()
            
            message = (
                "📊 *ESTADO DEL CONGRESO*\n\n"
                f"🔄 Generación: {status.get('generation', 0)}\n"
                f"🧪 Experimentos totales: {status.get('total_experiments', 0)}\n"
                f"✅ Mejoras implementadas: {status.get('improvements_implemented', 0)}\n"
                f"⏸️ Estado: {'PAUSADO' if status.get('paused', False) else 'ACTIVO'}\n\n"
                f"*Último experimento:*\n"
                f"{status.get('last_experiment', 'Ninguno')}\n\n"
                f"*Mejora promedio:* {status.get('avg_improvement', 0):.1f}%"
            )
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error obteniendo estado: {e}")
    
    async def cmd_experiments(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List recent experiments"""
        try:
            experiments = self.congress.get_recent_experiments(limit=5)
            
            if not experiments:
                await update.message.reply_text("No hay experimentos recientes.")
                return
            
            message = "🧪 *EXPERIMENTOS RECIENTES*\n\n"
            
            for i, exp in enumerate(experiments, 1):
                status_emoji = "✅" if exp.get('approved') else "❌"
                message += (
                    f"{i}. {status_emoji} *{exp.get('title', 'Sin título')}*\n"
                    f"   Mejora: {exp.get('improvement', 0):.1f}%\n"
                    f"   Fecha: {exp.get('date', 'N/A')}\n\n"
                )
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error obteniendo experimentos: {e}")
    
    async def cmd_toggle_approval(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Toggle automatic approval mode"""
        self.auto_approve = not self.auto_approve
        
        mode = "AUTOMÁTICO" if self.auto_approve else "MANUAL"
        message = (
            f"🔄 Modo de aprobación cambiado a: *{mode}*\n\n"
        )
        
        if self.auto_approve:
            message += (
                "El congreso ejecutará mejoras automáticamente sin esperar aprobación.\n"
                "Solo te notificaré de cambios importantes."
            )
        else:
            message += (
                "El congreso esperará tu aprobación antes de implementar cambios.\n"
                "Te enviaré propuestas para que las revises."
            )
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def cmd_assign_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Assign specific task to congress"""
        if not context.args:
            await update.message.reply_text(
                "❌ Uso: /task <descripción de la tarea>\n\n"
                "Ejemplo:\n"
                "/task Optimizar prompts de agentes para SEO\n"
                "/task Investigar nuevos modelos de IA\n"
                "/task Mejorar tasa de conversión en 20%"
            )
            return
        
        task_description = " ".join(context.args)
        
        try:
            # Assign task to congress
            task_id = self.congress.assign_manual_task(
                description=task_description,
                requested_by="Leo (Telegram)"
            )
            
            await update.message.reply_text(
                f"✅ *Tarea asignada al congreso*\n\n"
                f"ID: `{task_id}`\n"
                f"Descripción: {task_description}\n\n"
                f"El congreso comenzará a trabajar en esto.\n"
                f"Te notificaré cuando complete la investigación.",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error asignando tarea: {e}")
    
    async def cmd_stop_congress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Stop autonomous congress execution"""
        try:
            self.congress.pause()
            
            await update.message.reply_text(
                "⏸️ *Congreso pausado*\n\n"
                "El congreso detendrá ejecución automática.\n"
                "Experimentos en curso se completarán pero no se iniciarán nuevos.\n\n"
                "Usa /resume para reanudar.",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error pausando congreso: {e}")
    
    async def cmd_resume_congress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Resume autonomous congress execution"""
        try:
            self.congress.resume()
            
            await update.message.reply_text(
                "▶️ *Congreso reanudado*\n\n"
                "El congreso continuará con ejecución automática.",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error reanudando congreso: {e}")
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message"""
        help_text = """
🏛️ *COMANDOS DISPONIBLES*

*Consulta:*
/status - Estado actual del congreso
/experiments - Experimentos recientes

*Control:*
/approve - Toggle aprobación automática/manual
/task <desc> - Asignar tarea específica
/stop - Pausar congreso
/resume - Reanudar congreso

*Conversación Natural:*
También puedes escribir directamente:
• "¿Qué está haciendo el congreso?"
• "Optimiza los prompts para mejor SEO"
• "¿Cuántas mejoras se han implementado?"

El bot interpreta lenguaje natural y responde apropiadamente.
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle natural language messages"""
        text = update.message.text.lower()
        
        # Simple NLP routing
        if any(word in text for word in ['estado', 'status', 'cómo está', 'que hace']):
            await self.cmd_status(update, context)
            
        elif any(word in text for word in ['experimentos', 'pruebas', 'tests']):
            await self.cmd_experiments(update, context)
            
        elif any(word in text for word in ['pausar', 'detener', 'stop', 'parar']):
            await self.cmd_stop_congress(update, context)
            
        elif any(word in text for word in ['reanudar', 'continuar', 'resume', 'seguir']):
            await self.cmd_resume_congress(update, context)
            
        elif any(word in text for word in ['optimiza', 'mejora', 'investiga', 'analiza']):
            # Treat as task assignment
            task_description = update.message.text
            try:
                task_id = self.congress.assign_manual_task(
                    description=task_description,
                    requested_by="Leo (Telegram)"
                )
                
                await update.message.reply_text(
                    f"✅ Entendido. He asignado esta tarea al congreso:\n\n"
                    f"*ID:* `{task_id}`\n"
                    f"*Tarea:* {task_description}\n\n"
                    f"Te notificaré cuando tenga resultados.",
                    parse_mode='Markdown'
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {e}")
        
        else:
            # General response
            await update.message.reply_text(
                "🤔 No estoy seguro de qué necesitas.\n\n"
                "Intenta:\n"
                "• /help para ver comandos\n"
                "• /status para ver estado\n"
                "• O describe una tarea específica"
            )
    
    async def handle_callback(self, query_update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = query_update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("approve_"):
            experiment_id = data.replace("approve_", "")
            try:
                self.congress.approve_experiment(experiment_id)
                await query.edit_message_text(
                    f"✅ Experimento {experiment_id} aprobado.\n"
                    f"El congreso implementará los cambios."
                )
            except Exception as e:
                await query.edit_message_text(f"❌ Error: {e}")
                
        elif data.startswith("reject_"):
            experiment_id = data.replace("reject_", "")
            try:
                self.congress.reject_experiment(experiment_id)
                await query.edit_message_text(
                    f"❌ Experimento {experiment_id} rechazado.\n"
                    f"El congreso no implementará estos cambios."
                )
            except Exception as e:
                await query.edit_message_text(f"❌ Error: {e}")
    
    async def notify_leo(self, message: str, markup: Optional[InlineKeyboardMarkup] = None):
        """Send notification to Leo"""
        try:
            await self.app.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown',
                reply_markup=markup
            )
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
    
    async def request_approval(self, experiment: Dict[str, Any]) -> bool:
        """
        Request Leo's approval for an experiment
        Returns True if auto-approve is on, otherwise waits for Leo's response
        """
        if self.auto_approve:
            # Notify but don't wait
            await self.notify_leo(
                f"✅ *Mejora implementada automáticamente*\n\n"
                f"*Experimento:* {experiment.get('title')}\n"
                f"*Mejora:* {experiment.get('improvement', 0):.1f}%\n"
                f"*Descripción:* {experiment.get('description')}\n\n"
                f"Cambios aplicados al sistema."
            )
            return True
        
        # Manual approval mode
        experiment_id = experiment.get('id')
        self.pending_approvals[experiment_id] = experiment
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Aprobar", callback_data=f"approve_{experiment_id}"),
                InlineKeyboardButton("❌ Rechazar", callback_data=f"reject_{experiment_id}")
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        await self.notify_leo(
            f"🔔 *APROBACIÓN REQUERIDA*\n\n"
            f"*Experimento:* {experiment.get('title')}\n"
            f"*Mejora esperada:* {experiment.get('improvement', 0):.1f}%\n"
            f"*Descripción:* {experiment.get('description')}\n\n"
            f"*Cambios propuestos:*\n{experiment.get('changes', 'N/A')}\n\n"
            f"¿Aprobar implementación?",
            markup=markup
        )
        
        # Wait for approval (in real implementation, this would be async)
        return False
    
    def run(self):
        """Start the bot (blocking)"""
        logger.info("🚀 Starting Telegram bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def start_async(self):
        """Start bot asynchronously"""
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        
        # Send startup notification
        await self.notify_leo(
            "🏛️ *Congreso Autónomo iniciado*\n\n"
            f"Modo: {'AUTOMÁTICO' if self.auto_approve else 'MANUAL'}\n"
            f"Estado: ACTIVO\n\n"
            "Usa /help para ver comandos disponibles."
        )
    
    async def stop_async(self):
        """Stop bot asynchronously"""
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Mock congress for testing
    class MockCongress:
        def get_status(self):
            return {
                'generation': 5,
                'total_experiments': 42,
                'improvements_implemented': 15,
                'paused': False,
                'last_experiment': 'Optimización de prompts',
                'avg_improvement': 12.5
            }
        
        def get_recent_experiments(self, limit=5):
            return [
                {'title': 'Test 1', 'improvement': 15.0, 'approved': True, 'date': '2025-11-20'},
                {'title': 'Test 2', 'improvement': 8.5, 'approved': False, 'date': '2025-11-19'},
            ]
        
        def assign_manual_task(self, description, requested_by):
            return f"task_{hash(description) % 10000}"
        
        def pause(self):
            pass
        
        def resume(self):
            pass
        
        def approve_experiment(self, exp_id):
            pass
        
        def reject_experiment(self, exp_id):
            pass
    
    mock_congress = MockCongress()
    bot = CongressTelegramBot(mock_congress)
    bot.run()
