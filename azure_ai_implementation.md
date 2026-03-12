# Azure AI Foundry — Implementation Plan

Reference SDK: `azure_ai_inference_sdk.md`

---

## Decisions

| Question | Decision |
|---|---|
| Default model name | `None` — user must explicitly set `ai.azure_model` or `AZURE_AI_MODEL` env var |
| `api_version` | Hardcoded to `"2024-05-01-preview"`; overridable via `ai.azure_api_version` in config or `AZURE_AI_API_VERSION` env var |
| Config example file | New `conf-example/azure-config.yaml` (consistent with `openai-config.yaml`, `anthropic-config.yaml`, etc.) |

---

## Files to Change

### 1. `moka_news/constants.py`

Add `"azure"` to `DEFAULT_AI_MODELS` with value `None` (model name is deployment-specific):

```python
DEFAULT_AI_MODELS = {
    "openai": "gpt-3.5-turbo",
    "anthropic": "claude-3-haiku-20240307",
    "gemini": "gemini-pro",
    "mistral": "mistral-tiny",
    "azure": None,  # Must be set via ai.azure_model config or AZURE_AI_MODEL env var
}

AZURE_AI_API_VERSION = "2024-05-01-preview"  # Hardcoded default; override via ai.azure_api_version
```

---

### 2. `moka_news/barista/providers.py`

Add `AzureAIBarista` among the API-based providers (after `MistralBarista`, before `SimpleBarista`):

```python
class AzureAIBarista(AIProvider):
    """Azure AI Foundry-based content processor (Azure AI Inference SDK)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        try:
            from azure.ai.inference import ChatCompletionsClient
            from azure.core.credentials import AzureKeyCredential
        except ImportError:
            raise ImportError(
                "azure-ai-inference package is required. "
                "Install with: pip install azure-ai-inference"
            )

        resolved_endpoint = endpoint or os.getenv("AZURE_AI_ENDPOINT")
        if not resolved_endpoint:
            raise ValueError(
                "Azure AI Foundry requires an endpoint URL. "
                "Set 'ai.azure_endpoint' in config or the AZURE_AI_ENDPOINT env var."
            )

        resolved_key = api_key or os.getenv("AZURE_AI_API_KEY")
        resolved_api_version = api_version or os.getenv("AZURE_AI_API_VERSION") or AZURE_AI_API_VERSION

        self.client = ChatCompletionsClient(
            endpoint=resolved_endpoint,
            credential=AzureKeyCredential(resolved_key or ""),
            api_version=resolved_api_version,
        )

        resolved_model = model or os.getenv("AZURE_AI_MODEL") or DEFAULT_AI_MODELS.get("azure")
        if not resolved_model:
            raise ValueError(
                "Azure AI Foundry requires a model name. "
                "Set 'ai.azure_model' in config or the AZURE_AI_MODEL env var."
            )
        self.model = resolved_model

    def _invoke_ai(
        self,
        system_message: str,
        user_prompt: str,
        max_tokens: int = EDITORIAL_MAX_TOKENS,
    ) -> str:
        from azure.ai.inference.models import SystemMessage, UserMessage

        response = self.client.complete(
            messages=[
                SystemMessage(content=system_message),
                UserMessage(content=user_prompt),
            ],
            max_tokens=max_tokens,
            model=self.model,
        )
        return response.choices[0].message.content
```

Import `AZURE_AI_API_VERSION` from `moka_news.constants` at the top of the file.

---

### 3. `moka_news/barista/__init__.py`

- Import `AzureAIBarista` from `providers`.
- Add to `__all__`.
- Add to `provider_map`: `"azure": AzureAIBarista`.
- Handle `"azure"` in the factory instantiation branch (it needs 4 optional args, not just `api_key`):

```python
if provider_name == "azure":
    api_key = api_keys.get("azure")
    endpoint = ai_config.get("azure_endpoint")
    model = ai_config.get("azure_model")
    api_version = ai_config.get("azure_api_version")
    try:
        return AzureAIBarista(
            api_key=api_key, endpoint=endpoint, model=model, api_version=api_version
        )
    except (ImportError, ValueError) as e:
        logger.warning("Cannot create azure provider: %s. Falling back to simple.", e)
        return SimpleBarista()
```

Place this block before the generic `provider_name in ["openai", "anthropic", "gemini", "mistral"]` branch so it is handled first (or extend that branch conditionally — placing it as a separate `if` before the group is cleaner).

---

### 4. `moka_news/infrastructure/config/defaults.py`

Extend `DEFAULT_CONFIG["ai"]` with three new keys:

```python
"ai": {
    ...
    "api_keys": {
        "openai": None,
        "anthropic": None,
        "gemini": None,
        "mistral": None,
        "azure": None,          # Azure AI API key (or AZURE_AI_API_KEY env var)
    },
    "azure_endpoint": None,     # Azure AI Foundry endpoint URL (or AZURE_AI_ENDPOINT env var)
    "azure_model": None,        # Deployed model name (or AZURE_AI_MODEL env var) — required for azure provider
    "azure_api_version": None,  # API version override; defaults to AZURE_AI_API_VERSION constant
    ...
}
```

---

### 5. `moka_news/infrastructure/config/loader.py`

Add env-var override block for Azure fields (after the existing Mistral block):

```python
if os.getenv("AZURE_AI_API_KEY"):
    api_keys["azure"] = os.getenv("AZURE_AI_API_KEY")
if os.getenv("AZURE_AI_ENDPOINT"):
    ai_config["azure_endpoint"] = os.getenv("AZURE_AI_ENDPOINT")
if os.getenv("AZURE_AI_MODEL"):
    ai_config["azure_model"] = os.getenv("AZURE_AI_MODEL")
if os.getenv("AZURE_AI_API_VERSION"):
    ai_config["azure_api_version"] = os.getenv("AZURE_AI_API_VERSION")
```

