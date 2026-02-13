"""
Tests for The Grinder component
"""

import pytest
from moka_news.grinder import Grinder, get_default_feeds


def test_grinder_initialization():
    """Test that Grinder can be initialized with feed URLs"""
    feeds = ['https://example.com/feed.xml']
    grinder = Grinder(feeds)
    assert grinder.feed_urls == feeds


def test_grinder_with_empty_list():
    """Test that Grinder handles empty feed list"""
    grinder = Grinder([])
    articles = grinder.grind()
    assert articles == []


def test_get_default_feeds():
    """Test that default feeds are provided"""
    feeds = get_default_feeds()
    assert isinstance(feeds, list)
    assert len(feeds) > 0
    assert all(isinstance(url, str) for url in feeds)


def test_grinder_grind_returns_list():
    """Test that grind() returns a list"""
    grinder = Grinder(['https://example.com/feed.xml'])
    result = grinder.grind()
    assert isinstance(result, list)
