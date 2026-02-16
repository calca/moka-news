"""
First Run Setup - Interactive wizard for initial configuration
Handles AI provider selection and OPML feed initialization
"""

import os
import sys
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from moka_news.opml_manager import OPMLManager
from moka_news.constants import DEFAULT_TECH_FEEDS, SUPPORTED_LANGUAGES


# Suggested tech feeds for moka-cafè (directly use from constants)
SUGGESTED_TECH_FEEDS = DEFAULT_TECH_FEEDS

# AI provider configurations
AI_PROVIDERS = {
    "openai": {
        "name": "OpenAI (GPT models)",
        "requires_api_key": True,
        "env_var": "OPENAI_API_KEY",
        "cli_required": False
    },
    "anthropic": {
        "name": "Anthropic (Claude models)",
        "requires_api_key": True,
        "env_var": "ANTHROPIC_API_KEY",
        "cli_required": False
    },
    "gemini": {
        "name": "Google Gemini (API)",
        "requires_api_key": True,
        "env_var": "GEMINI_API_KEY",
        "cli_required": False
    },
    "mistral": {
        "name": "Mistral AI (API)",
        "requires_api_key": True,
        "env_var": "MISTRAL_API_KEY",
        "cli_required": False
    },
    "copilot-cli": {
        "name": "GitHub Copilot CLI",
        "requires_api_key": False,
        "cli_required": True,
        "cli_command": "copilot",
        "install_info": "Install: 'npm install -g @github/copilot-cli' then authenticate"
    },
    "gemini-cli": {
        "name": "Google Gemini CLI",
        "requires_api_key": False,
        "cli_required": True,
        "cli_command": "gemini",
        "install_info": "Install: 'pip install google-generativeai-cli' then authenticate"
    },
    "mistral-cli": {
        "name": "Mistral CLI",
        "requires_api_key": False,
        "cli_required": True,
        "cli_command": "mistral",
        "install_info": "Install: 'pip install mistralai-cli' then authenticate"
    }
}


def is_first_run() -> bool:
    """
    Check if this is the first run (no config file exists)
    
    Returns:
        True if this is the first run, False otherwise
    """
    config_locations = [
        Path.cwd() / "moka-news.yaml",
        Path.cwd() / ".moka-news.yaml",
        Path.home() / ".config" / "moka-news" / "config.yaml",
        Path.home() / ".moka-news.yaml",
    ]
    
    for location in config_locations:
        if location.exists():
            return False
    
    return True


def check_cli_available(command: str) -> bool:
    """
    Check if a CLI command is available in PATH
    
    Args:
        command: Command to check
        
    Returns:
        True if available, False otherwise
    """
    return shutil.which(command) is not None


