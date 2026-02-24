"""
Tests for the Editorial Generator
"""

from moka_news.editorial import EditorialGenerator
from moka_news.barista import SimpleBarista
from datetime import datetime
import tempfile
from pathlib import Path
import pytest


class FailingBarista(SimpleBarista):
    """Test provider that always fails in editorial mode."""

    def _invoke_ai(self, system_message, user_prompt, max_tokens=4096):
        raise RuntimeError("'gemini' CLI timed out after 120s")


def test_editorial_generator_initialization():
    """Test EditorialGenerator initialization"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = EditorialGenerator(
            ai_provider=SimpleBarista(),
            keywords=["test", "keyword"],
            editorials_dir=tmpdir
        )
        assert generator.ai_provider is not None
        assert generator.keywords == ["test", "keyword"]
        assert generator.editorials_dir == Path(tmpdir)
        assert generator.editorials_dir.exists()


def test_generate_editorial_empty_articles():
    """Test generating editorial with empty articles list"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = EditorialGenerator(
            ai_provider=SimpleBarista(),
            editorials_dir=tmpdir
        )
        editorial = generator.generate_editorial([])
        
        assert editorial["title"] == "Good Morning!"
        assert "No news articles" in editorial["content"]
        assert editorial["article_count"] == 0
        assert editorial["sources"] == []


def test_generate_editorial_with_articles():
    """Test generating editorial with articles"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = EditorialGenerator(
            ai_provider=SimpleBarista(),
            editorials_dir=tmpdir
        )
        
        articles = [
            {
                "title": "Test Article 1",
                "ai_title": "AI Title 1",
                "summary": "Test summary 1",
                "ai_summary": "AI summary 1",
                "link": "https://example.com/1",
                "source": "Test Source 1"
            },
            {
                "title": "Test Article 2",
                "ai_title": "AI Title 2",
                "summary": "Test summary 2",
                "ai_summary": "AI summary 2",
                "link": "https://example.com/2",
                "source": "Test Source 2"
            }
        ]
        
        editorial = generator.generate_editorial(articles)
        
        assert editorial["title"] is not None
        assert editorial["content"] is not None
        assert editorial["article_count"] == 2
        assert len(editorial["sources"]) == 2
        assert isinstance(editorial["timestamp"], datetime)


def test_save_and_load_editorial():
    """Test saving and loading editorial"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = EditorialGenerator(
            ai_provider=SimpleBarista(),
            editorials_dir=tmpdir
        )
        
        editorial = {
            "title": "Test Editorial",
            "content": "This is test content",
            "timestamp": datetime.now(),
            "sources": [
                {"title": "Source 1", "url": "https://example.com/1", "source": "Test"}
            ],
            "article_count": 1
        }
        
        # Save editorial
        filepath = generator.save_editorial(editorial)
        assert filepath.exists()
        
        # Load editorial
        content = generator.load_editorial(filepath)
        assert "Test Editorial" in content
        assert "This is test content" in content
        assert "Source 1" in content


def test_list_editorials():
    """Test listing editorials"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = EditorialGenerator(
            ai_provider=SimpleBarista(),
            editorials_dir=tmpdir
        )
        
        # Initially empty
        editorials = generator.list_editorials()
        assert editorials == []
        
        # Create one editorial
        editorial = {
            "title": "Test Editorial",
            "content": "Test content",
            "timestamp": datetime.now(),
            "sources": [],
            "article_count": 0
        }
        generator.save_editorial(editorial)
        
        # Should have one editorial
        editorials = generator.list_editorials()
        assert len(editorials) == 1
        assert editorials[0]["title"] == "Test Editorial"


def test_format_editorial_markdown():
    """Test markdown formatting"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = EditorialGenerator(
            ai_provider=SimpleBarista(),
            editorials_dir=tmpdir
        )
        
        editorial = {
            "title": "Morning News",
            "content": "Today's news content",
            "timestamp": datetime(2024, 2, 14, 8, 0, 0),
            "sources": [
                {"title": "Article 1", "url": "https://example.com/1", "source": "Source A"},
                {"title": "Article 2", "url": "", "source": "Source B"}
            ],
            "article_count": 2
        }
        
        markdown = generator._format_editorial_markdown(editorial)
        
        assert "# Morning News" in markdown
        assert "Today's news content" in markdown
        assert "## Sources" in markdown
        assert "Article 1" in markdown
        assert "https://example.com/1" in markdown
        assert "Article 2" in markdown
        assert "Editorial generated from 2 articles" in markdown


