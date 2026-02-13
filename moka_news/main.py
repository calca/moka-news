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
)
from moka_news.cup import serve
from moka_news.config import load_config, create_sample_config


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
  moka-news                          # Use default feeds with simple processing
  moka-news --ai openai              # Use OpenAI for summaries
  moka-news --ai anthropic           # Use Anthropic for summaries
  moka-news --ai gemini              # Use Google Gemini for summaries
  moka-news --ai mistral             # Use Mistral AI for summaries
  moka-news --feeds feed1.xml feed2.xml  # Use custom feeds
  moka-news --config myconfig.yaml   # Use custom config file
  moka-news --create-config          # Create a sample config file
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
        choices=["openai", "anthropic", "gemini", "mistral", "simple"],
        default=None,
        help="AI provider for generating summaries (default: from config or simple)",
    )

    parser.add_argument(
        "--no-tui", action="store_true", help="Print articles to console instead of TUI"
    )

    args = parser.parse_args()

    # Handle --create-config
    if args.create_config:
        create_sample_config()
        return

    # Load configuration
    config = load_config(args.config)

    # CLI arguments override config file
    ai_provider = args.ai if args.ai else config["ai"]["provider"]
    feed_urls = args.feeds if args.feeds else config["feeds"]["urls"]
    use_tui = not args.no_tui if args.no_tui else config["ui"]["use_tui"]

    print("☕ Brewing your morning news...")
    print(f"📡 Grinding {len(feed_urls)} feeds...")

    # Step 1: The Grinder - Extract articles from RSS feeds
    grinder = Grinder(feed_urls)
    articles = grinder.grind()

    print(f"✓ Ground {len(articles)} articles")

    if not articles:
        print("No articles found. Please check your RSS feeds.")
        return

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
    else:
        barista = Barista(SimpleBarista())

    processed_articles = barista.brew(articles)
    print(f"✓ Brewed {len(processed_articles)} articles")

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
        serve(processed_articles)


if __name__ == "__main__":
    main()
