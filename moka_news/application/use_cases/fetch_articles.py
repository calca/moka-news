"""Use-case for fetching articles from RSS feeds."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from moka_news.grinder import Grinder
from moka_news.infrastructure.storage import DownloadTracker
from moka_news.logger import get_logger

logger = get_logger(__name__)


def fetch_and_brew(
    feed_urls: List[str],
    config: Dict[str, Any],
    ai_provider: str,
    download_tracker: Optional[DownloadTracker] = None,
) -> Tuple[List[Dict[str, Any]], datetime]:
    """Fetch RSS feeds and optionally expand lookback window if too few articles."""
    editorial_config = config.get("editorial", {})
    min_articles = editorial_config.get("min_articles", 5)
    extended_window_days = editorial_config.get("extended_window_days", 3)

    since = None
    if download_tracker:
        since = download_tracker.get_last_download()
        if since:
            logger.info("Filtering articles since %s", since.strftime("%Y-%m-%d %H:%M:%S"))

    logger.info("Grinding %d feeds...", len(feed_urls))

    grinder = Grinder(feed_urls, since=since)
    articles, last_update = grinder.grind()

    logger.info("Ground %d articles", len(articles))

    if articles and len(articles) < min_articles and download_tracker:
        logger.info(
            "Only %d articles found (minimum: %d). Expanding time window to last %d days...",
            len(articles),
            min_articles,
            extended_window_days,
        )

        extended_since = download_tracker.get_last_download(days_back=extended_window_days)
        if extended_since:
            logger.info(
                "Fetching articles since %s",
                extended_since.strftime("%Y-%m-%d %H:%M:%S"),
            )
            grinder_extended = Grinder(feed_urls, since=extended_since)
            articles, last_update = grinder_extended.grind()
            logger.info("Extended fetch: found %d articles", len(articles))

    if not articles:
        logger.warning("No articles found. Please check your RSS feeds.")
        return [], last_update

    if download_tracker:
        download_tracker.update_last_download(last_update)

    logger.info(
        "Extracted %d articles - AI processing will be applied during editorial generation",
        len(articles),
    )

    return articles, last_update
