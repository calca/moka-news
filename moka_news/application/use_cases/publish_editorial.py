"""Use-case for publishing editorial content."""

from typing import Any, List


def publish_editorial_content(
    publish_manager: Any,
    title: str,
    content: str,
) -> List[Any]:
    """Publish editorial content to all enabled providers."""
    return publish_manager.publish_all(title, content)
