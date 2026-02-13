"""
MoKa News - Main Entry Point
Orchestrates The Grinder, The Barista, and The Cup
"""

import os
import argparse
from dotenv import load_dotenv
from moka_news.grinder import Grinder
from moka_news.barista import (
    Barista,
    OpenAIBarista,
    AnthropicBarista,
    SimpleBarista,
    GeminiBarista,
    MistralBarista,
    GitHubCopilotCLIBarista,
    GeminiCLIBarista,
    MistralCLIBarista,
)
from moka_news.cup import serve
from moka_news.config import load_config, create_sample_config
from moka_news.opml_manager import OPMLManager
from moka_news.first_run_setup import is_first_run, run_first_run_setup
from datetime import datetime, time


def fetch_and_brew(feed_urls, config, ai_provider):
    """
    Fetch RSS feeds and brew articles with AI summaries.
    
    Returns:
        Tuple of (processed_articles, last_update_time)
    """
    print(f"📡 Grinding {len(feed_urls)} feeds...")
    
    # Step 1: The Grinder - Extract articles from RSS feeds
    grinder = Grinder(feed_urls)
    articles, last_update = grinder.grind()
    
    print(f"✓ Ground {len(articles)} articles")
    
    if not articles:
        print("No articles found. Please check your RSS feeds.")
        return [], last_update
    
    # Step 2: The Barista - Process articles with AI
    print(f"🤖 Brewing summaries with {ai_provider}...")
    
    if ai_provider == "openai":
        api_key = config["ai"]["api_keys"].get("openai") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️  Warning: OPENAI_API_KEY not found. Falling back to simple mode.")
            print(
                "   Set your API key in config file or: export OPENAI_API_KEY='your-key'"
            )
            barista = Barista(SimpleBarista())
        else:
            try:
                barista = Barista(OpenAIBarista(api_key=api_key))
            except ImportError as e:
                print(f"⚠️  Error: {e}")
                barista = Barista(SimpleBarista())
    elif ai_provider == "anthropic":
        api_key = config["ai"]["api_keys"].get("anthropic") or os.getenv(
            "ANTHROPIC_API_KEY"
        )
        if not api_key:
            print(
                "⚠️  Warning: ANTHROPIC_API_KEY not found. Falling back to simple mode."
            )
            print(
                "   Set your API key in config file or: export ANTHROPIC_API_KEY='your-key'"
            )
            barista = Barista(SimpleBarista())
        else:
            try:
                barista = Barista(AnthropicBarista(api_key=api_key))
            except ImportError as e:
                print(f"⚠️  Error: {e}")
                barista = Barista(SimpleBarista())
    elif ai_provider == "gemini":
        api_key = config["ai"]["api_keys"].get("gemini") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️  Warning: GEMINI_API_KEY not found. Falling back to simple mode.")
            print(
                "   Set your API key in config file or: export GEMINI_API_KEY='your-key'"
            )
            barista = Barista(SimpleBarista())
        else:
            try:
                barista = Barista(GeminiBarista(api_key=api_key))
            except ImportError as e:
                print(f"⚠️  Error: {e}")
                barista = Barista(SimpleBarista())
    elif ai_provider == "mistral":
        api_key = config["ai"]["api_keys"].get("mistral") or os.getenv(
            "MISTRAL_API_KEY"
        )
        if not api_key:
            print(
                "⚠️  Warning: MISTRAL_API_KEY not found. Falling back to simple mode."
            )
            print(
                "   Set your API key in config file or: export MISTRAL_API_KEY='your-key'"
            )
            barista = Barista(SimpleBarista())
        else:
            try:
                barista = Barista(MistralBarista(api_key=api_key))
            except ImportError as e:
                print(f"⚠️  Error: {e}")
                barista = Barista(SimpleBarista())
    elif ai_provider == "copilot-cli":
        print("ℹ️  Using GitHub Copilot CLI (requires 'gh' CLI installed)")
        try:
            barista = Barista(GitHubCopilotCLIBarista())
        except RuntimeError as e:
            print(f"⚠️  Error: {e}")
            print("   Falling back to simple mode.")
            barista = Barista(SimpleBarista())
    elif ai_provider == "gemini-cli":
        print("ℹ️  Using Gemini CLI (requires 'gcloud' CLI installed)")
        try:
            barista = Barista(GeminiCLIBarista())
        except RuntimeError as e:
            print(f"⚠️  Error: {e}")
            print("   Falling back to simple mode.")
            barista = Barista(SimpleBarista())
    elif ai_provider == "mistral-cli":
        print("ℹ️  Using Mistral CLI (requires 'mistral' CLI installed)")
        try:
            barista = Barista(MistralCLIBarista())
        except RuntimeError as e:
            print(f"⚠️  Error: {e}")
            print("   Falling back to simple mode.")
            barista = Barista(SimpleBarista())
    else:
        barista = Barista(SimpleBarista())
    
    processed_articles = barista.brew(articles)
    print(f"✓ Brewed {len(processed_articles)} articles")
    
    return processed_articles, last_update


