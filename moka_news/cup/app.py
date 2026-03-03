"""Main Cup application class — the Textual TUI for MoKa News."""

from textual.app import App, ComposeResult
from textual import work
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, Static
from textual.binding import Binding
from typing import List, Dict, Any, Callable, Optional, Tuple
from pathlib import Path
from datetime import datetime, time
import asyncio
import re

from moka_news.paths import THEME_DARK, THEME_LIGHT
from moka_news.logger import get_logger
from moka_news.cup.dialogs import InfoDialog
from moka_news.cup.widgets import EditorialView
from moka_news.cup.screens import EditorialListScreen

logger = get_logger(__name__)


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
        Binding("u", "publish", "Publish"),
        Binding("h", "show_history", "History"),
        Binding("i", "show_info", "Info"),
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
            Callable[[], Tuple[List[Dict[str, Any]], datetime]]
        ] = None,
        auto_refresh_time: Optional[time] = time(8, 0),
        editorial_content: Optional[str] = None,
        editorial_generator: Optional[Any] = None,
        theme: str = THEME_DARK,
        theme_light: str = THEME_LIGHT,
        theme_dark: str = THEME_DARK,
        refresh_manager: Optional[Any] = None,
        current_editorial_path: Optional[Path] = None,
        config_path: Optional[str] = None,
        editorials_dir: Optional[str] = None,
        posters_dir: Optional[str] = None,
        logs_dir: Optional[str] = None,
        poster_config: Optional[Dict[str, Any]] = None,
        publish_manager: Optional[Any] = None,
    ):
        super().__init__()
        self.articles = articles or []
        self.last_update = last_update or datetime.now()
        self.refresh_callback = refresh_callback
        self.auto_refresh_time = auto_refresh_time
        self.editorial_content = editorial_content
        self.editorial_generator = editorial_generator
        self.view_mode = "editorial"
        self.title = "☕ MoKa News"
        self.sub_title = self._format_subtitle()
        self._auto_refresh_task = None
        self.theme_light = theme_light
        self.theme_dark = theme_dark
        self.theme = theme
        self.refresh_manager = refresh_manager
        self.current_editorial_path = current_editorial_path
        self.config_path = config_path
        self.editorials_dir = editorials_dir
        self.posters_dir = posters_dir
        self.logs_dir = logs_dir
        self.poster_config = poster_config or {
            "method": "local",
            "default_template": "story",
        }
        if publish_manager is not None:
            self.publish_manager = publish_manager
        else:
            from moka_news.publisher import PublishManager

            self.publish_manager = PublishManager([])
        self._manual_refresh_in_progress = False

        # Navigation properties for editorials
        self.editorial_list: List[Dict[str, Any]] = []
        self.current_editorial_index: int = 0
        self._load_editorial_list()

    # -- editorial navigation ------------------------------------------------

    def _load_editorial_list(self) -> None:
        if self.editorial_generator:
            try:
                self.editorial_list = self.editorial_generator.list_editorials()
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
        if not self.editorial_list or len(self.editorial_list) <= 1:
            return
        if self.current_editorial_index > 0:
            self.current_editorial_index -= 1
            self._load_current_editorial()

    def _navigate_next_editorial(self) -> None:
        if not self.editorial_list or len(self.editorial_list) <= 1:
            return
        if self.current_editorial_index < len(self.editorial_list) - 1:
            self.current_editorial_index += 1
            self._load_current_editorial()

    def _load_current_editorial(self) -> None:
        if not self.editorial_list or self.current_editorial_index >= len(
            self.editorial_list
        ):
            return
        try:
            current_editorial = self.editorial_list[self.current_editorial_index]
            editorial_path = current_editorial["filepath"]
            content = self.editorial_generator.load_editorial(editorial_path)
            self.editorial_content = content
            self.current_editorial_path = editorial_path
            self.sub_title = self._format_subtitle()
            self._rebuild_view()
            self.notify(
                f"Loaded editorial: {current_editorial.get('title', 'Untitled')}",
                severity="information",
            )
        except Exception as e:
            self.notify(f"Error loading editorial: {e}", severity="error")

    def _load_previous_editorial_fallback(self) -> bool:
        if not self.editorial_generator:
            return False
        try:
            previous_editorial = self.editorial_generator.load_most_recent_editorial()
            if not previous_editorial:
                return False
            self.current_editorial_path = previous_editorial["filepath"]
            self.editorial_content = previous_editorial["content"]
            self._load_editorial_list()
            return True
        except Exception as exc:
            logger.warning(f"Could not load fallback editorial: {exc}")
            return False

    # -- formatting helpers --------------------------------------------------

    def _format_subtitle(self) -> str:
        time_str = self.last_update.strftime("%H:%M:%S")
        date_str = self.last_update.strftime("%d/%m/%Y")
        return f"Your Morning News | Last update: {date_str} at {time_str}"

    # -- compose & mount -----------------------------------------------------

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="content-container"):
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
        if self.refresh_callback:
            self._auto_refresh_task = asyncio.create_task(self._auto_refresh_loop())

    # -- auto-refresh --------------------------------------------------------

    async def _auto_refresh_loop(self) -> None:
        from datetime import timedelta

        while True:
            now = datetime.now()

            if self.refresh_manager:
                allowed_times = self.refresh_manager.get_allowed_refresh_times()
            elif self.auto_refresh_time:
                allowed_times = [self.auto_refresh_time]
            else:
                await asyncio.sleep(3600)
                continue

            target = None
            for refresh_time in allowed_times:
                potential_target = now.replace(
                    hour=refresh_time.hour,
                    minute=refresh_time.minute,
                    second=0,
                    microsecond=0,
                )
                if now < potential_target:
                    if target is None or potential_target < target:
                        target = potential_target

            if target is None:
                tomorrow = now + timedelta(days=1)
                first_time = allowed_times[0]
                target = tomorrow.replace(
                    hour=first_time.hour,
                    minute=first_time.minute,
                    second=0,
                    microsecond=0,
                )

            seconds_until_target = (target - now).total_seconds()
            await asyncio.sleep(seconds_until_target)
            await self._perform_auto_refresh()
            await asyncio.sleep(60)

    async def _update_with_new_articles(
        self, new_articles, new_update_time, notify_editorial: bool = False
    ):
        logger.info(f"Updating with {len(new_articles)} new articles")
        self.articles = new_articles
        self.last_update = new_update_time
        self.sub_title = self._format_subtitle()

        if self.editorial_generator:
            logger.info(
                f"Generating editorial with language: {self.editorial_generator.language}"
            )
            if notify_editorial:
                self.notify("Generating editorial...", severity="information")
            try:
                editorial = self.editorial_generator.generate_editorial(new_articles)
                editorial_path = self.editorial_generator.save_editorial(editorial)
                self.current_editorial_path = editorial_path
                self.editorial_content = self.editorial_generator.load_editorial(
                    editorial_path
                )
                if notify_editorial:
                    self.notify("✓ Editorial generated", severity="information")
            except Exception as e:
                if self._load_previous_editorial_fallback():
                    self.notify(
                        "Error generating editorial. Loaded previous editorial.",
                        severity="warning",
                    )
                else:
                    self.notify(f"Error generating editorial: {e}", severity="error")

        await self._force_editorial_only_view()

    async def _perform_auto_refresh(self) -> None:
        if not self.refresh_callback:
            return

        logger.info("Starting automatic refresh...")
        self.notify("Automatic refresh starting...", severity="information")

        try:
            new_articles, new_update_time = self.refresh_callback()
            logger.info(f"Automatic refresh fetched {len(new_articles)} new articles")

            if new_articles:
                await self._update_with_new_articles(
                    new_articles, new_update_time, notify_editorial=False
                )
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

    # -- actions -------------------------------------------------------------

    def action_refresh(self) -> None:
        if not self.refresh_callback:
            self.notify("Refresh functionality not available", severity="warning")
            return
        if self._manual_refresh_in_progress:
            return
        self._manual_refresh_in_progress = True
        self._do_refresh()

    @work(exclusive=True)
    async def _do_refresh(self) -> None:
        try:
            import concurrent.futures

            loop = asyncio.get_running_loop()

            with concurrent.futures.ThreadPoolExecutor() as executor:
                new_articles, new_update_time = await loop.run_in_executor(
                    executor, self.refresh_callback
                )

                if not new_articles:
                    self.notify("No new articles found", severity="information")
                    return

                self.articles = new_articles
                self.last_update = new_update_time
                self.sub_title = self._format_subtitle()

                if self.editorial_generator:
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

            self._load_editorial_list()
            await self._force_editorial_only_view()

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
            if self._load_previous_editorial_fallback():
                await self._force_editorial_only_view()
                self.notify(
                    "Error refreshing editorial. Loaded previous editorial.",
                    severity="warning",
                )
            else:
                self.notify(f"Error refreshing: {e}", severity="error")
        finally:
            self._manual_refresh_in_progress = False

    def action_quit(self) -> None:
        self.exit()

    def action_toggle_theme(self) -> None:
        current_theme = self.theme
        if current_theme == self.theme_light:
            new_theme = self.theme_dark
            theme_name = "dark"
        else:
            new_theme = self.theme_light
            theme_name = "light"
        self.theme = new_theme
        self.notify(
            f"Switched to {theme_name} theme: {new_theme}", severity="information"
        )

    def action_navigate_prev(self) -> None:
        self._navigate_prev_editorial()

    def action_navigate_next(self) -> None:
        self._navigate_next_editorial()

    def action_show_history(self) -> None:
        if not self.editorial_generator:
            self.notify("Editorial history not available", severity="warning")
            return
        try:
            editorial_files = self.editorial_generator.list_editorials()
            if not editorial_files:
                self.notify("No past editorials found", severity="information")
                return
            editorials = editorial_files
            editorials.sort(key=lambda x: x["timestamp"], reverse=False)
            screen = EditorialListScreen(editorials)
            self.push_screen(screen, callback=self._handle_editorial_selection_wrapper)
        except Exception as e:
            self.notify(f"Error accessing editorial history: {e}", severity="error")

    async def _handle_editorial_selection(self, result) -> None:
        if result:
            editorial_path = result["filepath"]
            try:
                self.articles = []
                content = self.editorial_generator.load_editorial(editorial_path)
                self.editorial_content = content
                self.current_editorial_path = editorial_path
                self._load_editorial_list()

                for i, editorial in enumerate(self.editorial_list):
                    if editorial["filepath"] == editorial_path:
                        self.current_editorial_index = i
                        break

                self.sub_title = self._format_subtitle()
                await self._force_editorial_only_view()

                container = self.query_one("#content-container")
                container.scroll_home(animate=True)

                self.notify(
                    f"Loaded editorial: {result['title']}", severity="information"
                )
            except Exception as e:
                self.notify(f"Error loading editorial: {e}", severity="error")

    def _handle_editorial_selection_wrapper(self, result) -> None:
        if result:
            asyncio.create_task(self._handle_editorial_selection(result))

    async def _force_editorial_only_view(self) -> None:
        container = self.query_one("#content-container")
        widgets_to_remove = ["#editorial-container", "#empty-state"]
        for widget_id in widgets_to_remove:
            try:
                widget = self.query_one(widget_id)
                await widget.remove()
            except Exception:
                pass  # Widget doesn't exist, which is fine

        if self.editorial_content:
            editorial_view = EditorialView(
                self.editorial_content, id="editorial-container"
            )
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
        info_dialog = InfoDialog(
            config_path=self.config_path,
            editorials_dir=self.editorials_dir,
            posters_dir=self.posters_dir,
            logs_dir=self.logs_dir,
        )
        self.push_screen(info_dialog)

    def action_generate_poster(self) -> None:
        if not self.editorial_content:
            self.notify(
                "No editorial available to generate poster from", severity="warning"
            )
            return
        self.notify("Generating poster in background…", severity="information")
        self._generate_poster_background()

    def action_publish(self) -> None:
        if not self.editorial_content:
            self.notify("No editorial available to publish", severity="warning")
            return

        if not self.publish_manager.has_enabled_providers():
            self.notify(
                "No publish providers enabled. Configure writeas or buttondown in config.",
                severity="warning",
            )
            return

        provider_names = ", ".join(self.publish_manager.get_enabled_provider_names())
        self.notify(
            f"Publishing to {provider_names} in background…",
            severity="information",
        )
        self._publish_background()

    @work(thread=True, exclusive=True)
    def _publish_background(self) -> None:
        logger.info("Publish started (background thread)")
        content = str(self.editorial_content or "")
        title = self._extract_editorial_title(content)
        results = self.publish_manager.publish_all(title, content)

        for result in results:
            if result.success:
                msg = f"✓ Published to {result.provider}"
                if result.url:
                    msg += f": {result.url}"
                self.call_from_thread(self.notify, msg, severity="success")
            else:
                self.call_from_thread(
                    self.notify,
                    f"Error publishing to {result.provider}: {result.error}",
                    severity="error",
                )

    @work(thread=True, exclusive=True)
    def _generate_poster_background(self) -> None:
        logger.info("Poster generation started (background thread)")
        try:
            from moka_news.poster import PosterGenerator

            poster_config = getattr(
                self,
                "poster_config",
                {
                    "method": "local",
                    "default_template": "story",
                },
            )
            logger.debug(f"Poster config: {poster_config}")
            logger.debug(
                f"Instantiating PosterGenerator (posters_dir={self.posters_dir})"
            )
            poster_gen = PosterGenerator(
                config=poster_config, posters_dir=self.posters_dir
            )

            content = str(self.editorial_content)
            title = self._extract_editorial_title(content)
            logger.debug(f"Extracted title: {title!r}")
            logger.debug(f"Editorial content length: {len(content)} chars")

            editorial_data = {
                "title": title,
                "content": content,
                "timestamp": datetime.now(),
            }

            template_name = poster_config.get("default_template", "story")
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

    @staticmethod
    def _extract_editorial_title(content: str) -> str:
        text = content or ""
        title_marker_re = re.compile(
            r"^\s*(?:\*\*)?TITLE(?:\*\*)?\s*:\s*(.+?)\s*$",
            re.IGNORECASE | re.MULTILINE,
        )
        match = title_marker_re.search(text)
        if match:
            title = match.group(1).strip()
            if title:
                return title

        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip() or "Morning Editorial"
            if stripped.startswith("## "):
                return stripped[3:].strip() or "Morning Editorial"

        return "Morning Editorial"

    def _rebuild_view(self) -> None:
        asyncio.create_task(self._force_editorial_only_view())
