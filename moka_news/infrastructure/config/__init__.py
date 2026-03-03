"""Configuration adapters in the infrastructure layer."""

from moka_news.infrastructure.config.defaults import (
    DEFAULT_CONFIG,
    DEFAULT_EDITORIAL_PROMPTS,
)
from moka_news.infrastructure.config.loader import (
    get_config_path,
    load_config,
    merge_configs,
)
from moka_news.infrastructure.config.sample import create_sample_config

__all__ = [
    "DEFAULT_CONFIG",
    "DEFAULT_EDITORIAL_PROMPTS",
    "get_config_path",
    "load_config",
    "merge_configs",
    "create_sample_config",
]
