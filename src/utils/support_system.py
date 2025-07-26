import asyncio
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from src.database.models import Job, User, UserPreferences
from src.database.manager import SupabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SupportCategory(Enum):
    """Categories of support requests."""
    JOB_APPLICATION = "job_application"
    TECHNICAL_SKILLS = "technical_skills"
    INTERVIEW_PREP = "interview_prep"
    SALARY_NEGOTIATION = "salary_negotiation"
    CAREER_ADVICE = "career_advice"
    REMOTE_WORK = "remote_work"
    RESUME_CV = "resume_cv"
    COMPANY_INFO = "company_info"
    GENERAL = "general"

class SupportLanguage(Enum):
    """Support languages."""
    ARABIC = "ar"
    ENGLISH = "en"

@dataclass
class SupportRequest:
    """Represents a support request."""
    user_id: int
    category: SupportCategory
    question: str
    job_id: Optional[int] = None
    keywords: List[str] = None
    language: SupportLanguage = SupportLanguage.ARABIC
    context: Dict[str, Any] = None

@dataclass
class SupportResponse:
    """Represents a support response."""
    answer: str
    related_jobs: List[Job] = None
    helpful_links: List[str] = None
    follow_up_questions: List[str] = None
    confidence_score: float = 0.0

class JobSupportSystem:
    """Comprehensive support system for job-related queries."""
    
    def __init__(self, db_manager: SupabaseManager):
        self.db_manager = db_manager
        self.knowledge_base = self._initialize_knowledge_base()
        self.job_specific_advice = self._initialize_job_advice()
        self.skill_keywords = self._initialize_skill_keywords()
        
        logger.info("JobSupportSystem initialized")
    
    def _initialize_knowledge_base(self) -> Dict[str, Dict[str, Any]]:
        """Initializes the knowledge base with common questions and answers."""
        return {
            "job_application": {
                "ar": {
                    "كيف أتقدم للوظيفة؟": {
                        "answer": "لتقديم طلب وظيفة ناجح:\n1. اقرأ متطلبات الوظيفة بعناية\n2. تأكد من مطابقة مهاراتك للمطلوب\n3. اكتب رسالة تغطية مخصصة\n4. راجع سيرتك الذاتية\n5. تقدم عبر الرابط الرسمي",
                        "keywords": ["تقديم", "طلب", "وظيفة", "تطبيق"],
                        "confidence": 0.9
                    },
                    "ما هي أفضل طريقة لكتابة السيرة الذاتية؟": {
                        "answer": "نصائح لسيرة ذاتية مميزة:\n1. ابدأ بمعلومات الاتصال الواضحة\n2. اكتب ملخص مهني قصير\n3. رتب الخبرات من الأحدث للأقدم\n4. اذكر الإنجازات بأرقام محددة\n5. تأكد من عدم وجود أخطاء إملائية",
                        "keywords": ["سيرة", "ذاتية", "cv", "resume"],
                        "confidence": 0.9
                    }
                },
                "en": {
                    "how to apply for jobs?": {
                        "answer": "To apply for jobs successfully:\n1. Read job requirements carefully\n2. Match your skills to requirements\n3. Write a customized cover letter\n4. Update your resume\n5. Apply through official channels",
                        "keywords": ["apply", "application", "job", "submit"],
                        "confidence": 0.9
                    }
                }
            },
            "technical_skills": {
                "ar": {
                    "كيف أطور مهاراتي التقنية؟": {
                        "answer": "لتطوير المهارات التقنية:\n1. حدد المهارات المطلوبة في مجالك\n2. ابدأ بدورات أونلاين مجانية\n3. مارس على مشاريع حقيقية\n4. انضم لمجتمعات المطورين\n5. احصل على شهادات معتمدة",
                        "keywords": ["مهارات", "تقنية", "تطوير", "برمجة"],
                        "confidence": 0.8
                    },
                    "ما هي أهم لغات البرمجة؟": {
                        "answer": "أهم لغات البرمجة حالياً:\n1. Python - للذكاء الاصطناعي وتحليل البيانات\n2. JavaScript - لتطوير الويب\n3. Java - للتطبيقات المؤسسية\n4. React - لواجهات المستخدم\n5. SQL - لقواعد البيانات",
                        "keywords": ["لغات", "برمجة", "python", "javascript"],
                        "confidence": 0.9
                    }
                }
            },
            "interview_prep": {
                "ar": {
                    "كيف أستعد للمقابلة الشخصية؟": {
                        "answer": "للاستعداد للمقابلة:\n1. ابحث عن الشركة ومجال عملها\n2. راجع متطلبات الوظيفة\n3. حضر أمثلة على إنجازاتك\n4. تدرب على الأسئلة الشائعة\n5. حضر أسئلة لطرحها على المقابل",
                        "keywords": ["مقابلة", "استعداد", "interview"],
                        "confidence": 0.9
                    }
                }
            },
            "remote_work": {
                "ar": {
                    "كيف أجد وظائف عن بعد؟": {
                        "answer": "للعثور على وظائف عن بعد:\n1. استخدم مواقع متخصصة في العمل عن بعد\n2. ابحث عن كلمة 'remote' في إعلانات الوظائف\n3. طور مهارات التواصل الرقمي\n4. أنشئ مساحة عمل منزلية مناسبة\n5. تعلم أدوات التعاون عن بعد",
                        "keywords": ["عن بعد", "remote", "منزل", "أونلاين"],
                        "confidence": 0.8
                    }
                }
            }
        }
    
    def _initialize_job_advice(self) -> Dict[str, Dict[str, str]]:
        """Initializes job-specific advice based on job titles and skills."""
        return {
            "developer": {
                "ar": "نصائح للمطورين:\n• أنشئ portfolio قوي على GitHub\n• تعلم أحدث التقنيات في مجالك\n• شارك في مشاريع مفتوحة المصدر\n• احضر meetups ومؤتمرات التقنية",
                "en": "Tips for developers:\n• Build a strong GitHub portfolio\n• Learn latest technologies in your field\n• Contribute to open source projects\n• Attend tech meetups and conferences"
            },
            "designer": {
                "ar": "نصائح للمصممين:\n• أنشئ portfolio متنوع\n• تعلم أدوات التصميم الحديثة\n• تابع اتجاهات التصميم الحالية\n• احصل على feedback من مصممين آخرين",
                "en": "Tips for designers:\n• Create a diverse portfolio\n• Learn modern design tools\n• Follow current design trends\n• Get feedback from other designers"
            },
            "manager": {
                "ar": "نصائح للمدراء:\n• طور مهارات القيادة والتواصل\n• تعلم إدارة المشاريع\n• احصل على شهادات في الإدارة\n• مارس التفكير الاستراتيجي",
                "en": "Tips for managers:\n• Develop leadership and communication skills\n• Learn project management\n• Get management certifications\n• Practice strategic thinking"
            },
            "data_scientist": {
                "ar": "نصائح لعلماء البيانات:\n• أتقن Python و R\n• تعلم machine learning\n• اعمل على مشاريع بيانات حقيقية\n• تعلم storytelling بالبيانات",
                "en": "Tips for data scientists:\n• Master Python and R\n• Learn machine learning\n• Work on real data projects\n• Learn data storytelling"
            }
        }
    
    def _initialize_skill_keywords(self) -> Dict[str, List[str]]:
        """Initializes skill-based keywords for better matching."""
        return {
            "programming": ["python", "javascript", "java", "react", "node", "برمجة", "مطور"],
            "design": ["ui", "ux", "figma", "photoshop", "illustrator", "تصميم", "مصمم"],
            "data": ["data", "analytics", "sql", "machine learning", "بيانات", "تحليل"],
            "management": ["project", "team", "leadership", "agile", "scrum", "إدارة", "مدير"],
            "marketing": ["digital", "seo", "social media", "content", "تسويق", "إعلان"],
            "finance": ["accounting", "financial", "budget", "محاسبة", "مالية"],
            "sales": ["sales", "business development", "crm", "مبيعات", "تطوير أعمال"]
        }
    
    async def process_support_request(self, request: SupportRequest) -> SupportResponse:
        """Processes a support request and returns a comprehensive response."""
        try:
            logger.info(f"Processing support request for user {request.user_id}")
            
            # Get user context
            user_context = await self._get_user_context(request.user_id)
            
            # Analyze the question
            analysis = self._analyze_question(request.question, request.language)
            
            # Get job-specific context if job_id provided
            job_context = None
            if request.job_id:
                job_context = await self._get_job_context(request.job_id)
            
            # Generate response
            response = await self._generate_response(request, analysis, user_context, job_context)
            
            # Add related jobs
            response.related_jobs = await self._find_related_jobs(request, user_context)
            
            # Add follow-up questions
            response.follow_up_questions = self._generate_follow_up_questions(request, analysis)
            
            logger.info(f"Support response generated with confidence: {response.confidence_score}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing support request: {e}")
            return SupportResponse(
                answer="عذراً، حدث خطأ في معالجة طلبك. يرجى المحاولة مرة أخرى.",
                confidence_score=0.0
            )
    
    async def _get_user_context(self, user_id: int) -> Dict[str, Any]:
        """Gets user context including preferences and history."""
        try:
            user = await self.db_manager.get_user(user_id)
            preferences = await self.db_manager.get_user_preferences(user_id)
            
            context = {
                "user": user,
                "preferences": preferences,
                "skills": preferences.skills if preferences else [],
                "language_preference": preferences.language_preference if preferences else "both"
            }
            
            return context
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return {}
    
    async def _get_job_context(self, job_id: int) -> Dict[str, Any]:
        """Gets context about a specific job."""
        try:
            job = await self.db_manager.get_job(job_id)
            if not job:
                return {}
            
            context = {
                "job": job,
                "title": job.title,
                "company": job.company,
                "skills_required": job.skills_required,
                "location": job.location,
                "is_remote": job.is_remote,
                "job_type": job.job_type
            }
            
            return context
        except Exception as e:
            logger.error(f"Error getting job context: {e}")
            return {}
    
    def _analyze_question(self, question: str, language: SupportLanguage) -> Dict[str, Any]:
        """Analyzes the question to understand intent and extract keywords."""
        try:
            question_lower = question.lower()
            
            # Extract keywords
            keywords = []
            for skill_category, skill_keywords in self.skill_keywords.items():
                for keyword in skill_keywords:
                    if keyword in question_lower:
                        keywords.append(keyword)
            
            # Determine category
            category = self._determine_category(question_lower, language)
            
            # Extract job-related terms
            job_terms = self._extract_job_terms(question_lower)
            
            analysis = {
                "category": category,
                "keywords": keywords,
                "job_terms": job_terms,
                "language": language,
                "question_type": self._determine_question_type(question_lower)
            }
            
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing question: {e}")
            return {"category": SupportCategory.GENERAL, "keywords": [], "job_terms": []}
    
    def _determine_category(self, question: str, language: SupportLanguage) -> SupportCategory:
        """Determines the category of the support request."""
        category_keywords = {
            SupportCategory.JOB_APPLICATION: ["تقديم", "طلب", "apply", "application", "submit"],
            SupportCategory.TECHNICAL_SKILLS: ["مهارات", "تقنية", "برمجة", "skills", "technical", "programming"],
            SupportCategory.INTERVIEW_PREP: ["مقابلة", "interview", "preparation", "استعداد"],
            SupportCategory.SALARY_NEGOTIATION: ["راتب", "salary", "negotiation", "تفاوض"],
            SupportCategory.CAREER_ADVICE: ["مسار", "career", "advice", "نصيحة"],
            SupportCategory.REMOTE_WORK: ["عن بعد", "remote", "منزل", "home"],
            SupportCategory.RESUME_CV: ["سيرة", "ذاتية", "resume", "cv"],
            SupportCategory.COMPANY_INFO: ["شركة", "company", "معلومات", "info"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in question for keyword in keywords):
                return category
        
        return SupportCategory.GENERAL
    
    def _extract_job_terms(self, question: str) -> List[str]:
        """Extracts job-related terms from the question."""
        job_terms = []
        
        # Common job titles and terms
        job_keywords = [
            "developer", "مطور", "engineer", "مهندس", "designer", "مصمم",
            "manager", "مدير", "analyst", "محلل", "consultant", "استشاري",
            "specialist", "أخصائي", "coordinator", "منسق"
        ]
        
        for term in job_keywords:
            if term in question:
                job_terms.append(term)
        
        return job_terms
    
    def _determine_question_type(self, question: str) -> str:
        """Determines the type of question (how, what, why, etc.)."""
        if any(word in question for word in ["كيف", "how"]):
            return "how"
        elif any(word in question for word in ["ما", "what", "ماذا"]):
            return "what"
        elif any(word in question for word in ["لماذا", "why"]):
            return "why"
        elif any(word in question for word in ["متى", "when"]):
            return "when"
        elif any(word in question for word in ["أين", "where"]):
            return "where"
        else:
            return "general"
    
    async def _generate_response(self, request: SupportRequest, analysis: Dict[str, Any], 
                               user_context: Dict[str, Any], job_context: Dict[str, Any]) -> SupportResponse:
        """Generates a comprehensive response based on all available context."""
        try:
            # Get base answer from knowledge base
            base_answer = self._get_knowledge_base_answer(analysis, request.language)
            
            # Add job-specific advice if applicable
            job_advice = self._get_job_specific_advice(analysis, job_context, request.language)
            
            # Add personalized recommendations
            personal_recommendations = self._get_personal_recommendations(user_context, analysis)
            
            # Combine all parts
            full_answer = self._combine_answer_parts(base_answer, job_advice, personal_recommendations)
            
            # Add helpful links
            helpful_links = self._get_helpful_links(analysis, job_context)
            
            # Calculate confidence score
            confidence = self._calculate_confidence(analysis, base_answer, job_context)
            
            return SupportResponse(
                answer=full_answer,
                helpful_links=helpful_links,
                confidence_score=confidence
            )
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return SupportResponse(
                answer="عذراً، لم أتمكن من إنشاء إجابة مناسبة. يرجى إعادة صياغة سؤالك.",
                confidence_score=0.0
            )
    
    def _get_knowledge_base_answer(self, analysis: Dict[str, Any], language: SupportLanguage) -> str:
        """Gets answer from the knowledge base."""
        category = analysis["category"].value
        lang = language.value
        
        if category in self.knowledge_base and lang in self.knowledge_base[category]:
            category_kb = self.knowledge_base[category][lang]
            
            # Try to find exact match first
            for question, data in category_kb.items():
                if any(keyword in analysis["keywords"] for keyword in data.get("keywords", [])):
                    return data["answer"]
            
            # Return first answer in category if no exact match
            if category_kb:
                return list(category_kb.values())[0]["answer"]
        
        # Default answer
        if language == SupportLanguage.ARABIC:
            return "شكراً لسؤالك. سأحاول مساعدتك بأفضل ما أستطيع."
        else:
            return "Thank you for your question. I'll try to help you as best as I can."
    
    def _get_job_specific_advice(self, analysis: Dict[str, Any], job_context: Dict[str, Any], 
                               language: SupportLanguage) -> str:
        """Gets job-specific advice based on the job context."""
        if not job_context or "job" not in job_context:
            return ""
        
        job = job_context["job"]
        job_title_lower = job.title.lower()
        
        # Determine job type
        job_type = None
        for job_category in self.job_specific_advice.keys():
            if job_category in job_title_lower:
                job_type = job_category
                break
        
        if job_type and job_type in self.job_specific_advice:
            lang = language.value
            if lang in self.job_specific_advice[job_type]:
                advice = self.job_specific_advice[job_type][lang]
                return f"\n\n📋 نصائح خاصة بوظيفة {job.title}:\n{advice}"
        
        return ""
    
    def _get_personal_recommendations(self, user_context: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Gets personalized recommendations based on user context."""
        if not user_context or "preferences" not in user_context:
            return ""
        
        preferences = user_context["preferences"]
        if not preferences or not preferences.skills:
            return ""
        
        # Generate recommendations based on user skills
        user_skills = [skill.lower() for skill in preferences.skills]
        recommendations = []
        
        # Check if user skills match question keywords
        matching_skills = [skill for skill in user_skills if skill in analysis.get("keywords", [])]
        
        if matching_skills:
            recommendations.append(f"بناءً على مهاراتك في {', '.join(matching_skills)}:")
            
            if "programming" in analysis.get("keywords", []):
                recommendations.append("• فكر في التخصص في مجال معين مثل تطوير الويب أو الذكاء الاصطناعي")
                recommendations.append("• ابني مشاريع تطبيقية تظهر مهاراتك")
        
        if recommendations:
            return f"\n\n🎯 توصيات شخصية:\n" + "\n".join(recommendations)
        
        return ""
    
    def _combine_answer_parts(self, base_answer: str, job_advice: str, personal_recommendations: str) -> str:
        """Combines all answer parts into a coherent response."""
        parts = [base_answer]
        
        if job_advice:
            parts.append(job_advice)
        
        if personal_recommendations:
            parts.append(personal_recommendations)
        
        return "\n".join(parts)
    
    def _get_helpful_links(self, analysis: Dict[str, Any], job_context: Dict[str, Any]) -> List[str]:
        """Gets helpful links based on the analysis and context."""
        links = []
        
        category = analysis["category"]
        
        if category == SupportCategory.TECHNICAL_SKILLS:
            links.extend([
                "https://www.coursera.org",
                "https://www.udemy.com",
                "https://www.freecodecamp.org"
            ])
        elif category == SupportCategory.RESUME_CV:
            links.extend([
                "https://www.canva.com/resumes",
                "https://resume.io"
            ])
        elif category == SupportCategory.INTERVIEW_PREP:
            links.extend([
                "https://www.glassdoor.com",
                "https://leetcode.com"
            ])
        
        return links
    
    def _calculate_confidence(self, analysis: Dict[str, Any], base_answer: str, job_context: Dict[str, Any]) -> float:
        """Calculates confidence score for the response."""
        confidence = 0.5  # Base confidence
        
        # Increase confidence if we found keywords
        if analysis.get("keywords"):
            confidence += 0.2
        
        # Increase confidence if we have job context
        if job_context:
            confidence += 0.2
        
        # Increase confidence if we have a good base answer
        if len(base_answer) > 50:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    async def _find_related_jobs(self, request: SupportRequest, user_context: Dict[str, Any]) -> List[Job]:
        """Finds jobs related to the support request."""
        try:
            if not user_context or "preferences" not in user_context:
                return []
            
            preferences = user_context["preferences"]
            if not preferences:
                return []
            
            # Get matched jobs for the user
            matched_jobs = await self.db_manager.get_matched_jobs_for_user(request.user_id, limit=3)
            
            # Convert JobMatch objects to Job objects
            jobs = []
            for match in matched_jobs:
                job = await self.db_manager.get_job(match.job_id)
                if job:
                    jobs.append(job)
            
            return jobs
        except Exception as e:
            logger.error(f"Error finding related jobs: {e}")
            return []
    
    def _generate_follow_up_questions(self, request: SupportRequest, analysis: Dict[str, Any]) -> List[str]:
        """Generates relevant follow-up questions."""
        category = analysis["category"]
        language = request.language
        
        follow_ups = []
        
        if language == SupportLanguage.ARABIC:
            if category == SupportCategory.JOB_APPLICATION:
                follow_ups = [
                    "هل تحتاج مساعدة في كتابة رسالة التغطية؟",
                    "هل تريد نصائح لتحسين سيرتك الذاتية؟",
                    "هل تحتاج معلومات عن الشركة؟"
                ]
            elif category == SupportCategory.TECHNICAL_SKILLS:
                follow_ups = [
                    "ما هي المهارات التي تريد تطويرها؟",
                    "هل تحتاج توصيات لدورات تدريبية؟",
                    "هل تريد معرفة المهارات المطلوبة في مجالك؟"
                ]
            elif category == SupportCategory.INTERVIEW_PREP:
                follow_ups = [
                    "هل تحتاج أسئلة مقابلة شائعة؟",
                    "هل تريد نصائح للمقابلات عن بعد؟",
                    "هل تحتاج مساعدة في التحضير التقني؟"
                ]
        else:
            if category == SupportCategory.JOB_APPLICATION:
                follow_ups = [
                    "Do you need help writing a cover letter?",
                    "Would you like tips to improve your resume?",
                    "Do you need information about the company?"
                ]
        
        return follow_ups[:3]  # Limit to 3 follow-up questions
    
    async def search_support_by_keywords(self, keywords: List[str], language: SupportLanguage = SupportLanguage.ARABIC) -> List[Dict[str, Any]]:
        """Searches support content by keywords."""
        try:
            results = []
            lang = language.value
            
            for category_name, category_data in self.knowledge_base.items():
                if lang in category_data:
                    for question, data in category_data[lang].items():
                        # Check if any keyword matches
                        question_keywords = data.get("keywords", [])
                        if any(keyword.lower() in [k.lower() for k in question_keywords] for keyword in keywords):
                            results.append({
                                "category": category_name,
                                "question": question,
                                "answer": data["answer"],
                                "confidence": data.get("confidence", 0.5)
                            })
            
            # Sort by confidence
            results.sort(key=lambda x: x["confidence"], reverse=True)
            return results[:5]  # Return top 5 results
            
        except Exception as e:
            logger.error(f"Error searching support by keywords: {e}")
            return []
    
    async def get_job_specific_faq(self, job_id: int, language: SupportLanguage = SupportLanguage.ARABIC) -> List[Dict[str, str]]:
        """Gets FAQ specific to a job."""
        try:
            job_context = await self._get_job_context(job_id)
            if not job_context:
                return []
            
            job = job_context["job"]
            faq = []
            
            if language == SupportLanguage.ARABIC:
                faq.extend([
                    {
                        "question": f"ما هي متطلبات وظيفة {job.title}؟",
                        "answer": f"المهارات المطلوبة: {', '.join(job.skills_required) if job.skills_required else 'غير محدد'}\nالموقع: {job.location or 'غير محدد'}\nنوع العمل: {'عن بعد' if job.is_remote else 'في المكتب'}"
                    },
                    {
                        "question": f"كيف أتقدم لوظيفة {job.title} في {job.company}؟",
                        "answer": f"يمكنك التقدم مباشرة عبر الرابط: {job.apply_url}\nتأكد من مراجعة متطلبات الوظيفة وتحضير سيرتك الذاتية."
                    }
                ])
                
                if job.is_remote:
                    faq.append({
                        "question": "ما هي نصائح العمل عن بعد؟",
                        "answer": "نصائح للعمل عن بعد:\n• أنشئ مساحة عمل مخصصة\n• حافظ على روتين يومي\n• استخدم أدوات التواصل بفعالية\n• خذ فترات راحة منتظمة"
                    })
            
            return faq
            
        except Exception as e:
            logger.error(f"Error getting job-specific FAQ: {e}")
            return []

