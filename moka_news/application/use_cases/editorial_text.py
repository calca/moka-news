"""Utilities for editorial markdown content."""

import re


_TITLE_MARKER_RE = re.compile(
    r"^\s*(?:\*\*)?TITLE(?:\*\*)?\s*:\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def extract_editorial_title(content: str) -> str:
    """Extract the best title from editorial markdown content."""
    text = content or ""

    match = _TITLE_MARKER_RE.search(text)
    if match:
        title = match.group(1).strip()
        if title:
            return title

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip() or "Morning Editorial"
        if stripped.startswith("## "):
            return stripped[3:].strip() or "Morning Editorial"

    return "Morning Editorial"
