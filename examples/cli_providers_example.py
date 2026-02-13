#!/usr/bin/env python3
"""
Example: Using CLI-based AI providers

This example demonstrates how to use CLI-based AI providers (GitHub Copilot CLI,
Gemini CLI, Mistral CLI) in MoKa News for article summarization.
"""

from moka_news.barista import (
    Barista,
    GitHubCopilotCLIBarista,
    GeminiCLIBarista,
    MistralCLIBarista,
    SimpleBarista,
)

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
]


def demo_github_copilot_cli():
    """Demonstrate using GitHub Copilot CLI for article summarization"""
    print("\n" + "=" * 80)
    print("DEMO: GitHub Copilot CLI Integration")
    print("=" * 80)

    try:
        print("✓ Initializing GitHub Copilot CLI provider")
        barista = Barista(GitHubCopilotCLIBarista())
        print("✓ GitHub Copilot CLI is available")

        print("\nℹ️  Note: This requires 'gh' CLI to be installed and authenticated")
        print("   Install: https://cli.github.com/")
        print("   Authenticate: gh auth login")

        # Process articles
        print("\n🤖 Processing article with GitHub Copilot CLI...")
        processed = barista.brew(sample_articles)

        # Display results
        for i, article in enumerate(processed, 1):
            print(f"\n[{i}] {article['ai_title']}")
            print(f"    {article['ai_summary']}")

    except RuntimeError as e:
        print(f"⚠️  Error: {e}")
        print("   Using SimpleBarista fallback instead")
        barista = Barista(SimpleBarista())
        processed = barista.brew(sample_articles)
        for i, article in enumerate(processed, 1):
            print(f"\n[{i}] {article['ai_title']}")
            print(f"    {article['ai_summary']}")


def demo_gemini_cli():
    """Demonstrate using Gemini CLI for article summarization"""
    print("\n" + "=" * 80)
    print("DEMO: Gemini CLI Integration")
    print("=" * 80)

    try:
        print("✓ Initializing Gemini CLI provider")
        barista = Barista(GeminiCLIBarista())
        print("✓ Gemini CLI (gcloud) is available")

        print("\nℹ️  Note: This requires 'gcloud' CLI to be installed and configured")
        print("   Install: https://cloud.google.com/sdk/docs/install")
        print("   Configure: gcloud init")

        # Process articles
        print("\n🤖 Processing article with Gemini CLI...")
        processed = barista.brew(sample_articles)

        # Display results
        for i, article in enumerate(processed, 1):
            print(f"\n[{i}] {article['ai_title']}")
            print(f"    {article['ai_summary']}")

    except RuntimeError as e:
        print(f"⚠️  Error: {e}")
        print("   Using SimpleBarista fallback instead")
        barista = Barista(SimpleBarista())
        processed = barista.brew(sample_articles)
        for i, article in enumerate(processed, 1):
            print(f"\n[{i}] {article['ai_title']}")
            print(f"    {article['ai_summary']}")


def demo_mistral_cli():
    """Demonstrate using Mistral CLI for article summarization"""
    print("\n" + "=" * 80)
    print("DEMO: Mistral CLI Integration")
    print("=" * 80)

    try:
        print("✓ Initializing Mistral CLI provider")
        barista = Barista(MistralCLIBarista())
        print("✓ Mistral CLI is available")

        print("\nℹ️  Note: This requires 'mistral' CLI to be installed")
        print("   Install: pip install mistralai-cli")
        print("   Or see: https://docs.mistral.ai/cli/")

        # Process articles
        print("\n🤖 Processing article with Mistral CLI...")
        processed = barista.brew(sample_articles)

        # Display results
        for i, article in enumerate(processed, 1):
            print(f"\n[{i}] {article['ai_title']}")
            print(f"    {article['ai_summary']}")

    except RuntimeError as e:
        print(f"⚠️  Error: {e}")
        print("   Using SimpleBarista fallback instead")
        barista = Barista(SimpleBarista())
        processed = barista.brew(sample_articles)
        for i, article in enumerate(processed, 1):
            print(f"\n[{i}] {article['ai_title']}")
            print(f"    {article['ai_summary']}")


def demo_cli_usage():
    """Demonstrate CLI usage"""
    print("\n" + "=" * 80)
    print("DEMO: CLI Usage")
    print("=" * 80)

    print("""
To use CLI-based providers from the command line:

1. GitHub Copilot CLI:
   $ moka-news --ai copilot-cli

2. Gemini CLI (via gcloud):
   $ moka-news --ai gemini-cli

3. Mistral CLI:
   $ moka-news --ai mistral-cli

Or configure in moka-news.yaml:
   ai:
     provider: copilot-cli  # or gemini-cli, mistral-cli

Advantages of CLI providers:
- No API keys needed (CLIs handle authentication)
- Direct integration with existing CLI tools
- Leverages CLI's built-in features and configurations
""")


if __name__ == "__main__":
    print("☕ MoKa News - CLI-based AI Provider Examples")

    # Run demos
    demo_github_copilot_cli()
    demo_gemini_cli()
    demo_mistral_cli()
    demo_cli_usage()

    print("\n" + "=" * 80)
    print("For more information, see: moka-news --help")
    print("=" * 80 + "\n")
