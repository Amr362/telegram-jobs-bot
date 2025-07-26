import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from src.utils.link_checker import LinkChecker, LinkCheckResult
from src.database.manager import SupabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class LinkMonitor:
    """Monitors and manages link checking operations."""
    
    def __init__(self, db_manager: SupabaseManager):
        self.db_manager = db_manager
        self.link_checker = LinkChecker(db_manager)
        self.monitoring_active = False
        self.check_interval = 3600  # 1 hour in seconds
        self.daily_check_hour = 2   # 2 AM for daily checks
        
        logger.info("LinkMonitor initialized")
    
    async def start_monitoring(self):
        """Starts the link monitoring service."""
        try:
            self.monitoring_active = True
            logger.info("Link monitoring service started")
            
            while self.monitoring_active:
                try:
                    # Perform regular link checks
                    await self._perform_scheduled_checks()
                    
                    # Wait for next check interval
                    await asyncio.sleep(self.check_interval)
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(60)  # Wait 1 minute before retrying
            
            logger.info("Link monitoring service stopped")
        
        except Exception as e:
            logger.error(f"Error starting link monitoring: {e}")
    
    def stop_monitoring(self):
        """Stops the link monitoring service."""
        self.monitoring_active = False
        logger.info("Link monitoring service stop requested")
    
    async def _perform_scheduled_checks(self):
        """Performs scheduled link checks based on time and priority."""
        try:
            current_hour = datetime.now().hour
            
            # Daily comprehensive check at specified hour
            if current_hour == self.daily_check_hour:
                await self._daily_comprehensive_check()
            
            # Hourly priority checks
            else:
                await self._hourly_priority_check()
        
        except Exception as e:
            logger.error(f"Error in scheduled checks: {e}")
    
    async def _daily_comprehensive_check(self):
        """Performs comprehensive daily link checking."""
        try:
            logger.info("Starting daily comprehensive link check")
            
            # Check jobs that haven't been checked in 24 hours
            results = await self.link_checker.check_jobs_needing_verification(hours_since_last_check=24)
            
            # Re-check previously broken jobs
            broken_results = await self.link_checker.check_broken_jobs()
            
            # Combine results
            all_results = results + broken_results
            
            # Generate and log summary
            summary = self._generate_daily_summary(all_results)
            logger.info(f"Daily link check completed: {summary}")
            
            # Update monitoring statistics
            await self._update_monitoring_stats(summary)
            
        except Exception as e:
            logger.error(f"Error in daily comprehensive check: {e}")
    
    async def _hourly_priority_check(self):
        """Performs hourly priority link checking."""
        try:
            logger.info("Starting hourly priority link check")
            
            # Check jobs that haven't been checked in 6 hours (high priority)
            results = await self.link_checker.check_jobs_needing_verification(hours_since_last_check=6)
            
            # Limit to prevent overwhelming servers
            if len(results) > 20:
                results = results[:20]
                logger.info(f"Limited hourly check to 20 jobs")
            
            if results:
                summary = self._generate_hourly_summary(results)
                logger.info(f"Hourly link check completed: {summary}")
            else:
                logger.info("No jobs needed priority link checking")
        
        except Exception as e:
            logger.error(f"Error in hourly priority check: {e}")
    
    async def check_new_jobs(self, job_ids: List[int]) -> List[Dict[str, Any]]:
        """Checks links for newly scraped jobs."""
        try:
            logger.info(f"Checking links for {len(job_ids)} new jobs")
            
            # Get job objects
            jobs = []
            for job_id in job_ids:
                job = await self.db_manager.get_job(job_id)
                if job:
                    jobs.append(job)
            
            if not jobs:
                logger.warning("No valid jobs found for link checking")
                return []
            
            # Check links
            results = await self.link_checker.check_multiple_jobs(jobs, max_concurrent=3)
            
            logger.info(f"Completed link checking for {len(results)} new jobs")
            return results
        
        except Exception as e:
            logger.error(f"Error checking new jobs: {e}")
            return []
    
    async def check_source_health(self, source: str) -> Dict[str, Any]:
        """Checks the health of links from a specific source."""
        try:
            logger.info(f"Checking source health for: {source}")
            
            # Check recent jobs from this source
            results = await self.link_checker.check_jobs_by_source(source)
            
            if not results:
                return {
                    'source': source,
                    'status': 'no_jobs',
                    'message': 'No jobs found for this source'
                }
            
            # Calculate health metrics
            total_jobs = len(results)
            working_jobs = sum(1 for r in results if r.get('status') == LinkCheckResult.WORKING.value)
            broken_jobs = sum(1 for r in results if r.get('status') == LinkCheckResult.BROKEN.value)
            
            health_percentage = (working_jobs / total_jobs) * 100 if total_jobs > 0 else 0
            
            # Determine health status
            if health_percentage >= 80:
                health_status = 'healthy'
            elif health_percentage >= 60:
                health_status = 'warning'
            else:
                health_status = 'unhealthy'
            
            health_report = {
                'source': source,
                'status': health_status,
                'health_percentage': round(health_percentage, 1),
                'total_jobs_checked': total_jobs,
                'working_links': working_jobs,
                'broken_links': broken_jobs,
                'check_timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Source health check completed for {source}: {health_status} ({health_percentage:.1f}%)")
            return health_report
        
        except Exception as e:
            logger.error(f"Error checking source health for {source}: {e}")
            return {
                'source': source,
                'status': 'error',
                'error': str(e)
            }
    
    async def get_monitoring_report(self) -> Dict[str, Any]:
        """Generates a comprehensive monitoring report."""
        try:
            # Get link check statistics
            stats = await self.link_checker.get_link_check_stats(days=7)
            
            # Get source health for all sources
            sources = ['google_jobs', 'remoteok', 'remotive', 'angellist', 'weworkremotely', 'wuzzuf', 'bayt', 'tanqeeb']
            source_health = {}
            
            for source in sources:
                try:
                    health = await self.check_source_health(source)
                    source_health[source] = health
                except Exception as e:
                    logger.error(f"Error getting health for source {source}: {e}")
                    source_health[source] = {'status': 'error', 'error': str(e)}
            
            # Generate overall report
            report = {
                'monitoring_status': 'active' if self.monitoring_active else 'inactive',
                'last_report_time': datetime.now().isoformat(),
                'link_statistics': stats,
                'source_health': source_health,
                'monitoring_config': {
                    'check_interval_hours': self.check_interval / 3600,
                    'daily_check_hour': self.daily_check_hour
                }
            }
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating monitoring report: {e}")
            return {'error': str(e)}
    
    async def emergency_check_all_sources(self) -> Dict[str, Any]:
        """Performs an emergency check of all job sources."""
        try:
            logger.info("Starting emergency check of all sources")
            
            sources = ['google_jobs', 'remoteok', 'remotive', 'angellist', 'weworkremotely', 'wuzzuf', 'bayt', 'tanqeeb']
            results = {}
            
            for source in sources:
                try:
                    # Check a sample of jobs from each source
                    source_results = await self.link_checker.check_jobs_by_source(source)
                    
                    # Limit to 10 jobs per source for emergency check
                    if len(source_results) > 10:
                        source_results = source_results[:10]
                    
                    results[source] = {
                        'checked_jobs': len(source_results),
                        'results': source_results,
                        'summary': self.link_checker._generate_check_summary(source_results)
                    }
                    
                    # Add delay between sources
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error in emergency check for source {source}: {e}")
                    results[source] = {'error': str(e)}
            
            logger.info("Emergency check of all sources completed")
            return {
                'emergency_check_completed': True,
                'timestamp': datetime.now().isoformat(),
                'results': results
            }
        
        except Exception as e:
            logger.error(f"Error in emergency check: {e}")
            return {'error': str(e)}
    
    def _generate_daily_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates a summary for daily checks."""
        if not results:
            return {'total_checked': 0}
        
        summary = self.link_checker._generate_check_summary(results)
        summary['check_type'] = 'daily_comprehensive'
        summary['timestamp'] = datetime.now().isoformat()
        
        return summary
    
    def _generate_hourly_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generates a summary for hourly checks."""
        if not results:
            return {'total_checked': 0}
        
        summary = self.link_checker._generate_check_summary(results)
        summary['check_type'] = 'hourly_priority'
        summary['timestamp'] = datetime.now().isoformat()
        
        return summary
    
    async def _update_monitoring_stats(self, summary: Dict[str, Any]):
        """Updates monitoring statistics in the database."""
        try:
            # This would update daily statistics in the database
            # For now, just log the summary
            logger.info(f"Daily monitoring stats: {summary}")
            
            # In a full implementation, you would save this to a monitoring_stats table
            # await self.db_manager.save_monitoring_stats(summary)
            
        except Exception as e:
            logger.error(f"Error updating monitoring stats: {e}")
    
    async def schedule_source_check(self, source: str, delay_minutes: int = 0):
        """Schedules a check for a specific source."""
        try:
            if delay_minutes > 0:
                logger.info(f"Scheduling check for source {source} in {delay_minutes} minutes")
                await asyncio.sleep(delay_minutes * 60)
            
            logger.info(f"Starting scheduled check for source: {source}")
            results = await self.link_checker.check_jobs_by_source(source)
            
            summary = self.link_checker._generate_check_summary(results)
            logger.info(f"Scheduled check completed for {source}: {summary}")
            
            return summary
        
        except Exception as e:
            logger.error(f"Error in scheduled source check for {source}: {e}")
            return {'error': str(e)}

