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

# Import GitHub Copilot for intelligent responses
from app.integrations.github_copilot import get_copilot_client
from app.integrations.filesystem_manager import get_filesystem_manager

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
        
        # GitHub Copilot integration for intelligent responses
        self.copilot = get_copilot_client()
        
        # FileSystem manager for file operations
        self.fs_manager = get_filesystem_manager()
        
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
        
        # File operations commands
        self.app.add_handler(CommandHandler("ls", self.cmd_list_files))
        self.app.add_handler(CommandHandler("read", self.cmd_read_file))
        self.app.add_handler(CommandHandler("write", self.cmd_write_file))
        self.app.add_handler(CommandHandler("search", self.cmd_search_files))
        self.app.add_handler(CommandHandler("git_status", self.cmd_git_status))
        self.app.add_handler(CommandHandler("commit", self.cmd_git_commit))
        self.app.add_handler(CommandHandler("pr", self.cmd_create_pr))
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
            "*Congreso:*\n"
            "• Estado: /status\n"
            "• Experimentos: /experiments\n"
            "• Tarea: /task <desc>\n"
            "• Pausar: /stop | /resume\n\n"
            "*Archivos:*\n"
            "• Listar: /ls [dir]\n"
            "• Leer: /read <archivo>\n"
            "• Buscar: /search <patrón>\n\n"
            "*Git:*\n"
            "• Status: /git_status\n"
            "• Commit: /commit\n"
            "• PR: /pr\n\n"
            "• Ayuda: /help\n\n"
            "También puedes escribir en lenguaje natural.",
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

*Consulta del Congreso:*
/status - Estado actual del congreso
/experiments - Experimentos recientes

*Control del Congreso:*
/approve - Toggle aprobación automática/manual
/task <desc> - Asignar tarea específica
/stop - Pausar congreso
/resume - Reanudar congreso

*Gestión de Archivos:*
/ls [dir] - Listar archivos en directorio
/read <archivo> - Leer contenido de archivo
/write <archivo> <contenido> - Escribir archivo
/search <patrón> - Buscar archivos

*Git & GitHub:*
/git_status - Ver estado de git
/commit <archivos> -m 'mensaje' - Hacer commit
/pr 'título' -d 'descripción' - Crear Pull Request

*Conversación Natural:*
También puedes escribir directamente:
• "¿Qué está haciendo el congreso?"
• "Lee el archivo app/config.py"
• "Optimiza los prompts para mejor SEO"
• "Crea un PR con los cambios recientes"

El bot interpreta lenguaje natural y responde apropiadamente.

