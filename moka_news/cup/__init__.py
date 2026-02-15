"""
The Cup - Textual TUI Interface
Displays the news digest in a beautiful terminal interface
"""

from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, VerticalScroll, Vertical, Horizontal
from textual.widgets import (
    Header,
    Footer,
    Static,
    Label,
    Markdown,
    ListView,
    ListItem,
    Button,
)
from textual.binding import Binding
from textual.screen import Screen, ModalScreen
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime, time
import webbrowser
import asyncio


class ConfirmationDialog(ModalScreen):
    """Modal dialog for confirming actions"""

    BINDINGS = [
        Binding("escape", "dismiss(False)", "Cancel", priority=True),
        Binding("n", "dismiss(False)", "No", priority=True),
        Binding("y", "dismiss(True)", "Yes", priority=True),
    ]

    CSS = """
    ConfirmationDialog {
        align: center middle;
    }
    
    #dialog-container {
        width: 60;
        height: auto;
        border: thick $primary;
        background: $panel;
        padding: 2;
    }
    
    #dialog-message {
        padding: 1 2;
        width: 100%;
        content-align: center middle;
    }
    
    #button-container {
        width: 100%;
        height: auto;
        align: center middle;
        padding: 1;
    }
    
    Button {
        margin: 0 1;
    }
    """

    def __init__(self, message: str, title: str = "Confirmation", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message
        self.dialog_title = title

    def compose(self) -> ComposeResult:
        """Create the dialog layout"""
        with Vertical(id="dialog-container"):
            yield Static(f"[bold]{self.dialog_title}[/bold]", id="dialog-title")
            yield Static(self.message, id="dialog-message")
            with Horizontal(id="button-container"):
                yield Button("Yes", variant="success", id="yes-button")
                yield Button("No", variant="error", id="no-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "yes-button":
            self.dismiss(True)
        else:
            self.dismiss(False)


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
            yield Label("[dim]🔗 Click card to open link[/dim]")

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
                    timestamp = editorial["timestamp"]
                    date_str = timestamp.strftime("%A, %B %d, %Y at %H:%M")
                    title = editorial.get("title", "Untitled")
                    item = ListItem(
                        Label(f"[bold]{title}[/bold]\n[dim]{date_str}[/dim]")
                    )
                    item.editorial_data = editorial
                    list_view.append(item)
                yield list_view
            else:
                yield Static(
                    "[bold]No past editorials found[/bold]\n\n"
                    "Editorials will appear here after they are generated.",
                    id="empty-state",
                )

        yield Footer()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle editorial selection"""
        if hasattr(event.item, "editorial_data"):
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
        Binding("h", "show_history", "History"),
        Binding("t", "toggle_theme", "Toggle Theme"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(
        self,
        articles: List[Dict[str, Any]] = None,
        last_update: Optional[datetime] = None,
        refresh_callback: Optional[
            Callable[[], tuple[List[Dict[str, Any]], datetime]]
        ] = None,
        auto_refresh_time: Optional[time] = time(8, 0),  # Default 8:00 AM
        editorial_content: Optional[str] = None,
        editorial_generator: Optional[Any] = None,
        theme: str = "rose-pine",
        theme_light: str = "rose-pine-dawn",
        theme_dark: str = "rose-pine",
        refresh_manager: Optional[Any] = None,
    ):
        super().__init__()
        self.articles = articles or []
        self.last_update = last_update or datetime.now()
        self.refresh_callback = refresh_callback
        self.auto_refresh_time = auto_refresh_time
        self.editorial_content = editorial_content
        self.editorial_generator = editorial_generator
        self.view_mode = "editorial"  # Always show editorial view
        self.title = "☕ MoKa News"
        self.sub_title = self._format_subtitle()
        self._auto_refresh_task = None
        self.theme_light = theme_light
        self.theme_dark = theme_dark
        self.theme = theme
        self.refresh_manager = refresh_manager

    def _format_subtitle(self) -> str:
        """Format the subtitle with last update time"""
        time_str = self.last_update.strftime("%H:%M:%S")
        date_str = self.last_update.strftime("%d/%m/%Y")
        return f"Your Morning Persona News | Editorial View | Last update: {date_str} at {time_str}"

    def compose(self) -> ComposeResult:
        """Create the application layout"""
        yield Header(show_clock=True)

        with ScrollableContainer(id="content-container"):
            if self.editorial_content:
                yield EditorialView(self.editorial_content, id="editorial-container")
            else:
                yield Static(
                    "[bold]No editorial available[/bold]\n\n"
                    "An editorial will be generated from your RSS feeds.",
                    id="empty-state",
                )

        yield Footer()

    async def on_mount(self) -> None:
        """Start the auto-refresh timer when the app mounts"""
        # If refresh manager is available, use its configured times
        # Otherwise, fall back to the single auto_refresh_time
        if self.refresh_callback:
            self._auto_refresh_task = asyncio.create_task(self._auto_refresh_loop())

    async def _auto_refresh_loop(self) -> None:
        """Background task that triggers refresh at specified times"""
        from datetime import timedelta

        while True:
            now = datetime.now()

            # Get refresh times - either from refresh manager or default
            if self.refresh_manager:
                allowed_times = self.refresh_manager.get_allowed_refresh_times()
            elif self.auto_refresh_time:
                allowed_times = [self.auto_refresh_time]
            else:
                # No refresh times configured
                await asyncio.sleep(3600)
                continue

            # Find the next refresh time
            target = None
            for refresh_time in allowed_times:
                potential_target = now.replace(
                    hour=refresh_time.hour,
                    minute=refresh_time.minute,
                    second=0,
                    microsecond=0,
                )

                # If this time hasn't passed today
                if now < potential_target:
                    if target is None or potential_target < target:
                        target = potential_target

            # If all times have passed today, schedule for first time tomorrow
            if target is None:
                tomorrow = now + timedelta(days=1)
                first_time = allowed_times[0]
                target = tomorrow.replace(
                    hour=first_time.hour,
                    minute=first_time.minute,
                    second=0,
                    microsecond=0,
                )

            # Calculate seconds until target time
            seconds_until_target = (target - now).total_seconds()

            # Wait until target time
            await asyncio.sleep(seconds_until_target)

            # Trigger automatic refresh (no confirmation needed)
            await self._perform_auto_refresh()

            # Wait a bit to avoid multiple triggers
            await asyncio.sleep(60)

    async def _perform_auto_refresh(self) -> None:
        """Perform automatic refresh without user confirmation"""
        if not self.refresh_callback:
            return

        self.notify("Automatic refresh starting...", severity="information")

        try:
            # Call the refresh callback to fetch new articles
            new_articles, new_update_time = self.refresh_callback()

            if new_articles:
                self.articles = new_articles
                self.last_update = new_update_time
                self.sub_title = self._format_subtitle()

                # Generate new editorial
                if self.editorial_generator:
                    try:
                        editorial = self.editorial_generator.generate_editorial(
                            new_articles
                        )
                        editorial_path = self.editorial_generator.save_editorial(
                            editorial
                        )
                        self.editorial_content = (
                            self.editorial_generator.load_editorial(editorial_path)
                        )
                    except Exception as e:
                        self.notify(
                            f"Error generating editorial: {e}", severity="error"
                        )

                # Rebuild the UI
                self._rebuild_view()

                # Log the automatic refresh
                if self.refresh_manager:
                    self.refresh_manager.log_refresh(auto=True)

                self.notify(
                    f"✓ Auto-refreshed {len(new_articles)} articles",
                    severity="information",
                )
            else:
                self.notify("No new articles found", severity="information")
        except Exception as e:
            self.notify(f"Error during auto-refresh: {e}", severity="error")

    async def action_refresh(self) -> None:
        """Refresh the news feed"""
        if not self.refresh_callback:
            self.notify("Refresh functionality not available", severity="warning")
            return

        # Check if refresh manager is available
        if self.refresh_manager:
            is_allowed, reason = self.refresh_manager.is_within_allowed_time()

            if not is_allowed:
                # Show warning dialog and ask for confirmation
                dialog = ConfirmationDialog(
                    message=f"{reason}\n\nDo you want to refresh anyway?",
                    title="⚠️ Refresh Outside Scheduled Hours",
                )
                confirmed = await self.push_screen_wait(dialog)

                if not confirmed:
                    self.notify("Refresh cancelled", severity="information")
                    return

                # User confirmed, proceed with manual refresh
                self.notify("Manual refresh confirmed", severity="information")

        self.notify("Refreshing news feeds...", severity="information")

        try:
            # Call the refresh callback to fetch new articles
            new_articles, new_update_time = self.refresh_callback()

            if new_articles:
                self.articles = new_articles
                self.last_update = new_update_time
                self.sub_title = self._format_subtitle()

                # Generate new editorial
                if self.editorial_generator:
                    self.notify("Generating editorial...", severity="information")
                    try:
                        editorial = self.editorial_generator.generate_editorial(
                            new_articles
                        )
                        editorial_path = self.editorial_generator.save_editorial(
                            editorial
                        )
                        self.editorial_content = (
                            self.editorial_generator.load_editorial(editorial_path)
                        )
                        self.notify("✓ Editorial generated", severity="information")
                    except Exception as e:
                        self.notify(
                            f"Error generating editorial: {e}", severity="error"
                        )

                # Rebuild the UI
                self._rebuild_view()

                # Log the refresh
                if self.refresh_manager:
                    self.refresh_manager.log_refresh(auto=False)

                self.notify(
                    f"✓ Refreshed {len(new_articles)} articles", severity="information"
                )
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

        # If current theme is the light theme, switch to dark
        # Otherwise (including custom themes), switch to light
        if current_theme == self.theme_light:
            # Switch to dark theme
            new_theme = self.theme_dark
            theme_name = "dark"
        else:
            # Switch to light theme
            new_theme = self.theme_light
            theme_name = "light"

        # Apply the new theme
        self.theme = new_theme
        self.notify(
            f"Switched to {theme_name} theme: {new_theme}", severity="information"
        )

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
            editorial_path = result["filepath"]
            try:
                content = self.editorial_generator.load_editorial(editorial_path)
                self.editorial_content = content
                self.sub_title = self._format_subtitle()
                self._rebuild_view()
                self.notify(
                    f"Loaded editorial: {result['title']}", severity="information"
                )
            except Exception as e:
                self.notify(f"Error loading editorial: {e}", severity="error")

    def _rebuild_view(self) -> None:
        """Rebuild the view to show the editorial"""
        container = self.query_one("#content-container")
        container.remove_children()

        if self.editorial_content:
            container.mount(
                EditorialView(self.editorial_content, id="editorial-container")
            )
        else:
            container.mount(
                Static(
                    "[bold]No editorial available[/bold]\n\n"
                    "An editorial will be generated from your RSS feeds.",
                    id="empty-state",
                )
            )


def serve(
    articles: List[Dict[str, Any]],
    last_update: Optional[datetime] = None,
    refresh_callback: Optional[
        Callable[[], tuple[List[Dict[str, Any]], datetime]]
    ] = None,
    auto_refresh_time: Optional[time] = time(8, 0),
    editorial_content: Optional[str] = None,
    editorial_generator: Optional[Any] = None,
    theme: str = "rose-pine",
    theme_light: str = "rose-pine-dawn",
    theme_dark: str = "rose-pine",
    refresh_manager: Optional[Any] = None,
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
        refresh_manager: Optional RefreshManager instance for controlling refresh times
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
        refresh_manager,
    )
    app.run()