def prompt_ai_provider() -> Dict[str, Any]:
    """
    Prompt user to select an AI provider
    
    Returns:
        Dictionary with provider selection and API key if needed
    """
    print("\n" + "=" * 60)
    print("☕ Welcome to MoKa News!")
    print("=" * 60)
    print("\nLet's set up your AI provider for generating morning editorials.\n")
    
    # Separate available and unavailable providers
    available_providers = []
    unavailable_providers = []
    
    print("🤖 Available AI Providers:")
    provider_index = 1
    
    for key, provider in AI_PROVIDERS.items():
        if provider.get("cli_required", False):
            cli_cmd = provider.get("cli_command")
            is_available = cli_cmd and check_cli_available(cli_cmd)
            
            if is_available:
                available_providers.append(key)
                print(f"  [{provider_index}] {provider['name']} ✅")
                print(f"      (uses '{cli_cmd}' CLI - detected and ready)")
                provider_index += 1
            else:
                unavailable_providers.append(key)
        else:
            # API-based provider
            available_providers.append(key)
            env_var = provider.get('env_var', '')
            has_key = os.getenv(env_var) is not None
            key_status = "✅ key found" if has_key else "⚠️ key needed"
            print(f"  [{provider_index}] {provider['name']} ({key_status})")
            print(f"      (requires {env_var} environment variable)")
            provider_index += 1
    
    # Show unavailable CLI providers with installation instructions
    if unavailable_providers:
        print(f"\n📥 CLI Providers (require installation):")
        start_index = len(available_providers) + 1
        
        for i, key in enumerate(unavailable_providers):
            provider = AI_PROVIDERS[key]
            cli_cmd = provider.get("cli_command")
            install_info = provider.get("install_info", f"Install '{cli_cmd}' CLI")
            
            available_providers.append(key)  # Add to selectable list
            print(f"  [{start_index + i}] {provider['name']} ❌")
            print(f"      ('{cli_cmd}' not found - {install_info})")
            provider_index += 1
    
    print(f"\n🧪 Testing Option:")
    simple_index = len(available_providers) + 1
    print(f"  [{simple_index}] Simple mode (no AI editorials, for demo/testing only)")
    
    # Get user choice
    while True:
        try:
            choice_str = input(f"\nSelect provider [1-{simple_index}]: ").strip()
            choice = int(choice_str)
            
            if choice == simple_index:
                # Simple mode selected
                print("\n⚠️  Note: Simple mode is for demo/testing only. No AI editorials will be generated.")
                confirm = input("Continue with simple mode? [y/N]: ").strip().lower()
                if confirm == 'y':
                    return {"provider": "simple", "api_key": None}
                else:
                    continue
            
            if 1 <= choice <= len(available_providers):
                selected_provider = available_providers[choice - 1]
                provider_info = AI_PROVIDERS[selected_provider]
                
                # Check if CLI is required but not available
                if provider_info.get("cli_required", False):
                    cli_cmd = provider_info.get("cli_command")
                    if not check_cli_available(cli_cmd):
                        print(f"\n❌ '{cli_cmd}' CLI is not installed.")
                        print(f"   {provider_info.get('install_info', f'Please install {cli_cmd}')}")
                        
                        install_choice = input(f"\nInstall '{cli_cmd}' now and try again? [y/N]: ").strip().lower()
                        if install_choice == 'y':
                            print(f"\n📋 Installation instructions for {provider_info['name']}:")
                            print(f"   {provider_info.get('install_info', f'Install {cli_cmd}')}")
                            print("\n   After installation, restart moka-news to try again.")
                            input("\nPress Enter when ready to continue setup...")
                            continue
                        else:
                            print("   Please select a different provider or install the CLI.")
                            continue
                
                result = {"provider": selected_provider}
                
                # Check if API key is needed
                if provider_info.get("requires_api_key"):
                    env_var = provider_info["env_var"]
                    existing_key = os.getenv(env_var)
                    
                    if existing_key:
                        print(f"\n✓ {env_var} found in environment")
                        result["api_key"] = existing_key
                    else:
                        print(f"\n⚠️  {env_var} not found in environment variables.")
                        print("   Please set it before running moka-news:")
                        print(f"   export {env_var}='your-api-key-here'")
                        result["api_key"] = None
                else:
                    print(f"\n✓ {provider_info['name']} configured successfully")
                
                return result
            else:
                print(f"Invalid choice. Please enter a number between 1 and {simple_index}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n❌ Setup cancelled.")
            sys.exit(1)


def prompt_keywords() -> list:
    """
    Prompt user to configure keywords for editorial focus
    
    Returns:
        List of keywords (empty if user skips)
    """
    print("\n" + "=" * 60)
    print("🔑 Keywords Configuration (Optional)")
    print("=" * 60)
    print("\nKeywords help focus AI editorial generation on topics you care about.")
    print("Examples: 'artificial intelligence', 'security', 'python', 'kubernetes'")
    print("\nYou can enter multiple keywords separated by commas.")
    
    while True:
        choice = input("\nConfigure keywords now? [y/N]: ").strip().lower()
        
        if choice in ['n', 'no', '']:
            print("\n⏭️  Skipping keywords configuration.")
            print("  You can add keywords later in your config file.")
            return []
        elif choice in ['y', 'yes']:
            keywords_input = input("\nEnter keywords (comma-separated): ").strip()
            if keywords_input:
                keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]
                if keywords:
                    print(f"\n✓ Keywords configured: {', '.join(keywords)}")
                    return keywords
                else:
                    print("\n⚠️  No valid keywords entered. Skipping.")
                    return []
            else:
                print("\n⚠️  No keywords entered. Skipping.")
                return []
        else:
            print("Please enter 'y' or 'n'.")


