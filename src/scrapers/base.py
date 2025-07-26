from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from src.database.models import Job
from src.utils.logger import get_logger

logger = get_logger(__name__)

class BaseScraper(ABC):
    """Abstract base class for all job scrapers."""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.logger = get_logger(f"scraper.{source_name}")
    
    @abstractmethod
    async def scrape_jobs(self, query: str, location: Optional[str] = None, is_remote: bool = False) -> List[Job]:
        """Abstract method to scrape jobs from a specific source.

        Args:
            query (str): The search query (e.g., job title, keywords).
            location (Optional[str]): The geographical location for the job search.
            is_remote (bool): True if searching for remote jobs, False otherwise.

        Returns:
            List[Job]: A list of scraped Job objects.
        """
        pass
    
    async def _fetch_html(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Fetches HTML content from a given URL."""
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10)
                response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
                return response.text
        except httpx.RequestError as exc:
            self.logger.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
        except httpx.HTTPStatusError as exc:
            self.logger.error(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while fetching {url}: {e}")
        return None

    def _parse_job_data(self, data: Dict[str, Any]) -> Job:
        """Parses raw job data into a Job object. Can be overridden by subclasses."""
        return Job(
            title=data.get("title", "N/A"),
            company=data.get("company"),
            location=data.get("location"),
            apply_url=data.get("apply_url", "N/A"),
            description=data.get("description"),
            source=self.source_name,
            source_job_id=data.get("source_job_id"),
            is_remote=data.get("is_remote", False),
            job_type=data.get("job_type"),
            skills_required=data.get("skills_required", [])
        )

    def _clean_text(self, text: str) -> str:
        """Cleans and normalizes text content."""
        import re
        text = re.sub(r'\s+', ' ', text).strip()
        return text


