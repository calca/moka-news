"""
Tests for poster generation functionality
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from moka_news.poster import (
    PosterGenerator, 
    PosterTemplate, 
    PosterGenerationError,
    _create_gradient_background,
    _interpolate_colors,
    _draw_rounded_box_with_shadow
)
from moka_news.constants import DEFAULT_GRADIENT_PRESETS


class TestPosterTemplate:
    """Test PosterTemplate class functionality"""
    
    def test_template_initialization_with_defaults(self):
        """Test template initialization with default values"""
        template_data = {
            "name": "Test Template",
            "description": "Test description"
        }
        
        template = PosterTemplate(template_data)
        
        assert template.name == "Test Template"
        assert template.description == "Test description"
        assert template.width == 1080
        assert template.height == 1080
        assert template.background_color == "#1e1e2e"
        assert template.text_color == "#cdd6f4"
    
    def test_template_initialization_with_custom_values(self):
        """Test template initialization with custom values"""
        template_data = {
            "name": "Custom Template",
            "layout": {
                "width": 800,
                "height": 1600,
                "padding": 50
            },
            "colors": {
                "background": "#ffffff",
                "text": "#000000"
            }
        }
        
        template = PosterTemplate(template_data)
        
        assert template.width == 800
        assert template.height == 1600
        assert template.padding == 50
        assert template.background_color == "#ffffff"
        assert template.text_color == "#000000"
    
    def test_template_from_file_valid_json(self):
        """Test loading template from valid JSON file"""
        template_data = {
            "name": "File Template",
            "description": "Loaded from file"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(template_data, f)
            temp_path = Path(f.name)
        
        try:
            template = PosterTemplate.from_file(temp_path)
            assert template.name == "File Template"
            assert template.description == "Loaded from file"
        finally:
            temp_path.unlink()
    
    def test_template_from_file_invalid_json(self):
        """Test error handling for invalid JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(PosterGenerationError, match="Failed to load template"):
                PosterTemplate.from_file(temp_path)
        finally:
            temp_path.unlink()


