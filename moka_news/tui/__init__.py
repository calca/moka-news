"""The TUI package (primary UI implementation)."""

from datetime import datetime, time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from moka_news.models import Article
from moka_news.paths import THEME_DARK, THEME_LIGHT
from moka_news.tui.app import Cup
from moka_news.tui.dialogs import (
    ConfirmationDialog as ConfirmationDialog,
    InfoDialog as InfoDialog,
    LoadingDialog as LoadingDialog,
)
from moka_news.tui.screens import EditorialListScreen as EditorialListScreen
from moka_news.tui.widgets import (
    ArticleCard as ArticleCard,
    EditorialView as EditorialView,
)


def serve(
    articles: List[Article],
    last_update: Optional[datetime] = None,
    refresh_callback: Optional[Callable[[], Tuple[List[Article], datetime]]] = None,
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
) -> None:
    """Display articles in the Textual TUI."""
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
        current_editorial_path,
        config_path,
        editorials_dir,
        posters_dir,
        logs_dir,
        poster_config,
        publish_manager,
    )
    app.run()


__all__ = [
    "Cup",
    "ArticleCard",
    "EditorialView",
    "EditorialListScreen",
    "ConfirmationDialog",
    "LoadingDialog",
    "InfoDialog",
    "serve",
]
