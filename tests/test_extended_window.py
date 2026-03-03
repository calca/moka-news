"""
Test for extended time window functionality
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from moka_news.infrastructure.storage import DownloadTracker


def test_get_last_download_with_days_back():
    """Test that days_back parameter returns correct timestamp"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker_file = Path(tmpdir) / "test_tracker.json"
        tracker = DownloadTracker(tracker_file)

        # Test with days_back=3
        three_days_ago = tracker.get_last_download(days_back=3)
        expected = datetime.now() - timedelta(days=3)

        # Check that it's approximately 3 days ago (within 1 minute tolerance)
        assert (
            abs(
                (
                    three_days_ago
                    - expected.replace(hour=0, minute=0, second=0, microsecond=0)
                ).total_seconds()
            )
            < 60
        )

        # Test with days_back=7
        seven_days_ago = tracker.get_last_download(days_back=7)
        expected = datetime.now() - timedelta(days=7)

        assert (
            abs(
                (
                    seven_days_ago
                    - expected.replace(hour=0, minute=0, second=0, microsecond=0)
                ).total_seconds()
            )
            < 60
        )


def test_get_last_download_days_back_ignores_tracker_file():
    """Test that days_back ignores existing tracker file"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker_file = Path(tmpdir) / "test_tracker.json"
        tracker = DownloadTracker(tracker_file)

        # Update tracker with a specific date
        specific_date = datetime(2024, 1, 15, 10, 30)
        tracker.update_last_download(specific_date)

        # Without days_back, should return the stored date
        stored_date = tracker.get_last_download(default_to_yesterday=False)
        assert stored_date == specific_date

        # With days_back, should ignore stored date and return days_back
        three_days_ago = tracker.get_last_download(days_back=3)
        expected = datetime.now() - timedelta(days=3)
        assert (
            abs(
                (
                    three_days_ago
                    - expected.replace(hour=0, minute=0, second=0, microsecond=0)
                ).total_seconds()
            )
            < 60
        )


def test_extended_window_config():
    """Test that extended window configuration is properly structured"""
    from moka_news.infrastructure.config import DEFAULT_CONFIG

    # Check that the new config options exist
    assert "editorial" in DEFAULT_CONFIG
    assert "min_articles" in DEFAULT_CONFIG["editorial"]
    assert "extended_window_days" in DEFAULT_CONFIG["editorial"]

    # Check default values
    assert DEFAULT_CONFIG["editorial"]["min_articles"] == 10
    assert DEFAULT_CONFIG["editorial"]["extended_window_days"] == 3
