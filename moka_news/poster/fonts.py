"""Poster fonts — loading, platform fallback chains, and auto-sizing."""

from typing import List, Optional

try:
    from PIL import ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from moka_news.logger import get_logger
from moka_news.poster.text import wrap_text, split_paragraphs

logger = get_logger(__name__)

# Hard floor font size when text cannot fit at min_size
_HARD_FLOOR = 8


def load_font(
    font_file: Optional[str],
    font_family: str,
    size: int,
) -> "ImageFont.ImageFont":
    """
    Load a font with fallback chain:
    custom font → bundled font → system font → default.
    """
    if font_file:
        # Try bundled fonts directory
        try:
            import importlib.resources as pkg_resources
            try:
                fonts_path = pkg_resources.files("moka_news") / "fonts" / font_file
                if fonts_path.exists():
                    font = ImageFont.truetype(str(fonts_path), size)
                    logger.debug(f"Loaded bundled font: {font_file!r} @ {size}px")
                    return font
            except AttributeError:
                with pkg_resources.path("moka_news.fonts", font_file) as font_path:
                    if font_path.exists():
                        font = ImageFont.truetype(str(font_path), size)
                        logger.debug(f"Loaded bundled font (3.8): {font_file!r} @ {size}px")
                        return font
        except Exception as e:
            logger.debug(f"Could not load bundled font {font_file!r}: {e}")

        # Try as absolute path or relative to cwd
        try:
            from pathlib import Path
            font_path = Path(font_file)
            if font_path.exists():
                font = ImageFont.truetype(str(font_path), size)
                logger.debug(f"Loaded font from path: {font_path} @ {size}px")
                return font
        except Exception as e:
            logger.debug(f"Could not load font from path {font_file!r}: {e}")

    # Try system font
    try:
        font = ImageFont.truetype(font_family, size)
        logger.debug(f"Loaded system font: {font_family!r} @ {size}px")
        return font
    except Exception as e:
        logger.debug(f"Could not load system font {font_family!r}: {e}")

    # Try common TrueType fallbacks
    for candidate in _get_fallback_font_candidates(font_family):
        try:
            font = ImageFont.truetype(candidate, size)
            logger.debug(f"Loaded fallback TrueType font: {candidate!r} @ {size}px")
            return font
        except Exception:
            continue

    logger.warning(
        "Font fallback to PIL default (bitmap): "
        f"requested font_file={font_file!r}, font_family={font_family!r}, size={size}"
    )
    return ImageFont.load_default()


def _get_fallback_font_candidates(font_family: str) -> List[str]:
    """Return platform-friendly fallback font names/paths for scalable text."""
    family = (font_family or "").lower()
    candidates: List[str] = []

    if "times" in family or "serif" in family:
        candidates.extend([
            "Times New Roman.ttf",
            "Times.ttc",
            "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "DejaVuSerif.ttf",
        ])
    else:
        candidates.extend([
            "Arial.ttf",
            "Helvetica.ttc",
            "LiberationSans-Regular.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "DejaVuSans.ttf",
        ])

    candidates.extend([
        "Arial.ttf",
        "Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVuSans.ttf",
    ])

    unique: List[str] = []
    seen = set()
    for item in candidates:
        if item not in seen:
            seen.add(item)
            unique.append(item)

    return unique


# ---------------------------------------------------------------------------
# Unified font sizing
# ---------------------------------------------------------------------------

def fit_font_size(
    draw: "ImageDraw.ImageDraw",
    text: str,
    font_file: Optional[str],
    font_family: str,
    max_width: int,
    max_height: int,
    line_spacing: float = 1.3,
    min_size: int = 12,
    max_size: int = 220,
    *,
    single_line: bool = False,
    max_lines: int = 0,
    paragraph_mode: bool = False,
    paragraph_gap_factor: float = 0.4,
) -> int:
    """Unified binary-search for the largest font size that fits text.

    Modes (mutually exclusive flags):
      - **single_line=True**: text must fit in one line.
      - **max_lines > 0**: text may wrap up to *max_lines* lines.
      - **paragraph_mode=True**: text is split at blank lines and gaps
        between paragraphs are included in height measurement.
      - Default: wrapping with no line limit.
    """
    best: Optional[int] = None
    lo, hi = min_size, max_size

    while lo <= hi:
        mid = (lo + hi) // 2
        font = load_font(font_file, font_family, mid)
        fits = _check_fit(
            draw, text, font, max_width, max_height, line_spacing,
            single_line=single_line, max_lines=max_lines,
            paragraph_mode=paragraph_mode, paragraph_gap_factor=paragraph_gap_factor,
        )
        if fits:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1

    if best is not None:
        return best

    # Shrink below min_size down to hard floor
    for size in range(min_size - 1, _HARD_FLOOR - 1, -1):
        font = load_font(font_file, font_family, size)
        if _check_fit(
            draw, text, font, max_width, max_height, line_spacing,
            single_line=single_line, max_lines=max_lines,
            paragraph_mode=paragraph_mode, paragraph_gap_factor=paragraph_gap_factor,
        ):
            return size

    return _HARD_FLOOR


def _check_fit(
    draw: "ImageDraw.ImageDraw",
    text: str,
    font: "ImageFont.ImageFont",
    max_width: int,
    max_height: int,
    line_spacing: float,
    *,
    single_line: bool,
    max_lines: int,
    paragraph_mode: bool,
    paragraph_gap_factor: float,
) -> bool:
    """Return True if *text* fits the given constraints at *font*."""
    if single_line:
        bbox = draw.textbbox((0, 0), text, font=font)
        return (bbox[2] - bbox[0]) <= max_width and (bbox[3] - bbox[1]) <= max_height

    if paragraph_mode:
        paragraphs = split_paragraphs(text)
        if not paragraphs:
            return True
        total_h = _measure_wrapped_paragraphs(
            draw, paragraphs, font, max_width, line_spacing, paragraph_gap_factor,
        )
        return total_h <= max_height

    lines = wrap_text(draw, text, font, max_width)
    if max_lines > 0 and len(lines) > max_lines:
        return False

    total_h = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        total_h += int((bbox[3] - bbox[1]) * line_spacing)
    return total_h <= max_height


def _measure_wrapped_paragraphs(
    draw: "ImageDraw.ImageDraw",
    paragraphs: List[str],
    font: "ImageFont.ImageFont",
    max_width: int,
    line_spacing: float,
    paragraph_gap_factor: float = 0.4,
) -> int:
    """Measure total height for wrapped paragraphs including paragraph gaps."""
    if not paragraphs:
        return 0

    probe_bbox = draw.textbbox((0, 0), "Ag", font=font)
    base_line_h = max(1, probe_bbox[3] - probe_bbox[1])
    paragraph_gap_h = max(6, int(base_line_h * paragraph_gap_factor))

    total_h = 0
    for idx, paragraph in enumerate(paragraphs):
        lines = wrap_text(draw, paragraph, font, max_width)
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            total_h += int((bbox[3] - bbox[1]) * line_spacing)
        if idx < len(paragraphs) - 1:
            total_h += paragraph_gap_h
    return total_h
