#!/usr/bin/env python3
"""
Example demonstrating keyword functionality in MoKa News

This example shows how to use keywords to focus AI-generated summaries
on specific topics or aspects you're interested in.
"""

from moka_news.infrastructure.config import create_sample_config
from moka_news.barista import SimpleBarista
from moka_news.barista import _build_prompt

# Example 1: Create a config file with keywords
print("=" * 80)
print("Example 1: Creating a configuration file with keywords")
print("=" * 80)

# Create a sample config (will be saved as moka-news.yaml)
create_sample_config("example-keywords.yaml")

print("\n✓ Sample config created at: example-keywords.yaml")
print("\nYou can edit this file to add your preferred keywords:")
print("""
ai:
  keywords:
    - technology
    - artificial intelligence
    - programming
    - cybersecurity
    - machine learning
""")

# Example 2: Load config with keywords
print("\n" + "=" * 80)
print("Example 2: Loading configuration with keywords")
print("=" * 80)

# For this demo, we'll create a config dict directly
config = {
    "ai": {
        "provider": "simple",
        "keywords": ["artificial intelligence", "machine learning", "deep learning"],
        "api_keys": {},
    },
    "feeds": {"urls": []},
    "ui": {"use_tui": False},
}

print(f"\n✓ Keywords configured: {config['ai']['keywords']}")

# Example 3: Process articles with keywords
print("\n" + "=" * 80)
print("Example 3: Processing articles with keywords")
print("=" * 80)

# Sample articles
articles = [
    {
        "title": "New AI Model Achieves State-of-the-Art Results",
        "summary": "Researchers have developed a new machine learning model that surpasses previous benchmarks in natural language processing tasks.",
        "link": "https://example.com/article1",
        "source": "Tech News",
        "published": "2026-02-13",
    },
    {
        "title": "Company Announces Cloud Infrastructure Expansion",
        "summary": "Major cloud provider announces plans to expand data center infrastructure across multiple regions.",
        "link": "https://example.com/article2",
        "source": "Cloud Weekly",
        "published": "2026-02-13",
    },
]

# Create provider (keywords are used at the editorial level, not individual articles)
keywords = config["ai"]["keywords"]
provider = SimpleBarista()

print(f"\nProcessing {len(articles)} articles with keywords: {keywords}")
print("\nNote: With SimpleBarista, the functionality is demonstrated but AI providers")
print("      will use these keywords to focus their summary generation.\n")

# Process articles
processed_articles = []
for article in articles:
    result = provider.generate_summary(article)
    out = article.copy()
    out["ai_title"] = result["title"]
    out["ai_summary"] = result["summary"]
    processed_articles.append(out)

for i, article in enumerate(processed_articles, 1):
    print(f"\n[{i}] {article['ai_title']}")
    print(f"    Source: {article['source']}")
    print(f"    Summary: {article['ai_summary']}")
    print(f"    Link: {article['link']}")

# Example 4: How keywords and prompts affect AI behavior
print("\n" + "=" * 80)
print("Example 4: How keywords and prompts affect AI behavior")
print("=" * 80)

test_article = {
    "title": "Technology Breakthrough in Quantum Computing",
    "summary": "Scientists demonstrate a new approach to quantum error correction that could enable practical quantum computers.",
}

# Without keywords
prompt_no_keywords = _build_prompt(test_article, None)
print("\n--- Prompt WITHOUT keywords ---")
print(prompt_no_keywords)

# With keywords
test_keywords = ["quantum computing", "technology", "research"]
prompt_with_keywords = _build_prompt(test_article, test_keywords)
print("\n--- Prompt WITH keywords ---")
print(prompt_with_keywords)

# Note: Single article prompts are no longer used in MoKa News
# AI processing is now focused on editorial generation only
print("\n--- NOTE ---")
print("Custom prompts for individual articles are no longer supported.")
print("MoKa News now focuses AI processing only on editorial generation.")

print("\n" + "=" * 80)
print("Summary")
print("=" * 80)
print("""
Keywords help customize editorial AI behavior:
1. Add keywords to your moka-news.yaml configuration file
2. Keywords are used during editorial generation (not individual articles)
3. The AI will prioritize these topics when generating editorials
4. Keywords are optional - the system works fine without them
5. Great for customizing editorial content to your interests!

Editorial Prompts customization:
6. Editorial prompts can be customized in config files  
7. Use placeholders: {content}, {keywords}
8. Customize system_message, user_prompt, keywords_section, format_section
9. Edit the 'ai.editorial_prompts' section in ~/.config/moka-news/config.yaml
10. Default editorial prompts work great for most users

Poster generation:
11. Poster rendering is local/deterministic (no GenAI prompt for posters)
12. Poster body is extracted from the first editorial paragraph
13. Configure poster style via template settings under 'poster'
14. See examples/poster_example.py for a full walkthrough
""")
