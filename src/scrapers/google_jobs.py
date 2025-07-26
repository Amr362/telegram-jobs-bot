import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from src.scrapers.base import BaseScraper
from src.database.models import Job, JobType
from src.utils.logger import get_logger

logger = get_logger(__name__)

class GoogleJobsScraper(BaseScraper):
    """Scraper for Google Jobs search results."""
    
    def __init__(self):
        super().__init__("google_jobs")
        self.base_url = "https://www.google.com/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def scrape_jobs(self, query: str, location: Optional[str] = None, is_remote: bool = False) -> List[Job]:
        """Scrapes jobs from Google Jobs."""
        try:
            self.logger.info(f"Starting Google Jobs scraping for query: {query}, location: {location}, remote: {is_remote}")
            
            # Build search URL
            search_url = self._build_search_url(query, location, is_remote)
            self.logger.debug(f"Search URL: {search_url}")
            
            # Fetch HTML content
            html_content = await self._fetch_html(search_url, self.headers)
            if not html_content:
                self.logger.error("Failed to fetch HTML content from Google Jobs")
                return []
            
            # Parse jobs from HTML
            jobs = self._parse_jobs_from_html(html_content)
            self.logger.info(f"Successfully scraped {len(jobs)} jobs from Google Jobs")
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error scraping Google Jobs: {e}")
            return []
    
    def _build_search_url(self, query: str, location: Optional[str] = None, is_remote: bool = False) -> str:
        """Builds the Google Jobs search URL."""
        # Base query for jobs
        search_query = f"jobs {query}"
        
        # Add location if specified
        if location and not is_remote:
            search_query += f" in {location}"
        elif is_remote:
            search_query += " remote"
        
        # URL encode the query
        encoded_query = quote_plus(search_query)
        
        # Build the full URL
        url = f"{self.base_url}?q={encoded_query}&ibp=htl;jobs"
        
        return url
    
    def _parse_jobs_from_html(self, html_content: str) -> List[Job]:
        """Parses job listings from Google Jobs HTML."""
        jobs = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for job cards in Google Jobs results
            # Google Jobs uses various selectors, we'll try multiple approaches
            job_elements = self._find_job_elements(soup)
            
            for job_element in job_elements:
                try:
                    job_data = self._extract_job_data(job_element)
                    if job_data and job_data.get('title') and job_data.get('apply_url'):
                        job = self._parse_job_data(job_data)
                        jobs.append(job)
                except Exception as e:
                    self.logger.warning(f"Error parsing individual job: {e}")
                    continue
            
            # If no jobs found with primary method, try alternative parsing
            if not jobs:
                jobs = self._parse_jobs_alternative(soup)
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML content: {e}")
        
        return jobs
    
    def _find_job_elements(self, soup: BeautifulSoup) -> List:
        """Finds job elements using various selectors."""
        job_elements = []
        
        # Try different selectors that Google might use
        selectors = [
            'div[data-ved]',  # Common Google result selector
            '.g',  # Standard Google result class
            '[role="listitem"]',  # Accessibility role
            '.job-result',  # Potential job-specific class
            '.result'  # Generic result class
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            if elements:
                # Filter elements that seem to contain job information
                job_elements = [elem for elem in elements if self._is_job_element(elem)]
                if job_elements:
                    break
        
        return job_elements[:20]  # Limit to first 20 results
    
    def _is_job_element(self, element) -> bool:
        """Checks if an element contains job information."""
        text = element.get_text().lower()
        job_indicators = ['apply', 'job', 'position', 'career', 'hiring', 'employment']
        return any(indicator in text for indicator in job_indicators)
    
    def _extract_job_data(self, job_element) -> Optional[Dict[str, Any]]:
        """Extracts job data from a job element."""
        try:
            # Extract title
            title = self._extract_title(job_element)
            if not title:
                return None
            
            # Extract company
            company = self._extract_company(job_element)
            
            # Extract location
            location = self._extract_location(job_element)
            
            # Extract apply URL
            apply_url = self._extract_apply_url(job_element)
            if not apply_url:
                return None
            
            # Extract description
            description = self._extract_description(job_element)
            
            # Generate source job ID
            source_job_id = self._generate_job_id(title, company)
            
            return {
                'title': title,
                'company': company,
                'location': location,
                'apply_url': apply_url,
                'description': description,
                'source_job_id': source_job_id,
                'is_remote': self._is_remote_job(location, description),
                'job_type': self._extract_job_type(description),
                'skills_required': self._extract_skills(description)
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting job data: {e}")
            return None
    
    def _extract_title(self, element) -> Optional[str]:
        """Extracts job title from element."""
        # Try different selectors for title
        title_selectors = ['h3', '.title', '[role="heading"]', 'a']
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title = self._clean_text(title_elem.get_text())
                if title and len(title) > 5:  # Basic validation
                    return title
        
        return None
    
    def _extract_company(self, element) -> Optional[str]:
        """Extracts company name from element."""
        text = element.get_text()
        
        # Look for common company indicators
        company_patterns = [
            r'at\s+([A-Za-z0-9\s&.,]+?)(?:\s*-|\s*\||\s*•|\n)',
            r'by\s+([A-Za-z0-9\s&.,]+?)(?:\s*-|\s*\||\s*•|\n)',
            r'([A-Za-z0-9\s&.,]+?)\s*-\s*\d+\s*days?\s*ago',
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company = self._clean_text(match.group(1))
                if company and len(company) > 2:
                    return company
        
        return None
    
    def _extract_location(self, element) -> Optional[str]:
        """Extracts location from element."""
        text = element.get_text()
        
        # Look for location patterns
        location_patterns = [
            r'([A-Za-z\s,]+(?:Remote|Work from home))',
            r'([A-Za-z\s,]+,\s*[A-Z]{2,3})',  # City, State/Country
            r'([A-Za-z\s,]+,\s*[A-Za-z\s]+)',  # City, Country
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = self._clean_text(match.group(1))
                if location and len(location) > 2:
                    return location
        
        return None
    
    def _extract_apply_url(self, element) -> Optional[str]:
        """Extracts apply URL from element."""
        # Look for links
        links = element.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            if href.startswith('http') and 'google.com' not in href:
                return href
            elif href.startswith('/url?q='):
                # Google redirect URL
                import urllib.parse
                parsed = urllib.parse.parse_qs(href[7:])
                if 'q' in parsed:
                    return parsed['q'][0]
        
        return None
    
    def _extract_description(self, element) -> Optional[str]:
        """Extracts job description from element."""
        # Get all text and clean it
        description = self._clean_text(element.get_text())
        
        # Limit description length
        if len(description) > 500:
            description = description[:500] + "..."
        
        return description if description else None
    
    def _generate_job_id(self, title: str, company: str) -> str:
        """Generates a unique job ID for the source."""
        import hashlib
        content = f"{title}_{company}_{self.source_name}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _is_remote_job(self, location: str, description: str) -> bool:
        """Determines if a job is remote based on location and description."""
        if not location and not description:
            return False
        
        remote_keywords = ['remote', 'work from home', 'telecommute', 'distributed']
        text = f"{location or ''} {description or ''}".lower()
        
        return any(keyword in text for keyword in remote_keywords)
    
    def _extract_job_type(self, description: str) -> Optional[JobType]:
        """Extracts job type from description."""
        if not description:
            return None
        
        description_lower = description.lower()
        
        if 'full-time' in description_lower or 'full time' in description_lower:
            return JobType.FULL_TIME
        elif 'part-time' in description_lower or 'part time' in description_lower:
            return JobType.PART_TIME
        elif 'contract' in description_lower or 'contractor' in description_lower:
            return JobType.CONTRACT
        elif 'freelance' in description_lower:
            return JobType.FREELANCE
        
        return None
    
    def _extract_skills(self, description: str) -> List[str]:
        """Extracts required skills from job description."""
        if not description:
            return []
        
        # Common skills to look for
        common_skills = [
            'python', 'javascript', 'java', 'react', 'node.js', 'sql', 'html', 'css',
            'aws', 'docker', 'kubernetes', 'git', 'linux', 'mongodb', 'postgresql',
            'machine learning', 'data science', 'ui/ux', 'figma', 'photoshop',
            'project management', 'agile', 'scrum', 'marketing', 'seo', 'content writing'
        ]
        
        description_lower = description.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill in description_lower:
                found_skills.append(skill.title())
        
        return found_skills
    
    def _parse_jobs_alternative(self, soup: BeautifulSoup) -> List[Job]:
        """Alternative parsing method if primary method fails."""
        jobs = []
        
        try:
            # Look for any links that might be job-related
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                text = link.get_text().strip()
                
                # Skip Google internal links
                if 'google.com' in href or not href.startswith('http'):
                    continue
                
                # Check if link text looks like a job title
                if len(text) > 10 and any(word in text.lower() for word in ['developer', 'engineer', 'manager', 'analyst', 'designer']):
                    job_data = {
                        'title': text,
                        'company': 'Unknown',
                        'location': None,
                        'apply_url': href,
                        'description': text,
                        'source_job_id': self._generate_job_id(text, 'Unknown'),
                        'is_remote': False,
                        'job_type': None,
                        'skills_required': []
                    }
                    
                    job = self._parse_job_data(job_data)
                    jobs.append(job)
                    
                    if len(jobs) >= 10:  # Limit alternative results
                        break
        
        except Exception as e:
            self.logger.error(f"Error in alternative parsing: {e}")
        
        return jobs

