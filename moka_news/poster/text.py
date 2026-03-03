"""Poster text processing — extraction, cleaning, rich-text parsing, and wrapping."""

import re
from typing import List, Optional, Tuple

try:
    from PIL import ImageDraw, ImageFont

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def extract_title_and_body(content: str) -> Tuple[Optional[str], str]:
    """Extract title from a leading ``TITLE:`` line and return remaining body."""
    raw = content or ""
    lines = raw.splitlines()
    title_re = re.compile(r"^\s*(?:\*\*)?TITLE(?:\*\*)?\s*:\s*(.+?)\s*$", re.IGNORECASE)
    summary_prefix_re = re.compile(
        r"^\s*(?:\*\*)?SUMMARY(?:\*\*)?\s*:\s*", re.IGNORECASE
    )

    for idx, line in enumerate(lines):
        stripped = line.strip()
        match = title_re.match(stripped)
        if not match:
            continue

        title = match.group(1).strip() or None
        remainder = "\n".join(lines[idx + 1 :]).lstrip()
        remainder = summary_prefix_re.sub("", remainder, count=1)
        return title, remainder

    return None, raw


def extract_poster_paragraph(markdown_content: str) -> str:
    """Extract and clean the first editorial paragraph for poster text."""
    content = markdown_content or ""

    if "\n## Sources" in content:
        content = content.split("\n## Sources", 1)[0]

    _, content = extract_title_and_body(content)

    for block in re.split(r"\n\s*\n", content):
        cleaned = clean_content_for_poster(block)
        if cleaned:
            return cleaned

    return "No editorial content available."


def clean_content_for_poster(content: str) -> str:
    """Clean a single paragraph for poster display."""
    raw = (content or "").strip()
    if not raw:
        return ""

    cleaned_lines: List[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "---":
            continue
        if stripped.startswith("#"):
            continue
        if re.match(
            r"^(?:\*\*)?(?:TITLE|SUMMARY)(?:\*\*)?\s*:", stripped, re.IGNORECASE
        ):
            continue
        if re.fullmatch(r"\*[^*]+\*", stripped):
            continue
        if stripped.startswith("- "):
            continue
        cleaned_lines.append(stripped)
    text = " ".join(cleaned_lines).strip()
    if not text:
        return ""

    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def format_body_for_readability(text: str) -> str:
    """Format body text to improve scanability — split sentences onto separate lines."""
    raw = (text or "").strip()
    if not raw:
        return ""

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw) if s.strip()]
    if not sentences:
        return raw

    return "\n\n".join(sentences)


def split_paragraphs(text: str) -> List[str]:
    """Split body text into cleaned paragraphs preserving blank-line boundaries."""
    if not text:
        return []
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def parse_rich_text(text: str) -> List[tuple]:
    """Parse ``**bold**`` markup into ``(segment_text, is_bold)`` tuples."""
    segments: List[tuple] = []
    pattern = re.compile(r"\*\*([^*]+)\*\*")
    last_end = 0
    for match in pattern.finditer(text):
        start, end = match.span()
        if start > last_end:
            segments.append((text[last_end:start], False))
        segments.append((match.group(1), True))
        last_end = end
    if last_end < len(text):
        segments.append((text[last_end:], False))
    return segments


def wrap_text(
    draw: "ImageDraw.ImageDraw",
    text: str,
    font: "ImageFont.ImageFont",
    max_width: int,
) -> List[str]:
    """Wrap text to fit within specified width."""
    words = text.split()
    lines: List[str] = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def truncate_single_line_text(
    draw: "ImageDraw.ImageDraw",
    text: str,
    font: "ImageFont.ImageFont",
    max_width: int,
) -> str:
    """Truncate text to a single line with ASCII ellipsis if needed."""
    raw = (text or "").strip()
    if not raw:
        return ""

    def text_width(value: str) -> int:
        bbox = draw.textbbox((0, 0), value, font=font)
        return int(bbox[2] - bbox[0])

    if text_width(raw) <= max_width:
        return raw

    suffix = "..."
    words = raw.split()
    while words:
        candidate = " ".join(words).rstrip()
        trial = f"{candidate}{suffix}"
        if text_width(trial) <= max_width:
            return trial
        words.pop()

    for idx in range(len(raw), 0, -1):
        trial = f"{raw[:idx].rstrip()}{suffix}"
        if text_width(trial) <= max_width:
            return trial

    return suffix if text_width(suffix) <= max_width else ""


def limit_wrapped_lines(
    draw: "ImageDraw.ImageDraw",
    text: str,
    font: "ImageFont.ImageFont",
    max_width: int,
    max_lines: int,
) -> List[str]:
    """Wrap text and truncate final line so output has at most max_lines."""
    lines = wrap_text(draw, text, font, max_width)
    if max_lines <= 0 or len(lines) <= max_lines:
        return lines

    head = lines[: max_lines - 1]
    tail_text = " ".join(lines[max_lines - 1 :]).strip()
    tail = truncate_single_line_text(draw, tail_text, font, max_width)
    return head + [tail]


def wrap_rich_lines(
    draw: "ImageDraw.ImageDraw",
    segments: List[tuple],
    regular_font: "ImageFont.ImageFont",
    bold_font: "ImageFont.ImageFont",
    max_width: int,
) -> List[List[tuple]]:
    """Wrap rich-text segments into pixel-constrained lines.

    Returns:
        List of lines. Each line is a list of ``(token_str, is_bold, font)``
        triples ready for rendering.
    """
    word_tokens: List[tuple] = []
    for seg_text, is_bold in segments:
        for word in seg_text.split():
            word_tokens.append((word, is_bold))

    lines: List[List[tuple]] = []
    current_line: List[tuple] = []
    current_width = 0

    for word, is_bold in word_tokens:
        font = bold_font if is_bold else regular_font
        display = (" " + word) if current_line else word
        bbox = draw.textbbox((0, 0), display, font=font)
        token_w = int(bbox[2] - bbox[0])

        if current_width + token_w <= max_width:
            current_line.append((display, is_bold, font))
            current_width += token_w
        else:
            if current_line:
                lines.append(current_line)
            current_line = [(word, is_bold, font)]
            bbox = draw.textbbox((0, 0), word, font=font)
            current_width = int(bbox[2] - bbox[0])

    if current_line:
        lines.append(current_line)

    return lines
