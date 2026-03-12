"""Default configuration values for MoKa News."""

from typing import Any, Dict

from moka_news.constants import DEFAULT_TECH_FEEDS, MAX_CONTENT_LENGTH, MAX_TOKENS
from moka_news.paths import THEME_DARK, THEME_LIGHT


DEFAULT_EDITORIAL_PROMPTS: Dict[str, str] = {
    "system_message": (
        "You are a brilliant morning newspaper editor with a warm, conversational voice. "
        "You write editorials that feel like chatting with a well-informed friend over coffee — "
        "insightful yet approachable, sharp but never dry. You have a talent for weaving disparate "
        "news stories into a compelling narrative, finding the hidden threads that connect the day's "
        "events. Your prose is vivid, occasionally witty, and always respectful of your reader's "
        "intelligence and time. "
        "CRITICAL: You maintain this rich, flowing editorial style REGARDLESS of the number of articles provided. "
        "Even with just 2-3 articles, you write a comprehensive 400-600 word editorial with context, "
        "analysis, connections, and insights. You NEVER write brief summaries - you always craft "
        "a full, engaging editorial piece. "
        "IMPORTANT: You NEVER use bullet points, numbered lists, or any list formatting. "
        "Your writing flows as continuous prose, paragraph after paragraph, like a real newspaper editorial."
    ),
    "user_prompt": """Here are today's news articles fresh from the wire:

{content}

Craft a morning editorial that a reader will genuinely enjoy over their first cup of coffee. Follow these guidelines:

**Structure & Flow**
- Open with a strong, engaging hook — a striking detail, a bold observation, or a thought-provoking question that pulls the reader in immediately.
- Group related stories into thematic threads rather than listing them one by one. Find the connections: what common trends, tensions, or ironies tie the day's news together?
- Use smooth transitions between themes so the editorial reads as a single coherent piece, not a patchwork of summaries.
- Close with a memorable reflection, a forward-looking thought, or a touch of wit that leaves the reader thinking.

**Tone & Style**
- Write in a warm, conversational tone — as if you're a knowledgeable friend sharing the morning's most interesting developments.
- Be insightful and analytical: don't just report what happened, help the reader understand *why it matters*.
- Sprinkle in personality — an apt metaphor, a dry observation, a dash of humor where appropriate — but keep it elegant, never forced.
- Vary sentence rhythm: mix punchy short sentences with longer, flowing ones to keep the reading experience dynamic.
- MAINTAIN THIS DEPTH AND QUALITY EVEN WITH FEW ARTICLES: If you receive only 2-3 articles, still write a full 400-600 word editorial. Add context, historical perspective, connections to broader trends, and thoughtful analysis to reach the target length with substance.

**Content**
- Prioritize the most significant and interesting stories; not every article needs equal coverage.
- Provide enough context so readers feel informed without being overwhelmed.
- For each story or topic discussed, include a Markdown link to the original article so the reader can dive deeper (e.g., [Read more](url)). Use the article links provided in the input.
- Aim for approximately 400-600 words — substantial enough to be satisfying, concise enough to finish in one coffee.

**CRITICAL FORMATTING RULES**
- Write ONLY in flowing prose paragraphs. NEVER use bullet points (-, *, •), numbered lists (1., 2., 3.), or any list-based formatting.
- The editorial must read like a real newspaper article — continuous, fluid text that naturally guides the reader from one topic to the next.
- You may use Markdown headers (##) to separate major thematic sections, but within each section write in uninterrupted prose.
- Weave article links naturally into sentences (e.g., "as [reported by TechCrunch](url), the deal signals...") rather than appending them as a list.""",
    "keywords_section": """

Give special emphasis and deeper analysis to topics related to: {keywords}""",
    "format_section": """

Format your response as:
TITLE: <a crisp, evocative editorial title that captures the day's mood>
SUMMARY: <the full editorial content in Markdown, written in flowing prose with NO bullet points or numbered lists>""",
}


DEFAULT_CONFIG: Dict[str, Any] = {
    "ai": {
        "provider": "gemini-cli",  # Default AI provider - requires gcloud CLI
        "language": "en",  # Editorial language: en, it, es, fr
        "api_keys": {
            "openai": None,
            "anthropic": None,
            "gemini": None,
            "mistral": None,
            "azure": None,  # Azure AI API key (or AZURE_AI_API_KEY env var)
        },
        "azure_endpoint": None,  # Azure AI Foundry endpoint URL (or AZURE_AI_ENDPOINT env var)
        "azure_model": None,  # Deployed model name (or AZURE_AI_MODEL env var) — required for azure provider
        "azure_api_version": None,  # API version override; defaults to AZURE_AI_API_VERSION constant
        "keywords": [],  # Optional keywords for summary generation
        "editorial_prompts": DEFAULT_EDITORIAL_PROMPTS,  # Prompts for editorial generation
        "max_content_length": MAX_CONTENT_LENGTH,  # Maximum characters to send to AI for context
        "max_tokens": MAX_TOKENS,  # Maximum tokens for AI response
        "cli_timeout_seconds": 240,  # Timeout for CLI-based AI providers (copilot-cli/gemini-cli/mistral-cli)
    },
    "feeds": {
        "urls": [
            feed["url"] for feed in DEFAULT_TECH_FEEDS[:3]
        ]  # Internal fallback only — used when no OPML file exists and no --feeds CLI arg is provided.
        # Users should manage feeds via OPML: moka-news --add-feed / --remove-feed / --list-feeds
    },
    "ui": {
        "use_tui": True,
        "theme": THEME_DARK,  # Default theme (dark, relaxing)
        "theme_light": THEME_LIGHT,  # Light theme option
        "theme_dark": THEME_DARK,  # Dark theme option
    },
    "refresh": {
        "allowed_times": [
            "08:00"
        ],  # Single morning refresh to accumulate more articles overnight
        "max_daily_refreshes": 1,  # One refresh per day for richer editorial content
        "require_confirmation_outside_hours": True,  # Ask for confirmation outside allowed times
        "auto_refresh_window": 60,  # Time window in minutes around allowed times for automatic refresh
    },
    "editorial": {
        "editorials_dir": None,  # Directory to save editorials (defaults to ~/.config/moka-news/editorials)
        "min_articles": 10,  # Minimum number of articles needed for quality editorial generation
        "extended_window_days": 3,  # How many days to look back if initial fetch has too few articles
    },
    "poster": {
        "method": "local",  # Generation method: local (PIL/Pillow)
        "default_template": "story",  # Default template to use for poster generation
        "posters_dir": None,  # Directory to save posters (defaults to ~/.config/moka-news/posters)
        "templates_dir": None,  # Directory containing custom templates (defaults to package templates)
        "local": {
            "font_dirs": [],  # Additional directories to search for fonts
            "default_font": "arial",  # Default font family for text rendering
            "optimize_output": True,  # Optimize PNG output for smaller file sizes
            "add_watermark": True,  # Add MoKa News watermark to generated posters
        },
    },
    "publish": {
        "autosend": False,  # Auto-publish editorials after refresh in the TUI
        "providers": [],  # List of publish provider configs. Each entry needs "type" + provider-specific keys.
        # Supported types: "writeas", "buttondown"
    },
}


__all__ = ["DEFAULT_EDITORIAL_PROMPTS", "DEFAULT_CONFIG"]
