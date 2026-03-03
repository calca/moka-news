"""Reusable widgets for the Cup TUI."""

import webbrowser
from typing import Dict, Any

from textual.app import ComposeResult
from textual.widgets import Static, Label, Markdown, Collapsible


class ArticleCard(Static):
    """Widget to display a single article"""

    def __init__(self, article: Dict[str, Any], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.article = article
        self.border_title = article.get("source", "Unknown Source")

    def compose(self) -> ComposeResult:
        title = self.article.get("ai_title", self.article.get("title", "No Title"))
        summary = self.article.get(
            "ai_summary", self.article.get("summary", "No summary available.")
        )
        link = self.article.get("link", "")
        published = self.article.get("published", "")

        yield Label(f"[bold cyan]{title}[/bold cyan]")
        yield Label(f"\n{summary}")
        if published:
            yield Label(f"\n[dim]{published}[/dim]")
        if link:
            yield Label("[dim]🔗 Click card to open link[/dim]")

    def on_click(self) -> None:
        link = self.article.get("link")
        if link:
            try:
                webbrowser.open(link)
            except Exception as e:
                self.app.notify(f"Could not open link: {e}", severity="error")


class EditorialView(Static):
    """Widget to display the morning editorial with collapsible sources"""

    def __init__(self, editorial_content: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editorial_content = editorial_content
        self._parse_editorial()

    def _parse_editorial(self):
        """Parse editorial content to separate main content from sources"""
        if "## Sources" in self.editorial_content:
            parts = self.editorial_content.split("## Sources", 1)
            self.main_content = parts[0].rstrip()
            self.sources_content = parts[1].strip() if len(parts) > 1 else ""
        else:
            self.main_content = self.editorial_content
            self.sources_content = ""

    def compose(self) -> ComposeResult:
        yield Markdown(self.main_content)
        if self.sources_content:
            with Collapsible(title="📰 Sources", collapsed=True):
                yield Markdown(self.sources_content)
