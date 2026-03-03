"""
Centralized path constants for MoKa News.

Every module that needs the application's config / data directories should
import from here instead of hard-coding ``Path.home() / ".config" / "moka-news"``.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Root directories
# ---------------------------------------------------------------------------

APP_CONFIG_DIR: Path = Path.home() / ".config" / "moka-news"
"""Main application configuration directory."""

EDITORIALS_DIR: Path = APP_CONFIG_DIR / "editorials"
"""Default directory to store generated editorials."""

POSTERS_DIR: Path = APP_CONFIG_DIR / "posters"
"""Default directory to store generated posters."""

LOGS_DIR: Path = APP_CONFIG_DIR / "logs"
"""Default directory to store log files."""

# ---------------------------------------------------------------------------
# Specific files
# ---------------------------------------------------------------------------

DEFAULT_CONFIG_PATH: Path = APP_CONFIG_DIR / "config.yaml"
"""Default path for the YAML configuration file."""

FEEDS_OPML_PATH: Path = APP_CONFIG_DIR / "feeds.opml"
"""Default path for the RSS feeds OPML file."""

DOWNLOAD_TRACKER_PATH: Path = APP_CONFIG_DIR / "last_download.json"
"""Path to the download tracker JSON file."""

REFRESH_LOG_PATH: Path = APP_CONFIG_DIR / "refresh_log.json"
"""Path to the refresh log JSON file."""

# ---------------------------------------------------------------------------
# Config file search order
# ---------------------------------------------------------------------------

CONFIG_SEARCH_LOCATIONS = [
    Path.cwd() / "moka-news.yaml",
    Path.cwd() / ".moka-news.yaml",
    DEFAULT_CONFIG_PATH,
    Path.home() / ".moka-news.yaml",
]
"""Ordered list of locations to search for configuration files."""

# ---------------------------------------------------------------------------
# Theme names
# ---------------------------------------------------------------------------

THEME_DARK: str = "rose-pine"
"""Default dark theme name."""

THEME_LIGHT: str = "rose-pine-dawn"
"""Default light theme name."""
