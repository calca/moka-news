"""
Integration tests for MoKa News
"""

from moka_news.barista import SimpleBarista
from moka_news.tui import Cup


def _process_articles(articles):
    """Process articles through SimpleBarista, adding ai_title/ai_summary."""
    provider = SimpleBarista()
    processed = []
    for article in articles:
        result = provider.generate_summary(article)
        processed_article = article.copy()
        processed_article["ai_title"] = result["title"]
        processed_article["ai_summary"] = result["summary"]
        processed.append(processed_article)
    return processed


def test_full_pipeline_with_mock_data():
    """Test the full pipeline with mock data"""
    # Create mock articles (simulating Grinder output)
    mock_articles = [
        {
            "title": "Test Article 1",
            "link": "https://example.com/1",
            "summary": "This is the first test article summary.",
            "published": "2026-01-01T10:00:00Z",
            "source": "Test Source",
        },
        {
            "title": "Test Article 2",
            "link": "https://example.com/2",
            "summary": "This is the second test article summary.",
            "published": "2026-01-02T10:00:00Z",
            "source": "Test Source",
        },
    ]

    # Process with SimpleBarista
    processed = _process_articles(mock_articles)

    # Verify processing
    assert len(processed) == 2
    assert all("ai_title" in article for article in processed)
    assert all("ai_summary" in article for article in processed)

    # Create Cup app
    app = Cup(processed)
    assert len(app.articles) == 2
    assert app.articles[0]["ai_title"] is not None


def test_empty_pipeline():
    """Test pipeline with no articles"""
    # Empty grinder result
    articles = []

    # Process with SimpleBarista
    processed = _process_articles(articles)

    # Create Cup app
    app = Cup(processed)
    assert len(app.articles) == 0
