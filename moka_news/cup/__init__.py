"""
The Cup - Textual TUI Interface
Displays the news digest in a beautiful terminal interface
"""

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, VerticalScroll
from textual.widgets import Header, Footer, Static, Label, Markdown, ListView, ListItem
from textual.binding import Binding
from textual.screen import Screen
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime, time
from pathlib import Path
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


class EditorialView(Static):
    """Widget to display the morning editorial"""
    
    def __init__(self, editorial_content: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editorial_content = editorial_content
    
    def compose(self) -> ComposeResult:
        """Create the editorial view layout"""
        yield Markdown(self.editorial_content)


class EditorialListScreen(Screen):
    """Screen for browsing past editorials"""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Back", priority=True),
        ("q", "dismiss", "Back"),
    ]
    
    CSS = """
    EditorialListScreen {
        align: center middle;
    }
    
    #editorial-list-container {
        width: 80%;
        height: 80%;
        border: solid $primary;
        background: $panel;
        padding: 1;
    }
    
    ListView {
        height: 100%;
    }
    
    ListItem {
        padding: 1 2;
    }
    
    ListItem:hover {
        background: $boost;
    }
    """
    
    def __init__(self, editorials: List[Dict[str, Any]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editorials = editorials
        self.selected_editorial = None
    
    def compose(self) -> ComposeResult:
        """Create the editorial list layout"""
        yield Header()
        
        with VerticalScroll(id="editorial-list-container"):
            if self.editorials:
                list_view = ListView()
                for editorial in self.editorials:
                    timestamp = editorial['timestamp']
                    date_str = timestamp.strftime("%A, %B %d, %Y at %H:%M")
                    title = editorial.get('title', 'Untitled')
                    item = ListItem(Label(f"[bold]{title}[/bold]\n[dim]{date_str}[/dim]"))
                    item.editorial_data = editorial
                    list_view.append(item)
                yield list_view
            else:
                yield Static(
                    "[bold]No past editorials found[/bold]\n\n"
                    "Editorials will appear here after they are generated.",
                    id="empty-state"
                )
        
        yield Footer()
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle editorial selection"""
        if hasattr(event.item, 'editorial_data'):
            self.selected_editorial = event.item.editorial_data
            self.dismiss(self.selected_editorial)
    
    def action_dismiss(self) -> None:
        """Dismiss the screen"""
        self.dismiss(None)


class Cup(App):
    """MoKa News TUI Application"""

    CSS = """
    Screen {
        background: $surface;
    }
    
    #content-container {
        height: 100%;
        padding: 1;
    }
    
    #editorial-container {
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
    
    EditorialView {
        border: solid $primary;
        padding: 2;
        background: $panel;
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
        Binding("e", "toggle_editorial", "Editorial"),
        Binding("a", "show_articles", "Articles"),
        Binding("h", "show_history", "History"),
        Binding("t", "toggle_theme", "Toggle Theme"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(
        self,
        articles: List[Dict[str, Any]] = None,
        last_update: Optional[datetime] = None,
        refresh_callback: Optional[Callable[[], tuple[List[Dict[str, Any]], datetime]]] = None,
        auto_refresh_time: Optional[time] = time(8, 0),  # Default 8:00 AM
        editorial_content: Optional[str] = None,
        editorial_generator: Optional[Any] = None,
        theme: str = "rose-pine",
        theme_light: str = "rose-pine-dawn",
        theme_dark: str = "rose-pine",
    ):
        super().__init__()
        self.articles = articles or []
        self.last_update = last_update or datetime.now()
        self.refresh_callback = refresh_callback
        self.auto_refresh_time = auto_refresh_time
        self.editorial_content = editorial_content
        self.editorial_generator = editorial_generator
        self.view_mode = "editorial" if editorial_content else "articles"
        self.title = "☕ MoKa News"
        self.sub_title = self._format_subtitle()
        self._auto_refresh_task = None
        self.theme_light = theme_light
        self.theme_dark = theme_dark
        self.theme = theme

    def _format_subtitle(self) -> str:
        """Format the subtitle with last update time"""
        time_str = self.last_update.strftime("%H:%M:%S")
        date_str = self.last_update.strftime("%d/%m/%Y")
        mode_text = "Editorial View" if self.view_mode == "editorial" else "Articles View"
        return f"Your Morning Persona News | {mode_text} | Last update: {date_str} at {time_str}"

    def compose(self) -> ComposeResult:
        """Create the application layout"""
        yield Header(show_clock=True)

        with ScrollableContainer(id="content-container"):
            if self.view_mode == "editorial" and self.editorial_content:
                yield EditorialView(self.editorial_content, id="editorial-container")
            elif self.articles:
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
        # Set initial theme
        self.theme = self.theme
        
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
    
    def action_toggle_theme(self) -> None:
        """Toggle between light and dark theme"""
        current_theme = self.theme
        
        # Determine if current theme is light or dark
        is_dark = current_theme == self.theme_dark
        
        if is_dark:
            # Switch to light theme
            new_theme = self.theme_light
            theme_name = "light"
        else:
            # Switch to dark theme
            new_theme = self.theme_dark
            theme_name = "dark"
        
        # Apply the new theme
        self.theme = new_theme
        self.notify(f"Switched to {theme_name} theme: {new_theme}", severity="information")
    
    def action_toggle_editorial(self) -> None:
        """Toggle between editorial and articles view"""
        if self.editorial_content:
            self.view_mode = "editorial" if self.view_mode == "articles" else "articles"
            self.sub_title = self._format_subtitle()
            self._rebuild_view()
        else:
            self.notify("No editorial available", severity="warning")
    
    def action_show_articles(self) -> None:
        """Show articles view"""
        self.view_mode = "articles"
        self.sub_title = self._format_subtitle()
        self._rebuild_view()
    
    async def action_show_history(self) -> None:
        """Show past editorials"""
        if not self.editorial_generator:
            self.notify("Editorial history not available", severity="warning")
            return
        
        editorials = self.editorial_generator.list_editorials()
        
        if not editorials:
            self.notify("No past editorials found", severity="information")
            return
        
        # Show editorial list screen
        screen = EditorialListScreen(editorials)
        result = await self.push_screen_wait(screen)
        
        if result:
            # Load and display selected editorial
            editorial_path = result['filepath']
            try:
                content = self.editorial_generator.load_editorial(editorial_path)
                self.editorial_content = content
                self.view_mode = "editorial"
                self.sub_title = self._format_subtitle()
                self._rebuild_view()
                self.notify(f"Loaded editorial: {result['title']}", severity="information")
            except Exception as e:
                self.notify(f"Error loading editorial: {e}", severity="error")
    
    def _rebuild_view(self) -> None:
        """Rebuild the view based on current mode"""
        container = self.query_one("#content-container")
        container.remove_children()
        
        if self.view_mode == "editorial" and self.editorial_content:
            container.mount(EditorialView(self.editorial_content, id="editorial-container"))
        elif self.articles:
            for article in self.articles:
                container.mount(ArticleCard(article))
        else:
            container.mount(Static(
                "[bold]No articles available[/bold]\n\n"
                "Run with RSS feeds to see news articles here.",
                id="empty-state",
            ))


def serve(
    articles: List[Dict[str, Any]],
    last_update: Optional[datetime] = None,
    refresh_callback: Optional[Callable[[], tuple[List[Dict[str, Any]], datetime]]] = None,
    auto_refresh_time: Optional[time] = time(8, 0),
    editorial_content: Optional[str] = None,
    editorial_generator: Optional[Any] = None,
    theme: str = "rose-pine",
    theme_light: str = "rose-pine-dawn",
    theme_dark: str = "rose-pine",
):
    """
    Display articles in the TUI

    Args:
        articles: List of article dictionaries to display
        last_update: Timestamp of when articles were last fetched
        refresh_callback: Optional callback function to refresh articles
        auto_refresh_time: Time of day to automatically refresh (default: 8:00 AM)
        editorial_content: Optional markdown content of the editorial
        editorial_generator: Optional EditorialGenerator instance for accessing past editorials
        theme: Initial theme to use (default: rose-pine)
        theme_light: Light theme option (default: rose-pine-dawn)
        theme_dark: Dark theme option (default: rose-pine)
    """
    app = Cup(
        articles,
        last_update,
        refresh_callback,
        auto_refresh_time,
        editorial_content,
        editorial_generator,
        theme,
        theme_light,
        theme_dark,
    )
    app.run()