def main():
    """Main entry point for MoKa News"""
    # Load environment variables from .env file
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="☕ MoKa News - Your Morning Persona News",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  moka-news                          # Use default feeds with AI processing (OpenAI)
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
        choices=[
            "openai",
            "anthropic",
            "gemini",
            "mistral",
            "simple",
            "copilot-cli",
            "gemini-cli",
            "mistral-cli",
        ],
        default=None,
        help="AI provider for generating summaries (default: from config or openai; 'simple' is demo/testing only)",
    )

    parser.add_argument(
        "--no-tui", action="store_true", help="Print articles to console instead of TUI"
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
        "--opml",
        metavar="PATH",
        help="Path to OPML file (default: ~/.config/moka-news/feeds.opml)",
    )

    args = parser.parse_args()

    # Initialize OPML manager
    opml_manager = OPMLManager(args.opml)

    # Check for first run and run setup wizard if needed
    # Skip setup wizard for specific commands that don't need it
    skip_setup = (
        args.create_config or 
        args.add_feed or 
        args.remove_feed or 
        args.list_feeds
    )
    
    if is_first_run() and not skip_setup:
        run_first_run_setup(opml_manager)
        # After setup, user needs to run moka-news again
        return

    # Handle feed management commands
    if args.add_feed:
        if opml_manager.add_feed(args.add_feed):
            print(f"✓ Added feed: {args.add_feed}")
            print(f"  Saved to: {opml_manager.opml_path}")
        else:
            print(f"⚠️  Feed already exists: {args.add_feed}")
        return

    if args.remove_feed:
        if opml_manager.remove_feed(args.remove_feed):
            print(f"✓ Removed feed: {args.remove_feed}")
            print(f"  Updated: {opml_manager.opml_path}")
        else:
            print(f"⚠️  Feed not found: {args.remove_feed}")
        return

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
        return

    # Handle --create-config
    if args.create_config:
        create_sample_config()
        return

    # Load configuration
    config = load_config(args.config)

    # CLI arguments override config file
    ai_provider = args.ai if args.ai else config["ai"]["provider"]
    
    # Get feeds from: CLI args > OPML manager > config file
    if args.feeds:
        feed_urls = args.feeds
    else:
        opml_feeds = opml_manager.list_feeds()
        if opml_feeds:
            feed_urls = [feed["url"] for feed in opml_feeds]
        else:
            feed_urls = config["feeds"]["urls"]
    
    use_tui = not args.no_tui if args.no_tui else config["ui"]["use_tui"]

    print("☕ Brewing your morning news...")
    
    # Fetch and brew articles
    processed_articles, last_update = fetch_and_brew(feed_urls, config, ai_provider)
    
    if not processed_articles:
        print("No articles to display.")
        return

    # Step 3: The Cup - Display in TUI
    if not use_tui:
        print("\n" + "=" * 80)
        for i, article in enumerate(processed_articles, 1):
            print(f"\n[{i}] {article.get('ai_title', article['title'])}")
            print(f"    Source: {article.get('source', 'Unknown')}")
            print(f"    {article.get('ai_summary', article['summary'][:200])}")
            print(f"    Link: {article.get('link', 'N/A')}")
        print("\n" + "=" * 80)
    else:
        print("☕ Serving your news...\n")
        
        # Create refresh callback for the TUI
        def refresh_callback():
            return fetch_and_brew(feed_urls, config, ai_provider)
        
        serve(processed_articles, last_update, refresh_callback)


if __name__ == "__main__":
    main()
