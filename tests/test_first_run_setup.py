"""
Tests for first-run setup module
"""

import os
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from moka_news.first_run_setup import (
    is_first_run,
    check_cli_available,
    save_config,
    SUGGESTED_TECH_FEEDS,
    AI_PROVIDERS
)


def test_suggested_tech_feeds():
    """Test that suggested tech feeds list is properly formatted"""
    assert len(SUGGESTED_TECH_FEEDS) == 5
    
    for feed in SUGGESTED_TECH_FEEDS:
        assert "url" in feed
        assert "title" in feed
        assert "htmlUrl" in feed
        assert feed["url"].startswith("http")


def test_ai_providers_structure():
    """Test that AI providers dict has expected structure"""
    assert "openai" in AI_PROVIDERS
    assert "anthropic" in AI_PROVIDERS
    assert "gemini" in AI_PROVIDERS
    assert "mistral" in AI_PROVIDERS
    assert "copilot-cli" in AI_PROVIDERS
    
    # Check structure of one provider
    openai = AI_PROVIDERS["openai"]
    assert "name" in openai
    assert "requires_api_key" in openai
    assert openai["requires_api_key"] is True


def test_is_first_run_with_no_config():
    """Test first run detection when no config exists"""
    with patch('pathlib.Path.exists', return_value=False):
        assert is_first_run() is True


def test_is_first_run_with_existing_config():
    """Test first run detection when config exists"""
    def mock_exists(self):
        # Return True for the first config location
        return str(self).endswith("moka-news.yaml")
    
    with patch.object(Path, 'exists', mock_exists):
        assert is_first_run() is False


def test_check_cli_available():
    """Test CLI availability check"""
    # Test with a command that should exist
    assert check_cli_available("python") or check_cli_available("python3")
    
    # Test with a command that shouldn't exist
    assert check_cli_available("nonexistent-command-xyz") is False


def test_save_config(tmp_path):
    """Test saving configuration to file"""
    config_path = tmp_path / "config.yaml"
    
    config_data = {
        "provider": "openai",
        "api_key": "test-key"
    }
    
    result_path = save_config(config_data, config_path)
    
    assert result_path == config_path
    assert config_path.exists()
    
    # Read and verify content
    with open(config_path, 'r') as f:
        saved_config = yaml.safe_load(f)
    
    assert saved_config["ai"]["provider"] == "openai"
    assert "api_keys" in saved_config["ai"]
    assert saved_config["ui"]["use_tui"] is True


def test_save_config_creates_directory(tmp_path):
    """Test that save_config creates parent directories"""
    config_path = tmp_path / "subdir" / "config.yaml"
    
    config_data = {
        "provider": "anthropic",
    }
    
    result_path = save_config(config_data, config_path)
    
    assert config_path.exists()
    assert config_path.parent.exists()


def test_save_config_includes_keywords(tmp_path):
    """Test that save_config includes keywords when provided"""
    config_path = tmp_path / "config.yaml"
    
    config_data = {
        "provider": "openai",
        "keywords": ["technology", "AI", "programming"]
    }
    
    result_path = save_config(config_data, config_path)
    
    assert config_path.exists()
    
    # Read and verify content
    with open(config_path, 'r') as f:
        saved_config = yaml.safe_load(f)
    
    assert "keywords" in saved_config["ai"]
    assert saved_config["ai"]["keywords"] == ["technology", "AI", "programming"]


def test_save_config_defaults_empty_keywords(tmp_path):
    """Test that save_config defaults to empty keywords list"""
    config_path = tmp_path / "config.yaml"
    
    config_data = {
        "provider": "gemini"
    }
    
    result_path = save_config(config_data, config_path)
    
    # Read and verify content
    with open(config_path, 'r') as f:
        saved_config = yaml.safe_load(f)
    
    assert "keywords" in saved_config["ai"]
    assert saved_config["ai"]["keywords"] == []
