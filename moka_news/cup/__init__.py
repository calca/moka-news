"""
The Cup - Textual TUI Interface
Displays the news digest in a beautiful terminal interface
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Scrollable
from textual.widgets import Header, Footer, Static, Button, Label
from textual.binding import Binding
from typing import List, Dict, Any
import webbrowser


class ArticleCard(Static):
    """Widget to display a single article"""
    
    def __init__(self, article: Dict[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.article = article
        self.border_title = article.get('source', 'Unknown Source')
    
    def compose(self) -> ComposeResult:
        """Create the article card layout"""
        title = self.article.get('ai_title', self.article.get('title', 'No Title'))
        summary = self.article.get('ai_summary', self.article.get('summary', 'No summary available.'))
        link = self.article.get('link', '')
        published = self.article.get('published', '')
        
        yield Label(f"[bold cyan]{title}[/bold cyan]")
        yield Label(f"\n{summary}")
        if published:
            yield Label(f"\n[dim]{published}[/dim]")
        if link:
            yield Label(f"[dim][link={link}]{link}[/link][/dim]")
    
    def on_click(self) -> None:
        """Open article link in browser when clicked"""
        link = self.article.get('link')
        if link:
            try:
                webbrowser.open(link)
            except Exception as e:
                self.app.notify(f"Could not open link: {e}", severity="error")


class Cup(App):
    """MoKa News TUI Application"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #articles-container {
        height: 100%;
        padding: 1;
    }
    
    ArticleCard {
        border: solid $primary;
        padding: 1 2;
        margin: 1 0;
        background: $panel;
    }
    
    ArticleCard:hover {
        background: $boost;
        border: solid $accent;
    }
    
    #empty-state {
        text-align: center;
        padding: 4;
        color: $text-muted;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("r", "refresh", "Refresh"),
        ("ctrl+c", "quit", "Quit"),
    ]
    
    def __init__(self, articles: List[Dict[str, Any]] = None):
        super().__init__()
        self.articles = articles or []
        self.title = "☕ MoKa News"
        self.sub_title = "Your Morning Persona News"
    
    def compose(self) -> ComposeResult:
        """Create the application layout"""
        yield Header(show_clock=True)
        
        with Scrollable(id="articles-container"):
            if self.articles:
                for article in self.articles:
                    yield ArticleCard(article)
            else:
                yield Static(
                    "[bold]No articles available[/bold]\n\n"
                    "Run with RSS feeds to see news articles here.",
                    id="empty-state"
                )
        
        yield Footer()
    
    def action_refresh(self) -> None:
        """Refresh the news feed"""
        self.notify("Refresh functionality coming soon!", severity="information")
    
    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()


def serve(articles: List[Dict[str, Any]]):
    """
    Display articles in the TUI
    
    Args:
        articles: List of article dictionaries to display
    """
    app = Cup(articles)
    app.run()
