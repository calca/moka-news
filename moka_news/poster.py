"""
Poster Generator - Creates 9:16 posters from editorial content
Supports both local generation (PIL/Pillow) and optional AI image generation
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
try:
    from PIL import Image, ImageDraw, ImageFont, ImageColor
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
        
        # Typography
        typography = template_data.get("typography", {})
        self.title_font_size = typography.get("title_size", 48)
        self.summary_font_size = typography.get("summary_size", 24)
        self.metadata_font_size = typography.get("metadata_size", 18)
        self.font_family = typography.get("font_family", "arial")
        
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
        
        # Minimal template (Rose Pine inspired)
        minimal_template = {
            "name": "Minimal",
            "description": "Clean and simple design with Rose Pine color scheme",
            "layout": {
                "width": 1080,
                "height": 1920,
                "padding": 80,
                "line_spacing": 1.3
            },
            "colors": {
                "background": "#191724",
                "text": "#e0def4",
                "accent": "#ebbcba",
                "secondary": "#9ccfd8"
            },
            "typography": {
                "title_size": 52,
                "summary_size": 26,
                "metadata_size": 20,
                "font_family": "arial"
            },
            "elements": {
                "qr_code": False,
                "timestamp": True,
                "source": True,
                "qr_position": "bottom_right"
            }
        }
        
        # Elegant template
        elegant_template = {
            "name": "Elegant",
            "description": "Sophisticated design with serif typography",
            "layout": {
                "width": 1080,
                "height": 1920,
                "padding": 100,
                "line_spacing": 1.4
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
                "font_family": "Times"
            },
            "elements": {
                "qr_code": False,
                "timestamp": True,
                "source": True,
                "qr_position": "bottom_left"
            }
        }
        
        # Social template
        social_template = {
            "name": "Social",
            "description": "Optimized for social media sharing",
            "layout": {
                "width": 1080,
                "height": 1920,
                "padding": 60,
                "line_spacing": 1.2
            },
            "colors": {
                "background": "#000000",
                "text": "#ffffff",
                "accent": "#ff6b6b",
                "secondary": "#4ecdc4"
            },
            "typography": {
                "title_size": 48,
                "summary_size": 24,
                "metadata_size": 18,
                "font_family": "arial"
            },
            "elements": {
                "qr_code": False,
                "timestamp": False,
                "source": True,
                "qr_position": "bottom_center"
            }
        }
        
        # Modern template
        modern_template = {
            "name": "Modern",
            "description": "Contemporary design with geometric elements",
            "layout": {
                "width": 1080,
                "height": 1920,
                "padding": 70,
                "line_spacing": 1.25
            },
            "colors": {
                "background": "#2d3748",
                "text": "#f7fafc",
                "accent": "#68d391",
                "secondary": "#4299e1"
            },
            "typography": {
                "title_size": 50,
                "summary_size": 25,
                "metadata_size": 19,
                "font_family": "arial"
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
    
    def _generate_local_poster(
        self,
        editorial: Dict[str, Any],
        template_name: Optional[str] = None,
        custom_options: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Generate poster locally using PIL/Pillow"""
        # Load template
        template_name = template_name or self.default_template
        template = self.load_template(template_name)
        
        # Apply custom options
        if custom_options:
            for key, value in custom_options.items():
                if hasattr(template, key):
                    setattr(template, key, value)
        
        # Create image
        img = Image.new("RGB", (template.width, template.height), template.background_color)
        draw = ImageDraw.Draw(img)
        
        # Load fonts (fallback to default if not available)
        try:
            title_font = ImageFont.truetype(template.font_family, template.title_font_size)
        except:
            title_font = ImageFont.load_default()
        
        try:
            summary_font = ImageFont.truetype(template.font_family, template.summary_font_size)
        except:
            summary_font = ImageFont.load_default()
        
        try:
            metadata_font = ImageFont.truetype(template.font_family, template.metadata_font_size)
        except:
            metadata_font = ImageFont.load_default()
        
        # Calculate layout positions
        current_y = template.padding
        max_width = template.width - (template.padding * 2)
        
        # Draw title
        title = editorial.get("title", "Morning Editorial")
        title_lines = self._wrap_text(draw, title, title_font, max_width)
        
        for line in title_lines:
            draw.text((template.padding, current_y), line, fill=template.accent_color, font=title_font)
            bbox = draw.textbbox((template.padding, current_y), line, font=title_font)
            current_y += int((bbox[3] - bbox[1]) * template.line_spacing)
        
        current_y += template.padding // 2  # Extra space after title
        
        # Draw summary content (first few lines)
        content = editorial.get("content", "")
        # Remove markdown formatting and take first paragraph
        clean_content = self._clean_content_for_poster(content)
        summary_lines = self._wrap_text(draw, clean_content, summary_font, max_width)
        
        # Limit to fit on poster (approximately 20 lines)
        max_lines = 20
        for i, line in enumerate(summary_lines[:max_lines]):
            if current_y > template.height - template.padding * 3:  # Leave space for footer
                break
            draw.text((template.padding, current_y), line, fill=template.text_color, font=summary_font)
            bbox = draw.textbbox((template.padding, current_y), line, font=summary_font)
            current_y += int((bbox[3] - bbox[1]) * template.line_spacing)
        
        # Draw metadata at bottom
        footer_y = template.height - template.padding - 100
        
        if template.show_timestamp:
            timestamp = datetime.now().strftime("%B %d, %Y")
            draw.text((template.padding, footer_y), f"Generated: {timestamp}", 
                     fill=template.secondary_color, font=metadata_font)
            footer_y += 30
        
        if template.show_source:
            source_text = "MoKa News - AI-Generated Editorial"
            draw.text((template.padding, footer_y), source_text, 
                     fill=template.secondary_color, font=metadata_font)
        
        # QR code generation disabled
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"{timestamp}_poster.png"
        output_path = self.posters_dir / filename
        
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