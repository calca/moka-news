"""
Tests for Grinder date filtering
"""

from moka_news.grinder import Grinder
from datetime import datetime, timedelta


def test_grinder_initialization_with_since():
    """Test that Grinder can be initialized with since parameter"""
    feeds = ["https://example.com/feed.xml"]
    since = datetime.now() - timedelta(days=1)
    grinder = Grinder(feeds, since=since)
    assert grinder.feed_urls == feeds
    assert grinder.since == since


def test_grinder_initialization_without_since():
    """Test that Grinder can be initialized without since parameter"""
    feeds = ["https://example.com/feed.xml"]
    grinder = Grinder(feeds)
    assert grinder.feed_urls == feeds
    assert grinder.since is None


def test_grinder_with_since_returns_tuple():
    """Test that grind() with since parameter returns a tuple"""
    since = datetime.now() - timedelta(days=7)
    grinder = Grinder(["https://example.com/feed.xml"], since=since)
    result = grinder.grind()
    assert isinstance(result, tuple)
    assert len(result) == 2
    articles, last_update = result
    assert isinstance(articles, list)
    assert isinstance(last_update, datetime)
