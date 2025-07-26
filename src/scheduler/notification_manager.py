import asyncio
from datetime import datetime, timedelta, time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from src.database.manager import SupabaseManager
from src.database.models import User, Job, JobNotification, NotificationFrequency, UserPreferences
from src.utils.logger import get_logger

logger = get_logger(__name__)

class NotificationType(Enum):
    """Types of notifications."""
    DAILY_JOBS = "daily_jobs"
    URGENT_JOBS = "urgent_jobs"
    WEEKLY_SUMMARY = "weekly_summary"
    CUSTOM_ALERT = "custom_alert"
    SYSTEM_UPDATE = "system_update"

@dataclass
class NotificationTemplate:
    """Template for creating notifications."""
    type: NotificationType
    title: str
    content_template: str
    include_jobs: bool = True
    include_opinions: bool = False
    include_stats: bool = False
    max_jobs: int = 3

class AdvancedNotificationManager:
    """Advanced notification manager with personalization and templates."""
    
    def __init__(self, bot: Bot, db_manager: SupabaseManager):
        self.bot = bot
        self.db_manager = db_manager
        
        # Notification templates
        self.templates = self._load_notification_templates()
        
        # Personalization settings
        self.personalization_enabled = True
        self.max_daily_notifications = 3
        self.min_job_relevance_score = 0.6
        
        logger.info("AdvancedNotificationManager initialized")
    
    def _load_notification_templates(self) -> Dict[NotificationType, NotificationTemplate]:
        """Loads notification templates."""
        return {
            NotificationType.DAILY_JOBS: NotificationTemplate(
                type=NotificationType.DAILY_JOBS,
                title="🎯 وظائف جديدة مناسبة لك",
                content_template="""
{greeting}

{jobs_section}

{tips_section}

{footer}
                """.strip(),
                include_jobs=True,
                include_opinions=True,
                max_jobs=3
            ),
            
            NotificationType.URGENT_JOBS: NotificationTemplate(
                type=NotificationType.URGENT_JOBS,
                title="🚨 وظائف عاجلة - انتهاء قريب!",
                content_template="""
⚡ **تنبيه عاجل!**

{jobs_section}

⏰ هذه الوظائف تنتهي قريباً - قدم الآن!

{footer}
                """.strip(),
                include_jobs=True,
                include_opinions=False,
                max_jobs=2
            ),
            
            NotificationType.WEEKLY_SUMMARY: NotificationTemplate(
                type=NotificationType.WEEKLY_SUMMARY,
                title="📊 ملخص الأسبوع",
                content_template="""
📈 **ملخص أسبوعك في البحث عن الوظائف**

{stats_section}

{top_jobs_section}

{recommendations_section}

{footer}
                """.strip(),
                include_jobs=True,
                include_stats=True,
                max_jobs=5
            ),
            
            NotificationType.CUSTOM_ALERT: NotificationTemplate(
                type=NotificationType.CUSTOM_ALERT,
                title="🔔 تنبيه مخصص",
                content_template="""
{custom_message}

{jobs_section}

{footer}
                """.strip(),
                include_jobs=True,
                include_opinions=True,
                max_jobs=2
            )
        }
    
    async def send_personalized_notification(
        self, 
        user: User, 
        notification_type: NotificationType,
        jobs: List[Job] = None,
        custom_data: Dict[str, Any] = None
    ) -> bool:
        """Sends a personalized notification to a user."""
        try:
            # Get user preferences
            user_prefs = await self.db_manager.get_user_preferences(user.telegram_id)
            if not user_prefs:
                logger.warning(f"No preferences found for user {user.telegram_id}")
                return False
            
            # Get notification template
            template = self.templates.get(notification_type)
            if not template:
                logger.error(f"No template found for notification type: {notification_type}")
                return False
            
            # Get jobs if not provided
            if jobs is None and template.include_jobs:
                jobs = await self._get_relevant_jobs_for_user(user, template.max_jobs)
            
            # Create notification content
            content = await self._create_notification_content(
                user, template, jobs, custom_data
            )
            
            # Create inline keyboard
            keyboard = self._create_notification_keyboard(notification_type, jobs)
            
            # Send notification
            await self.bot.send_message(
                chat_id=user.telegram_id,
                text=content,
                parse_mode='Markdown',
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
            
            # Record notification
            await self._record_notification(user, notification_type, content, jobs)
            
            logger.info(f"Sent {notification_type.value} notification to user {user.telegram_id}")
            return True
            
        except TelegramError as e:
            logger.warning(f"Telegram error sending notification to {user.telegram_id}: {e}")
            
            # Handle blocked bot
            if "bot was blocked" in str(e).lower():
                await self.db_manager.deactivate_user(user.telegram_id)
            
            return False
            
        except Exception as e:
            logger.error(f"Error sending notification to {user.telegram_id}: {e}")
            return False
    
    async def _get_relevant_jobs_for_user(self, user: User, max_jobs: int) -> List[Job]:
        """Gets relevant jobs for a user based on their preferences."""
        try:
            # Get user preferences
            user_prefs = await self.db_manager.get_user_preferences(user.telegram_id)
            if not user_prefs:
                return []
            
            # Find matching jobs
            matching_jobs = await self.db_manager.find_matching_jobs_for_user(
                user.telegram_id, 
                limit=max_jobs * 2  # Get more to filter
            )
            
            # Score and filter jobs
            scored_jobs = []
            for job in matching_jobs:
                score = await self._calculate_job_relevance_score(job, user_prefs)
                if score >= self.min_job_relevance_score:
                    scored_jobs.append((job, score))
            
            # Sort by score and return top jobs
            scored_jobs.sort(key=lambda x: x[1], reverse=True)
            return [job for job, score in scored_jobs[:max_jobs]]
            
        except Exception as e:
            logger.error(f"Error getting relevant jobs for user {user.telegram_id}: {e}")
            return []
    
    async def _calculate_job_relevance_score(self, job: Job, user_prefs: UserPreferences) -> float:
        """Calculates relevance score for a job based on user preferences."""
        try:
            score = 0.0
            
            # Skills matching
            if user_prefs.skills and job.description:
                job_desc_lower = job.description.lower()
                skill_matches = sum(1 for skill in user_prefs.skills 
                                  if skill.lower() in job_desc_lower)
                score += (skill_matches / len(user_prefs.skills)) * 0.4
            
            # Location matching
            if user_prefs.location_preference:
                if user_prefs.location_preference.lower() == "remote":
                    if job.job_type and "remote" in job.job_type.lower():
                        score += 0.3
                elif job.location and user_prefs.location_preference.lower() in job.location.lower():
                    score += 0.3
            
            # Job type matching
            if user_prefs.job_type_preference and job.job_type:
                if user_prefs.job_type_preference.lower() in job.job_type.lower():
                    score += 0.2
            
            # Recency bonus (newer jobs get higher score)
            if job.posted_date:
                days_old = (datetime.now().date() - job.posted_date).days
                if days_old <= 1:
                    score += 0.1
                elif days_old <= 3:
                    score += 0.05
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error calculating job relevance score: {e}")
            return 0.0
    
    async def _create_notification_content(
        self, 
        user: User, 
        template: NotificationTemplate,
        jobs: List[Job],
        custom_data: Dict[str, Any] = None
    ) -> str:
        """Creates notification content based on template."""
        try:
            content = template.content_template
            
            # Replace greeting
            greeting = self._get_personalized_greeting(user)
            content = content.replace("{greeting}", greeting)
            
            # Replace jobs section
            if template.include_jobs and jobs:
                jobs_section = await self._create_jobs_section(jobs, template)
                content = content.replace("{jobs_section}", jobs_section)
            else:
                content = content.replace("{jobs_section}", "")
            
            # Replace stats section
            if template.include_stats:
                stats_section = await self._create_stats_section(user)
                content = content.replace("{stats_section}", stats_section)
            else:
                content = content.replace("{stats_section}", "")
            
            # Replace tips section
            tips_section = self._create_tips_section(user, jobs)
            content = content.replace("{tips_section}", tips_section)
            
            # Replace recommendations section
            recommendations_section = await self._create_recommendations_section(user)
            content = content.replace("{recommendations_section}", recommendations_section)
            
            # Replace footer
            footer = self._create_footer(template.type)
            content = content.replace("{footer}", footer)
            
            # Replace custom data
            if custom_data:
                for key, value in custom_data.items():
                    content = content.replace(f"{{{key}}}", str(value))
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error creating notification content: {e}")
            return "حدث خطأ في إنشاء الإشعار."
    
    def _get_personalized_greeting(self, user: User) -> str:
        """Gets a personalized greeting for the user."""
        current_hour = datetime.now().hour
        name = user.first_name or "عزيزي"
        
        if 5 <= current_hour < 12:
            return f"🌅 صباح الخير {name}!"
        elif 12 <= current_hour < 17:
            return f"☀️ مساء الخير {name}!"
        elif 17 <= current_hour < 21:
            return f"🌆 مساء الخير {name}!"
        else:
            return f"🌙 مساء الخير {name}!"
    
    async def _create_jobs_section(self, jobs: List[Job], template: NotificationTemplate) -> str:
        """Creates the jobs section of the notification."""
        try:
            if not jobs:
                return "لا توجد وظائف جديدة مناسبة لتفضيلاتك اليوم."
            
            jobs_text = ""
            
            for i, job in enumerate(jobs, 1):
                jobs_text += f"**{i}. {job.title}**\n"
                jobs_text += f"🏢 {job.company}\n"
                
                if job.location:
                    jobs_text += f"📍 {job.location}\n"
                
                if job.job_type:
                    jobs_text += f"💼 {job.job_type}\n"
                
                # Add salary if available
                if job.salary_range:
                    jobs_text += f"💰 {job.salary_range}\n"
                
                # Add link with status check
                jobs_text += f"🔗 [التقديم الآن]({job.apply_url})\n"
                
                # Add opinions if template includes them
                if template.include_opinions:
                    opinions = await self.db_manager.get_job_opinions(job.id, limit=1)
                    if opinions:
                        opinion_summary = self._format_opinion_summary(opinions[0])
                        jobs_text += f"💬 {opinion_summary}\n"
                
                jobs_text += "\n"
            
            return jobs_text.strip()
            
        except Exception as e:
            logger.error(f"Error creating jobs section: {e}")
            return "حدث خطأ في عرض الوظائف."
    
    def _format_opinion_summary(self, opinion) -> str:
        """Formats a brief opinion summary."""
        try:
            sentiment_emojis = {
                'positive': '😊',
                'negative': '😞',
                'neutral': '😐',
                'mixed': '🤔'
            }
            
            emoji = sentiment_emojis.get(opinion.sentiment, '💭')
            short_content = opinion.content[:50] + "..." if len(opinion.content) > 50 else opinion.content
            
            return f"{emoji} \"{short_content}\""
            
        except Exception as e:
            logger.error(f"Error formatting opinion summary: {e}")
            return "💭 رأي متاح"
    
    async def _create_stats_section(self, user: User) -> str:
        """Creates the statistics section."""
        try:
            # Get user statistics
            stats = await self.db_manager.get_user_statistics(user.telegram_id)
            
            if not stats:
                return "لا توجد إحصائيات متاحة بعد."
            
            stats_text = "📊 **إحصائياتك:**\n"
            stats_text += f"• الوظائف المرسلة: {stats.get('jobs_sent', 0)}\n"
            stats_text += f"• الوظائف المحفوظة: {stats.get('jobs_saved', 0)}\n"
            stats_text += f"• عمليات البحث: {stats.get('searches_performed', 0)}\n"
            stats_text += f"• الإشعارات المستلمة: {stats.get('notifications_received', 0)}\n"
            
            return stats_text
            
        except Exception as e:
            logger.error(f"Error creating stats section: {e}")
            return ""
    
    def _create_tips_section(self, user: User, jobs: List[Job]) -> str:
        """Creates personalized tips section."""
        try:
            if not jobs:
                tips = [
                    "💡 جرب توسيع نطاق البحث في الإعدادات",
                    "🎯 أضف مهارات جديدة لملفك الشخصي",
                    "🔍 استخدم /search للبحث اليدوي"
                ]
                return "💡 **نصائح:**\n" + "\n".join(tips)
            
            tips = [
                "📝 اقرأ وصف الوظيفة بعناية قبل التقديم",
                "💼 تأكد من تحديث سيرتك الذاتية",
                "🎯 اكتب رسالة تغطية مخصصة لكل وظيفة"
            ]
            
            return "💡 **نصائح للتقديم:**\n" + "\n".join(tips)
            
        except Exception as e:
            logger.error(f"Error creating tips section: {e}")
            return ""
    
    async def _create_recommendations_section(self, user: User) -> str:
        """Creates personalized recommendations."""
        try:
            # Get user activity patterns
            user_prefs = await self.db_manager.get_user_preferences(user.telegram_id)
            
            recommendations = []
            
            if user_prefs and user_prefs.skills:
                if len(user_prefs.skills) < 3:
                    recommendations.append("🎯 أضف المزيد من المهارات لتحسين نتائج البحث")
            
            recommendations.extend([
                "📚 تابع دورات تطوير المهارات عبر الإنترنت",
                "🤝 وسع شبكة علاقاتك المهنية",
                "📈 حدث ملفك الشخصي على LinkedIn"
            ])
            
            if recommendations:
                return "🎯 **توصيات لك:**\n" + "\n".join(recommendations[:3])
            
            return ""
            
        except Exception as e:
            logger.error(f"Error creating recommendations section: {e}")
            return ""
    
    def _create_footer(self, notification_type: NotificationType) -> str:
        """Creates footer based on notification type."""
        footers = {
            NotificationType.DAILY_JOBS: "📱 /search للمزيد | ⚙️ /settings للإعدادات | 🆘 /support للمساعدة",
            NotificationType.URGENT_JOBS: "⚡ قدم بسرعة! | 🔍 /search للمزيد",
            NotificationType.WEEKLY_SUMMARY: "📊 /stats للإحصائيات | 🎯 /goals لتحديد الأهداف",
            NotificationType.CUSTOM_ALERT: "🔔 /notifications لإدارة التنبيهات"
        }
        
        return footers.get(notification_type, "📱 /help للمساعدة")
    
    def _create_notification_keyboard(
        self, 
        notification_type: NotificationType, 
        jobs: List[Job]
    ) -> Optional[InlineKeyboardMarkup]:
        """Creates inline keyboard for notification."""
        try:
            keyboard = []
            
            if notification_type == NotificationType.DAILY_JOBS and jobs:
                # Add quick action buttons for daily jobs
                if len(jobs) >= 1:
                    keyboard.append([
                        InlineKeyboardButton("💾 حفظ الأولى", callback_data=f"save_job_{jobs[0].id}"),
                        InlineKeyboardButton("🔍 وظائف مشابهة", callback_data=f"similar_jobs_{jobs[0].id}")
                    ])
                
                keyboard.append([
                    InlineKeyboardButton("📱 بحث جديد", callback_data="new_search"),
                    InlineKeyboardButton("⚙️ الإعدادات", callback_data="open_settings")
                ])
            
            elif notification_type == NotificationType.URGENT_JOBS and jobs:
                # Add urgent action buttons
                keyboard.append([
                    InlineKeyboardButton("⚡ تقديم سريع", url=jobs[0].apply_url),
                    InlineKeyboardButton("💾 حفظ للمراجعة", callback_data=f"save_job_{jobs[0].id}")
                ])
            
            elif notification_type == NotificationType.WEEKLY_SUMMARY:
                # Add summary action buttons
                keyboard.append([
                    InlineKeyboardButton("📊 إحصائيات مفصلة", callback_data="detailed_stats"),
                    InlineKeyboardButton("🎯 تحديد أهداف", callback_data="set_goals")
                ])
            
            # Add common buttons
            keyboard.append([
                InlineKeyboardButton("🔕 إيقاف الإشعارات", callback_data="disable_notifications"),
                InlineKeyboardButton("🆘 مساعدة", callback_data="get_help")
            ])
            
            return InlineKeyboardMarkup(keyboard) if keyboard else None
            
        except Exception as e:
            logger.error(f"Error creating notification keyboard: {e}")
            return None
    
    async def _record_notification(
        self, 
        user: User, 
        notification_type: NotificationType,
        content: str,
        jobs: List[Job]
    ):
        """Records the notification in the database."""
        try:
            notification = Notification(
                user_id=user.telegram_id,
                job_ids=[job.id for job in jobs] if jobs else [],
                message_content=content,
                notification_type=notification_type.value,
                sent_at=datetime.now()
            )
            
            await self.db_manager.save_notification(notification)
            
        except Exception as e:
            logger.error(f"Error recording notification: {e}")
    
    async def send_bulk_notification(
        self, 
        users: List[User], 
        notification_type: NotificationType,
        custom_data: Dict[str, Any] = None
    ) -> Dict[str, int]:
        """Sends bulk notifications to multiple users."""
        try:
            results = {
                'sent': 0,
                'failed': 0,
                'blocked': 0
            }
            
            for user in users:
                try:
                    success = await self.send_personalized_notification(
                        user, notification_type, custom_data=custom_data
                    )
                    
                    if success:
                        results['sent'] += 1
                    else:
                        results['failed'] += 1
                    
                    # Add delay between notifications
                    await asyncio.sleep(0.5)
                    
                except TelegramError as e:
                    if "bot was blocked" in str(e).lower():
                        results['blocked'] += 1
                    else:
                        results['failed'] += 1
                    
                except Exception as e:
                    logger.warning(f"Error sending bulk notification to user {user.telegram_id}: {e}")
                    results['failed'] += 1
            
            logger.info(f"Bulk notification results: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in bulk notification: {e}")
            return {'sent': 0, 'failed': len(users), 'blocked': 0}
    
    async def send_system_announcement(self, message: str, target_users: str = "all") -> Dict[str, int]:
        """Sends system announcement to users."""
        try:
            # Get target users
            if target_users == "all":
                users = await self.db_manager.get_active_users()
            elif target_users == "premium":
                users = await self.db_manager.get_premium_users()
            else:
                users = []
            
            if not users:
                return {'sent': 0, 'failed': 0, 'blocked': 0}
            
            # Create announcement content
            announcement = f"📢 **إعلان النظام**\n\n{message}\n\n"
            announcement += "شكراً لاستخدامك بوت الوظائف! 🤖"
            
            results = {
                'sent': 0,
                'failed': 0,
                'blocked': 0
            }
            
            for user in users:
                try:
                    await self.bot.send_message(
                        chat_id=user.telegram_id,
                        text=announcement,
                        parse_mode='Markdown'
                    )
                    
                    results['sent'] += 1
                    
                    # Add delay
                    await asyncio.sleep(0.3)
                    
                except TelegramError as e:
                    if "bot was blocked" in str(e).lower():
                        results['blocked'] += 1
                        await self.db_manager.deactivate_user(user.telegram_id)
                    else:
                        results['failed'] += 1
                        
                except Exception as e:
                    logger.warning(f"Error sending announcement to user {user.telegram_id}: {e}")
                    results['failed'] += 1
            
            logger.info(f"System announcement results: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error sending system announcement: {e}")
            return {'sent': 0, 'failed': 0, 'blocked': 0}
    
    async def get_notification_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Gets notification analytics for the specified period."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get notification statistics
            notifications = await self.db_manager.get_notifications_in_period(start_date, end_date)
            
            analytics = {
                'total_notifications': len(notifications),
                'notifications_by_type': {},
                'notifications_by_day': {},
                'average_per_day': 0,
                'most_active_users': []
            }
            
            # Group by type
            for notification in notifications:
                notif_type = notification.notification_type
                analytics['notifications_by_type'][notif_type] = \
                    analytics['notifications_by_type'].get(notif_type, 0) + 1
            
            # Group by day
            for notification in notifications:
                day = notification.sent_at.date().isoformat()
                analytics['notifications_by_day'][day] = \
                    analytics['notifications_by_day'].get(day, 0) + 1
            
            # Calculate average
            if days > 0:
                analytics['average_per_day'] = len(notifications) / days
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting notification analytics: {e}")
            return {}
    
    def create_custom_template(
        self, 
        template_id: str, 
        title: str, 
        content_template: str,
        **kwargs
    ) -> NotificationTemplate:
        """Creates a custom notification template."""
        try:
            template = NotificationTemplate(
                type=NotificationType.CUSTOM_ALERT,
                title=title,
                content_template=content_template,
                **kwargs
            )
            
            # Store custom template (could be saved to database)
            self.templates[template_id] = template
            
            logger.info(f"Created custom template: {template_id}")
            return template
            
        except Exception as e:
            logger.error(f"Error creating custom template: {e}")
            return None

