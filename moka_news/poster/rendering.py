"""Poster rendering — gradient backgrounds, rounded boxes, and shadow effects."""

import re
from typing import Dict, Any, List

try:
    from PIL import Image, ImageDraw, ImageColor, ImageFilter

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from moka_news.constants import (
    DEFAULT_SHADOW_OFFSET,
    DEFAULT_SHADOW_BLUR,
)


def create_gradient_background(
    width: int,
    height: int,
    colors: List[str],
    gradient_type: str = "vertical",
) -> "Image.Image":
    """
    Create a gradient background image.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        colors: List of color hex strings (minimum 2)
        gradient_type: Type of gradient - "vertical" or "diagonal"

    Returns:
        PIL Image with gradient background
    """
    if not colors or len(colors) < 2:
        return Image.new("RGB", (width, height), colors[0] if colors else "#000000")

    rgb_colors = []
    for color in colors:
        try:
            rgb = ImageColor.getrgb(color)
            rgb_colors.append(rgb)
        except Exception:
            rgb_colors.append((0, 0, 0))

    img = Image.new("RGB", (width, height))

    if gradient_type == "diagonal":
        max_distance = (width**2 + height**2) ** 0.5
        for y in range(height):
            for x in range(width):
                distance = (x**2 + y**2) ** 0.5
                ratio = distance / max_distance
                color = _interpolate_colors(rgb_colors, ratio)
                img.putpixel((x, y), color)
    else:
        for y in range(height):
            ratio = y / height
            color = _interpolate_colors(rgb_colors, ratio)
            for x in range(width):
                img.putpixel((x, y), color)

    return img


def _interpolate_colors(colors: List[tuple], ratio: float) -> tuple:
    """Interpolate between multiple colors based on ratio (0-1)."""
    if len(colors) == 1:
        return colors[0]

    segment_count = len(colors) - 1
    segment = min(int(ratio * segment_count), segment_count - 1)
    local_ratio = (ratio * segment_count) - segment
    local_ratio = max(0.0, min(1.0, local_ratio))

    color1 = colors[segment]
    color2 = colors[segment + 1]

    r = int(color1[0] + (color2[0] - color1[0]) * local_ratio)
    g = int(color1[1] + (color2[1] - color1[1]) * local_ratio)
    b = int(color1[2] + (color2[2] - color1[2]) * local_ratio)

    return (r, g, b)


def draw_rounded_box_with_shadow(
    img: "Image.Image",
    position: tuple,
    size: tuple,
    radius: int,
    shadow_config: Dict[str, Any],
    fill_color: str,
) -> "Image.Image":
    """
    Draw a rounded rectangle box with shadow on the image.

    Args:
        img: Base image to draw on
        position: (x, y) top-left position of the box
        size: (width, height) of the box
        radius: Corner radius in pixels
        shadow_config: Dict with offset_x, offset_y, blur, color
        fill_color: Fill color for the box

    Returns:
        Modified image with box and shadow
    """
    x, y = position
    box_width, box_height = size

    shadow_offset_x = shadow_config.get("offset_x", DEFAULT_SHADOW_OFFSET)
    shadow_offset_y = shadow_config.get("offset_y", DEFAULT_SHADOW_OFFSET)
    shadow_blur = shadow_config.get("blur", DEFAULT_SHADOW_BLUR)
    shadow_color_str = shadow_config.get("color", "rgba(0,0,0,0.15)")

    try:
        if "rgba" in shadow_color_str:
            match = re.match(r"rgba\((\d+),(\d+),(\d+),([\d.]+)\)", shadow_color_str)
            if match:
                r_val, g_val, b_val, a_val = match.groups()
                shadow_color = (
                    int(r_val),
                    int(g_val),
                    int(b_val),
                    int(float(a_val) * 255),
                )
            else:
                shadow_color = (0, 0, 0, 38)
        else:
            rgb = ImageColor.getrgb(shadow_color_str)
            shadow_color = rgb + (38,)
    except Exception:
        shadow_color = (0, 0, 0, 38)

    shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)

    shadow_x = x + shadow_offset_x
    shadow_y = y + shadow_offset_y
    shadow_draw.rounded_rectangle(
        [shadow_x, shadow_y, shadow_x + box_width, shadow_y + box_height],
        radius=radius,
        fill=shadow_color,
    )

    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))

    if img.mode != "RGBA":
        img = img.convert("RGBA")
    img = Image.alpha_composite(img, shadow_layer)

    box_draw = ImageDraw.Draw(img)
    box_rgb = ImageColor.getrgb(fill_color)
    box_draw.rounded_rectangle(
        [x, y, x + box_width, y + box_height],
        radius=radius,
        fill=box_rgb,
    )

    return img
