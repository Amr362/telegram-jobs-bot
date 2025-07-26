import asyncio
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from telegram import Bot
from telegram.error import TelegramError
from src.database.manager import SupabaseManager
from src.database.models import User, Job, JobNotification, NotificationFrequency
from src.scrapers.manager import ScrapingManager
from src.utils.opinion_collector import OpinionCollector
from src.utils.link_checker import LinkChecker
from src.utils.logger import get_logger

logger = get_logger(__name__)

class JobNotificationScheduler:
    """Handles scheduling and sending of job notifications."""
    
    def __init__(self, bot: Bot, db_manager: SupabaseManager):
        self.bot = bot
        self.db_manager = db_manager
        self.scraping_manager = ScrapingManager(db_manager)
        self.opinion_collector = OpinionCollector(db_manager)
        self.link_checker = LinkChecker(db_manager)
        
        # Configure scheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 300  # 5 minutes
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        self.is_running = False
        logger.info("JobNotificationScheduler initialized")
    
    async def start(self):
        """Starts the scheduler."""
        try:
            if not self.is_running:
                self.scheduler.start()
                self.is_running = True
                
                # Schedule main jobs
                await self._schedule_main_jobs()
                
                logger.info("Job notification scheduler started")
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
    
    async def stop(self):
        """Stops the scheduler."""
        try:
            if self.is_running:
                self.scheduler.shutdown(wait=False)
                self.is_running = False
                logger.info("Job notification scheduler stopped")
                
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    async def _schedule_main_jobs(self):
        """Schedules the main recurring jobs."""
        try:
            # Daily job scraping at 6 AM UTC
            self.scheduler.add_job(
                self._daily_job_scraping,
                CronTrigger(hour=6, minute=0),
                id='daily_job_scraping',
                name='Daily Job Scraping',
                replace_existing=True
            )
            
            # Morning notifications at 8 AM UTC
            self.scheduler.add_job(
                self._send_morning_notifications,
                CronTrigger(hour=8, minute=0),
                id='morning_notifications',
                name='Morning Job Notifications',
                replace_existing=True
            )
            
            # Evening notifications at 6 PM UTC
            self.scheduler.add_job(
                self._send_evening_notifications,
                CronTrigger(hour=18, minute=0),
                id='evening_notifications',
                name='Evening Job Notifications',
                replace_existing=True
            )
            
            # Weekly link checking on Sundays at 2 AM UTC
            self.scheduler.add_job(
                self._weekly_link_check,
                CronTrigger(day_of_week=6, hour=2, minute=0),
                id='weekly_link_check',
                name='Weekly Link Check',
                replace_existing=True
            )
            
            # Hourly opinion collection (limited)
            self.scheduler.add_job(
                self._hourly_opinion_collection,
                CronTrigger(minute=30),
                id='hourly_opinion_collection',
                name='Hourly Opinion Collection',
                replace_existing=True
            )
            
            logger.info("Main scheduler jobs configured")
            
        except Exception as e:
            logger.error(f"Error scheduling main jobs: {e}")
    
    async def _daily_job_scraping(self):
        """Performs daily job scraping for all users."""
        try:
            logger.info("Starting daily job scraping")
            
            # Get all active users
            active_users = await self.db_manager.get_active_users()
            
            if not active_users:
                logger.info("No active users found for job scraping")
                return
            
            # Collect unique search criteria
            search_criteria = set()
            for user in active_users:
                user_prefs = await self.db_manager.get_user_preferences(user.telegram_id)
                if user_prefs:
                    # Add user's skills and preferences to search criteria
                    if user_prefs.skills:
                        search_criteria.update(user_prefs.skills)
                    
                    # Add location preferences
                    if user_prefs.location_preference:
                        search_criteria.add(user_prefs.location_preference)
            
            # Perform scraping for collected criteria
            total_jobs_found = 0
            for criteria in list(search_criteria)[:10]:  # Limit to 10 criteria per day
                try:
                    jobs = await self.scraping_manager.search_jobs_by_criteria(criteria)
                    total_jobs_found += len(jobs)
                    
                    # Add delay between searches
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    logger.warning(f"Error scraping for criteria '{criteria}': {e}")
                    continue
            
            logger.info(f"Daily job scraping completed. Found {total_jobs_found} new jobs")
            
            # Update scraping statistics
            await self.db_manager.update_scraping_stats(
                date=datetime.now().date(),
                jobs_found=total_jobs_found,
                sources_scraped=len(self.scraping_manager.scrapers)
            )
            
        except Exception as e:
            logger.error(f"Error in daily job scraping: {e}")
    
    async def _send_morning_notifications(self):
        """Sends morning job notifications to users."""
        try:
            logger.info("Starting morning notifications")
            
            # Get users who want morning notifications
            users = await self.db_manager.get_users_by_notification_frequency(
                NotificationFrequency.DAILY_MORNING
            )
            
            users.extend(await self.db_manager.get_users_by_notification_frequency(
                NotificationFrequency.TWICE_DAILY
            ))
            
            notification_count = 0
            for user in users:
                try:
                    await self._send_personalized_notification(user, "morning")
                    notification_count += 1
                    
                    # Add delay between notifications
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Error sending morning notification to user {user.telegram_id}: {e}")
                    continue
            
            logger.info(f"Morning notifications sent to {notification_count} users")
            
        except Exception as e:
            logger.error(f"Error in morning notifications: {e}")
    
    async def _send_evening_notifications(self):
        """Sends evening job notifications to users."""
        try:
            logger.info("Starting evening notifications")
            
            # Get users who want evening notifications
            users = await self.db_manager.get_users_by_notification_frequency(
                NotificationFrequency.DAILY_EVENING
            )
            
            users.extend(await self.db_manager.get_users_by_notification_frequency(
                NotificationFrequency.TWICE_DAILY
            ))
            
            notification_count = 0
            for user in users:
                try:
                    await self._send_personalized_notification(user, "evening")
                    notification_count += 1
                    
                    # Add delay between notifications
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Error sending evening notification to user {user.telegram_id}: {e}")
                    continue
            
            logger.info(f"Evening notifications sent to {notification_count} users")
            
        except Exception as e:
            logger.error(f"Error in evening notifications: {e}")
    
    async def _send_personalized_notification(self, user: User, time_of_day: str):
        """Sends a personalized job notification to a user."""
        try:
            # Get user preferences
            user_prefs = await self.db_manager.get_user_preferences(user.telegram_id)
            if not user_prefs:
                logger.warning(f"No preferences found for user {user.telegram_id}")
                return
            
            # Find matching jobs
            matching_jobs = await self.db_manager.find_matching_jobs_for_user(user.telegram_id)
            
            if not matching_jobs:
                # Send "no new jobs" message occasionally
                if datetime.now().hour % 3 == 0:  # Every 3rd hour
                    await self._send_no_jobs_message(user, time_of_day)
                return
            
            # Limit to top 3 jobs
            top_jobs = matching_jobs[:3]
            
            # Collect opinions for jobs (if available)
            jobs_with_opinions = []
            for job in top_jobs:
                opinions = await self.db_manager.get_job_opinions(job.id, limit=2)
                jobs_with_opinions.append((job, opinions))
            
            # Create notification message
            message = await self._create_notification_message(
                user, jobs_with_opinions, time_of_day
            )
            
            # Send notification
            await self.bot.send_message(
                chat_id=user.telegram_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            # Record notification in database
            notification = JobNotification(
                user_id=user.telegram_id,
                job_ids=[job.id for job, _ in jobs_with_opinions],
                message_content=message,
                notification_type=f"daily_{time_of_day}",
                sent_at=datetime.now()
            )
            
            await self.db_manager.save_notification(notification)
            
            logger.info(f"Sent {time_of_day} notification to user {user.telegram_id} with {len(top_jobs)} jobs")
            
        except TelegramError as e:
            logger.warning(f"Telegram error sending notification to {user.telegram_id}: {e}")
            # Mark user as inactive if bot was blocked
            if "bot was blocked" in str(e).lower():
                await self.db_manager.deactivate_user(user.telegram_id)
                
        except Exception as e:
            logger.error(f"Error sending personalized notification to {user.telegram_id}: {e}")
    
    async def _create_notification_message(
        self, 
        user: User, 
        jobs_with_opinions: List[tuple], 
        time_of_day: str
    ) -> str:
        """Creates a formatted notification message."""
        try:
            # Greeting based on time of day
            greetings = {
                "morning": f"🌅 صباح الخير {user.first_name or 'عزيزي'}!",
                "evening": f"🌆 مساء الخير {user.first_name or 'عزيزي'}!"
            }
            
            greeting = greetings.get(time_of_day, f"مرحباً {user.first_name or 'عزيزي'}!")
            
            message = f"{greeting}\n\n"
            message += "🎯 **وظائف جديدة مناسبة لك:**\n\n"
            
            for i, (job, opinions) in enumerate(jobs_with_opinions, 1):
                # Job header
                message += f"**{i}. {job.title}**\n"
                message += f"🏢 {job.company}\n"
                
                if job.location:
                    message += f"📍 {job.location}\n"
                
                if job.job_type:
                    message += f"💼 {job.job_type}\n"
                
                # Check link status
                link_status = await self.link_checker.check_link_status(job.apply_url)
                status_emoji = "✅" if link_status.is_working else "⚠️"
                message += f"{status_emoji} [التقديم الآن]({job.apply_url})\n"
                
                # Add opinions if available
                if opinions:
                    opinion_summary = self._format_opinions_summary(opinions)
                    message += f"💬 {opinion_summary}\n"
                
                message += "\n"
            
            # Footer
            message += "📱 استخدم /search للبحث عن المزيد\n"
            message += "⚙️ استخدم /settings لتعديل تفضيلاتك\n"
            message += "🆘 استخدم /support للحصول على المساعدة"
            
            return message
            
        except Exception as e:
            logger.error(f"Error creating notification message: {e}")
            return "حدث خطأ في إنشاء الإشعار. يرجى المحاولة مرة أخرى."
    
    def _format_opinions_summary(self, opinions: List) -> str:
        """Formats a brief summary of opinions."""
        if not opinions:
            return ""
        
        positive_count = sum(1 for op in opinions if 'positive' in op.sentiment)
        negative_count = sum(1 for op in opinions if 'negative' in op.sentiment)
        
        if positive_count > negative_count:
            return "آراء إيجابية 😊"
        elif negative_count > positive_count:
            return "آراء متباينة 🤔"
        else:
            return "آراء متنوعة 💭"
    
    async def _send_no_jobs_message(self, user: User, time_of_day: str):
        """Sends a message when no new jobs are found."""
        try:
            message = f"مرحباً {user.first_name or 'عزيزي'}! 👋\n\n"
            message += "لم أجد وظائف جديدة مناسبة لتفضيلاتك اليوم، لكن لا تقلق!\n\n"
            message += "💡 **نصائح:**\n"
            message += "• جرب توسيع نطاق البحث في /settings\n"
            message += "• أضف مهارات جديدة لملفك الشخصي\n"
            message += "• استخدم /search للبحث اليدوي\n\n"
            message += "سأواصل البحث لك! 🔍"
            
            await self.bot.send_message(
                chat_id=user.telegram_id,
                text=message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.warning(f"Error sending no jobs message to {user.telegram_id}: {e}")
    
    async def _weekly_link_check(self):
        """Performs weekly link checking for all jobs."""
        try:
            logger.info("Starting weekly link check")
            
            # Get all jobs from the last week
            week_ago = datetime.now() - timedelta(days=7)
            recent_jobs = await self.db_manager.get_jobs_since_date(week_ago)
            
            checked_count = 0
            broken_count = 0
            
            for job in recent_jobs:
                try:
                    link_status = await self.link_checker.check_link_status(job.apply_url)
                    
                    if not link_status.is_working:
                        broken_count += 1
                        # Mark job as having broken link
                        await self.db_manager.update_job_link_status(job.id, False)
                    
                    checked_count += 1
                    
                    # Add delay between checks
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"Error checking link for job {job.id}: {e}")
                    continue
            
            logger.info(f"Weekly link check completed. Checked {checked_count} jobs, found {broken_count} broken links")
            
        except Exception as e:
            logger.error(f"Error in weekly link check: {e}")
    
    async def _hourly_opinion_collection(self):
        """Performs limited hourly opinion collection."""
        try:
            # Get jobs that don't have opinions yet (limit to 5 per hour)
            jobs_without_opinions = await self.db_manager.get_jobs_without_opinions(limit=5)
            
            if not jobs_without_opinions:
                return
            
            collected_count = 0
            for job in jobs_without_opinions:
                try:
                    opinions = await self.opinion_collector.collect_opinions_for_job(job)
                    if opinions:
                        collected_count += 1
                    
                    # Add delay between collections
                    await asyncio.sleep(10)
                    
                except Exception as e:
                    logger.warning(f"Error collecting opinions for job {job.id}: {e}")
                    continue
            
            if collected_count > 0:
                logger.info(f"Hourly opinion collection: collected opinions for {collected_count} jobs")
            
        except Exception as e:
            logger.error(f"Error in hourly opinion collection: {e}")
    
    async def schedule_custom_notification(
        self, 
        user_id: int, 
        notification_time: time, 
        frequency: str = "daily"
    ):
        """Schedules a custom notification for a specific user."""
        try:
            job_id = f"custom_notification_{user_id}"
            
            if frequency == "daily":
                trigger = CronTrigger(
                    hour=notification_time.hour,
                    minute=notification_time.minute
                )
            elif frequency == "weekly":
                trigger = CronTrigger(
                    day_of_week=1,  # Monday
                    hour=notification_time.hour,
                    minute=notification_time.minute
                )
            else:
                logger.warning(f"Unsupported frequency: {frequency}")
                return False
            
            self.scheduler.add_job(
                self._send_custom_user_notification,
                trigger,
                args=[user_id],
                id=job_id,
                name=f"Custom notification for user {user_id}",
                replace_existing=True
            )
            
            logger.info(f"Scheduled custom {frequency} notification for user {user_id} at {notification_time}")
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling custom notification for user {user_id}: {e}")
            return False
    
    async def _send_custom_user_notification(self, user_id: int):
        """Sends a custom notification to a specific user."""
        try:
            user = await self.db_manager.get_user_by_telegram_id(user_id)
            if user and user.is_active:
                await self._send_personalized_notification(user, "custom")
                
        except Exception as e:
            logger.error(f"Error sending custom notification to user {user_id}: {e}")
    
    async def remove_user_notifications(self, user_id: int):
        """Removes all scheduled notifications for a user."""
        try:
            job_id = f"custom_notification_{user_id}"
            
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"Removed custom notifications for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing notifications for user {user_id}: {e}")
            return False
    
    async def get_scheduler_status(self) -> Dict[str, Any]:
        """Gets the current status of the scheduler."""
        try:
            jobs = self.scheduler.get_jobs()
            
            status = {
                'is_running': self.is_running,
                'total_jobs': len(jobs),
                'jobs': [
                    {
                        'id': job.id,
                        'name': job.name,
                        'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                        'trigger': str(job.trigger)
                    }
                    for job in jobs
                ]
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting scheduler status: {e}")
            return {'is_running': False, 'error': str(e)}
    
    async def send_immediate_notification(self, user_id: int, job_ids: List[int]):
        """Sends an immediate notification for specific jobs."""
        try:
            user = await self.db_manager.get_user_by_telegram_id(user_id)
            if not user:
                return False
            
            jobs = []
            for job_id in job_ids:
                job = await self.db_manager.get_job_by_id(job_id)
                if job:
                    jobs.append(job)
            
            if not jobs:
                return False
            
            # Create jobs with opinions
            jobs_with_opinions = []
            for job in jobs:
                opinions = await self.db_manager.get_job_opinions(job.id, limit=2)
                jobs_with_opinions.append((job, opinions))
            
            # Create and send message
            message = await self._create_notification_message(
                user, jobs_with_opinions, "immediate"
            )
            
            await self.bot.send_message(
                chat_id=user.telegram_id,
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            # Record notification
            notification = JobNotification(
                user_id=user.telegram_id,
                job_ids=job_ids,
                message_content=message,
                notification_type="immediate",
                sent_at=datetime.now()
            )
            
            await self.db_manager.save_notification(notification)
            
            logger.info(f"Sent immediate notification to user {user_id} with {len(jobs)} jobs")
            return True
            
        except Exception as e:
            logger.error(f"Error sending immediate notification to user {user_id}: {e}")
            return False

