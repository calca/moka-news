"""
Configuration management for MoKa News
Supports YAML configuration files for customization
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

DEFAULT_PROMPTS = {
    "system_message": "You are a news editor creating engaging titles and summaries.",
    "user_prompt": """Given this article:
Title: {title}
Content: {content}

Generate:
1. A concise, engaging title (max 80 characters)
2. A brief summary (max 200 characters)""",
    "keywords_section": """

Focus on these keywords/topics if relevant: {keywords}""",
    "format_section": """

Format as:
TITLE: <title>
SUMMARY: <summary>"""
}

DEFAULT_EDITORIAL_PROMPTS = {
    "system_message": "You are a skilled news editor creating an engaging morning editorial.",
    "user_prompt": """Create a cohesive morning news editorial from these articles:

{content}

Write an engaging editorial that:
1. Highlights the most important and relevant news
2. Connects related topics into a coherent narrative
3. Is enjoyable to read over morning coffee
4. Is approximately 300-500 words

Focus on creating a pleasant reading experience.""",
    "keywords_section": """

Pay special attention to topics related to: {keywords}""",
    "format_section": """

Format as:
TITLE: <engaging editorial title>
SUMMARY: <the editorial content>"""
}

DEFAULT_CONFIG = {
    "ai": {
        "provider": "openai",  # Changed from "simple" - AI is now default, simple is demo only
        "api_keys": {
            "openai": None,
            "anthropic": None,
            "gemini": None,
            "mistral": None,
        },
        "keywords": [],  # Optional keywords for summary generation
        "prompts": DEFAULT_PROMPTS,  # External prompts with placeholders
        "editorial_prompts": DEFAULT_EDITORIAL_PROMPTS,  # Prompts for editorial generation
    },
    "feeds": {
        "urls": [
            "https://news.ycombinator.com/rss",
            "https://www.reddit.com/r/programming/.rss",
            "https://github.blog/feed/",
        ]
    },
    "ui": {
        "use_tui": True,
        "theme": "rose-pine",  # Default theme (dark, relaxing)
        "theme_light": "rose-pine-dawn",  # Light theme option
        "theme_dark": "rose-pine",  # Dark theme option
    },
}


def get_config_path() -> Path:
    """
    Get the path to the configuration file

    Returns:
        Path to config file (checks multiple locations)
    """
    # Check in order: current directory, user home, package directory
    config_locations = [
        Path.cwd() / "moka-news.yaml",
        Path.cwd() / ".moka-news.yaml",
        Path.home() / ".config" / "moka-news" / "config.yaml",
        Path.home() / ".moka-news.yaml",
    ]

    for location in config_locations:
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
            print(f"⚠️  Warning: Could not load config file: {e}")

    # Override with environment variables
    if os.getenv("OPENAI_API_KEY"):
        config["ai"]["api_keys"]["openai"] = os.getenv("OPENAI_API_KEY")
    if os.getenv("ANTHROPIC_API_KEY"):
        config["ai"]["api_keys"]["anthropic"] = os.getenv("ANTHROPIC_API_KEY")
    if os.getenv("GEMINI_API_KEY"):
        config["ai"]["api_keys"]["gemini"] = os.getenv("GEMINI_API_KEY")
    if os.getenv("MISTRAL_API_KEY"):
        config["ai"]["api_keys"]["mistral"] = os.getenv("MISTRAL_API_KEY")

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
  provider: openai  # Options: openai, anthropic, gemini, mistral, copilot-cli, gemini-cli, mistral-cli
                     # Note: 'simple' mode is for demo/testing only (no AI summaries)
  
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
      2. A brief summary (max 200 characters)
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
    system_message: "You are a skilled news editor creating an engaging morning editorial."
    user_prompt: |
      Create a cohesive morning news editorial from these articles:

      {content}

      Write an engaging editorial that:
      1. Highlights the most important and relevant news
      2. Connects related topics into a coherent narrative
      3. Is enjoyable to read over morning coffee
      4. Is approximately 300-500 words

      Focus on creating a pleasant reading experience.
    keywords_section: |

      Pay special attention to topics related to: {keywords}
    format_section: |

      Format as:
      TITLE: <engaging editorial title>
      SUMMARY: <the editorial content>

# RSS Feed Configuration
feeds:
  urls:
    - https://news.ycombinator.com/rss
    - https://www.reddit.com/r/programming/.rss
    - https://github.blog/feed/

# UI Configuration
ui:
  use_tui: true  # Set to false to use console output instead of TUI
  theme: rose-pine  # Default theme (dark, relaxing) - see Textual themes
  theme_light: rose-pine-dawn  # Light theme option
  theme_dark: rose-pine  # Dark theme option
"""

    with open(path, "w") as f:
        f.write(sample_config)

    print(f"✓ Sample configuration created at: {path}")
