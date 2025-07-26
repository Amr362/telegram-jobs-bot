import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import httpx
from src.database.models import Job, LinkStatus
from src.database.manager import SupabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class LinkCheckResult(Enum):
    """Results of link checking."""
    WORKING = "working"
    BROKEN = "broken"
    TIMEOUT = "timeout"
    REDIRECT = "redirect"
    UNKNOWN = "unknown"

class LinkChecker:
    """Handles checking job application links for validity."""
    
    def __init__(self, db_manager: SupabaseManager):
        self.db_manager = db_manager
        self.timeout = 10  # seconds
        self.max_retries = 2
        self.delay_between_checks = 1  # seconds
        
        # Headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        logger.info("LinkChecker initialized")
    
    async def check_single_link(self, url: str) -> Tuple[LinkCheckResult, Optional[str], Optional[int]]:
        """Checks a single URL and returns the result, final URL, and status code."""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
                headers=self.headers
            ) as client:
                
                for attempt in range(self.max_retries + 1):
                    try:
                        # Use HEAD request first (faster)
                        response = await client.head(url)
                        
                        # If HEAD is not allowed, try GET
                        if response.status_code == 405:  # Method Not Allowed
                            response = await client.get(url)
                        
                        # Check status code
                        if 200 <= response.status_code < 300:
                            final_url = str(response.url) if response.url != url else None
                            result = LinkCheckResult.REDIRECT if final_url else LinkCheckResult.WORKING
                            return result, final_url, response.status_code
                        
                        elif 300 <= response.status_code < 400:
                            # Redirect - should be handled by follow_redirects
                            return LinkCheckResult.REDIRECT, str(response.url), response.status_code
                        
                        elif 400 <= response.status_code < 500:
                            # Client error (404, 403, etc.)
                            return LinkCheckResult.BROKEN, None, response.status_code
                        
                        elif 500 <= response.status_code < 600:
                            # Server error - might be temporary, retry
                            if attempt < self.max_retries:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            return LinkCheckResult.BROKEN, None, response.status_code
                        
                        else:
                            return LinkCheckResult.UNKNOWN, None, response.status_code
                    
                    except httpx.TimeoutException:
                        if attempt < self.max_retries:
                            await asyncio.sleep(1)
                            continue
                        return LinkCheckResult.TIMEOUT, None, None
                    
                    except httpx.RequestError as e:
                        if attempt < self.max_retries:
                            await asyncio.sleep(1)
                            continue
                        logger.warning(f"Request error for {url}: {e}")
                        return LinkCheckResult.BROKEN, None, None
        
        except Exception as e:
            logger.error(f"Unexpected error checking {url}: {e}")
            return LinkCheckResult.UNKNOWN, None, None
    
    async def check_job_link(self, job: Job) -> Dict[str, Any]:
        """Checks a job's application link and returns detailed results."""
        try:
            start_time = time.time()
            
            result, final_url, status_code = await self.check_single_link(job.apply_url)
            
            check_duration = time.time() - start_time
            
            # Convert result to LinkStatus
            if result == LinkCheckResult.WORKING:
                link_status = LinkStatus.WORKING
            elif result in [LinkCheckResult.BROKEN, LinkCheckResult.TIMEOUT]:
                link_status = LinkStatus.BROKEN
            else:
                link_status = LinkStatus.UNKNOWN
            
            # Update job in database
            await self.db_manager.update_job_link_status(job.id, link_status.value)
            
            check_result = {
                'job_id': job.id,
                'job_title': job.title,
                'company': job.company,
                'original_url': job.apply_url,
                'final_url': final_url,
                'status': result.value,
                'status_code': status_code,
                'check_duration': round(check_duration, 2),
                'timestamp': time.time()
            }
            
            logger.info(f"Link check completed for job {job.id}: {result.value}")
            return check_result
        
        except Exception as e:
            logger.error(f"Error checking job link for job {job.id}: {e}")
            return {
                'job_id': job.id,
                'job_title': job.title,
                'company': job.company,
                'original_url': job.apply_url,
                'status': LinkCheckResult.UNKNOWN.value,
                'error': str(e),
                'timestamp': time.time()
            }
    
    async def check_multiple_jobs(self, jobs: List[Job], max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """Checks multiple job links concurrently with rate limiting."""
        try:
            results = []
            
            # Process jobs in batches to avoid overwhelming servers
            for i in range(0, len(jobs), max_concurrent):
                batch = jobs[i:i + max_concurrent]
                
                # Create tasks for concurrent execution
                tasks = [self.check_job_link(job) for job in batch]
                
                # Execute batch
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"Exception in batch processing: {result}")
                    else:
                        results.append(result)
                
                # Add delay between batches
                if i + max_concurrent < len(jobs):
                    await asyncio.sleep(self.delay_between_checks)
            
            logger.info(f"Completed link checking for {len(results)} jobs")
            return results
        
        except Exception as e:
            logger.error(f"Error in check_multiple_jobs: {e}")
            return []
    
    async def check_jobs_needing_verification(self, hours_since_last_check: int = 24) -> List[Dict[str, Any]]:
        """Checks jobs that haven't been verified recently."""
        try:
            # Get jobs that need link checking
            from src.database.queries import JobQueries
            job_queries = JobQueries(self.db_manager)
            
            jobs_to_check = await job_queries.get_jobs_needing_link_check(hours_since_last_check)
            
            if not jobs_to_check:
                logger.info("No jobs need link checking at this time")
                return []
            
            logger.info(f"Found {len(jobs_to_check)} jobs needing link verification")
            
            # Check the links
            results = await self.check_multiple_jobs(jobs_to_check)
            
            # Generate summary
            summary = self._generate_check_summary(results)
            logger.info(f"Link check summary: {summary}")
            
            return results
        
        except Exception as e:
            logger.error(f"Error in check_jobs_needing_verification: {e}")
            return []
    
    async def check_broken_jobs(self) -> List[Dict[str, Any]]:
        """Re-checks jobs that were previously marked as broken."""
        try:
            # Get jobs with broken links
            from src.database.queries import JobQueries
            job_queries = JobQueries(self.db_manager)
            
            broken_jobs = await job_queries.get_jobs_with_broken_links()
            
            if not broken_jobs:
                logger.info("No broken jobs to re-check")
                return []
            
            logger.info(f"Re-checking {len(broken_jobs)} previously broken jobs")
            
            # Check the links
            results = await self.check_multiple_jobs(broken_jobs)
            
            # Count how many are now working
            fixed_count = sum(1 for r in results if r.get('status') == LinkCheckResult.WORKING.value)
            logger.info(f"Found {fixed_count} previously broken jobs that are now working")
            
            return results
        
        except Exception as e:
            logger.error(f"Error in check_broken_jobs: {e}")
            return []
    
    async def check_jobs_by_source(self, source: str) -> List[Dict[str, Any]]:
        """Checks all jobs from a specific source."""
        try:
            # Get jobs from the specified source
            from src.database.queries import JobQueries
            job_queries = JobQueries(self.db_manager)
            
            jobs = await job_queries.get_jobs_by_source(source, limit=50)  # Limit to avoid too many requests
            
            if not jobs:
                logger.info(f"No jobs found for source: {source}")
                return []
            
            logger.info(f"Checking {len(jobs)} jobs from source: {source}")
            
            # Check the links
            results = await self.check_multiple_jobs(jobs)
            
            return results
        
        except Exception as e:
            logger.error(f"Error in check_jobs_by_source: {e}")
            return []
    
    def _generate_check_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates a summary of link check results."""
        if not results:
            return {}
        
        summary = {
            'total_checked': len(results),
            'working': 0,
            'broken': 0,
            'timeout': 0,
            'redirect': 0,
            'unknown': 0,
            'average_duration': 0
        }
        
        total_duration = 0
        
        for result in results:
            status = result.get('status', 'unknown')
            summary[status] = summary.get(status, 0) + 1
            
            duration = result.get('check_duration', 0)
            total_duration += duration
        
        if summary['total_checked'] > 0:
            summary['average_duration'] = round(total_duration / summary['total_checked'], 2)
            summary['success_rate'] = round((summary['working'] / summary['total_checked']) * 100, 1)
        
        return summary
    
    async def get_link_check_stats(self, days: int = 7) -> Dict[str, Any]:
        """Gets statistics about link checking over the specified period."""
        try:
            # This would require storing link check history in the database
            # For now, return basic stats from current job statuses
            
            total_jobs = await self.db_manager.get_total_jobs_count()
            
            # Get jobs by status (this would need to be implemented in the database manager)
            # For now, return placeholder stats
            
            stats = {
                'total_jobs': total_jobs,
                'period_days': days,
                'working_links': 0,  # Would need database query
                'broken_links': 0,   # Would need database query
                'unchecked_links': 0, # Would need database query
                'last_check_run': None  # Would need to track this
            }
            
            return stats
        
        except Exception as e:
            logger.error(f"Error getting link check stats: {e}")
            return {}
    
    async def validate_url_format(self, url: str) -> bool:
        """Validates if a URL has a proper format."""
        try:
            import re
            
            # Basic URL pattern
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            return bool(url_pattern.match(url))
        
        except Exception as e:
            logger.error(f"Error validating URL format: {e}")
            return False

