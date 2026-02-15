"""
Constants and configuration values for MoKa News
"""

# Default RSS feeds for tech news
DEFAULT_TECH_FEEDS = [
    {
        "url": "https://news.ycombinator.com/rss",
        "title": "Hacker News"
    },
    {
        "url": "https://github.blog/feed/",
        "title": "GitHub Blog"
    },
    {
        "url": "https://www.theverge.com/rss/index.xml",
        "title": "The Verge - Tech"
    },
    {
        "url": "https://techcrunch.com/feed/",
        "title": "TechCrunch"
    },
    {
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "title": "Ars Technica"
    }
]

# AI model names
DEFAULT_AI_MODELS = {
    "openai": "gpt-3.5-turbo",
    "anthropic": "claude-3-haiku-20240307",
    "gemini": "gemini-pro",
    "mistral": "mistral-tiny"
}

# Content processing limits
MAX_CONTENT_LENGTH = 1500  # Maximum characters of article content to process
MAX_TOKENS = 250  # Maximum tokens for AI response
SUMMARY_TRUNCATE_LENGTH = 200  # Length to truncate summaries for fallback
TITLE_MAX_LENGTH = 80  # Maximum length for titles

# Subprocess timeouts
CLI_VERSION_CHECK_TIMEOUT = 5  # Seconds to wait for CLI version checks
CLI_GENERATION_TIMEOUT = 30  # Seconds to wait for AI generation via CLI
