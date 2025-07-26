import os
from typing import Optional
from dotenv import load_dotenv

class Config:
    """Configuration class for the Telegram Jobs Bot."""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Telegram Bot Configuration
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required but not found in environment variables")
        
        # Supabase Configuration
        self.SUPABASE_URL = os.getenv("SUPABASE_URL")
        self.SUPABASE_KEY = os.getenv("SUPABASE_KEY")
        if not self.SUPABASE_URL or not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY are required but not found in environment variables")
        
        # Database Configuration
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE", "logs/bot.log")
        
        # Scheduler Configuration
        self.TIMEZONE = os.getenv("TIMEZONE", "UTC")
        self.DAILY_NOTIFICATION_TIME = os.getenv("DAILY_NOTIFICATION_TIME", "09:00")
        
        # Scraping Configuration
        self.SCRAPING_DELAY = int(os.getenv("SCRAPING_DELAY", "2"))
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
        self.USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # Social Media APIs
        self.REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
        self.REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
        self.REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "JobBot/1.0")
        self.TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
        
        # Rate Limiting
        self.MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60"))
        self.MAX_JOBS_PER_NOTIFICATION = int(os.getenv("MAX_JOBS_PER_NOTIFICATION", "5"))
        
        # Feature Flags
        self.ENABLE_OPINION_GATHERING = os.getenv("ENABLE_OPINION_GATHERING", "false").lower() == "true"
        self.ENABLE_LINK_VERIFICATION = os.getenv("ENABLE_LINK_VERIFICATION", "true").lower() == "true"
        self.ENABLE_PREMIUM_FEATURES = os.getenv("ENABLE_PREMIUM_FEATURES", "false").lower() == "true"
        
        # Development Settings
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.TESTING = os.getenv("TESTING", "false").lower() == "true"
    
    def validate(self) -> bool:
        """Validates that all required configuration values are present."""
        required_fields = [
            "TELEGRAM_BOT_TOKEN",
            "SUPABASE_URL", 
            "SUPABASE_KEY"
        ]
        
        for field in required_fields:
            if not getattr(self, field):
                raise ValueError(f"Required configuration field {field} is missing")
        
        return True

def load_config() -> Config:
    """Loads and validates the configuration."""
    config = Config()
    config.validate()
    return config

