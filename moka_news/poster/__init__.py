"""Poster package — generates shareable social images from editorial content."""

from moka_news.poster.template import PosterTemplate, PosterGenerationError
from moka_news.poster.generator import PosterGenerator
from moka_news.poster.rendering import (
    create_gradient_background as _create_gradient_background,
    _interpolate_colors,
    draw_rounded_box_with_shadow as _draw_rounded_box_with_shadow,
)

__all__ = [
    "PosterGenerator",
    "PosterGenerationError",
    "PosterTemplate",
    "_create_gradient_background",
    "_interpolate_colors",
    "_draw_rounded_box_with_shadow",
]
