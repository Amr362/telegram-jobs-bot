import asyncio
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import httpx
from bs4 import BeautifulSoup
from src.database.models import Job, Opinion, OpinionSource
from src.database.manager import SupabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class OpinionSentiment(Enum):
    """Sentiment classification for opinions."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

@dataclass
class CollectedOpinion:
    """Represents a collected opinion about a job or company."""
    source: OpinionSource
    content: str
    sentiment: OpinionSentiment
    author: Optional[str] = None
    url: Optional[str] = None
    date: Optional[str] = None
    upvotes: Optional[int] = None
    confidence_score: float = 0.0
    keywords: List[str] = None

class OpinionCollector:
    """Collects opinions and reviews about jobs and companies from various sources."""
    
    def __init__(self, db_manager: SupabaseManager):
        self.db_manager = db_manager
        self.timeout = 15
        self.max_opinions_per_source = 5
        
        # Headers to mimic real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Sentiment keywords for basic analysis
        self.positive_keywords = [
            'great', 'excellent', 'amazing', 'good', 'love', 'best', 'awesome', 'fantastic',
            'رائع', 'ممتاز', 'جيد', 'أحب', 'أفضل', 'مذهل'
        ]
        
        self.negative_keywords = [
            'bad', 'terrible', 'awful', 'hate', 'worst', 'horrible', 'disappointing',
            'سيء', 'فظيع', 'أكره', 'أسوأ', 'مخيب'
        ]
        
        logger.info("OpinionCollector initialized")
    
    async def collect_opinions_for_job(self, job: Job) -> List[CollectedOpinion]:
        """Collects opinions for a specific job."""
        try:
            logger.info(f"Collecting opinions for job: {job.title} at {job.company}")
            
            all_opinions = []
            
            # Collect from different sources
            search_queries = self._generate_search_queries(job)
            
            for query in search_queries:
                try:
                    # Collect from Reddit-style search (using Google search with site:reddit.com)
                    reddit_opinions = await self._collect_from_reddit_search(query, job)
                    all_opinions.extend(reddit_opinions)
                    
                    # Add delay between sources
                    await asyncio.sleep(2)
                    
                    # Collect from general web search
                    web_opinions = await self._collect_from_web_search(query, job)
                    all_opinions.extend(web_opinions)
                    
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"Error collecting opinions for query '{query}': {e}")
                    continue
            
            # Remove duplicates and limit results
            unique_opinions = self._remove_duplicate_opinions(all_opinions)
            limited_opinions = unique_opinions[:10]  # Limit to 10 opinions per job
            
            # Save opinions to database
            if limited_opinions:
                await self._save_opinions_to_db(job.id, limited_opinions)
            
            logger.info(f"Collected {len(limited_opinions)} opinions for job {job.id}")
            return limited_opinions
            
        except Exception as e:
            logger.error(f"Error collecting opinions for job {job.id}: {e}")
            return []
    
    async def collect_opinions_for_company(self, company_name: str) -> List[CollectedOpinion]:
        """Collects general opinions about a company."""
        try:
            logger.info(f"Collecting opinions for company: {company_name}")
            
            all_opinions = []
            
            # Generate company-specific search queries
            company_queries = [
                f"{company_name} employee review",
                f"{company_name} work experience",
                f"{company_name} company culture",
                f"working at {company_name}",
                f"{company_name} مراجعة موظف",
                f"العمل في {company_name}"
            ]
            
            for query in company_queries[:3]:  # Limit to 3 queries
                try:
                    # Search for company opinions
                    web_opinions = await self._collect_from_web_search(query, None)
                    all_opinions.extend(web_opinions)
                    
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"Error collecting company opinions for query '{query}': {e}")
                    continue
            
            # Process and limit results
            unique_opinions = self._remove_duplicate_opinions(all_opinions)
            limited_opinions = unique_opinions[:8]  # Limit to 8 opinions per company
            
            logger.info(f"Collected {len(limited_opinions)} opinions for company {company_name}")
            return limited_opinions
            
        except Exception as e:
            logger.error(f"Error collecting opinions for company {company_name}: {e}")
            return []
    
    def _generate_search_queries(self, job: Job) -> List[str]:
        """Generates search queries for opinion collection."""
        queries = []
        
        # Job-specific queries
        queries.extend([
            f"{job.title} {job.company} review",
            f"{job.title} experience {job.company}",
            f"working as {job.title} at {job.company}",
            f"{job.company} {job.title} interview"
        ])
        
        # Arabic queries if applicable
        if any(char in job.title for char in 'أبتثجحخدذرزسشصضطظعغفقكلمنهوي'):
            queries.extend([
                f"{job.title} {job.company} مراجعة",
                f"تجربة العمل {job.company}",
                f"مقابلة عمل {job.company}"
            ])
        
        return queries[:4]  # Limit to 4 queries per job
    
    async def _collect_from_reddit_search(self, query: str, job: Optional[Job]) -> List[CollectedOpinion]:
        """Collects opinions using Google search with site:reddit.com."""
        try:
            # Use Google search to find Reddit discussions
            search_query = f"site:reddit.com {query}"
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                response = await client.get(search_url)
                
                if response.status_code != 200:
                    logger.warning(f"Failed to search Reddit opinions: {response.status_code}")
                    return []
                
                # Parse search results
                soup = BeautifulSoup(response.text, 'html.parser')
                opinions = []
                
                # Find search result links
                search_results = soup.find_all('div', class_='g')
                
                for result in search_results[:3]:  # Limit to first 3 results
                    try:
                        link_elem = result.find('a', href=True)
                        if not link_elem:
                            continue
                        
                        url = link_elem['href']
                        if not url.startswith('http'):
                            continue
                        
                        # Extract snippet text
                        snippet_elem = result.find('span', class_='aCOpRe') or result.find('div', class_='VwiC3b')
                        if not snippet_elem:
                            continue
                        
                        snippet = snippet_elem.get_text().strip()
                        
                        if len(snippet) < 20:  # Skip very short snippets
                            continue
                        
                        # Analyze sentiment
                        sentiment = self._analyze_sentiment(snippet)
                        
                        # Extract keywords
                        keywords = self._extract_keywords(snippet)
                        
                        opinion = CollectedOpinion(
                            source=OpinionSource.REDDIT,
                            content=snippet,
                            sentiment=sentiment,
                            url=url,
                            keywords=keywords,
                            confidence_score=0.6  # Medium confidence for search snippets
                        )
                        
                        opinions.append(opinion)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing Reddit search result: {e}")
                        continue
                
                return opinions
                
        except Exception as e:
            logger.error(f"Error collecting from Reddit search: {e}")
            return []
    
    async def _collect_from_web_search(self, query: str, job: Optional[Job]) -> List[CollectedOpinion]:
        """Collects opinions from general web search."""
        try:
            # Search for reviews and opinions
            search_query = f"{query} review opinion experience"
            search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
            
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                response = await client.get(search_url)
                
                if response.status_code != 200:
                    logger.warning(f"Failed to search web opinions: {response.status_code}")
                    return []
                
                # Parse search results
                soup = BeautifulSoup(response.text, 'html.parser')
                opinions = []
                
                # Find search result snippets
                search_results = soup.find_all('div', class_='g')
                
                for result in search_results[:3]:  # Limit to first 3 results
                    try:
                        # Extract snippet
                        snippet_elem = result.find('span', class_='aCOpRe') or result.find('div', class_='VwiC3b')
                        if not snippet_elem:
                            continue
                        
                        snippet = snippet_elem.get_text().strip()
                        
                        if len(snippet) < 30:  # Skip very short snippets
                            continue
                        
                        # Get URL
                        link_elem = result.find('a', href=True)
                        url = link_elem['href'] if link_elem else None
                        
                        # Determine source based on URL
                        source = self._determine_source_from_url(url)
                        
                        # Analyze sentiment
                        sentiment = self._analyze_sentiment(snippet)
                        
                        # Extract keywords
                        keywords = self._extract_keywords(snippet)
                        
                        opinion = CollectedOpinion(
                            source=source,
                            content=snippet,
                            sentiment=sentiment,
                            url=url,
                            keywords=keywords,
                            confidence_score=0.5  # Lower confidence for general web search
                        )
                        
                        opinions.append(opinion)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing web search result: {e}")
                        continue
                
                return opinions
                
        except Exception as e:
            logger.error(f"Error collecting from web search: {e}")
            return []
    
    def _analyze_sentiment(self, text: str) -> OpinionSentiment:
        """Analyzes sentiment of text using keyword-based approach."""
        try:
            text_lower = text.lower()
            
            positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
            negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
            
            if positive_count > negative_count:
                return OpinionSentiment.POSITIVE
            elif negative_count > positive_count:
                return OpinionSentiment.NEGATIVE
            elif positive_count > 0 and negative_count > 0:
                return OpinionSentiment.MIXED
            else:
                return OpinionSentiment.NEUTRAL
                
        except Exception as e:
            logger.warning(f"Error analyzing sentiment: {e}")
            return OpinionSentiment.NEUTRAL
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extracts relevant keywords from text."""
        try:
            # Simple keyword extraction
            words = re.findall(r'\b\w+\b', text.lower())
            
            # Filter out common words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                'من', 'في', 'على', 'إلى', 'مع', 'هذا', 'هذه', 'ذلك', 'التي', 'الذي'
            }
            
            keywords = [word for word in words if len(word) > 3 and word not in stop_words]
            
            # Return top 5 keywords
            return keywords[:5]
            
        except Exception as e:
            logger.warning(f"Error extracting keywords: {e}")
            return []
    
    def _determine_source_from_url(self, url: str) -> OpinionSource:
        """Determines the source based on URL."""
        if not url:
            return OpinionSource.WEB
        
        url_lower = url.lower()
        
        if 'reddit.com' in url_lower:
            return OpinionSource.REDDIT
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return OpinionSource.TWITTER
        elif 'linkedin.com' in url_lower:
            return OpinionSource.LINKEDIN
        elif 'glassdoor.com' in url_lower:
            return OpinionSource.GLASSDOOR
        elif 'indeed.com' in url_lower:
            return OpinionSource.INDEED
        else:
            return OpinionSource.WEB
    
    def _remove_duplicate_opinions(self, opinions: List[CollectedOpinion]) -> List[CollectedOpinion]:
        """Removes duplicate opinions based on content similarity."""
        unique_opinions = []
        seen_content = set()
        
        for opinion in opinions:
            # Create a simplified version of content for comparison
            simplified_content = re.sub(r'\W+', ' ', opinion.content.lower()).strip()
            
            # Check if we've seen similar content
            is_duplicate = False
            for seen in seen_content:
                if self._calculate_similarity(simplified_content, seen) > 0.8:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_opinions.append(opinion)
                seen_content.add(simplified_content)
        
        return unique_opinions
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculates similarity between two texts."""
        try:
            words1 = set(text1.split())
            words2 = set(text2.split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            
            return len(intersection) / len(union)
            
        except Exception as e:
            logger.warning(f"Error calculating similarity: {e}")
            return 0.0
    
    async def _save_opinions_to_db(self, job_id: int, opinions: List[CollectedOpinion]):
        """Saves collected opinions to the database."""
        try:
            for opinion in opinions:
                opinion_obj = Opinion(
                    job_id=job_id,
                    source=opinion.source,
                    content=opinion.content,
                    sentiment=opinion.sentiment.value,
                    author=opinion.author,
                    source_url=opinion.url,
                    confidence_score=opinion.confidence_score,
                    keywords=opinion.keywords
                )
                
                await self.db_manager.save_opinion(opinion_obj)
            
            logger.info(f"Saved {len(opinions)} opinions for job {job_id}")
            
        except Exception as e:
            logger.error(f"Error saving opinions to database: {e}")
    
    async def get_job_opinions_summary(self, job_id: int) -> Dict[str, Any]:
        """Gets a summary of opinions for a job."""
        try:
            opinions = await self.db_manager.get_job_opinions(job_id)
            
            if not opinions:
                return {
                    'total_opinions': 0,
                    'sentiment_breakdown': {},
                    'top_keywords': [],
                    'sample_opinions': []
                }
            
            # Calculate sentiment breakdown
            sentiment_counts = {}
            all_keywords = []
            
            for opinion in opinions:
                sentiment = opinion.sentiment
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                
                if opinion.keywords:
                    all_keywords.extend(opinion.keywords)
            
            # Get top keywords
            keyword_counts = {}
            for keyword in all_keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Get sample opinions (highest confidence)
            sample_opinions = sorted(opinions, key=lambda x: x.confidence_score, reverse=True)[:3]
            
            summary = {
                'total_opinions': len(opinions),
                'sentiment_breakdown': sentiment_counts,
                'top_keywords': [kw[0] for kw in top_keywords],
                'sample_opinions': [
                    {
                        'content': op.content[:200] + '...' if len(op.content) > 200 else op.content,
                        'sentiment': op.sentiment,
                        'source': op.source.value,
                        'confidence': op.confidence_score
                    }
                    for op in sample_opinions
                ]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting job opinions summary: {e}")
            return {}
    
    async def collect_opinions_batch(self, jobs: List[Job]) -> Dict[int, List[CollectedOpinion]]:
        """Collects opinions for multiple jobs in batch."""
        try:
            results = {}
            
            for job in jobs:
                try:
                    opinions = await self.collect_opinions_for_job(job)
                    results[job.id] = opinions
                    
                    # Add delay between jobs to be respectful
                    await asyncio.sleep(5)
                    
                except Exception as e:
                    logger.error(f"Error collecting opinions for job {job.id}: {e}")
                    results[job.id] = []
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch opinion collection: {e}")
            return {}
    
    def format_opinions_for_display(self, opinions: List[CollectedOpinion]) -> str:
        """Formats opinions for display in bot messages."""
        if not opinions:
            return "لا توجد آراء متاحة حالياً."
        
        formatted = "💬 **آراء وتعليقات:**\n\n"
        
        for i, opinion in enumerate(opinions[:3], 1):  # Show top 3 opinions
            # Add sentiment emoji
            sentiment_emoji = {
                OpinionSentiment.POSITIVE: "😊",
                OpinionSentiment.NEGATIVE: "😞",
                OpinionSentiment.NEUTRAL: "😐",
                OpinionSentiment.MIXED: "🤔"
            }
            
            emoji = sentiment_emoji.get(opinion.sentiment, "💭")
            source_name = opinion.source.value.title()
            
            formatted += f"{emoji} **{source_name}:**\n"
            formatted += f"_{opinion.content[:150]}..._\n\n"
        
        return formatted

