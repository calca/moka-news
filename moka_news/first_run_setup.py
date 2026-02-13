"""
First Run Setup - Interactive wizard for initial configuration
Handles AI provider selection and OPML feed initialization
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from moka_news.opml_manager import OPMLManager


# Suggested tech feeds for moka-cafè
SUGGESTED_TECH_FEEDS = [
    {
        "url": "https://news.ycombinator.com/rss",
        "title": "Hacker News",
        "htmlUrl": "https://news.ycombinator.com"
    },
    {
        "url": "https://github.blog/feed/",
        "title": "GitHub Blog",
        "htmlUrl": "https://github.blog"
    },
    {
        "url": "https://www.theverge.com/rss/index.xml",
        "title": "The Verge - Tech",
        "htmlUrl": "https://www.theverge.com"
    },
    {
        "url": "https://techcrunch.com/feed/",
        "title": "TechCrunch",
        "htmlUrl": "https://techcrunch.com"
    },
    {
        "url": "https://feeds.arstechnica.com/arstechnica/index",
        "title": "Ars Technica",
        "htmlUrl": "https://arstechnica.com"
    }
]

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
        "cli_command": "gh"
    },
    "gemini-cli": {
        "name": "Gemini CLI (gcloud)",
        "requires_api_key": False,
        "cli_required": True,
        "cli_command": "gcloud"
    },
    "mistral-cli": {
        "name": "Mistral CLI",
        "requires_api_key": False,
        "cli_required": True,
        "cli_command": "mistral"
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
    import shutil
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
    print("\nLet's set up your AI provider for news summaries.\n")
    print("Available AI providers:")
    
    # Display available providers
    available_providers = []
    for i, (key, provider) in enumerate(AI_PROVIDERS.items(), 1):
        # Check if CLI is available for CLI-based providers
        if provider.get("cli_required", False):
            cli_cmd = provider.get("cli_command")
            if cli_cmd and not check_cli_available(cli_cmd):
                continue  # Skip unavailable CLI providers
        
        available_providers.append(key)
        print(f"  [{i}] {provider['name']}")
        if provider.get("requires_api_key"):
            print(f"      (requires {provider['env_var']} environment variable)")
        elif provider.get("cli_required"):
            print(f"      (uses '{provider.get('cli_command')}' CLI - detected)")
    
    # Add demo/simple option
    print(f"  [{len(available_providers) + 1}] Simple mode (no AI, for demo/testing only)")
    
    # Get user choice
    while True:
        try:
            choice_str = input(f"\nSelect provider [1-{len(available_providers) + 1}]: ").strip()
            choice = int(choice_str)
            
            if choice == len(available_providers) + 1:
                # Simple mode selected
                print("\n⚠️  Note: Simple mode is for demo/testing only. No AI summaries will be generated.")
                confirm = input("Continue with simple mode? [y/N]: ").strip().lower()
                if confirm == 'y':
                    return {"provider": "simple", "api_key": None}
                else:
                    continue
            
            if 1 <= choice <= len(available_providers):
                selected_provider = available_providers[choice - 1]
                provider_info = AI_PROVIDERS[selected_provider]
                
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
                        print(f"   Please set it before running moka-news:")
                        print(f"   export {env_var}='your-api-key-here'")
                        result["api_key"] = None
                
                return result
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(available_providers) + 1}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n❌ Setup cancelled.")
            sys.exit(1)


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
    import yaml
    
    if config_path is None:
        config_path = Path.home() / ".config" / "moka-news" / "config.yaml"
    
    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare config content
    config_content = {
        "ai": {
            "provider": config_data["provider"],
            "api_keys": {
                "openai": None,
                "anthropic": None,
                "gemini": None,
                "mistral": None,
            }
        },
        "ui": {
            "use_tui": True
        }
    }
    
    # Save to file
    with open(config_path, 'w') as f:
        yaml.dump(config_content, f, default_flow_style=False, sort_keys=False)
    
    return config_path


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
    print("\nYou can now run: moka-news")
    print("=" * 60 + "\n")
    
    return {
        "provider": provider_config["provider"],
        "config_path": config_path,
        "feeds_configured": feeds_configured
    }
