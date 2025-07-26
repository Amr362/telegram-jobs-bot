from enum import Enum
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

class ConversationState(Enum):
    """Enum for conversation states during user onboarding."""
    LANGUAGE_SELECTION = "language_selection"
    LOCATION_PREFERENCE = "location_preference"
    SKILLS_INPUT = "skills_input"
    NOTIFICATION_FREQUENCY = "notification_frequency"
    CONFIRMATION = "confirmation"
    COMPLETED = "completed"

class ConversationManager:
    """Manages conversation flow during user onboarding."""
    
    def __init__(self):
        self.states = ConversationState
    
    async def start_onboarding(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Starts the user onboarding process."""
        user = update.effective_user
        
        welcome_message = f"""
🤖 مرحباً {user.first_name}! أهلاً بك في بوت الوظائف الذكي

أنا هنا لمساعدتك في العثور على أفضل الوظائف المناسبة لمهاراتك واهتماماتك. سأرسل لك إشعارات يومية بالوظائف الجديدة بناءً على تفضيلاتك.

دعني أجمع بعض المعلومات عنك لأتمكن من تقديم أفضل خدمة ممكنة.

أولاً، ما نوع الوظائف التي تبحث عنها؟
        """
        
        keyboard = [
            [InlineKeyboardButton("🇸🇦 وظائف عربية/محلية", callback_data="lang_arabic")],
            [InlineKeyboardButton("🌍 وظائف عالمية", callback_data="lang_global")],
            [InlineKeyboardButton("🔄 كلاهما", callback_data="lang_both")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
        
        # Store user data in context
        context.user_data['user_id'] = user.id
        context.user_data['username'] = user.username
        context.user_data['first_name'] = user.first_name
        context.user_data['conversation_state'] = ConversationState.LANGUAGE_SELECTION.value
        
        return ConversationState.LANGUAGE_SELECTION.value
    
    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Handles language/region selection."""
        query = update.callback_query
        await query.answer()
        
        language_map = {
            "lang_arabic": "arabic",
            "lang_global": "global", 
            "lang_both": "both"
        }
        
        selected_language = language_map.get(query.data)
        context.user_data['language_preference'] = selected_language
        
        language_text = {
            "arabic": "الوظائف العربية/المحلية",
            "global": "الوظائف العالمية",
            "both": "كلا النوعين"
        }
        
        message = f"""
✅ تم اختيار: {language_text[selected_language]}

الآن، ما تفضيلك بخصوص موقع العمل؟
        """
        
        keyboard = [
            [InlineKeyboardButton("🏢 في بلد محدد", callback_data="location_specific")],
            [InlineKeyboardButton("🌐 عمل عن بُعد", callback_data="location_remote")],
            [InlineKeyboardButton("🔄 كلاهما", callback_data="location_both")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)
        context.user_data['conversation_state'] = ConversationState.LOCATION_PREFERENCE.value
        
        return ConversationState.LOCATION_PREFERENCE.value
    
    async def handle_location_preference(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Handles location preference selection."""
        query = update.callback_query
        await query.answer()
        
        location_map = {
            "location_specific": "specific",
            "location_remote": "remote",
            "location_both": "both"
        }
        
        selected_location = location_map.get(query.data)
        context.user_data['location_preference'] = selected_location
        
        location_text = {
            "specific": "في بلد محدد",
            "remote": "عمل عن بُعد", 
            "both": "كلاهما"
        }
        
        # If specific location is selected, ask for country
        if selected_location == "specific":
            message = f"""
✅ تم اختيار: {location_text[selected_location]}

يرجى كتابة اسم البلد أو المدينة التي تفضل العمل بها:

مثال: السعودية، الإمارات، مصر، الأردن، الكويت
            """
            await query.edit_message_text(message)
            context.user_data['awaiting_country'] = True
        else:
            message = f"""
✅ تم اختيار: {location_text[selected_location]}

الآن، ما هي مهاراتك أو المجالات التي تهتم بها؟

يرجى كتابة مهاراتك مفصولة بفواصل:

مثال: Python, تطوير الويب, التصميم الجرافيكي, التسويق الرقمي, إدارة المشاريع
            """
            await query.edit_message_text(message)
            context.user_data['conversation_state'] = ConversationState.SKILLS_INPUT.value
        
        return ConversationState.SKILLS_INPUT.value
    
    async def handle_country_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Handles country input for specific location preference."""
        country = update.message.text.strip()
        context.user_data['preferred_country'] = country
        context.user_data['awaiting_country'] = False
        
        message = f"""
✅ تم تسجيل البلد المفضل: {country}

الآن، ما هي مهاراتك أو المجالات التي تهتم بها؟

يرجى كتابة مهاراتك مفصولة بفواصل:

مثال: Python, تطوير الويب, التصميم الجرافيكي, التسويق الرقمي, إدارة المشاريع
        """
        
        await update.message.reply_text(message)
        context.user_data['conversation_state'] = ConversationState.SKILLS_INPUT.value
        
        return ConversationState.SKILLS_INPUT.value
    
    async def handle_skills_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Handles skills input."""
        skills_text = update.message.text.strip()
        skills_list = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
        
        context.user_data['skills'] = skills_list
        
        message = f"""
✅ تم تسجيل مهاراتك: {', '.join(skills_list)}

أخيراً، كم مرة تريد تلقي إشعارات الوظائف يومياً؟
        """
        
        keyboard = [
            [InlineKeyboardButton("📅 مرة واحدة صباحاً", callback_data="freq_once")],
            [InlineKeyboardButton("📅 مرتين (صباحاً ومساءً)", callback_data="freq_twice")],
            [InlineKeyboardButton("📅 ثلاث مرات", callback_data="freq_three")],
            [InlineKeyboardButton("🔕 حسب الحاجة فقط", callback_data="freq_ondemand")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup)
        context.user_data['conversation_state'] = ConversationState.NOTIFICATION_FREQUENCY.value
        
        return ConversationState.NOTIFICATION_FREQUENCY.value
    
    async def handle_notification_frequency(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Handles notification frequency selection."""
        query = update.callback_query
        await query.answer()
        
        frequency_map = {
            "freq_once": 1,
            "freq_twice": 2,
            "freq_three": 3,
            "freq_ondemand": 0
        }
        
        selected_frequency = frequency_map.get(query.data)
        context.user_data['notification_frequency'] = selected_frequency
        
        frequency_text = {
            1: "مرة واحدة صباحاً",
            2: "مرتين (صباحاً ومساءً)",
            3: "ثلاث مرات يومياً",
            0: "حسب الحاجة فقط"
        }
        
        # Show confirmation summary
        await self.show_confirmation(query, context, frequency_text[selected_frequency])
        context.user_data['conversation_state'] = ConversationState.CONFIRMATION.value
        
        return ConversationState.CONFIRMATION.value
    
    async def show_confirmation(self, query, context: ContextTypes.DEFAULT_TYPE, frequency_text: str):
        """Shows confirmation summary of user preferences."""
        user_data = context.user_data
        
        language_text = {
            "arabic": "الوظائف العربية/المحلية",
            "global": "الوظائف العالمية",
            "both": "كلا النوعين"
        }
        
        location_text = {
            "specific": f"في بلد محدد ({user_data.get('preferred_country', 'غير محدد')})",
            "remote": "عمل عن بُعد",
            "both": "كلاهما"
        }
        
        summary = f"""
📋 ملخص تفضيلاتك:

🌍 نوع الوظائف: {language_text.get(user_data.get('language_preference'), 'غير محدد')}
📍 موقع العمل: {location_text.get(user_data.get('location_preference'), 'غير محدد')}
🎯 المهارات: {', '.join(user_data.get('skills', []))}
🔔 تكرار الإشعارات: {frequency_text}

هل هذه المعلومات صحيحة؟
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ نعم، احفظ التفضيلات", callback_data="confirm_yes")],
            [InlineKeyboardButton("❌ لا، أريد التعديل", callback_data="confirm_no")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(summary, reply_markup=reply_markup)
    
    async def handle_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
        """Handles final confirmation."""
        query = update.callback_query
        await query.answer()
        
        if query.data == "confirm_yes":
            # Here we would save to database (will implement in next phase)
            message = """
🎉 تم حفظ تفضيلاتك بنجاح!

سأبدأ الآن في البحث عن الوظائف المناسبة لك وإرسال الإشعارات حسب تفضيلاتك.

يمكنك استخدام الأوامر التالية:
• /profile - عرض ملفك الشخصي
• /settings - تعديل التفضيلات
• /search - البحث اليدوي عن الوظائف
• /help - المساعدة

مرحباً بك في عائلة بوت الوظائف الذكي! 🚀
            """
            
            await query.edit_message_text(message)
            context.user_data['conversation_state'] = ConversationState.COMPLETED.value
            context.user_data['onboarding_completed'] = True
            
            return ConversationState.COMPLETED.value
        else:
            # Restart onboarding
            await self.start_onboarding(update, context)
            return ConversationState.LANGUAGE_SELECTION.value
    
    def get_user_preferences(self, context: ContextTypes.DEFAULT_TYPE) -> Dict[str, Any]:
        """Extracts user preferences from context."""
        return {
            'user_id': context.user_data.get('user_id'),
            'username': context.user_data.get('username'),
            'first_name': context.user_data.get('first_name'),
            'language_preference': context.user_data.get('language_preference'),
            'location_preference': context.user_data.get('location_preference'),
            'preferred_country': context.user_data.get('preferred_country'),
            'skills': context.user_data.get('skills', []),
            'notification_frequency': context.user_data.get('notification_frequency'),
            'onboarding_completed': context.user_data.get('onboarding_completed', False)
        }

