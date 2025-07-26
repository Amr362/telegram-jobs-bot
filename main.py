#!/usr/bin/env python3
"""
Telegram Jobs Bot - Main Application
====================================

A comprehensive Telegram bot for job seekers that provides:
- Daily personalized job notifications
- Job search and filtering
- Opinion collection and sentiment analysis
- Link verification
- Support system
- User preference management

Author: Manus AI
Version: 1.0.0
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Optional

from telegram import Update, Bot
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ConversationHandler,
    filters
)
from telegram.error import TelegramError

# Import our modules
from src.utils.config import Config
from src.utils.logger import setup_logging, get_logger
from src.database.manager import SupabaseManager
from src.bot.handlers import BotHandlers
from src.bot.conversation import ConversationManager
from src.bot.support_handlers import SupportHandlers
from src.scheduler.job_scheduler import JobNotificationScheduler
from src.scheduler.notification_manager import AdvancedNotificationManager
from src.scrapers.manager import ScrapingManager
from src.utils.opinion_collector import OpinionCollector
from src.utils.link_checker import LinkChecker

# Setup logging
setup_logging()
logger = get_logger(__name__)

class TelegramJobsBot:
    """Main bot application class."""
    
    def __init__(self):
        """Initialize the bot application."""
        self.config = Config()
        self.application: Optional[Application] = None
        self.db_manager: Optional[SupabaseManager] = None
        self.scheduler: Optional[JobNotificationScheduler] = None
        self.notification_manager: Optional[AdvancedNotificationManager] = None
        self.is_running = False
        
        logger.info("TelegramJobsBot initialized")
    
    async def initialize(self):
        """Initialize all bot components."""
        try:
            logger.info("Initializing bot components...")
            
            # Initialize database manager
            self.db_manager = SupabaseManager(
                url=self.config.SUPABASE_URL,
                key=self.config.SUPABASE_KEY
            )
            await self.db_manager.initialize()
            
            # Create bot application
            self.application = Application.builder().token(self.config.BOT_TOKEN).build()
            
            # Initialize managers
            self.notification_manager = AdvancedNotificationManager(
                self.application.bot, 
                self.db_manager
            )
            
            self.scheduler = JobNotificationScheduler(
                self.application.bot,
                self.db_manager
            )
            
            # Initialize handlers
            await self._setup_handlers()
            
            logger.info("Bot components initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing bot: {e}")
            raise
    
    async def _setup_handlers(self):
        """Setup all bot handlers."""
        try:
            logger.info("Setting up bot handlers...")
            
            # Initialize handler classes
            bot_handlers = BotHandlers(self.db_manager, self.scheduler, self.notification_manager)
            conversation_manager = ConversationManager(self.db_manager)
            support_handlers = SupportHandlers(self.db_manager)
            
            # Setup conversation handler for user onboarding
            setup_conversation = ConversationHandler(
                entry_points=[CommandHandler("start", conversation_manager.start_command)],
                states=conversation_manager.get_conversation_states(),
                fallbacks=[CommandHandler("cancel", conversation_manager.cancel_command)],
                name="user_setup",
                persistent=False
            )
            
            # Setup support conversation handler
            support_conversation = ConversationHandler(
                entry_points=[CommandHandler("support", support_handlers.support_command)],
                states={
                    support_handlers.SUPPORT_CATEGORY: [
                        CallbackQueryHandler(support_handlers.support_category_selected)
                    ],
                    support_handlers.SUPPORT_QUESTION: [
                        CallbackQueryHandler(support_handlers.support_question_received),
                        MessageHandler(filters.TEXT & ~filters.COMMAND, support_handlers.support_question_received)
                    ]
                },
                fallbacks=[CommandHandler("cancel", conversation_manager.cancel_command)],
                name="support_system",
                persistent=False
            )
            
            # Add conversation handlers
            self.application.add_handler(setup_conversation)
            self.application.add_handler(support_conversation)
            
            # Add command handlers
            self.application.add_handler(CommandHandler("help", bot_handlers.help_command))
            self.application.add_handler(CommandHandler("profile", bot_handlers.profile_command))
            self.application.add_handler(CommandHandler("settings", bot_handlers.settings_command))
            self.application.add_handler(CommandHandler("search", bot_handlers.search_command))
            self.application.add_handler(CommandHandler("jobs", bot_handlers.jobs_command))
            self.application.add_handler(CommandHandler("saved", bot_handlers.saved_jobs_command))
            self.application.add_handler(CommandHandler("stats", bot_handlers.stats_command))
            self.application.add_handler(CommandHandler("notifications", bot_handlers.notifications_command))
            self.application.add_handler(CommandHandler("job_support", support_handlers.job_support_command))
            
            # Admin commands
            self.application.add_handler(CommandHandler("admin", bot_handlers.admin_command))
            self.application.add_handler(CommandHandler("broadcast", bot_handlers.broadcast_command))
            self.application.add_handler(CommandHandler("system_stats", bot_handlers.system_stats_command))
            self.application.add_handler(CommandHandler("force_scrape", bot_handlers.force_scrape_command))
            
            # Callback query handlers
            self.application.add_handler(CallbackQueryHandler(bot_handlers.handle_callback_query))
            self.application.add_handler(CallbackQueryHandler(support_handlers.handle_support_callbacks, pattern="^(show_|job_support_|search_detail_)"))
            
            # Message handlers
            self.application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                bot_handlers.handle_text_message
            ))
            
            # Error handler
            self.application.add_error_handler(self._error_handler)
            
            logger.info("Bot handlers setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up handlers: {e}")
            raise
    
    async def _error_handler(self, update: Update, context):
        """Handle errors in bot operations."""
        try:
            logger.error(f"Bot error: {context.error}")
            
            if update and update.effective_chat:
                error_message = (
                    "عذراً، حدث خطأ غير متوقع. 😔\n\n"
                    "يرجى المحاولة مرة أخرى أو استخدام /help للحصول على المساعدة."
                )
                
                try:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=error_message
                    )
                except TelegramError:
                    pass  # Ignore if we can't send error message
            
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
    
    async def start(self):
        """Start the bot."""
        try:
            if self.is_running:
                logger.warning("Bot is already running")
                return
            
            logger.info("Starting Telegram Jobs Bot...")
            
            # Initialize if not already done
            if not self.application:
                await self.initialize()
            
            # Start scheduler
            await self.scheduler.start()
            
            # Start bot polling
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=Update.ALL_TYPES
            )
            
            self.is_running = True
            
            logger.info("🤖 Telegram Jobs Bot started successfully!")
            logger.info(f"Bot username: @{self.application.bot.username}")
            logger.info("Bot is now listening for messages...")
            
            # Send startup notification to admin
            await self._send_startup_notification()
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    async def stop(self):
        """Stop the bot gracefully."""
        try:
            if not self.is_running:
                logger.warning("Bot is not running")
                return
            
            logger.info("Stopping Telegram Jobs Bot...")
            
            # Stop scheduler
            if self.scheduler:
                await self.scheduler.stop()
            
            # Stop bot
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            
            # Close database connections
            if self.db_manager:
                await self.db_manager.close()
            
            self.is_running = False
            
            logger.info("Telegram Jobs Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
    
    async def _send_startup_notification(self):
        """Send startup notification to admin."""
        try:
            if self.config.ADMIN_USER_ID:
                startup_message = (
                    "🚀 **بوت الوظائف بدأ العمل!**\n\n"
                    f"⏰ الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"🤖 البوت: @{self.application.bot.username}\n"
                    f"📊 الحالة: نشط ويعمل بكامل طاقته\n\n"
                    "جميع الأنظمة تعمل بشكل طبيعي! ✅"
                )
                
                await self.application.bot.send_message(
                    chat_id=self.config.ADMIN_USER_ID,
                    text=startup_message,
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            logger.warning(f"Could not send startup notification: {e}")
    
    async def run_forever(self):
        """Run the bot until interrupted."""
        try:
            await self.start()
            
            # Keep running until interrupted
            while self.is_running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            await self.stop()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}")
            self.is_running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def health_check(self) -> dict:
        """Perform health check on all components."""
        try:
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'healthy',
                'components': {}
            }
            
            # Check bot
            try:
                bot_info = await self.application.bot.get_me()
                health_status['components']['bot'] = {
                    'status': 'healthy',
                    'username': bot_info.username,
                    'id': bot_info.id
                }
            except Exception as e:
                health_status['components']['bot'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['overall_status'] = 'degraded'
            
            # Check database
            try:
                db_status = await self.db_manager.health_check()
                health_status['components']['database'] = {
                    'status': 'healthy' if db_status else 'unhealthy'
                }
            except Exception as e:
                health_status['components']['database'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['overall_status'] = 'degraded'
            
            # Check scheduler
            try:
                scheduler_status = await self.scheduler.get_scheduler_status()
                health_status['components']['scheduler'] = {
                    'status': 'healthy' if scheduler_status['is_running'] else 'unhealthy',
                    'jobs_count': scheduler_status.get('total_jobs', 0)
                }
            except Exception as e:
                health_status['components']['scheduler'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['overall_status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'unhealthy',
                'error': str(e)
            }

async def main():
    """Main entry point."""
    try:
        # Create bot instance
        bot = TelegramJobsBot()
        
        # Setup signal handlers
        bot.setup_signal_handlers()
        
        # Run bot
        await bot.run_forever()
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            print("Error: Python 3.8 or higher is required")
            sys.exit(1)
        
        # Run the bot
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

