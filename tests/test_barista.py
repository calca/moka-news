"""
Tests for The Barista component
"""

import pytest
from moka_news.barista import (
    Barista,
    SimpleBarista,
    AIProvider,
    GeminiBarista,
    MistralBarista,
    GitHubCopilotCLIBarista,
    GeminiCLIBarista,
    MistralCLIBarista,
)


def test_simple_barista_initialization():
    """Test that SimpleBarista can be initialized"""
    barista = SimpleBarista()
    assert isinstance(barista, AIProvider)


def test_simple_barista_generates_summary():
    """Test that SimpleBarista generates summaries"""
    barista = SimpleBarista()
    article = {
        "title": "Test Article Title",
        "summary": "This is a test summary that should be truncated to 200 characters maximum.",
    }
    result = barista.generate_summary(article)

    assert "title" in result
    assert "summary" in result
    assert len(result["summary"]) <= 200


def test_barista_brew_processes_articles():
    """Test that Barista processes a list of articles"""
    barista = Barista(SimpleBarista())
    articles = [
        {
            "title": "Article 1",
            "summary": "Summary 1",
            "link": "https://example.com/1",
            "published": "2026-01-01",
            "source": "Test Source",
        },
        {
            "title": "Article 2",
            "summary": "Summary 2",
            "link": "https://example.com/2",
            "published": "2026-01-02",
            "source": "Test Source",
        },
    ]

    processed = barista.brew(articles)

    assert len(processed) == 2
    assert all("ai_title" in article for article in processed)
    assert all("ai_summary" in article for article in processed)


def test_barista_brew_with_keywords():
    """Test that Barista processes articles with keywords"""
    keywords = ["technology", "AI", "programming"]
    barista = Barista(SimpleBarista(), keywords)
    articles = [
        {
            "title": "Article 1",
            "summary": "Summary about technology",
            "link": "https://example.com/1",
            "published": "2026-01-01",
            "source": "Test Source",
        },
    ]

    processed = barista.brew(articles)

    assert len(processed) == 1
    assert "ai_title" in processed[0]
    assert "ai_summary" in processed[0]
    assert barista.keywords == keywords


def test_barista_handles_empty_list():
    """Test that Barista handles empty article list"""
    barista = Barista(SimpleBarista())
    processed = barista.brew([])
    assert processed == []


def test_simple_barista_truncates_long_title():
    """Test that SimpleBarista truncates long titles"""
    barista = SimpleBarista()
    article = {
        "title": "A" * 100,  # Very long title
        "summary": "Short summary",
    }
    result = barista.generate_summary(article)
    assert len(result["title"]) <= 80


def test_gemini_barista_initialization_without_key():
    """Test that GeminiBarista raises error without API key"""
    with pytest.raises(Exception):  # Will raise ImportError or AttributeError
        GeminiBarista(api_key="invalid-key")


def test_mistral_barista_initialization_without_key():
    """Test that MistralBarista raises error without API key"""
    with pytest.raises(Exception):  # Will raise ImportError or AttributeError
        MistralBarista(api_key="invalid-key")


def test_github_copilot_cli_barista_checks_gh():
    """Test that GitHubCopilotCLIBarista can be instantiated"""
    barista = GitHubCopilotCLIBarista()
    assert isinstance(barista, AIProvider)


def test_gemini_cli_barista_checks_gcloud():
    """Test that GeminiCLIBarista can be instantiated"""
    barista = GeminiCLIBarista()
    assert isinstance(barista, AIProvider)


def test_mistral_cli_barista_checks_mistral():
    """Test that MistralCLIBarista can be instantiated"""
    barista = MistralCLIBarista()
    assert isinstance(barista, AIProvider)


def test_parse_editorial_response_new_title_paragraph_format():
    text = "TITLE: Morning Brief\n\nMarkets opened mixed after overnight volatility.\n\nSecond paragraph."
    parsed = AIProvider._parse_editorial_response(text)

    assert parsed["title"] == "Morning Brief"
    assert parsed["summary"] == "Markets opened mixed after overnight volatility.\n\nSecond paragraph."


def test_parse_editorial_response_legacy_summary_format():
    text = "TITLE: Legacy Title\nSUMMARY: Legacy summary body."
    parsed = AIProvider._parse_editorial_response(text)

    assert parsed["title"] == "Legacy Title"
    assert parsed["summary"] == "Legacy summary body."


def test_parse_editorial_response_without_title_marker():
    text = "No marker available"
    parsed = AIProvider._parse_editorial_response(text)

    assert parsed["title"] == "Your Morning News"
    assert parsed["summary"] == "No marker available"


def test_parse_editorial_response_case_insensitive_markers():
    text = "title: Lowercase Title\nsummary: Lowercase summary body."
    parsed = AIProvider._parse_editorial_response(text)

    assert parsed["title"] == "Lowercase Title"
    assert parsed["summary"] == "Lowercase summary body."
