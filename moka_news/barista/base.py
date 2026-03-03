"""Base classes and helpers for the Barista AI abstraction layer."""

import re
from typing import Dict, Any, Optional, List
from abc import ABC

from moka_news.logger import get_logger
from moka_news.constants import (
    EDITORIAL_MAX_TOKENS,
    MAX_CONTENT_LENGTH,
    MAX_TOKENS,
    SUMMARY_TRUNCATE_LENGTH,
    TITLE_MAX_LENGTH,
)

logger = get_logger(__name__)


def _get_article_text(
    article: Dict[str, Any], max_content_length: int = MAX_CONTENT_LENGTH
) -> str:
    """Get simple text representation of article (no AI prompts)."""
    return f"Title: {article['title']}\nContent: {article['summary'][:max_content_length]}"


def _build_prompt(
    article: Dict[str, Any],
    keywords: Optional[list] = None,
    prompts: Optional[Dict[str, str]] = None,
    max_content_length: int = MAX_CONTENT_LENGTH,
) -> str:
    """Build a textual prompt from *article*, optional *keywords* and *prompts*.

    Utility kept for backward compatibility and testing.
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
    back-end via ``_invoke_ai``, and parses the response.
    """

    def generate_summary(
        self,
        article: Dict[str, Any],
        max_content_length: int = MAX_CONTENT_LENGTH,
        max_tokens: int = MAX_TOKENS,
        **kwargs,
    ) -> Dict[str, str]:
        """Generate a summary for *article*.

        Without ``prompts`` the article is returned as-is (pass-through).
        With ``prompts`` the method assembles the editorial prompt, invokes
        the AI and parses the response.
        """
        prompts = kwargs.get("prompts")
        keywords = kwargs.get("keywords", [])

        if prompts:
            return self._generate_editorial(article, prompts, keywords, max_tokens)

        return {
            "title": article.get("title", "No Title")[:TITLE_MAX_LENGTH],
            "summary": (
                article.get("summary", "No summary available.")[:SUMMARY_TRUNCATE_LENGTH]
                if article.get("summary")
                else "No summary available."
            ),
        }

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
                "AI invocation not implemented for %s -- returning raw content",
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

        title_match = re.search(
            r"^\s*(?:\*\*)?TITLE(?:\*\*)?\s*:\s*(.+?)\s*$",
            text,
            flags=re.IGNORECASE | re.MULTILINE,
        )
        if not title_match:
            return {"title": title, "summary": summary}

        title = title_match.group(1).strip() or title
        remainder = text[title_match.end():].strip()

        remainder = re.sub(
            r"^\s*(?:\*\*)?SUMMARY(?:\*\*)?\s*:\s*",
            "",
            remainder,
            count=1,
            flags=re.IGNORECASE,
        )

        if not remainder:
            return {"title": title, "summary": summary}

        summary = remainder.strip() or summary
        return {"title": title, "summary": summary}