def prompt_language() -> str:
    """
    Prompt user to select the editorial language
    
    Returns:
        Language code (e.g. 'en', 'it', 'es', 'fr')
    """
    print("\n" + "=" * 60)
    print("🌍 Editorial Language")
    print("=" * 60)
    print("\nSelect the language for your morning editorials:\n")
    
    lang_list = list(SUPPORTED_LANGUAGES.items())
    for i, (code, name) in enumerate(lang_list, 1):
        default_marker = " (default)" if code == "en" else ""
        print(f"  [{i}] {name} ({code}){default_marker}")
    
    while True:
        try:
            choice_str = input(f"\nSelect language [1-{len(lang_list)}] (default: 1): ").strip()
            if choice_str == "":
                print("\n✓ Language set to: English")
                return "en"
            choice = int(choice_str)
            if 1 <= choice <= len(lang_list):
                code, name = lang_list[choice - 1]
                print(f"\n✓ Language set to: {name}")
                return code
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(lang_list)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n❌ Setup cancelled.")
            sys.exit(1)


def prompt_prompts_customization() -> bool:
    """
    Prompt user if they want to customize editorial AI prompts
    
    Returns:
        True if user wants to customize editorial prompts, False otherwise
    """
    print("\n" + "=" * 60)
    print("📝 Editorial AI Prompts Customization (Optional)")
    print("=" * 60)
    print("\nMoKa News uses AI to generate daily morning editorials from your collected articles.")
    print("You can use the default editorial prompts or customize them later.")
    print("\nDefault editorial prompts are well-tested and work great for most users.")
    print("Advanced users can customize editorial prompts in the config file using placeholders:")
    print("  - {content}: Combined content from all collected articles")
    print("  - {keywords}: Your configured keywords")
    
    while True:
        choice = input("\nUse default editorial prompts? [Y/n]: ").strip().lower()
        
        if choice in ['', 'y', 'yes']:
            print("\n✓ Using default editorial prompts.")
            print("  You can customize editorial prompts later in your config file.")
            print("  See the 'ai.editorial_prompts' section in ~/.config/moka-news/config.yaml")
            return False
        elif choice in ['n', 'no']:
            print("\n✓ You can customize editorial prompts after setup.")
            print("  Edit the 'ai.editorial_prompts' section in your config file:")
            print("  ~/.config/moka-news/config.yaml")
            print("\n  Available editorial prompts to customize:")
            print("    - system_message: AI system instructions for editorial writing")
            print("    - user_prompt: Main editorial generation template")
            print("    - keywords_section: Keywords integration for editorials")
            print("    - format_section: Editorial output format instructions")
            return True
        else:
            print("Please enter 'y' or 'n'.")


def prompt_opml_setup(opml_manager: OPMLManager) -> bool:
    """
    Prompt user to set up OPML feeds with suggestions
    
    Args:
        opml_manager: OPML manager instance
        
    Returns:
        True if feeds were set up, False otherwise
    """
    print("\n" + "=" * 60)
    print("📰 RSS Feed Configuration")
    print("=" * 60)
    print("\nWe recommend these 5 tech feeds for your moka-cafè:")
    
    for i, feed in enumerate(SUGGESTED_TECH_FEEDS, 1):
        print(f"  [{i}] {feed['title']}")
        print(f"      {feed['url']}")
    
    print(f"\nThese feeds will be saved to: {opml_manager.opml_path}")
    
    while True:
        choice = input("\nUse these suggested feeds? [Y/n]: ").strip().lower()
        
        if choice in ['', 'y', 'yes']:
            # Save suggested feeds
            opml_manager.save_feeds(SUGGESTED_TECH_FEEDS)
            print(f"\n✓ Feeds saved to: {opml_manager.opml_path}")
            print("  You can add more feeds later with: moka-news --add-feed URL")
            return True
        elif choice in ['n', 'no']:
            print("\n⚠️  No feeds configured.")
            print("  You can add feeds later with: moka-news --add-feed URL")
            print("  Or run with custom feeds: moka-news --feeds URL1 URL2")
            return False
        else:
            print("Please enter 'y' or 'n'.")


