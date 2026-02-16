"""
The Barista - Content Processing (NO AI FOR INDIVIDUAL ARTICLES)
Individual articles are returned as-is, AI processing is only used for editorials
"""

import os
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from moka_news.logger import get_logger
from moka_news.constants import (
    DEFAULT_AI_MODELS,
    MAX_CONTENT_LENGTH,
    MAX_TOKENS,
    SUMMARY_TRUNCATE_LENGTH,
    TITLE_MAX_LENGTH,
)

logger = get_logger(__name__)


def _get_article_text(article: Dict[str, Any], max_content_length: int = MAX_CONTENT_LENGTH) -> str:
    """
    Get simple text representation of article (no AI prompts)
    
    Args:
        article: Article dictionary with title and summary
        max_content_length: Maximum characters of content to include
        
    Returns:
        Simple text representation
    """
    return f"Title: {article['title']}\nContent: {article['summary'][:max_content_length]}"


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    def generate_summary(self, article: Dict[str, Any], max_content_length: int = MAX_CONTENT_LENGTH, max_tokens: int = MAX_TOKENS, **kwargs) -> Dict[str, str]:
        """
        Generate a simple copy of article (no AI processing)

        Args:
            article: Article dictionary with title, link, summary
            max_content_length: Maximum characters of content to include
            max_tokens: Maximum tokens for AI response (unused)
            **kwargs: Additional keyword arguments (e.g., keywords, prompts)

        Returns:
            Dictionary with 'title' and 'summary' keys
        """
        pass


class OpenAIBarista(AIProvider):
    """OpenAI-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI provider

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        try:
            import openai

            self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )

    def generate_summary(self, article: Dict[str, Any], max_content_length: int = MAX_CONTENT_LENGTH, max_tokens: int = MAX_TOKENS, **kwargs) -> Dict[str, str]:
        """Return article as-is (no AI processing for individual articles)"""
        return {
            "title": article["title"][:TITLE_MAX_LENGTH], 
            "summary": article["summary"][:SUMMARY_TRUNCATE_LENGTH]
        }


class AnthropicBarista(AIProvider):
    """Anthropic-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Anthropic provider

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        try:
            import anthropic

            self.client = anthropic.Anthropic(
                api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
            )
        except ImportError:
            raise ImportError(
                "anthropic package is required. Install with: pip install anthropic"
            )

    def generate_summary(self, article: Dict[str, Any], max_content_length: int = MAX_CONTENT_LENGTH, max_tokens: int = MAX_TOKENS, **kwargs) -> Dict[str, str]:
        """Return article as-is (no AI processing for individual articles)"""
        return {
            "title": article["title"][:TITLE_MAX_LENGTH], 
            "summary": article["summary"][:SUMMARY_TRUNCATE_LENGTH]
        }


class GeminiBarista(AIProvider):
    """Google Gemini-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini provider

        Args:
            api_key: Google API key (defaults to GEMINI_API_KEY env var)
        """
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel("gemini-pro")
        except ImportError:
            raise ImportError(
                "google-generativeai package is required. Install with: pip install google-generativeai"
            )

    def generate_summary(self, article: Dict[str, Any], max_content_length: int = MAX_CONTENT_LENGTH, max_tokens: int = MAX_TOKENS, **kwargs) -> Dict[str, str]:
        """Return article as-is (no AI processing for individual articles)"""
        return {
            "title": article["title"][:TITLE_MAX_LENGTH], 
            "summary": article["summary"][:SUMMARY_TRUNCATE_LENGTH]
        }


class MistralBarista(AIProvider):
    """Mistral AI-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Mistral provider

        Args:
            api_key: Mistral API key (defaults to MISTRAL_API_KEY env var)
        """
        try:
            from mistralai.client import MistralClient

            self.client = MistralClient(api_key=api_key or os.getenv("MISTRAL_API_KEY"))
        except ImportError:
            raise ImportError(
                "mistralai package is required. Install with: pip install mistralai"
            )

    def generate_summary(self, article: Dict[str, Any], max_content_length: int = MAX_CONTENT_LENGTH, max_tokens: int = MAX_TOKENS, **kwargs) -> Dict[str, str]:
        """Return article as-is (no AI processing for individual articles)"""
        return {
            "title": article["title"][:TITLE_MAX_LENGTH], 
            "summary": article["summary"][:SUMMARY_TRUNCATE_LENGTH]
        }


class SimpleBarista(AIProvider):
    """Simple non-AI processor for testing without API keys"""

    def generate_summary(self, article: Dict[str, Any], max_content_length: int = MAX_CONTENT_LENGTH, max_tokens: int = MAX_TOKENS, **kwargs) -> Dict[str, str]:
        """Generate a simple summary by truncating the content"""
        return {
            "title": article.get("title", "No Title")[:TITLE_MAX_LENGTH],
            "summary": (
                article.get("summary", "No summary available.")[:SUMMARY_TRUNCATE_LENGTH]
                if article.get("summary")
                else "No summary available."
            ),
        }


