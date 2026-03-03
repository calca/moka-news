"""Helpers for TUI refresh workflows."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple

from moka_news.models import Article


@dataclass
class RefreshOutcome:
    """Normalized output of a refresh cycle."""

    articles: List[Article]
    last_update: datetime
    editorial_path: Optional[Path] = None
    editorial_content: Optional[str] = None


def generate_editorial_artifacts(
    editorial_generator: Any,
    articles: List[Article],
) -> Tuple[Optional[Path], Optional[str]]:
    """Generate editorial markdown and return (path, content)."""
    editorial = editorial_generator.generate_editorial(articles)
    editorial_path = editorial_generator.save_editorial(editorial)
    editorial_content = editorial_generator.load_editorial(editorial_path)
    return editorial_path, editorial_content


def collect_refresh_outcome(
    refresh_callback: Callable[[], Tuple[List[Article], datetime]],
    editorial_generator: Optional[Any] = None,
) -> RefreshOutcome:
    """Execute refresh callback and optional editorial generation."""
    articles, last_update = refresh_callback()

    editorial_path: Optional[Path] = None
    editorial_content: Optional[str] = None

    if articles and editorial_generator is not None:
        editorial_path, editorial_content = generate_editorial_artifacts(
            editorial_generator,
            articles,
        )

    return RefreshOutcome(
        articles=articles,
        last_update=last_update,
        editorial_path=editorial_path,
        editorial_content=editorial_content,
    )
