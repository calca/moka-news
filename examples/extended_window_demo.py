#!/usr/bin/env python3
"""
Example: Extended Time Window for Article Fetching

This example demonstrates MoKa News's smart article fetching feature.
When too few articles are found in the recent time window, the system
automatically expands the search to previous days.

This ensures you always get a rich, informative editorial even during
slow news periods (weekends, holidays, etc.).
"""

import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from moka_news.grinder import Grinder
from moka_news.download_tracker import DownloadTracker
from moka_news.logger import setup_logger, get_logger

# Setup logging
setup_logger("extended_window_demo")
logger = get_logger(__name__)


def demo_extended_window():
    """Demonstrate the extended time window feature"""
    
    print("=" * 70)
    print("MoKa News - Extended Time Window Demo")
    print("=" * 70)
    print()
    
    # Sample RSS feeds
    feeds = [
        "https://news.ycombinator.com/rss",
        "https://feeds.bbci.co.uk/news/technology/rss.xml",
    ]
    
    # Configuration (simulating the config.yaml)
    config = {
        "editorial": {
            "min_articles": 5,  # We want at least 5 articles
            "extended_window_days": 3  # Look back 3 days if needed
        }
    }
    
    min_articles = config["editorial"]["min_articles"]
    extended_window_days = config["editorial"]["extended_window_days"]
    
    print(f"Configuration:")
    print(f"  - Minimum articles needed: {min_articles}")
    print(f"  - Extended window: {extended_window_days} days")
    print()
    
    # Create a temporary download tracker
    with tempfile.TemporaryDirectory() as tmpdir:
        tracker_file = Path(tmpdir) / "demo_tracker.json"
        tracker = DownloadTracker(tracker_file)
        
        # Simulate a scenario where we last downloaded 12 hours ago
        last_download = datetime.now() - timedelta(hours=12)
        tracker.update_last_download(last_download)
        
        print(f"Scenario: Last download was {last_download.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"          (approximately 12 hours ago)")
        print()
        
        # Step 1: Try fetching with normal time window
        print("Step 1: Fetching articles since last download...")
        print("-" * 70)
        since = tracker.get_last_download()
        grinder = Grinder(feeds, since=since)
        articles, _ = grinder.grind()
        
        print(f"✓ Found {len(articles)} articles in the last 12 hours")
        print()
        
        # Step 2: Check if we need extended window
        if len(articles) < min_articles:
            print(f"⚠️  Only {len(articles)} articles found (need {min_articles} minimum)")
            print(f"→  Expanding time window to last {extended_window_days} days...")
            print("-" * 70)
            
            # Fetch with extended window
            extended_since = tracker.get_last_download(days_back=extended_window_days)
            grinder_extended = Grinder(feeds, since=extended_since)
            articles_extended, _ = grinder_extended.grind()
            
            print(f"✓ Found {len(articles_extended)} articles in the last {extended_window_days} days")
            print()
            
            # Show the difference
            print("Summary:")
            print(f"  - Articles in last 12 hours: {len(articles)}")
            print(f"  - Articles in last {extended_window_days} days: {len(articles_extended)}")
            print(f"  - Additional articles: {len(articles_extended) - len(articles)}")
            print()
            
            if len(articles_extended) >= min_articles:
                print(f"✓ Success! Now we have enough articles ({len(articles_extended)}) for a quality editorial")
            else:
                print(f"⚠️  Still only {len(articles_extended)} articles. Consider:")
                print(f"    - Adding more RSS feeds")
                print(f"    - Increasing extended_window_days")
                print(f"    - Lowering min_articles threshold")
        else:
            print(f"✓ Success! {len(articles)} articles is enough for editorial generation")
            print("   (No need to extend the time window)")
        
        print()
        print("=" * 70)
        print()
        print("How to configure this in your config.yaml:")
        print()
        print("editorial:")
        print("  min_articles: 5          # Minimum articles needed")
        print("  extended_window_days: 3  # Days to look back if needed")
        print()
        print("This feature is automatic - MoKa News will handle it for you!")
        print("=" * 70)


if __name__ == "__main__":
    demo_extended_window()
