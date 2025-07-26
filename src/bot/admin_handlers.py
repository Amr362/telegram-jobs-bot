import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.database.manager import SupabaseManager
from src.scheduler.job_scheduler import JobNotificationScheduler
from src.scheduler.notification_manager import AdvancedNotificationManager, NotificationType
from src.scrapers.manager import ScrapingManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AdminHandlers:
    """Handles admin-only commands and operations."""
    
    def __init__(
        self, 
        db_manager: SupabaseManager,
        scheduler: JobNotificationScheduler,
        notification_manager: AdvancedNotificationManager
    ):
        self.db_manager = db_manager
        self.scheduler = scheduler
        self.notification_manager = notification_manager
        self.scraping_manager = ScrapingManager(db_manager)
        
        # Admin user IDs (should be loaded from config)
        self.admin_user_ids = {
            123456789,  # Replace with actual admin user IDs
            987654321   # Add more admin IDs as needed
        }
        
        logger.info("AdminHandlers initialized")
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is an admin."""
        return user_id in self.admin_user_ids
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main admin command with admin panel."""
        try:
            user_id = update.effective_user.id
            
            if not self.is_admin(user_id):
                await update.message.reply_text("❌ غير مصرح لك بالوصول لهذا الأمر.")
                return
            
            # Create admin panel keyboard
            keyboard = [
                [
                    InlineKeyboardButton("📊 إحصائيات النظام", callback_data="admin_system_stats"),
                    InlineKeyboardButton("👥 إحصائيات المستخدمين", callback_data="admin_user_stats")
                ],
                [
                    InlineKeyboardButton("🔍 فرض جمع الوظائف", callback_data="admin_force_scrape"),
                    InlineKeyboardButton("🔗 فحص الروابط", callback_data="admin_check_links")
                ],
                [
                    InlineKeyboardButton("📢 إرسال إعلان", callback_data="admin_broadcast"),
                    InlineKeyboardButton("📱 إرسال إشعار", callback_data="admin_send_notification")
                ],
                [
                    InlineKeyboardButton("⏰ حالة الجدولة", callback_data="admin_scheduler_status"),
                    InlineKeyboardButton("🗄️ حالة قاعدة البيانات", callback_data="admin_db_status")
                ],
                [
                    InlineKeyboardButton("🧹 تنظيف البيانات", callback_data="admin_cleanup"),
                    InlineKeyboardButton("📋 سجلات النظام", callback_data="admin_logs")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            admin_message = """
🔧 **لوحة تحكم الإدارة**

مرحباً بك في لوحة تحكم بوت الوظائف. يمكنك من هنا:

📊 **المراقبة**: عرض إحصائيات النظام والمستخدمين
🔍 **الصيانة**: فرض جمع الوظائف وفحص الروابط
📢 **التواصل**: إرسال إعلانات وإشعارات للمستخدمين
⚙️ **الإدارة**: مراقبة الجدولة وقاعدة البيانات

اختر العملية التي تريد تنفيذها:
            """
            
            await update.message.reply_text(
                admin_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in admin command: {e}")
            await update.message.reply_text("حدث خطأ في تحميل لوحة الإدارة.")
    
    async def system_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed system statistics."""
        try:
            user_id = update.effective_user.id
            
            if not self.is_admin(user_id):
                await update.message.reply_text("❌ غير مصرح لك بالوصول لهذا الأمر.")
                return
            
            # Get system statistics
            stats = await self._get_system_statistics()
            
            stats_message = f"""
📊 **إحصائيات النظام الشاملة**

👥 **المستخدمون:**
• إجمالي المستخدمين: {stats['users']['total']}
• المستخدمون النشطون: {stats['users']['active']}
• مستخدمون جدد اليوم: {stats['users']['new_today']}
• مستخدمون جدد هذا الأسبوع: {stats['users']['new_this_week']}

💼 **الوظائف:**
• إجمالي الوظائف: {stats['jobs']['total']}
• وظائف جديدة اليوم: {stats['jobs']['new_today']}
• وظائف جديدة هذا الأسبوع: {stats['jobs']['new_this_week']}
• الوظائف النشطة: {stats['jobs']['active']}

📱 **الإشعارات:**
• إشعارات اليوم: {stats['notifications']['today']}
• إشعارات هذا الأسبوع: {stats['notifications']['this_week']}
• متوسط الإشعارات اليومية: {stats['notifications']['daily_average']:.1f}

🔍 **عمليات الجمع:**
• عمليات جمع اليوم: {stats['scraping']['today']}
• آخر عملية جمع: {stats['scraping']['last_scrape']}
• نجاح عمليات الجمع: {stats['scraping']['success_rate']:.1f}%

⏰ **الجدولة:**
• المهام النشطة: {stats['scheduler']['active_jobs']}
• حالة الجدولة: {stats['scheduler']['status']}
• آخر تشغيل: {stats['scheduler']['last_run']}

🗄️ **قاعدة البيانات:**
• حالة الاتصال: {stats['database']['status']}
• حجم البيانات: {stats['database']['size']}
• آخر نسخة احتياطية: {stats['database']['last_backup']}
            """
            
            await update.message.reply_text(stats_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in system stats command: {e}")
            await update.message.reply_text("حدث خطأ في جلب إحصائيات النظام.")
    
    async def force_scrape_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Force immediate job scraping."""
        try:
            user_id = update.effective_user.id
            
            if not self.is_admin(user_id):
                await update.message.reply_text("❌ غير مصرح لك بالوصول لهذا الأمر.")
                return
            
            await update.message.reply_text("🔍 بدء عملية جمع الوظائف الفورية...")
            
            # Start scraping in background
            asyncio.create_task(self._perform_forced_scraping(update.effective_chat.id))
            
        except Exception as e:
            logger.error(f"Error in force scrape command: {e}")
            await update.message.reply_text("حدث خطأ في بدء عملية جمع الوظائف.")
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Broadcast message to all users."""
        try:
            user_id = update.effective_user.id
            
            if not self.is_admin(user_id):
                await update.message.reply_text("❌ غير مصرح لك بالوصول لهذا الأمر.")
                return
            
            # Get message from command arguments
            if not context.args:
                await update.message.reply_text(
                    "📢 **إرسال إعلان**\n\n"
                    "الاستخدام: `/broadcast رسالة الإعلان`\n\n"
                    "مثال: `/broadcast مرحباً بكم في التحديث الجديد!`",
                    parse_mode='Markdown'
                )
                return
            
            message = " ".join(context.args)
            
            await update.message.reply_text("📢 جاري إرسال الإعلان لجميع المستخدمين...")
            
            # Send broadcast
            results = await self.notification_manager.send_system_announcement(message, "all")
            
            result_message = f"""
📢 **نتائج الإعلان:**

✅ تم الإرسال: {results['sent']}
❌ فشل الإرسال: {results['failed']}
🚫 محظور: {results['blocked']}

إجمالي المحاولات: {sum(results.values())}
            """
            
            await update.message.reply_text(result_message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in broadcast command: {e}")
            await update.message.reply_text("حدث خطأ في إرسال الإعلان.")
    
    async def handle_admin_callbacks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin panel callback queries."""
        try:
            query = update.callback_query
            await query.answer()
            
            user_id = query.from_user.id
            
            if not self.is_admin(user_id):
                await query.edit_message_text("❌ غير مصرح لك بالوصول لهذا الأمر.")
                return
            
            data = query.data
            
            if data == "admin_system_stats":
                await self._show_system_stats(query)
            
            elif data == "admin_user_stats":
                await self._show_user_stats(query)
            
            elif data == "admin_force_scrape":
                await self._handle_force_scrape(query)
            
            elif data == "admin_check_links":
                await self._handle_check_links(query)
            
            elif data == "admin_broadcast":
                await self._handle_broadcast_setup(query)
            
            elif data == "admin_send_notification":
                await self._handle_notification_setup(query)
            
            elif data == "admin_scheduler_status":
                await self._show_scheduler_status(query)
            
            elif data == "admin_db_status":
                await self._show_database_status(query)
            
            elif data == "admin_cleanup":
                await self._handle_cleanup(query)
            
            elif data == "admin_logs":
                await self._show_system_logs(query)
            
        except Exception as e:
            logger.error(f"Error handling admin callback: {e}")
            await query.edit_message_text("حدث خطأ في معالجة الطلب.")
    
    async def _get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        try:
            stats = {
                'users': {},
                'jobs': {},
                'notifications': {},
                'scraping': {},
                'scheduler': {},
                'database': {}
            }
            
            # User statistics
            total_users = await self.db_manager.get_total_users_count()
            active_users = await self.db_manager.get_active_users_count()
            new_users_today = await self.db_manager.get_new_users_count(days=1)
            new_users_week = await self.db_manager.get_new_users_count(days=7)
            
            stats['users'] = {
                'total': total_users,
                'active': active_users,
                'new_today': new_users_today,
                'new_this_week': new_users_week
            }
            
            # Job statistics
            total_jobs = await self.db_manager.get_total_jobs_count()
            new_jobs_today = await self.db_manager.get_new_jobs_count(days=1)
            new_jobs_week = await self.db_manager.get_new_jobs_count(days=7)
            active_jobs = await self.db_manager.get_active_jobs_count()
            
            stats['jobs'] = {
                'total': total_jobs,
                'new_today': new_jobs_today,
                'new_this_week': new_jobs_week,
                'active': active_jobs
            }
            
            # Notification statistics
            notifications_today = await self.db_manager.get_notifications_count(days=1)
            notifications_week = await self.db_manager.get_notifications_count(days=7)
            daily_avg = notifications_week / 7 if notifications_week else 0
            
            stats['notifications'] = {
                'today': notifications_today,
                'this_week': notifications_week,
                'daily_average': daily_avg
            }
            
            # Scraping statistics
            scraping_today = await self.db_manager.get_scraping_count(days=1)
            last_scrape = await self.db_manager.get_last_scraping_time()
            success_rate = await self.db_manager.get_scraping_success_rate()
            
            stats['scraping'] = {
                'today': scraping_today,
                'last_scrape': last_scrape.strftime('%Y-%m-%d %H:%M') if last_scrape else 'غير متاح',
                'success_rate': success_rate * 100 if success_rate else 0
            }
            
            # Scheduler statistics
            scheduler_status = await self.scheduler.get_scheduler_status()
            
            stats['scheduler'] = {
                'active_jobs': scheduler_status.get('total_jobs', 0),
                'status': 'نشط' if scheduler_status.get('is_running') else 'متوقف',
                'last_run': 'متاح' if scheduler_status.get('is_running') else 'غير متاح'
            }
            
            # Database statistics
            db_health = await self.db_manager.health_check()
            
            stats['database'] = {
                'status': 'متصل' if db_health else 'غير متصل',
                'size': 'غير متاح',  # Could be implemented
                'last_backup': 'غير متاح'  # Could be implemented
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system statistics: {e}")
            return {}
    
    async def _perform_forced_scraping(self, chat_id: int):
        """Perform forced scraping and report results."""
        try:
            # Get active users for scraping criteria
            active_users = await self.db_manager.get_active_users()
            
            if not active_users:
                await self.notification_manager.bot.send_message(
                    chat_id=chat_id,
                    text="⚠️ لا يوجد مستخدمون نشطون لجمع الوظائف."
                )
                return
            
            # Collect search criteria
            search_criteria = set()
            for user in active_users[:50]:  # Limit to 50 users for forced scraping
                user_prefs = await self.db_manager.get_user_preferences(user.telegram_id)
                if user_prefs and user_prefs.skills:
                    search_criteria.update(user_prefs.skills[:3])  # Top 3 skills per user
            
            total_jobs = 0
            successful_sources = 0
            
            # Perform scraping
            for criteria in list(search_criteria)[:10]:  # Limit to 10 criteria
                try:
                    jobs = await self.scraping_manager.search_jobs_by_criteria(criteria)
                    total_jobs += len(jobs)
                    successful_sources += 1
                    
                    await asyncio.sleep(3)  # Delay between searches
                    
                except Exception as e:
                    logger.warning(f"Error scraping for criteria '{criteria}': {e}")
                    continue
            
            # Send results
            result_message = f"""
🔍 **نتائج جمع الوظائف الفوري:**

✅ الوظائف المجمعة: {total_jobs}
📊 المصادر الناجحة: {successful_sources}
🎯 معايير البحث: {len(search_criteria)}
⏰ وقت الانتهاء: {datetime.now().strftime('%H:%M:%S')}

{'✅ تمت العملية بنجاح!' if total_jobs > 0 else '⚠️ لم يتم العثور على وظائف جديدة.'}
            """
            
            await self.notification_manager.bot.send_message(
                chat_id=chat_id,
                text=result_message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in forced scraping: {e}")
            await self.notification_manager.bot.send_message(
                chat_id=chat_id,
                text="❌ حدث خطأ في عملية جمع الوظائف الفوري."
            )
    
    async def _show_system_stats(self, query):
        """Show system statistics in callback."""
        try:
            stats = await self._get_system_statistics()
            
            stats_message = f"""
📊 **إحصائيات النظام السريعة**

👥 المستخدمون: {stats['users']['total']} (نشط: {stats['users']['active']})
💼 الوظائف: {stats['jobs']['total']} (جديد اليوم: {stats['jobs']['new_today']})
📱 الإشعارات اليوم: {stats['notifications']['today']}
🔍 عمليات الجمع اليوم: {stats['scraping']['today']}
⏰ حالة الجدولة: {stats['scheduler']['status']}
🗄️ قاعدة البيانات: {stats['database']['status']}

للحصول على تفاصيل أكثر، استخدم /system_stats
            """
            
            keyboard = [[InlineKeyboardButton("🔙 العودة للوحة الإدارة", callback_data="admin_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                stats_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing system stats: {e}")
            await query.edit_message_text("حدث خطأ في جلب الإحصائيات.")
    
    async def _show_user_stats(self, query):
        """Show user statistics."""
        try:
            # Get user statistics
            total_users = await self.db_manager.get_total_users_count()
            active_users = await self.db_manager.get_active_users_count()
            new_today = await self.db_manager.get_new_users_count(days=1)
            new_week = await self.db_manager.get_new_users_count(days=7)
            
            # Get top active users
            top_users = await self.db_manager.get_most_active_users(limit=5)
            
            user_stats_message = f"""
👥 **إحصائيات المستخدمين**

📊 **الأرقام العامة:**
• إجمالي المستخدمين: {total_users}
• المستخدمون النشطون: {active_users}
• مستخدمون جدد اليوم: {new_today}
• مستخدمون جدد هذا الأسبوع: {new_week}
• معدل النشاط: {(active_users/total_users*100):.1f}% إذا كان total_users > 0 else 0

🏆 **أكثر المستخدمين نشاطاً:**
            """
            
            for i, user in enumerate(top_users, 1):
                user_stats_message += f"{i}. {user.first_name or 'مستخدم'} - {user.activity_score or 0} نقطة\n"
            
            keyboard = [[InlineKeyboardButton("🔙 العودة للوحة الإدارة", callback_data="admin_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                user_stats_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing user stats: {e}")
            await query.edit_message_text("حدث خطأ في جلب إحصائيات المستخدمين.")
    
    async def _handle_force_scrape(self, query):
        """Handle force scrape callback."""
        try:
            await query.edit_message_text("🔍 جاري بدء عملية جمع الوظائف الفورية...")
            
            # Start scraping in background
            asyncio.create_task(self._perform_forced_scraping(query.message.chat_id))
            
        except Exception as e:
            logger.error(f"Error handling force scrape: {e}")
            await query.edit_message_text("حدث خطأ في بدء عملية جمع الوظائف.")
    
    async def _show_scheduler_status(self, query):
        """Show scheduler status."""
        try:
            status = await self.scheduler.get_scheduler_status()
            
            status_message = f"""
⏰ **حالة نظام الجدولة**

🔄 الحالة: {'نشط' if status['is_running'] else 'متوقف'}
📋 إجمالي المهام: {status['total_jobs']}

📅 **المهام المجدولة:**
            """
            
            for job in status.get('jobs', []):
                next_run = job.get('next_run', 'غير محدد')
                status_message += f"• {job['name']}: {next_run}\n"
            
            keyboard = [[InlineKeyboardButton("🔙 العودة للوحة الإدارة", callback_data="admin_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                status_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing scheduler status: {e}")
            await query.edit_message_text("حدث خطأ في جلب حالة الجدولة.")
    
    async def _show_database_status(self, query):
        """Show database status."""
        try:
            health = await self.db_manager.health_check()
            
            db_message = f"""
🗄️ **حالة قاعدة البيانات**

🔗 الاتصال: {'متصل ✅' if health else 'غير متصل ❌'}
📊 الحالة: {'صحية' if health else 'تحتاج فحص'}

📈 **الإحصائيات:**
• إجمالي المستخدمين: {await self.db_manager.get_total_users_count()}
• إجمالي الوظائف: {await self.db_manager.get_total_jobs_count()}
• إجمالي الإشعارات: {await self.db_manager.get_notifications_count(days=30)}

⚡ **الأداء:**
• زمن الاستجابة: جيد
• آخر نسخة احتياطية: غير متاح
            """
            
            keyboard = [[InlineKeyboardButton("🔙 العودة للوحة الإدارة", callback_data="admin_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                db_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing database status: {e}")
            await query.edit_message_text("حدث خطأ في جلب حالة قاعدة البيانات.")
    
    async def _handle_cleanup(self, query):
        """Handle data cleanup."""
        try:
            cleanup_message = """
🧹 **تنظيف البيانات**

هذه العملية ستقوم بـ:
• حذف الوظائف القديمة (أكثر من 30 يوم)
• حذف الإشعارات القديمة (أكثر من 7 أيام)
• تنظيف الآراء المكررة
• تحديث إحصائيات النظام

⚠️ هذه العملية لا يمكن التراجع عنها!
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ تأكيد التنظيف", callback_data="admin_confirm_cleanup"),
                    InlineKeyboardButton("❌ إلغاء", callback_data="admin_back")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                cleanup_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error handling cleanup: {e}")
            await query.edit_message_text("حدث خطأ في إعداد عملية التنظيف.")
    
    async def get_admin_statistics(self) -> Dict[str, Any]:
        """Get comprehensive admin statistics."""
        try:
            return await self._get_system_statistics()
        except Exception as e:
            logger.error(f"Error getting admin statistics: {e}")
            return {}

