#!/usr/bin/env python3
"""Test script to verify the new Collapsible feature for articles by source"""

from datetime import datetime
from moka_news.cup import ArticleListScreen
from textual.app import App, ComposeResult


# Sample articles for testing
sample_articles = [
    {
        "title": "Python 3.12 Released",
        "ai_title": "Python 3.12 Released with Major Performance Improvements",
        "summary": "Python Software Foundation announces Python 3.12",
        "ai_summary": "The Python Software Foundation has released Python 3.12 with significant performance improvements and new features.",
        "link": "https://example.com/python-312",
        "published": "2024-01-15 10:00:00",
        "source": "Python.org"
    },
    {
        "title": "New AI Breakthrough",
        "ai_title": "Breakthrough in Natural Language Processing",
        "summary": "Researchers achieve new milestone in AI",
        "ai_summary": "A team of researchers has achieved a significant breakthrough in natural language processing capabilities.",
        "link": "https://example.com/ai-breakthrough",
        "published": "2024-01-15 11:30:00",
        "source": "TechCrunch"
    },
    {
        "title": "Django 5.0 Features",
        "ai_title": "Django 5.0 Introduces Exciting New Features",
        "summary": "Django web framework gets major update",
        "ai_summary": "The Django web framework has been updated to version 5.0 with several exciting new features for developers.",
        "link": "https://example.com/django-5",
        "published": "2024-01-15 09:00:00",
        "source": "Python.org"
    },
    {
        "title": "Startup Funding News",
        "ai_title": "Tech Startup Raises $50M in Series B",
        "summary": "Major funding round for promising startup",
        "ai_summary": "A promising tech startup has successfully raised $50 million in Series B funding.",
        "link": "https://example.com/funding",
        "published": "2024-01-15 14:00:00",
        "source": "TechCrunch"
    },
]


class TestApp(App):
    """Simple test app to demonstrate the ArticleListScreen"""

    def on_mount(self) -> None:
        """Show the article list screen on mount"""
        self.push_screen(ArticleListScreen(sample_articles))


if __name__ == "__main__":
    print("Testing Collapsible articles by source feature...")
    print("This will open the TUI with sample articles grouped by source.")
    print("Press 'q' or 'Escape' to exit.")
    print()
    app = TestApp()
    app.run()
