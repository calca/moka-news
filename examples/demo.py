"""
Example script demonstrating MoKa News with mock data
"""

from moka_news.barista import Barista, SimpleBarista
from moka_news.cup import serve


def create_mock_articles():
    """Create mock articles for demonstration"""
    return [
        {
            'title': 'Python 3.13 Released with Major Performance Improvements',
            'link': 'https://example.com/python-3.13',
            'summary': 'The Python Software Foundation announced the release of Python 3.13, featuring significant performance improvements including a new JIT compiler and optimized memory management. The release brings up to 40% speed improvements in certain workloads.',
            'published': '2026-02-10T10:00:00Z',
            'source': 'Tech News Daily',
        },
        {
            'title': 'New AI Model Achieves Human-Level Reasoning',
            'link': 'https://example.com/ai-breakthrough',
            'summary': 'Researchers unveil a groundbreaking AI model that demonstrates human-level reasoning capabilities across multiple domains. The model excels in mathematical problem-solving, creative writing, and complex decision-making tasks.',
            'published': '2026-02-11T14:30:00Z',
            'source': 'AI Research News',
        },
        {
            'title': 'GitHub Launches New Code Review Features',
            'link': 'https://example.com/github-features',
            'summary': 'GitHub introduces AI-powered code review suggestions and enhanced collaboration tools. The new features include intelligent comment threading, automated code quality checks, and improved diff visualization.',
            'published': '2026-02-12T09:15:00Z',
            'source': 'Developer Weekly',
        },
        {
            'title': 'Quantum Computing Breakthrough in Error Correction',
            'link': 'https://example.com/quantum-computing',
            'summary': 'Scientists achieve a major milestone in quantum computing by developing a new error correction technique that dramatically reduces computational errors. This advancement brings practical quantum computers closer to reality.',
            'published': '2026-02-12T16:45:00Z',
            'source': 'Science Today',
        },
        {
            'title': 'Open Source Project Reaches 100K Stars on GitHub',
            'link': 'https://example.com/opensource-success',
            'summary': 'The popular Textual framework for building terminal user interfaces hits a major milestone with 100,000 stars on GitHub. The project continues to gain traction among developers building CLI applications.',
            'published': '2026-02-13T08:00:00Z',
            'source': 'Open Source Digest',
        },
    ]


def main():
    """Run the example"""
    print("☕ MoKa News - Example with Mock Data\n")
    print("=" * 80)
    
    # Create mock articles
    articles = create_mock_articles()
    print(f"📰 Created {len(articles)} mock articles")
    
    # Process with Barista (using SimpleBarista since we don't have API keys)
    print("🤖 Processing articles with SimpleBarista...")
    barista = Barista(SimpleBarista())
    processed = barista.brew(articles)
    print(f"✓ Processed {len(processed)} articles\n")
    
    # Display in console
    print("=" * 80)
    print("CONSOLE OUTPUT:")
    print("=" * 80)
    for i, article in enumerate(processed, 1):
        print(f"\n[{i}] {article['ai_title']}")
        print(f"    Source: {article['source']}")
        print(f"    {article['ai_summary']}")
        print(f"    Published: {article['published']}")
    print("\n" + "=" * 80)
    
    # Ask if user wants to see TUI
    print("\nTo see the TUI version, run this script with '--tui' flag")
    print("Example: python examples/demo.py --tui\n")
    
    import sys
    if '--tui' in sys.argv:
        print("☕ Launching TUI...\n")
        serve(processed)


if __name__ == '__main__':
    main()
