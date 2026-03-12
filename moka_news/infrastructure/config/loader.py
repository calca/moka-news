"""Configuration loading utilities for MoKa News."""

import copy
import os
from pathlib import Path
from typing import Any, Dict, Optional, cast

import yaml

from moka_news.infrastructure.config.defaults import DEFAULT_CONFIG
from moka_news.logger import get_logger
from moka_news.paths import CONFIG_SEARCH_LOCATIONS

logger = get_logger(__name__)


def get_config_path() -> Optional[Path]:
    """Get the path to the configuration file, if one exists."""
    for location in CONFIG_SEARCH_LOCATIONS:
        if location.exists():
            return location
    return None


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML and apply environment overrides."""
    config = copy.deepcopy(DEFAULT_CONFIG)

    config_file: Optional[Path]
    if config_path:
        config_file = Path(config_path)
    else:
        config_file = get_config_path()

    if config_file and config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f)
                if isinstance(user_config, dict):
                    config = merge_configs(config, user_config)
        except (OSError, yaml.YAMLError) as e:
            logger.warning("Could not load config file: %s", e)

    ai_config = cast(Dict[str, Any], config.setdefault("ai", {}))
    api_keys = cast(Dict[str, Any], ai_config.setdefault("api_keys", {}))
    if os.getenv("OPENAI_API_KEY"):
        api_keys["openai"] = os.getenv("OPENAI_API_KEY")
    if os.getenv("ANTHROPIC_API_KEY"):
        api_keys["anthropic"] = os.getenv("ANTHROPIC_API_KEY")
    if os.getenv("GEMINI_API_KEY"):
        api_keys["gemini"] = os.getenv("GEMINI_API_KEY")
    if os.getenv("MISTRAL_API_KEY"):
        api_keys["mistral"] = os.getenv("MISTRAL_API_KEY")
    if os.getenv("AZURE_AI_API_KEY"):
        api_keys["azure"] = os.getenv("AZURE_AI_API_KEY")
    if os.getenv("AZURE_AI_ENDPOINT"):
        ai_config["azure_endpoint"] = os.getenv("AZURE_AI_ENDPOINT")
    if os.getenv("AZURE_AI_MODEL"):
        ai_config["azure_model"] = os.getenv("AZURE_AI_MODEL")
    if os.getenv("AZURE_AI_API_VERSION"):
        ai_config["azure_api_version"] = os.getenv("AZURE_AI_API_VERSION")

    return config


def merge_configs(default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    """Deep-merge user config into defaults."""
    result = default.copy()

    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


__all__ = ["get_config_path", "load_config", "merge_configs"]
