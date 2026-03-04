"""Sample configuration writer for MoKa News."""

def create_sample_config(path: str = "moka-news.yaml") -> None:
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
  cli_timeout_seconds: 240  # Timeout for CLI-based providers (copilot-cli, gemini-cli, mistral-cli)

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

__all__ = ["create_sample_config"]
