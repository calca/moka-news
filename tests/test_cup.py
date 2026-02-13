"""
Tests for The Cup component
"""

import pytest
from moka_news.cup import Cup, ArticleCard


def test_cup_initialization():
    """Test that Cup can be initialized"""
    articles = [
        {
            'title': 'Test Article',
            'summary': 'Test summary',
            'link': 'https://example.com',
            'published': '2026-01-01',
            'source': 'Test Source',
            'ai_title': 'AI Test Article',
            'ai_summary': 'AI test summary',
        }
    ]
    app = Cup(articles)
    assert app.articles == articles
    assert app.title == "☕ MoKa News"


def test_cup_with_empty_articles():
    """Test that Cup handles empty article list"""
    app = Cup([])
    assert app.articles == []


def test_cup_initialization_without_articles():
    """Test that Cup can be initialized without articles"""
    app = Cup()
    assert app.articles == []


def test_article_card_initialization():
    """Test that ArticleCard can be initialized"""
    article = {
        'title': 'Test',
        'summary': 'Test summary',
        'link': 'https://example.com',
        'source': 'Test Source',
    }
    card = ArticleCard(article)
    assert card.article == article
