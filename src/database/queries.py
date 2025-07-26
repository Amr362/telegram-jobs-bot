from typing import List, Dict, Any, Optional
from src.database.manager import SupabaseManager
from src.database.models import User, UserPreferences, Job, JobMatch
from src.utils.logger import get_logger

logger = get_logger(__name__)

class UserQueries:
    """Specialized queries for user-related operations."""
    
    def __init__(self, db_manager: SupabaseManager):
        self.db = db_manager
    
    async def get_users_by_language_preference(self, language: str) -> List[User]:
        """Gets users by their language preference."""
        try:
            result = self.db.client.table('bot_users').select(
                'bot_users.*, user_preferences.language_preference'
            ).join(
                'user_preferences', 'bot_users.telegram_id', 'user_preferences.user_id'
            ).eq('user_preferences.language_preference', language).execute()
            
            return [User.from_dict(user_data) for user_data in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Failed to get users by language preference: {e}")
            return []
    
    async def get_users_by_skills(self, skills: List[str]) -> List[Dict[str, Any]]:
        """Gets users who have any of the specified skills."""
        try:
            result = self.db.client.table('user_preferences').select(
                'user_id, skills'
            ).overlaps('skills', skills).execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get users by skills: {e}")
            return []
    
    async def get_users_for_location(self, location: str, is_remote: bool = False) -> List[Dict[str, Any]]:
        """Gets users interested in a specific location or remote work."""
        try:
            if is_remote:
                result = self.db.client.table('user_preferences').select(
                    'user_id, location_preference, preferred_country'
                ).in_('location_preference', ['remote', 'both']).execute()
            else:
                result = self.db.client.table('user_preferences').select(
                    'user_id, location_preference, preferred_country'
                ).or_(
                    f'location_preference.eq.both,and(location_preference.eq.specific,preferred_country.ilike.%{location}%)'
                ).execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get users for location: {e}")
            return []

class JobQueries:
    """Specialized queries for job-related operations."""
    
    def __init__(self, db_manager: SupabaseManager):
        self.db = db_manager
    
    async def search_jobs_by_keywords(self, keywords: List[str], limit: int = 20) -> List[Job]:
        """Searches jobs by keywords in title and description."""
        try:
            # Create search query for keywords
            search_conditions = []
            for keyword in keywords:
                search_conditions.append(f'title.ilike.%{keyword}%')
                search_conditions.append(f'description.ilike.%{keyword}%')
            
            search_query = ','.join(search_conditions)
            
            result = self.db.client.table('jobs').select('*').or_(search_query).eq('is_active', True).order('scraped_at', desc=True).limit(limit).execute()
            
            return [Job.from_dict(job_data) for job_data in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Failed to search jobs by keywords: {e}")
            return []
    
    async def get_jobs_by_skills(self, skills: List[str], limit: int = 20) -> List[Job]:
        """Gets jobs that require any of the specified skills."""
        try:
            result = self.db.client.table('jobs').select('*').overlaps('skills_required', skills).eq('is_active', True).order('scraped_at', desc=True).limit(limit).execute()
            
            return [Job.from_dict(job_data) for job_data in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Failed to get jobs by skills: {e}")
            return []
    
    async def get_remote_jobs(self, limit: int = 20) -> List[Job]:
        """Gets remote jobs."""
        try:
            result = self.db.client.table('jobs').select('*').eq('is_remote', True).eq('is_active', True).order('scraped_at', desc=True).limit(limit).execute()
            
            return [Job.from_dict(job_data) for job_data in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Failed to get remote jobs: {e}")
            return []
    
    async def get_jobs_by_location(self, location: str, limit: int = 20) -> List[Job]:
        """Gets jobs in a specific location."""
        try:
            result = self.db.client.table('jobs').select('*').ilike('location', f'%{location}%').eq('is_active', True).order('scraped_at', desc=True).limit(limit).execute()
            
            return [Job.from_dict(job_data) for job_data in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Failed to get jobs by location: {e}")
            return []
    
    async def get_jobs_by_source(self, source: str, limit: int = 20) -> List[Job]:
        """Gets jobs from a specific source."""
        try:
            result = self.db.client.table('jobs').select('*').eq('source', source).eq('is_active', True).order('scraped_at', desc=True).limit(limit).execute()
            
            return [Job.from_dict(job_data) for job_data in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Failed to get jobs by source: {e}")
            return []
    
    async def get_jobs_with_broken_links(self) -> List[Job]:
        """Gets jobs with broken links that need to be checked."""
        try:
            result = self.db.client.table('jobs').select('*').eq('link_status', 'broken').eq('is_active', True).execute()
            
            return [Job.from_dict(job_data) for job_data in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Failed to get jobs with broken links: {e}")
            return []
    
    async def get_jobs_needing_link_check(self, hours: int = 24) -> List[Job]:
        """Gets jobs that haven't had their links checked recently."""
        try:
            result = self.db.client.table('jobs').select('*').or_(
                f'link_checked_at.is.null,link_checked_at.lt.now() - interval \'{hours} hours\''
            ).eq('is_active', True).limit(100).execute()
            
            return [Job.from_dict(job_data) for job_data in result.data] if result.data else []
        except Exception as e:
            logger.error(f"Failed to get jobs needing link check: {e}")
            return []
    
    async def get_trending_skills(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Gets trending skills from recent job postings."""
        try:
            # This is a complex query that would need to be implemented as a database function
            # For now, return empty list
            logger.warning("get_trending_skills not implemented yet")
            return []
        except Exception as e:
            logger.error(f"Failed to get trending skills: {e}")
            return []

class NotificationQueries:
    """Specialized queries for notification-related operations."""
    
    def __init__(self, db_manager: SupabaseManager):
        self.db = db_manager
    
    async def get_users_due_for_notification(self, current_time: str) -> List[Dict[str, Any]]:
        """Gets users who are due for notification at the current time."""
        try:
            result = self.db.client.table('user_preferences').select(
                'user_id, notification_frequency, notification_times, language_preference, location_preference, preferred_country, skills'
            ).eq('onboarding_completed', True).contains('notification_times', [current_time]).execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get users due for notification: {e}")
            return []
    
    async def get_unsent_jobs_for_user(self, user_id: int, limit: int = 5) -> List[JobMatch]:
        """Gets jobs that haven't been sent to a specific user yet."""
        try:
            # Use the database function for job matching
            result = self.db.client.rpc('match_jobs_for_user', {
                'user_telegram_id': user_id,
                'limit_count': limit
            }).execute()
            
            if result.data:
                return [JobMatch.from_dict(match) for match in result.data]
            return []
        except Exception as e:
            logger.error(f"Failed to get unsent jobs for user: {e}")
            return []
    
    async def get_notification_history(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Gets notification history for a user."""
        try:
            result = self.db.client.table('job_notifications').select(
                'job_notifications.*, jobs.title, jobs.company'
            ).join(
                'jobs', 'job_notifications.job_id', 'jobs.id'
            ).eq('job_notifications.user_id', user_id).gte(
                'job_notifications.sent_at', f'now() - interval \'{days} days\''
            ).order('job_notifications.sent_at', desc=True).execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get notification history: {e}")
            return []
    
    async def get_notification_stats(self, days: int = 30) -> Dict[str, Any]:
        """Gets notification statistics for the specified period."""
        try:
            # Total notifications sent
            total_result = self.db.client.table('job_notifications').select(
                'count'
            ).gte('sent_at', f'now() - interval \'{days} days\'').execute()
            
            # Clicked notifications
            clicked_result = self.db.client.table('job_notifications').select(
                'count'
            ).eq('is_clicked', True).gte('sent_at', f'now() - interval \'{days} days\'').execute()
            
            total_sent = total_result.count if hasattr(total_result, 'count') else 0
            total_clicked = clicked_result.count if hasattr(clicked_result, 'count') else 0
            
            return {
                'total_sent': total_sent,
                'total_clicked': total_clicked,
                'click_rate': (total_clicked / total_sent * 100) if total_sent > 0 else 0
            }
        except Exception as e:
            logger.error(f"Failed to get notification stats: {e}")
            return {'total_sent': 0, 'total_clicked': 0, 'click_rate': 0}

class AnalyticsQueries:
    """Specialized queries for analytics and reporting."""
    
    def __init__(self, db_manager: SupabaseManager):
        self.db = db_manager
    
    async def get_user_engagement_stats(self, days: int = 30) -> Dict[str, Any]:
        """Gets user engagement statistics."""
        try:
            # Active users (users who received notifications)
            active_users_result = self.db.client.table('job_notifications').select(
                'user_id'
            ).gte('sent_at', f'now() - interval \'{days} days\'').execute()
            
            active_users = len(set(notif['user_id'] for notif in active_users_result.data)) if active_users_result.data else 0
            
            # Total users
            total_users_result = self.db.client.table('bot_users').select('count').eq('is_active', True).execute()
            total_users = total_users_result.count if hasattr(total_users_result, 'count') else 0
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'engagement_rate': (active_users / total_users * 100) if total_users > 0 else 0
            }
        except Exception as e:
            logger.error(f"Failed to get user engagement stats: {e}")
            return {'total_users': 0, 'active_users': 0, 'engagement_rate': 0}
    
    async def get_popular_skills(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Gets the most popular skills from user preferences."""
        try:
            # This would need a more complex query or database function
            # For now, return empty list
            logger.warning("get_popular_skills not implemented yet")
            return []
        except Exception as e:
            logger.error(f"Failed to get popular skills: {e}")
            return []
    
    async def get_source_performance(self, days: int = 30) -> List[Dict[str, Any]]:
        """Gets performance statistics for different job sources."""
        try:
            result = self.db.client.table('jobs').select(
                'source, count(*)'
            ).gte('scraped_at', f'now() - interval \'{days} days\'').group('source').execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get source performance: {e}")
            return []
    
    async def get_daily_stats(self, days: int = 7) -> List[Dict[str, Any]]:
        """Gets daily statistics for the specified number of days."""
        try:
            result = self.db.client.table('bot_statistics').select('*').gte(
                'date', f'current_date - interval \'{days} days\''
            ).order('date', desc=True).execute()
            
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get daily stats: {e}")
            return []

