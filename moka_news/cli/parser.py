"""Argument parser for the MoKa News CLI."""

import argparse

from moka_news.constants import SUPPORTED_LANGUAGES


AI_CHOICES = [
    "openai",
    "anthropic",
    "gemini",
    "mistral",
    "simple",
    "copilot-cli",
    "gemini-cli",
    "mistral-cli",
]


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI parser."""
    parser = argparse.ArgumentParser(
        description="☕ MoKa News - Your Morning News",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  moka-news                          # Use default feeds with AI processing (Gemini CLI)
  moka-news --ai openai              # Use OpenAI API for summaries
  moka-news --ai anthropic           # Use Anthropic API for summaries
  moka-news --ai gemini              # Use Google Gemini API for summaries
  moka-news --ai mistral             # Use Mistral AI API for summaries
  moka-news --ai copilot-cli         # Use GitHub Copilot CLI for summaries
  moka-news --ai gemini-cli          # Use Gemini CLI (gcloud) for summaries
  moka-news --ai mistral-cli         # Use Mistral CLI for summaries
  moka-news --ai simple              # Use simple mode (demo/testing, no AI)
  moka-news --feeds feed1.xml feed2.xml  # Use custom feeds
  moka-news --config myconfig.yaml   # Use custom config file
  moka-news --daemon                 # Run as background service without TUI
  moka-news --create-config          # Create a sample config file

Feed Management:
  moka-news --add-feed URL           # Add RSS feed to OPML storage
  moka-news --remove-feed URL        # Remove RSS feed from OPML storage
  moka-news --list-feeds             # List all configured feeds
        """,
    )

    parser.add_argument(
        "--config", help="Path to configuration file (YAML)", default=None
    )

    parser.add_argument(
        "--create-config",
        action="store_true",
        help="Create a sample configuration file and exit",
    )

    parser.add_argument(
        "--feeds",
        nargs="+",
        help="RSS feed URLs to parse (default: built-in feeds)",
        default=None,
    )

    parser.add_argument(
        "--ai",
        choices=AI_CHOICES,
        default=None,
        help="AI provider for generating summaries (default: from config or gemini-cli; 'simple' is demo/testing only)",
    )

    parser.add_argument(
        "--language",
        choices=list(SUPPORTED_LANGUAGES.keys()),
        default=None,
        help="Language for editorial generation (default: from config or 'en')",
    )

    parser.add_argument(
        "--add-feed", metavar="URL", help="Add a new RSS feed URL to OPML storage"
    )

    parser.add_argument(
        "--remove-feed", metavar="URL", help="Remove an RSS feed URL from OPML storage"
    )

    parser.add_argument(
        "--list-feeds", action="store_true", help="List all configured RSS feeds"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode and write all logs to file (saves to ~/.config/moka-news/logs/)",
    )

    parser.add_argument(
        "--opml",
        metavar="PATH",
        help="Path to OPML file (default: ~/.config/moka-news/feeds.opml)",
    )

    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as background service without launching the TUI",
    )

    parser.add_argument(
        "--daemon-worker",
        action="store_true",
        help=argparse.SUPPRESS,
    )

    return parser
