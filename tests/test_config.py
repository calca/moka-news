"""
Tests for configuration module
"""

import yaml

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
    parsed = yaml.safe_load(content)
    assert (
        "feeds" not in parsed
    )  # Feeds are managed via OPML, not YAML top-level config
    assert "OPML" in content or "opml" in content  # Should mention OPML feed management


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


def test_default_config_includes_language():
    """Test that default config includes language field"""
    assert "language" in DEFAULT_CONFIG["ai"]
    assert DEFAULT_CONFIG["ai"]["language"] == "en"


def test_merge_configs_preserves_language():
    """Test merging configurations preserves language setting"""
    default = {
        "ai": {
            "provider": "simple",
            "language": "en",
            "api_keys": {"openai": None},
        },
    }

    user = {
        "ai": {
            "language": "it",
        },
    }

    result = merge_configs(default, user)

    assert result["ai"]["language"] == "it"
    assert result["ai"]["provider"] == "simple"  # Preserved from default


def test_default_config_includes_editorial():
    """Test that default config includes editorial configuration"""
    assert "editorial" in DEFAULT_CONFIG
    assert "editorials_dir" in DEFAULT_CONFIG["editorial"]
    assert DEFAULT_CONFIG["editorial"]["editorials_dir"] is None


def test_merge_configs_preserves_editorial_settings():
    """Test merging configurations preserves editorial settings"""
    default = {
        "editorial": {
            "editorials_dir": None,
        },
        "ai": {"provider": "simple"},
    }

    user = {
        "editorial": {
            "editorials_dir": "/custom/path",
        },
    }

    result = merge_configs(default, user)

    assert result["editorial"]["editorials_dir"] == "/custom/path"
    assert result["ai"]["provider"] == "simple"  # Preserved from default


def test_default_config_includes_publish():
    """Test that default config includes publish configuration."""
    assert "publish" in DEFAULT_CONFIG
    assert "providers" in DEFAULT_CONFIG["publish"]
    assert isinstance(DEFAULT_CONFIG["publish"]["providers"], list)


def test_writeas_env_vars_read_by_publisher_directly():
    """Write.as env vars are read by WriteAsPublisher, not by load_config."""
    config = load_config("/nonexistent/path/config.yaml")
    # config no longer has a top-level "writeas" key;
    # env vars are consumed by WriteAsPublisher.__init__ itself.
    assert "writeas" not in config
