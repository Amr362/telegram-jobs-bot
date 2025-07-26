import asyncio
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
from src.utils.config import Config
from src.utils.logger import get_logger
from src.database.models import (
    User, UserPreferences, Job, JobNotification, JobOpinion, 
    SearchLog, BotStatistics, JobMatch, UserStats
)

logger = get_logger(__name__)

class SupabaseManager:
    """Manages all database operations using Supabase."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logger.info("Supabase client initialized")
    
    async def test_connection(self) -> bool:
        """Tests the connection to Supabase."""
        try:
            # Simple query to test connection
            result = self.client.table('bot_users').select('count').execute()
            logger.info("Supabase connection test successful")
            return True
        except Exception as e:
            logger.error(f"Supabase connection test failed: {e}")
            return False
    
    # User Management Methods
    async def create_user(self, user: User) -> Optional[User]:
        """Creates a new user in the database."""
        try:
            result = self.client.table('bot_users').insert(user.to_dict()).execute()
            if result.data:
                logger.info(f"User created successfully: {user.telegram_id}")
                return User.from_dict(result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to create user {user.telegram_id}: {e}")
            return None
    
    async def get_user(self, telegram_id: int) -> Optional[User]:
        """Retrieves a user by Telegram ID."""
        try:
            result = self.client.table('bot_users').select('*').eq('telegram_id', telegram_id).execute()
            if result.data:
                return User.from_dict(result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get user {telegram_id}: {e}")
            return None
    
    async def update_user(self, telegram_id: int, updates: Dict[str, Any]) -> bool:
        """Updates user information."""
        try:
            result = self.client.table('bot_users').update(updates).eq('telegram_id', telegram_id).execute()
            logger.info(f"User {telegram_id} updated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to update user {telegram_id}: {e}")
            return False
    
    async def get_or_create_user(self, telegram_id: int, username: str = None, first_name: str = None) -> User:
        """Gets an existing user or creates a new one."""
        user = await self.get_user(telegram_id)
        if user:
            return user
        
        new_user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name
        )
        created_user = await self.create_user(new_user)
        return created_user or new_user
    
    # User Preferences Methods
    async def save_user_preferences(self, preferences: UserPreferences) -> bool:
        """Saves or updates user preferences."""
        try:
            # Check if preferences exist
            existing = self.client.table('user_preferences').select('id').eq('user_id', preferences.user_id).execute()
            
            if existing.data:
                # Update existing preferences
                result = self.client.table('user_preferences').update(preferences.to_dict()).eq('user_id', preferences.user_id).execute()
            else:
                # Insert new preferences
                result = self.client.table('user_preferences').insert(preferences.to_dict()).execute()
            
            logger.info(f"User preferences saved for user {preferences.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save preferences for user {preferences.user_id}: {e}")
            return False
    
    async def get_user_preferences(self, user_id: int) -> Optional[UserPreferences]:
        """Retrieves user preferences."""
        try:
            result = self.client.table('user_preferences').select('*').eq('user_id', user_id).execute()
            if result.data:
                return UserPreferences.from_dict(result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get preferences for user {user_id}: {e}")
            return None
    
    async def get_users_for_notification(self, notification_time: str = None) -> List[Dict[str, Any]]:
        """Gets users who should receive notifications at a specific time."""
        try:
            query = self.client.table('user_preferences').select(
                'user_id, language_preference, location_preference, preferred_country, skills, notification_frequency'
            ).eq('onboarding_completed', True)
            
            if notification_time:
                # Filter by notification time if provided
                query = query.contains('notification_times', [notification_time])
            
            result = query.execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get users for notification: {e}")
            return []
    
    # Job Management Methods
    async def save_job(self, job: Job) -> Optional[Job]:
        """Saves a job to the database."""
        try:
            result = self.client.table('jobs').insert(job.to_dict()).execute()
            if result.data:
                logger.info(f"Job saved: {job.title} from {job.source}")
                return Job.from_dict(result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to save job {job.title}: {e}")
            return None
    
    async def save_jobs_batch(self, jobs: List[Job]) -> int:
        """Saves multiple jobs in a batch operation."""
        try:
            job_dicts = [job.to_dict() for job in jobs]
            result = self.client.table('jobs').insert(job_dicts).execute()
            saved_count = len(result.data) if result.data else 0
            logger.info(f"Batch saved {saved_count} jobs")
            return saved_count
        except Exception as e:
            logger.error(f"Failed to batch save jobs: {e}")
            return 0
    
    async def get_job(self, job_id: int) -> Optional[Job]:
        """Retrieves a job by ID."""
        try:
            result = self.client.table('jobs').select('*').eq('id', job_id).execute()
            if result.data:
                return Job.from_dict(result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
    
    async def get_recent_jobs(self, limit: int = 10, source: str = None) -> List[Job]:
        """Gets recent jobs, optionally filtered by source."""
        try:
            query = self.client.table('jobs').select('*').eq('is_active', True).order('scraped_at', desc=True).limit(limit)
            
            if source:
                query = query.eq('source', source)
            
            result = query.execute()
            return [Job.from_dict(job_data) for job_data in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Failed to get recent jobs: {e}")
            return []
    
    async def update_job_link_status(self, job_id: int, status: str) -> bool:
        """Updates the link status of a job."""
        try:
            result = self.client.table('jobs').update({
                'link_status': status,
                'link_checked_at': 'now()'
            }).eq('id', job_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to update job link status {job_id}: {e}")
            return False
    
    async def job_exists(self, source: str, source_job_id: str) -> bool:
        """Checks if a job already exists in the database."""
        try:
            result = self.client.table('jobs').select('id').eq('source', source).eq('source_job_id', source_job_id).execute()
            return len(result.data) > 0 if result.data else False
        except Exception as e:
            logger.error(f"Failed to check job existence: {e}")
            return False
    
    # Job Matching Methods
    async def get_matched_jobs_for_user(self, user_id: int, limit: int = 5) -> List[JobMatch]:
        """Gets matched jobs for a user using the database function."""
        try:
            result = self.client.rpc('match_jobs_for_user', {
                'user_telegram_id': user_id,
                'limit_count': limit
            }).execute()
            
            if result.data:
                return [JobMatch.from_dict(match) for match in result.data]
            return []
        except Exception as e:
            logger.error(f"Failed to get matched jobs for user {user_id}: {e}")
            return []
    
    # Job Notification Methods
    async def save_job_notification(self, notification: JobNotification) -> bool:
        """Saves a job notification record."""
        try:
            result = self.client.table('job_notifications').insert(notification.to_dict()).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to save job notification: {e}")
            return False
    
    async def mark_notification_clicked(self, user_id: int, job_id: int) -> bool:
        """Marks a notification as clicked."""
        try:
            result = self.client.table('job_notifications').update({
                'is_clicked': True,
                'clicked_at': 'now()'
            }).eq('user_id', user_id).eq('job_id', job_id).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to mark notification as clicked: {e}")
            return False
    
    async def get_user_notifications(self, user_id: int, limit: int = 10) -> List[JobNotification]:
        """Gets recent notifications for a user."""
        try:
            result = self.client.table('job_notifications').select('*').eq('user_id', user_id).order('sent_at', desc=True).limit(limit).execute()
            return [JobNotification.from_dict(notif) for notif in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Failed to get user notifications: {e}")
            return []
    
    # Job Opinion Methods
    async def save_job_opinion(self, opinion: JobOpinion) -> bool:
        """Saves a job opinion."""
        try:
            result = self.client.table('job_opinions').insert(opinion.to_dict()).execute()
            logger.info(f"Job opinion saved for job {opinion.job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save job opinion: {e}")
            return False
    
    async def get_job_opinions(self, job_id: int) -> List[JobOpinion]:
        """Gets opinions for a specific job."""
        try:
            result = self.client.table('job_opinions').select('*').eq('job_id', job_id).execute()
            return [JobOpinion.from_dict(opinion) for opinion in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Failed to get job opinions: {e}")
            return []
    
    # Search Log Methods
    async def log_search(self, search_log: SearchLog) -> bool:
        """Logs a search operation."""
        try:
            result = self.client.table('search_logs').insert(search_log.to_dict()).execute()
            return True
        except Exception as e:
            logger.error(f"Failed to log search: {e}")
            return False
    
    # Statistics Methods
    async def update_bot_statistics(self, stats: BotStatistics) -> bool:
        """Updates daily bot statistics."""
        try:
            # Try to update existing record for the date
            existing = self.client.table('bot_statistics').select('id').eq('date', stats.date.date()).execute()
            
            if existing.data:
                result = self.client.table('bot_statistics').update(stats.to_dict()).eq('date', stats.date.date()).execute()
            else:
                result = self.client.table('bot_statistics').insert(stats.to_dict()).execute()
            
            return True
        except Exception as e:
            logger.error(f"Failed to update bot statistics: {e}")
            return False
    
    async def get_user_stats(self, user_id: int) -> Optional[UserStats]:
        """Gets statistics for a specific user."""
        try:
            result = self.client.rpc('get_user_stats', {'user_telegram_id': user_id}).execute()
            if result.data:
                return UserStats.from_dict(result.data[0])
            return None
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return None
    
    # Utility Methods
    async def cleanup_old_jobs(self, days: int = 30) -> int:
        """Removes jobs older than specified days."""
        try:
            result = self.client.table('jobs').delete().lt('scraped_at', f'now() - interval \'{days} days\'').execute()
            deleted_count = len(result.data) if result.data else 0
            logger.info(f"Cleaned up {deleted_count} old jobs")
            return deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup old jobs: {e}")
            return 0
    
    async def get_active_users_count(self) -> int:
        """Gets the count of active users."""
        try:
            result = self.client.table('bot_users').select('count').eq('is_active', True).execute()
            return result.count if hasattr(result, 'count') else 0
        except Exception as e:
            logger.error(f"Failed to get active users count: {e}")
            return 0
    
    async def get_total_jobs_count(self) -> int:
        """Gets the total count of jobs."""
        try:
            result = self.client.table('jobs').select('count').eq('is_active', True).execute()
            return result.count if hasattr(result, 'count') else 0
        except Exception as e:
            logger.error(f"Failed to get total jobs count: {e}")
            return 0

