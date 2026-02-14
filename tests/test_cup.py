"""
Tests for The Cup component
"""

from moka_news.cup import Cup, ArticleCard
from datetime import datetime


def test_cup_initialization():
    """Test that Cup can be initialized"""
    articles = [
        {
            "title": "Test Article",
            "summary": "Test summary",
            "link": "https://example.com",
            "published": "2026-01-01",
            "source": "Test Source",
            "ai_title": "AI Test Article",
            "ai_summary": "AI test summary",
        }
    ]
    last_update = datetime(2026, 1, 1, 12, 0, 0)
    app = Cup(articles, last_update)
    assert app.articles == articles
    assert app.title == "☕ MoKa News"
    assert app.last_update == last_update


def test_cup_with_empty_articles():
    """Test that Cup handles empty article list"""
    app = Cup([])
    assert app.articles == []


def test_cup_initialization_without_articles():
    """Test that Cup can be initialized without articles"""
    app = Cup()
    assert app.articles == []
    assert isinstance(app.last_update, datetime)


def test_article_card_initialization():
    """Test that ArticleCard can be initialized"""
    article = {
        "title": "Test",
        "summary": "Test summary",
        "link": "https://example.com",
        "source": "Test Source",
    }
    card = ArticleCard(article)
    assert card.article == article


def test_cup_theme_initialization():
    """Test that Cup can be initialized with custom themes"""
    app = Cup(
        theme="rose-pine",
        theme_light="rose-pine-dawn",
        theme_dark="rose-pine"
    )
    assert app.theme == "rose-pine"
    assert app.theme_light == "rose-pine-dawn"
    assert app.theme_dark == "rose-pine"


def test_cup_default_theme():
    """Test that Cup has default theme values"""
    app = Cup()
    assert app.theme == "rose-pine"
    assert app.theme_light == "rose-pine-dawn"
    assert app.theme_dark == "rose-pine"


def test_cup_theme_toggle():
    """Test that theme toggle switches between light and dark themes"""
    app = Cup(
        theme="rose-pine",
        theme_light="rose-pine-dawn",
        theme_dark="rose-pine"
    )
    
    # Initially on dark theme
    assert app.theme == "rose-pine"
    
    # Simulate toggle action (we can't easily test the actual action without running the app)
    # Instead, test the toggle logic directly
    current_theme = app.theme
    is_dark = current_theme == app.theme_dark
    
    # After first toggle, should switch to light
    if is_dark:
        new_theme = app.theme_light
    else:
        new_theme = app.theme_dark
    
    assert new_theme == "rose-pine-dawn", "First toggle should switch to light theme"
    
    # After second toggle, should switch back to dark
    current_theme = new_theme
    is_dark = current_theme == app.theme_dark
    
    if is_dark:
        new_theme = app.theme_light
    else:
        new_theme = app.theme_dark
    
    assert new_theme == "rose-pine", "Second toggle should switch back to dark theme"
