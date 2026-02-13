"""
The Cup - Textual TUI Interface
Displays the news digest in a beautiful terminal interface
"""

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, Static, Label
from textual.binding import Binding
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime, time
import webbrowser
import asyncio


class ArticleCard(Static):
    """Widget to display a single article"""

    def __init__(self, article: Dict[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.article = article
        self.border_title = article.get("source", "Unknown Source")

    def compose(self) -> ComposeResult:
        """Create the article card layout"""
        title = self.article.get("ai_title", self.article.get("title", "No Title"))
        summary = self.article.get(
            "ai_summary", self.article.get("summary", "No summary available.")
        )
        link = self.article.get("link", "")
        published = self.article.get("published", "")

        yield Label(f"[bold cyan]{title}[/bold cyan]")
        yield Label(f"\n{summary}")
        if published:
            yield Label(f"\n[dim]{published}[/dim]")
        if link:
            # Display simplified link - click the article card to open
            yield Label(f"[dim]🔗 Click card to open link[/dim]")

    def on_click(self) -> None:
        """Open article link in browser when clicked"""
        link = self.article.get("link")
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
    
    #update-info {
        padding: 0 2;
        text-align: right;
        color: $text-muted;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("r", "refresh", "Refresh"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(
        self,
        articles: List[Dict[str, Any]] = None,
        last_update: Optional[datetime] = None,
        refresh_callback: Optional[Callable[[], tuple[List[Dict[str, Any]], datetime]]] = None,
        auto_refresh_time: Optional[time] = time(8, 0),  # Default 8:00 AM
    ):
        super().__init__()
        self.articles = articles or []
        self.last_update = last_update or datetime.now()
        self.refresh_callback = refresh_callback
        self.auto_refresh_time = auto_refresh_time
        self.title = "☕ MoKa News"
        self.sub_title = self._format_subtitle()
        self._auto_refresh_task = None

    def _format_subtitle(self) -> str:
        """Format the subtitle with last update time"""
        time_str = self.last_update.strftime("%H:%M:%S")
        date_str = self.last_update.strftime("%d/%m/%Y")
        return f"Your Morning Persona News | Last update: {date_str} at {time_str}"

    def compose(self) -> ComposeResult:
        """Create the application layout"""
        yield Header(show_clock=True)

        with ScrollableContainer(id="articles-container"):
            if self.articles:
                for article in self.articles:
                    yield ArticleCard(article)
            else:
                yield Static(
                    "[bold]No articles available[/bold]\n\n"
                    "Run with RSS feeds to see news articles here.",
                    id="empty-state",
                )

        yield Footer()

    async def on_mount(self) -> None:
        """Start the auto-refresh timer when the app mounts"""
        if self.auto_refresh_time and self.refresh_callback:
            self._auto_refresh_task = asyncio.create_task(self._auto_refresh_loop())

    async def _auto_refresh_loop(self) -> None:
        """Background task that triggers refresh at specified time"""
        while True:
            now = datetime.now()
            target = now.replace(
                hour=self.auto_refresh_time.hour,
                minute=self.auto_refresh_time.minute,
                second=0,
                microsecond=0
            )
            
            # If target time has passed today, schedule for tomorrow
            if now >= target:
                from datetime import timedelta
                target = target + timedelta(days=1)
            
            # Calculate seconds until target time
            seconds_until_target = (target - now).total_seconds()
            
            # Wait until target time
            await asyncio.sleep(seconds_until_target)
            
            # Trigger refresh
            self.action_refresh()
            
            # Wait a bit to avoid multiple triggers
            await asyncio.sleep(60)

    def action_refresh(self) -> None:
        """Refresh the news feed"""
        if not self.refresh_callback:
            self.notify("Refresh functionality not available", severity="warning")
            return
        
        self.notify("Refreshing news feeds...", severity="information")
        
        try:
            # Call the refresh callback to fetch new articles
            new_articles, new_update_time = self.refresh_callback()
            
            if new_articles:
                self.articles = new_articles
                self.last_update = new_update_time
                self.sub_title = self._format_subtitle()
                
                # Rebuild the UI with new articles
                container = self.query_one("#articles-container")
                container.remove_children()
                
                for article in self.articles:
                    container.mount(ArticleCard(article))
                
                self.notify(f"✓ Refreshed {len(new_articles)} articles", severity="information")
            else:
                self.notify("No articles found during refresh", severity="warning")
        except Exception as e:
            self.notify(f"Error refreshing: {e}", severity="error")

    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()


def serve(
    articles: List[Dict[str, Any]],
    last_update: Optional[datetime] = None,
    refresh_callback: Optional[Callable[[], tuple[List[Dict[str, Any]], datetime]]] = None,
    auto_refresh_time: Optional[time] = time(8, 0),
):
    """
    Display articles in the TUI

    Args:
        articles: List of article dictionaries to display
        last_update: Timestamp of when articles were last fetched
        refresh_callback: Optional callback function to refresh articles
        auto_refresh_time: Time of day to automatically refresh (default: 8:00 AM)
    """
    app = Cup(articles, last_update, refresh_callback, auto_refresh_time)
    app.run()
