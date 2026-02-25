"""Poster Generator - Creates social posters from editorial content."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
try:
    from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

from moka_news.logger import get_logger
from moka_news.constants import (
    DEFAULT_GRADIENT_PRESETS,
    DEFAULT_BOX_PADDING,
    DEFAULT_BOX_RADIUS,
    DEFAULT_SHADOW_OFFSET,
    DEFAULT_SHADOW_BLUR,
)

logger = get_logger(__name__)


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
        
        # Gradient settings (new)
        gradient = template_data.get("gradient", {})
        self.gradient_enabled = gradient.get("enabled", False)
        self.gradient_type = gradient.get("type", "vertical")  # vertical or diagonal
        self.gradient_colors = gradient.get("colors", [])
        self.gradient_preset = gradient.get("preset", None)
        
        # Resolve gradient preset to colors
        if self.gradient_enabled and self.gradient_preset and not self.gradient_colors:
            self.gradient_colors = DEFAULT_GRADIENT_PRESETS.get(self.gradient_preset, [])
        
        # Content box settings (new)
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
        self.title_min_size = typography.get(
            "title_min_size", max(20, int(self.title_font_size * 0.7))
        )
        self.title_max_size = typography.get("title_max_size", self.title_font_size)
        self.summary_min_size = typography.get(
            "summary_min_size", max(16, int(self.summary_font_size * 0.75))
        )
        self.summary_max_size = typography.get("summary_max_size", self.summary_font_size)
        self.font_family = typography.get("font_family", "arial")
        self.font_file = typography.get("font_file", None)  # Custom font file
        self.bold_font_file = typography.get("bold_font_file", self.font_file)  # Bold variant, falls back to font_file
        
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


def _create_gradient_background(width: int, height: int, colors: List[str], gradient_type: str = "vertical") -> Image.Image:
    """
    Create a gradient background image
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        colors: List of color hex strings (minimum 2)
        gradient_type: Type of gradient - "vertical" or "diagonal"
        
    Returns:
        PIL Image with gradient background
    """
    if not colors or len(colors) < 2:
        # Fallback to solid color
        return Image.new("RGB", (width, height), colors[0] if colors else "#000000")
    
    # Convert hex colors to RGB tuples
    rgb_colors = []
    for color in colors:
        try:
            rgb = ImageColor.getrgb(color)
            rgb_colors.append(rgb)
        except:
            # Fallback for invalid color
            rgb_colors.append((0, 0, 0))
    
    # Create base image
    img = Image.new("RGB", (width, height))
    
    if gradient_type == "diagonal":
        # Diagonal gradient from top-left to bottom-right
        # Use the diagonal distance for smooth interpolation
        max_distance = (width**2 + height**2) ** 0.5
        
        for y in range(height):
            for x in range(width):
                # Calculate distance from top-left corner
                distance = (x**2 + y**2) ** 0.5
                # Normalize to 0-1
                ratio = distance / max_distance
                
                # Interpolate between colors
                color = _interpolate_colors(rgb_colors, ratio)
                img.putpixel((x, y), color)
    else:
        # Vertical gradient (top to bottom) - much faster
        for y in range(height):
            # Calculate interpolation ratio
            ratio = y / height
            
            # Interpolate between colors
            color = _interpolate_colors(rgb_colors, ratio)
            
            # Draw horizontal line
            for x in range(width):
                img.putpixel((x, y), color)
    
    return img


def _interpolate_colors(colors: List[tuple], ratio: float) -> tuple:
    """
    Interpolate between multiple colors based on ratio (0-1)
    
    Args:
        colors: List of RGB tuples
        ratio: Position in gradient (0-1)
        
    Returns:
        Interpolated RGB tuple
    """
    if len(colors) == 1:
        return colors[0]
    
    # Determine which two colors to interpolate between
    segment_count = len(colors) - 1
    segment = min(int(ratio * segment_count), segment_count - 1)
    
    # Calculate local ratio within the segment
    local_ratio = (ratio * segment_count) - segment
    local_ratio = max(0.0, min(1.0, local_ratio))
    
    # Get the two colors
    color1 = colors[segment]
    color2 = colors[segment + 1]
    
    # Linear interpolation
    r = int(color1[0] + (color2[0] - color1[0]) * local_ratio)
    g = int(color1[1] + (color2[1] - color1[1]) * local_ratio)
    b = int(color1[2] + (color2[2] - color1[2]) * local_ratio)
    
    return (r, g, b)


def _draw_rounded_box_with_shadow(
    img: Image.Image,
    position: tuple,
    size: tuple,
    radius: int,
    shadow_config: Dict[str, Any],
    fill_color: str
) -> Image.Image:
    """
    Draw a rounded rectangle box with shadow on the image
    
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
    
    # First, create the shadow layer
    shadow_offset_x = shadow_config.get("offset_x", DEFAULT_SHADOW_OFFSET)
    shadow_offset_y = shadow_config.get("offset_y", DEFAULT_SHADOW_OFFSET)
    shadow_blur = shadow_config.get("blur", DEFAULT_SHADOW_BLUR)
    shadow_color_str = shadow_config.get("color", "rgba(0,0,0,0.15)")
    
    # Parse shadow color (support rgba)
    try:
        if "rgba" in shadow_color_str:
            # Extract rgba values
            import re
            match = re.match(r'rgba\((\d+),(\d+),(\d+),([\d.]+)\)', shadow_color_str)
            if match:
                r, g, b, a = match.groups()
                shadow_color = (int(r), int(g), int(b), int(float(a) * 255))
            else:
                shadow_color = (0, 0, 0, 38)  # Default semi-transparent black
        else:
            rgb = ImageColor.getrgb(shadow_color_str)
            shadow_color = rgb + (38,)  # Add alpha
    except:
        shadow_color = (0, 0, 0, 38)
    
    # Create shadow layer
    shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    
    # Draw shadow (offset position)
    shadow_x = x + shadow_offset_x
    shadow_y = y + shadow_offset_y
    shadow_draw.rounded_rectangle(
        [shadow_x, shadow_y, shadow_x + box_width, shadow_y + box_height],
        radius=radius,
        fill=shadow_color
    )
    
    # Apply blur to shadow
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))
    
    # Composite shadow onto base image
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    img = Image.alpha_composite(img, shadow_layer)
    
    # Now draw the actual box on top
    box_draw = ImageDraw.Draw(img)
    box_rgb = ImageColor.getrgb(fill_color)
    box_draw.rounded_rectangle(
        [x, y, x + box_width, y + box_height],
        radius=radius,
        fill=box_rgb
    )
    
    return img


