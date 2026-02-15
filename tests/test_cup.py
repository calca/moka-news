"""
Tests for The Cup component
"""

from moka_news.cup import Cup
from datetime import datetime
from unittest.mock import MagicMock


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
    """Test that theme toggle action switches between light and dark themes"""
    app = Cup(
        theme="rose-pine",
        theme_light="rose-pine-dawn",
        theme_dark="rose-pine"
    )
    
    # Mock the notify method since it requires the app to be running
    app.notify = MagicMock()
    
    # Initially on dark theme
    assert app.theme == "rose-pine"
    
    # Call the actual action method to toggle to light
    app.action_toggle_theme()
    assert app.theme == "rose-pine-dawn", "First toggle should switch to light theme"
    assert app.notify.called, "Should notify user of theme change"
    
    # Call the action method again to toggle back to dark
    app.action_toggle_theme()
    assert app.theme == "rose-pine", "Second toggle should switch back to dark theme"


def test_cup_theme_toggle_from_custom():
    """Test that theme toggle from a custom theme switches to light first"""
    app = Cup(
        theme="nord",  # Custom theme not matching either light or dark
        theme_light="rose-pine-dawn",
        theme_dark="rose-pine"
    )
    
    # Mock the notify method
    app.notify = MagicMock()
    
    # Starting with custom theme
    assert app.theme == "nord"
    
    # Toggle from custom theme should switch to light (since it's not the light theme)
    app.action_toggle_theme()
    assert app.theme == "rose-pine-dawn", "Toggle from custom theme should switch to light"
    
    # Toggle again should switch to dark
    app.action_toggle_theme()
    assert app.theme == "rose-pine", "Second toggle should switch to dark"


def test_cup_with_editorial_content():
    """Test that Cup can display editorial content"""
    editorial_content = "# Test Editorial\n\nThis is a test editorial."
    app = Cup(editorial_content=editorial_content)
    assert app.editorial_content == editorial_content
