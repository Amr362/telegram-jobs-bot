import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SentimentScore(Enum):
    """Detailed sentiment scoring."""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    SLIGHTLY_POSITIVE = "slightly_positive"
    NEUTRAL = "neutral"
    SLIGHTLY_NEGATIVE = "slightly_negative"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    score: SentimentScore
    confidence: float
    positive_score: float
    negative_score: float
    neutral_score: float
    keywords_found: List[str]
    emotional_indicators: List[str]

class AdvancedSentimentAnalyzer:
    """Advanced sentiment analyzer for job and company reviews."""
    
    def __init__(self):
        self.positive_keywords = self._load_positive_keywords()
        self.negative_keywords = self._load_negative_keywords()
        self.neutral_keywords = self._load_neutral_keywords()
        self.emotional_indicators = self._load_emotional_indicators()
        self.job_specific_terms = self._load_job_specific_terms()
        
        logger.info("AdvancedSentimentAnalyzer initialized")
    
    def _load_positive_keywords(self) -> Dict[str, float]:
        """Loads positive keywords with weights."""
        return {
            # English positive keywords
            'excellent': 0.9, 'amazing': 0.9, 'outstanding': 0.9, 'fantastic': 0.9,
            'great': 0.8, 'wonderful': 0.8, 'awesome': 0.8, 'brilliant': 0.8,
            'good': 0.7, 'nice': 0.6, 'decent': 0.6, 'fine': 0.5,
            'love': 0.8, 'enjoy': 0.7, 'like': 0.6, 'appreciate': 0.7,
            'recommend': 0.7, 'satisfied': 0.7, 'happy': 0.7, 'pleased': 0.7,
            'professional': 0.6, 'supportive': 0.7, 'helpful': 0.7, 'friendly': 0.6,
            'innovative': 0.7, 'creative': 0.6, 'flexible': 0.6, 'collaborative': 0.6,
            'growth': 0.7, 'opportunity': 0.6, 'learning': 0.6, 'development': 0.6,
            
            # Arabic positive keywords
            'ممتاز': 0.9, 'رائع': 0.9, 'مذهل': 0.9, 'عظيم': 0.8,
            'جيد': 0.7, 'لطيف': 0.6, 'جميل': 0.7, 'مفيد': 0.7,
            'أحب': 0.8, 'أستمتع': 0.7, 'أقدر': 0.7, 'راضي': 0.7,
            'أنصح': 0.7, 'سعيد': 0.7, 'مسرور': 0.7, 'مهني': 0.6,
            'داعم': 0.7, 'مساعد': 0.7, 'ودود': 0.6, 'مبدع': 0.6,
            'مرن': 0.6, 'تعاوني': 0.6, 'نمو': 0.7, 'فرصة': 0.6,
            'تعلم': 0.6, 'تطوير': 0.6, 'إبداعي': 0.6, 'متقدم': 0.6
        }
    
    def _load_negative_keywords(self) -> Dict[str, float]:
        """Loads negative keywords with weights."""
        return {
            # English negative keywords
            'terrible': 0.9, 'awful': 0.9, 'horrible': 0.9, 'disgusting': 0.9,
            'bad': 0.8, 'poor': 0.8, 'worst': 0.9, 'hate': 0.8,
            'disappointing': 0.7, 'frustrating': 0.7, 'annoying': 0.6, 'boring': 0.6,
            'stressful': 0.7, 'toxic': 0.9, 'unprofessional': 0.8, 'rude': 0.7,
            'disorganized': 0.7, 'chaotic': 0.7, 'unfair': 0.7, 'biased': 0.7,
            'overworked': 0.7, 'underpaid': 0.8, 'exploitative': 0.9, 'abusive': 0.9,
            'micromanagement': 0.7, 'bureaucratic': 0.6, 'inflexible': 0.6, 'outdated': 0.5,
            'quit': 0.7, 'fired': 0.8, 'layoff': 0.8, 'downsizing': 0.7,
            
            # Arabic negative keywords
            'فظيع': 0.9, 'سيء': 0.8, 'أسوأ': 0.9, 'أكره': 0.8,
            'مخيب': 0.7, 'محبط': 0.7, 'مزعج': 0.6, 'ممل': 0.6,
            'مرهق': 0.7, 'سام': 0.9, 'غير مهني': 0.8, 'وقح': 0.7,
            'فوضوي': 0.7, 'غير عادل': 0.7, 'متحيز': 0.7, 'مستغل': 0.9,
            'مسيء': 0.9, 'استقلت': 0.7, 'طردت': 0.8, 'تسريح': 0.8,
            'ضغط': 0.6, 'إجهاد': 0.7, 'تعب': 0.6, 'صعب': 0.6
        }
    
    def _load_neutral_keywords(self) -> Dict[str, float]:
        """Loads neutral keywords."""
        return {
            'okay': 0.5, 'average': 0.5, 'normal': 0.5, 'standard': 0.5,
            'typical': 0.5, 'regular': 0.5, 'common': 0.5, 'usual': 0.5,
            'عادي': 0.5, 'طبيعي': 0.5, 'متوسط': 0.5, 'مقبول': 0.5,
            'اعتيادي': 0.5, 'منتظم': 0.5, 'شائع': 0.5
        }
    
    def _load_emotional_indicators(self) -> Dict[str, str]:
        """Loads emotional indicators and their sentiment."""
        return {
            # Positive emotions
            'excited': 'positive', 'thrilled': 'positive', 'delighted': 'positive',
            'grateful': 'positive', 'proud': 'positive', 'confident': 'positive',
            'motivated': 'positive', 'inspired': 'positive', 'energized': 'positive',
            'متحمس': 'positive', 'فخور': 'positive', 'واثق': 'positive',
            'محفز': 'positive', 'ملهم': 'positive', 'نشيط': 'positive',
            
            # Negative emotions
            'frustrated': 'negative', 'disappointed': 'negative', 'angry': 'negative',
            'stressed': 'negative', 'overwhelmed': 'negative', 'exhausted': 'negative',
            'worried': 'negative', 'anxious': 'negative', 'depressed': 'negative',
            'محبط': 'negative', 'غاضب': 'negative', 'مرهق': 'negative',
            'قلق': 'negative', 'متوتر': 'negative', 'يائس': 'negative',
            
            # Neutral emotions
            'calm': 'neutral', 'relaxed': 'neutral', 'content': 'neutral',
            'هادئ': 'neutral', 'مرتاح': 'neutral', 'راضي': 'neutral'
        }
    
    def _load_job_specific_terms(self) -> Dict[str, Dict[str, float]]:
        """Loads job-specific terms and their sentiment weights."""
        return {
            'work_environment': {
                'collaborative': 0.7, 'supportive': 0.8, 'inclusive': 0.7,
                'toxic': -0.9, 'hostile': -0.8, 'competitive': -0.3,
                'تعاوني': 0.7, 'داعم': 0.8, 'شامل': 0.7,
                'سام': -0.9, 'عدائي': -0.8, 'تنافسي': -0.3
            },
            'management': {
                'micromanagement': -0.8, 'supportive': 0.8, 'transparent': 0.7,
                'incompetent': -0.8, 'inspiring': 0.8, 'fair': 0.7,
                'إدارة تفصيلية': -0.8, 'داعم': 0.8, 'شفاف': 0.7,
                'غير كفء': -0.8, 'ملهم': 0.8, 'عادل': 0.7
            },
            'compensation': {
                'underpaid': -0.8, 'competitive': 0.7, 'generous': 0.8,
                'fair': 0.6, 'below market': -0.7, 'excellent benefits': 0.8,
                'راتب منخفض': -0.8, 'تنافسي': 0.7, 'سخي': 0.8,
                'عادل': 0.6, 'تحت السوق': -0.7, 'مزايا ممتازة': 0.8
            },
            'work_life_balance': {
                'flexible': 0.7, 'remote friendly': 0.7, 'overworked': -0.8,
                'burnout': -0.9, 'work life balance': 0.8, 'long hours': -0.6,
                'مرن': 0.7, 'عمل عن بعد': 0.7, 'عمل مفرط': -0.8,
                'إرهاق': -0.9, 'توازن العمل': 0.8, 'ساعات طويلة': -0.6
            }
        }
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """Performs comprehensive sentiment analysis."""
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            # Calculate basic sentiment scores
            positive_score = self._calculate_positive_score(cleaned_text)
            negative_score = self._calculate_negative_score(cleaned_text)
            neutral_score = self._calculate_neutral_score(cleaned_text)
            
            # Apply job-specific analysis
            job_sentiment_adjustment = self._analyze_job_specific_terms(cleaned_text)
            
            # Adjust scores based on job-specific terms
            positive_score += max(0, job_sentiment_adjustment)
            negative_score += max(0, -job_sentiment_adjustment)
            
            # Normalize scores
            total_score = positive_score + negative_score + neutral_score
            if total_score > 0:
                positive_score /= total_score
                negative_score /= total_score
                neutral_score /= total_score
            
            # Determine overall sentiment
            sentiment_score = self._determine_sentiment_score(positive_score, negative_score, neutral_score)
            
            # Calculate confidence
            confidence = self._calculate_confidence(positive_score, negative_score, neutral_score, text)
            
            # Find keywords and emotional indicators
            keywords_found = self._find_keywords_in_text(cleaned_text)
            emotional_indicators = self._find_emotional_indicators(cleaned_text)
            
            return SentimentResult(
                score=sentiment_score,
                confidence=confidence,
                positive_score=positive_score,
                negative_score=negative_score,
                neutral_score=neutral_score,
                keywords_found=keywords_found,
                emotional_indicators=emotional_indicators
            )
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return SentimentResult(
                score=SentimentScore.NEUTRAL,
                confidence=0.0,
                positive_score=0.0,
                negative_score=0.0,
                neutral_score=1.0,
                keywords_found=[],
                emotional_indicators=[]
            )
    
    def _clean_text(self, text: str) -> str:
        """Cleans and normalizes text for analysis."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep Arabic and English letters
        text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
        
        return text
    
    def _calculate_positive_score(self, text: str) -> float:
        """Calculates positive sentiment score."""
        score = 0.0
        word_count = 0
        
        for word, weight in self.positive_keywords.items():
            if word in text:
                # Count occurrences
                occurrences = text.count(word)
                score += weight * occurrences
                word_count += occurrences
        
        # Apply diminishing returns for multiple positive words
        if word_count > 0:
            score = score / (1 + 0.1 * word_count)
        
        return score
    
    def _calculate_negative_score(self, text: str) -> float:
        """Calculates negative sentiment score."""
        score = 0.0
        word_count = 0
        
        for word, weight in self.negative_keywords.items():
            if word in text:
                # Count occurrences
                occurrences = text.count(word)
                score += weight * occurrences
                word_count += occurrences
        
        # Apply diminishing returns for multiple negative words
        if word_count > 0:
            score = score / (1 + 0.1 * word_count)
        
        return score
    
    def _calculate_neutral_score(self, text: str) -> float:
        """Calculates neutral sentiment score."""
        score = 0.0
        
        for word, weight in self.neutral_keywords.items():
            if word in text:
                score += weight * text.count(word)
        
        # Base neutral score for texts without strong sentiment
        if score == 0:
            score = 0.3
        
        return score
    
    def _analyze_job_specific_terms(self, text: str) -> float:
        """Analyzes job-specific terms and returns sentiment adjustment."""
        adjustment = 0.0
        
        for category, terms in self.job_specific_terms.items():
            for term, weight in terms.items():
                if term in text:
                    adjustment += weight * text.count(term)
        
        return adjustment
    
    def _determine_sentiment_score(self, positive: float, negative: float, neutral: float) -> SentimentScore:
        """Determines the overall sentiment score."""
        # Calculate net sentiment
        net_sentiment = positive - negative
        
        if net_sentiment >= 0.6:
            return SentimentScore.VERY_POSITIVE
        elif net_sentiment >= 0.3:
            return SentimentScore.POSITIVE
        elif net_sentiment >= 0.1:
            return SentimentScore.SLIGHTLY_POSITIVE
        elif net_sentiment <= -0.6:
            return SentimentScore.VERY_NEGATIVE
        elif net_sentiment <= -0.3:
            return SentimentScore.NEGATIVE
        elif net_sentiment <= -0.1:
            return SentimentScore.SLIGHTLY_NEGATIVE
        else:
            return SentimentScore.NEUTRAL
    
    def _calculate_confidence(self, positive: float, negative: float, neutral: float, original_text: str) -> float:
        """Calculates confidence in the sentiment analysis."""
        # Base confidence on the strength of sentiment
        max_sentiment = max(positive, negative, neutral)
        
        # Higher confidence for stronger sentiment
        confidence = max_sentiment
        
        # Adjust based on text length (longer texts generally more reliable)
        text_length_factor = min(1.0, len(original_text) / 100)
        confidence *= (0.5 + 0.5 * text_length_factor)
        
        # Adjust based on presence of emotional indicators
        emotional_count = len(self._find_emotional_indicators(original_text.lower()))
        emotional_factor = min(1.0, emotional_count / 3)
        confidence *= (0.7 + 0.3 * emotional_factor)
        
        return min(confidence, 1.0)
    
    def _find_keywords_in_text(self, text: str) -> List[str]:
        """Finds sentiment keywords present in the text."""
        found_keywords = []
        
        all_keywords = {**self.positive_keywords, **self.negative_keywords, **self.neutral_keywords}
        
        for keyword in all_keywords:
            if keyword in text:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _find_emotional_indicators(self, text: str) -> List[str]:
        """Finds emotional indicators in the text."""
        found_indicators = []
        
        for indicator in self.emotional_indicators:
            if indicator in text:
                found_indicators.append(indicator)
        
        return found_indicators
    
    def analyze_multiple_texts(self, texts: List[str]) -> Dict[str, Any]:
        """Analyzes sentiment for multiple texts and provides aggregate results."""
        try:
            results = []
            
            for text in texts:
                result = self.analyze_sentiment(text)
                results.append(result)
            
            if not results:
                return {}
            
            # Calculate aggregate statistics
            total_positive = sum(r.positive_score for r in results)
            total_negative = sum(r.negative_score for r in results)
            total_neutral = sum(r.neutral_score for r in results)
            
            avg_confidence = sum(r.confidence for r in results) / len(results)
            
            # Count sentiment categories
            sentiment_counts = {}
            for result in results:
                sentiment = result.score.value
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            # Determine overall sentiment
            if total_positive > total_negative:
                overall_sentiment = "positive"
            elif total_negative > total_positive:
                overall_sentiment = "negative"
            else:
                overall_sentiment = "neutral"
            
            return {
                'total_texts': len(texts),
                'overall_sentiment': overall_sentiment,
                'average_confidence': avg_confidence,
                'sentiment_breakdown': sentiment_counts,
                'aggregate_scores': {
                    'positive': total_positive / len(results),
                    'negative': total_negative / len(results),
                    'neutral': total_neutral / len(results)
                },
                'individual_results': [
                    {
                        'sentiment': r.score.value,
                        'confidence': r.confidence,
                        'keywords': r.keywords_found[:3]  # Top 3 keywords
                    }
                    for r in results
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in multiple text analysis: {e}")
            return {}
    
    def get_sentiment_summary(self, sentiment_result: SentimentResult) -> str:
        """Gets a human-readable summary of sentiment analysis."""
        try:
            sentiment_names = {
                SentimentScore.VERY_POSITIVE: "إيجابي جداً",
                SentimentScore.POSITIVE: "إيجابي",
                SentimentScore.SLIGHTLY_POSITIVE: "إيجابي قليلاً",
                SentimentScore.NEUTRAL: "محايد",
                SentimentScore.SLIGHTLY_NEGATIVE: "سلبي قليلاً",
                SentimentScore.NEGATIVE: "سلبي",
                SentimentScore.VERY_NEGATIVE: "سلبي جداً"
            }
            
            sentiment_name = sentiment_names.get(sentiment_result.score, "غير محدد")
            confidence_percent = int(sentiment_result.confidence * 100)
            
            summary = f"المشاعر: {sentiment_name} (ثقة: {confidence_percent}%)"
            
            if sentiment_result.keywords_found:
                top_keywords = sentiment_result.keywords_found[:3]
                summary += f"\nالكلمات المفتاحية: {', '.join(top_keywords)}"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating sentiment summary: {e}")
            return "تعذر تحليل المشاعر"