def save_config(config_data: Dict[str, Any], config_path: Optional[Path] = None) -> Path:
    """
    Save configuration to YAML file
    
    Args:
        config_data: Configuration dictionary
        config_path: Optional path to save config (defaults to ~/.config/moka-news/config.yaml)
        
    Returns:
        Path where config was saved
    """
    if config_path is None:
        config_path = Path.home() / ".config" / "moka-news" / "config.yaml"
    
    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare config content (editorial prompts are handled by default config)
    config_content = {
        "ai": {
            "provider": config_data["provider"],
            "language": config_data.get("language", "en"),
            "api_keys": {
                "openai": None,
                "anthropic": None,
                "gemini": None,
                "mistral": None,
            },
            "keywords": config_data.get("keywords", []),
        },
        "ui": {
            "use_tui": True
        }
    }
    
    # Save to file
    with open(config_path, 'w') as f:
        yaml.dump(config_content, f, default_flow_style=False, sort_keys=False)
    
    return config_path


def prompt_launch_now(provider_config: Dict[str, Any], feeds_configured: bool) -> bool:
    """
    Prompt user if they want to launch MoKa News immediately after setup
    
    Args:
        provider_config: AI provider configuration
        feeds_configured: Whether feeds were configured
        
    Returns:
        True if user wants to launch now, False otherwise
    """
    print("\n" + "=" * 60)
    print("🚀 Launch MoKa News")
    print("=" * 60)
    
    if not feeds_configured:
        print("⚠️  No RSS feeds configured. MoKa News will use default tech feeds.")
        
    # Check provider readiness
    provider = provider_config.get("provider")
    if provider == "simple":
        print("ℹ️  Using simple mode (no AI editorials).")
    elif provider in ["copilot-cli", "gemini-cli", "mistral-cli"]:
        print(f"ℹ️  Using {provider}. Make sure the CLI is installed and authenticated.")
    elif provider_config.get("api_key") is None:
        print(f"⚠️  {provider} API key not configured. Set environment variable first.")
        
    print("\nMoKa News will:")
    print("  1. 📰 Fetch RSS feeds")
    print("  2. ✍️  Generate morning editorial with AI")  
    print("  3. ☕ Launch beautiful TUI")
    
    while True:
        choice = input("\nLaunch MoKa News now? [Y/n]: ").strip().lower()
        
        if choice in ['', 'y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'.")


def launch_moka_news():
    """
    Launch MoKa News with the newly created configuration
    This reuses the main application logic
    """
    from moka_news.main import fetch_and_brew
    from moka_news.config import load_config
    from moka_news.cup import serve
    from moka_news.barista import create_ai_provider
    from moka_news.editorial import EditorialGenerator
    from moka_news.refresh_manager import RefreshManager
    from moka_news.download_tracker import DownloadTracker
    from datetime import datetime, time
    
    # Load the fresh configuration
    config = load_config()
    
    # Setup OPML manager
    opml_manager = OPMLManager()
    
    # Get feed URLs
    feed_urls = config.get("feeds", {}).get("urls", [])
    if not feed_urls:
        # Use default tech feeds if none configured
        from moka_news.constants import DEFAULT_TECH_FEEDS
        feed_urls = [feed["url"] for feed in DEFAULT_TECH_FEEDS[:3]]
    
    # Create AI provider
    ai_config = config.get("ai", {})
    provider_name = ai_config.get("provider", "gemini-cli")
    ai_provider = create_ai_provider(provider_name, config)
    
    if not ai_provider:
        print(f"⚠️  Could not initialize {provider_name} provider. Using SimpleBarista.")
        from moka_news.barista import SimpleBarista
        ai_provider = SimpleBarista()
    
    # Fetch and process articles
    print("📰 Fetching RSS feeds...")
    articles, last_update = fetch_and_brew(feed_urls, config, ai_provider)
    print(f"✓ Processed {len(articles)} articles")
    
    # Generate editorial
    print("✍️  Generating morning editorial...")
    ui_config = config.get("ui", {})
    editorial_config = config.get("editorial", {})
    refresh_config = config.get("refresh", {})
    
    editorial_generator = EditorialGenerator(
        ai_provider=ai_provider,
        keywords=ai_config.get("keywords", []),
        editorial_prompts=ai_config.get("editorial_prompts", {}),
        editorials_dir=editorial_config.get("editorials_dir"),
        language=ai_config.get("language", "en"),
    )
    
    try:
        editorial = editorial_generator.generate_editorial(articles)
        editorial_path = editorial_generator.save_editorial(editorial)
        editorial_content = editorial_generator.load_editorial(editorial_path)
        print(f"✓ Editorial generated and saved")
    except Exception as e:
        print(f"⚠️  Could not generate editorial: {e}")
        editorial_content = None
        editorial_path = None
    
    # Setup refresh manager
    refresh_manager = RefreshManager()
    allowed_times = refresh_config.get("allowed_times", ["08:00", "20:00"])
    refresh_manager.max_daily_refreshes = refresh_config.get("max_daily_refreshes", 2)
    refresh_manager.require_confirmation_outside_hours = refresh_config.get(
        "require_confirmation_outside_hours", True
    )
    
    # Convert time strings to time objects
    parsed_times = []
    for time_str in allowed_times:
        try:
            hour, minute = map(int, time_str.split(":"))
            parsed_times.append(time(hour, minute))
        except ValueError:
            print(f"⚠️  Invalid time format: {time_str}")
    
    if parsed_times:
        refresh_manager.allowed_refresh_times = parsed_times
    
    # Setup refresh callback
    def refresh_callback():
        download_tracker = DownloadTracker()
        new_articles, new_update = fetch_and_brew(feed_urls, config, ai_provider, download_tracker)
        return new_articles, new_update
    
    # Launch TUI
    print("☕ Launching TUI...")
    serve(
        articles,
        last_update,
        refresh_callback,
        editorial_content=editorial_content,
        editorial_generator=editorial_generator,
        theme=ui_config.get("theme", "rose-pine"),
        theme_light=ui_config.get("theme_light", "rose-pine-dawn"),
        theme_dark=ui_config.get("theme_dark", "rose-pine"),
        refresh_manager=refresh_manager,
        opener_command=editorial_config.get("opener_command"),
        current_editorial_path=editorial_path,
    )


def run_first_run_setup(opml_manager: OPMLManager) -> Dict[str, Any]:
    """
    Run the complete first-run setup wizard
    
    Args:
        opml_manager: OPML manager instance
        
    Returns:
        Dictionary with setup configuration
    """
    # Prompt for AI provider
    provider_config = prompt_ai_provider()
    
    # Prompt for language
    language = prompt_language()
    provider_config["language"] = language
    
    # Prompt for keywords
    keywords = prompt_keywords()
    provider_config["keywords"] = keywords
    
    # Prompt for prompts customization
    will_customize_prompts = prompt_prompts_customization()
    
    # Prompt for OPML setup
    feeds_configured = prompt_opml_setup(opml_manager)
    
    # Save configuration
    config_path = save_config(provider_config)
    
    print("\n" + "=" * 60)
    print("✓ Setup complete!")
    print("=" * 60)
    print(f"Configuration saved to: {config_path}")
    if feeds_configured:
        print(f"Feeds saved to: {opml_manager.opml_path}")
    if keywords:
        print(f"Keywords configured: {', '.join(keywords)}")
    lang_name = SUPPORTED_LANGUAGES.get(language, "English")
    print(f"Editorial language: {lang_name}")
    if will_customize_prompts:
        print("Editorial AI prompts: Can be customized in config file")
    else:
        print("Editorial AI prompts: Using defaults (can customize later)")
    
    # Ask if user wants to launch MoKa News now
    launch_now = prompt_launch_now(provider_config, feeds_configured)
    
    if launch_now:
        print("\n" + "=" * 60)
        print("🚀 Launching MoKa News...")
        print("=" * 60)
        try:
            launch_moka_news()
        except Exception as e:
            print(f"❌ Error launching MoKa News: {e}")
            print("You can launch it manually with: ./moka-news")
    else:
        print("\nYou can now run: ./moka-news or moka-news")
        print("=" * 60 + "\n")
    
    return {
        "provider": provider_config["provider"],
        "keywords": keywords,
        "config_path": config_path,
        "feeds_configured": feeds_configured,
        "launched": launch_now
    }
