"""
Editorial Generator - Creates AI-powered morning news editorials
Combines multiple articles into a single coherent editorial with source links
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from moka_news.barista import AIProvider
from moka_news.constants import SUPPORTED_LANGUAGES
from moka_news.paths import APP_CONFIG_DIR, EDITORIALS_DIR, POSTERS_DIR
from moka_news.logger import get_logger

logger = get_logger(__name__)


class EditorialGenerator:
    """Generates AI-powered editorials from news articles"""

    def __init__(
        self,
        ai_provider: AIProvider,
        keywords: Optional[List[str]] = None,
        editorials_dir: Optional[Path] = None,
        editorial_prompts: Optional[Dict[str, str]] = None,
        language: str = "en",
    ):
        """
        Initialize the Editorial Generator

        Args:
            ai_provider: AI provider instance for generating editorial content
            keywords: Optional list of keywords to focus the editorial on
            editorials_dir: Directory to save editorials (defaults to ~/.config/moka-news/editorials)
            editorial_prompts: Optional dictionary of custom prompts for editorial generation
            language: Language code for editorial output (en, it, es, fr)
        """
        self.ai_provider = ai_provider
        self.keywords = keywords or []
        self.editorial_prompts = editorial_prompts
        self.language = language

        # Set config directory
        self.config_dir = APP_CONFIG_DIR

        # Set editorials directory
        if editorials_dir:
            self.editorials_dir = Path(editorials_dir)
        else:
            self.editorials_dir = EDITORIALS_DIR

        # Set posters directory
        self.posters_dir = POSTERS_DIR

        # Create directories if they don't exist
        self.editorials_dir.mkdir(parents=True, exist_ok=True)
        self.posters_dir.mkdir(parents=True, exist_ok=True)

        # Log configuration for debugging
        self._log_configuration()

    def _log_configuration(self):
        """Log the current configuration of the EditorialGenerator"""
        logger.info("EditorialGenerator configuration:")
        logger.info(f"  - Language: {self.language}")
        logger.info(f"  - Keywords: {self.keywords if self.keywords else 'None'}")
        logger.info(f"  - AI Provider: {self.ai_provider.__class__.__name__}")
        logger.info(
            f"  - Custom prompts: {'Yes' if self.editorial_prompts else 'No (using defaults)'}"
        )
        logger.info(f"  - Editorials directory: {self.editorials_dir}")
        logger.info(f"  - Posters directory: {self.posters_dir}")

    def generate_editorial(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate an editorial from a list of articles

        Args:
            articles: List of article dictionaries

        Returns:
            Dictionary containing the editorial content and metadata
        """
        logger.info(f"\n{'='*60}")
        logger.info("GENERATING EDITORIAL")
        logger.info(f"{'='*60}")
        logger.info(f"Number of articles: {len(articles)}")
        logger.info(f"Language: {self.language}")
        logger.info(
            f"Keywords: {', '.join(self.keywords) if self.keywords else 'None'}"
        )
        logger.info(f"AI Provider: {self.ai_provider.__class__.__name__}")
        logger.info(f"{'='*60}\n")

        if not articles:
            logger.warning("No articles provided for editorial generation")
            return {
                "title": "Good Morning!",
                "content": "No news articles available today.",
                "timestamp": datetime.now(),
                "sources": [],
                "article_count": 0,
            }

        # Build editorial prompt
        prompt = self._build_editorial_prompt(articles)

        # Create a pseudo-article for the AI provider
        editorial_article = {"title": "Morning Editorial", "summary": prompt}

        # Get prompts with language configuration
        editorial_prompts = self._get_editorial_prompts()
        logger.debug(f"Using editorial prompts with language: {self.language}")

        # Generate editorial content using AI
        try:
            result = self.ai_provider.generate_summary(
                editorial_article, keywords=self.keywords, prompts=editorial_prompts
            )

            editorial_content = result.get("summary", "")
            editorial_title = result.get("title", "Your Morning News")
            logger.info(f"Editorial generated successfully: {editorial_title}")

        except Exception as e:
            logger.error(f"Error generating editorial with AI: {e}")
            raise RuntimeError(f"Error generating editorial with AI: {e}") from e

        # Collect sources
        sources = []
        for article in articles:
            sources.append(
                {
                    "title": article.get("ai_title", article.get("title", "Untitled")),
                    "url": article.get("link", ""),
                    "source": article.get("source", "Unknown"),
                }
            )

        return {
            "title": editorial_title,
            "content": editorial_content,
            "timestamp": datetime.now(),
            "sources": sources,
            "article_count": len(articles),
        }

    def _build_editorial_prompt(self, articles: List[Dict[str, Any]]) -> str:
        """
        Build a prompt for editorial generation

        Args:
            articles: List of articles to include in the editorial

        Returns:
            Formatted prompt string
        """
        # Use all articles - they are already filtered by date
        # Use full AI summaries (already optimized) instead of truncating
        articles_text = ""
        for i, article in enumerate(articles, 1):
            title = article.get("ai_title", article.get("title", ""))
            summary = article.get("ai_summary", article.get("summary", ""))
            source = article.get("source", "Unknown")
            link = article.get("link", "")

            articles_text += f"{i}. {title}\n"
            articles_text += f"   Source: {source}\n"
            if link:
                articles_text += f"   Link: {link}\n"
            articles_text += f"   {summary}\n\n"

        return articles_text

    def _get_editorial_prompts(self) -> Dict[str, str]:
        """
        Get custom prompts for editorial generation, with language instruction injected.

        Returns:
            Dictionary of custom prompts for editorial generation
        """
        # Use configured prompts if provided, otherwise use defaults
        if self.editorial_prompts:
            prompts = dict(self.editorial_prompts)
        else:
            # Default prompts
            from moka_news.config import DEFAULT_EDITORIAL_PROMPTS

            prompts = dict(DEFAULT_EDITORIAL_PROMPTS)

        # Inject language instruction into system_message
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
                f"Injected language instruction for {language_name} into prompts"
            )

        return prompts

    def _create_simple_editorial(self, articles: List[Dict[str, Any]]) -> str:
        """
        Create a simple editorial without AI (fallback).

        Produces flowing prose rather than a numbered list so the output
        reads like a real newspaper editorial.

        Args:
            articles: List of articles

        Returns:
            Simple editorial text in Markdown
        """
        top = articles[:8]
        content = "Good morning — here's what's making headlines today.\n\n"

        for article in top:
            title = article.get("ai_title", article.get("title", "Untitled"))
            summary = article.get("ai_summary", article.get("summary", ""))[:200]
            link = article.get("link", "")
            source = article.get("source", "")

            if link:
                content += f"**{title}** — {summary} [Read more]({link})"
            else:
                content += f"**{title}** — {summary}"

            if source:
                content += f" *({source})*"
            content += "\n\n"

        content += "That's all for now — enjoy your coffee and have a great day.\n"
        return content

    def save_editorial(self, editorial: Dict[str, Any]) -> Path:
        """
        Save editorial to markdown file

        Args:
            editorial: Editorial dictionary from generate_editorial()

        Returns:
            Path to saved editorial file
        """
        timestamp = editorial["timestamp"]
        filename = timestamp.strftime("%Y-%m-%d_%H-%M.md")
        filepath = self.editorials_dir / filename

        # Format editorial as markdown
        markdown = self._format_editorial_markdown(editorial)

        # Save to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown)

        return filepath

    def _format_editorial_markdown(self, editorial: Dict[str, Any]) -> str:
        """
        Format editorial as markdown

        Args:
            editorial: Editorial dictionary

        Returns:
            Formatted markdown string
        """
        timestamp = editorial["timestamp"]
        date_str = timestamp.strftime("%A, %B %d, %Y at %H:%M")

        md = f"# {editorial['title']}\n\n"
        md += f"*{date_str}*\n\n"
        md += "---\n\n"
        md += editorial["content"]
        md += "\n\n---\n\n"
        md += "## Sources\n\n"

        for source in editorial["sources"]:
            title = source["title"]
            url = source["url"]
            source_name = source["source"]
            if url:
                md += f"- [**{title}**]({url}) - *{source_name}*\n\n"
            else:
                md += f"- **{title}** - *{source_name}*\n\n"

        md += f"\n*Editorial generated from {editorial['article_count']} articles*\n"

        return md

    def list_editorials(self) -> List[Dict[str, Any]]:
        """
        List all saved editorials

        Returns:
            List of editorial metadata dictionaries
        """
        editorials = []

        if not self.editorials_dir.exists():
            return editorials

        for filepath in sorted(self.editorials_dir.glob("*.md"), reverse=False):
            try:
                # Parse filename to get timestamp
                filename = filepath.stem
                timestamp = datetime.strptime(filename, "%Y-%m-%d_%H-%M")

                # Read first line as title
                with open(filepath, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    title = (
                        first_line.replace("# ", "")
                        if first_line.startswith("# ")
                        else "Untitled"
                    )

                editorials.append(
                    {
                        "title": title,
                        "timestamp": timestamp,
                        "filepath": filepath,
                        "filename": filepath.name,
                    }
                )
            except Exception as e:
                logger.warning("Error reading editorial %s: %s", filepath, e)

        return editorials

    def load_most_recent_editorial(self) -> Optional[Dict[str, Any]]:
        """
        Load the most recent saved editorial, if available.

        Returns:
            Dictionary with filepath and content, or None when no editorial exists.
        """
        editorials = self.list_editorials()
        if not editorials:
            return None

        most_recent = editorials[-1]  # list_editorials() returns oldest -> newest
        return {
            "filepath": most_recent["filepath"],
            "content": self.load_editorial(most_recent["filepath"]),
            "title": most_recent.get("title", "Untitled"),
        }

    def load_editorial(self, filepath: Path) -> str:
        """
        Load an editorial from file

        Args:
            filepath: Path to editorial markdown file

        Returns:
            Editorial content as markdown string
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
