"""
The Grinder - RSS Feed Parser
Extracts data from RSS feeds using feedparser
"""

import feedparser
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import time
from moka_news.logger import get_logger
from moka_news.constants import DEFAULT_TECH_FEEDS

logger = get_logger(__name__)


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

    def grind(self) -> Tuple[List[Dict[str, Any]], datetime]:
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
                        except (TypeError, ValueError, OverflowError):
                            try:
                                # Fallback: try feedparser's parsed date
                                if (
                                    hasattr(entry, "published_parsed")
                                    and entry.published_parsed
                                ):
                                    published_dt = datetime.fromtimestamp(
                                        time.mktime(entry.published_parsed)
                                    )
                            except (TypeError, ValueError, OverflowError, OSError):
                                pass

                    # Filter by date if since parameter is provided
                    if self.since and published_dt:
                        # Normalize datetime objects for comparison
                        # Convert timezone-aware datetime to naive datetime for comparison
                        if published_dt.tzinfo is not None:
                            # Convert to UTC then remove timezone info
                            published_dt_naive = published_dt.astimezone(
                                timezone.utc
                            ).replace(tzinfo=None)
                        else:
                            published_dt_naive = published_dt

                        # Ensure self.since is also naive (assume it's UTC if it has timezone)
                        if self.since.tzinfo is not None:
                            since_naive = self.since.astimezone(timezone.utc).replace(
                                tzinfo=None
                            )
                        else:
                            since_naive = self.since

                        if published_dt_naive < since_naive:
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
            except (OSError, ValueError, AttributeError) as e:
                logger.error(f"Error parsing feed {feed_url}: {e}", exc_info=True)

        return articles, last_update


def get_default_feeds() -> List[str]:
    """
    Get a list of default RSS feeds

    Returns:
        List of default RSS feed URLs
    """
    return [feed["url"] for feed in DEFAULT_TECH_FEEDS]