class TestPosterGenerator:
    """Test PosterGenerator class functionality"""
    
    def test_initialization_without_pil(self):
        """Test initialization fails when PIL is not available"""
        with patch('moka_news.poster.PIL_AVAILABLE', False):
            with pytest.raises(PosterGenerationError, match="Pillow library is required"):
                PosterGenerator({})
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    def test_initialization_with_default_config(self):
        """Test successful initialization with default configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"method": "local", "default_template": "minimal"}
            poster_gen = PosterGenerator(config, posters_dir=Path(temp_dir) / "posters")
            
            assert poster_gen.generation_method == "local"
            assert poster_gen.default_template == "minimal"
            assert poster_gen.posters_dir.exists()
            assert poster_gen.templates_dir.exists()
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    def test_list_templates(self):
        """Test listing available templates"""
        with tempfile.TemporaryDirectory() as temp_dir:
            templates_dir = Path(temp_dir) / "templates"
            config = {"method": "local"}
            
            poster_gen = PosterGenerator(config, templates_dir=templates_dir)
            templates = poster_gen.list_templates()
            
            # Should have default templates
            assert "minimal" in templates
            assert "elegant" in templates
            assert "social" in templates
            assert "modern" in templates
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    def test_load_template(self):
        """Test loading a specific template"""
        with tempfile.TemporaryDirectory() as temp_dir:
            templates_dir = Path(temp_dir) / "templates"
            config = {"method": "local"}
            
            poster_gen = PosterGenerator(config, templates_dir=templates_dir)
            template = poster_gen.load_template("minimal")
            
            assert isinstance(template, PosterTemplate)
            assert template.name == "Minimal"
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    def test_load_nonexistent_template(self):
        """Test error when loading non-existent template"""
        with tempfile.TemporaryDirectory() as temp_dir:
            templates_dir = Path(temp_dir) / "templates"
            config = {"method": "local"}
            
            poster_gen = PosterGenerator(config, templates_dir=templates_dir)
            
            with pytest.raises(PosterGenerationError, match="Template 'nonexistent' not found"):
                poster_gen.load_template("nonexistent")
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    @patch('moka_news.poster.Image')
    @patch('moka_news.poster.ImageDraw')
    @patch('moka_news.poster.ImageFont')
    @patch('moka_news.poster._create_gradient_background')
    @patch('moka_news.poster._draw_rounded_box_with_shadow')
    def test_generate_local_poster_success(
        self, mock_box, mock_gradient, mock_font, mock_draw, mock_image
    ):
        """Test successful local poster generation"""
        # Mock gradient background
        mock_gradient_img = MagicMock()
        mock_gradient_img.mode = "RGBA"
        mock_gradient_img.size = (1080, 1080)
        mock_gradient_img.split.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_gradient.return_value = mock_gradient_img
        
        # Mock box drawing
        mock_box_img = MagicMock()
        mock_box_img.mode = "RGBA"
        mock_box_img.size = (1080, 1080)
        mock_box_img.split.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_box.return_value = mock_box_img
        
        # Mock Image.new for RGB background
        mock_rgb_img = MagicMock()
        mock_image.new.return_value = mock_rgb_img
        
        # Mock draw context
        mock_draw_obj = MagicMock()
        mock_draw.Draw.return_value = mock_draw_obj
        mock_font.load_default.return_value = MagicMock()
        mock_draw_obj.textbbox.return_value = (0, 0, 100, 30)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"method": "local", "default_template": "minimal"}
            poster_gen = PosterGenerator(
                config, 
                posters_dir=Path(temp_dir) / "posters",
                templates_dir=Path(temp_dir) / "templates"
            )
            
            editorial = {
                "title": "Test Editorial",
                "content": "This is a test editorial content.",
                "timestamp": "2024-01-01T10:00:00"
            }
            
            poster_path = poster_gen._generate_local_poster(editorial)
            
            assert poster_path.suffix == ".png"
            assert poster_path.parent == poster_gen.posters_dir
            # Verify gradient and box were created
            mock_gradient.assert_called_once()
            mock_box.assert_called_once()
            # Verify save was called on the final RGB image
            mock_rgb_img.save.assert_called_once()
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    def test_content_cleaning(self):
        """Test markdown content cleaning for poster display"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"method": "local"}
            poster_gen = PosterGenerator(config, posters_dir=Path(temp_dir))
            
            # Test markdown cleaning (no leading whitespace for headers to be removed)
            content = """# This is a header

This is **bold text** and *italic text* and `code text`.

Here's a [link](http://example.com) in the content.

## Another header

More content here with multiple sentences. This should be long enough 
to test the word counting functionality. We want to make sure it handles 
properly when there are many sentences and words."""
            
            cleaned = poster_gen._clean_content_for_poster(content)
            
            # Should remove markdown formatting
            assert "**" not in cleaned
            assert "*" not in cleaned
            assert "`" not in cleaned
            assert "[link](" not in cleaned
            # Headers at start of line (no indent) should be removed
            assert not cleaned.startswith("# ")
    def test_ai_generation_not_implemented(self):
        """Test that AI generation raises not implemented error"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"method": "ai"}
            poster_gen = PosterGenerator(config, posters_dir=Path(temp_dir))
            
            editorial = {"title": "Test", "content": "Test content"}
            
            with pytest.raises(PosterGenerationError, match="AI poster generation not yet implemented"):
                poster_gen._generate_ai_poster(editorial)
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    @patch('moka_news.poster.qrcode')
    @patch('moka_news.poster.QRCODE_AVAILABLE', True)
    def test_qr_code_generation(self, mock_qrcode):
        """Test QR code generation functionality"""
        # Mock qrcode components
        mock_qr = MagicMock()
        mock_qrcode.QRCode.return_value = mock_qr
        mock_qr_img = MagicMock()
        mock_qr_img.resize.return_value = mock_qr_img
        mock_qr_img.mode = "RGB"
        mock_qr.make_image.return_value = mock_qr_img
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"method": "local"}
            poster_gen = PosterGenerator(config, posters_dir=Path(temp_dir))
            
            # Create mock image and template
            mock_img = MagicMock()
            template = PosterTemplate({
                "elements": {"qr_code": True, "qr_position": "bottom_right"},
                "layout": {"width": 1080, "height": 1080, "padding": 60},
                "colors": {"text": "#ffffff", "background": "#000000"}
            })
            
            poster_gen._add_qr_code(mock_img, "https://example.com", template)
            
            # Verify QR code was created
            mock_qrcode.QRCode.assert_called_once()
            mock_qr.add_data.assert_called_once_with("https://example.com")
            mock_qr.make.assert_called_once()
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    def test_wrap_text_functionality(self):
        """Test text wrapping functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"method": "local"}
            poster_gen = PosterGenerator(config, posters_dir=Path(temp_dir))
            
            # Mock draw and font
            mock_draw = MagicMock()
            mock_font = MagicMock()
            
            # Mock textbbox to return predictable widths
            def mock_textbbox(pos, text, font):
                # Return width proportional to text length
                return (0, 0, len(text) * 10, 30)
            
            mock_draw.textbbox = mock_textbbox
            
            text = "This is a long sentence that should be wrapped across multiple lines"
            max_width = 200  # Should fit about 20 characters per line
            
            lines = poster_gen._wrap_text(mock_draw, text, mock_font, max_width)
            
            # Should wrap into multiple lines
            assert len(lines) > 1
            assert all(len(line) <= 25 for line in lines)  # Rough estimate
            
            # All words should be preserved
            all_words = text.split()
            wrapped_words = " ".join(lines).split()
            assert all_words == wrapped_words


