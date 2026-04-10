import time
import schedule
import logging
import os
from trends import get_single_random_trend, mark_topic_posted
from generator import generate_blog_post
from publisher import publish_to_wordpress

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def job():
    """
    The main execution flow:
    1. Gets a trending topic
    2. Writes a blog post about it
    3. Publishes it to WordPress
    """
    logger.info("============== STARTING AUTOBLOG JOB ==============")
    
    # Get multiple topics
    from trends import get_trending_topics
    topics = get_trending_topics(limit=10)
    
    if not topics:
        logger.error("Could not find any trending topics. Aborting job.")
        return
        
    article_data = None
    for topic in topics:
        logger.info(f"Attempting to generate post for topic: {topic}")
        article_data = generate_blog_post(topic)
        if article_data:
            break
        logger.warning(f"Failed to generate article for '{topic}'. Trying the next one...")
        
    if not article_data:
        logger.error("Failed to generate article data for any topic. Aborting job.")
        return
        
    title = article_data.get("title")
    content = article_data.get("content")
    
    if not title or not content:
        logger.error("Missing title or content from generator. Aborting job.")
        return
        
    # 3. Publish
    success, result_or_url = publish_to_wordpress(title, content)
    
    if success:
        logger.info(f"============== JOB SUCCESS ==============")
        logger.info(f"Published to: {result_or_url}")
        mark_topic_posted(topic)
    else:
        logger.error(f"============== JOB FAILED ==============")
        logger.error(f"WordPress Error: {result_or_url}")

def start_scheduler():
    """
    Schedules the job to run 3 times a day.
    """
    # Adjust these times based on your preference and timezone
    schedule.every().day.at("08:00").do(job)
    schedule.every().day.at("14:00").do(job)
    schedule.every().day.at("20:00").do(job)
    
    logger.info("Scheduler started. Will post at 08:00, 14:00, and 20:00 daily.")
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Wait a minute before checking again
        
if __name__ == "__main__":
    logger.info("Autoblog System Initialized.")
    
    if os.environ.get("GITHUB_ACTIONS") == "true":
        logger.info("Running single job for GitHub Actions...")
        job()
    else:
        # Run once immediately upon start to make sure it works
        logger.info("Running initial test job...")
        job()
        
        # Then enter the scheduling loop
        start_scheduler()
