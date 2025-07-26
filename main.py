#!/usr/bin/env python3
""" Telegram Jobs Bot - Main Application

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
from datetime import datetime, timedelta
from typing import Optional

from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from telegram.error import TelegramError

# Import our modules
from src.utils.config import Config
from src.utils.logger import setup_logging, get_logger
from src.database.manager import SupabaseManager
from src.bot.handlers import BotHandlers
from src.bot.conversation import ConversationManager
from src.scheduler.job_scheduler import JobNotificationScheduler
from src.scheduler.notification_manager import AdvancedNotificationManager
from src.scrapers.manager import ScrapingManager # Changed from JobScraper
from src.utils.opinion_collector import OpinionCollector
from src.utils.link_checker import LinkChecker

# Setup logging
setup_logging()
logger = get_logger(__name__)

class TelegramJobsBot:
    """Main bot application class."""

    def __init__(self):
        self.config = Config()
        self.application: Optional[Application] = None
        self.db_manager: Optional[SupabaseManager] = None
        self.scheduler: Optional[JobNotificationScheduler] = None
        self.notification_manager: Optional[AdvancedNotificationManager] = None
        self.scraping_manager: Optional[ScrapingManager] = None # Changed from JobScraper
        self.opinion_collector: Optional[OpinionCollector] = None
        self.link_checker: Optional[LinkChecker] = None

    async def initialize(self):
        """Initializes the bot components."""
        logger.info("Initializing bot components...")

        # Initialize Supabase Manager
        self.db_manager = SupabaseManager(
            self.config.SUPABASE_URL,
            self.config.SUPABASE_KEY
        )
        await self.db_manager.connect()
        logger.info("SupabaseManager initialized and connected.")

        # Initialize Scraping Manager
        self.scraping_manager = ScrapingManager(self.db_manager)
        logger.info("ScrapingManager initialized.")

        # Initialize Notification Manager
        self.notification_manager = AdvancedNotificationManager(self.db_manager)
        logger.info("NotificationManager initialized.")

        # Initialize Job Notification Scheduler
        self.scheduler = JobNotificationScheduler(
            self.db_manager,
            self.notification_manager,
            self.scraping_manager,
            self.config.NOTIFICATION_INTERVAL_MINUTES
        )
        logger.info("JobNotificationScheduler initialized.")

        # Initialize Opinion Collector
        self.opinion_collector = OpinionCollector(self.db_manager)
        logger.info("OpinionCollector initialized.")

        # Initialize Link Checker
        self.link_checker = LinkChecker(self.db_manager)
        logger.info("LinkChecker initialized.")

        # Initialize Bot Application
        self.application = (
            Application.builder()
            .token(self.config.TELEGRAM_BOT_TOKEN)
            .build()
        )
        logger.info("Telegram Application built.")

        # Setup handlers
        bot_handlers = BotHandlers(self.db_manager, self.scraping_manager, self.opinion_collector, self.link_checker)
        conversation_manager = ConversationManager(self.db_manager, self.scraping_manager)

        self.application.add_handler(CommandHandler("start", bot_handlers.start))
        self.application.add_handler(CommandHandler("help", bot_handlers.help_command))
        self.application.add_handler(CommandHandler("settings", bot_handlers.settings))
        self.application.add_handler(CommandHandler("search", bot_handlers.search_command))
        self.application.add_handler(CommandHandler("latest_jobs", bot_handlers.latest_jobs))
        self.application.add_handler(CommandHandler("feedback", bot_handlers.feedback_command))
        self.application.add_handler(CommandHandler("cancel", bot_handlers.cancel_command))
        self.application.add_handler(CommandHandler("stats", bot_handlers.stats_command))

        self.application.add_handler(
            ConversationHandler(
                entry_points=[CommandHandler("set_preferences", conversation_manager.set_preferences_start)],
                states={
                    conversation_manager.LANGUAGE: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_manager.set_language)
                    ],
                    conversation_manager.LOCATION: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_manager.set_location)
                    ],
                    conversation_manager.COUNTRY: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_manager.set_country)
                    ],
                    conversation_manager.SKILLS: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_manager.set_skills)
                    ],
                    conversation_manager.FREQUENCY: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_manager.set_frequency)
                    ],
                    conversation_manager.TIMES: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, conversation_manager.set_times)
                    ],
                },
                fallbacks=[CommandHandler("cancel", conversation_manager.cancel_preferences)],
            )
        )

        self.application.add_handler(CallbackQueryHandler(bot_handlers.button_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handlers.echo))

        logger.info("Bot handlers set up.")

    async def start_polling(self):
        """Starts the bot polling for updates."""
        if self.application:
            logger.info("Starting bot polling...")
            await self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        else:
            logger.error("Application not initialized. Call initialize() first.")

    async def start_scheduler(self):
        """Starts the job notification scheduler."""
        if self.scheduler:
            logger.info("Starting job notification scheduler...")
            await self.scheduler.start()
        else:
            logger.error("Scheduler not initialized. Call initialize() first.")

    async def start_link_checker(self):
        """Starts the link checker."""
        if self.link_checker:
            logger.info("Starting link checker...")
            await self.link_checker.start()
        else:
            logger.error("Link checker not initialized. Call initialize() first.")

    async def stop_all(self):
        """Stops all running components of the bot."""
        logger.info("Stopping all bot components...")
        if self.scheduler:
            await self.scheduler.stop()
        if self.link_checker:
            await self.link_checker.stop()
        if self.db_manager:
            await self.db_manager.disconnect()
        if self.application:
            await self.application.stop()
        logger.info("All bot components stopped.")

async def main():
    bot = TelegramJobsBot()
    await bot.initialize()

    # Start polling and scheduler in parallel
    await asyncio.gather(
        bot.start_polling(),
        bot.start_scheduler(),
        bot.start_link_checker()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except TelegramError as e:
        logger.error(f"Telegram error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)