class TestPosterIntegration:
    """Integration tests for poster generation"""
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    @patch('moka_news.poster.Image')
    @patch('moka_news.poster.ImageDraw')
    @patch('moka_news.poster.ImageFont')
    @patch('moka_news.poster._create_gradient_background')
    @patch('moka_news.poster._draw_rounded_box_with_shadow')
    def test_full_poster_generation_flow(
        self, mock_box, mock_gradient, mock_font, mock_draw, mock_image
    ):
        """Test complete poster generation workflow"""
        # Mock gradient and box functions
        mock_gradient_img = MagicMock()
        mock_gradient_img.mode = "RGBA"
        mock_gradient_img.size = (1080, 1080)
        mock_gradient_img.split.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_gradient.return_value = mock_gradient_img
        
        mock_box_img = MagicMock()
        mock_box_img.mode = "RGBA"
        mock_box_img.size = (1080, 1080)
        mock_box_img.split.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_box.return_value = mock_box_img
        
        # Mock Image.new for RGB conversion
        mock_rgb_img = MagicMock()
        mock_image.new.return_value = mock_rgb_img
        
        # Mock draw context
        mock_draw_obj = MagicMock()
        mock_draw.Draw.return_value = mock_draw_obj
        mock_draw_obj.textbbox.return_value = (0, 0, 100, 30)
        
        # Mock font loading
        mock_font.load_default.return_value = MagicMock()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "method": "local",
                "default_template": "minimal"
            }
            
            poster_gen = PosterGenerator(
                config,
                posters_dir=Path(temp_dir) / "posters",
                templates_dir=Path(temp_dir) / "templates"
            )
            
            editorial = {
                "title": "Morning Tech Briefing",
                "content": """# Tech News Update

Today's tech landscape brings exciting developments in **AI** and 
*machine learning*. Companies are pushing the boundaries of what's 
possible with [new frameworks](http://example.com) and innovative 
approaches.

## Key Highlights

- Major breakthrough in neural networks
- New open-source project gains traction
- Industry partnerships reshape the market"""
            }
            
            # Generate poster
            poster_path = poster_gen.generate_poster(editorial, "minimal")
            
            # Verify output path is correct
            assert poster_path.suffix == ".png"
            assert poster_path.parent == poster_gen.posters_dir
            
            # Verify gradient was created (minimal template has gradient enabled)
            mock_gradient.assert_called_once()
            
            # Verify PIL save was called
            mock_rgb_img.save.assert_called_once()