*Rutas permitidas:*
• d8/ - Proyecto principal
• ~/Documents/d8_data/ - Datos y configuración
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle natural language messages with GitHub Copilot intelligence"""
        text = update.message.text
        text_lower = text.lower()
        
        # Check if it's a question about the project
        question_indicators = ['qué', 'que', 'cómo', 'como', 'por qué', 'porque', 'cuál', 'cual', 
                               'dónde', 'donde', 'cuándo', 'cuando', 'quién', 'quien',
                               'explain', 'explica', 'what', 'how', 'why', 'where', 'who', 'when',
                               '?']  # Any question mark indicates a question
        
        is_question = any(indicator in text_lower for indicator in question_indicators)
        
        # Check for command routing keywords
        command_keywords = {
            'estado': ['estado', 'status', 'cómo está', 'como está', 'que hace', 'qué hace'],
            'experimentos': ['experimentos', 'pruebas', 'tests'],
            'pausar': ['pausar', 'detener', 'stop', 'parar'],
            'reanudar': ['reanudar', 'continuar', 'resume', 'seguir'],
            'tarea': ['optimiza', 'mejora', 'investiga', 'analiza'],
            'leer': ['lee', 'leer', 'muestra', 'mostrar', 'ver archivo', 'read'],
            'listar': ['lista archivos', 'listar', 'ls', 'dir', 'archivos en'],
            'buscar': ['busca', 'buscar', 'encuentra', 'search', 'find'],
            'git': ['git status', 'cambios en git', 'estado git', 'qué cambió']
        }
        
        # Check for command routing first (higher priority than generic questions)
        for cmd, keywords in command_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                if cmd == 'estado':
                    await self.cmd_status(update, context)
                    return
                elif cmd == 'experimentos':
                    await self.cmd_experiments(update, context)
                    return
                elif cmd == 'pausar':
                    await self.cmd_stop_congress(update, context)
                    return
                elif cmd == 'reanudar':
                    await self.cmd_resume_congress(update, context)
                    return
                elif cmd == 'tarea':
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
                    return
        
        # If it's a question and Copilot is available, use it
        if is_question and self.copilot.enabled:
            # Use GitHub Copilot for intelligent response
            await update.message.reply_text("🧠 Consultando con conocimiento del proyecto...")
            
            try:
                intelligent_response = self.copilot.ask_about_project(update.message.text)
                # Send without Markdown to avoid parse errors
                await update.message.reply_text(f"💡 {intelligent_response}")
                return
            except Exception as e:
                logger.error(f"Copilot error: {e}")
                # Fall through to fallback
        
        # Fallback: If GitHub Copilot is available, try it anyway
        if self.copilot.enabled:
            await update.message.reply_text("🧠 Analizando con contexto del proyecto...")
            
            try:
                intelligent_response = self.copilot.ask_about_project(update.message.text)
                # Send without Markdown to avoid parse errors
                await update.message.reply_text(f"💡 {intelligent_response}")
            except Exception as e:
                logger.error(f"Copilot error: {e}")
                await update.message.reply_text(
                    "🤔 No estoy seguro de qué necesitas.\n\n"
                    "Intenta:\n"
                    "• /help para ver comandos\n"
                    "• /status para ver estado\n"
                    "• O describe una tarea específica"
                )
        else:
            # Fallback without Copilot
            await update.message.reply_text(
                "🤔 No estoy seguro de qué necesitas.\n\n"
                "Intenta:\n"
                "• /help para ver comandos\n"
                "• /status para ver estado\n"
                "• O describe una tarea específica\n\n"
                "💡 Tip: Configura GITHUB_TOKEN en .env para respuestas más inteligentes."
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
    
    async def cmd_list_files(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List files in directory"""
        path = context.args[0] if context.args else "."
        
        try:
            result = self.fs_manager.list_directory(path)
            
            if "error" in result:
                await update.message.reply_text(f"❌ {result['error']}")
                return
            
            message = f"📁 *{result['path']}*\n\n"
            
            if result['directories']:
                message += "*Directorios:*\n"
                for dir_name in result['directories'][:20]:  # Limit to 20
                    message += f"📁 {dir_name}\n"
                if len(result['directories']) > 20:
                    message += f"... y {len(result['directories']) - 20} más\n"
                message += "\n"
            
            if result['files']:
                message += "*Archivos:*\n"
                for file in result['files'][:20]:  # Limit to 20
                    size_kb = file['size'] / 1024
                    message += f"📄 {file['name']} ({size_kb:.1f}KB)\n"
                if len(result['files']) > 20:
                    message += f"... y {len(result['files']) - 20} más\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def cmd_read_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Read file contents"""
        if not context.args:
            await update.message.reply_text(
                "❌ Uso: /read <archivo>\n\n"
                "Ejemplos:\n"
                "/read app/config.py\n"
                "/read README.md"
            )
            return
        
        file_path = " ".join(context.args)
        
        try:
            result = self.fs_manager.read_file(file_path)
            
            if "error" in result:
                await update.message.reply_text(f"❌ {result['error']}")
                return
            
            content = result['content']
            
            # Truncate if too long for Telegram (4096 char limit)
            if len(content) > 3500:
                content = content[:3500] + "\n\n... (truncado, archivo muy largo)"
            
            message = (
                f"📄 *{result['path']}*\n"
                f"Tamaño: {result['size']} bytes | Líneas: {result['lines']}\n\n"
                f"```\n{content}\n```"
            )
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def cmd_write_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Write content to file (requires confirmation)"""
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Uso: /write <archivo> <contenido>\n\n"
                "⚠️ Esto sobrescribirá el archivo existente.\n"
                "Se creará un backup automáticamente.\n\n"
                "Ejemplo:\n"
                "/write test.txt Hola mundo"
            )
            return
        
        file_path = context.args[0]
        content = " ".join(context.args[1:])
        
        try:
            result = self.fs_manager.write_file(file_path, content, create_backup=True)
            
            if "error" in result:
                await update.message.reply_text(f"❌ {result['error']}")
                return
            
            message = (
                f"✅ *Archivo escrito*\n\n"
                f"📄 {result['path']}\n"
                f"📝 {result['bytes_written']} bytes escritos\n"
            )
            
            if 'backup_path' in result:
                message += f"💾 Backup: {result['backup_path']}\n"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def cmd_search_files(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Search for files"""
        if not context.args:
            await update.message.reply_text(
                "❌ Uso: /search <patrón>\n\n"
                "Ejemplos:\n"
                "/search *.py\n"
                "/search test_\n"
                "/search config"
            )
            return
        
        pattern = " ".join(context.args)
        
        try:
            matches = self.fs_manager.search_files(pattern)
            
            if not matches:
                await update.message.reply_text(f"🔍 No se encontraron archivos para: {pattern}")
                return
            
            message = f"🔍 *Resultados para: {pattern}*\n\n"
            
            for match in matches[:30]:  # Limit to 30
                message += f"📄 {match}\n"
            
            if len(matches) > 30:
                message += f"\n... y {len(matches) - 30} más"
            
            message += f"\n\n*Total:* {len(matches)} archivos"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def cmd_git_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get git status"""
        try:
            result = self.fs_manager.git_status()
            
            if "error" in result:
                await update.message.reply_text(f"❌ {result['error']}")
                return
            
            message = f"🔀 *Git Status*\n\nBranch: `{result['branch']}`\n\n"
            
            if result['modified']:
                message += "*Modificados:*\n"
                for file in result['modified'][:15]:
                    message += f"📝 {file}\n"
                if len(result['modified']) > 15:
                    message += f"... y {len(result['modified']) - 15} más\n"
                message += "\n"
            
            if result['untracked']:
                message += "*Sin seguimiento:*\n"
                for file in result['untracked'][:15]:
                    message += f"❓ {file}\n"
                if len(result['untracked']) > 15:
                    message += f"... y {len(result['untracked']) - 15} más\n"
                message += "\n"
            
            if result['staged']:
                message += "*Preparados (staged):*\n"
                for file in result['staged'][:15]:
                    message += f"✅ {file}\n"
                message += "\n"
            
            if not result['modified'] and not result['untracked'] and not result['staged']:
                message += "✨ Working tree limpio"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def cmd_git_commit(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Commit changes"""
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Uso: /commit <archivos...> -m <mensaje>\n\n"
                "Ejemplos:\n"
                "/commit app/config.py -m 'feat: Update config'\n"
                "/commit . -m 'docs: Update README'"
            )
            return
        
        # Parse args
        args = context.args
        try:
            m_index = args.index('-m')
            files = args[:m_index]
            message = " ".join(args[m_index + 1:])
        except (ValueError, IndexError):
            await update.message.reply_text("❌ Falta el mensaje. Usa: -m 'mensaje'")
            return
        
        try:
            result = self.fs_manager.git_commit(
                files=files,
                message=message
            )
            
            if "error" in result:
                await update.message.reply_text(f"❌ {result['error']}")
                return
            
            response = (
                f"✅ *Commit exitoso*\n\n"
                f"Hash: `{result['commit_hash'][:8]}`\n"
                f"Mensaje: {result['message']}\n\n"
                f"Usa /pr para crear Pull Request"
            )
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
    async def cmd_create_pr(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create pull request"""
        if len(context.args) < 2:
            await update.message.reply_text(
                "❌ Uso: /pr <título> -d <descripción>\n\n"
                "Ejemplo:\n"
                "/pr 'feat: New feature' -d 'Adds X functionality'"
            )
            return
        
        # Parse args
        args = context.args
        try:
            d_index = args.index('-d')
            title = " ".join(args[:d_index])
            body = " ".join(args[d_index + 1:])
        except (ValueError, IndexError):
            title = " ".join(args)
            body = "Pull request creado por D8 Autonomous Congress"
        
        try:
            # Push first
            push_result = self.fs_manager.push_to_github()
            
            if "error" in push_result:
                await update.message.reply_text(
                    f"⚠️ Error al hacer push: {push_result['error']}\n"
                    "Asegúrate de tener commits para pushear."
                )
                return
            
            # Create PR
            result = self.fs_manager.create_pull_request(
                title=title,
                body=body
            )
            
            if "error" in result:
                await update.message.reply_text(f"❌ {result['error']}")
                return
            
            response = (
                f"✅ *Pull Request creado*\n\n"
                f"Número: #{result['pr_number']}\n"
                f"Título: {title}\n"
                f"Estado: {result['state']}\n\n"
                f"🔗 {result['pr_url']}"
            )
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    
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
