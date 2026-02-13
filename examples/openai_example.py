"""
Example: Using OpenAI for AI-powered summaries

Before running this example:
1. Set your OpenAI API key:
   export OPENAI_API_KEY='your-key-here'

2. Or create a .env file with:
   OPENAI_API_KEY=your-key-here
"""

import os
from dotenv import load_dotenv
from examples.demo import create_mock_articles
from moka_news.barista import Barista, OpenAIBarista, SimpleBarista
from moka_news.cup import serve


def main():
    """Example using OpenAI for summaries"""
    
    # Load environment variables
    load_dotenv()
    
    print("☕ MoKa News - OpenAI Example\n")
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY not found!")
        print("   Please set your API key:")
        print("   export OPENAI_API_KEY='your-key-here'")
        print("\n   Falling back to SimpleBarista...")
        barista = Barista(SimpleBarista())
    else:
        print("✓ OpenAI API key found")
        print("🤖 Using OpenAI for intelligent summaries...\n")
        try:
            barista = Barista(OpenAIBarista())
        except Exception as e:
            print(f"⚠️  Error initializing OpenAI: {e}")
            print("   Falling back to SimpleBarista...")
            barista = Barista(SimpleBarista())
    
    # Get mock articles
    articles = create_mock_articles()
    print(f"📰 Processing {len(articles)} articles...")
    
    # Process with barista
    processed = barista.brew(articles)
    print(f"✓ Processed {len(processed)} articles\n")
    
    # Display results
    print("=" * 80)
    for i, article in enumerate(processed[:2], 1):
        print(f"\n[{i}] Original: {article['title'][:70]}...")
        print(f"    AI Title:  {article['ai_title']}")
        print(f"    AI Summary: {article['ai_summary'][:100]}...")
    print("\n" + "=" * 80)
    
    # Launch TUI
    import sys
    if '--tui' in sys.argv:
        print("\n☕ Launching TUI...\n")
        serve(processed)
    else:
        print("\nAdd --tui flag to see the TUI version")


if __name__ == '__main__':
    main()