class TestGradientGeneration:
    """Test gradient background generation functionality"""
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    def test_gradient_background_vertical(self):
        """Test vertical gradient generation"""
        colors = ["#ff0000", "#0000ff"]  # Red to blue
        width, height = 100, 200
        
        img = _create_gradient_background(width, height, colors, "vertical")
        
        assert img.size == (width, height)
        assert img.mode == "RGB"
        
        # Top pixel should be close to red
        top_pixel = img.getpixel((50, 0))
        assert top_pixel[0] > 200  # High red
        assert top_pixel[2] < 50   # Low blue
        
        # Bottom pixel should be close to blue
        bottom_pixel = img.getpixel((50, 199))
        assert bottom_pixel[0] < 50   # Low red
        assert bottom_pixel[2] > 200  # High blue
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    def test_gradient_background_diagonal(self):
        """Test diagonal gradient generation"""
        colors = ["#ffffff", "#000000"]  # White to black
        width, height = 100, 100
        
        img = _create_gradient_background(width, height, colors, "diagonal")
        
        assert img.size == (width, height)
        
        # Top-left should be lighter
        top_left = img.getpixel((0, 0))
        assert all(c > 200 for c in top_left)
        
        # Bottom-right should be darker
        bottom_right = img.getpixel((99, 99))
        assert all(c < 100 for c in bottom_right)
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    def test_gradient_with_preset(self):
        """Test gradient generation with preset colors"""
        preset_colors = DEFAULT_GRADIENT_PRESETS["purple-pink"]
        
        img = _create_gradient_background(100, 100, preset_colors, "vertical")
        
        assert img is not None
        assert img.size == (100, 100)
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    def test_gradient_fallback_single_color(self):
        """Test gradient fallback when only one color provided"""
        colors = ["#ff0000"]
        
        img = _create_gradient_background(100, 100, colors, "vertical")
        
        # Should create solid color image
        assert img is not None
        assert img.size == (100, 100)
    
    def test_color_interpolation_two_colors(self):
        """Test color interpolation between two colors"""
        colors = [(255, 0, 0), (0, 0, 255)]  # Red to blue
        
        # At 0, should be red
        result = _interpolate_colors(colors, 0.0)
        assert result == (255, 0, 0)
        
        # At 1, should be blue
        result = _interpolate_colors(colors, 1.0)
        assert result == (0, 0, 255)
        
        # At 0.5, should be purple-ish
        result = _interpolate_colors(colors, 0.5)
        assert result == (127, 0, 127)
    
    def test_color_interpolation_multiple_colors(self):
        """Test color interpolation with more than two colors"""
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Red, green, blue
        
        # At 0, should be red
        result = _interpolate_colors(colors, 0.0)
        assert result == (255, 0, 0)
        
        # At 0.5, should be green
        result = _interpolate_colors(colors, 0.5)
        assert result == (0, 255, 0)
        
        # At 1.0, should be blue
        result = _interpolate_colors(colors, 1.0)
        assert result == (0, 0, 255)


