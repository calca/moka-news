"""
The Cup - Textual TUI Interface
Displays the news digest in a beautiful terminal interface
"""

from textual.app import App, ComposeResult
from textual import work
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
    ProgressBar,
    Collapsible,
)
from textual.binding import Binding
from textual.screen import Screen, ModalScreen
from textual.events import Mount
from typing import List, Dict, Any, Callable, Optional
from pathlib import Path
from datetime import datetime, time
import webbrowser
import asyncio
import subprocess
from moka_news import __version__
from moka_news.logger import get_logger

logger = get_logger(__name__)


class ConfirmationDialog(ModalScreen[bool]):
    """Modal dialog for confirming actions"""

    DEFAULT_CSS = """
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

    def __init__(self, message: str, title: str = "Confirmation"):
        super().__init__()
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
        elif event.button.id == "no-button":
            self.dismiss(False)
    
    def on_key(self, event) -> None:
        """Handle keyboard input"""
        if event.key == "y":
            self.dismiss(True)
        elif event.key == "n" or event.key == "escape":
            self.dismiss(False)


class LoadingDialog(ModalScreen):
    """Modal dialog showing loading progress"""

    DEFAULT_CSS = """
    LoadingDialog {
        align: center middle;
    }
    
    #loading-container {
        width: 50;
        height: auto;
        border: thick $primary;
        background: $panel;
        padding: 2;
    }
    
    #loading-message {
        padding: 1 2;
        width: 100%;
        content-align: center middle;
    }
    
    #progress-container {
        width: 100%;
        padding: 1 2;
    }
    
    ProgressBar {
        width: 100%;
        margin: 1 0;
    }
    """

    def __init__(self, message: str = "Loading..."):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        """Create the loading dialog layout"""
        with Vertical(id="loading-container"):
            yield Static(f"[bold]🔄 {self.message}[/bold]", id="loading-message")
            with Vertical(id="progress-container"):
                yield ProgressBar(show_eta=False, show_percentage=False)

    def on_mount(self) -> None:
        """Start the progress bar animation"""
        progress_bar = self.query_one(ProgressBar)
        # Set to indeterminate mode for infinite progress
        progress_bar.update(progress=None)
    
    def update_message(self, new_message: str) -> None:
        """Update the loading message
        
        Args:
            new_message: New message to display
        """
        self.message = new_message
        try:
            message_widget = self.query_one("#loading-message", Static)
            message_widget.update(f"[bold]🔄 {new_message}[/bold]")
        except Exception:
            pass  # Widget might not be mounted yet


class InfoDialog(ModalScreen[bool]):
    """Modal dialog showing application info"""

    DEFAULT_CSS = """
    InfoDialog {
        align: center middle;
    }
    
    #info-container {
        width: 70;
        height: 26;
        border: thick $primary;
        background: $panel;
        padding: 2;
    }
    
    #info-buttons {
        dock: bottom;
        width: 100%;
        height: 3;
        padding: 1 0;
        content-align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    """

    def __init__(self, config_path: Optional[str] = None, editorials_dir: Optional[str] = None, posters_dir: Optional[str] = None, logs_dir: Optional[str] = None):
        super().__init__()
        self.config_path = config_path or "Not specified"
        self.editorials_dir = editorials_dir or "Default location"
        self.posters_dir = posters_dir or "Default location"
        self.logs_dir = logs_dir or "Default location"

    def compose(self) -> ComposeResult:
        """Create the info dialog layout"""
        with Vertical(id="info-container"):
            yield Static(
                f"[bold]☕ MoKa News - Application Info[/bold]\n\n"
                f"[bold]Version:[/bold] {__version__}\n\n"
                f"[bold]Configuration File:[/bold]\n{self.config_path}\n\n"
                f"[bold]Editorials Directory:[/bold]\n{self.editorials_dir}\n\n"
                f"[bold]Posters Directory:[/bold]\n{self.posters_dir}\n\n"
                f"[bold]Logs Directory:[/bold]\n{self.logs_dir}\n\n"
                f"[dim]Press ESC or click OK to close[/dim]"
            )
            with Horizontal(id="info-buttons"):
                yield Button("OK", variant="primary", id="ok-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press"""
        if event.button.id == "ok-button":
            self.dismiss(True)

    def on_key(self, event) -> None:
        """Handle key press"""
        if event.key == "escape":
            self.dismiss(True)


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
    """Widget to display the morning editorial with collapsible sources"""

    def __init__(self, editorial_content: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editorial_content = editorial_content
        self._parse_editorial()

    def _parse_editorial(self):
        """Parse editorial content to separate main content from sources"""
        # Split editorial at the Sources section
        if "## Sources" in self.editorial_content:
            parts = self.editorial_content.split("## Sources", 1)
            self.main_content = parts[0].rstrip()
            self.sources_content = parts[1].strip() if len(parts) > 1 else ""
        else:
            self.main_content = self.editorial_content
            self.sources_content = ""

    def compose(self) -> ComposeResult:
        """Create the editorial view layout with collapsible sources"""
        # Main editorial content
        yield Markdown(self.main_content)
        
        # Sources section in a collapsible
        if self.sources_content:
            with Collapsible(title="📰 Sources", collapsed=True):
                yield Markdown(self.sources_content)


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
                # Create ListItems with attached data
                items = []
                for editorial in self.editorials:
                    timestamp = editorial["timestamp"]
                    date_str = timestamp.strftime("%A, %B %d, %Y at %H:%M")
                    title = editorial.get("title", "Untitled")
                    item = ListItem(
                        Label(f"[bold]{title}[/bold]\n[dim]{date_str}[/dim]")
                    )
                    item.editorial_data = editorial
                    items.append(item)
                
                # Yield the ListView with all items
                yield ListView(*items)
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
        Binding("g", "generate_poster", "Generate Poster"),
        Binding("h", "show_history", "History"),
        Binding("i", "show_info", "Info"),
        Binding("o", "open_external", "Open External"),
        Binding("t", "toggle_theme", "Toggle Theme"),
        Binding("p", "navigate_prev", "Prev Editorial"),
        Binding("n", "navigate_next", "Next Editorial"),
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
        opener_command: Optional[str] = None,
        current_editorial_path: Optional[Path] = None,
        config_path: Optional[str] = None,
        editorials_dir: Optional[str] = None,
        posters_dir: Optional[str] = None,
        logs_dir: Optional[str] = None,
        poster_config: Optional[Dict[str, Any]] = None,
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
        self.opener_command = opener_command
        self.current_editorial_path = current_editorial_path  # Track current editorial path
        self.config_path = config_path
        self.editorials_dir = editorials_dir
        self.posters_dir = posters_dir
        self.logs_dir = logs_dir
        self.poster_config = poster_config or {"method": "local", "default_template": "minimal"}
        
        # Navigation properties for editorials
        self.editorial_list: List[Dict[str, Any]] = []
        self.current_editorial_index: int = 0
        self._load_editorial_list()

    def _load_editorial_list(self) -> None:
        """Load the list of available editorials"""
        if self.editorial_generator:
            try:
                self.editorial_list = self.editorial_generator.list_editorials()
                # Find current editorial index if a path is provided
                if self.current_editorial_path and self.editorial_list:
                    for i, editorial in enumerate(self.editorial_list):
                        if editorial["filepath"] == self.current_editorial_path:
                            self.current_editorial_index = i
                            break
            except Exception as e:
                logger.warning(f"Could not load editorial list: {e}")
                self.editorial_list = []
                self.current_editorial_index = 0

    def _navigate_prev_editorial(self) -> None:
        """Navigate to the previous editorial"""
        if not self.editorial_list or len(self.editorial_list) <= 1:
            return
        
        if self.current_editorial_index > 0:
            self.current_editorial_index -= 1
            self._load_current_editorial()
    
    def _navigate_next_editorial(self) -> None:
        """Navigate to the next editorial"""
        if not self.editorial_list or len(self.editorial_list) <= 1:
            return
        
        if self.current_editorial_index < len(self.editorial_list) - 1:
            self.current_editorial_index += 1
            self._load_current_editorial()
    
    def _load_current_editorial(self) -> None:
        """Load and display the current editorial based on index"""
        if not self.editorial_list or self.current_editorial_index >= len(self.editorial_list):
            return
        
        try:
            current_editorial = self.editorial_list[self.current_editorial_index]
            editorial_path = current_editorial["filepath"]
            
            # Load editorial content
            content = self.editorial_generator.load_editorial(editorial_path)
            self.editorial_content = content
            self.current_editorial_path = editorial_path
            
            # Update subtitle
            self.sub_title = self._format_subtitle()
            
            # Rebuild the view with new content
            self._rebuild_view()
            
            # Notify user
            self.notify(
                f"Loaded editorial: {current_editorial.get('title', 'Untitled')}",
                severity="information"
            )
        except Exception as e:
            self.notify(f"Error loading editorial: {e}", severity="error")

    def _format_subtitle(self) -> str:
        """Format the subtitle with last update time"""
        time_str = self.last_update.strftime("%H:%M:%S")
        date_str = self.last_update.strftime("%d/%m/%Y")
        return f"Your Morning News | Last update: {date_str} at {time_str}"

    def compose(self) -> ComposeResult:
        """Create the application layout"""
        yield Header(show_clock=True)

        with ScrollableContainer(id="content-container"):
            # Always start with editorial if available, otherwise show empty state
            if self.editorial_content:
                yield EditorialView(self.editorial_content, id="editorial-container")
            else:
                yield Static(
                    "[bold]No editorial available[/bold]\n\n"
                    "No new articles found from your RSS feeds.\n"
                    "• Press 'r' to refresh feeds manually\n"
                    "• Press 'h' to view past editorials\n"
                    "• Check your feed configuration if this persists",
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

    async def _update_with_new_articles(
        self, new_articles, new_update_time, notify_editorial: bool = False
    ):
        """
        Update the app with new articles and generate editorial

        Args:
            new_articles: List of new articles
            new_update_time: Timestamp of the update
            notify_editorial: Whether to show editorial generation notifications
        """
        logger.info(f"Updating with {len(new_articles)} new articles")
        self.articles = new_articles
        self.last_update = new_update_time
        self.sub_title = self._format_subtitle()

        # Generate new editorial
        if self.editorial_generator:
            logger.info(f"Generating editorial with language: {self.editorial_generator.language}")
            if notify_editorial:
                self.notify("Generating editorial...", severity="information")
            try:
                editorial = self.editorial_generator.generate_editorial(new_articles)
                editorial_path = self.editorial_generator.save_editorial(editorial)
                self.current_editorial_path = editorial_path  # Track current editorial
                self.editorial_content = self.editorial_generator.load_editorial(
                    editorial_path
                )
                if notify_editorial:
                    self.notify("✓ Editorial generated", severity="information")
            except Exception as e:
                self.notify(f"Error generating editorial: {e}", severity="error")

        # Rebuild the UI (await to ensure it completes)
        await self._force_editorial_only_view()

    async def _perform_auto_refresh(self) -> None:
        """Perform automatic refresh without user confirmation"""
        if not self.refresh_callback:
            return

        logger.info("Starting automatic refresh...")
        self.notify("Automatic refresh starting...", severity="information")

        try:
            # Call the refresh callback to fetch new articles
            new_articles, new_update_time = self.refresh_callback()
            logger.info(f"Automatic refresh fetched {len(new_articles)} new articles")

            if new_articles:
                await self._update_with_new_articles(
                    new_articles, new_update_time, notify_editorial=False
                )

                # Log the automatic refresh
                if self.refresh_manager:
                    self.refresh_manager.log_refresh(auto=True)

                self.notify(
                    f"✓ Auto-refreshed {len(new_articles)} articles",
                    severity="information",
                )
            else:
                logger.info("No new articles found during automatic refresh")
                self.notify("No new articles found", severity="information")
        except Exception as e:
            logger.error(f"Error during auto-refresh: {e}")
            self.notify(f"Error during auto-refresh: {e}", severity="error")

    def action_refresh(self) -> None:
        """Refresh the news feed"""
        if not self.refresh_callback:
            self.notify("Refresh functionality not available", severity="warning")
            return

        # Ask for confirmation via callback (no push_screen_wait needed)
        dialog = ConfirmationDialog(
            message="Refresh feeds and generate a new editorial?",
            title="☕ Refresh",
        )
        self.push_screen(dialog, callback=self._on_refresh_confirmed)

    def _on_refresh_confirmed(self, confirmed: bool) -> None:
        """Handle refresh confirmation result"""
        if not confirmed:
            self.notify("Refresh cancelled", severity="information")
            return
        # Kick off the actual refresh work
        self._do_refresh()

    @work(exclusive=True)
    async def _do_refresh(self) -> None:
        """Perform the full refresh cycle in a worker thread"""
        loading_dialog = LoadingDialog("Starting refresh...")
        self.app.push_screen(loading_dialog)
        await asyncio.sleep(0.2)  # Give dialog time to render

        try:
            import concurrent.futures

            loop = asyncio.get_event_loop()

            # Step 1: Fetch RSS feeds
            loading_dialog.update_message("Fetching RSS feeds...")
            await asyncio.sleep(0.1)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                new_articles, new_update_time = await loop.run_in_executor(
                    executor, self.refresh_callback
                )

            if not new_articles:
                loading_dialog.dismiss()
                self.notify("No new articles found", severity="warning")
                return

            # Step 2: Generate editorial
            loading_dialog.update_message(
                f"Generating editorial from {len(new_articles)} articles..."
            )
            await asyncio.sleep(0.1)

            self.articles = new_articles
            self.last_update = new_update_time
            self.sub_title = self._format_subtitle()

            if self.editorial_generator:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    editorial = await loop.run_in_executor(
                        executor,
                        self.editorial_generator.generate_editorial,
                        new_articles,
                    )
                    editorial_path = await loop.run_in_executor(
                        executor,
                        self.editorial_generator.save_editorial,
                        editorial,
                    )
                    self.current_editorial_path = editorial_path
                    self.editorial_content = await loop.run_in_executor(
                        executor,
                        self.editorial_generator.load_editorial,
                        editorial_path,
                    )

            # Step 3: Prepare updated view
            loading_dialog.update_message("Building view...")
            await asyncio.sleep(0.1)

            # Reload editorial list for navigation
            self._load_editorial_list()

            # Dismiss loading dialog BEFORE rebuilding view
            loading_dialog.dismiss()
            await asyncio.sleep(0.1)

            # Rebuild the UI with new editorial
            await self._force_editorial_only_view()

            # Scroll to top
            try:
                container = self.query_one("#content-container")
                container.scroll_home(animate=True)
            except Exception:
                pass

            self.notify(
                f"✓ Refreshed {len(new_articles)} articles and generated new editorial",
                severity="information",
            )

        except Exception as e:
            try:
                loading_dialog.dismiss()
            except Exception:
                pass
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

    def action_navigate_prev(self) -> None:
        """Navigate to previous editorial using keyboard shortcut"""
        self._navigate_prev_editorial()

    def action_navigate_next(self) -> None:
        """Navigate to next editorial using keyboard shortcut"""
        self._navigate_next_editorial()

    def action_open_external(self) -> None:
        """Open current editorial in external application"""
        if not self.opener_command:
            self.notify(
                "No opener command configured. Set 'editorial.opener_command' in config.",
                severity="warning"
            )
            return
        
        if not self.current_editorial_path:
            self.notify("No editorial available to open", severity="warning")
            return
        
        try:
            subprocess.Popen([self.opener_command, str(self.current_editorial_path)])
            self.notify(
                f"Opening editorial with {self.opener_command}",
                severity="information"
            )
        except FileNotFoundError:
            self.notify(
                f"Command '{self.opener_command}' not found. Please check your configuration.",
                severity="error"
            )
        except Exception as e:
            self.notify(
                f"Error opening editorial: {e}",
                severity="error"
            )

    def action_show_history(self) -> None:
        """Show past editorials"""
        if not self.editorial_generator:
            self.notify("Editorial history not available", severity="warning")
            return

        try:
            # Get list of editorial files
            editorial_files = self.editorial_generator.list_editorials()

            if not editorial_files:
                self.notify("No past editorials found", severity="information")
                return

            # The list_editorials already returns properly formatted editorials
            editorials = editorial_files  # Use the data directly
            
            # Sort by timestamp (oldest first) - should already be sorted but ensure it
            editorials.sort(key=lambda x: x["timestamp"], reverse=False)

            # Show editorial list screen
            screen = EditorialListScreen(editorials)
            self.push_screen(screen, callback=self._handle_editorial_selection_wrapper)
        except Exception as e:
            self.notify(f"Error accessing editorial history: {e}", severity="error")

    async def _handle_editorial_selection(self, result) -> None:
        """Handle the selection from editorial history screen"""
        if result:
            # Load and display selected editorial
            editorial_path = result["filepath"]
            try:
                # Completely reset the application state for editorial-only view
                self.articles = []
                
                content = self.editorial_generator.load_editorial(editorial_path)
                self.editorial_content = content
                self.current_editorial_path = editorial_path  # Track current editorial
                
                # Reload editorial list and update current index for navigation
                self._load_editorial_list()
                
                # Find the index of the selected editorial
                for i, editorial in enumerate(self.editorial_list):
                    if editorial["filepath"] == editorial_path:
                        self.current_editorial_index = i
                        break
                
                self.sub_title = self._format_subtitle()
                
                # Force complete rebuild by clearing and remounting everything
                await self._force_editorial_only_view()
                
                # Scroll to top to show the editorial from the beginning
                container = self.query_one("#content-container")
                container.scroll_home(animate=True)
                
                self.notify(
                    f"Loaded editorial: {result['title']}", severity="information"
                )
            except Exception as e:
                self.notify(f"Error loading editorial: {e}", severity="error")
    
    def _handle_editorial_selection_wrapper(self, result) -> None:
        """Wrapper to handle async editorial selection callback"""
        if result:
            # Schedule the async handler
            asyncio.create_task(self._handle_editorial_selection(result))
    
    async def _force_editorial_only_view(self) -> None:
        """Force the view to show only the editorial, removing everything else"""
        container = self.query_one("#content-container")
        
        # Remove specific widgets by ID and wait for removal to complete
        widgets_to_remove = ["#editorial-container", "#empty-state"]
        for widget_id in widgets_to_remove:
            try:
                widget = self.query_one(widget_id)
                await widget.remove()
            except:
                pass  # Widget doesn't exist, which is fine
        
        # Mount only the editorial
        if self.editorial_content:
            editorial_view = EditorialView(self.editorial_content, id="editorial-container")
            await container.mount(editorial_view)
        else:
            empty_state = Static(
                "[bold]No editorial available[/bold]\n\n"
                "No new articles found from your RSS feeds.\n"
                "• Press 'r' to refresh feeds manually\n"
                "• Press 'h' to view past editorials\n"
                "• Check your feed configuration if this persists",
                id="empty-state",
            )
            await container.mount(empty_state)

    def action_show_info(self) -> None:
        """Show application information dialog"""
        info_dialog = InfoDialog(
            config_path=self.config_path,
            editorials_dir=self.editorials_dir,
            posters_dir=self.posters_dir,
            logs_dir=self.logs_dir
        )
        self.push_screen(info_dialog)

    def action_generate_poster(self) -> None:
        """Generate a poster from current editorial in the background"""
        if not self.editorial_content:
            self.notify("No editorial available to generate poster from", severity="warning")
            return
        self.notify("Generating poster in background…", severity="information")
        self._generate_poster_background()

    @work(thread=True, exclusive=True)
    def _generate_poster_background(self) -> None:
        """Generate poster in a background thread without blocking the TUI"""
        logger.info("Poster generation started (background thread)")
        try:
            from moka_news.poster import PosterGenerator, PosterContentGenerator

            poster_config = getattr(self, "poster_config", {
                "method": "local",
                "default_template": "minimal",
            })
            logger.debug(f"Poster config: {poster_config}")

            logger.debug(f"Instantiating PosterGenerator (posters_dir={self.posters_dir})")
            poster_gen = PosterGenerator(config=poster_config, posters_dir=self.posters_dir)

            # ── extract title from editorial markdown ────────────────────
            content = str(self.editorial_content)
            title = "Morning Editorial"
            for line in content.split("\n"):
                stripped = line.strip()
                if stripped.startswith("# "):
                    title = stripped[2:]
                    break
                elif stripped.startswith("## "):
                    title = stripped[3:]
                    break
            logger.debug(f"Extracted title: {title!r}")
            logger.debug(f"Editorial content length: {len(content)} chars")

            # ── AI poster content (configurable prompt) ──────────────────
            eg = getattr(self, "editorial_generator", None)
            ai_provider = getattr(eg, "ai_provider", None)
            language = getattr(eg, "language", "en")
            logger.debug(f"AI provider: {type(ai_provider).__name__ if ai_provider else 'None'}, language: {language}")
            content_prompt = poster_config.get("content_prompt")  # None → use default
            content_gen = PosterContentGenerator(
                ai_provider=ai_provider,
                prompt_config=content_prompt,
                language=language,
            )

            if ai_provider is not None:
                self.call_from_thread(
                    self.notify,
                    "Generating AI poster summary…",
                    severity="information",
                )

            logger.debug("Calling PosterContentGenerator.generate()")
            poster_content = content_gen.generate({"title": title, "content": content})
            logger.debug(f"Poster content length: {len(poster_content)} chars")
            # ─────────────────────────────────────────────────────────────

            editorial_data = {
                "title": title,
                "content": poster_content,
                "timestamp": datetime.now(),
            }

            template_name = poster_config.get("default_template", "minimal")
            logger.debug(f"Generating poster with template: {template_name!r}")
            poster_path = poster_gen.generate_poster(editorial_data, template_name)
            logger.info(f"Poster generated successfully: {poster_path}")

            self.call_from_thread(
                self.notify,
                f"✓ Poster saved: {poster_path.name}",
                severity="success",
            )
        except Exception as e:
            logger.exception(f"Poster generation failed: {e}")
            self.call_from_thread(
                self.notify,
                f"Error generating poster: {e}",
                severity="error",
            )

    def _rebuild_view(self) -> None:
        """Rebuild the view to show current content"""
        # Schedule the async force editorial only view
        asyncio.create_task(self._force_editorial_only_view())


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
    opener_command: Optional[str] = None,
    current_editorial_path: Optional[Path] = None,
    config_path: Optional[str] = None,
    editorials_dir: Optional[str] = None,
    posters_dir: Optional[str] = None,
    logs_dir: Optional[str] = None,
    poster_config: Optional[Dict[str, Any]] = None,
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
        opener_command: Optional command to open editorials in external app
        current_editorial_path: Path to the current editorial file
        config_path: Path to the configuration file
        editorials_dir: Path to the editorials directory
        posters_dir: Path to the posters directory
        logs_dir: Path to the logs directory
        poster_config: Configuration for poster generation
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
        opener_command,
        current_editorial_path,
        config_path,
        editorials_dir,
        posters_dir,
        logs_dir,
        poster_config,
    )
    app.run()
