"""
Download Tracker - Tracks last download timestamp for filtering articles
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from moka_news.paths import APP_CONFIG_DIR, DOWNLOAD_TRACKER_PATH
from moka_news.logger import get_logger

logger = get_logger(__name__)


class DownloadTracker:
    """Tracks last download timestamp for filtering new articles"""

    def __init__(self, tracker_file: Optional[Path] = None):
        """
        Initialize the Download Tracker

        Args:
            tracker_file: Path to tracker file (defaults to ~/.config/moka-news/last_download.json)
        """
        if tracker_file:
            self.tracker_file = Path(tracker_file)
        else:
            APP_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            self.tracker_file = DOWNLOAD_TRACKER_PATH

    def get_last_download(
        self, default_to_yesterday: bool = True, days_back: Optional[int] = None
    ) -> Optional[datetime]:
        """
        Get the timestamp of last download

        Args:
            default_to_yesterday: If True and no download history exists,
                                 return yesterday's date (for limiting initial articles)
            days_back: If specified, return timestamp from N days ago instead of last download.
                      This is useful for expanding the time window when fetching articles.

        Returns:
            datetime of last download, or yesterday if never downloaded and default_to_yesterday=True
        """
        # If days_back is specified, return timestamp from N days ago
        if days_back is not None:
            days_ago = datetime.now() - timedelta(days=days_back)
            return days_ago.replace(hour=0, minute=0, second=0, microsecond=0)

        if not self.tracker_file.exists():
            if default_to_yesterday:
                # First time - return yesterday's date to limit articles
                yesterday = datetime.now() - timedelta(days=1)
                # Set to start of yesterday to get full day's articles
                return yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            return None

        try:
            with open(self.tracker_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                timestamp_str = data.get("last_download")
                if timestamp_str:
                    return datetime.fromisoformat(timestamp_str)
        except Exception as e:
            logger.warning(f"Could not read download tracker: {e}")

        if default_to_yesterday:
            yesterday = datetime.now() - timedelta(days=1)
            return yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

        return None

    def update_last_download(self, timestamp: Optional[datetime] = None):
        """
        Update the last download timestamp

        Args:
            timestamp: Timestamp to save (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        data = {"last_download": timestamp.isoformat()}

        try:
            with open(self.tracker_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not update download tracker: {e}")
