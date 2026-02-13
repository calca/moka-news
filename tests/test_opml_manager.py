"""
Tests for OPML Manager
"""

import pytest
import os
import tempfile
import xml.etree.ElementTree as ET
from moka_news.opml_manager import OPMLManager


@pytest.fixture
def temp_opml_file():
    """Create a temporary OPML file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.opml', delete=False) as f:
        temp_path = f.name
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def opml_manager(temp_opml_file):
    """Create an OPML manager with a temporary file"""
    return OPMLManager(temp_opml_file)


def test_opml_manager_initialization(temp_opml_file):
    """Test that OPML manager can be initialized"""
    manager = OPMLManager(temp_opml_file)
    assert manager.opml_path == temp_opml_file


def test_opml_manager_default_path():
    """Test that OPML manager uses default path when not specified"""
    manager = OPMLManager()
    assert manager.opml_path == os.path.expanduser("~/.config/moka-news/feeds.opml")


def test_add_feed(opml_manager):
    """Test adding a new RSS feed"""
    url = "https://example.com/feed.xml"
    result = opml_manager.add_feed(url)
    assert result is True
    
    feeds = opml_manager.load_feeds()
    assert url in feeds


def test_add_feed_with_title(opml_manager):
    """Test adding a feed with a title"""
    url = "https://example.com/feed.xml"
    title = "Example Feed"
    result = opml_manager.add_feed(url, title=title)
    assert result is True
    
    feeds = opml_manager.list_feeds()
    assert len(feeds) == 1
    assert feeds[0]['url'] == url
    assert feeds[0]['title'] == title


def test_add_duplicate_feed(opml_manager):
    """Test that adding a duplicate feed returns False"""
    url = "https://example.com/feed.xml"
    opml_manager.add_feed(url)
    result = opml_manager.add_feed(url)
    assert result is False
    
    feeds = opml_manager.load_feeds()
    assert feeds.count(url) == 1


def test_remove_feed(opml_manager):
    """Test removing an RSS feed"""
    url = "https://example.com/feed.xml"
    opml_manager.add_feed(url)
    
    result = opml_manager.remove_feed(url)
    assert result is True
    
    feeds = opml_manager.load_feeds()
    assert url not in feeds


def test_remove_nonexistent_feed(opml_manager):
    """Test that removing a non-existent feed returns False"""
    url = "https://nonexistent.com/feed.xml"
    result = opml_manager.remove_feed(url)
    assert result is False


def test_load_feeds_empty_file(opml_manager):
    """Test loading feeds from non-existent file returns empty list"""
    feeds = opml_manager.load_feeds()
    assert feeds == []


def test_load_feeds_multiple(opml_manager):
    """Test loading multiple feeds"""
    urls = [
        "https://example1.com/feed.xml",
        "https://example2.com/feed.xml",
        "https://example3.com/feed.xml"
    ]
    
    for url in urls:
        opml_manager.add_feed(url)
    
    feeds = opml_manager.load_feeds()
    assert len(feeds) == 3
    for url in urls:
        assert url in feeds


def test_list_feeds_with_metadata(opml_manager):
    """Test listing feeds with metadata"""
    opml_manager.add_feed(
        "https://example.com/feed.xml",
        title="Example Feed",
        html_url="https://example.com"
    )
    
    feeds = opml_manager.list_feeds()
    assert len(feeds) == 1
    assert feeds[0]['url'] == "https://example.com/feed.xml"
    assert feeds[0]['title'] == "Example Feed"
    assert feeds[0]['htmlUrl'] == "https://example.com"


def test_opml_file_format(opml_manager):
    """Test that OPML file has correct format"""
    opml_manager.add_feed("https://example.com/feed.xml", title="Example")
    
    # Parse the OPML file
    tree = ET.parse(opml_manager.opml_path)
    root = tree.getroot()
    
    # Check root element
    assert root.tag == 'opml'
    assert root.get('version') == '2.0'
    
    # Check head section
    head = root.find('head')
    assert head is not None
    assert head.find('title') is not None
    assert head.find('dateCreated') is not None
    assert head.find('dateModified') is not None
    
    # Check body section
    body = root.find('body')
    assert body is not None
    
    # Check outline elements
    outlines = body.findall('.//outline[@type="rss"]')
    assert len(outlines) == 1
    assert outlines[0].get('xmlUrl') == "https://example.com/feed.xml"
    assert outlines[0].get('text') == "Example"


def test_save_and_load_consistency(opml_manager):
    """Test that saving and loading feeds preserves data"""
    test_feeds = [
        {'url': 'https://feed1.com/rss', 'title': 'Feed 1'},
        {'url': 'https://feed2.com/rss', 'title': 'Feed 2', 'htmlUrl': 'https://feed2.com'},
        {'url': 'https://feed3.com/rss', 'title': 'Feed 3'}
    ]
    
    opml_manager.save_feeds(test_feeds)
    loaded_feeds = opml_manager.list_feeds()
    
    assert len(loaded_feeds) == len(test_feeds)
    for original, loaded in zip(test_feeds, loaded_feeds):
        assert loaded['url'] == original['url']
        assert loaded['title'] == original['title']
        if 'htmlUrl' in original:
            assert loaded['htmlUrl'] == original['htmlUrl']