class GitHubCopilotCLIBarista(AIProvider):
    """GitHub Copilot CLI-based content processor (no actual AI processing)"""

    def __init__(self):
        """Initialize GitHub Copilot CLI provider"""
        pass

    def generate_summary(self, article: Dict[str, Any], max_content_length: int = MAX_CONTENT_LENGTH, max_tokens: int = MAX_TOKENS, **kwargs) -> Dict[str, str]:
        """Return article as-is (no AI processing for individual articles)"""
        return {
            "title": article["title"][:TITLE_MAX_LENGTH], 
            "summary": article["summary"][:SUMMARY_TRUNCATE_LENGTH]
        }


class GeminiCLIBarista(AIProvider):
    """Gemini CLI-based content processor (no actual AI processing)"""

    def __init__(self):
        """Initialize Gemini CLI provider"""
        pass

    def generate_summary(self, article: Dict[str, Any], max_content_length: int = MAX_CONTENT_LENGTH, max_tokens: int = MAX_TOKENS, **kwargs) -> Dict[str, str]:
        """Return article as-is (no AI processing for individual articles)"""
        return {
            "title": article["title"][:TITLE_MAX_LENGTH], 
            "summary": article["summary"][:SUMMARY_TRUNCATE_LENGTH]
        }


class MistralCLIBarista(AIProvider):
    """Mistral CLI-based content processor (no actual AI processing)"""

    def __init__(self):
        """Initialize Mistral CLI provider"""
        pass

    def generate_summary(self, article: Dict[str, Any], max_content_length: int = MAX_CONTENT_LENGTH, max_tokens: int = MAX_TOKENS, **kwargs) -> Dict[str, str]:
        """Return article as-is (no AI processing for individual articles)"""
        return {
            "title": article["title"][:TITLE_MAX_LENGTH], 
            "summary": article["summary"][:SUMMARY_TRUNCATE_LENGTH]
        }


class Barista:
    """Main Barista class that coordinates AI processing"""

    def __init__(self, provider: Optional[AIProvider] = None, keywords: Optional[list] = None, max_content_length: int = MAX_CONTENT_LENGTH, max_tokens: int = MAX_TOKENS):
        """
        Initialize the Barista (articles are no longer AI-processed)

        Args:
            provider: AI provider instance (defaults to SimpleBarista)
            keywords: Optional list of keywords for editorial generation
            max_content_length: Maximum characters of content to include (unused)
            max_tokens: Maximum tokens for AI response (unused)
        """
        self.provider = provider or SimpleBarista()
        self.keywords = keywords or []
        self.max_content_length = max_content_length
        self.max_tokens = max_tokens

    def brew(self, articles: list) -> list:
        """
        Process a list of articles (no AI processing, returns articles as-is)

        Args:
            articles: List of article dictionaries

        Returns:
            List of articles with ai_title and ai_summary same as original
        """
        processed = []

        for article in articles:
            try:
                enhanced = self.provider.generate_summary(
                    article, 
                    self.max_content_length,
                    self.max_tokens
                )
                processed_article = article.copy()
                processed_article["ai_title"] = enhanced["title"]
                processed_article["ai_summary"] = enhanced["summary"]
                processed.append(processed_article)
            except Exception as e:
                logger.error(f"Error processing article: {e}", exc_info=True)
                article["ai_title"] = article["title"]
                article["ai_summary"] = article["summary"][:SUMMARY_TRUNCATE_LENGTH]
                processed.append(article)

        return processed


def create_ai_provider(provider_name: str, config: Dict[str, Any]) -> AIProvider:
    """
    Create an AI provider instance (no actual AI processing for articles)
    
    Args:
        provider_name: Name of AI provider ('openai', 'anthropic', 'gemini', 'mistral', 
                      'copilot-cli', 'gemini-cli', 'mistral-cli', 'simple')
        config: Configuration dictionary (unused)
    
    Returns:
        AI provider instance, always successful since no external dependencies
    """
    
    # All providers work the same now - no actual AI processing
    provider_map = {
        "openai": OpenAIBarista,
        "anthropic": AnthropicBarista,
        "gemini": GeminiBarista,
        "mistral": MistralBarista,
        "copilot-cli": GitHubCopilotCLIBarista,
        "gemini-cli": GeminiCLIBarista,
        "mistral-cli": MistralCLIBarista,
        "simple": SimpleBarista
    }
    
    if provider_name in provider_map:
        provider_class = provider_map[provider_name]
        if provider_name in ["openai", "anthropic", "gemini", "mistral"]:
            return provider_class(api_key=None)  # No API key needed since no AI processing
        else:
            return provider_class()
    
    # Unknown provider - default to simple
    logger.warning(f"Unknown AI provider: {provider_name}, defaulting to simple")
    return SimpleBarista()


def create_barista(
    provider_name: str,
    config: Dict[str, Any],
    max_content_length: int = MAX_CONTENT_LENGTH,
    max_tokens: int = MAX_TOKENS
) -> Barista:
    """
    Factory function to create a Barista (no AI processing for articles)
    
    Args:
        provider_name: Name of AI provider (all providers work the same now)
        config: Configuration dictionary
        max_content_length: Maximum characters of content to include (unused)
        max_tokens: Maximum tokens for AI response (unused)
    
    Returns:
        Configured Barista instance
    """
    logger.info(f"Creating barista with {provider_name} provider (no AI processing)")
    
    # Get AI provider instance (always works now)
    provider = create_ai_provider(provider_name, config)
    
    return Barista(provider, max_content_length, max_tokens)
