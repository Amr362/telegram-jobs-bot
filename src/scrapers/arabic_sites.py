import asyncio
import json
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from src.scrapers.base import BaseScraper
from src.database.models import Job, JobType
from src.utils.logger import get_logger

logger = get_logger(__name__)

class WuzzufScraper(BaseScraper):
    """Scraper for Wuzzuf.net jobs (Arabic job site)."""
    
    def __init__(self):
        super().__init__("wuzzuf")
        self.base_url = "https://wuzzuf.net"
        self.search_url = "https://wuzzuf.net/search/jobs"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ar,en;q=0.5',
        }
    
    async def scrape_jobs(self, query: str, location: Optional[str] = None, is_remote: bool = False) -> List[Job]:
        """Scrapes jobs from Wuzzuf."""
        try:
            self.logger.info(f"Starting Wuzzuf scraping for query: {query}, location: {location}")
            
            # Build search URL
            params = f"?q={quote_plus(query)}"
            if location:
                params += f"&filters[country][0]={quote_plus(location)}"
            
            search_url = f"{self.search_url}{params}"
            
            # Fetch HTML content
            html_content = await self._fetch_html(search_url, self.headers)
            if not html_content:
                self.logger.error("Failed to fetch HTML content from Wuzzuf")
                return []
            
            # Parse jobs from HTML
            jobs = self._parse_jobs_from_html(html_content)
            self.logger.info(f"Successfully scraped {len(jobs)} jobs from Wuzzuf")
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error scraping Wuzzuf: {e}")
            return []
    
    def _parse_jobs_from_html(self, html_content: str) -> List[Job]:
        """Parses job listings from Wuzzuf HTML."""
        jobs = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for job cards
            job_elements = (soup.find_all('div', class_='css-1gatmva') or 
                          soup.find_all('div', class_='job-card') or
                          soup.find_all('article'))
            
            for job_element in job_elements:
                try:
                    job = self._parse_wuzzuf_job(job_element)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    self.logger.warning(f"Error parsing Wuzzuf job: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error parsing Wuzzuf HTML: {e}")
        
        return jobs[:20]  # Limit to 20 jobs
    
    def _parse_wuzzuf_job(self, job_element) -> Optional[Job]:
        """Parses a single Wuzzuf job element."""
        try:
            # Extract title
            title_elem = (job_element.find('h2') or 
                         job_element.find('h3') or 
                         job_element.find('a', class_='css-o171kl'))
            title = title_elem.get_text().strip() if title_elem else None
            
            if not title:
                return None
            
            # Extract company
            company_elem = (job_element.find('a', class_='css-17s97q8') or 
                           job_element.find('span', class_='company'))
            company = company_elem.get_text().strip() if company_elem else "شركة"
            
            # Extract apply URL
            link_elem = job_element.find('a', href=True)
            apply_url = link_elem['href'] if link_elem else None
            
            if apply_url and not apply_url.startswith('http'):
                apply_url = f"{self.base_url}{apply_url}"
            
            if not apply_url:
                return None
            
            # Extract location
            location_elem = job_element.find('span', class_='css-5wys0k')
            location = location_elem.get_text().strip() if location_elem else None
            
            # Extract description/requirements
            description_elem = job_element.find('div', class_='css-y4udm8')
            description = description_elem.get_text().strip() if description_elem else ""
            
            # Extract job type
            job_type_elem = job_element.find('span', class_='css-1ve4b75')
            job_type_text = job_type_elem.get_text().strip() if job_type_elem else ""
            job_type = self._parse_job_type(job_type_text)
            
            # Check if remote
            is_remote = 'عن بعد' in (location or '') or 'remote' in description.lower()
            
            # Generate job ID
            job_id = self._generate_job_id(title, company)
            
            return Job(
                title=title,
                company=company,
                description=self._clean_text(description),
                location=location,
                job_type=job_type,
                apply_url=apply_url,
                source=self.source_name,
                source_job_id=job_id,
                is_remote=is_remote
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing Wuzzuf job element: {e}")
            return None
    
    def _parse_job_type(self, job_type_text: str) -> Optional[JobType]:
        """Parses job type from Arabic text."""
        if not job_type_text:
            return None
        
        job_type_lower = job_type_text.lower()
        
        if 'دوام كامل' in job_type_lower or 'full time' in job_type_lower:
            return JobType.FULL_TIME
        elif 'دوام جزئي' in job_type_lower or 'part time' in job_type_lower:
            return JobType.PART_TIME
        elif 'عقد' in job_type_lower or 'contract' in job_type_lower:
            return JobType.CONTRACT
        elif 'عن بعد' in job_type_lower or 'remote' in job_type_lower:
            return JobType.REMOTE
        
        return JobType.FULL_TIME  # Default
    
    def _generate_job_id(self, title: str, company: str) -> str:
        """Generates a unique job ID."""
        import hashlib
        content = f"{title}_{company}_{self.source_name}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

class BaytScraper(BaseScraper):
    """Scraper for Bayt.com jobs (Arabic job site)."""
    
    def __init__(self):
        super().__init__("bayt")
        self.base_url = "https://www.bayt.com"
        self.search_url = "https://www.bayt.com/en/jobs"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ar,en;q=0.5',
        }
    
    async def scrape_jobs(self, query: str, location: Optional[str] = None, is_remote: bool = False) -> List[Job]:
        """Scrapes jobs from Bayt."""
        try:
            self.logger.info(f"Starting Bayt scraping for query: {query}, location: {location}")
            
            # Build search URL
            params = f"?q={quote_plus(query)}"
            if location:
                params += f"&location={quote_plus(location)}"
            
            search_url = f"{self.search_url}{params}"
            
            # Fetch HTML content
            html_content = await self._fetch_html(search_url, self.headers)
            if not html_content:
                self.logger.error("Failed to fetch HTML content from Bayt")
                return []
            
            # Parse jobs from HTML
            jobs = self._parse_jobs_from_html(html_content)
            self.logger.info(f"Successfully scraped {len(jobs)} jobs from Bayt")
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error scraping Bayt: {e}")
            return []
    
    def _parse_jobs_from_html(self, html_content: str) -> List[Job]:
        """Parses job listings from Bayt HTML."""
        jobs = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for job cards
            job_elements = (soup.find_all('li', class_='has-pointer-d') or 
                          soup.find_all('div', class_='job-card') or
                          soup.find_all('article'))
            
            for job_element in job_elements:
                try:
                    job = self._parse_bayt_job(job_element)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    self.logger.warning(f"Error parsing Bayt job: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error parsing Bayt HTML: {e}")
        
        return jobs[:20]  # Limit to 20 jobs
    
    def _parse_bayt_job(self, job_element) -> Optional[Job]:
        """Parses a single Bayt job element."""
        try:
            # Extract title
            title_elem = (job_element.find('h3') or 
                         job_element.find('h2') or 
                         job_element.find('a', class_='job-title'))
            title = title_elem.get_text().strip() if title_elem else None
            
            if not title:
                return None
            
            # Extract company
            company_elem = (job_element.find('b') or 
                           job_element.find('span', class_='company') or
                           job_element.find('div', class_='company-name'))
            company = company_elem.get_text().strip() if company_elem else "شركة"
            
            # Extract apply URL
            link_elem = job_element.find('a', href=True)
            apply_url = link_elem['href'] if link_elem else None
            
            if apply_url and not apply_url.startswith('http'):
                apply_url = f"{self.base_url}{apply_url}"
            
            if not apply_url:
                return None
            
            # Extract location
            location_elem = job_element.find('span', class_='location')
            location = location_elem.get_text().strip() if location_elem else None
            
            # Extract description
            description_elem = job_element.find('p') or job_element.find('div', class_='description')
            description = description_elem.get_text().strip() if description_elem else ""
            
            # Check if remote
            is_remote = 'عن بعد' in (location or '') or 'remote' in description.lower()
            
            # Generate job ID
            job_id = self._generate_job_id(title, company)
            
            return Job(
                title=title,
                company=company,
                description=self._clean_text(description),
                location=location,
                apply_url=apply_url,
                source=self.source_name,
                source_job_id=job_id,
                is_remote=is_remote,
                job_type=JobType.FULL_TIME  # Default for Bayt
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing Bayt job element: {e}")
            return None
    
    def _generate_job_id(self, title: str, company: str) -> str:
        """Generates a unique job ID."""
        import hashlib
        content = f"{title}_{company}_{self.source_name}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

class TanqeebScraper(BaseScraper):
    """Scraper for Tanqeeb.com jobs (Arabic job site)."""
    
    def __init__(self):
        super().__init__("tanqeeb")
        self.base_url = "https://www.tanqeeb.com"
        self.search_url = "https://www.tanqeeb.com/jobs"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ar,en;q=0.5',
        }
    
    async def scrape_jobs(self, query: str, location: Optional[str] = None, is_remote: bool = False) -> List[Job]:
        """Scrapes jobs from Tanqeeb."""
        try:
            self.logger.info(f"Starting Tanqeeb scraping for query: {query}, location: {location}")
            
            # Build search URL
            params = f"?q={quote_plus(query)}"
            if location:
                params += f"&location={quote_plus(location)}"
            
            search_url = f"{self.search_url}{params}"
            
            # Fetch HTML content
            html_content = await self._fetch_html(search_url, self.headers)
            if not html_content:
                self.logger.error("Failed to fetch HTML content from Tanqeeb")
                return []
            
            # Parse jobs from HTML
            jobs = self._parse_jobs_from_html(html_content)
            self.logger.info(f"Successfully scraped {len(jobs)} jobs from Tanqeeb")
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error scraping Tanqeeb: {e}")
            return []
    
    def _parse_jobs_from_html(self, html_content: str) -> List[Job]:
        """Parses job listings from Tanqeeb HTML."""
        jobs = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for job cards
            job_elements = (soup.find_all('div', class_='job-item') or 
                          soup.find_all('div', class_='job-card') or
                          soup.find_all('article'))
            
            for job_element in job_elements:
                try:
                    job = self._parse_tanqeeb_job(job_element)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    self.logger.warning(f"Error parsing Tanqeeb job: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error parsing Tanqeeb HTML: {e}")
        
        return jobs[:20]  # Limit to 20 jobs
    
    def _parse_tanqeeb_job(self, job_element) -> Optional[Job]:
        """Parses a single Tanqeeb job element."""
        try:
            # Extract title
            title_elem = (job_element.find('h3') or 
                         job_element.find('h2') or 
                         job_element.find('a', class_='job-title'))
            title = title_elem.get_text().strip() if title_elem else None
            
            if not title:
                return None
            
            # Extract company
            company_elem = (job_element.find('span', class_='company') or 
                           job_element.find('div', class_='company'))
            company = company_elem.get_text().strip() if company_elem else "شركة"
            
            # Extract apply URL
            link_elem = job_element.find('a', href=True)
            apply_url = link_elem['href'] if link_elem else None
            
            if apply_url and not apply_url.startswith('http'):
                apply_url = f"{self.base_url}{apply_url}"
            
            if not apply_url:
                return None
            
            # Extract location
            location_elem = job_element.find('span', class_='location')
            location = location_elem.get_text().strip() if location_elem else None
            
            # Extract description
            description_elem = job_element.find('p') or job_element.find('div', class_='description')
            description = description_elem.get_text().strip() if description_elem else ""
            
            # Check if remote
            is_remote = 'عن بعد' in (location or '') or 'remote' in description.lower()
            
            # Generate job ID
            job_id = self._generate_job_id(title, company)
            
            return Job(
                title=title,
                company=company,
                description=self._clean_text(description),
                location=location,
                apply_url=apply_url,
                source=self.source_name,
                source_job_id=job_id,
                is_remote=is_remote,
                job_type=JobType.FULL_TIME  # Default
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing Tanqeeb job element: {e}")
            return None
    
    def _generate_job_id(self, title: str, company: str) -> str:
        """Generates a unique job ID."""
        import hashlib
        content = f"{title}_{company}_{self.source_name}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

