"""
Integration tests for MoKa News
"""

import pytest
from moka_news.grinder import Grinder
from moka_news.barista import Barista, SimpleBarista
from moka_news.cup import Cup


def test_full_pipeline_with_mock_data():
    """Test the full pipeline with mock data"""
    # Create mock articles (simulating Grinder output)
    mock_articles = [
        {
            'title': 'Test Article 1',
            'link': 'https://example.com/1',
            'summary': 'This is the first test article summary.',
            'published': '2026-01-01T10:00:00Z',
            'source': 'Test Source',
        },
        {
            'title': 'Test Article 2',
            'link': 'https://example.com/2',
            'summary': 'This is the second test article summary.',
            'published': '2026-01-02T10:00:00Z',
            'source': 'Test Source',
        },
    ]
    
    # Process with Barista
    barista = Barista(SimpleBarista())
    processed = barista.brew(mock_articles)
    
    # Verify processing
    assert len(processed) == 2
    assert all('ai_title' in article for article in processed)
    assert all('ai_summary' in article for article in processed)
    
    # Create Cup app
    app = Cup(processed)
    assert len(app.articles) == 2
    assert app.articles[0]['ai_title'] is not None


def test_empty_pipeline():
    """Test pipeline with no articles"""
    # Empty grinder result
    articles = []
    
    # Process with Barista
    barista = Barista(SimpleBarista())
    processed = barista.brew(articles)
    
    # Create Cup app
    app = Cup(processed)
    assert len(app.articles) == 0
