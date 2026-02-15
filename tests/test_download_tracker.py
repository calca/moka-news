"""
Tests for the Download Tracker
"""

from moka_news.download_tracker import DownloadTracker
from datetime import datetime, timedelta
import tempfile
from pathlib import Path


def test_download_tracker_initialization():
    """Test DownloadTracker initialization"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker_file = Path(tmpdir) / "tracker.json"
        tracker = DownloadTracker(tracker_file)
        assert tracker.tracker_file == tracker_file


def test_get_last_download_no_file():
    """Test get_last_download when file doesn't exist"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker_file = Path(tmpdir) / "tracker.json"
        tracker = DownloadTracker(tracker_file)
        last_download = tracker.get_last_download(default_to_yesterday=False)
        assert last_download is None


def test_get_last_download_defaults_to_yesterday():
    """Test get_last_download defaults to yesterday on first run"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker_file = Path(tmpdir) / "tracker.json"
        tracker = DownloadTracker(tracker_file)
        last_download = tracker.get_last_download(default_to_yesterday=True)
        
        # Should return yesterday at midnight
        expected = datetime.now() - timedelta(days=1)
        expected = expected.replace(hour=0, minute=0, second=0, microsecond=0)
        
        assert last_download is not None
        assert last_download.date() == expected.date()
        assert last_download.hour == 0
        assert last_download.minute == 0


def test_update_and_get_last_download():
    """Test updating and retrieving last download"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker_file = Path(tmpdir) / "tracker.json"
        tracker = DownloadTracker(tracker_file)
        
        # Update with specific timestamp
        test_time = datetime(2024, 2, 14, 8, 0, 0)
        tracker.update_last_download(test_time)
        
        # Retrieve and verify
        retrieved = tracker.get_last_download()
        assert retrieved == test_time


def test_update_last_download_defaults_to_now():
    """Test that update_last_download defaults to current time"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker_file = Path(tmpdir) / "tracker.json"
        tracker = DownloadTracker(tracker_file)
        
        before = datetime.now()
        tracker.update_last_download()
        after = datetime.now()
        
        retrieved = tracker.get_last_download()
        assert before <= retrieved <= after


def test_tracker_file_persistence():
    """Test that tracker file persists across instances"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker_file = Path(tmpdir) / "tracker.json"
        
        # Create first tracker and save timestamp
        tracker1 = DownloadTracker(tracker_file)
        test_time = datetime(2024, 2, 14, 10, 30, 0)
        tracker1.update_last_download(test_time)
        
        # Create second tracker and verify timestamp
        tracker2 = DownloadTracker(tracker_file)
        retrieved = tracker2.get_last_download()
        assert retrieved == test_time
