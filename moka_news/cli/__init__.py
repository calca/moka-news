"""CLI package for MoKa News."""

from moka_news.cli.parser import build_parser
from moka_news.cli.commands import (
    should_skip_first_run_setup,
    handle_feed_management_commands,
    resolve_feed_urls,
)

__all__ = [
    "build_parser",
    "should_skip_first_run_setup",
    "handle_feed_management_commands",
    "resolve_feed_urls",
]