class TestContentBox:
    """Test content box with shadow functionality"""
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    @patch('moka_news.poster.Image')
    @patch('moka_news.poster.ImageDraw')
    @patch('moka_news.poster.ImageFilter')
    def test_rounded_box_with_shadow(self, mock_filter, mock_draw, mock_image):
        """Test drawing rounded box with shadow"""
        # Mock components
        mock_base_img = MagicMock()
        mock_base_img.size = (1080, 1080)
        mock_base_img.mode = "RGB"
        mock_rgba_img = MagicMock()
        mock_base_img.convert.return_value = mock_rgba_img
        
        mock_shadow_layer = MagicMock()
        mock_image.new.return_value = mock_shadow_layer
        mock_shadow_layer.filter.return_value = mock_shadow_layer
        
        mock_image.alpha_composite.return_value = mock_rgba_img
        
        mock_draw_obj = MagicMock()
        mock_draw.Draw.return_value = mock_draw_obj
        
        shadow_config = {
            "offset_x": 4,
            "offset_y": 4,
            "blur": 12,
            "color": "rgba(0,0,0,0.15)"
        }
        
        result = _draw_rounded_box_with_shadow(
            mock_base_img,
            (100, 100),
            (800, 1600),
            20,
            shadow_config,
            "#ffffff"
        )
        
        assert result is not None
        mock_draw_obj.rounded_rectangle.assert_called()
    
    def test_template_with_gradient_enabled(self):
        """Test PosterTemplate with gradient configuration"""
        template_data = {
            "name": "Gradient Test",
            "gradient": {
                "enabled": True,
                "type": "vertical",
                "colors": ["#ff0000", "#0000ff"]
            }
        }
        
        template = PosterTemplate(template_data)
        
        assert template.gradient_enabled is True
        assert template.gradient_type == "vertical"
        assert template.gradient_colors == ["#ff0000", "#0000ff"]
    
    def test_template_with_gradient_preset(self):
        """Test PosterTemplate with gradient preset"""
        template_data = {
            "name": "Preset Test",
            "gradient": {
                "enabled": True,
                "type": "vertical",
                "preset": "purple-pink"
            }
        }
        
        template = PosterTemplate(template_data)
        
        assert template.gradient_enabled is True
        assert template.gradient_preset == "purple-pink"
        assert template.gradient_colors == DEFAULT_GRADIENT_PRESETS["purple-pink"]
    
    def test_template_with_content_box(self):
        """Test PosterTemplate with content box configuration"""
        template_data = {
            "name": "Box Test",
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
            }
        }
        
        template = PosterTemplate(template_data)
        
        assert template.content_box_enabled is True
        assert template.content_box_background == "#ffffff"
        assert template.content_box_padding == 40
        assert template.content_box_radius == 20
        assert template.shadow_offset_x == 4
        assert template.shadow_offset_y == 4
        assert template.shadow_blur == 12
    
    def test_template_backward_compatibility(self):
        """Test that templates without gradient/content_box still work"""
        template_data = {
            "name": "Old Template",
            "colors": {
                "background": "#000000"
            }
        }
        
        template = PosterTemplate(template_data)
        
        # Should have default values
        assert template.gradient_enabled is False
        assert template.content_box_enabled is False
        assert template.background_color == "#000000"


