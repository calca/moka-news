"""
The Barista - Content Processing
Individual articles are returned as-is. AI processing is invoked only for editorial
generation (when prompts are passed via kwargs).
"""

import os
import subprocess
from typing import Dict, Any, Optional, List
from abc import ABC
from moka_news.logger import get_logger
from moka_news.constants import (
    DEFAULT_AI_MODELS,
    MAX_CONTENT_LENGTH,
    MAX_TOKENS,
    SUMMARY_TRUNCATE_LENGTH,
    TITLE_MAX_LENGTH,
    CLI_GENERATION_TIMEOUT,
)

logger = get_logger(__name__)

# Higher token limit for editorial generation (400-600 word articles need ~2k tokens)
EDITORIAL_MAX_TOKENS = 4096


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


def _build_prompt(
    article: Dict[str, Any],
    keywords: Optional[list] = None,
    prompts: Optional[Dict[str, str]] = None,
    max_content_length: int = MAX_CONTENT_LENGTH,
) -> str:
    """Build a textual prompt from *article*, optional *keywords* and *prompts*.

    This is a utility kept for backward compatibility and testing.
    """
    title = article.get("title", "")
    content = article.get("summary", "")[:max_content_length]

    if prompts and "user_prompt" in prompts:
        prompt = prompts["user_prompt"].replace("{title}", title).replace("{content}", content)
    else:
        prompt = f"Title: {title}\nContent: {content}"

    if keywords:
        kw_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
        if prompts and "keywords_section" in prompts:
            prompt += prompts["keywords_section"].replace("{keywords}", kw_str)
        else:
            prompt += f"\nKeywords: {kw_str}"

    if prompts and "format_section" in prompts:
        prompt += prompts["format_section"]

    return prompt


class AIProvider(ABC):
    """Abstract base class for AI providers.

    Individual articles are passed through without AI processing.
    When *prompts* is supplied via ``generate_summary(**kwargs)`` the provider
    enters **editorial mode**: it assembles the full prompt, calls the AI
    back-end (API or CLI) via ``_invoke_ai``, and parses the ``TITLE:`` line
    plus the following paragraph (or ``SUMMARY:`` when present).
    """

    # ── public interface ────────────────────────────────────────────────

    def generate_summary(
        self,
        article: Dict[str, Any],
        max_content_length: int = MAX_CONTENT_LENGTH,
        max_tokens: int = MAX_TOKENS,
        **kwargs,
    ) -> Dict[str, str]:
        """Generate a summary for *article*.

        When called **without** ``prompts`` the article is returned as-is
        (pass-through for individual articles).

        When ``prompts`` is provided (editorial generation) the method
        assembles the full editorial prompt, invokes the AI back-end and
        parses the response.

        Args:
            article: Article dictionary with title, link, summary.
            max_content_length: Maximum characters of content to include.
            max_tokens: Maximum tokens for AI response.
            **kwargs: ``prompts`` (dict) and ``keywords`` (list[str]) for
                      editorial generation.

        Returns:
            Dictionary with ``title`` and ``summary`` keys.
        """
        prompts = kwargs.get("prompts")
        keywords = kwargs.get("keywords", [])

        if prompts:
            return self._generate_editorial(article, prompts, keywords, max_tokens)

        # Pass-through mode for individual articles
        return {
            "title": article.get("title", "No Title")[:TITLE_MAX_LENGTH],
            "summary": (
                article.get("summary", "No summary available.")[:SUMMARY_TRUNCATE_LENGTH]
                if article.get("summary")
                else "No summary available."
            ),
        }

    # ── editorial helpers ───────────────────────────────────────────────

    def _generate_editorial(
        self,
        article: Dict[str, Any],
        prompts: Dict[str, str],
        keywords: List[str],
        max_tokens: int,
    ) -> Dict[str, str]:
        """Build the editorial prompt, call the AI and parse the result."""

        system_message = prompts.get("system_message", "")
        user_prompt = prompts.get("user_prompt", "").replace(
            "{content}", article.get("summary", "")
        )

        if keywords:
            kw_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
            keywords_section = prompts.get("keywords_section", "").replace(
                "{keywords}", kw_str
            )
            user_prompt += keywords_section

        user_prompt += prompts.get("format_section", "")

        editorial_max = max(max_tokens, EDITORIAL_MAX_TOKENS)

        try:
            response_text = self._invoke_ai(system_message, user_prompt, editorial_max)
            return self._parse_editorial_response(response_text)
        except NotImplementedError:
            logger.warning(
                "AI invocation not implemented for %s – returning raw content",
                self.__class__.__name__,
            )
            return {
                "title": "Your Morning News",
                "summary": article.get("summary", "No content available."),
            }

    def _invoke_ai(
        self, system_message: str, user_prompt: str, max_tokens: int = EDITORIAL_MAX_TOKENS
    ) -> str:
        """Call the AI model. Subclasses override this for their back-end."""
        raise NotImplementedError

    @staticmethod
    def _parse_editorial_response(text: str) -> Dict[str, str]:
        """Parse editorial AI output into ``title`` and ``summary``."""
        title = "Your Morning News"
        summary = text

        if "TITLE:" not in text:
            return {"title": title, "summary": summary}

        after_title_marker = text.split("TITLE:", 1)[1].lstrip()
        lines = after_title_marker.splitlines()
        if not lines:
            return {"title": title, "summary": summary}

        title = lines[0].strip() or title
        remainder = "\n".join(lines[1:]).strip()

        # Backward compatibility for legacy format:
        # TITLE: ...
        # SUMMARY: ...
        if remainder.startswith("SUMMARY:"):
            summary = remainder.split("SUMMARY:", 1)[1].strip()
            return {"title": title, "summary": summary}

        # New format:
        # TITLE: ...
        #
        # <first paragraph of body>
        paragraphs = [p.strip() for p in remainder.split("\n\n") if p.strip()]
        if paragraphs:
            summary = paragraphs[0]
        else:
            summary = remainder or summary

        return {"title": title, "summary": summary}


