"""Command handlers and CLI input resolution."""

import argparse
from typing import Any, Dict, List

from moka_news.infrastructure.storage import OPMLManager


def should_skip_first_run_setup(args: argparse.Namespace) -> bool:
    """Return True when command does not need setup wizard."""
    return bool(
        args.create_config or args.add_feed or args.remove_feed or args.list_feeds
    )


def handle_feed_management_commands(
    args: argparse.Namespace, opml_manager: OPMLManager
) -> bool:
    """Handle feed-management commands. Returns True if command handled."""
    if args.add_feed:
        if opml_manager.add_feed(args.add_feed):
            print(f"✓ Added feed: {args.add_feed}")
            print(f"  Saved to: {opml_manager.opml_path}")
        else:
            print(f"⚠️  Feed already exists: {args.add_feed}")
        return True

    if args.remove_feed:
        if opml_manager.remove_feed(args.remove_feed):
            print(f"✓ Removed feed: {args.remove_feed}")
            print(f"  Updated: {opml_manager.opml_path}")
        else:
            print(f"⚠️  Feed not found: {args.remove_feed}")
        return True

    if args.list_feeds:
        feeds = opml_manager.list_feeds()
        if feeds:
            print(f"📋 Configured RSS Feeds ({len(feeds)}):")
            print(f"   OPML file: {opml_manager.opml_path}\n")
            for i, feed in enumerate(feeds, 1):
                print(f"   [{i}] {feed['title']}")
                print(f"       {feed['url']}")
                if i < len(feeds):
                    print()
        else:
            print("No feeds configured.")
            print("Add feeds with: moka-news --add-feed URL")
        return True

    return False


def resolve_feed_urls(
    args: argparse.Namespace,
    opml_manager: OPMLManager,
    config: Dict[str, Any],
) -> List[str]:
    """Resolve feed URLs from CLI args, OPML, or config fallback."""
    if args.feeds:
        return args.feeds

    opml_feeds = opml_manager.list_feeds()
    if opml_feeds:
        return [feed["url"] for feed in opml_feeds]

    return config["feeds"]["urls"]
