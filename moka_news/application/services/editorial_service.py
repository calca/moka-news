"""Service responsible for editorial generation logic."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from moka_news.barista import AIProvider
from moka_news.infrastructure.config.defaults import DEFAULT_EDITORIAL_PROMPTS
from moka_news.constants import SUPPORTED_LANGUAGES
from moka_news.logger import get_logger
from moka_news.models import Article, Editorial, EditorialSource

logger = get_logger(__name__)


class EditorialService:
    """Generate editorial content and metadata from a list of articles."""

    def __init__(
        self,
        ai_provider: AIProvider,
        keywords: Optional[List[str]] = None,
        editorial_prompts: Optional[Dict[str, str]] = None,
        language: str = "en",
    ):
        self.ai_provider = ai_provider
        self.keywords = keywords or []
        self.editorial_prompts = editorial_prompts
        self.language = language

    def log_configuration(self, editorials_dir: Path, posters_dir: Path) -> None:
        """Log service configuration details."""
        logger.info("EditorialGenerator configuration:")
        logger.info("  - Language: %s", self.language)
        logger.info("  - Keywords: %s", self.keywords if self.keywords else "None")
        logger.info("  - AI Provider: %s", self.ai_provider.__class__.__name__)
        logger.info(
            "  - Custom prompts: %s",
            "Yes" if self.editorial_prompts else "No (using defaults)",
        )
        logger.info("  - Editorials directory: %s", editorials_dir)
        logger.info("  - Posters directory: %s", posters_dir)

    def generate_editorial(self, articles: Sequence[Article]) -> Editorial:
        """Generate an editorial from article dictionaries."""
        logger.info("\n%s", "=" * 60)
        logger.info("GENERATING EDITORIAL")
        logger.info("%s", "=" * 60)
        logger.info("Number of articles: %d", len(articles))
        logger.info("Language: %s", self.language)
        logger.info(
            "Keywords: %s", ", ".join(self.keywords) if self.keywords else "None"
        )
        logger.info("AI Provider: %s", self.ai_provider.__class__.__name__)
        logger.info("%s\n", "=" * 60)

        if not articles:
            logger.warning("No articles provided for editorial generation")
            return Editorial(
                title="Good Morning!",
                content="No news articles available today.",
                timestamp=datetime.now(),
                sources=[],
                article_count=0,
            )

        prompt = self.build_editorial_prompt(articles)
        editorial_article = {"title": "Morning Editorial", "summary": prompt}

        editorial_prompts = self.get_editorial_prompts()
        logger.debug("Using editorial prompts with language: %s", self.language)

        try:
            result = self.ai_provider.generate_summary(
                editorial_article,
                keywords=self.keywords,
                prompts=editorial_prompts,
            )
            editorial_content = result.get("summary", "")
            editorial_title = result.get("title", "Your Morning News")
            logger.info("Editorial generated successfully: %s", editorial_title)
        except Exception as exc:
            logger.error("Error generating editorial with AI: %s", exc)
            raise RuntimeError(f"Error generating editorial with AI: {exc}") from exc

        sources: List[EditorialSource] = []
        for article in articles:
            sources.append(
                EditorialSource(
                    title=article.display_title or "Untitled",
                    url=article.link,
                    source=article.source or "Unknown",
                )
            )

        return Editorial(
            title=editorial_title,
            content=editorial_content,
            timestamp=datetime.now(),
            sources=sources,
            article_count=len(articles),
        )

    def build_editorial_prompt(self, articles: Sequence[Article]) -> str:
        """Build AI prompt text from articles."""
        articles_text = ""
        for i, article in enumerate(articles, 1):
            title = article.display_title
            summary = article.display_summary
            source = article.source or "Unknown"
            link = article.link

            articles_text += f"{i}. {title}\n"
            articles_text += f"   Source: {source}\n"
            if link:
                articles_text += f"   Link: {link}\n"
            articles_text += f"   {summary}\n\n"

        return articles_text

    def get_editorial_prompts(self) -> Dict[str, str]:
        """Return prompts with language instruction injected when needed."""
        prompts = (
            dict(self.editorial_prompts)
            if self.editorial_prompts
            else dict(DEFAULT_EDITORIAL_PROMPTS)
        )

        language_name = SUPPORTED_LANGUAGES.get(self.language, "English")
        if self.language != "en":
            language_instruction = (
                f" IMPORTANT: Write the ENTIRE editorial in {language_name}. "
                f"The title, all paragraphs, transitions, and closing remarks "
                f"must be written in {language_name}."
            )
            prompts["system_message"] = (
                prompts.get("system_message", "") + language_instruction
            )
            logger.info(
                "Injected language instruction for %s into prompts",
                language_name,
            )

        return prompts

    def create_simple_editorial(self, articles: Sequence[Article]) -> str:
        """Create a non-AI fallback editorial with simple prose."""
        top = articles[:8]
        content = "Good morning — here's what's making headlines today.\n\n"

        for article in top:
            title = article.display_title or "Untitled"
            summary = article.display_summary[:200]
            link = article.link
            source = article.source

            if link:
                content += f"**{title}** — {summary} [Read more]({link})"
            else:
                content += f"**{title}** — {summary}"

            if source:
                content += f" *({source})*"
            content += "\n\n"

        content += "That's all for now — enjoy your coffee and have a great day.\n"
        return content
