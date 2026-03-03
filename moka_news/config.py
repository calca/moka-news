"""
Configuration management for MoKa News
Supports YAML configuration files for customization
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from moka_news.constants import DEFAULT_TECH_FEEDS, MAX_CONTENT_LENGTH, MAX_TOKENS, SUPPORTED_LANGUAGES
from moka_news.paths import CONFIG_SEARCH_LOCATIONS, THEME_DARK, THEME_LIGHT
from moka_news.logger import get_logger

logger = get_logger(__name__)



DEFAULT_EDITORIAL_PROMPTS = {
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

DEFAULT_CONFIG = {
    "ai": {
        "provider": "gemini-cli",  # Default AI provider - requires gcloud CLI
        "language": "en",  # Editorial language: en, it, es, fr
        "api_keys": {
            "openai": None,
            "anthropic": None,
            "gemini": None,
            "mistral": None,
        },
        "keywords": [],  # Optional keywords for summary generation
        "editorial_prompts": DEFAULT_EDITORIAL_PROMPTS,  # Prompts for editorial generation
        "max_content_length": MAX_CONTENT_LENGTH,  # Maximum characters to send to AI for context
        "max_tokens": MAX_TOKENS,  # Maximum tokens for AI response
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
        "allowed_times": ["08:00"],  # Single morning refresh to accumulate more articles overnight
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
            "add_watermark": True  # Add MoKa News watermark to generated posters
        }
    },
    "publish": {
        "providers": [],  # List of publish provider configs. Each entry needs "type" + provider-specific keys.
        # Supported types: "writeas", "buttondown"
    },
}


def get_config_path() -> Path:
    """
    Get the path to the configuration file

    Returns:
        Path to config file (checks multiple locations)
    """
    # Check in order: current directory, user config, user home
    for location in CONFIG_SEARCH_LOCATIONS:
        if location.exists():
            return location

    return None


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file

    Args:
        config_path: Optional path to config file. If not provided, searches default locations

    Returns:
        Configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()

    if config_path:
        config_file = Path(config_path)
    else:
        config_file = get_config_path()

    if config_file and config_file.exists():
        try:
            with open(config_file, "r") as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    # Deep merge user config with defaults
                    config = merge_configs(config, user_config)
        except Exception as e:
            logger.warning("Could not load config file: %s", e)

    # Override with environment variables
    if os.getenv("OPENAI_API_KEY"):
        config["ai"]["api_keys"]["openai"] = os.getenv("OPENAI_API_KEY")
    if os.getenv("ANTHROPIC_API_KEY"):
        config["ai"]["api_keys"]["anthropic"] = os.getenv("ANTHROPIC_API_KEY")
    if os.getenv("GEMINI_API_KEY"):
        config["ai"]["api_keys"]["gemini"] = os.getenv("GEMINI_API_KEY")
    if os.getenv("MISTRAL_API_KEY"):
        config["ai"]["api_keys"]["mistral"] = os.getenv("MISTRAL_API_KEY")
    # NOTE: Write.as env vars (WRITEAS_ALIAS, etc.) are read directly by
    # WriteAsPublisher at construction time — no config-level override needed.

    return config


def merge_configs(default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge user configuration with default configuration

    Args:
        default: Default configuration dictionary
        user: User configuration dictionary

    Returns:
        Merged configuration dictionary
    """
    result = default.copy()

    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def create_sample_config(path: str = "moka-news.yaml"):
    """
    Create a sample configuration file

    Args:
        path: Path where to create the sample config file
    """
    sample_config = """# MoKa News Configuration File
# Save this as 'moka-news.yaml' in your current directory or ~/.config/moka-news/config.yaml

# AI Provider Configuration
ai:
  provider: gemini-cli  # Options: openai, anthropic, gemini, mistral, copilot-cli, gemini-cli, mistral-cli
                        # Note: 'simple' mode is for demo/testing only (no AI summaries)
  
  # Editorial language (en = English, it = Italian, es = Spanish, fr = French)
  language: en
  
  # API Keys (can also be set via environment variables)
  # Only needed for API-based providers (not CLI providers)
  api_keys:
    openai: null      # or set OPENAI_API_KEY env var
    anthropic: null   # or set ANTHROPIC_API_KEY env var
    gemini: null      # or set GEMINI_API_KEY env var
    mistral: null     # or set MISTRAL_API_KEY env var
  
  # Keywords for summary generation (optional)
  # These keywords help focus the AI on specific topics or aspects
  keywords: []
    # Example:
    # - technology
    # - artificial intelligence
    # - programming
  
  # AI Prompts Configuration (optional)
  # You can customize the prompts used for AI summary generation
  # Use placeholders: {title}, {content}, {keywords}
  prompts:
    system_message: "You are a news editor creating engaging titles and summaries."
    user_prompt: |
      Given this article:
      Title: {title}
      Content: {content}

      Generate:
      1. A concise, engaging title (max 80 characters)
      2. A brief summary (approximately 200-250 characters)
    keywords_section: |

      Focus on these keywords/topics if relevant: {keywords}
    format_section: |

      Format as:
      TITLE: <title>
      SUMMARY: <summary>
  
  # Editorial Prompts Configuration (optional)
  # Customize the prompts used for generating morning editorials
  # Use placeholders: {content}, {keywords}
  editorial_prompts:
    system_message: >
      You are a brilliant morning newspaper editor with a warm, conversational voice.
      You write editorials that feel like chatting with a well-informed friend over coffee —
      insightful yet approachable, sharp but never dry. You weave disparate news stories
      into a compelling narrative, finding the hidden threads that connect the day's events.
    user_prompt: |
      Here are today's news articles fresh from the wire:

      {content}

      Craft a morning editorial that a reader will genuinely enjoy over their first cup of coffee.
      Open with a strong hook, group related stories into thematic threads, use smooth transitions,
      and close with a memorable reflection. Write in a warm, conversational tone — be insightful
      and analytical, with a touch of personality. For each story discussed, include a Markdown link
      to the original article so the reader can dive deeper. Aim for 400-600 words in Markdown format.
    keywords_section: |

      Give special emphasis and deeper analysis to topics related to: {keywords}
    format_section: |

      Format your response as:
      TITLE: <a crisp, evocative editorial title that captures the day's mood>
      SUMMARY: <the full editorial content in Markdown>
  
  # Token optimization settings
  max_content_length: 1500  # Maximum characters of article content to send to AI (default: 1500)
  max_tokens: 250           # Maximum tokens for AI to generate in response (default: 250)

# RSS Feed Configuration
# Feeds are managed via OPML, not this YAML file.
# Use the CLI to manage your feeds:
#   moka-news --add-feed URL      Add a feed
#   moka-news --remove-feed URL   Remove a feed
#   moka-news --list-feeds         List all feeds
# Feeds are stored in: ~/.config/moka-news/feeds.opml

# UI Configuration
ui:
  use_tui: true  # Set to false to use console output instead of TUI
  theme: rose-pine  # Default theme (dark, relaxing) - see Textual themes
  theme_light: rose-pine-dawn  # Light theme option
  theme_dark: rose-pine  # Dark theme option

# Refresh Configuration
refresh:
  allowed_times:
    - "08:00"  # Morning refresh time
    - "20:00"  # Evening refresh time
  max_daily_refreshes: 2  # Maximum number of refreshes per day
  require_confirmation_outside_hours: true  # Require confirmation for manual refresh outside allowed times
  auto_refresh_window: 60  # Time window in minutes around allowed times for automatic refresh

# Editorial Configuration
editorial:
  # Directory to save editorials (defaults to ~/.config/moka-news/editorials if not specified)
  editorials_dir: null
    # Example: ~/Documents/editorials
    # Example: /path/to/custom/editorials

# Poster Generation Configuration (press 'g' in TUI)
poster:
  method: local              # Generation method: local (PIL/Pillow)
  default_template: story    # Built-in template: story (create your own in templates_dir if needed)

# ── Publishing (press 'u' in TUI) ────────────────────────────
# All enabled providers execute when you publish.
# Each provider entry needs "type" plus provider-specific settings.

publish:
    providers:
        # Write.as
        # - type: writeas
        #   enabled: false
        #   api_base: https://write.as/api
        #   alias: null              # required (WRITEAS_ALIAS env var)
        #   pass: null               # required (WRITEAS_PASS env var)
        #   collection_alias: null   # optional (WRITEAS_COLLECTION_ALIAS env var)
        #   font: serif              # serif, sans, wrap, mono, code
        #   lang: null
        #   rtl: false
        #   timeout_seconds: 20
        #   verify_ssl: true

        # Buttondown Newsletter
        # - type: buttondown
        #   enabled: false
        #   api_key: null            # required (BUTTONDOWN_API_KEY env var)
        #   api_base: https://api.buttondown.com/v1
        #   status: draft            # draft or about_to_send
        #   email_type: public       # public or private
        #   timeout_seconds: 20
        #   verify_ssl: true
"""

    with open(path, "w") as f:
        f.write(sample_config)

    print(f"✓ Sample configuration created at: {path}")
