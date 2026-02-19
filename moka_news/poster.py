"""
Poster Generator - Creates 9:16 posters from editorial content
Supports both local generation (PIL/Pillow) and optional AI image generation
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
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

import requests
from moka_news.logger import get_logger
from moka_news.constants import (
    DEFAULT_GRADIENT_PRESETS,
    DEFAULT_BOX_PADDING,
    DEFAULT_BOX_RADIUS,
    DEFAULT_SHADOW_OFFSET,
    DEFAULT_SHADOW_BLUR,
    BUNDLED_FONTS,
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
        self.width = layout.get("width", 1080)  # 9:16 aspect ratio
        self.height = layout.get("height", 1920)
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
        self.title_font_size = typography.get("title_size", 48)
        self.summary_font_size = typography.get("summary_size", 24)
        self.metadata_font_size = typography.get("metadata_size", 18)
        self.font_family = typography.get("font_family", "arial")
        self.font_file = typography.get("font_file", None)  # Custom font file
        
        # Elements positioning
        elements = template_data.get("elements", {})
        self.show_qr_code = elements.get("qr_code", True)
        self.show_timestamp = elements.get("timestamp", True)
        self.show_source = elements.get("source", True)
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
    """Generates 9:16 posters from editorial content"""
    
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
        self.generation_method = config.get("method", "local")  # local, ai, hybrid
        self.default_template = config.get("default_template", "minimal")
        self.ai_config = config.get("ai", {})
        
        logger.info(f"PosterGenerator initialized:")
        logger.info(f"  - Method: {self.generation_method}")
        logger.info(f"  - Default template: {self.default_template}")
        logger.info(f"  - Posters directory: {self.posters_dir}")
        logger.info(f"  - Templates directory: {self.templates_dir}")
    
    def _create_default_templates(self):
        """Create default template files if templates directory doesn't exist"""
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Minimal template (Rose Pine inspired with gradient)
        minimal_template = {
            "name": "Minimal",
            "description": "Clean and simple design with Rose Pine color scheme",
            "layout": {
                "width": 1080,
                "height": 1920,
                "padding": 80,
                "line_spacing": 1.3
            },
            "gradient": {
                "enabled": True,
                "type": "vertical",
                "preset": "rose-pine"
            },
            "content_box": {
                "enabled": True,
                "background": "#ffffff",
                "padding": 50,
                "border_radius": 20,
                "shadow": {
                    "offset_x": 4,
                    "offset_y": 4,
                    "blur": 12,
                    "color": "rgba(0,0,0,0.15)"
                }
            },
            "colors": {
                "background": "#191724",
                "text": "#2d2d2d",
                "accent": "#eb6f92",
                "secondary": "#6e6a86"
            },
            "typography": {
                "title_size": 52,
                "summary_size": 26,
                "metadata_size": 20,
                "font_family": "arial",
                "font_file": "Inter-Regular.ttf"
            },
            "elements": {
                "qr_code": False,
                "timestamp": True,
                "source": True,
                "qr_position": "bottom_right"
            }
        }
        
        # Elegant template with diagonal gradient
        elegant_template = {
            "name": "Elegant",
            "description": "Sophisticated design with serif typography",
            "layout": {
                "width": 1080,
                "height": 1920,
                "padding": 100,
                "line_spacing": 1.4
            },
            "gradient": {
                "enabled": True,
                "type": "diagonal",
                "colors": ["#f5f5dc", "#d3d3d3"]
            },
            "content_box": {
                "enabled": True,
                "background": "#ffffff",
                "padding": 45,
                "border_radius": 20,
                "shadow": {
                    "offset_x": 4,
                    "offset_y": 4,
                    "blur": 12,
                    "color": "rgba(0,0,0,0.15)"
                }
            },
            "colors": {
                "background": "#f8f8f2",
                "text": "#282a36",
                "accent": "#bd93f9",
                "secondary": "#6272a4"
            },
            "typography": {
                "title_size": 56,
                "summary_size": 28,
                "metadata_size": 22,
                "font_family": "Times",
                "font_file": "Roboto-Regular.ttf"
            },
            "elements": {
                "qr_code": False,
                "timestamp": True,
                "source": True,
                "qr_position": "bottom_left"
            }
        }
        
        # Social template with vivid gradient
        social_template = {
            "name": "Social",
            "description": "Optimized for social media sharing",
            "layout": {
                "width": 1080,
                "height": 1920,
                "padding": 60,
                "line_spacing": 1.2
            },
            "gradient": {
                "enabled": True,
                "type": "diagonal",
                "preset": "purple-pink"
            },
            "content_box": {
                "enabled": True,
                "background": "#ffffff",
                "padding": 40,
                "border_radius": 20,
                "shadow": {
                    "offset_x": 4,
                    "offset_y": 4,
                    "blur": 12,
                    "color": "rgba(0,0,0,0.15)"
                }
            },
            "colors": {
                "background": "#000000",
                "text": "#1a1a1a",
                "accent": "#dc2626",
                "secondary": "#6b7280"
            },
            "typography": {
                "title_size": 48,
                "summary_size": 24,
                "metadata_size": 18,
                "font_family": "arial",
                "font_file": "OpenSans-Regular.ttf"
            },
            "elements": {
                "qr_code": False,
                "timestamp": False,
                "source": True,
                "qr_position": "bottom_center"
            }
        }
        
        # Modern template with blue gradient
        modern_template = {
            "name": "Modern",
            "description": "Contemporary design with geometric elements",
            "layout": {
                "width": 1080,
                "height": 1920,
                "padding": 70,
                "line_spacing": 1.25
            },
            "gradient": {
                "enabled": True,
                "type": "vertical",
                "colors": ["#4299e1", "#2dd4bf"]
            },
            "content_box": {
                "enabled": True,
                "background": "#ffffff",
                "padding": 40,
                "border_radius": 20,
                "shadow": {
                    "offset_x": 4,
                    "offset_y": 4,
                    "blur": 12,
                    "color": "rgba(0,0,0,0.15)"
                }
            },
            "colors": {
                "background": "#2d3748",
                "text": "#2d3748",
                "accent": "#2563eb",
                "secondary": "#64748b"
            },
            "typography": {
                "title_size": 50,
                "summary_size": 25,
                "metadata_size": 19,
                "font_family": "arial",
                "font_file": "Inter-Bold.ttf"
            },
            "elements": {
                "qr_code": False,
                "timestamp": True,
                "source": True,
                "qr_position": "top_right"
            }
        }
        
        # Save templates
        templates = {
            "minimal.json": minimal_template,
            "elegant.json": elegant_template,
            "social.json": social_template,
            "modern.json": modern_template
        }
        
        for filename, template_data in templates.items():
            template_path = self.templates_dir / filename
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2)
        
        logger.info(f"Created {len(templates)} default templates in {self.templates_dir}")
    
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
        if self.generation_method == "ai":
            return self._generate_ai_poster(editorial, template_name, custom_options)
        elif self.generation_method == "hybrid":
            # Try AI first, fallback to local
            try:
                return self._generate_ai_poster(editorial, template_name, custom_options)
            except Exception as e:
                logger.warning(f"AI poster generation failed, falling back to local: {e}")
                return self._generate_local_poster(editorial, template_name, custom_options)
        else:
            # Default to local generation
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
                        return ImageFont.truetype(str(fonts_path), size)
                except AttributeError:
                    # Python 3.7-3.8 fallback
                    with pkg_resources.path("moka_news.fonts", font_file) as font_path:
                        if font_path.exists():
                            return ImageFont.truetype(str(font_path), size)
            except Exception as e:
                logger.debug(f"Could not load bundled font {font_file}: {e}")
            
            # Try as absolute path or relative to cwd
            try:
                font_path = Path(font_file)
                if font_path.exists():
                    return ImageFont.truetype(str(font_path), size)
            except Exception as e:
                logger.debug(f"Could not load font from path {font_file}: {e}")
        
        # Try system font
        try:
            return ImageFont.truetype(font_family, size)
        except Exception as e:
            logger.debug(f"Could not load system font {font_family}: {e}")
        
        # Fallback to default PIL font
        logger.warning(f"Could not load font, using default. Requested: {font_file or font_family}")
        return ImageFont.load_default()
    
    def _generate_local_poster(
        self,
        editorial: Dict[str, Any],
        template_name: Optional[str] = None,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Generate poster locally using PIL/Pillow with gradient and content box support"""
        # Load template
        template_name = template_name or self.default_template
        template = self.load_template(template_name)
        
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
            img = _create_gradient_background(
                template.width,
                template.height,
                template.gradient_colors,
                template.gradient_type
            )
        else:
            img = Image.new("RGB", (template.width, template.height), template.background_color)
        
        # Add content box with shadow if enabled
        if template.content_box_enabled:
            # Calculate box dimensions (80% width, auto height)
            box_width = int(template.width * 0.8)
            box_x = (template.width - box_width) // 2
            box_y = template.padding * 2  # Start below top margin
            # Height will be calculated based on content, for now use most of the canvas
            box_height = template.height - (template.padding * 4)
            
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
        
        # Load fonts using the new font loading method
        title_font = self._load_font(template.font_file, template.font_family, template.title_font_size)
        summary_font = self._load_font(template.font_file, template.font_family, template.summary_font_size)
        metadata_font = self._load_font(template.font_file, template.font_family, template.metadata_font_size)
        
        # Calculate layout positions
        current_y = draw_y
        
        # Draw title
        title = editorial.get("title", "Morning Editorial")
        title_lines = self._wrap_text(draw, title, title_font, max_width)
        
        for line in title_lines:
            draw.text((draw_x, current_y), line, fill=template.accent_color, font=title_font)
            bbox = draw.textbbox((draw_x, current_y), line, font=title_font)
            current_y += int((bbox[3] - bbox[1]) * template.line_spacing)
        
        current_y += template.padding // 2  # Extra space after title
        
        # Draw summary content (first few lines)
        content = editorial.get("content", "")
        # Remove markdown formatting and take first paragraph
        clean_content = self._clean_content_for_poster(content)
        summary_lines = self._wrap_text(draw, clean_content, summary_font, max_width)
        
        # Calculate space available for content
        if template.content_box_enabled:
            max_y = box_y + box_height - template.content_box_padding - 100  # Leave space for footer
        else:
            max_y = template.height - template.padding * 3
        
        # Limit to fit on poster
        for i, line in enumerate(summary_lines):
            if current_y > max_y:
                break
            draw.text((draw_x, current_y), line, fill=template.text_color, font=summary_font)
            bbox = draw.textbbox((draw_x, current_y), line, font=summary_font)
            current_y += int((bbox[3] - bbox[1]) * template.line_spacing)
        
        # Draw metadata at bottom
        if template.content_box_enabled:
            footer_y = box_y + box_height - template.content_box_padding - 60
        else:
            footer_y = template.height - template.padding - 100
        
        if template.show_timestamp:
            timestamp = datetime.now().strftime("%B %d, %Y")
            draw.text((draw_x, footer_y), f"Generated: {timestamp}", 
                     fill=template.secondary_color, font=metadata_font)
            footer_y += 30
        
        if template.show_source:
            source_text = "MoKa News - AI-Generated Editorial"
            draw.text((draw_x, footer_y), source_text, 
                     fill=template.secondary_color, font=metadata_font)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{timestamp}_poster.png"
        output_path = self.posters_dir / filename
        
        # Convert back to RGB if needed (after RGBA operations)
        if img.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = background
        
        # Save image
        img.save(output_path, "PNG", optimize=True)
        logger.info(f"Local poster generated: {output_path}")
        
        return output_path
    
    def _generate_ai_poster(
        self,
        editorial: Dict[str, Any],
        template_name: Optional[str] = None,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Generate poster using AI image generation (placeholder implementation)"""
        # This is a placeholder for AI integration
        # In a real implementation, this would call DALL-E, Midjourney, or similar
        raise PosterGenerationError("AI poster generation not yet implemented. Use 'local' or 'hybrid' method.")
    
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
    
    def _clean_content_for_poster(self, content: str) -> str:
        """Clean editorial content for poster display"""
        import re
        
        # Remove markdown links [text](url) -> text
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        
        # Remove markdown headers
        content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
        
        # Remove markdown formatting
        content = re.sub(r'\*\*([^\*]+)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*([^\*]+)\*', r'\1', content)      # Italic
        content = re.sub(r'`([^`]+)`', r'\1', content)         # Code
        
        # Split into sentences and take the first few
        sentences = content.split('. ')
        # Take roughly first 200 words for poster
        word_count = 0
        poster_content = ""
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            if word_count + sentence_words > 200:
                break
            poster_content += sentence + ". "
            word_count += sentence_words
        
        return poster_content.strip()
    
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