"""
Tests for poster generation functionality
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from moka_news.poster import PosterGenerator, PosterTemplate, PosterGenerationError


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
        assert template.height == 1920
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
    def test_generate_local_poster_success(self, mock_font, mock_draw, mock_image):
        """Test successful local poster generation"""
        # Mock PIL components
        mock_img = MagicMock()
        mock_image.new.return_value = mock_img
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
            mock_img.save.assert_called_once()
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
    def test_content_cleaning(self):
        """Test markdown content cleaning for poster display"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {"method": "local"}
            poster_gen = PosterGenerator(config, posters_dir=Path(temp_dir))
            
            # Test markdown cleaning
            content = """
            # This is a header
            
            This is **bold text** and *italic text* and `code text`.
            
            Here's a [link](http://example.com) in the content.
            
            ## Another header
            
            More content here with multiple sentences. This should be long enough 
            to test the word counting functionality. We want to make sure it handles
            properly when there are many sentences and words.
            """
            
            cleaned = poster_gen._clean_content_for_poster(content)
            
            # Should remove markdown formatting
            assert "**" not in cleaned
            assert "*" not in cleaned
            assert "`" not in cleaned
            assert "[link](" not in cleaned
            assert "# " not in cleaned
            assert "## " not in cleaned
            
            # Should contain the actual text
            assert "This is bold text and italic text and code text" in cleaned
            assert "link" in cleaned  # Link text should remain
    
    @patch('moka_news.poster.PIL_AVAILABLE', True)
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
                "layout": {"width": 1080, "height": 1920, "padding": 80},
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
    def test_full_poster_generation_flow(self, mock_font, mock_draw, mock_image):
        """Test complete poster generation workflow"""
        # Mock PIL components
        mock_img = MagicMock()
        mock_image.new.return_value = mock_img
        mock_draw_obj = MagicMock()
        mock_draw.Draw.return_value = mock_draw_obj
        mock_font.load_default.return_value = MagicMock()
        mock_draw_obj.textbbox.return_value = (0, 0, 100, 30)
        
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
                "content": """
                # Tech News Update
                
                Today's tech landscape brings exciting developments in **AI** and 
                *machine learning*. Companies are pushing the boundaries of what's 
                possible with [new frameworks](http://example.com) and innovative 
                approaches.
                
                ## Key Highlights
                
                - Major breakthrough in neural networks
                - New open-source project gains traction
                - Industry partnerships reshape the market
                """
            }
            
            # Generate poster
            poster_path = poster_gen.generate_poster(editorial, "minimal")
            
            # Verify output
            assert poster_path.exists()
            assert poster_path.suffix == ".png"
            assert poster_path.parent == poster_gen.posters_dir
            
            # Verify PIL interactions
            mock_image.new.assert_called_once()
            mock_draw.Draw.assert_called_once()
            mock_img.save.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])