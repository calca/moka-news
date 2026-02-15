"""
Tests for the Editorial Generator
"""

from moka_news.editorial import EditorialGenerator
from moka_news.barista import SimpleBarista
from datetime import datetime
import tempfile
import shutil
from pathlib import Path


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