def test_editorial_generator_custom_directory():
    """Test EditorialGenerator with custom directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_dir = Path(tmpdir) / "custom" / "editorials"
        generator = EditorialGenerator(
            ai_provider=SimpleBarista(),
            editorials_dir=custom_dir
        )
        
        assert generator.editorials_dir == custom_dir
        assert generator.editorials_dir.exists()
        
        # Test saving to custom directory
        editorial = {
            "title": "Test Editorial",
            "content": "Test content",
            "timestamp": datetime.now(),
            "sources": [],
            "article_count": 0
        }
        
        filepath = generator.save_editorial(editorial)
        assert filepath.parent == custom_dir
        assert filepath.exists()


def test_editorial_generator_default_directory():
    """Test EditorialGenerator uses default directory when none specified"""
    generator = EditorialGenerator(
        ai_provider=SimpleBarista()
    )
    
    expected_dir = Path.home() / ".config" / "moka-news" / "editorials"
    assert generator.editorials_dir == expected_dir


def test_editorial_generator_default_language():
    """Test EditorialGenerator defaults to English"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = EditorialGenerator(
            ai_provider=SimpleBarista(),
            editorials_dir=tmpdir
        )
        assert generator.language == "en"


def test_editorial_generator_custom_language():
    """Test EditorialGenerator with custom language"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = EditorialGenerator(
            ai_provider=SimpleBarista(),
            editorials_dir=tmpdir,
            language="it"
        )
        assert generator.language == "it"


def test_editorial_prompts_language_injection():
    """Test that non-English language is injected into prompts"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = EditorialGenerator(
            ai_provider=SimpleBarista(),
            editorials_dir=tmpdir,
            language="it"
        )
        prompts = generator._get_editorial_prompts()
        assert "Italian" in prompts["system_message"]


def test_editorial_prompts_english_no_injection():
    """Test that English language does not add extra instruction"""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = EditorialGenerator(
            ai_provider=SimpleBarista(),
            editorials_dir=tmpdir,
            language="en"
        )
        prompts = generator._get_editorial_prompts()
        # Should not contain the IMPORTANT language instruction
        assert "IMPORTANT: Write the ENTIRE editorial" not in prompts["system_message"]


def test_editorial_prompts_all_supported_languages():
    """Test that all supported languages inject correctly"""
    from moka_news.constants import SUPPORTED_LANGUAGES
    with tempfile.TemporaryDirectory() as tmpdir:
        for code, name in SUPPORTED_LANGUAGES.items():
            generator = EditorialGenerator(
                ai_provider=SimpleBarista(),
                editorials_dir=tmpdir,
                language=code
            )
            prompts = generator._get_editorial_prompts()
            if code != "en":
                assert name in prompts["system_message"]


def test_generate_editorial_raises_on_ai_failure():
    """AI failures should propagate so callers can load previous editorials."""
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = EditorialGenerator(
            ai_provider=FailingBarista(),
            editorials_dir=tmpdir
        )
        articles = [
            {
                "title": "Test Article",
                "summary": "Test summary",
                "link": "https://example.com/1",
                "source": "Test Source"
            }
        ]

        with pytest.raises(RuntimeError, match="Error generating editorial with AI"):
            generator.generate_editorial(articles)
