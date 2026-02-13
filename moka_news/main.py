"""
MoKa News - Main Entry Point
Orchestrates The Grinder, The Barista, and The Cup
"""

import os
import argparse
from dotenv import load_dotenv
from moka_news.grinder import Grinder, get_default_feeds
from moka_news.barista import Barista, OpenAIBarista, AnthropicBarista, SimpleBarista
from moka_news.cup import serve


def main():
    """Main entry point for MoKa News"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='☕ MoKa News - Your Morning Persona News',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  moka-news                          # Use default feeds with simple processing
  moka-news --ai openai              # Use OpenAI for summaries
  moka-news --ai anthropic           # Use Anthropic for summaries
  moka-news --feeds feed1.xml feed2.xml  # Use custom feeds
        """
    )
    
    parser.add_argument(
        '--feeds',
        nargs='+',
        help='RSS feed URLs to parse (default: built-in feeds)',
        default=None
    )
    
    parser.add_argument(
        '--ai',
        choices=['openai', 'anthropic', 'simple'],
        default='simple',
        help='AI provider for generating summaries (default: simple)'
    )
    
    parser.add_argument(
        '--no-tui',
        action='store_true',
        help='Print articles to console instead of TUI'
    )
    
    args = parser.parse_args()
    
    # Get feed URLs
    feed_urls = args.feeds if args.feeds else get_default_feeds()
    
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
    print(f"🤖 Brewing summaries with {args.ai}...")
    
    if args.ai == 'openai':
        if not os.getenv('OPENAI_API_KEY'):
            print("⚠️  Warning: OPENAI_API_KEY not found. Falling back to simple mode.")
            print("   Set your API key: export OPENAI_API_KEY='your-key'")
            barista = Barista(SimpleBarista())
        else:
            try:
                barista = Barista(OpenAIBarista())
            except ImportError as e:
                print(f"⚠️  Error: {e}")
                barista = Barista(SimpleBarista())
    elif args.ai == 'anthropic':
        if not os.getenv('ANTHROPIC_API_KEY'):
            print("⚠️  Warning: ANTHROPIC_API_KEY not found. Falling back to simple mode.")
            print("   Set your API key: export ANTHROPIC_API_KEY='your-key'")
            barista = Barista(SimpleBarista())
        else:
            try:
                barista = Barista(AnthropicBarista())
            except ImportError as e:
                print(f"⚠️  Error: {e}")
                barista = Barista(SimpleBarista())
    else:
        barista = Barista(SimpleBarista())
    
    processed_articles = barista.brew(articles)
    print(f"✓ Brewed {len(processed_articles)} articles")
    
    # Step 3: The Cup - Display in TUI
    if args.no_tui:
        print("\n" + "="*80)
        for i, article in enumerate(processed_articles, 1):
            print(f"\n[{i}] {article.get('ai_title', article['title'])}")
            print(f"    Source: {article.get('source', 'Unknown')}")
            print(f"    {article.get('ai_summary', article['summary'][:200])}")
            print(f"    Link: {article.get('link', 'N/A')}")
        print("\n" + "="*80)
    else:
        print("☕ Serving your news...\n")
        serve(processed_articles)


if __name__ == '__main__':
    main()
