import asyncio
from typing import List, Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from src.utils.support_system import JobSupportSystem, SupportRequest, SupportCategory, SupportLanguage
from src.database.manager import SupabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Conversation states
SUPPORT_CATEGORY, SUPPORT_QUESTION, SUPPORT_JOB_SELECTION = range(3)

class SupportHandlers:
    """Handles all support-related bot interactions."""
    
    def __init__(self, db_manager: SupabaseManager):
        self.db_manager = db_manager
        self.support_system = JobSupportSystem(db_manager)
        
        logger.info("SupportHandlers initialized")
    
    async def support_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handles the /support command."""
        try:
            user_id = update.effective_user.id
            
            # Create support category keyboard
            keyboard = [
                [
                    InlineKeyboardButton("📝 التقديم للوظائف", callback_data="support_job_application"),
                    InlineKeyboardButton("💻 المهارات التقنية", callback_data="support_technical_skills")
                ],
                [
                    InlineKeyboardButton("🎯 التحضير للمقابلات", callback_data="support_interview_prep"),
                    InlineKeyboardButton("💰 التفاوض على الراتب", callback_data="support_salary_negotiation")
                ],
                [
                    InlineKeyboardButton("🏠 العمل عن بعد", callback_data="support_remote_work"),
                    InlineKeyboardButton("📄 السيرة الذاتية", callback_data="support_resume_cv")
                ],
                [
                    InlineKeyboardButton("🏢 معلومات الشركات", callback_data="support_company_info"),
                    InlineKeyboardButton("🎓 نصائح مهنية", callback_data="support_career_advice")
                ],
                [
                    InlineKeyboardButton("🔍 بحث بالكلمات المفتاحية", callback_data="support_keyword_search"),
                    InlineKeyboardButton("❓ سؤال عام", callback_data="support_general")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            message = """
🆘 **مركز الدعم والمساعدة**

مرحباً بك في مركز الدعم! يمكنني مساعدتك في:

📝 **التقديم للوظائف** - نصائح للتقديم الناجح
💻 **المهارات التقنية** - تطوير وتحسين مهاراتك
🎯 **التحضير للمقابلات** - استعداد شامل للمقابلات
💰 **التفاوض على الراتب** - استراتيجيات التفاوض
🏠 **العمل عن بعد** - نصائح للعمل من المنزل
📄 **السيرة الذاتية** - كتابة وتحسين CV
🏢 **معلومات الشركات** - معرفة المزيد عن أصحاب العمل
🎓 **نصائح مهنية** - إرشادات لتطوير المسار المهني