# ── API-based providers ────────────────────────────────────────────────


class OpenAIBarista(AIProvider):
    """OpenAI-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )

    def _invoke_ai(self, system_message: str, user_prompt: str, max_tokens: int = EDITORIAL_MAX_TOKENS) -> str:
        response = self.client.chat.completions.create(
            model=DEFAULT_AI_MODELS.get("openai", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content


class AnthropicBarista(AIProvider):
    """Anthropic-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            import anthropic
            self.client = anthropic.Anthropic(
                api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
            )
        except ImportError:
            raise ImportError(
                "anthropic package is required. Install with: pip install anthropic"
            )

    def _invoke_ai(self, system_message: str, user_prompt: str, max_tokens: int = EDITORIAL_MAX_TOKENS) -> str:
        response = self.client.messages.create(
            model=DEFAULT_AI_MODELS.get("anthropic", "claude-3-haiku-20240307"),
            max_tokens=max_tokens,
            system=system_message,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text


class GeminiBarista(AIProvider):
    """Google Gemini-based content processor (API key)"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel(
                DEFAULT_AI_MODELS.get("gemini", "gemini-pro")
            )
        except ImportError:
            raise ImportError(
                "google-generativeai package is required. Install with: pip install google-generativeai"
            )

    def _invoke_ai(self, system_message: str, user_prompt: str, max_tokens: int = EDITORIAL_MAX_TOKENS) -> str:
        full_prompt = f"{system_message}\n\n{user_prompt}"
        response = self.model.generate_content(full_prompt)
        return response.text


class MistralBarista(AIProvider):
    """Mistral AI-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            from mistralai.client import MistralClient

            self.client = MistralClient(
                api_key=api_key or os.getenv("MISTRAL_API_KEY")
            )
        except ImportError:
            raise ImportError(
                "mistralai package is required. Install with: pip install mistralai"
            )

    def _invoke_ai(self, system_message: str, user_prompt: str, max_tokens: int = EDITORIAL_MAX_TOKENS) -> str:
        from mistralai.models.chat_completion import ChatMessage

        response = self.client.chat(
            model=DEFAULT_AI_MODELS.get("mistral", "mistral-tiny"),
            messages=[
                ChatMessage(role="system", content=system_message),
                ChatMessage(role="user", content=user_prompt),
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content


# ── Simple (no-AI) provider ───────────────────────────────────────────


class SimpleBarista(AIProvider):
    """Simple non-AI processor for testing without API keys"""
    pass  # inherits generate_summary pass-through from AIProvider


# ── CLI-based providers ────────────────────────────────────────────────


class _CLIBarista(AIProvider):
    """Base class for CLI-based AI providers.

    Runs the CLI command as a subprocess, sending the full prompt via stdin
    and reading the AI-generated text from stdout.
    """

    cli_command: str = ""  # override in subclasses

    def _invoke_ai(self, system_message: str, user_prompt: str, max_tokens: int = EDITORIAL_MAX_TOKENS) -> str:
        full_prompt = f"{system_message}\n\n{user_prompt}"
        try:
            result = subprocess.run(
                [self.cli_command],
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=max(CLI_GENERATION_TIMEOUT, 120),
            )
            if result.returncode != 0:
                error_msg = result.stderr.strip() or f"{self.cli_command} exited with code {result.returncode}"
                raise RuntimeError(f"{self.cli_command} CLI error: {error_msg}")
            output = result.stdout.strip()
            if not output:
                raise RuntimeError(f"{self.cli_command} returned empty output")
            return output
        except FileNotFoundError:
            raise RuntimeError(
                f"'{self.cli_command}' CLI not found on PATH. "
                f"Make sure it is installed and accessible."
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"'{self.cli_command}' CLI timed out after {max(CLI_GENERATION_TIMEOUT, 120)}s"
            )


class GitHubCopilotCLIBarista(_CLIBarista):
    """GitHub Copilot CLI-based content processor"""
    cli_command = "copilot"


class GeminiCLIBarista(_CLIBarista):
    """Gemini CLI-based content processor"""
    cli_command = "gemini"


class MistralCLIBarista(_CLIBarista):
    """Mistral CLI-based content processor"""
    cli_command = "mistral"


class Barista:
    """Main Barista class that coordinates AI processing"""

    def __init__(self, provider: Optional[AIProvider] = None, keywords: Optional[list] = None, prompts: Optional[Dict[str, str]] = None, max_content_length: int = MAX_CONTENT_LENGTH, max_tokens: int = MAX_TOKENS):
        """
        Initialize the Barista (articles are no longer AI-processed)

        Args:
            provider: AI provider instance (defaults to SimpleBarista)
            keywords: Optional list of keywords for editorial generation
            prompts: Optional custom prompts (kept for compatibility)
            max_content_length: Maximum characters of content to include (unused)
            max_tokens: Maximum tokens for AI response (unused)
        """
        self.provider = provider or SimpleBarista()
        self.keywords = keywords or []
        self.prompts = prompts
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
        "copilot-cli": GitHubCopilotCLIBarista,
        "gemini-cli": GeminiCLIBarista,
        "mistral-cli": MistralCLIBarista,
        "simple": SimpleBarista,
    }

    if provider_name not in provider_map:
        logger.warning(f"Unknown AI provider: {provider_name}, defaulting to simple")
        return SimpleBarista()

    provider_class = provider_map[provider_name]

    if provider_name in ["openai", "anthropic", "gemini", "mistral"]:
        api_key = api_keys.get(provider_name)
        try:
            return provider_class(api_key=api_key)
        except ImportError as e:
            logger.warning(f"Cannot create {provider_name} provider: {e}. Falling back to simple.")
            return SimpleBarista()
    else:
        return provider_class()


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
