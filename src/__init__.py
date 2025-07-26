"""
Telegram Jobs Bot - Smart Job Notification Bot for Freelancers

This package contains all the modules for the Telegram Jobs Bot,
a smart bot that sends personalized job notifications to freelancers
based on their preferences and skills.

Author: Manus AI
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Manus AI"
__email__ = "support@manus.ai"

# Package imports
from .bot import TelegramJobsBot
from .database import SupabaseManager
from .scrapers import ScrapingManager
from .scheduler import JobNotificationScheduler

__all__ = [
    "TelegramJobsBot",
    "SupabaseManager", 
    "ScrapingManager",
    "NotificationScheduler"
]

