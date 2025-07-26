import asyncio
from typing import List, Dict, Any, Optional

from src.scrapers.google_jobs import GoogleJobsScraper
from src.scrapers.remote_sites import RemoteOKScraper, RemotiveScraper, AngelListScraper, WeWorkRemotelyScraper
from src.scrapers.arabic_sites import WuzzufScraper, BaytScraper, TanqeebScraper
from src.database.models import Job, LanguagePreference, LocationPreference
from src.database.manager import SupabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class ScrapingManager:
    """Manages all job scraping operations."""

    def __init__(self, db_manager: SupabaseManager):
        self.db_manager = db_manager

        # Initialize all scrapers
        self.scrapers = {
            'google_jobs': GoogleJobsScraper(),
            'remoteok': RemoteOKScraper(),
            'remotive': RemotiveScraper(),
            'angellist': AngelListScraper(),
            'weworkremotely': WeWorkRemotelyScraper(),
            'wuzzuf': WuzzufScraper(),
            'bayt': BaytScraper(),
            'tanqeeb': TanqeebScraper(),
        }

        # Define scraper groups
        self.remote_scrapers = ['remoteok', 'remotive', 'angellist', 'weworkremotely']
        self.arabic_scrapers = ['wuzzuf', 'bayt', 'tanqeeb']
        self.global_scrapers = ['google_jobs', 'angellist']

        logger.info("ScrapingManager initialized with all scrapers")

    async def scrape_jobs_for_user_preferences(self,
                                             language_pref: LanguagePreference,
                                             location_pref: LocationPreference,
                                             skills: List[str],
                                             preferred_country: Optional[str] = None) -> List[Job]:
        """Scrapes jobs based on user preferences."""
        try:
            all_jobs = []

            # Determine which scrapers to use based on preferences
            scrapers_to_use = self._get_scrapers_for_preferences(language_pref, location_pref)

            # Generate search queries from skills
            search_queries = self._generate_search_queries(skills)

            # Scrape from each selected scraper
            for scraper_name in scrapers_to_use:
                for query in search_queries:
                    try:
                        scraper = self.scrapers[scraper_name]

                        # Determine location and remote settings
                        location = preferred_country if location_pref == LocationPreference.SPECIFIC else None
                        is_remote = location_pref in [LocationPreference.REMOTE, LocationPreference.BOTH]

                        # Scrape jobs
                        scraped_jobs = await scraper.scrape(query, location=location, is_remote=is_remote)
                        all_jobs.extend(scraped_jobs)

                        # Save jobs to the database
                        for job in scraped_jobs:
                            await self.db_manager.job_queries.create_job(job)

                    except Exception as e:
                        logger.error(f"Error scraping with {scraper_name} for query '{query}': {e}")

            return all_jobs

        except Exception as e:
            logger.error(f"Error in scrape_jobs_for_user_preferences: {e}")
            return []

    def _get_scrapers_for_preferences(self, language_pref: LanguagePreference, location_pref: LocationPreference) -> List[str]:
        """Determines which scrapers to use based on user preferences."""
        scrapers_to_use = []

        if language_pref == LanguagePreference.ARABIC:
            scrapers_to_use.extend(self.arabic_scrapers)
        elif language_pref == LanguagePreference.GLOBAL:
            scrapers_to_use.extend(self.global_scrapers)
        elif language_pref == LanguagePreference.BOTH:
            scrapers_to_use.extend(self.arabic_scrapers)
            scrapers_to_use.extend(self.global_scrapers)

        if location_pref == LocationPreference.REMOTE:
            scrapers_to_use.extend(self.remote_scrapers)
        elif location_pref == LocationPreference.BOTH:
            scrapers_to_use.extend(self.remote_scrapers)

        return list(set(scrapers_to_use))  # Remove duplicates

    def _generate_search_queries(self, skills: List[str]) -> List[str]:
        """Generates search queries from a list of skills."""
        # Simple implementation: use each skill as a separate query
        return skills

    async def run_all_scrapers(self):
        """Runs all scrapers to fetch and store jobs."""
        tasks = []
        for scraper_name, scraper in self.scrapers.items():
            tasks.append(self._run_scraper(scraper_name, scraper))
        
        await asyncio.gather(*tasks)

    async def _run_scraper(self, scraper_name: str, scraper):
        """Helper function to run a single scraper and handle its results."""
        try:
            # Define a default query for each scraper if needed
            default_query = "software engineer"
            jobs = await scraper.scrape(default_query)
            for job in jobs:
                await self.db_manager.job_queries.create_job(job)
            logger.info(f"Successfully ran scraper: {scraper_name}")
        except Exception as e:
            logger.error(f"Error running scraper {scraper_name}: {e}")