class TestFontLoading:
    """Test custom font loading functionality"""
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    @patch('moka_news.poster.ImageFont')
    def test_load_font_with_bundled_font(self, mock_font):
        """Test loading bundled font files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"method": "local"}
            poster_gen = PosterGenerator(config, posters_dir=Path(temp_dir))
            
            mock_font.truetype.return_value = MagicMock()
            
            # Try to load bundled font
            font = poster_gen._load_font("Inter-Regular.ttf", "arial", 24)
            
            assert font is not None
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    @patch('moka_news.poster.ImageFont')
    def test_load_font_fallback_to_system(self, mock_font):
        """Test fallback to system font when custom font not found"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"method": "local"}
            poster_gen = PosterGenerator(config, posters_dir=Path(temp_dir))
            
            # Mock font loading to fail for custom, succeed for system
            def mock_truetype(name, size):
                if "nonexistent" in str(name):
                    raise Exception("Font not found")
                return MagicMock()
            
            mock_font.truetype.side_effect = mock_truetype
            mock_font.load_default.return_value = MagicMock()
            
            # Should fallback to system font
            font = poster_gen._load_font("nonexistent.ttf", "arial", 24)
            assert font is not None
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    @patch('moka_news.poster.ImageFont')
    def test_load_font_fallback_to_default(self, mock_font):
        """Test fallback to default font when all else fails"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"method": "local"}
            poster_gen = PosterGenerator(config, posters_dir=Path(temp_dir))
            
            # Mock all font loading to fail
            mock_font.truetype.side_effect = Exception("No fonts available")
            mock_default = MagicMock()
            mock_font.load_default.return_value = mock_default
            
            font = poster_gen._load_font("any.ttf", "any_family", 24)
            
            assert font == mock_default
            mock_font.load_default.assert_called_once()


class TestEnhancedPosterGeneration:
    """Test enhanced poster generation with gradients and content boxes"""
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    @patch('moka_news.poster.Image')
    @patch('moka_news.poster.ImageDraw')
    @patch('moka_news.poster.ImageFont')
    @patch('moka_news.poster._create_gradient_background')
    @patch('moka_news.poster._draw_rounded_box_with_shadow')
    def test_generate_poster_with_gradient_and_box(
        self, mock_box, mock_gradient, mock_font, mock_draw, mock_image
    ):
        """Test poster generation with gradient and content box enabled"""
        # Mock gradient background
        mock_gradient_img = MagicMock()
        mock_gradient_img.mode = "RGBA"
        mock_gradient_img.size = (1080, 1080)
        mock_gradient.return_value = mock_gradient_img
        
        # Mock box drawing
        mock_rgba_img = MagicMock()
        mock_rgba_img.mode = "RGBA"
        mock_rgba_img.size = (1080, 1080)
        mock_rgba_img.split.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        mock_box.return_value = mock_rgba_img
        
        # Mock Image.new for RGB background
        mock_rgb_bg = MagicMock()
        mock_image.new.return_value = mock_rgb_bg
        
        # Mock draw context
        mock_draw_obj = MagicMock()
        mock_draw.Draw.return_value = mock_draw_obj
        mock_draw_obj.textbbox.return_value = (0, 0, 100, 30)
        
        # Mock font loading
        mock_font.load_default.return_value = MagicMock()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create template with gradient and content box
            templates_dir = Path(temp_dir) / "templates"
            templates_dir.mkdir()
            
            template_data = {
                "name": "Enhanced",
                "gradient": {
                    "enabled": True,
                    "type": "vertical",
                    "colors": ["#ff0000", "#0000ff"]
                },
                "content_box": {
                    "enabled": True,
                    "background": "#ffffff",
                    "padding": 40,
                    "border_radius": 20
                }
            }
            
            import json
            with open(templates_dir / "enhanced.json", 'w') as f:
                json.dump(template_data, f)
            
            config = {"method": "local", "default_template": "enhanced"}
            poster_gen = PosterGenerator(
                config,
                posters_dir=Path(temp_dir) / "posters",
                templates_dir=templates_dir
            )
            
            editorial = {
                "title": "Test Editorial",
                "content": "Test content"
            }
            
            poster_path = poster_gen._generate_local_poster(editorial, "enhanced")
            
            # Verify gradient was created
            mock_gradient.assert_called_once()
            
            # Verify content box was drawn
            mock_box.assert_called_once()
            
            # Verify poster was saved
            assert poster_path.suffix == ".png"
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    def test_custom_options_override_gradient(self):
        """Test that custom options can override gradient settings"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"method": "local", "default_template": "minimal"}
            poster_gen = PosterGenerator(
                config,
                posters_dir=Path(temp_dir) / "posters",
                templates_dir=Path(temp_dir) / "templates"
            )
            
            template = poster_gen.load_template("minimal")
            
            # Override gradient colors via custom options
            custom_options = {
                "gradient": {
                    "colors": ["#00ff00", "#ff00ff"]
                }
            }
            
            # Apply custom options
            for key, value in custom_options.items():
                if key == "gradient" and isinstance(value, dict):
                    for gkey, gval in value.items():
                        attr_name = f"gradient_{gkey}"
                        if hasattr(template, attr_name):
                            setattr(template, attr_name, gval)
            
            assert template.gradient_colors == ["#00ff00", "#ff00ff"]


if __name__ == "__main__":
    pytest.main([__file__])