import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from src.utils.config import load_config
from src.utils.logger import setup_logger, get_logger
from src.bot.handlers import CommandHandlers, CallbackHandlers, MessageHandlers, ErrorHandlers
from src.bot.conversation import ConversationState

class TelegramJobsBot:
    """Main Telegram Jobs Bot class."""
    
    def __init__(self):
        # Load configuration
        self.config = load_config()
        
        # Setup logging
        setup_logger(self.config.LOG_LEVEL, self.config.LOG_FILE)
        self.logger = get_logger(__name__)
        
        # Initialize handlers
        self.command_handlers = CommandHandlers()
        self.callback_handlers = CallbackHandlers()
        self.message_handlers = MessageHandlers()
        
        # Initialize application
        self.application = None
        
        self.logger.info("Telegram Jobs Bot initialized")
    
    def setup_handlers(self):
        """Sets up all bot handlers."""
        
        # Conversation handler for onboarding
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.command_handlers.start_command)],
            states={
                ConversationState.LANGUAGE_SELECTION.value: [
                    CallbackQueryHandler(self.callback_handlers.handle_callback_query, pattern='^lang_')
                ],
                ConversationState.LOCATION_PREFERENCE.value: [
                    CallbackQueryHandler(self.callback_handlers.handle_callback_query, pattern='^location_')
                ],
                ConversationState.SKILLS_INPUT.value: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handlers.handle_text_message)
                ],
                ConversationState.NOTIFICATION_FREQUENCY.value: [
                    CallbackQueryHandler(self.callback_handlers.handle_callback_query, pattern='^freq_')
                ],
                ConversationState.CONFIRMATION.value: [
                    CallbackQueryHandler(self.callback_handlers.handle_callback_query, pattern='^confirm_')
                ]
            },
            fallbacks=[CommandHandler('start', self.command_handlers.start_command)],
            per_user=True,
            per_chat=True
        )
        
        # Add conversation handler
        self.application.add_handler(conversation_handler)
        
        # Command handlers
        self.application.add_handler(CommandHandler('help', self.command_handlers.help_command))
        self.application.add_handler(CommandHandler('profile', self.command_handlers.profile_command))
        self.application.add_handler(CommandHandler('settings', self.command_handlers.settings_command))
        self.application.add_handler(CommandHandler('search', self.command_handlers.search_command))
        self.application.add_handler(CommandHandler('jobs', self.command_handlers.jobs_command))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self.callback_handlers.handle_callback_query))
        
        # Message handlers
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.message_handlers.handle_text_message
        ))
        
        # Unknown command handler
        self.application.add_handler(MessageHandler(
            filters.COMMAND, 
            self.message_handlers.handle_unknown_command
        ))
        
        # Error handler
        self.application.add_error_handler(ErrorHandlers.error_handler)
        
        self.logger.info("All handlers set up successfully")
    
    async def start_bot(self):
        """Starts the bot."""
        try:
            # Create application
            self.application = Application.builder().token(self.config.TELEGRAM_BOT_TOKEN).build()
            
            # Setup handlers
            self.setup_handlers()
            
            # Start the bot
            self.logger.info("Starting Telegram Jobs Bot...")
            await self.application.initialize()
            await self.application.start()
            
            # Start polling
            self.logger.info("Bot is now running and polling for updates...")
            await self.application.updater.start_polling(
                allowed_updates=['message', 'callback_query'],
                drop_pending_updates=True
            )
            
            # Keep the bot running
            await self.application.updater.idle()
            
        except Exception as e:
            self.logger.error(f"Failed to start bot: {e}")
            raise
        finally:
            # Cleanup
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
    
    def run(self):
        """Runs the bot using asyncio."""
        try:
            asyncio.run(self.start_bot())
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
        except Exception as e:
            self.logger.error(f"Bot crashed: {e}")
            raise

# For running the bot directly
if __name__ == "__main__":
    bot = TelegramJobsBot()
    bot.run()

