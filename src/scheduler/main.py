"""Main scheduler for automated tasks"""
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from datetime import datetime

from ..data_collection import WebSearcher, GenericWebScraper
from ..database import get_db_context, ScrapedContent
from ..config import settings


class TradingPlatformScheduler:
    """Scheduler for automated platform tasks"""
    
    def __init__(self):
        """Initialize scheduler"""
        self.scheduler = AsyncIOScheduler()
        self.searcher = WebSearcher()
        self.scraper = GenericWebScraper()
    
    async def search_and_scrape_job(self):
        """Job to search web and scrape new content"""
        try:
            logger.info("Starting scheduled search and scrape job")
            
            # Get search topics
            topics = self.searcher.get_default_trading_topics()[:5]  # Limit to 5 topics
            
            # Search for content
            all_results = await self.searcher.comprehensive_search(
                custom_topics=topics,
                max_results_per_topic=5
            )
            
            logger.info(f"Found {len(all_results)} search results")
            
            # Scrape URLs
            urls_to_scrape = [r["url"] for r in all_results[:10]]  # Limit to 10 URLs
            
            scraped_results = await self.scraper.scrape_multiple(urls_to_scrape)
            
            # Save to database
            with get_db_context() as db:
                for result in scraped_results:
                    # Check if URL already exists
                    existing = db.query(ScrapedContent).filter(
                        ScrapedContent.source_url == result["url"]
                    ).first()
                    
                    if not existing:
                        content = ScrapedContent(
                            source_url=result["url"],
                            source_type=result.get("source_type", "article"),
                            title=result.get("title"),
                            content=result.get("content"),
                            raw_html=result.get("raw_html"),
                            extracted_data=result
                        )
                        db.add(content)
                
                db.commit()
            
            logger.info(f"Scraped and saved {len(scraped_results)} items")
            
        except Exception as e:
            logger.error(f"Error in search and scrape job: {e}")
    
    async def process_scraped_content_job(self):
        """Job to process unprocessed scraped content"""
        try:
            logger.info("Starting scraped content processing job")
            
            with get_db_context() as db:
                unprocessed = db.query(ScrapedContent).filter(
                    ScrapedContent.processed == False
                ).limit(10).all()
                
                logger.info(f"Processing {len(unprocessed)} unprocessed items")
                
                for item in unprocessed:
                    # TODO: Add NLP processing to extract strategy information
                    # TODO: Create strategy if valid trading strategy found
                    
                    item.processed = True
                
                db.commit()
            
        except Exception as e:
            logger.error(f"Error in content processing job: {e}")
    
    async def cleanup_job(self):
        """Job to clean up old data"""
        try:
            logger.info("Starting cleanup job")
            
            # TODO: Add cleanup logic (e.g., remove old scraped content, failed backtests)
            
            logger.info("Cleanup job completed")
            
        except Exception as e:
            logger.error(f"Error in cleanup job: {e}")
    
    def start(self):
        """Start the scheduler"""
        logger.info("Starting Trading Platform Scheduler")
        
        # Add jobs
        self.scheduler.add_job(
            self.search_and_scrape_job,
            trigger=IntervalTrigger(minutes=settings.scrape_interval_minutes),
            id="search_and_scrape",
            name="Search and scrape trading strategies",
            replace_existing=True
        )
        
        self.scheduler.add_job(
            self.process_scraped_content_job,
            trigger=IntervalTrigger(minutes=15),
            id="process_content",
            name="Process scraped content",
            replace_existing=True
        )
        
        self.scheduler.add_job(
            self.cleanup_job,
            trigger=IntervalTrigger(hours=24),
            id="cleanup",
            name="Cleanup old data",
            replace_existing=True
        )
        
        # Start scheduler
        self.scheduler.start()
        logger.info("Scheduler started successfully")
        
        # Print scheduled jobs
        logger.info("Scheduled jobs:")
        for job in self.scheduler.get_jobs():
            logger.info(f"  - {job.name} (Next run: {job.next_run_time})")
    
    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping scheduler")
        self.scheduler.shutdown()


async def main():
    """Main function"""
    scheduler = TradingPlatformScheduler()
    scheduler.start()
    
    logger.info("Scheduler is running. Press Ctrl+C to exit.")
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        scheduler.stop()


if __name__ == "__main__":
    asyncio.run(main())
