"""
The Barista -- Content Processing

Individual articles are returned as-is.  AI processing is invoked only for
editorial generation (when prompts are passed via kwargs).

Sub-modules:
    base       -- AIProvider ABC, helper functions
    providers  -- Concrete provider implementations
"""

from typing import Dict, Any

from moka_news.logger import get_logger
from moka_news.barista.base import AIProvider, _get_article_text, _build_prompt
from moka_news.barista.providers import (
    OpenAIBarista,
    AnthropicBarista,
    GeminiBarista,
    MistralBarista,
    AzureAIBarista,
    SimpleBarista,
    GitHubCopilotCLIBarista,
    GeminiCLIBarista,
    MistralCLIBarista,
)

logger = get_logger(__name__)

__all__ = [
    "AIProvider",
    "OpenAIBarista",
    "AnthropicBarista",
    "GeminiBarista",
    "MistralBarista",
    "AzureAIBarista",
    "SimpleBarista",
    "GitHubCopilotCLIBarista",
    "GeminiCLIBarista",
    "MistralCLIBarista",
    "create_ai_provider",
    "_get_article_text",
    "_build_prompt",
]


def create_ai_provider(provider_name: str, config: Dict[str, Any]) -> AIProvider:
    """
    Create an AI provider instance.

    Individual articles are still passed through without AI.  The provider's
    ``_invoke_ai`` method is called only during editorial generation.

    Args:
        provider_name: Provider identifier.
        config: Full application configuration dictionary.

    Returns:
        AI provider instance.
    """
    ai_config = config.get("ai", {})
    api_keys = ai_config.get("api_keys", {})

    provider_map = {
        "openai": OpenAIBarista,
        "anthropic": AnthropicBarista,
        "gemini": GeminiBarista,
        "mistral": MistralBarista,
        "azure": AzureAIBarista,
        "copilot-cli": GitHubCopilotCLIBarista,
        "gemini-cli": GeminiCLIBarista,
        "mistral-cli": MistralCLIBarista,
        "simple": SimpleBarista,
    }

    if provider_name not in provider_map:
        logger.warning(f"Unknown AI provider: {provider_name}, defaulting to simple")
        return SimpleBarista()

    provider_class = provider_map[provider_name]

    if provider_name == "azure":
        api_key = api_keys.get("azure")
        endpoint = ai_config.get("azure_endpoint")
        model = ai_config.get("azure_model")
        api_version = ai_config.get("azure_api_version")
        try:
            return AzureAIBarista(
                api_key=api_key, endpoint=endpoint, model=model, api_version=api_version
            )
        except (ImportError, ValueError) as e:
            logger.warning("Cannot create azure provider: %s. Falling back to simple.", e)
            return SimpleBarista()

    if provider_name in ["openai", "anthropic", "gemini", "mistral"]:
        api_key = api_keys.get(provider_name)
        try:
            return provider_class(api_key=api_key)
        except ImportError as e:
            logger.warning(
                f"Cannot create {provider_name} provider: {e}. Falling back to simple."
            )
            return SimpleBarista()
    if provider_name in ["copilot-cli", "gemini-cli", "mistral-cli"]:
        timeout_seconds = ai_config.get("cli_timeout_seconds")
        if not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
            timeout_seconds = None
        return provider_class(timeout_seconds=timeout_seconds)

    if provider_name == "simple":
        return SimpleBarista()

    else:
        return provider_class()
