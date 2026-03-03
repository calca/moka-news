"""Use-case helpers for preparing and launching the TUI."""

import argparse
from datetime import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from moka_news.application.use_cases.fetch_articles import fetch_and_brew
from moka_news.tui import serve
from moka_news.infrastructure.config.loader import get_config_path
from moka_news.infrastructure.storage import DownloadTracker, RefreshManager
from moka_news.logger import get_logger
from moka_news.models import Article
from moka_news.paths import LOGS_DIR, POSTERS_DIR, THEME_DARK, THEME_LIGHT
from moka_news.publisher import PublishManager, create_publish_providers

logger = get_logger(__name__)


def build_refresh_manager(config: Dict[str, Any]) -> RefreshManager:
    """Create and configure refresh manager from config."""
    refresh_manager = RefreshManager()
    refresh_config = config.get("refresh", {})

    allowed_times = refresh_config.get("allowed_times", ["08:00", "20:00"])
    parsed_times = []
    for time_str in allowed_times:
        try:
            hour, minute = time_str.split(":")
            parsed_times.append(time(int(hour), int(minute)))
        except ValueError:
            logger.warning("Invalid time format in config: %s", time_str)

    if parsed_times:
        refresh_manager.allowed_refresh_times = parsed_times

    refresh_manager.auto_refresh_window = refresh_config.get("auto_refresh_window", 60)
    return refresh_manager


def resolve_posters_dir(config: Dict[str, Any]) -> str:
    """Resolve posters directory path for UI info."""
    poster_config = config.get("poster", {})
    posters_dir_path = poster_config.get("posters_dir")
    if posters_dir_path:
        return str(Path(posters_dir_path).expanduser().resolve())
    return str(POSTERS_DIR)


def launch_cup(
    args: argparse.Namespace,
    articles: List[Article],
    last_update: Any,
    feed_urls: List[str],
    config: Dict[str, Any],
    ai_provider: str,
    download_tracker: DownloadTracker,
    editorial_generator: Any,
    editorial_content: Optional[str],
    editorial_path: Optional[Path],
) -> None:
    """Launch TUI with assembled runtime context."""

    def refresh_callback():
        return fetch_and_brew(feed_urls, config, ai_provider, download_tracker)

    theme = config["ui"].get("theme", THEME_DARK)
    theme_light = config["ui"].get("theme_light", THEME_LIGHT)
    theme_dark = config["ui"].get("theme_dark", THEME_DARK)

    refresh_manager = None
    if config.get("refresh", {}).get("require_confirmation_outside_hours", True):
        refresh_manager = build_refresh_manager(config)

    config_path = str(args.config) if args.config else str(get_config_path())
    actual_editorials_dir = str(editorial_generator.editorials_dir)
    actual_posters_dir = resolve_posters_dir(config)
    actual_logs_dir = str(LOGS_DIR)
    poster_config = config.get("poster", {})

    publish_providers = create_publish_providers(config)
    publish_manager = PublishManager(publish_providers)

    serve(
        articles,
        last_update,
        refresh_callback,
        editorial_content=editorial_content,
        editorial_generator=editorial_generator,
        theme=theme,
        theme_light=theme_light,
        theme_dark=theme_dark,
        refresh_manager=refresh_manager,
        current_editorial_path=editorial_path,
        config_path=config_path,
        editorials_dir=actual_editorials_dir,
        posters_dir=actual_posters_dir,
        logs_dir=actual_logs_dir,
        poster_config=poster_config,
        publish_manager=publish_manager,
    )