class PosterGenerator:
    """Generates shareable social posters from editorial content"""
    
    def __init__(
        self,
        config: Dict[str, Any],
        posters_dir: Optional[Path] = None,
        templates_dir: Optional[Path] = None
    ):
        """
        Initialize the Poster Generator
        
        Args:
            config: Poster configuration dictionary
            posters_dir: Directory to save posters (defaults to ~/.config/moka-news/posters)
            templates_dir: Directory containing template files
        """
        if not PIL_AVAILABLE:
            raise PosterGenerationError("Pillow library is required for poster generation. Install with: pip install Pillow")
        
        self.config = config
        
        # Set posters directory
        if posters_dir:
            self.posters_dir = Path(posters_dir)
        else:
            config_dir = Path.home() / ".config" / "moka-news"
            self.posters_dir = config_dir / "posters"
        
        # Set templates directory
        if templates_dir:
            self.templates_dir = Path(templates_dir)
        else:
            # Default to package templates directory
            package_dir = Path(__file__).parent
            self.templates_dir = package_dir / "templates"
        
        # Create directories if they don't exist
        self.posters_dir.mkdir(parents=True, exist_ok=True)
        if not self.templates_dir.exists():
            self._create_default_templates()
        
        # Configuration
        self.generation_method = "local"
        self.default_template = config.get("default_template", "story")
        self.logo_path_override = (
            config.get("logo_path")
            or config.get("local", {}).get("logo_path")
        )
        requested_method = config.get("method", "local")
        if requested_method != "local":
            logger.warning(
                "Poster method %r is no longer supported, using local rendering.",
                requested_method,
            )

        if self.default_template == "story":
            story_template = self.templates_dir / "story.json"
            if not story_template.exists():
                self._create_default_templates()
        
        logger.info(f"PosterGenerator initialized:")
        logger.info(f"  - Method: {self.generation_method}")
        logger.info(f"  - Default template: {self.default_template}")
        logger.info(f"  - Posters directory: {self.posters_dir}")
        logger.info(f"  - Templates directory: {self.templates_dir}")
    
    def _create_default_templates(self):
        """Create default template files if templates directory doesn't exist"""
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # Story template for vertical social formats (compact portrait 4:5)
        template = {
            "name": "Story",
            "description": "Vertical 4:5 layout optimized for readability",
            "layout": {
                "width": 1080,
                "height": 1350,
                "padding": 72,
                "line_spacing": 1.32
            },
            "gradient": {
                "enabled": True,
                "type": "vertical",
                "preset": "warm"
            },
            "content_box": {
                "enabled": True,
                "background": "#ffffff",
                "padding": 56,
                "border_radius": 24,
                "shadow": {
                    "offset_x": 6,
                    "offset_y": 6,
                    "blur": 16,
                    "color": "rgba(0,0,0,0.16)"
                }
            },
            "colors": {
                "background": "#111827",
                "text": "#1f2937",
                "accent": "#be123c",
                "secondary": "#475569"
            },
            "typography": {
                "title_size": 64,
                "summary_size": 34,
                "metadata_size": 22,
                "title_single_line": True,
                "title_min_size": 34,
                "title_max_size": 64,
                "summary_min_size": 12,
                "summary_max_size": 34,
                "font_family": "arial",
                "font_file": "OpenSans-Regular.ttf",
                "bold_font_file": "OpenSans-Bold.ttf"
            },
            "elements": {
                "qr_code": False,
                "timestamp": False,
                "source": True,
                "editorial_date": True,
                "logo": True,
                "logo_position": "bottom_right",
                "qr_position": "bottom_center"
            }
        }

        template_path = self.templates_dir / "story.json"
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)

        logger.info(f"Created 1 default template in {self.templates_dir}")
    
    def list_templates(self) -> List[str]:
        """List available template names"""
        if not self.templates_dir.exists():
            return []
        
        templates = []
        for template_file in self.templates_dir.glob("*.json"):
            templates.append(template_file.stem)
        
        return sorted(templates)
    
    def load_template(self, template_name: str) -> PosterTemplate:
        """Load a specific template by name"""
        template_path = self.templates_dir / f"{template_name}.json"
        if not template_path.exists():
            available = self.list_templates()
            raise PosterGenerationError(
                f"Template '{template_name}' not found. Available templates: {', '.join(available)}"
            )
        
        return PosterTemplate.from_file(template_path)
    
    def generate_poster(
        self,
        editorial: Dict[str, Any],
        template_name: Optional[str] = None,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Generate a poster from editorial content
        
        Args:
            editorial: Dictionary containing editorial title and content
            template_name: Name of the template to use (defaults to default_template)
            custom_options: Optional dict to override template settings
            
        Returns:
            Path to the generated poster file
        """
        return self._generate_local_poster(editorial, template_name, custom_options)
    
    def _load_font(self, font_file: Optional[str], font_family: str, size: int) -> ImageFont.ImageFont:
        """
        Load a font with fallback chain: custom font → bundled font → system font → default
        
        Args:
            font_file: Custom font filename (e.g., "Inter-Regular.ttf")
            font_family: System font family name (e.g., "arial")
            size: Font size in points
            
        Returns:
            Loaded ImageFont object
        """
        # Try custom/bundled font first
        if font_file:
            # Try to load from bundled fonts directory
            try:
                import importlib.resources as pkg_resources
                try:
                    # Python 3.9+
                    fonts_path = pkg_resources.files("moka_news") / "fonts" / font_file
                    if fonts_path.exists():
                        font = ImageFont.truetype(str(fonts_path), size)
                        logger.debug(f"Loaded bundled font: {font_file!r} @ {size}px")
                        return font
                except AttributeError:
                    # Python 3.7-3.8 fallback
                    with pkg_resources.path("moka_news.fonts", font_file) as font_path:
                        if font_path.exists():
                            font = ImageFont.truetype(str(font_path), size)
                            logger.debug(f"Loaded bundled font (3.8): {font_file!r} @ {size}px")
                            return font
            except Exception as e:
                logger.debug(f"Could not load bundled font {font_file!r}: {e}")
            
            # Try as absolute path or relative to cwd
            try:
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

        # Try common TrueType fallbacks so text remains scalable and legible.
        fallback_candidates = self._get_fallback_font_candidates(font_family)
        for candidate in fallback_candidates:
            try:
                font = ImageFont.truetype(candidate, size)
                logger.debug(f"Loaded fallback TrueType font: {candidate!r} @ {size}px")
                return font
            except Exception:
                continue
        
        # Fallback to default PIL font
        logger.warning(
            "Font fallback to PIL default (bitmap): "
            f"requested font_file={font_file!r}, font_family={font_family!r}, size={size}"
        )
        return ImageFont.load_default()

    def _get_fallback_font_candidates(self, font_family: str) -> List[str]:
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

        # Always include a neutral fallback chain as last resort.
        candidates.extend([
            "Arial.ttf",
            "Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "DejaVuSans.ttf",
        ])

        # Preserve order while removing duplicates.
        unique_candidates: List[str] = []
        seen = set()
        for item in candidates:
            if item not in seen:
                seen.add(item)
                unique_candidates.append(item)

        return unique_candidates

    def _fit_font_size(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font_file: Optional[str],
        font_family: str,
        max_width: int,
        max_height: int,
        line_spacing: float = 1.3,
        min_size: int = 12,
        max_size: int = 220,
    ) -> int:
        """Binary-search for the largest font size where *text* wraps and fits
        inside (max_width × max_height). If text does not fit at *min_size*,
        shrink progressively to a small hard floor.
        """
        best: Optional[int] = None
        lo, hi = min_size, max_size
        while lo <= hi:
            mid = (lo + hi) // 2
            font = self._load_font(font_file, font_family, mid)
            lines = self._wrap_text(draw, text, font, max_width)
            total_h = 0
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                total_h += int((bbox[3] - bbox[1]) * line_spacing)
            if total_h <= max_height:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        if best is not None:
            return best

        # If text doesn't fit even at min_size, keep shrinking down to a
        # hard floor to maximize the chance of showing the full body text.
        hard_floor = 8
        for size in range(min_size - 1, hard_floor - 1, -1):
            font = self._load_font(font_file, font_family, size)
            lines = self._wrap_text(draw, text, font, max_width)
            total_h = 0
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                total_h += int((bbox[3] - bbox[1]) * line_spacing)
            if total_h <= max_height:
                return size

        return hard_floor

    def _fit_single_line_font_size(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font_file: Optional[str],
        font_family: str,
        max_width: int,
        max_height: int,
        min_size: int = 12,
        max_size: int = 220,
    ) -> int:
        """Binary-search the largest font size fitting one single line."""
        best: Optional[int] = None
        lo, hi = min_size, max_size
        while lo <= hi:
            mid = (lo + hi) // 2
            font = self._load_font(font_file, font_family, mid)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            if text_w <= max_width and text_h <= max_height:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1

        if best is not None:
            return best

        hard_floor = 8
        for size in range(min_size - 1, hard_floor - 1, -1):
            font = self._load_font(font_file, font_family, size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            if text_w <= max_width and text_h <= max_height:
                return size
        return hard_floor

    @staticmethod
    def _truncate_single_line_text(
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.ImageFont,
        max_width: int,
    ) -> str:
        """Truncate text to a single line with ASCII ellipsis if needed."""
        raw = (text or "").strip()
        if not raw:
            return ""

        def text_width(value: str) -> int:
            bbox = draw.textbbox((0, 0), value, font=font)
            return bbox[2] - bbox[0]

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

    def _generate_local_poster(
        self,
        editorial: Dict[str, Any],
        template_name: Optional[str] = None,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Generate poster locally using PIL/Pillow with gradient and content box support"""
        logger.info(f"_generate_local_poster: start (template={template_name or self.default_template!r})")
        # Load template
        template_name = template_name or self.default_template
        template = self.load_template(template_name)
        logger.debug(
            f"Template loaded: {template.name} ({template.width}x{template.height}), "
            f"gradient={template.gradient_enabled}, content_box={template.content_box_enabled}"
        )
        
        # Apply custom options (including gradient and content_box overrides)
        if custom_options:
            # Handle nested dicts for gradient and content_box
            for key, value in custom_options.items():
                if key == "gradient" and isinstance(value, dict):
                    for gkey, gval in value.items():
                        attr_name = f"gradient_{gkey}"
                        if hasattr(template, attr_name):
                            setattr(template, attr_name, gval)
                elif key == "content_box" and isinstance(value, dict):
                    for ckey, cval in value.items():
                        if ckey == "shadow" and isinstance(cval, dict):
                            for skey, sval in cval.items():
                                attr_name = f"shadow_{skey}"
                                if hasattr(template, attr_name):
                                    setattr(template, attr_name, sval)
                        else:
                            attr_name = f"content_box_{ckey}"
                            if hasattr(template, attr_name):
                                setattr(template, attr_name, cval)
                elif hasattr(template, key):
                    setattr(template, key, value)
        
        # Create base image with gradient or solid color
        if template.gradient_enabled and template.gradient_colors:
            logger.debug(f"Creating gradient background: type={template.gradient_type!r}, colors={template.gradient_colors}")
            img = _create_gradient_background(
                template.width,
                template.height,
                template.gradient_colors,
                template.gradient_type
            )
        else:
            logger.debug(f"Creating solid background: {template.background_color!r}")
            img = Image.new("RGB", (template.width, template.height), template.background_color)
        
        # Add content box with shadow if enabled
        if template.content_box_enabled:
            # Calculate box dimensions with uniform margins on all sides
            box_width = int(template.width * 0.9)
            # Use the same margin on all sides (10% of width)
            margin = (template.width - box_width) // 2
            box_x = margin
            box_y = margin
            box_height = template.height - (2 * margin)
            logger.debug(f"Content box: pos=({box_x},{box_y}), size=({box_width}x{box_height}), radius={template.content_box_radius}")
            
            # Draw rounded box with shadow
            shadow_config = {
                "offset_x": template.shadow_offset_x,
                "offset_y": template.shadow_offset_y,
                "blur": template.shadow_blur,
                "color": template.shadow_color
            }
            
            img = _draw_rounded_box_with_shadow(
                img,
                (box_x, box_y),
                (box_width, box_height),
                template.content_box_radius,
                shadow_config,
                template.content_box_background
            )
            logger.debug("Content box drawn")
            
            # Update drawing parameters to be relative to content box
            content_padding = template.content_box_padding
            draw_x = box_x + content_padding
            draw_y = box_y + content_padding
            max_width = box_width - (content_padding * 2)
        else:
            # No content box, use full canvas
            draw_x = template.padding
            draw_y = template.padding
            max_width = template.width - (template.padding * 2)
        
        # Create draw context
        draw = ImageDraw.Draw(img)

        # ── Text content ───────────────────────────────────────────────
        content = str(editorial.get("content") or "")
        title = str(editorial.get("title") or "Morning Editorial").strip()
        title_from_content, _ = self._extract_title_and_body(content)
        if title_from_content:
            title = title_from_content
        clean_content = self._extract_poster_paragraph(content)
        body_content = self._format_body_for_readability(clean_content)
        logger.debug(f"Title: {title!r}")
        logger.debug(
            f"Body text length after cleaning: {len(body_content)} chars / ~{len(body_content.split())} words"
        )

        # ── Zone calculation ───────────────────────────────────────────
        # Total drawable height (inside box padding, or canvas padding)
        if template.content_box_enabled:
            total_draw_h = box_height - (template.content_box_padding * 2)
        else:
            total_draw_h = template.height - (template.padding * 2)

        # Footer zone: one line per active metadata item + a small top gap
        footer_line_h = template.metadata_font_size + 8
        footer_lines = (
            int(template.show_timestamp)
            + int(template.show_source)
            + int(template.show_source and template.show_editorial_date)
        )
        footer_zone_h = max(footer_lines * footer_line_h + 20, 20)

        # Divider between title and body
        divider_zone_h = 32  # gap above + line + gap below

        # Remaining content split: title uses less height in single-line mode.
        usable_h = total_draw_h - footer_zone_h - divider_zone_h
        title_ratio = 0.14 if template.title_single_line else 0.25
        title_zone_h = max(int(usable_h * title_ratio), 40)
        body_zone_h = usable_h - title_zone_h

        # ── Auto-fit fonts ─────────────────────────────────────────────
        metadata_font = self._load_font(
            template.font_file, template.font_family, template.metadata_font_size
        )

        width_scale = max(0.6, template.width / 1080.0)
        title_min_size = max(16, int(template.title_min_size * width_scale))
        title_max_size = max(title_min_size, int(template.title_max_size * width_scale))

        if template.title_single_line:
            title_font_size = self._fit_single_line_font_size(
                draw,
                title,
                template.font_file,
                template.font_family,
                max_width,
                title_zone_h,
                min_size=title_min_size,
                max_size=title_max_size,
            )
        else:
            title_font_size = self._fit_font_size(
                draw, title,
                template.font_file, template.font_family,
                max_width, title_zone_h, template.line_spacing,
                min_size=title_min_size,
                max_size=title_max_size,
            )
        title_font = self._load_font(template.bold_font_file, template.font_family, title_font_size)
        logger.info(f"Title font: {title_font_size}px (zone {title_zone_h}px, max_width {max_width}px)")

        # Body sizing uses bold font as worst-case (bold glyphs are slightly wider)
        _plain_content = re.sub(r'\*\*([^*]+)\*\*', r'\1', body_content)
        body_min_size = max(8, int(template.summary_min_size * width_scale))
        body_max_size = max(body_min_size, int(template.summary_max_size * width_scale))
        body_intro_gap = 10
        body_fit_height = max(1, body_zone_h - body_intro_gap)
        body_font_size = self._fit_font_size_for_paragraphs(
            draw, _plain_content,
            template.bold_font_file, template.font_family,
            max_width, body_fit_height, template.line_spacing,
            min_size=body_min_size,
            max_size=body_max_size,
        )
        summary_font = self._load_font(template.font_file, template.font_family, body_font_size)
        summary_bold_font = self._load_font(template.bold_font_file, template.font_family, body_font_size)
        logger.info(f"Body font: {body_font_size}px (zone {body_zone_h}px)")

        # ── Draw title ─────────────────────────────────────────────────
        current_y = draw_y
        if template.title_single_line:
            title_lines = [self._truncate_single_line_text(draw, title, title_font, max_width)]
        else:
            title_lines = self._wrap_text(draw, title, title_font, max_width)
        for line in title_lines:
            draw.text((draw_x, current_y), line, fill=template.accent_color, font=title_font)
            bbox = draw.textbbox((draw_x, current_y), line, font=title_font)
            current_y += int((bbox[3] - bbox[1]) * template.line_spacing)

        # ── Divider line ───────────────────────────────────────────────
        current_y += 12
        draw.line(
            [(draw_x, current_y), (draw_x + max_width, current_y)],
            fill=template.accent_color,
            width=3,
        )
        current_y += 17
        current_y += body_intro_gap

        # ── Draw body (fills the body zone) ───────────────────────────
        body_max_y = current_y + body_fit_height
        body_paragraphs = self._split_paragraphs(body_content)
        line_probe_bbox = draw.textbbox((0, 0), "Ag", font=summary_font)
        paragraph_gap_h = max(4, int((line_probe_bbox[3] - line_probe_bbox[1]) * 0.4))
        stop_render = False
        for paragraph_index, paragraph in enumerate(body_paragraphs):
            rich_segments = self._parse_rich_text(paragraph)
            rich_lines = self._wrap_rich_lines(
                draw,
                rich_segments,
                summary_font,
                summary_bold_font,
                max_width,
            )
            for line_tokens in rich_lines:
                if current_y > body_max_y:
                    stop_render = True
                    break
                x = draw_x
                line_h = 0
                for token_text, _is_bold, token_font in line_tokens:
                    draw.text((x, current_y), token_text, fill=template.text_color, font=token_font)
                    bbox = draw.textbbox((x, current_y), token_text, font=token_font)
                    x += bbox[2] - bbox[0]
                    token_h = bbox[3] - bbox[1]
                    if token_h > line_h:
                        line_h = token_h
                current_y += int(line_h * template.line_spacing)
            if stop_render:
                break
            if paragraph_index < len(body_paragraphs) - 1:
                if current_y + paragraph_gap_h > body_max_y:
                    break
                current_y += paragraph_gap_h

        # ── Footer (anchored at bottom of drawable area) ───────────────
        footer_y = draw_y + total_draw_h - footer_zone_h + 20
        if template.show_timestamp:
            ts = datetime.now().strftime("%B %d, %Y")
            draw.text(
                (draw_x, footer_y), f"Generated: {ts}",
                fill=template.secondary_color, font=metadata_font,
            )
            footer_y += footer_line_h
        if template.show_source:
            draw.text(
                (draw_x, footer_y), "MoKa News Editorial",
                fill=template.secondary_color, font=metadata_font,
            )
            footer_y += footer_line_h
            if template.show_editorial_date:
                editorial_date = self._get_editorial_date_label(editorial)
                draw.text(
                    (draw_x, footer_y), f"Editorial date: {editorial_date}",
                    fill=template.secondary_color, font=metadata_font,
                )

        # Add logo if enabled
        img = self._add_logo(
            img,
            template,
            draw_x=draw_x,
            draw_y=draw_y,
            max_width=max_width,
            total_draw_h=total_draw_h,
        )

        # Generate filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{timestamp}_poster.png"
        output_path = self.posters_dir / filename
        
        # Convert back to RGB if needed (after RGBA operations)
        if img.mode == 'RGBA':
            logger.debug("Converting RGBA → RGB")
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = background
        
        # Save image
        img.save(output_path, "PNG", optimize=True)
        logger.info(f"_generate_local_poster: saved → {output_path}")
        return output_path
    
    def _wrap_text(self, draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
        """Wrap text to fit within specified width"""
        words = text.split()
        lines = []
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

    def _resolve_logo_path(self) -> Optional[Path]:
        """Resolve logo path from config override or known project locations."""
        candidates: List[Path] = []

        if self.logo_path_override:
            candidates.append(Path(self.logo_path_override).expanduser())

        package_dir = Path(__file__).resolve().parent
        candidates.append(package_dir.parent / "assets" / "moka-news-logo.png")
        candidates.append(package_dir / "assets" / "moka-news-logo.png")

        for candidate in candidates:
            try:
                if candidate.exists() and candidate.is_file():
                    return candidate
            except OSError:
                continue
        return None

    def _add_logo(
        self,
        img: Image.Image,
        template: PosterTemplate,
        draw_x: int,
        draw_y: int,
        max_width: int,
        total_draw_h: int,
    ) -> Image.Image:
        """Add branded logo to poster if enabled and available."""
        if not template.show_logo:
            return img

        logo_path = self._resolve_logo_path()
        if logo_path is None:
            logger.debug("Logo not found, skipping logo rendering.")
            return img

        try:
            with Image.open(logo_path) as logo_raw:
                logo_img = logo_raw.convert("RGBA")
        except Exception as exc:
            logger.warning("Could not load logo %s: %s", logo_path, exc)
            return img

        logo_w = getattr(logo_img, "width", 0)
        logo_h = getattr(logo_img, "height", 0)
        if not isinstance(logo_w, (int, float)) or not isinstance(logo_h, (int, float)):
            logger.debug("Logo dimensions are not numeric, skipping logo rendering.")
            return img
        if logo_w <= 0 or logo_h <= 0:
            return img

        max_logo_w = max(80, int(max_width * 0.24))
        max_logo_h = max(40, int(total_draw_h * 0.10))
        scale = min(max_logo_w / logo_w, max_logo_h / logo_h, 1.0)
        target_w = max(1, int(logo_w * scale))
        target_h = max(1, int(logo_h * scale))
        resampling = getattr(Image, "Resampling", Image)
        logo_img = logo_img.resize((target_w, target_h), resampling.LANCZOS)

        alpha = logo_img.getchannel("A").point(lambda p: int(p * 0.92))
        logo_img.putalpha(alpha)

        if template.logo_position == "top_left":
            logo_x = draw_x
            logo_y = draw_y
        elif template.logo_position == "top_right":
            logo_x = draw_x + max_width - target_w
            logo_y = draw_y
        elif template.logo_position == "bottom_left":
            logo_x = draw_x
            logo_y = draw_y + total_draw_h - target_h
        else:
            logo_x = draw_x + max_width - target_w
            logo_y = draw_y + total_draw_h - target_h

        if img.mode != "RGBA":
            img = img.convert("RGBA")
        img.alpha_composite(logo_img, (logo_x, logo_y))
        return img

    @staticmethod
    def _parse_editorial_datetime(value: Any) -> Optional[datetime]:
        """Best-effort parse of editorial timestamp values."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            try:
                return datetime.fromtimestamp(value)
            except (OverflowError, OSError, ValueError):
                return None
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return None

            normalized = raw
            if normalized.endswith("Z"):
                normalized = normalized[:-1] + "+00:00"

            candidates = [normalized]
            if " " in normalized and "T" not in normalized:
                candidates.append(normalized.replace(" ", "T", 1))

            for candidate in candidates:
                try:
                    return datetime.fromisoformat(candidate)
                except ValueError:
                    continue

            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d_%H-%M"):
                try:
                    return datetime.strptime(raw, fmt)
                except ValueError:
                    continue

        return None

    def _get_editorial_date_label(self, editorial: Dict[str, Any]) -> str:
        """Return formatted editorial date for footer display."""
        parsed = self._parse_editorial_datetime(editorial.get("timestamp"))
        if parsed is None:
            parsed = datetime.now()
        return parsed.strftime("%B %d, %Y")

    @staticmethod
    def _split_paragraphs(text: str) -> List[str]:
        """Split body text into cleaned paragraphs preserving blank-line boundaries."""
        if not text:
            return []
        return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    def _format_body_for_readability(self, text: str) -> str:
        """Format body text to improve scanability.

        - Split sentences onto separate lines
        """
        raw = (text or "").strip()
        if not raw:
            return ""

        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", raw) if s.strip()]
        if not sentences:
            return raw

        return "\n\n".join(sentences)

    def _measure_wrapped_paragraph_height(
        self,
        draw: ImageDraw.ImageDraw,
        paragraphs: List[str],
        font: ImageFont.ImageFont,
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
            lines = self._wrap_text(draw, paragraph, font, max_width)
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                total_h += int((bbox[3] - bbox[1]) * line_spacing)
            if idx < len(paragraphs) - 1:
                total_h += paragraph_gap_h
        return total_h

    def _fit_font_size_for_paragraphs(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font_file: Optional[str],
        font_family: str,
        max_width: int,
        max_height: int,
        line_spacing: float = 1.3,
        min_size: int = 12,
        max_size: int = 220,
        paragraph_gap_factor: float = 0.4,
    ) -> int:
        """Binary-search the largest font size that fits wrapped paragraphs."""
        paragraphs = self._split_paragraphs(text)
        if not paragraphs:
            return min_size

        best: Optional[int] = None
        lo, hi = min_size, max_size
        while lo <= hi:
            mid = (lo + hi) // 2
            font = self._load_font(font_file, font_family, mid)
            total_h = self._measure_wrapped_paragraph_height(
                draw,
                paragraphs,
                font,
                max_width,
                line_spacing,
                paragraph_gap_factor=paragraph_gap_factor,
            )
            if total_h <= max_height:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1

        if best is not None:
            return best

        hard_floor = 8
        for size in range(min_size - 1, hard_floor - 1, -1):
            font = self._load_font(font_file, font_family, size)
            total_h = self._measure_wrapped_paragraph_height(
                draw,
                paragraphs,
                font,
                max_width,
                line_spacing,
                paragraph_gap_factor=paragraph_gap_factor,
            )
            if total_h <= max_height:
                return size
        return hard_floor

    def _parse_rich_text(self, text: str) -> List[tuple]:
        """Parse ``**bold**`` markup in *text* into a list of segments.

        Returns:
            List of ``(segment_text, is_bold)`` tuples where *is_bold* is
            ``True`` for text enclosed in double asterisks.  Every token
            inside a bold span is returned as a separate ``(word, True)``
            tuple so that word-wrapping in :meth:`_wrap_rich_lines` can
            treat individual words.
        """
        segments: List[tuple] = []
        pattern = re.compile(r'\*\*([^*]+)\*\*')
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

    def _wrap_rich_lines(
        self,
        draw: "ImageDraw.ImageDraw",
        segments: List[tuple],
        regular_font: "ImageFont.ImageFont",
        bold_font: "ImageFont.ImageFont",
        max_width: int,
    ) -> List[List[tuple]]:
        """Wrap rich-text segments into pixel-constrained lines.

        Args:
            draw: PIL :class:`~PIL.ImageDraw.ImageDraw` context.
            segments: Output of :meth:`_parse_rich_text` —
                ``list[(text, is_bold)]``.
            regular_font: Font for non-bold tokens.
            bold_font: Font for bold tokens.
            max_width: Maximum line width in pixels.

        Returns:
            List of lines.  Each line is a list of
            ``(token_str, is_bold, font)`` triples ready for rendering.
        """
        # Build a flat list of (word, is_bold) tokens from all segments
        word_tokens: List[tuple] = []
        for seg_text, is_bold in segments:
            for word in seg_text.split():
                word_tokens.append((word, is_bold))

        lines: List[List[tuple]] = []
        current_line: List[tuple] = []
        current_width = 0

        for word, is_bold in word_tokens:
            font = bold_font if is_bold else regular_font
            # Add a space separator when joining to an existing line
            display = (" " + word) if current_line else word
            bbox = draw.textbbox((0, 0), display, font=font)
            token_w = bbox[2] - bbox[0]

            if current_width + token_w <= max_width:
                current_line.append((display, is_bold, font))
                current_width += token_w
            else:
                if current_line:
                    lines.append(current_line)
                # Start new line without leading space
                current_line = [(word, is_bold, font)]
                bbox = draw.textbbox((0, 0), word, font=font)
                current_width = bbox[2] - bbox[0]

        if current_line:
            lines.append(current_line)

        return lines

    def _extract_poster_paragraph(self, markdown_content: str) -> str:
        """Extract and clean the first editorial paragraph for poster text."""
        content = markdown_content or ""

        # Ignore trailing sources section if present.
        if "\n## Sources" in content:
            content = content.split("\n## Sources", 1)[0]

        # Normalize TITLE:/SUMMARY: format to body-only content.
        _, content = self._extract_title_and_body(content)

        for block in re.split(r"\n\s*\n", content):
            cleaned = self._clean_content_for_poster(block)
            if cleaned:
                return cleaned

        return "No editorial content available."

    @staticmethod
    def _extract_title_and_body(content: str) -> Tuple[Optional[str], str]:
        """Extract title from a leading ``TITLE:`` line and return remaining body."""
        raw = content or ""
        lines = raw.splitlines()
        title_re = re.compile(r"^\s*(?:\*\*)?TITLE(?:\*\*)?\s*:\s*(.+?)\s*$", re.IGNORECASE)
        summary_prefix_re = re.compile(r"^\s*(?:\*\*)?SUMMARY(?:\*\*)?\s*:\s*", re.IGNORECASE)

        for idx, line in enumerate(lines):
            stripped = line.strip()
            match = title_re.match(stripped)
            if not match:
                continue

            title = match.group(1).strip() or None
            remainder = "\n".join(lines[idx + 1:]).lstrip()
            remainder = summary_prefix_re.sub("", remainder, count=1)
            return title, remainder

        return None, raw

    def _clean_content_for_poster(self, content: str) -> str:
        """Clean a single paragraph for poster display."""
        raw = (content or "").strip()
        if not raw:
            return ""

        # Drop markdown metadata lines.
        cleaned_lines: List[str] = []
        for line in raw.splitlines():
            stripped = line.strip()
            if not stripped or stripped == "---":
                continue
            if stripped.startswith("#"):
                continue
            if re.match(r"^(?:\*\*)?(?:TITLE|SUMMARY)(?:\*\*)?\s*:", stripped, re.IGNORECASE):
                continue
            if re.fullmatch(r"\*[^*]+\*", stripped):
                continue
            if stripped.startswith("- "):
                continue
            cleaned_lines.append(stripped)
        text = " ".join(cleaned_lines).strip()
        if not text:
            return ""

        # Remove markdown links [text](url) -> text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Remove markdown formatting — keep **bold** intact, strip the rest
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)', r'\1', text)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text
    
    def _add_qr_code(self, img: Image.Image, url: str, template: PosterTemplate):
        """Add QR code to the poster"""
        if not QRCODE_AVAILABLE:
            return
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=3, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color=template.text_color, back_color=template.background_color)
        qr_size = 120  # QR code size
        qr_img = qr_img.resize((qr_size, qr_size))
        
        # Position QR code based on template settings
        if template.qr_position == "bottom_right":
            qr_pos = (template.width - qr_size - template.padding, template.height - qr_size - template.padding)
        elif template.qr_position == "bottom_left":
            qr_pos = (template.padding, template.height - qr_size - template.padding)
        elif template.qr_position == "top_right":
            qr_pos = (template.width - qr_size - template.padding, template.padding)
        elif template.qr_position == "bottom_center":
            qr_pos = ((template.width - qr_size) // 2, template.height - qr_size - template.padding)
        else:
            qr_pos = (template.width - qr_size - template.padding, template.height - qr_size - template.padding)
        
        # Paste QR code onto poster
        if qr_img.mode != 'RGBA':
            qr_img = qr_img.convert('RGBA')
        img.paste(qr_img, qr_pos, qr_img)
