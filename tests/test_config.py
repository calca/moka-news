"""
Tests for configuration module
"""

from moka_news.config import (
    load_config,
    merge_configs,
    create_sample_config,
    DEFAULT_CONFIG,
)


def test_default_config_structure():
    """Test that default config has expected structure"""
    assert "ai" in DEFAULT_CONFIG
    assert "feeds" in DEFAULT_CONFIG
    assert "ui" in DEFAULT_CONFIG
    assert "provider" in DEFAULT_CONFIG["ai"]
    assert "api_keys" in DEFAULT_CONFIG["ai"]


def test_load_config_without_file():
    """Test loading config when no config file exists"""
    config = load_config("/nonexistent/path/config.yaml")

    # Should return default config (gemini-cli is now default)
    assert config["ai"]["provider"] == "gemini-cli"
    assert "urls" in config["feeds"]
    assert config["ui"]["use_tui"] is True


def test_merge_configs():
    """Test merging configurations"""
    default = {
        "ai": {"provider": "simple", "api_keys": {"openai": None}},
        "feeds": {"urls": ["feed1"]},
    }

    user = {
        "ai": {
            "provider": "openai",
        },
        "feeds": {"urls": ["feed2", "feed3"]},
    }

    result = merge_configs(default, user)

    assert result["ai"]["provider"] == "openai"
    assert result["ai"]["api_keys"]["openai"] is None  # Preserved from default
    assert result["feeds"]["urls"] == ["feed2", "feed3"]


def test_create_sample_config(tmp_path):
    """Test creating a sample config file"""
    config_path = tmp_path / "test-config.yaml"
    create_sample_config(str(config_path))

    assert config_path.exists()

    # Read the file and check it contains expected content
    content = config_path.read_text()
    assert "ai:" in content
    assert "provider:" in content
    assert "feeds:" in content


def test_config_respects_env_vars(monkeypatch):
    """Test that environment variables override config"""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")

    config = load_config()

    assert config["ai"]["api_keys"]["openai"] == "test-key-123"


def test_default_config_includes_keywords():
    """Test that default config includes keywords field"""
    assert "keywords" in DEFAULT_CONFIG["ai"]
    assert isinstance(DEFAULT_CONFIG["ai"]["keywords"], list)
    assert len(DEFAULT_CONFIG["ai"]["keywords"]) == 0


def test_merge_configs_preserves_keywords():
    """Test merging configurations preserves keywords"""
    default = {
        "ai": {
            "provider": "simple",
            "api_keys": {"openai": None},
            "keywords": [],
        },
        "feeds": {"urls": ["feed1"]},
    }

    user = {
        "ai": {
            "provider": "openai",
            "keywords": ["technology", "AI"],
        },
        "feeds": {"urls": ["feed2"]},
    }

    result = merge_configs(default, user)

    assert result["ai"]["provider"] == "openai"
    assert result["ai"]["keywords"] == ["technology", "AI"]
    assert result["ai"]["api_keys"]["openai"] is None  # Preserved from default


def test_default_config_includes_editorial():
    """Test that default config includes editorial configuration"""
    assert "editorial" in DEFAULT_CONFIG
    assert "editorials_dir" in DEFAULT_CONFIG["editorial"]
    assert "opener_command" in DEFAULT_CONFIG["editorial"]
    assert DEFAULT_CONFIG["editorial"]["editorials_dir"] is None
    assert DEFAULT_CONFIG["editorial"]["opener_command"] is None


def test_merge_configs_preserves_editorial_settings():
    """Test merging configurations preserves editorial settings"""
    default = {
        "editorial": {
            "editorials_dir": None,
            "opener_command": None,
        },
        "ai": {"provider": "simple"},
    }

    user = {
        "editorial": {
            "editorials_dir": "/custom/path",
            "opener_command": "code",
        },
    }

    result = merge_configs(default, user)

    assert result["editorial"]["editorials_dir"] == "/custom/path"
    assert result["editorial"]["opener_command"] == "code"
    assert result["ai"]["provider"] == "simple"  # Preserved from default
