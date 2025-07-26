import asyncio
import json
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from src.scrapers.base import BaseScraper
from src.database.models import Job, JobType
from src.utils.logger import get_logger

logger = get_logger(__name__)

class RemoteOKScraper(BaseScraper):
    """Scraper for RemoteOK.io jobs."""
    
    def __init__(self):
        super().__init__("remoteok")
        self.base_url = "https://remoteok.io"
        self.api_url = "https://remoteok.io/api"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
        }
    
    async def scrape_jobs(self, query: str, location: Optional[str] = None, is_remote: bool = True) -> List[Job]:
        """Scrapes jobs from RemoteOK."""
        try:
            self.logger.info(f"Starting RemoteOK scraping for query: {query}")
            
            # RemoteOK API endpoint
            api_url = f"{self.api_url}"
            
            # Fetch JSON data
            html_content = await self._fetch_html(api_url, self.headers)
            if not html_content:
                self.logger.error("Failed to fetch data from RemoteOK API")
                return []
            
            # Parse JSON response
            try:
                jobs_data = json.loads(html_content)
                if not isinstance(jobs_data, list):
                    self.logger.error("Invalid JSON response from RemoteOK")
                    return []
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON from RemoteOK: {e}")
                return []
            
            # Filter and parse jobs
            jobs = self._parse_jobs_from_api(jobs_data, query)
            self.logger.info(f"Successfully scraped {len(jobs)} jobs from RemoteOK")
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error scraping RemoteOK: {e}")
            return []
    
    def _parse_jobs_from_api(self, jobs_data: List[Dict], query: str) -> List[Job]:
        """Parses jobs from RemoteOK API response."""
        jobs = []
        query_lower = query.lower()
        
        for job_data in jobs_data:
            try:
                # Skip if not a job posting
                if not isinstance(job_data, dict) or 'position' not in job_data:
                    continue
                
                # Filter by query
                title = job_data.get('position', '').lower()
                description = job_data.get('description', '').lower()
                tags = ' '.join(job_data.get('tags', [])).lower()
                
                if query_lower not in title and query_lower not in description and query_lower not in tags:
                    continue
                
                # Parse job data
                job = self._parse_remoteok_job(job_data)
                if job:
                    jobs.append(job)
                    
            except Exception as e:
                self.logger.warning(f"Error parsing RemoteOK job: {e}")
                continue
        
        return jobs[:20]  # Limit to 20 jobs
    
    def _parse_remoteok_job(self, job_data: Dict) -> Optional[Job]:
        """Parses a single RemoteOK job."""
        try:
            title = job_data.get('position')
            company = job_data.get('company')
            description = job_data.get('description', '')
            
            if not title or not company:
                return None
            
            # Build apply URL
            job_id = job_data.get('id')
            apply_url = f"{self.base_url}/job/{job_id}" if job_id else self.base_url
            
            # Extract skills from tags
            skills = [tag.title() for tag in job_data.get('tags', []) if tag]
            
            # Determine job type
            job_type = JobType.REMOTE if job_data.get('remote') else JobType.FULL_TIME
            
            return Job(
                title=title,
                company=company,
                description=self._clean_text(description),
                location="Remote",
                job_type=job_type,
                apply_url=apply_url,
                source=self.source_name,
                source_job_id=str(job_id) if job_id else None,
                skills_required=skills,
                is_remote=True
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing RemoteOK job data: {e}")
            return None

class RemotiveScraper(BaseScraper):
    """Scraper for Remotive.io jobs."""
    
    def __init__(self):
        super().__init__("remotive")
        self.base_url = "https://remotive.io"
        self.search_url = "https://remotive.io/remote-jobs"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
    
    async def scrape_jobs(self, query: str, location: Optional[str] = None, is_remote: bool = True) -> List[Job]:
        """Scrapes jobs from Remotive."""
        try:
            self.logger.info(f"Starting Remotive scraping for query: {query}")
            
            # Build search URL
            search_url = f"{self.search_url}?search={quote_plus(query)}"
            
            # Fetch HTML content
            html_content = await self._fetch_html(search_url, self.headers)
            if not html_content:
                self.logger.error("Failed to fetch HTML content from Remotive")
                return []
            
            # Parse jobs from HTML
            jobs = self._parse_jobs_from_html(html_content)
            self.logger.info(f"Successfully scraped {len(jobs)} jobs from Remotive")
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error scraping Remotive: {e}")
            return []
    
    def _parse_jobs_from_html(self, html_content: str) -> List[Job]:
        """Parses job listings from Remotive HTML."""
        jobs = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for job cards
            job_elements = soup.find_all('div', class_='job-tile') or soup.find_all('article')
            
            for job_element in job_elements:
                try:
                    job = self._parse_remotive_job(job_element)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    self.logger.warning(f"Error parsing Remotive job: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error parsing Remotive HTML: {e}")
        
        return jobs[:20]  # Limit to 20 jobs
    
    def _parse_remotive_job(self, job_element) -> Optional[Job]:
        """Parses a single Remotive job element."""
        try:
            # Extract title
            title_elem = job_element.find('h3') or job_element.find('h2') or job_element.find('a')
            title = title_elem.get_text().strip() if title_elem else None
            
            if not title:
                return None
            
            # Extract company
            company_elem = job_element.find('span', class_='company') or job_element.find('div', class_='company')
            company = company_elem.get_text().strip() if company_elem else "Unknown"
            
            # Extract apply URL
            link_elem = job_element.find('a', href=True)
            apply_url = link_elem['href'] if link_elem else None
            
            if apply_url and not apply_url.startswith('http'):
                apply_url = f"{self.base_url}{apply_url}"
            
            if not apply_url:
                return None
            
            # Extract description
            description_elem = job_element.find('p') or job_element.find('div', class_='description')
            description = description_elem.get_text().strip() if description_elem else ""
            
            # Generate job ID
            job_id = self._generate_job_id(title, company)
            
            return Job(
                title=title,
                company=company,
                description=self._clean_text(description),
                location="Remote",
                apply_url=apply_url,
                source=self.source_name,
                source_job_id=job_id,
                is_remote=True,
                job_type=JobType.REMOTE
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing Remotive job element: {e}")
            return None
    
    def _generate_job_id(self, title: str, company: str) -> str:
        """Generates a unique job ID."""
        import hashlib
        content = f"{title}_{company}_{self.source_name}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

class AngelListScraper(BaseScraper):
    """Scraper for AngelList (Wellfound) jobs."""
    
    def __init__(self):
        super().__init__("angellist")
        self.base_url = "https://wellfound.com"
        self.search_url = "https://wellfound.com/jobs"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
    
    async def scrape_jobs(self, query: str, location: Optional[str] = None, is_remote: bool = False) -> List[Job]:
        """Scrapes jobs from AngelList/Wellfound."""
        try:
            self.logger.info(f"Starting AngelList scraping for query: {query}")
            
            # Build search URL
            params = f"?q={quote_plus(query)}"
            if is_remote:
                params += "&remote=true"
            elif location:
                params += f"&l={quote_plus(location)}"
            
            search_url = f"{self.search_url}{params}"
            
            # Fetch HTML content
            html_content = await self._fetch_html(search_url, self.headers)
            if not html_content:
                self.logger.error("Failed to fetch HTML content from AngelList")
                return []
            
            # Parse jobs from HTML
            jobs = self._parse_jobs_from_html(html_content)
            self.logger.info(f"Successfully scraped {len(jobs)} jobs from AngelList")
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error scraping AngelList: {e}")
            return []
    
    def _parse_jobs_from_html(self, html_content: str) -> List[Job]:
        """Parses job listings from AngelList HTML."""
        jobs = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for job cards (AngelList uses various selectors)
            job_elements = (soup.find_all('div', class_='job') or 
                          soup.find_all('div', attrs={'data-test': 'JobSearchResult'}) or
                          soup.find_all('article'))
            
            for job_element in job_elements:
                try:
                    job = self._parse_angellist_job(job_element)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    self.logger.warning(f"Error parsing AngelList job: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error parsing AngelList HTML: {e}")
        
        return jobs[:20]  # Limit to 20 jobs
    
    def _parse_angellist_job(self, job_element) -> Optional[Job]:
        """Parses a single AngelList job element."""
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
                           job_element.find('div', class_='company') or
                           job_element.find('a', class_='company-name'))
            company = company_elem.get_text().strip() if company_elem else "Startup"
            
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
            description_elem = job_element.find('div', class_='description') or job_element.find('p')
            description = description_elem.get_text().strip() if description_elem else ""
            
            # Check if remote
            is_remote = (location and 'remote' in location.lower()) or ('remote' in description.lower())
            
            # Generate job ID
            job_id = self._generate_job_id(title, company)
            
            return Job(
                title=title,
                company=company,
                description=self._clean_text(description),
                location=location or ("Remote" if is_remote else None),
                apply_url=apply_url,
                source=self.source_name,
                source_job_id=job_id,
                is_remote=is_remote,
                job_type=JobType.FULL_TIME  # AngelList is mostly full-time positions
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing AngelList job element: {e}")
            return None
    
    def _generate_job_id(self, title: str, company: str) -> str:
        """Generates a unique job ID."""
        import hashlib
        content = f"{title}_{company}_{self.source_name}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

class WeWorkRemotelyScraper(BaseScraper):
    """Scraper for WeWorkRemotely jobs."""
    
    def __init__(self):
        super().__init__("weworkremotely")
        self.base_url = "https://weworkremotely.com"
        self.search_url = "https://weworkremotely.com/remote-jobs/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
    
    async def scrape_jobs(self, query: str, location: Optional[str] = None, is_remote: bool = True) -> List[Job]:
        """Scrapes jobs from WeWorkRemotely."""
        try:
            self.logger.info(f"Starting WeWorkRemotely scraping for query: {query}")
            
            # Build search URL
            search_url = f"{self.search_url}?term={quote_plus(query)}"
            
            # Fetch HTML content
            html_content = await self._fetch_html(search_url, self.headers)
            if not html_content:
                self.logger.error("Failed to fetch HTML content from WeWorkRemotely")
                return []
            
            # Parse jobs from HTML
            jobs = self._parse_jobs_from_html(html_content)
            self.logger.info(f"Successfully scraped {len(jobs)} jobs from WeWorkRemotely")
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error scraping WeWorkRemotely: {e}")
            return []
    
    def _parse_jobs_from_html(self, html_content: str) -> List[Job]:
        """Parses job listings from WeWorkRemotely HTML."""
        jobs = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for job listings
            job_elements = soup.find_all('li', class_='feature') or soup.find_all('article')
            
            for job_element in job_elements:
                try:
                    job = self._parse_weworkremotely_job(job_element)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    self.logger.warning(f"Error parsing WeWorkRemotely job: {e}")
                    continue
            
        except Exception as e:
            self.logger.error(f"Error parsing WeWorkRemotely HTML: {e}")
        
        return jobs[:20]  # Limit to 20 jobs
    
    def _parse_weworkremotely_job(self, job_element) -> Optional[Job]:
        """Parses a single WeWorkRemotely job element."""
        try:
            # Extract title and company from the link
            link_elem = job_element.find('a', href=True)
            if not link_elem:
                return None
            
            # Title is usually in a span or the link text
            title_elem = link_elem.find('span', class_='title') or link_elem
            title = title_elem.get_text().strip() if title_elem else None
            
            if not title:
                return None
            
            # Company is usually in a span with company class
            company_elem = link_elem.find('span', class_='company')
            company = company_elem.get_text().strip() if company_elem else "Remote Company"
            
            # Apply URL
            apply_url = link_elem['href']
            if not apply_url.startswith('http'):
                apply_url = f"{self.base_url}{apply_url}"
            
            # Extract category/description
            category_elem = job_element.find('span', class_='category')
            description = category_elem.get_text().strip() if category_elem else ""
            
            # Generate job ID
            job_id = self._generate_job_id(title, company)
            
            return Job(
                title=title,
                company=company,
                description=self._clean_text(description),
                location="Remote",
                apply_url=apply_url,
                source=self.source_name,
                source_job_id=job_id,
                is_remote=True,
                job_type=JobType.REMOTE
            )
            
        except Exception as e:
            self.logger.warning(f"Error parsing WeWorkRemotely job element: {e}")
            return None
    
    def _generate_job_id(self, title: str, company: str) -> str:
        """Generates a unique job ID."""
        import hashlib
        content = f"{title}_{company}_{self.source_name}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

