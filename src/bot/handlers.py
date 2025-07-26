from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from src.utils.logger import get_logger
from src.bot.conversation import ConversationManager, ConversationState

logger = get_logger(__name__)

class CommandHandlers:
    """Handles all bot commands."""
    
    def __init__(self):
        self.conversation_manager = ConversationManager()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Handles the /start command."""
        user = update.effective_user
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
        # Check if user has completed onboarding
        if context.user_data.get('onboarding_completed'):
            await self.show_main_menu(update, context)
            return ConversationHandler.END
        else:
            # Start onboarding process
            return await self.conversation_manager.start_onboarding(update, context)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the /help command."""
        help_text = """
🤖 **بوت الوظائف الذكي - المساعدة**

**الأوامر المتاحة:**
• `/start` - بدء استخدام البوت أو إعادة الإعداد
• `/profile` - عرض ملفك الشخصي وتفضيلاتك
• `/settings` - تعديل تفضيلاتك
• `/search` - البحث اليدوي عن الوظائف
• `/jobs` - عرض آخر الوظائف المتاحة
• `/help` - عرض هذه المساعدة

**كيف يعمل البوت:**
1. يبحث يومياً عن الوظائف الجديدة من مصادر متعددة
2. يرسل لك إشعارات بالوظائف المناسبة لمهاراتك
3. يتحقق من صحة روابط التقديم
4. يجمع آراء الناس عن الشركات (إن أمكن)

**المصادر المدعومة:**
• Google Jobs
• RemoteOK, Remotive, AngelList
• Wuzzuf, Bayt (للوظائف العربية)
• مواقع أخرى متنوعة

إذا كنت تواجه أي مشكلة، يرجى التواصل مع الدعم.
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
        logger.info(f"Help command used by user {update.effective_user.id}")
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the /profile command."""
        if not context.user_data.get('onboarding_completed'):
            await update.message.reply_text(
                "يرجى إكمال إعداد ملفك الشخصي أولاً باستخدام الأمر /start"
            )
            return
        
        preferences = self.conversation_manager.get_user_preferences(context)
        
        language_text = {
            "arabic": "الوظائف العربية/المحلية",
            "global": "الوظائف العالمية",
            "both": "كلا النوعين"
        }
        
        location_text = {
            "specific": f"في بلد محدد ({preferences.get('preferred_country', 'غير محدد')})",
            "remote": "عمل عن بُعد",
            "both": "كلاهما"
        }
        
        frequency_text = {
            1: "مرة واحدة صباحاً",
            2: "مرتين (صباحاً ومساءً)",
            3: "ثلاث مرات يومياً",
            0: "حسب الحاجة فقط"
        }
        
        profile_text = f"""
👤 **ملفك الشخصي**

**المعلومات الأساسية:**
• الاسم: {preferences.get('first_name', 'غير محدد')}
• اسم المستخدم: @{preferences.get('username', 'غير محدد')}

**تفضيلات البحث:**
• نوع الوظائف: {language_text.get(preferences.get('language_preference'), 'غير محدد')}
• موقع العمل: {location_text.get(preferences.get('location_preference'), 'غير محدد')}
• المهارات: {', '.join(preferences.get('skills', []))}
• تكرار الإشعارات: {frequency_text.get(preferences.get('notification_frequency'), 'غير محدد')}

**الإحصائيات:**
• تاريخ التسجيل: اليوم
• عدد الوظائف المرسلة: 0
• عدد التقديمات: 0

لتعديل تفضيلاتك، استخدم الأمر /settings
        """
        
        keyboard = [
            [InlineKeyboardButton("⚙️ تعديل التفضيلات", callback_data="edit_settings")],
            [InlineKeyboardButton("🔍 البحث عن وظائف", callback_data="manual_search")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(profile_text, reply_markup=reply_markup, parse_mode='Markdown')
        logger.info(f"Profile command used by user {update.effective_user.id}")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the /settings command."""
        if not context.user_data.get('onboarding_completed'):
            await update.message.reply_text(
                "يرجى إكمال إعداد ملفك الشخصي أولاً باستخدام الأمر /start"
            )
            return
        
        settings_text = """
⚙️ **إعدادات البوت**

ما الذي تريد تعديله؟
        """
        
        keyboard = [
            [InlineKeyboardButton("🌍 نوع الوظائف", callback_data="edit_language")],
            [InlineKeyboardButton("📍 موقع العمل", callback_data="edit_location")],
            [InlineKeyboardButton("🎯 المهارات", callback_data="edit_skills")],
            [InlineKeyboardButton("🔔 تكرار الإشعارات", callback_data="edit_frequency")],
            [InlineKeyboardButton("🔄 إعادة الإعداد الكامل", callback_data="full_reset")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(settings_text, reply_markup=reply_markup, parse_mode='Markdown')
        logger.info(f"Settings command used by user {update.effective_user.id}")
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the /search command for manual job search."""
        if not context.user_data.get('onboarding_completed'):
            await update.message.reply_text(
                "يرجى إكمال إعداد ملفك الشخصي أولاً باستخدام الأمر /start"
            )
            return
        
        search_text = """
🔍 **البحث اليدوي عن الوظائف**

سأبحث لك عن الوظائف الجديدة بناءً على تفضيلاتك المحفوظة...

⏳ جاري البحث، يرجى الانتظار...
        """
        
        message = await update.message.reply_text(search_text, parse_mode='Markdown')
        
        # Here we would call the scraping functions (will implement in later phases)
        # For now, show a placeholder
        await message.edit_text(
            "🔍 **نتائج البحث**\n\n"
            "⚠️ وحدة البحث قيد التطوير. سيتم تفعيلها في الإصدار القادم.\n\n"
            "في الوقت الحالي، ستتلقى الإشعارات اليومية تلقائياً حسب جدولك المحدد.",
            parse_mode='Markdown'
        )
        
        logger.info(f"Manual search requested by user {update.effective_user.id}")
    
    async def jobs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles the /jobs command to show recent jobs."""
        if not context.user_data.get('onboarding_completed'):
            await update.message.reply_text(
                "يرجى إكمال إعداد ملفك الشخصي أولاً باستخدام الأمر /start"
            )
            return
        
        # Placeholder for showing recent jobs
        jobs_text = """
💼 **آخر الوظائف المتاحة**

⚠️ قاعدة بيانات الوظائف قيد الإعداد. سيتم عرض الوظائف هنا قريباً.

في الوقت الحالي، ستتلقى الإشعارات اليومية تلقائياً حسب تفضيلاتك.
        """
        
        await update.message.reply_text(jobs_text, parse_mode='Markdown')
        logger.info(f"Jobs command used by user {update.effective_user.id}")
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Shows the main menu for existing users."""
        user = update.effective_user
        
        menu_text = f"""
🤖 مرحباً مرة أخرى {user.first_name}!

أنا جاهز لمساعدتك في العثور على أفضل الوظائف. ماذا تريد أن تفعل؟
        """
        
        keyboard = [
            [InlineKeyboardButton("🔍 البحث عن وظائف", callback_data="manual_search")],
            [InlineKeyboardButton("💼 آخر الوظائف", callback_data="recent_jobs")],
            [InlineKeyboardButton("👤 ملفي الشخصي", callback_data="view_profile")],
            [InlineKeyboardButton("⚙️ الإعدادات", callback_data="view_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(menu_text, reply_markup=reply_markup)

class CallbackHandlers:
    """Handles callback queries from inline keyboards."""
    
    def __init__(self):
        self.conversation_manager = ConversationManager()
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main callback query handler."""
        query = update.callback_query
        data = query.data
        
        logger.info(f"Callback query received: {data} from user {query.from_user.id}")
        
        # Handle conversation callbacks
        if data.startswith('lang_'):
            return await self.conversation_manager.handle_language_selection(update, context)
        elif data.startswith('location_'):
            return await self.conversation_manager.handle_location_preference(update, context)
        elif data.startswith('freq_'):
            return await self.conversation_manager.handle_notification_frequency(update, context)
        elif data.startswith('confirm_'):
            return await self.conversation_manager.handle_confirmation(update, context)
        
        # Handle main menu callbacks
        elif data == "manual_search":
            await query.answer("🔍 جاري البحث...")
            await query.edit_message_text("⏳ جاري البحث عن الوظائف، يرجى الانتظار...")
            # Here we would call search functions
        
        elif data == "recent_jobs":
            await query.answer("💼 عرض آخر الوظائف...")
            await query.edit_message_text("💼 قاعدة بيانات الوظائف قيد الإعداد...")
        
        elif data == "view_profile":
            await query.answer("👤 عرض الملف الشخصي...")
            # Here we would show profile info
        
        elif data == "view_settings":
            await query.answer("⚙️ فتح الإعدادات...")
            # Here we would show settings menu
        
        else:
            await query.answer("⚠️ خيار غير معروف")
            logger.warning(f"Unknown callback data: {data}")

class MessageHandlers:
    """Handles text messages."""
    
    def __init__(self):
        self.conversation_manager = ConversationManager()
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles text messages based on conversation state."""
        user = update.effective_user
        message_text = update.message.text
        
        logger.info(f"Text message received from user {user.id}: {message_text[:50]}...")
        
        # Check conversation state
        conversation_state = context.user_data.get('conversation_state')
        
        if conversation_state == ConversationState.SKILLS_INPUT.value:
            if context.user_data.get('awaiting_country'):
                return await self.conversation_manager.handle_country_input(update, context)
            else:
                return await self.conversation_manager.handle_skills_input(update, context)
        
        # If no active conversation, show help
        else:
            await update.message.reply_text(
                "لم أفهم رسالتك. يرجى استخدام الأوامر المتاحة أو /help للمساعدة."
            )
    
    async def handle_unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles unknown commands."""
        await update.message.reply_text(
            "أمر غير معروف. يرجى استخدام /help لمعرفة الأوامر المتاحة."
        )
        logger.info(f"Unknown command from user {update.effective_user.id}: {update.message.text}")

class ErrorHandlers:
    """Handles errors and exceptions."""
    
    @staticmethod
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Global error handler."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Try to inform the user
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى لاحقاً."
                )
            except Exception as e:
                logger.error(f"Failed to send error message to user: {e}")