اختر الموضوع الذي تحتاج المساعدة فيه:
            """
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            return SUPPORT_CATEGORY
            
        except Exception as e:
            logger.error(f"Error in support command: {e}")
            await update.message.reply_text("عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.")
            return ConversationHandler.END
    
    async def support_category_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handles support category selection."""
        try:
            query = update.callback_query
            await query.answer()
            
            category_data = query.data.replace("support_", "")
            
            # Map callback data to categories
            category_map = {
                "job_application": SupportCategory.JOB_APPLICATION,
                "technical_skills": SupportCategory.TECHNICAL_SKILLS,
                "interview_prep": SupportCategory.INTERVIEW_PREP,
                "salary_negotiation": SupportCategory.SALARY_NEGOTIATION,
                "remote_work": SupportCategory.REMOTE_WORK,
                "resume_cv": SupportCategory.RESUME_CV,
                "company_info": SupportCategory.COMPANY_INFO,
                "career_advice": SupportCategory.CAREER_ADVICE,
                "general": SupportCategory.GENERAL
            }
            
            if category_data == "keyword_search":
                await query.edit_message_text(
                    "🔍 **البحث بالكلمات المفتاحية**\n\n"
                    "أرسل الكلمات المفتاحية التي تريد البحث عنها، مفصولة بفواصل.\n"
                    "مثال: python, تطوير ويب, مقابلة عمل",
                    parse_mode='Markdown'
                )
                context.user_data['support_mode'] = 'keyword_search'
                return SUPPORT_QUESTION
            
            category = category_map.get(category_data, SupportCategory.GENERAL)
            context.user_data['support_category'] = category
            
            # Get category-specific quick questions
            quick_questions = self._get_quick_questions(category)
            
            if quick_questions:
                keyboard = []
                for question in quick_questions:
                    keyboard.append([InlineKeyboardButton(question, callback_data=f"quick_{question[:50]}")])
                
                keyboard.append([InlineKeyboardButton("✍️ اكتب سؤالك الخاص", callback_data="custom_question")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    f"📋 **{self._get_category_name(category)}**\n\n"
                    "اختر سؤالاً من الأسئلة الشائعة أو اكتب سؤالك الخاص:",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(
                    f"📋 **{self._get_category_name(category)}**\n\n"
                    "اكتب سؤالك وسأحاول مساعدتك:",
                    parse_mode='Markdown'
                )
            
            return SUPPORT_QUESTION
            
        except Exception as e:
            logger.error(f"Error in category selection: {e}")
            await query.edit_message_text("عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.")
            return ConversationHandler.END
    
    async def support_question_received(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handles support questions."""
        try:
            user_id = update.effective_user.id
            
            # Handle callback queries (quick questions)
            if update.callback_query:
                query = update.callback_query
                await query.answer()
                
                if query.data == "custom_question":
                    await query.edit_message_text(
                        "✍️ **اكتب سؤالك**\n\n"
                        "اكتب سؤالك بالتفصيل وسأحاول مساعدتك:",
                        parse_mode='Markdown'
                    )
                    return SUPPORT_QUESTION
                
                elif query.data.startswith("quick_"):
                    question = query.data.replace("quick_", "")
                    await self._process_support_question(query, user_id, question, context)
                    return ConversationHandler.END
            
            # Handle text messages
            elif update.message:
                question = update.message.text
                
                # Handle keyword search
                if context.user_data.get('support_mode') == 'keyword_search':
                    await self._handle_keyword_search(update, user_id, question)
                    return ConversationHandler.END
                
                # Handle regular questions
                else:
                    await self._process_support_question(update, user_id, question, context)
                    return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Error processing support question: {e}")
            await update.message.reply_text("عذراً، حدث خطأ في معالجة سؤالك. يرجى المحاولة مرة أخرى.")
            return ConversationHandler.END
    
    async def _process_support_question(self, update_or_query, user_id: int, question: str, context: ContextTypes.DEFAULT_TYPE):
        """Processes a support question and sends response."""
        try:
            # Show typing indicator
            if hasattr(update_or_query, 'message'):
                await update_or_query.message.reply_text("🤔 جاري البحث عن إجابة...")
            else:
                await update_or_query.edit_message_text("🤔 جاري البحث عن إجابة...")
            
            # Create support request
            category = context.user_data.get('support_category', SupportCategory.GENERAL)
            
            support_request = SupportRequest(
                user_id=user_id,
                category=category,
                question=question,
                language=SupportLanguage.ARABIC
            )
            
            # Process the request
            response = await self.support_system.process_support_request(support_request)
            
            # Format the response
            formatted_response = self._format_support_response(response)
            
            # Create keyboard for follow-up actions
            keyboard = []
            
            # Add related jobs if available
            if response.related_jobs:
                keyboard.append([InlineKeyboardButton("🔍 وظائف ذات صلة", callback_data="show_related_jobs")])
                context.user_data['related_jobs'] = response.related_jobs
            
            # Add follow-up questions if available
            if response.follow_up_questions:
                keyboard.append([InlineKeyboardButton("❓ أسئلة أخرى", callback_data="show_followup")])
                context.user_data['follow_up_questions'] = response.follow_up_questions
            
            # Add helpful links if available
            if response.helpful_links:
                keyboard.append([InlineKeyboardButton("🔗 روابط مفيدة", callback_data="show_links")])
                context.user_data['helpful_links'] = response.helpful_links
            
            keyboard.append([InlineKeyboardButton("🆘 سؤال جديد", callback_data="new_support_question")])
            
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            # Send response
            if hasattr(update_or_query, 'message'):
                await update_or_query.message.reply_text(
                    formatted_response,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            else:
                await update_or_query.edit_message_text(
                    formatted_response,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            
        except Exception as e:
            logger.error(f"Error processing support question: {e}")
            error_message = "عذراً، حدث خطأ في معالجة سؤالك. يرجى المحاولة مرة أخرى."
            
            if hasattr(update_or_query, 'message'):
                await update_or_query.message.reply_text(error_message)
            else:
                await update_or_query.edit_message_text(error_message)
    
    async def _handle_keyword_search(self, update: Update, user_id: int, keywords_text: str):
        """Handles keyword-based search."""
        try:
            # Parse keywords
            keywords = [k.strip() for k in keywords_text.split(',')]
            
            # Search support content
            results = await self.support_system.search_support_by_keywords(keywords)
            
            if not results:
                await update.message.reply_text(
                    "🔍 **نتائج البحث**\n\n"
                    "لم أجد نتائج مطابقة للكلمات المفتاحية التي أدخلتها.\n"
                    "جرب كلمات مفتاحية أخرى أو استخدم /support للحصول على المساعدة.",
                    parse_mode='Markdown'
                )
                return
            
            # Format results
            response = "🔍 **نتائج البحث**\n\n"
            
            for i, result in enumerate(results[:3], 1):  # Show top 3 results
                response += f"**{i}. {result['question']}**\n"
                response += f"{result['answer'][:200]}...\n\n"
            
            # Add keyboard for more details
            keyboard = []
            for i, result in enumerate(results[:3]):
                keyboard.append([InlineKeyboardButton(
                    f"التفاصيل الكاملة للنتيجة {i+1}",
                    callback_data=f"search_detail_{i}"
                )])
            
            keyboard.append([InlineKeyboardButton("🔍 بحث جديد", callback_data="new_keyword_search")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Store results for detailed view
            context.user_data['search_results'] = results
            
            await update.message.reply_text(
                response,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            await update.message.reply_text("عذراً، حدث خطأ في البحث. يرجى المحاولة مرة أخرى.")
    
    def _format_support_response(self, response) -> str:
        """Formats the support response for display."""
        formatted = f"💡 **الإجابة:**\n\n{response.answer}\n\n"
        
        if response.confidence_score > 0.7:
            formatted += "✅ *إجابة موثوقة*\n\n"
        elif response.confidence_score > 0.5:
            formatted += "⚠️ *إجابة جيدة - قد تحتاج تفاصيل إضافية*\n\n"
        else:
            formatted += "ℹ️ *إجابة عامة - يُنصح بالبحث عن مصادر إضافية*\n\n"
        
        return formatted
    
    def _get_quick_questions(self, category: SupportCategory) -> List[str]:
        """Gets quick questions for a category."""
        questions_map = {
            SupportCategory.JOB_APPLICATION: [
                "كيف أكتب رسالة تغطية مميزة؟",
                "ما هي أفضل طريقة للتقديم؟",
                "كيف أتابع طلب التوظيف؟"
            ],
            SupportCategory.TECHNICAL_SKILLS: [
                "ما هي أهم المهارات التقنية المطلوبة؟",
                "كيف أطور مهاراتي في البرمجة؟",
                "ما هي أفضل المصادر للتعلم؟"
            ],
            SupportCategory.INTERVIEW_PREP: [
                "كيف أستعد للمقابلة الشخصية؟",
                "ما هي الأسئلة الشائعة في المقابلات؟",
                "كيف أتعامل مع المقابلات التقنية؟"
            ],
            SupportCategory.REMOTE_WORK: [
                "كيف أجد وظائف عن بعد؟",
                "ما هي نصائح العمل من المنزل؟",
                "كيف أنظم وقتي في العمل عن بعد؟"
            ],
            SupportCategory.RESUME_CV: [
                "كيف أكتب سيرة ذاتية مميزة؟",
                "ما هي أهم أقسام السيرة الذاتية؟",
                "كيف أبرز إنجازاتي في السيرة الذاتية؟"
            ]
        }
        
        return questions_map.get(category, [])
    
    def _get_category_name(self, category: SupportCategory) -> str:
        """Gets the Arabic name for a category."""
        names = {
            SupportCategory.JOB_APPLICATION: "التقديم للوظائف",
            SupportCategory.TECHNICAL_SKILLS: "المهارات التقنية",
            SupportCategory.INTERVIEW_PREP: "التحضير للمقابلات",
            SupportCategory.SALARY_NEGOTIATION: "التفاوض على الراتب",
            SupportCategory.CAREER_ADVICE: "النصائح المهنية",
            SupportCategory.REMOTE_WORK: "العمل عن بعد",
            SupportCategory.RESUME_CV: "السيرة الذاتية",
            SupportCategory.COMPANY_INFO: "معلومات الشركات",
            SupportCategory.GENERAL: "عام"
        }
        
        return names.get(category, "عام")
    
    async def job_support_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles job-specific support requests."""
        try:
            user_id = update.effective_user.id
            
            # Get user's recent job applications or searches
            recent_jobs = await self.db_manager.get_user_recent_jobs(user_id, limit=5)
            
            if not recent_jobs:
                await update.message.reply_text(
                    "📋 **دعم الوظائف**\n\n"
                    "لم أجد وظائف حديثة في سجلك. استخدم /search للبحث عن وظائف أولاً، "
                    "ثم يمكنك الحصول على دعم مخصص لكل وظيفة.",
                    parse_mode='Markdown'
                )
                return
            
            # Create keyboard with recent jobs
            keyboard = []
            for job in recent_jobs:
                keyboard.append([InlineKeyboardButton(
                    f"{job.title} - {job.company}",
                    callback_data=f"job_support_{job.id}"
                )])
            
            keyboard.append([InlineKeyboardButton("🆘 دعم عام", callback_data="general_support")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "📋 **دعم الوظائف**\n\n"
                "اختر الوظيفة التي تحتاج دعماً بشأنها:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in job support command: {e}")
            await update.message.reply_text("عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.")
    
    async def handle_support_callbacks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handles various support-related callbacks."""
        try:
            query = update.callback_query
            await query.answer()
            
            if query.data == "show_related_jobs":
                await self._show_related_jobs(query, context)
            
            elif query.data == "show_followup":
                await self._show_follow_up_questions(query, context)
            
            elif query.data == "show_links":
                await self._show_helpful_links(query, context)
            
            elif query.data == "new_support_question":
                await query.edit_message_text("استخدم /support لطرح سؤال جديد.")
            
            elif query.data.startswith("job_support_"):
                job_id = int(query.data.replace("job_support_", ""))
                await self._show_job_specific_support(query, job_id)
            
            elif query.data.startswith("search_detail_"):
                index = int(query.data.replace("search_detail_", ""))
                await self._show_search_detail(query, context, index)
            
        except Exception as e:
            logger.error(f"Error handling support callback: {e}")
            await query.edit_message_text("عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.")
    
    async def _show_related_jobs(self, query, context):
        """Shows related jobs."""
        related_jobs = context.user_data.get('related_jobs', [])
        
        if not related_jobs:
            await query.edit_message_text("لا توجد وظائف ذات صلة متاحة حالياً.")
            return
        
        response = "🔍 **وظائف ذات صلة:**\n\n"
        
        for job in related_jobs[:3]:
            response += f"**{job.title}**\n"
            response += f"🏢 {job.company}\n"
            response += f"📍 {job.location or 'غير محدد'}\n"
            response += f"🔗 [التقديم]({job.apply_url})\n\n"
        
        keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data="back_to_support")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            response,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def _show_follow_up_questions(self, query, context):
        """Shows follow-up questions."""
        follow_up_questions = context.user_data.get('follow_up_questions', [])
        
        if not follow_up_questions:
            await query.edit_message_text("لا توجد أسئلة متابعة متاحة.")
            return
        
        keyboard = []
        for question in follow_up_questions:
            keyboard.append([InlineKeyboardButton(
                question,
                callback_data=f"followup_{question[:50]}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 العودة", callback_data="back_to_support")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "❓ **أسئلة أخرى قد تهمك:**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def _show_helpful_links(self, query, context):
        """Shows helpful links."""
        helpful_links = context.user_data.get('helpful_links', [])
        
        if not helpful_links:
            await query.edit_message_text("لا توجد روابط مفيدة متاحة.")
            return
        
        response = "🔗 **روابط مفيدة:**\n\n"
        
        for i, link in enumerate(helpful_links, 1):
            response += f"{i}. {link}\n"
        
        keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data="back_to_support")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            response,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def _show_job_specific_support(self, query, job_id: int):
        """Shows support specific to a job."""
        try:
            # Get job-specific FAQ
            faq = await self.support_system.get_job_specific_faq(job_id)
            
            if not faq:
                await query.edit_message_text("لا توجد معلومات دعم متاحة لهذه الوظيفة.")
                return
            
            response = "📋 **الأسئلة الشائعة لهذه الوظيفة:**\n\n"
            
            for item in faq[:3]:  # Show first 3 FAQ items
                response += f"**س: {item['question']}**\n"
                response += f"ج: {item['answer']}\n\n"
            
            keyboard = [[InlineKeyboardButton("🔙 العودة", callback_data="back_to_support")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                response,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error showing job-specific support: {e}")
            await query.edit_message_text("عذراً، حدث خطأ في جلب معلومات الدعم.")
    
    async def _show_search_detail(self, query, context, index: int):
        """Shows detailed search result."""
        search_results = context.user_data.get('search_results', [])
        
        if index >= len(search_results):
            await query.edit_message_text("النتيجة غير متاحة.")
            return
        
        result = search_results[index]
        
        response = f"📋 **{result['question']}**\n\n"
        response += f"{result['answer']}\n\n"
        response += f"📂 الفئة: {result['category']}\n"
        response += f"🎯 مستوى الثقة: {result['confidence']*100:.0f}%"
        
        keyboard = [[InlineKeyboardButton("🔙 العودة للنتائج", callback_data="back_to_search")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            response,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

