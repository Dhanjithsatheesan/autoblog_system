import feedparser
import random
import logging
import sqlite3
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google News RSS Feed for trending news.
TRENDS_RSS_URL = "https://news.google.com/rss"
DB_FILE = "history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posted_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT UNIQUE NOT NULL,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def is_topic_posted(topic):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM posted_topics WHERE topic = ?', (topic,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_topic_posted(topic):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO posted_topics (topic) VALUES (?)', (topic,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

# Initialize DB
init_db()

def get_trending_topics(limit=5):
    """
    Fetches the latest trending topics from Google Trends via RSS.
    Returns a list of strings representing the topics that have NOT been posted yet.
    """
    logger.info(f"Fetching trending topics from: {TRENDS_RSS_URL}")
    topics = []
    try:
        import requests
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(TRENDS_RSS_URL, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
        
        if not feed.entries:
            logger.warning("No entries found in the RSS feed.")
            return topics

        for entry in feed.entries:
            title = entry.title
            
            # Check DB to prevent duplicates
            if not is_topic_posted(title):
                topics.append(title)
                
            if len(topics) >= limit:
                break
                
        logger.info(f"Found {len(topics)} unposted trending topics: {topics}")
        return topics
        
    except Exception as e:
        logger.error(f"Error fetching trending topics: {e}")
        return []

def get_single_random_trend():
    """
    Fetches trending topics and randomly selects one to write about.
    Helps add variety so it's not always picking the #1 trend.
    """
    topics = get_trending_topics(limit=10)
    if topics:
        chosen = random.choice(topics)
        logger.info(f"Selected trend for blogging: {chosen}")
        return chosen
    return None

if __name__ == "__main__":
    # Test the scraper
    get_trending_topics()
