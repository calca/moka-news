"""
Tests for external prompts functionality
"""

import pytest
from moka_news.config import DEFAULT_PROMPTS, load_config
from moka_news.barista import _build_prompt, Barista, SimpleBarista


def test_default_prompts_structure():
    """Test that default prompts have the expected structure"""
    assert "system_message" in DEFAULT_PROMPTS
    assert "user_prompt" in DEFAULT_PROMPTS
    assert "keywords_section" in DEFAULT_PROMPTS
    assert "format_section" in DEFAULT_PROMPTS


def test_default_prompts_contain_placeholders():
    """Test that default prompts contain required placeholders"""
    assert "{title}" in DEFAULT_PROMPTS["user_prompt"]
    assert "{content}" in DEFAULT_PROMPTS["user_prompt"]
    assert "{keywords}" in DEFAULT_PROMPTS["keywords_section"]


def test_build_prompt_with_default_prompts():
    """Test building a prompt with default prompts"""
    article = {
        "title": "Test Article",
        "summary": "This is a test summary."
    }
    
    prompt = _build_prompt(article)
    
    assert "Test Article" in prompt
    assert "This is a test summary." in prompt
    assert "TITLE:" in prompt
    assert "SUMMARY:" in prompt


def test_build_prompt_with_keywords():
    """Test building a prompt with keywords"""
    article = {
        "title": "Test Article",
        "summary": "This is a test summary."
    }
    keywords = ["technology", "AI"]
    
    prompt = _build_prompt(article, keywords)
    
    assert "Test Article" in prompt
    assert "technology, AI" in prompt


def test_build_prompt_with_custom_prompts():
    """Test building a prompt with custom prompts"""
    article = {
        "title": "Test Article",
        "summary": "This is a test summary."
    }
    
    custom_prompts = {
        "user_prompt": "Custom prompt: {title} - {content}",
        "keywords_section": " Keywords: {keywords}",
        "format_section": " Output format here"
    }
    
    prompt = _build_prompt(article, None, custom_prompts)
    
    assert "Custom prompt:" in prompt
    assert "Test Article" in prompt
    assert "Output format here" in prompt


def test_build_prompt_with_custom_prompts_and_keywords():
    """Test building a prompt with both custom prompts and keywords"""
    article = {
        "title": "Test Article",
        "summary": "This is a test summary."
    }
    keywords = ["python", "programming"]
    
    custom_prompts = {
        "user_prompt": "Analyze: {title} | {content}",
        "keywords_section": " Focus: {keywords}",
        "format_section": " Return JSON"
    }
    
    prompt = _build_prompt(article, keywords, custom_prompts)
    
    assert "Analyze:" in prompt
    assert "Test Article" in prompt
    assert "Focus: python, programming" in prompt
    assert "Return JSON" in prompt


def test_barista_with_prompts():
    """Test that Barista accepts and stores prompts"""
    custom_prompts = {
        "user_prompt": "Custom: {title}",
        "keywords_section": "",
        "format_section": ""
    }
    
    barista = Barista(SimpleBarista(), keywords=[], prompts=custom_prompts)
    
    assert barista.prompts == custom_prompts


def test_barista_processes_articles_with_custom_prompts():
    """Test that Barista processes articles with custom prompts"""
    custom_prompts = {
        "user_prompt": "Summarize: {title} - {content}",
        "keywords_section": "",
        "format_section": "\nTITLE: <title>\nSUMMARY: <summary>"
    }
    
    barista = Barista(SimpleBarista(), keywords=[], prompts=custom_prompts)
    
    articles = [
        {
            "title": "Article 1",
            "summary": "Summary 1",
            "link": "https://example.com/1",
            "published": "2026-01-01",
            "source": "Test Source",
        }
    ]
    
    processed = barista.brew(articles)
    
    assert len(processed) == 1
    assert "ai_title" in processed[0]
    assert "ai_summary" in processed[0]


def test_config_includes_prompts():
    """Test that loaded config includes prompts"""
    config = load_config()
    
    assert "prompts" in config["ai"]
    assert "system_message" in config["ai"]["prompts"]
    assert "user_prompt" in config["ai"]["prompts"]


def test_build_prompt_truncates_long_content():
    """Test that build_prompt truncates content to 1500 characters"""
    article = {
        "title": "Test",
        "summary": "A" * 2000  # Very long content
    }
    
    prompt = _build_prompt(article)
    
    # Check that content was truncated (should be 1500 chars)
    assert "A" * 1500 in prompt
    assert "A" * 1501 not in prompt
