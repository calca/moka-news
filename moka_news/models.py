"""Domain models for MoKa News."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, List, Mapping, Optional

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class MokaNewsError(Exception):
    """Base exception for all MoKa News errors."""


class GrinderError(MokaNewsError):
    """Raised when RSS feed parsing fails."""


class BaristaError(MokaNewsError):
    """Raised when AI provider encounters an error."""


class EditorialError(MokaNewsError):
    """Raised when editorial generation or I/O fails."""


class CupError(MokaNewsError):
    """Raised when the TUI encounters an error."""


class PosterError(MokaNewsError):
    """Raised when poster generation fails."""


# ---------------------------------------------------------------------------
# Article
# ---------------------------------------------------------------------------


@dataclass
class Article:
    """A single RSS article."""

    title: str = "No Title"
    link: str = ""
    summary: str = ""
    published: str = ""
    published_dt: Optional[datetime] = None
    source: str = ""
    ai_title: Optional[str] = None
    ai_summary: Optional[str] = None

    @property
    def display_title(self) -> str:
        """Return the best available title (AI → original)."""
        return self.ai_title or self.title or "No Title"

    @property
    def display_summary(self) -> str:
        """Return the best available summary (AI → original)."""
        return self.ai_summary or self.summary or "No summary available."

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "Article":
        """Create an Article from a generic mapping."""
        published_dt_raw = data.get("published_dt")
        published_dt = (
            published_dt_raw if isinstance(published_dt_raw, datetime) else None
        )
        return cls(
            title=str(data.get("title", "No Title")),
            link=str(data.get("link", "")),
            summary=str(data.get("summary", "")),
            published=str(data.get("published", "")),
            published_dt=published_dt,
            source=str(data.get("source", "")),
            ai_title=(
                str(data["ai_title"]) if data.get("ai_title") is not None else None
            ),
            ai_summary=(
                str(data["ai_summary"]) if data.get("ai_summary") is not None else None
            ),
        )


# ---------------------------------------------------------------------------
# Editorial
# ---------------------------------------------------------------------------


@dataclass
class EditorialSource:
    """A single source referenced in an editorial."""

    title: str = "Untitled"
    url: str = ""
    source: str = "Unknown"


@dataclass
class Editorial:
    """Generated editorial content."""

    title: str = "Good Morning!"
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    sources: List[EditorialSource] = field(default_factory=list)
    article_count: int = 0


@dataclass
class EditorialMetadata:
    """Lightweight metadata for a saved editorial file."""

    title: str
    timestamp: datetime
    filepath: Path
    filename: str


@dataclass
class LoadedEditorial:
    """Loaded editorial document with metadata."""

    filepath: Path
    content: str
    title: str = "Untitled"
