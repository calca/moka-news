"""
Tests for The Barista component
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from moka_news.barista import (
    SimpleBarista,
    AIProvider,
    AzureAIBarista,
    GeminiBarista,
    MistralBarista,
    create_ai_provider,
    GitHubCopilotCLIBarista,
    GeminiCLIBarista,
    MistralCLIBarista,
)


def test_simple_barista_initialization():
    """Test that SimpleBarista can be initialized"""
    barista = SimpleBarista()
    assert isinstance(barista, AIProvider)


def test_simple_barista_generates_summary():
    """Test that SimpleBarista generates summaries"""
    barista = SimpleBarista()
    article = {
        "title": "Test Article Title",
        "summary": "This is a test summary that should be truncated to 200 characters maximum.",
    }
    result = barista.generate_summary(article)

    assert "title" in result
    assert "summary" in result
    assert len(result["summary"]) <= 200


def test_simple_barista_processes_articles():
    """Test that SimpleBarista processes a list of articles via generate_summary"""
    provider = SimpleBarista()
    articles = [
        {
            "title": "Article 1",
            "summary": "Summary 1",
            "link": "https://example.com/1",
            "published": "2026-01-01",
            "source": "Test Source",
        },
        {
            "title": "Article 2",
            "summary": "Summary 2",
            "link": "https://example.com/2",
            "published": "2026-01-02",
            "source": "Test Source",
        },
    ]

    processed = []
    for article in articles:
        result = provider.generate_summary(article)
        processed_article = article.copy()
        processed_article["ai_title"] = result["title"]
        processed_article["ai_summary"] = result["summary"]
        processed.append(processed_article)

    assert len(processed) == 2
    assert all("ai_title" in article for article in processed)
    assert all("ai_summary" in article for article in processed)


def test_simple_barista_with_keywords():
    """Test that SimpleBarista processes articles (keywords do not affect pass-through)"""
    provider = SimpleBarista()
    articles = [
        {
            "title": "Article 1",
            "summary": "Summary about technology",
            "link": "https://example.com/1",
            "published": "2026-01-01",
            "source": "Test Source",
        },
    ]

    result = provider.generate_summary(articles[0])

    assert "title" in result
    assert "summary" in result


def test_simple_barista_handles_empty_list():
    """Test that processing empty list returns empty"""
    provider = SimpleBarista()
    articles = []
    processed = [provider.generate_summary(a) for a in articles]
    assert processed == []


def test_simple_barista_truncates_long_title():
    """Test that SimpleBarista truncates long titles"""
    barista = SimpleBarista()
    article = {
        "title": "A" * 100,  # Very long title
        "summary": "Short summary",
    }
    result = barista.generate_summary(article)
    assert len(result["title"]) <= 80


def test_gemini_barista_initialization_without_key():
    """Test that GeminiBarista raises error without API key"""
    with pytest.raises(Exception):  # Will raise ImportError or AttributeError
        GeminiBarista(api_key="invalid-key")


def test_mistral_barista_initialization_without_key():
    """Test that MistralBarista raises error without API key"""
    with pytest.raises(Exception):  # Will raise ImportError or AttributeError
        MistralBarista(api_key="invalid-key")


def test_github_copilot_cli_barista_checks_gh():
    """Test that GitHubCopilotCLIBarista can be instantiated"""
    barista = GitHubCopilotCLIBarista()
    assert isinstance(barista, AIProvider)


def test_gemini_cli_barista_checks_gcloud():
    """Test that GeminiCLIBarista can be instantiated"""
    barista = GeminiCLIBarista()
    assert isinstance(barista, AIProvider)


def test_mistral_cli_barista_checks_mistral():
    """Test that MistralCLIBarista can be instantiated"""
    barista = MistralCLIBarista()
    assert isinstance(barista, AIProvider)


def test_cli_barista_uses_configured_timeout(monkeypatch):
    """CLI providers should honor ai.cli_timeout_seconds from config."""

    captured = {}

    def fake_run(command, input, capture_output, text, timeout):
        captured["timeout"] = timeout

        class Result:
            returncode = 0
            stdout = "TITLE: T\nSUMMARY: S"
            stderr = ""

        return Result()

    monkeypatch.setattr("moka_news.barista.providers.subprocess.run", fake_run)

    provider = create_ai_provider(
        "gemini-cli",
        {
            "ai": {
                "provider": "gemini-cli",
                "cli_timeout_seconds": 240,
                "api_keys": {},
            }
        },
    )

    provider._invoke_ai("system", "user")

    assert captured["timeout"] == 240


def test_cli_barista_retries_once_on_timeout(monkeypatch):
    """CLI providers should retry exactly once after a timeout."""

    calls = {"count": 0}

    def fake_run(command, input, capture_output, text, timeout):
        calls["count"] += 1
        if calls["count"] == 1:
            raise TimeoutError()

        class Result:
            returncode = 0
            stdout = "TITLE: T\nSUMMARY: S"
            stderr = ""

        return Result()

    monkeypatch.setattr("moka_news.barista.providers.subprocess.run", fake_run)
    monkeypatch.setattr(
        "moka_news.barista.providers.subprocess.TimeoutExpired", TimeoutError
    )

    provider = GeminiCLIBarista(timeout_seconds=180)
    result = provider._invoke_ai("system", "user")

    assert calls["count"] == 2
    assert "TITLE:" in result


def test_parse_editorial_response_new_title_paragraph_format():
    text = "TITLE: Morning Brief\n\nMarkets opened mixed after overnight volatility.\n\nSecond paragraph."
    parsed = AIProvider._parse_editorial_response(text)

    assert parsed["title"] == "Morning Brief"
    assert (
        parsed["summary"]
        == "Markets opened mixed after overnight volatility.\n\nSecond paragraph."
    )


def test_parse_editorial_response_legacy_summary_format():
    text = "TITLE: Legacy Title\nSUMMARY: Legacy summary body."
    parsed = AIProvider._parse_editorial_response(text)

    assert parsed["title"] == "Legacy Title"
    assert parsed["summary"] == "Legacy summary body."


def test_parse_editorial_response_without_title_marker():
    text = "No marker available"
    parsed = AIProvider._parse_editorial_response(text)

    assert parsed["title"] == "Your Morning News"
    assert parsed["summary"] == "No marker available"


def test_parse_editorial_response_case_insensitive_markers():
    text = "title: Lowercase Title\nsummary: Lowercase summary body."
    parsed = AIProvider._parse_editorial_response(text)

    assert parsed["title"] == "Lowercase Title"
    assert parsed["summary"] == "Lowercase summary body."


class TestAzureAIBarista:

    def test_invoke_ai_calls_client_correctly(self):
        """_invoke_ai sends system + user messages and returns content."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "TITLE: Test\nSUMMARY: Body"
        mock_client = MagicMock()
        mock_client.complete.return_value = mock_response

        mock_system_msg = MagicMock()
        mock_user_msg = MagicMock()
        mock_models = MagicMock()
        mock_models.SystemMessage = MagicMock(return_value=mock_system_msg)
        mock_models.UserMessage = MagicMock(return_value=mock_user_msg)

        with patch.dict(
            "sys.modules",
            {
                "azure": MagicMock(),
                "azure.ai": MagicMock(),
                "azure.ai.inference": MagicMock(),
                "azure.ai.inference.models": mock_models,
                "azure.core": MagicMock(),
                "azure.core.credentials": MagicMock(),
            },
        ):
            barista = AzureAIBarista.__new__(AzureAIBarista)
            barista.client = mock_client
            barista.model = "gpt-4o"

            result = barista._invoke_ai("sys msg", "user prompt", max_tokens=1024)

        assert result == "TITLE: Test\nSUMMARY: Body"
        mock_client.complete.assert_called_once()
        call_kwargs = mock_client.complete.call_args.kwargs
        assert call_kwargs["max_tokens"] == 1024
        assert call_kwargs["model"] == "gpt-4o"

    def test_raises_value_error_if_no_endpoint(self):
        """Constructor raises ValueError when endpoint is missing."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("moka_news.barista.providers.AzureAIBarista.__init__.__module__"):
                pass
            # Patch the azure imports to avoid ImportError masking the ValueError
            with patch.dict(
                "sys.modules",
                {
                    "azure": MagicMock(),
                    "azure.ai": MagicMock(),
                    "azure.ai.inference": MagicMock(),
                    "azure.core": MagicMock(),
                    "azure.core.credentials": MagicMock(),
                },
            ):
                with pytest.raises(ValueError, match="endpoint URL"):
                    AzureAIBarista(api_key="key", endpoint=None, model="gpt-4o")

    def test_raises_value_error_if_no_model(self):
        """Constructor raises ValueError when model name is not provided."""
        with patch.dict(
            "sys.modules",
            {
                "azure": MagicMock(),
                "azure.ai": MagicMock(),
                "azure.ai.inference": MagicMock(),
                "azure.core": MagicMock(),
                "azure.core.credentials": MagicMock(),
            },
        ):
            with pytest.raises(ValueError, match="model name"):
                AzureAIBarista(
                    api_key="key",
                    endpoint="https://example.com",
                    model=None,
                )

    def test_factory_returns_azure_barista(self, monkeypatch):
        """create_ai_provider returns AzureAIBarista for 'azure'."""
        monkeypatch.setattr(
            "moka_news.barista.providers.AzureAIBarista.__init__",
            lambda self, **kwargs: None,
        )
        config = {
            "ai": {
                "api_keys": {"azure": "key"},
                "azure_endpoint": "https://example.com",
                "azure_model": "gpt-4o",
                "azure_api_version": None,
            }
        }
        provider = create_ai_provider("azure", config)
        assert isinstance(provider, AzureAIBarista)

    def test_factory_falls_back_to_simple_on_import_error(self, monkeypatch):
        """create_ai_provider falls back to SimpleBarista when package missing."""

        def _raise_import(self, **kwargs):
            raise ImportError("no pkg")

        monkeypatch.setattr(
            "moka_news.barista.providers.AzureAIBarista.__init__",
            _raise_import,
        )
        config = {
            "ai": {
                "api_keys": {"azure": "key"},
                "azure_endpoint": "https://example.com",
                "azure_model": "gpt-4o",
                "azure_api_version": None,
            }
        }
        provider = create_ai_provider("azure", config)
        assert isinstance(provider, SimpleBarista)

    def test_editorial_mode_parses_response(self):
        """generate_summary with prompts goes through editorial path and parses TITLE/SUMMARY."""
        barista = AzureAIBarista.__new__(AzureAIBarista)
        barista.client = MagicMock()
        barista.model = "gpt-4o"
        barista._invoke_ai = MagicMock(return_value="TITLE: Hello\nSUMMARY: World")

        article = {"title": "T", "summary": "S", "link": "http://example.com"}
        result = barista.generate_summary(
            article,
            prompts={"user_prompt": "{content}", "format_section": ""},
        )
        assert result["title"] == "Hello"
        assert result["summary"] == "World"
