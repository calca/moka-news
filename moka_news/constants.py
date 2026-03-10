"""
Constants and configuration values for MoKa News
"""

# Default RSS feeds for tech news
DEFAULT_TECH_FEEDS = [
    {
        "url": "https://news.ycombinator.com/rss",
        "title": "Hacker News",
        "htmlUrl": "https://news.ycombinator.com",
    },
    {
        "url": "https://github.blog/feed/",
        "title": "GitHub Blog",
        "htmlUrl": "https://github.blog",
    },
    {
        "url": "https://www.theverge.com/rss/index.xml",
        "title": "The Verge - Tech",
        "htmlUrl": "https://www.theverge.com",
    },
    {
        "url": "https://techcrunch.com/feed/",
        "title": "TechCrunch",
        "htmlUrl": "https://techcrunch.com",
    },
    {
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "title": "Ars Technica",
        "htmlUrl": "https://arstechnica.com",
    },
]

# AI model names
DEFAULT_AI_MODELS = {
    "openai": "gpt-3.5-turbo",
    "anthropic": "claude-3-haiku-20240307",
    "gemini": "gemini-pro",
    "mistral": "mistral-tiny",
    "azure": None,  # Must be set via ai.azure_model config or AZURE_AI_MODEL env var
}

AZURE_AI_API_VERSION = "2024-05-01-preview"  # Hardcoded default; override via ai.azure_api_version

# Content processing limits
MAX_CONTENT_LENGTH = 1500  # Maximum characters of article content to process
MAX_TOKENS = 250  # Maximum tokens for AI response
SUMMARY_TRUNCATE_LENGTH = 200  # Length to truncate summaries for fallback
TITLE_MAX_LENGTH = 80  # Maximum length for titles

# Supported languages for editorial generation
SUPPORTED_LANGUAGES = {
    "en": "English",
    "it": "Italian",
    "es": "Spanish",
    "fr": "French",
}

# Subprocess timeouts
CLI_VERSION_CHECK_TIMEOUT = 5  # Seconds to wait for CLI version checks
CLI_GENERATION_TIMEOUT = 30  # Seconds to wait for AI generation via CLI

# Higher token limit for editorial generation (400-600 word articles need ~2k tokens)
EDITORIAL_MAX_TOKENS = 4096

# Poster generation constants
POSTER_MAX_TOKENS = 300  # Maximum AI response tokens for poster content
DEFAULT_BOX_PADDING = 40  # Padding inside content box
DEFAULT_BOX_RADIUS = 20  # Border radius for rounded corners
DEFAULT_SHADOW_OFFSET = 4  # Shadow offset in pixels
DEFAULT_SHADOW_BLUR = 12  # Shadow blur radius

# Gradient color presets for posters
DEFAULT_GRADIENT_PRESETS = {
    "purple-pink": ["#6a0dad", "#ff69b4"],  # Purple to pink
    "ocean": ["#2e3192", "#1bffff"],  # Deep blue to cyan
    "sunset": ["#ff6b6b", "#feca57"],  # Red to yellow
    "forest": ["#0f4c5c", "#9bc472"],  # Dark teal to light green
    "lavender": ["#9d84b7", "#daa5a4"],  # Lavender to rose
    "mint": ["#4ecdc4", "#44e5b0"],  # Mint to seafoam
    "rose-pine": ["#eb6f92", "#c4a7e7"],  # Rose Pine rose to mauve
    "warm": ["#ee9ca7", "#ffdde1"],  # Warm pink gradient
}

# Bundled fonts for poster generation
BUNDLED_FONTS = [
    "Inter-Regular.ttf",
    "Inter-Bold.ttf",
    "Roboto-Regular.ttf",
    "Roboto-Bold.ttf",
    "OpenSans-Regular.ttf",
    "OpenSans-Bold.ttf",
]
