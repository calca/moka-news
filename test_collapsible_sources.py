#!/usr/bin/env python3
"""Test script to verify the collapsible Sources section in editorial"""

from datetime import datetime
from moka_news.cup import EditorialView
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer


# Sample editorial content with Sources section
sample_editorial = """# Your Morning Tech News

*Sunday, February 16, 2026 at 09:30*

---

Good morning! Here's your curated tech news digest for today.

The tech world continues to evolve rapidly. Python 3.12 has been officially released with significant performance improvements that developers have been eagerly anticipating. Meanwhile, artificial intelligence research reaches new milestones in natural language processing.

In the web development space, Django 5.0 introduces several exciting features that will make developers' lives easier. The framework continues to be a cornerstone of modern web development.

On the business front, a promising startup has secured $50 million in Series B funding, highlighting continued investor interest in innovative tech solutions.

That's your morning wrap-up. Enjoy your coffee!

---

## Sources

- [**Python 3.12 Released with Major Performance Improvements**](https://example.com/python-312) - *Python.org*

- [**Breakthrough in Natural Language Processing**](https://example.com/ai-breakthrough) - *TechCrunch*

- [**Django 5.0 Introduces Exciting New Features**](https://example.com/django-5) - *Python.org*

- [**Tech Startup Raises $50M in Series B**](https://example.com/funding) - *TechCrunch*

*Editorial generated from 4 articles*
"""


class TestApp(App):
    """Simple test app to demonstrate the collapsible Sources section"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #content-container {
        height: 100%;
        padding: 1;
    }
    
    EditorialView {
        border: solid $primary;
        padding: 2;
        background: $panel;
    }
    
    Collapsible {
        margin-top: 2;
    }
    """

    def compose(self) -> ComposeResult:
        """Create the test layout"""
        with ScrollableContainer(id="content-container"):
            yield EditorialView(sample_editorial)


if __name__ == "__main__":
    print("Testing collapsible Sources section in editorial...")
    print("The Sources section should appear in a collapsible widget.")
    print("Click on it to collapse/expand.")
    print("Press 'q' to exit.")
    print()
    app = TestApp()
    app.run()
