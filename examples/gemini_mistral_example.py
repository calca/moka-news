#!/usr/bin/env python3
"""
Example: Using Gemini and Mistral AI providers

This example demonstrates how to use the new Gemini and Mistral AI providers
in MoKa News for article summarization.
"""

from moka_news.barista import Barista, GeminiBarista, MistralBarista, SimpleBarista
import os

# Sample article for demonstration
sample_articles = [
    {
        "title": "Python 3.13 Released with New Features",
        "summary": "The Python Software Foundation announced the release of Python 3.13, "
        "featuring improved performance, new syntax enhancements, and better error messages. "
        "The new version includes experimental features like free-threaded mode and "
        "an improved interactive interpreter with multi-line editing support.",
        "link": "https://example.com/python-3.13",
        "published": "2024-10-01",
        "source": "Python News",
    },
    {
        "title": "AI Models Continue to Advance",
        "summary": "Recent developments in artificial intelligence show significant improvements "
        "in model capabilities, with new architectures achieving better performance on "
        "various benchmarks while using less computational resources.",
        "link": "https://example.com/ai-advances",
        "published": "2024-10-02",
        "source": "Tech Review",
    },
]


def demo_gemini():
    """Demonstrate using Gemini for article summarization"""
    print("\n" + "=" * 80)
    print("DEMO: Google Gemini Integration")
    print("=" * 80)

    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  GEMINI_API_KEY not set. Using SimpleBarista instead.")
        print("   To use Gemini, set: export GEMINI_API_KEY='your-key'")
        barista = Barista(SimpleBarista())
    else:
        try:
            print("✓ Using Google Gemini for summarization")
            barista = Barista(GeminiBarista())
        except ImportError as e:
            print(f"⚠️  Error: {e}")
            print("   Install with: pip install -e '.[gemini]'")
            barista = Barista(SimpleBarista())

    # Process articles
    processed = barista.brew(sample_articles)

    # Display results
    for i, article in enumerate(processed, 1):
        print(f"\n[{i}] {article['ai_title']}")
        print(f"    {article['ai_summary']}")


def demo_mistral():
    """Demonstrate using Mistral for article summarization"""
    print("\n" + "=" * 80)
    print("DEMO: Mistral AI Integration")
    print("=" * 80)

    # Check if API key is set
    if not os.getenv("MISTRAL_API_KEY"):
        print("⚠️  MISTRAL_API_KEY not set. Using SimpleBarista instead.")
        print("   To use Mistral, set: export MISTRAL_API_KEY='your-key'")
        barista = Barista(SimpleBarista())
    else:
        try:
            print("✓ Using Mistral AI for summarization")
            barista = Barista(MistralBarista())
        except ImportError as e:
            print(f"⚠️  Error: {e}")
            print("   Install with: pip install -e '.[mistral]'")
            barista = Barista(SimpleBarista())

    # Process articles
    processed = barista.brew(sample_articles)

    # Display results
    for i, article in enumerate(processed, 1):
        print(f"\n[{i}] {article['ai_title']}")
        print(f"    {article['ai_summary']}")


def demo_config_file():
    """Demonstrate using configuration file"""
    print("\n" + "=" * 80)
    print("DEMO: Configuration File Usage")
    print("=" * 80)

    print("""
To use a configuration file:

1. Create a config file:
   $ moka-news --create-config

2. Edit 'moka-news.yaml':
   ai:
     provider: gemini  # or mistral, openai, anthropic
     api_keys:
       gemini: your-key-here
       mistral: your-key-here

3. Run with config:
   $ moka-news --config moka-news.yaml

Or place config in one of these locations:
  - ./moka-news.yaml
  - ./.moka-news.yaml
  - ~/.config/moka-news/config.yaml
  - ~/.moka-news.yaml
""")


if __name__ == "__main__":
    print("☕ MoKa News - Gemini & Mistral Integration Examples")

    # Run demos
    demo_gemini()
    demo_mistral()
    demo_config_file()

    print("\n" + "=" * 80)
    print("For more information, see: moka-news --help")
    print("=" * 80 + "\n")
