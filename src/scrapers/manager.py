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
            'tanqeeb': TanqeebScraper()
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
                        jobs = await scraper.scrape_jobs(query, location, is_remote)
                        
                        # Filter out duplicates and add to results
                        new_jobs = await self._filter_new_jobs(jobs)
                        all_jobs.extend(new_jobs)
                        
                        logger.info(f"Scraped {len(jobs)} jobs from {scraper_name} for query '{query}'")
                        
                        # Add delay between requests to be respectful
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"Error scraping from {scraper_name} with query '{query}': {e}")
                        continue
            
            # Save all new jobs to database
            if all_jobs:
                saved_count = await self.db_manager.save_jobs_batch(all_jobs)
                logger.info(f"Saved {saved_count} new jobs to database")
            
            return all_jobs
            
        except Exception as e:
            logger.error(f"Error in scrape_jobs_for_user_preferences: {e}")
            return []
    
    async def scrape_jobs_by_query(self, 
                                 query: str, 
                                 sources: Optional[List[str]] = None,
                                 location: Optional[str] = None,
                                 is_remote: bool = False) -> List[Job]:
        """Scrapes jobs by a specific query from specified sources."""
        try:
            all_jobs = []
            
            # Use specified sources or all scrapers
            scrapers_to_use = sources or list(self.scrapers.keys())
            
            # Scrape from each scraper
            for scraper_name in scrapers_to_use:
                if scraper_name not in self.scrapers:
                    logger.warning(f"Unknown scraper: {scraper_name}")
                    continue
                
                try:
                    scraper = self.scrapers[scraper_name]
                    jobs = await scraper.scrape_jobs(query, location, is_remote)
                    
                    # Filter out duplicates
                    new_jobs = await self._filter_new_jobs(jobs)
                    all_jobs.extend(new_jobs)
                    
                    logger.info(f"Scraped {len(jobs)} jobs from {scraper_name}")
                    
                    # Add delay between requests
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error scraping from {scraper_name}: {e}")
                    continue
            
            # Save new jobs to database
            if all_jobs:
                saved_count = await self.db_manager.save_jobs_batch(all_jobs)
                logger.info(f"Saved {saved_count} new jobs to database")
            
            return all_jobs
            
        except Exception as e:
            logger.error(f"Error in scrape_jobs_by_query: {e}")
            return []
    
    async def scrape_daily_jobs(self) -> Dict[str, int]:
        """Performs daily job scraping for all categories."""
        try:
            results = {
                'remote_jobs': 0,
                'arabic_jobs': 0,
                'global_jobs': 0,
                'total_jobs': 0
            }
            
            # Common tech skills for daily scraping
            common_queries = [
                'software developer', 'python developer', 'javascript developer',
                'data scientist', 'machine learning', 'ui ux designer',
                'project manager', 'product manager', 'marketing manager',
                'مطور برمجيات', 'مطور ويب', 'مصمم جرافيك'
            ]
            
            # Scrape remote jobs
            logger.info("Starting daily remote jobs scraping")
            for query in common_queries[:5]:  # Limit queries for daily scraping
                try:
                    jobs = await self.scrape_jobs_by_query(
                        query, 
                        sources=self.remote_scrapers,
                        is_remote=True
                    )
                    results['remote_jobs'] += len(jobs)
                    await asyncio.sleep(3)  # Longer delay for daily scraping
                except Exception as e:
                    logger.error(f"Error in daily remote scraping for '{query}': {e}")
            
            # Scrape Arabic jobs
            logger.info("Starting daily Arabic jobs scraping")
            arabic_queries = ['مطور', 'مهندس', 'مصمم', 'محاسب', 'مدير']
            for query in arabic_queries:
                try:
                    jobs = await self.scrape_jobs_by_query(
                        query,
                        sources=self.arabic_scrapers
                    )
                    results['arabic_jobs'] += len(jobs)
                    await asyncio.sleep(3)
                except Exception as e:
                    logger.error(f"Error in daily Arabic scraping for '{query}': {e}")
            
            # Scrape global jobs
            logger.info("Starting daily global jobs scraping")
            for query in common_queries[:3]:  # Fewer queries for global
                try:
                    jobs = await self.scrape_jobs_by_query(
                        query,
                        sources=self.global_scrapers
                    )
                    results['global_jobs'] += len(jobs)
                    await asyncio.sleep(3)
                except Exception as e:
                    logger.error(f"Error in daily global scraping for '{query}': {e}")
            
            results['total_jobs'] = results['remote_jobs'] + results['arabic_jobs'] + results['global_jobs']
            
            logger.info(f"Daily scraping completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error in scrape_daily_jobs: {e}")
            return {'remote_jobs': 0, 'arabic_jobs': 0, 'global_jobs': 0, 'total_jobs': 0}
    
    def _get_scrapers_for_preferences(self, 
                                    language_pref: LanguagePreference,
                                    location_pref: LocationPreference) -> List[str]:
        """Determines which scrapers to use based on user preferences."""
        scrapers = []
        
        # Add scrapers based on language preference
        if language_pref in [LanguagePreference.ARABIC, LanguagePreference.BOTH]:
            scrapers.extend(self.arabic_scrapers)
        
        if language_pref in [LanguagePreference.GLOBAL, LanguagePreference.BOTH]:
            scrapers.extend(self.global_scrapers)
        
        # Add remote scrapers if user wants remote jobs
        if location_pref in [LocationPreference.REMOTE, LocationPreference.BOTH]:
            scrapers.extend(self.remote_scrapers)
        
        # Remove duplicates and return
        return list(set(scrapers))
    
    def _generate_search_queries(self, skills: List[str]) -> List[str]:
        """Generates search queries from user skills."""
        if not skills:
            return ['developer', 'engineer', 'manager']  # Default queries
        
        # Use skills as queries, but limit to avoid too many requests
        queries = skills[:3]  # Limit to first 3 skills
        
        # Add some generic queries if we have less than 3 skills
        if len(queries) < 3:
            generic_queries = ['developer', 'engineer', 'designer', 'manager', 'analyst']
            for query in generic_queries:
                if query not in queries and len(queries) < 3:
                    queries.append(query)
        
        return queries
    
    async def _filter_new_jobs(self, jobs: List[Job]) -> List[Job]:
        """Filters out jobs that already exist in the database."""
        new_jobs = []
        
        for job in jobs:
            try:
                # Check if job already exists
                exists = await self.db_manager.job_exists(job.source, job.source_job_id)
                if not exists:
                    new_jobs.append(job)
            except Exception as e:
                logger.warning(f"Error checking job existence: {e}")
                # If we can't check, include the job to be safe
                new_jobs.append(job)
        
        return new_jobs
    
    async def get_scraper_status(self) -> Dict[str, Dict[str, Any]]:
        """Gets the status of all scrapers."""
        status = {}
        
        for scraper_name, scraper in self.scrapers.items():
            try:
                # Try a simple test scrape
                test_jobs = await scraper.scrape_jobs("test", is_remote=True)
                status[scraper_name] = {
                    'status': 'working',
                    'test_results': len(test_jobs),
                    'last_tested': 'now'
                }
            except Exception as e:
                status[scraper_name] = {
                    'status': 'error',
                    'error': str(e),
                    'last_tested': 'now'
                }
        
        return status
    
    async def scrape_jobs_for_skills(self, skills: List[str], limit_per_skill: int = 5) -> List[Job]:
        """Scrapes jobs specifically for given skills."""
        try:
            all_jobs = []
            
            for skill in skills[:3]:  # Limit to 3 skills to avoid too many requests
                # Use a mix of scrapers for each skill
                selected_scrapers = ['google_jobs', 'remoteok', 'wuzzuf']
                
                for scraper_name in selected_scrapers:
                    try:
                        scraper = self.scrapers[scraper_name]
                        jobs = await scraper.scrape_jobs(skill, is_remote=True)
                        
                        # Limit jobs per skill per scraper
                        limited_jobs = jobs[:limit_per_skill]
                        new_jobs = await self._filter_new_jobs(limited_jobs)
                        all_jobs.extend(new_jobs)
                        
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"Error scraping {scraper_name} for skill '{skill}': {e}")
                        continue
            
            # Save new jobs
            if all_jobs:
                saved_count = await self.db_manager.save_jobs_batch(all_jobs)
                logger.info(f"Saved {saved_count} jobs for skills: {skills}")
            
            return all_jobs
            
        except Exception as e:
            logger.error(f"Error in scrape_jobs_for_skills: {e}")
            return []

