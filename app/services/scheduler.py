import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore

from app.config import settings
from app.services.news_service import NewsService

logger = logging.getLogger(__name__)

# Create global scheduler instance
scheduler = AsyncIOScheduler(
    jobstores={"default": MemoryJobStore()},
)


async def fetch_news_job():
    """Job to fetch news periodically"""
    logger.info("Running scheduled news fetch job")
    news_service = NewsService()
    try:
        await news_service.fetch_news()
        logger.info("Scheduled news fetch completed successfully")
    except Exception as e:
        logger.error(f"Error in scheduled news fetch: {e}")


def start_scheduler():
    """Start the scheduler with configured jobs"""
    if not scheduler.running:
        # Add the news fetching job
        scheduler.add_job(
            fetch_news_job,
            trigger=IntervalTrigger(
                minutes=settings.NEWS_FETCH_INTERVAL_MINUTES,
            ),
            id="fetch_news_job",
            replace_existing=True,
        )
        
        # Also run once at startup
        scheduler.add_job(
            fetch_news_job,
            trigger="date",
            id="initial_fetch_news_job",
            replace_existing=True,
        )
        
        scheduler.start()
        logger.info(
            f"Scheduler started. News fetching every {settings.NEWS_FETCH_INTERVAL_MINUTES} minutes"
        )


def shutdown_scheduler():
    """Shutdown the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shutdown")