---

### 6. `moka_news/cli/parser.py`

- Add `"azure"` to `AI_CHOICES` list.
- Add example line to the epilog:

```
moka-news --ai azure              # Use Azure AI Foundry model
```

---

### 7. `moka_news/cli/first_run_setup.py`

Add `"azure"` entry to `AI_PROVIDERS`:

```python
"azure": {
    "name": "Azure AI Foundry",
    "requires_api_key": True,
    "env_var": "AZURE_AI_API_KEY",
    "cli_required": False,
},
```

Extend `prompt_ai_provider()` (or the config save step) to additionally prompt for `azure_endpoint` and `azure_model` when `"azure"` is selected. These should be written to the config YAML under `ai.azure_endpoint` and `ai.azure_model`.

Example prompt flow addition:

```python
if provider == "azure":
    endpoint = input("Azure AI Foundry endpoint URL: ").strip()
    model = input("Deployed model name (e.g. Mistral-Large-3, gpt-4o): ").strip()
    config["ai"]["azure_endpoint"] = endpoint or None
    config["ai"]["azure_model"] = model or None
```

---

### 8. `pyproject.toml`

Add optional dependency group and include in `all`:

```toml
azure = [
    "azure-ai-inference>=1.0.0b9",
]
all = [
    "google-generativeai>=0.3.0",
    "mistralai>=0.0.7",
    "azure-ai-inference>=1.0.0b9",
]
```

Also add `"azure"` to the `keywords` list in `[project]`.

---

### 9. `conf-example/azure-config.yaml` (new file)

Create alongside `openai-config.yaml`, `anthropic-config.yaml`, etc.:

```yaml
# MoKa News - Azure AI Foundry Configuration Example
#
# Before using:
#   pip install "moka-news[azure]"
#
# Required:
#   - An Azure AI Foundry deployment (Serverless API or Managed Compute endpoint)
#   - The endpoint URL from Deployments + Endpoints page
#   - An API key from the same page
#   - The deployed model name (e.g. Mistral-Large-3, gpt-4o, Llama-3-8B)
#
# Environment variables (alternative to config):
#   AZURE_AI_API_KEY, AZURE_AI_ENDPOINT, AZURE_AI_MODEL, AZURE_AI_API_VERSION

ai:
  provider: azure
  language: en

  api_keys:
    azure: null       # Set AZURE_AI_API_KEY env var, or paste key here

  azure_endpoint: null   # e.g. https://my-foundry.services.ai.azure.com/models
  azure_model: null      # e.g. Mistral-Large-3, gpt-4o, Llama-3-8B-Instruct
    azure_api_version: null  # Defaults to 2024-05-01-preview; override only if needed

  keywords: []
  max_content_length: 1500
  max_tokens: 300
  cli_timeout_seconds: 240

feeds:
  urls:
    - https://news.ycombinator.com/rss
    - https://github.blog/feed/
    - https://www.theverge.com/rss/index.xml
```

---

### 10. `tests/test_barista.py`

Add the following test cases:

#### `TestAzureAIBarista`

```python
class TestAzureAIBarista:

    def test_invoke_ai_calls_client_correctly(self):
        """_invoke_ai sends system + user messages and returns content."""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "TITLE: Test\nSUMMARY: Body"
        mock_client = MagicMock()
        mock_client.complete.return_value = mock_response

        with patch("moka_news.barista.providers.AzureAIBarista.__init__", return_value=None):
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
        with patch.dict(os.environ, {}, clear_True):
            with pytest.raises(ValueError, match="endpoint URL"):
                AzureAIBarista(api_key="key", endpoint=None, model="gpt-4o")

    def test_raises_value_error_if_no_model(self):
        """Constructor raises ValueError when model name is not provided."""
        with pytest.raises(ValueError, match="model name"):
            AzureAIBarista(api_key="key", endpoint="https://example.com", model=None)

    def test_factory_returns_azure_barista(self, monkeypatch):
        """create_ai_provider returns AzureAIBarista for 'azure'."""
        monkeypatch.setattr("moka_news.barista.providers.AzureAIBarista.__init__",
                            lambda self, **kwargs: None)
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
        monkeypatch.setattr("moka_news.barista.providers.AzureAIBarista.__init__",
                            lambda self, **kwargs: (_ for _ in ()).throw(ImportError("no pkg")))
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
        result = barista.generate_summary(article, prompts={"user_prompt": "{content}", "format_section": ""})
        assert result["title"] == "Hello"
        assert result["summary"] == "World"
```

---

## Edge Cases

| Case | Handling |
|---|---|
| `azure-ai-inference` not installed | `ImportError` in constructor; factory catches it and returns `SimpleBarista` with warning |
| `endpoint` is `None` | `ValueError` with clear message before client construction |
| `model` is `None` (user forgot) | `ValueError` with clear message before first call |
| `api_key` is `None` | Passed as empty string; Azure SDK raises auth error on first request |
| Custom `api_version` needed | Set `ai.azure_api_version` in config or `AZURE_AI_API_VERSION` env var |
| Multiple Azure deployments | Use separate `moka-news.yaml` files per deployment (standard config override pattern) |

---

## Environment Variables Reference

| Variable | Maps to config key | Required |
|---|---|---|
| `AZURE_AI_API_KEY` | `ai.api_keys.azure` | Yes |
| `AZURE_AI_ENDPOINT` | `ai.azure_endpoint` | Yes |
| `AZURE_AI_MODEL` | `ai.azure_model` | Yes |
| `AZURE_AI_API_VERSION` | `ai.azure_api_version` | No (default: `2024-05-01-preview`) |
