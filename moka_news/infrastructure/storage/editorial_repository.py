"""Filesystem-backed repository for editorial markdown files."""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from moka_news.logger import get_logger
from moka_news.models import Editorial, EditorialMetadata, LoadedEditorial

logger = get_logger(__name__)


class EditorialRepository:
    """Persist and retrieve editorials from disk."""

    def __init__(self, editorials_dir: Path):
        self.editorials_dir = editorials_dir
        self.editorials_dir.mkdir(parents=True, exist_ok=True)

    def save(self, editorial: Editorial) -> Path:
        """Save editorial to markdown file and return path."""
        timestamp = editorial.timestamp
        filename = timestamp.strftime("%Y-%m-%d_%H-%M.md")
        filepath = self.editorials_dir / filename

        markdown = self.format_markdown(editorial)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown)

        return filepath

    def format_markdown(self, editorial: Editorial) -> str:
        """Render editorial dictionary as markdown."""
        timestamp = editorial.timestamp
        date_str = timestamp.strftime("%A, %B %d, %Y at %H:%M")

        md = f"# {editorial.title}\n\n"
        md += f"*{date_str}*\n\n"
        md += "---\n\n"
        md += editorial.content
        md += "\n\n---\n\n"
        md += "## Sources\n\n"

        for source in editorial.sources:
            title = source.title
            url = source.url
            source_name = source.source
            if url:
                md += f"- [**{title}**]({url}) - *{source_name}*\n\n"
            else:
                md += f"- **{title}** - *{source_name}*\n\n"

        md += f"\n*Editorial generated from {editorial.article_count} articles*\n"
        return md

    def list(self) -> List[EditorialMetadata]:
        """List saved editorials as metadata dictionaries."""
        editorials: List[EditorialMetadata] = []

        if not self.editorials_dir.exists():
            return editorials

        for filepath in sorted(self.editorials_dir.glob("*.md"), reverse=False):
            try:
                filename = filepath.stem
                timestamp = datetime.strptime(filename, "%Y-%m-%d_%H-%M")

                with open(filepath, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    title = (
                        first_line.replace("# ", "")
                        if first_line.startswith("# ")
                        else "Untitled"
                    )

                editorials.append(
                    EditorialMetadata(
                        title=title,
                        timestamp=timestamp,
                        filepath=filepath,
                        filename=filepath.name,
                    )
                )
            except Exception as exc:
                logger.warning("Error reading editorial %s: %s", filepath, exc)

        return editorials

    def load_most_recent(self) -> Optional[LoadedEditorial]:
        """Load the most recent saved editorial, when available."""
        editorials = self.list()
        if not editorials:
            return None

        most_recent = editorials[-1]
        return LoadedEditorial(
            filepath=most_recent.filepath,
            content=self.load(most_recent.filepath),
            title=most_recent.title,
        )

    @staticmethod
    def load(filepath: Path) -> str:
        """Load editorial markdown content from file."""
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
