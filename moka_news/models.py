"""
Data models for MoKa News.

Provides typed dataclasses to replace the implicit dictionaries used throughout
the codebase. Every model includes a ``to_dict()`` helper for backward
compatibility with code that still expects plain dicts.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dict for backward compatibility."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Article":
        """Create an Article from a plain dict (ignoring unknown keys)."""
        known = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in known})


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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dict for backward compatibility."""
        return {
            "title": self.title,
            "content": self.content,
            "timestamp": self.timestamp,
            "sources": [asdict(s) for s in self.sources],
            "article_count": self.article_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Editorial":
        """Create an Editorial from a plain dict."""
        sources_raw = data.get("sources", [])
        sources = [
            EditorialSource(**s) if isinstance(s, dict) else s for s in sources_raw
        ]
        return cls(
            title=data.get("title", "Good Morning!"),
            content=data.get("content", ""),
            timestamp=data.get("timestamp", datetime.now()),
            sources=sources,
            article_count=data.get("article_count", 0),
        )


# ---------------------------------------------------------------------------
# Editorial metadata (for listing saved editorials)
# ---------------------------------------------------------------------------


@dataclass
class EditorialMetadata:
    """Lightweight metadata for a saved editorial file."""

    title: str = "Untitled"
    timestamp: datetime = field(default_factory=datetime.now)
    filepath: Optional[Path] = None
    filename: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dict for backward compatibility."""
        return {
            "title": self.title,
            "timestamp": self.timestamp,
            "filepath": self.filepath,
            "filename": self.filename,
        }
