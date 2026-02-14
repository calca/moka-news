"""
The Grinder - RSS Feed Parser
Extracts data from RSS feeds using feedparser
"""

import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime
from email.utils import parsedate_to_datetime


class Grinder:
    """RSS feed parser and aggregator"""

    def __init__(self, feed_urls: List[str], since: Optional[datetime] = None):
        """
        Initialize the Grinder with a list of RSS feed URLs

        Args:
            feed_urls: List of RSS feed URLs to parse
            since: Optional datetime to filter articles (only include articles published after this time)
        """
        self.feed_urls = feed_urls
        self.since = since

    def grind(self) -> tuple[List[Dict[str, Any]], datetime]:
        """
        Parse all RSS feeds and extract articles

        Returns:
            Tuple of (articles, last_update_time)
            - articles: List of article dictionaries with title, link, summary, and published date
            - last_update_time: Timestamp when feeds were fetched
        """
        articles = []
        last_update = datetime.now()

        for feed_url in self.feed_urls:
            try:
                feed = feedparser.parse(feed_url)

                for entry in feed.entries:
                    # Parse published date if available
                    published_str = entry.get("published", entry.get("updated", ""))
                    published_dt = None
                    
                    if published_str:
                        try:
                            # Try to parse the date using email.utils (handles RFC 2822 format)
                            published_dt = parsedate_to_datetime(published_str)
                        except Exception:
                            try:
                                # Fallback: try feedparser's parsed date
                                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                    import time
                                    published_dt = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                            except Exception:
                                pass
                    
                    # Filter by date if since parameter is provided
                    if self.since and published_dt:
                        if published_dt < self.since:
                            continue  # Skip articles older than the since timestamp
                    
                    article = {
                        "title": entry.get("title", "No Title"),
                        "link": entry.get("link", ""),
                        "summary": entry.get("summary", entry.get("description", "")),
                        "published": published_str,
                        "published_dt": published_dt,
                        "source": feed.feed.get("title", feed_url),
                    }
                    articles.append(article)
            except Exception as e:
                print(f"Error parsing feed {feed_url}: {e}")

        return articles, last_update


def get_default_feeds() -> List[str]:
    """
    Get a list of default RSS feeds

    Returns:
        List of default RSS feed URLs
    """
    return [
        "https://news.ycombinator.com/rss",
        "https://www.reddit.com/r/programming/.rss",
        "https://github.blog/feed/",
    ]
