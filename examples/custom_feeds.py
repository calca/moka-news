"""
Example: Using custom RSS feeds with MoKa News
"""

from moka_news.grinder import Grinder
from moka_news.barista import Barista, SimpleBarista
from moka_news.cup import serve


def main():
    """Example using custom RSS feeds"""

    # Define your own RSS feeds
    custom_feeds = [
        "https://news.ycombinator.com/rss",
        "https://www.reddit.com/r/python/.rss",
        "https://github.blog/feed/",
        "https://www.theverge.com/rss/index.xml",
    ]

    print("☕ MoKa News - Custom Feeds Example")
    print(f"📡 Grinding {len(custom_feeds)} feeds...\n")

    # Note: This example won't work in environments without internet access
    # In production, replace this with the actual grinder
    grinder = Grinder(custom_feeds)
    articles = grinder.grind()

    if not articles:
        print("⚠️  No articles found. This might be due to:")
        print("   - No internet connection")
        print("   - RSS feeds are not accessible")
        print("   - Feeds returned no content")
        print(
            "\n💡 Try running the demo.py script for a working example with mock data."
        )
        return

    print(f"✓ Ground {len(articles)} articles")
    print("🤖 Processing with SimpleBarista...")

    # Process articles
    barista = Barista(SimpleBarista())
    processed = barista.brew(articles)

    print(f"✓ Processed {len(processed)} articles")
    print("☕ Launching TUI...\n")

    # Display in TUI
    serve(processed)


if __name__ == "__main__":
    main()
