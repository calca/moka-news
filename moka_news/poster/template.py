"""Poster template — parses and holds poster template configuration."""

import json
from pathlib import Path
from typing import Dict, Any, List

from moka_news.constants import (
    DEFAULT_GRADIENT_PRESETS,
    DEFAULT_BOX_PADDING,
    DEFAULT_BOX_RADIUS,
    DEFAULT_SHADOW_OFFSET,
    DEFAULT_SHADOW_BLUR,
)


class PosterGenerationError(Exception):
    """Exception raised when poster generation fails"""
    pass


class PosterTemplate:
    """Represents a poster template configuration"""

    def __init__(self, template_data: Dict[str, Any]):
        """
        Initialize template from JSON data

        Args:
            template_data: Dictionary containing template configuration
        """
        self.name = template_data.get("name", "Unknown")
        self.description = template_data.get("description", "")

        # Layout settings
        layout = template_data.get("layout", {})
        self.width = layout.get("width", 1080)
        self.height = layout.get("height", 1080)
        self.padding = layout.get("padding", 60)
        self.line_spacing = layout.get("line_spacing", 1.2)

        # Color scheme
        colors = template_data.get("colors", {})
        self.background_color = colors.get("background", "#1e1e2e")
        self.text_color = colors.get("text", "#cdd6f4")
        self.accent_color = colors.get("accent", "#f38ba8")
        self.secondary_color = colors.get("secondary", "#89b4fa")

        # Gradient settings
        gradient = template_data.get("gradient", {})
        self.gradient_enabled = gradient.get("enabled", False)
        self.gradient_type = gradient.get("type", "vertical")
        self.gradient_colors = gradient.get("colors", [])
        self.gradient_preset = gradient.get("preset", None)

        if self.gradient_enabled and self.gradient_preset and not self.gradient_colors:
            self.gradient_colors = DEFAULT_GRADIENT_PRESETS.get(self.gradient_preset, [])

        # Content box settings
        content_box = template_data.get("content_box", {})
        self.content_box_enabled = content_box.get("enabled", False)
        self.content_box_background = content_box.get("background", "#ffffff")
        self.content_box_padding = content_box.get("padding", DEFAULT_BOX_PADDING)
        self.content_box_radius = content_box.get("border_radius", DEFAULT_BOX_RADIUS)

        # Shadow settings
        shadow = content_box.get("shadow", {})
        self.shadow_offset_x = shadow.get("offset_x", DEFAULT_SHADOW_OFFSET)
        self.shadow_offset_y = shadow.get("offset_y", DEFAULT_SHADOW_OFFSET)
        self.shadow_blur = shadow.get("blur", DEFAULT_SHADOW_BLUR)
        self.shadow_color = shadow.get("color", "rgba(0,0,0,0.15)")

        # Typography
        typography = template_data.get("typography", {})
        self.title_font_size = typography.get("title_size", 72)
        self.summary_font_size = typography.get("summary_size", 32)
        self.metadata_font_size = typography.get("metadata_size", 22)
        self.title_single_line = typography.get("title_single_line", False)
        self.title_max_lines = typography.get("title_max_lines", 0)
        self.title_min_size = typography.get(
            "title_min_size", max(20, int(self.title_font_size * 0.7))
        )
        self.title_max_size = typography.get("title_max_size", self.title_font_size)
        self.summary_min_size = typography.get(
            "summary_min_size", max(16, int(self.summary_font_size * 0.75))
        )
        self.summary_max_size = typography.get("summary_max_size", self.summary_font_size)
        self.font_family = typography.get("font_family", "arial")
        self.font_file = typography.get("font_file", None)
        self.bold_font_file = typography.get("bold_font_file", self.font_file)

        # Elements positioning
        elements = template_data.get("elements", {})
        self.show_qr_code = elements.get("qr_code", True)
        self.show_timestamp = elements.get("timestamp", True)
        self.show_source = elements.get("source", True)
        self.show_editorial_date = elements.get("editorial_date", True)
        self.show_logo = elements.get("logo", True)
        self.logo_position = elements.get("logo_position", "bottom_right")
        self.qr_position = elements.get("qr_position", "bottom_right")

    @classmethod
    def from_file(cls, template_path: Path) -> "PosterTemplate":
        """Load template from JSON file"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            return cls(template_data)
        except Exception as e:
            raise PosterGenerationError(f"Failed to load template from {template_path}: {e}")
