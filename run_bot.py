#!/usr/bin/env python3
"""
Simple Bot Runner
================

A simple script to run the Telegram Jobs Bot.
This script handles environment setup and basic error handling.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        'BOT_TOKEN',
        'SUPABASE_URL',
        'SUPABASE_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        return False
    
    return True

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    return True

async def main():
    """Main entry point for the bot."""
    print("🤖 Starting Telegram Jobs Bot...")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Load environment variables from .env file
    try:
        from dotenv import load_dotenv
        env_file = project_root / '.env'
        if env_file.exists():
            load_dotenv(env_file)
            print("✅ Environment variables loaded from .env file")
        else:
            print("⚠️  No .env file found, using system environment variables")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment variables")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    try:
        # Import and run the main bot
        from main import TelegramJobsBot
        
        bot = TelegramJobsBot()
        bot.setup_signal_handlers()
        
        print("🚀 Bot is starting up...")
        await bot.run_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Startup error: {e}")
        sys.exit(1)

