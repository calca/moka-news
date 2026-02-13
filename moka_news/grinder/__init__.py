"""
The Grinder - RSS Feed Parser
Extracts data from RSS feeds using feedparser
"""

import feedparser
from typing import List, Dict, Any
from datetime import datetime


class Grinder:
    """RSS feed parser and aggregator"""
    
    def __init__(self, feed_urls: List[str]):
        """
        Initialize the Grinder with a list of RSS feed URLs
        
        Args:
            feed_urls: List of RSS feed URLs to parse
        """
        self.feed_urls = feed_urls
    
    def grind(self) -> List[Dict[str, Any]]:
        """
        Parse all RSS feeds and extract articles
        
        Returns:
            List of article dictionaries with title, link, summary, and published date
        """
        articles = []
        
        for feed_url in self.feed_urls:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries:
                    article = {
                        'title': entry.get('title', 'No Title'),
                        'link': entry.get('link', ''),
                        'summary': entry.get('summary', entry.get('description', '')),
                        'published': entry.get('published', entry.get('updated', '')),
                        'source': feed.feed.get('title', feed_url),
                    }
                    articles.append(article)
            except Exception as e:
                print(f"Error parsing feed {feed_url}: {e}")
        
        return articles


def get_default_feeds() -> List[str]:
    """
    Get a list of default RSS feeds
    
    Returns:
        List of default RSS feed URLs
    """
    return [
        'https://news.ycombinator.com/rss',
        'https://www.reddit.com/r/programming/.rss',
        'https://github.blog/feed/',
    ]
