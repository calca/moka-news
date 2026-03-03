"""
The Cup - Textual TUI Interface
Displays the news digest in a beautiful terminal interface

Sub-modules:
    dialogs  -- ConfirmationDialog, LoadingDialog, InfoDialog
    widgets  -- ArticleCard, EditorialView
    screens  -- EditorialListScreen
    app      -- Cup (main Textual App)
"""

from moka_news.cup.dialogs import (
    ConfirmationDialog as ConfirmationDialog,
    LoadingDialog as LoadingDialog,
    InfoDialog as InfoDialog,
)
from moka_news.cup.widgets import (
    ArticleCard as ArticleCard,
    EditorialView as EditorialView,
)
from moka_news.cup.screens import EditorialListScreen as EditorialListScreen
from moka_news.cup.app import Cup

from typing import List, Dict, Any, Callable, Optional, Tuple
from pathlib import Path
from datetime import datetime, time

from moka_news.paths import THEME_DARK, THEME_LIGHT


def serve(
    articles: List[Dict[str, Any]],
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
    """
    Display articles in the TUI

    Args:
        articles: List of article dictionaries to display
        last_update: Timestamp of when articles were last fetched
        refresh_callback: Optional callback function to refresh articles
        auto_refresh_time: Time of day to automatically refresh (default: 8:00 AM)
        editorial_content: Optional markdown content of the editorial
        editorial_generator: Optional EditorialGenerator instance
        theme: Initial theme to use (default: rose-pine)
        theme_light: Light theme option (default: rose-pine-dawn)
        theme_dark: Dark theme option (default: rose-pine)
        refresh_manager: Optional RefreshManager instance
        current_editorial_path: Path to the current editorial file
        config_path: Path to the configuration file
        editorials_dir: Path to the editorials directory
        posters_dir: Path to the posters directory
        logs_dir: Path to the logs directory
        poster_config: Configuration for poster generation
        publish_manager: PublishManager instance
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
        current_editorial_path,
        config_path,
        editorials_dir,
        posters_dir,
        logs_dir,
        poster_config,
        publish_manager,
    )
    app.run()
