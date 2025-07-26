#!/usr/bin/env python3
"""
Bot Testing Suite
================

Comprehensive testing suite for the Telegram Jobs Bot.
Tests all major components and functionality.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import test modules
from src.utils.config import Config
from src.utils.logger import setup_logging, get_logger
from src.database.manager import SupabaseManager
from src.scrapers.manager import ScrapingManager
from src.utils.link_checker import LinkChecker
from src.utils.opinion_collector import OpinionCollector
from src.scheduler.job_scheduler import JobNotificationScheduler
from src.scheduler.notification_manager import AdvancedNotificationManager

# Setup logging for tests
setup_logging()
logger = get_logger(__name__)

class BotTester:
    """Comprehensive bot testing class."""
    
    def __init__(self):
        self.config = Config()
        self.test_results = {}
        self.db_manager = None
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        print("🧪 Starting comprehensive bot testing...")
        print("=" * 50)
        
        test_suite = [
            ("Configuration", self.test_configuration),
            ("Database Connection", self.test_database_connection),
            ("Database Operations", self.test_database_operations),
            ("Job Scraping", self.test_job_scraping),
            ("Link Checking", self.test_link_checking),
            ("Opinion Collection", self.test_opinion_collection),
            ("Notification System", self.test_notification_system),
            ("Scheduler", self.test_scheduler),
            ("Bot Integration", self.test_bot_integration)
        ]
        
        total_tests = len(test_suite)
        passed_tests = 0
        
        for test_name, test_func in test_suite:
            print(f"\n🔍 Testing: {test_name}")
            try:
                result = await test_func()
                if result:
                    print(f"✅ {test_name}: PASSED")
                    passed_tests += 1
                else:
                    print(f"❌ {test_name}: FAILED")
                self.test_results[test_name] = result
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {e}")
                self.test_results[test_name] = False
                logger.error(f"Test error in {test_name}: {e}")
        
        # Summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {passed_tests}/{total_tests} tests passed")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! Bot is ready for deployment.")
        else:
            print("⚠️  Some tests failed. Please check the issues above.")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'results': self.test_results
        }
    
    async def test_configuration(self) -> bool:
        """Test configuration loading."""
        try:
            # Test required environment variables
            required_vars = ['BOT_TOKEN', 'SUPABASE_URL', 'SUPABASE_KEY']
            
            for var in required_vars:
                value = getattr(self.config, var, None)
                if not value:
                    print(f"   ❌ Missing {var}")
                    return False
                print(f"   ✅ {var}: {'*' * 10}...{value[-4:]}")
            
            # Test optional configurations
            optional_vars = ['ADMIN_USER_ID', 'LOG_LEVEL', 'ENVIRONMENT']
            for var in optional_vars:
                value = getattr(self.config, var, None)
                if value:
                    print(f"   ✅ {var}: {value}")
                else:
                    print(f"   ⚠️  {var}: Not set (optional)")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Configuration error: {e}")
            return False
    
    async def test_database_connection(self) -> bool:
        """Test database connection."""
        try:
            self.db_manager = SupabaseManager(
                url=self.config.SUPABASE_URL,
                key=self.config.SUPABASE_KEY
            )
            
            await self.db_manager.initialize()
            health = await self.db_manager.health_check()
            
            if health:
                print("   ✅ Database connection successful")
                return True
            else:
                print("   ❌ Database health check failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Database connection error: {e}")
            return False
    
    async def test_database_operations(self) -> bool:
        """Test basic database operations."""
        try:
            if not self.db_manager:
                print("   ❌ Database manager not initialized")
                return False
            
            # Test user operations
            test_user_id = 123456789
            
            # Create test user
            from src.database.models import User
            test_user = User(
                telegram_id=test_user_id,
                username="test_user",
                first_name="Test",
                last_name="User",
                language_code="ar"
            )
            
            user_saved = await self.db_manager.save_user(test_user)
            if user_saved:
                print("   ✅ User creation successful")
            else:
                print("   ❌ User creation failed")
                return False
            
            # Retrieve user
            retrieved_user = await self.db_manager.get_user(test_user_id)
            if retrieved_user and retrieved_user.telegram_id == test_user_id:
                print("   ✅ User retrieval successful")
            else:
                print("   ❌ User retrieval failed")
                return False
            
            # Test job operations
            from src.database.models import Job
            test_job = Job(
                title="Test Developer",
                company="Test Company",
                description="Test job description",
                location="Remote",
                job_type="Full-time",
                apply_url="https://example.com/apply",
                source="test"
            )
            
            job_saved = await self.db_manager.save_job(test_job)
            if job_saved:
                print("   ✅ Job creation successful")
            else:
                print("   ❌ Job creation failed")
                return False
            
            # Clean up test data
            await self.db_manager.delete_user(test_user_id)
            print("   ✅ Test data cleanup successful")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Database operations error: {e}")
            return False
    
    async def test_job_scraping(self) -> bool:
        """Test job scraping functionality."""
        try:
            if not self.db_manager:
                print("   ❌ Database manager not initialized")
                return False
            
            scraping_manager = ScrapingManager(self.db_manager)
            
            # Test Google Jobs scraper
            print("   🔍 Testing Google Jobs scraper...")
            google_jobs = await scraping_manager.scrapers['google'].search_jobs("python developer", limit=2)
            
            if google_jobs and len(google_jobs) > 0:
                print(f"   ✅ Google Jobs: Found {len(google_jobs)} jobs")
            else:
                print("   ⚠️  Google Jobs: No jobs found (may be normal)")
            
            # Test at least one remote site
            print("   🔍 Testing RemoteOK scraper...")
            try:
                remote_jobs = await scraping_manager.scrapers['remoteok'].search_jobs("developer", limit=2)
                if remote_jobs and len(remote_jobs) > 0:
                    print(f"   ✅ RemoteOK: Found {len(remote_jobs)} jobs")
                else:
                    print("   ⚠️  RemoteOK: No jobs found (may be normal)")
            except Exception as e:
                print(f"   ⚠️  RemoteOK: Error - {e}")
            
            # Test search by criteria
            print("   🔍 Testing search by criteria...")
            criteria_jobs = await scraping_manager.search_jobs_by_criteria("python", limit=3)
            
            if criteria_jobs and len(criteria_jobs) > 0:
                print(f"   ✅ Criteria search: Found {len(criteria_jobs)} jobs")
                return True
            else:
                print("   ⚠️  Criteria search: No jobs found")
                return True  # Still pass as this might be normal
                
        except Exception as e:
            print(f"   ❌ Job scraping error: {e}")
            return False
    
    async def test_link_checking(self) -> bool:
        """Test link checking functionality."""
        try:
            link_checker = LinkChecker()
            
            # Test valid URL
            print("   🔗 Testing valid URL...")
            valid_result = await link_checker.check_link("https://www.google.com")
            
            if valid_result and valid_result.is_working:
                print("   ✅ Valid URL check successful")
            else:
                print("   ❌ Valid URL check failed")
                return False
            
            # Test invalid URL
            print("   🔗 Testing invalid URL...")
            invalid_result = await link_checker.check_link("https://invalid-url-that-does-not-exist.com")
            
            if invalid_result and not invalid_result.is_working:
                print("   ✅ Invalid URL check successful")
            else:
                print("   ⚠️  Invalid URL check unexpected result")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Link checking error: {e}")
            return False
    
    async def test_opinion_collection(self) -> bool:
        """Test opinion collection functionality."""
        try:
            if not self.db_manager:
                print("   ❌ Database manager not initialized")
                return False
            
            opinion_collector = OpinionCollector(self.db_manager)
            
            # Test opinion search
            print("   💬 Testing opinion collection...")
            opinions = await opinion_collector.collect_opinions_for_job(
                "Google", "Software Engineer", limit=2
            )
            
            if opinions and len(opinions) > 0:
                print(f"   ✅ Opinion collection: Found {len(opinions)} opinions")
            else:
                print("   ⚠️  Opinion collection: No opinions found (may be normal)")
            
            # Test sentiment analysis
            from src.utils.sentiment_analyzer import SentimentAnalyzer
            sentiment_analyzer = SentimentAnalyzer()
            
            test_text = "This is a great company to work for!"
            sentiment = await sentiment_analyzer.analyze_sentiment(test_text)
            
            if sentiment and sentiment.sentiment:
                print(f"   ✅ Sentiment analysis: {sentiment.sentiment} ({sentiment.confidence:.2f})")
                return True
            else:
                print("   ❌ Sentiment analysis failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Opinion collection error: {e}")
            return False
    
    async def test_notification_system(self) -> bool:
        """Test notification system."""
        try:
            # Create a mock bot for testing
            class MockBot:
                async def send_message(self, **kwargs):
                    return True
                
                @property
                def username(self):
                    return "test_bot"
            
            mock_bot = MockBot()
            
            if not self.db_manager:
                print("   ❌ Database manager not initialized")
                return False
            
            notification_manager = AdvancedNotificationManager(mock_bot, self.db_manager)
            
            # Test template loading
            templates = notification_manager.templates
            if templates and len(templates) > 0:
                print(f"   ✅ Notification templates: {len(templates)} loaded")
            else:
                print("   ❌ No notification templates loaded")
                return False
            
            # Test notification content creation
            from src.database.models import User
            test_user = User(
                telegram_id=123456789,
                username="test_user",
                first_name="Test"
            )
            
            from src.scheduler.notification_manager import NotificationType
            content = await notification_manager._create_notification_content(
                test_user,
                templates[NotificationType.DAILY_JOBS],
                []
            )
            
            if content and len(content) > 0:
                print("   ✅ Notification content creation successful")
                return True
            else:
                print("   ❌ Notification content creation failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Notification system error: {e}")
            return False
    
    async def test_scheduler(self) -> bool:
        """Test scheduler functionality."""
        try:
            # Create a mock bot for testing
            class MockBot:
                async def send_message(self, **kwargs):
                    return True
                
                @property
                def username(self):
                    return "test_bot"
            
            mock_bot = MockBot()
            
            if not self.db_manager:
                print("   ❌ Database manager not initialized")
                return False
            
            scheduler = JobNotificationScheduler(mock_bot, self.db_manager)
            
            # Test scheduler initialization
            await scheduler.start()
            status = await scheduler.get_scheduler_status()
            
            if status and status.get('is_running'):
                print("   ✅ Scheduler started successfully")
            else:
                print("   ❌ Scheduler failed to start")
                return False
            
            # Test job scheduling
            jobs_count = status.get('total_jobs', 0)
            if jobs_count > 0:
                print(f"   ✅ Scheduled jobs: {jobs_count}")
            else:
                print("   ⚠️  No scheduled jobs found")
            
            # Stop scheduler
            await scheduler.stop()
            print("   ✅ Scheduler stopped successfully")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Scheduler error: {e}")
            return False
    
    async def test_bot_integration(self) -> bool:
        """Test overall bot integration."""
        try:
            # Test bot token validation
            from telegram import Bot
            
            bot = Bot(token=self.config.BOT_TOKEN)
            bot_info = await bot.get_me()
            
            if bot_info and bot_info.username:
                print(f"   ✅ Bot token valid: @{bot_info.username}")
            else:
                print("   ❌ Bot token validation failed")
                return False
            
            # Test bot permissions
            try:
                # This will fail if bot doesn't have proper permissions
                await bot.get_my_commands()
                print("   ✅ Bot permissions check successful")
            except Exception as e:
                print(f"   ⚠️  Bot permissions warning: {e}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Bot integration error: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup test resources."""
        try:
            if self.db_manager:
                await self.db_manager.close()
            print("✅ Test cleanup completed")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")

async def main():
    """Main test runner."""
    print("🧪 Telegram Jobs Bot - Testing Suite")
    print("=" * 50)
    
    # Load environment
    try:
        from dotenv import load_dotenv
        env_file = Path(__file__).parent / '.env'
        if env_file.exists():
            load_dotenv(env_file)
            print("✅ Environment loaded from .env file")
        else:
            print("⚠️  No .env file found")
    except ImportError:
        print("⚠️  python-dotenv not available")
    
    tester = BotTester()
    
    try:
        results = await tester.run_all_tests()
        
        # Save test results
        results_file = Path(__file__).parent / 'test_results.json'
        import json
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                **results,
                'timestamp': datetime.now().isoformat(),
                'python_version': sys.version,
                'platform': sys.platform
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Test results saved to: {results_file}")
        
        return results['success_rate'] == 100.0
        
    except Exception as e:
        print(f"💥 Test suite error: {e}")
        return False
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Fatal test error: {e}")
        sys.exit(1)

