"""Concrete AI provider implementations."""

import os
import subprocess
from typing import Optional
from urllib.parse import urlparse

from moka_news.logger import get_logger
from moka_news.constants import (
    DEFAULT_AI_MODELS,
    EDITORIAL_MAX_TOKENS,
    CLI_GENERATION_TIMEOUT,
    AZURE_AI_API_VERSION,
)
from moka_news.barista.base import AIProvider

logger = get_logger(__name__)


# -- API-based providers -----------------------------------------------------


class OpenAIBarista(AIProvider):
    """OpenAI-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            import openai

            self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )

    def _invoke_ai(
        self,
        system_message: str,
        user_prompt: str,
        max_tokens: int = EDITORIAL_MAX_TOKENS,
    ) -> str:
        response = self.client.chat.completions.create(
            model=DEFAULT_AI_MODELS.get("openai", "gpt-3.5-turbo"),
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content


class AnthropicBarista(AIProvider):
    """Anthropic-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            import anthropic

            self.client = anthropic.Anthropic(
                api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
            )
        except ImportError:
            raise ImportError(
                "anthropic package is required. Install with: pip install anthropic"
            )

    def _invoke_ai(
        self,
        system_message: str,
        user_prompt: str,
        max_tokens: int = EDITORIAL_MAX_TOKENS,
    ) -> str:
        response = self.client.messages.create(
            model=DEFAULT_AI_MODELS.get("anthropic", "claude-3-haiku-20240307"),
            max_tokens=max_tokens,
            system=system_message,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text


class GeminiBarista(AIProvider):
    """Google Gemini-based content processor (API key)"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel(
                DEFAULT_AI_MODELS.get("gemini", "gemini-pro")
            )
        except ImportError:
            raise ImportError(
                "google-generativeai package is required. Install with: pip install google-generativeai"
            )

    def _invoke_ai(
        self,
        system_message: str,
        user_prompt: str,
        max_tokens: int = EDITORIAL_MAX_TOKENS,
    ) -> str:
        full_prompt = f"{system_message}\n\n{user_prompt}"
        response = self.model.generate_content(full_prompt)
        return response.text


class MistralBarista(AIProvider):
    """Mistral AI-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            from mistralai.client import MistralClient

            self.client = MistralClient(api_key=api_key or os.getenv("MISTRAL_API_KEY"))
        except ImportError:
            raise ImportError(
                "mistralai package is required. Install with: pip install mistralai"
            )

    def _invoke_ai(
        self,
        system_message: str,
        user_prompt: str,
        max_tokens: int = EDITORIAL_MAX_TOKENS,
    ) -> str:
        from mistralai.models.chat_completion import ChatMessage

        response = self.client.chat(
            model=DEFAULT_AI_MODELS.get("mistral", "mistral-tiny"),
            messages=[
                ChatMessage(role="system", content=system_message),
                ChatMessage(role="user", content=user_prompt),
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content


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
        resolved_endpoint = self._normalize_endpoint(resolved_endpoint)

        resolved_key = api_key or os.getenv("AZURE_AI_API_KEY")
        resolved_api_version = (
            api_version or os.getenv("AZURE_AI_API_VERSION") or AZURE_AI_API_VERSION
        )

        self.client = ChatCompletionsClient(
            endpoint=resolved_endpoint,
            credential=AzureKeyCredential(resolved_key or ""),
            api_version=resolved_api_version,
        )

        resolved_model = (
            model or os.getenv("AZURE_AI_MODEL") or DEFAULT_AI_MODELS.get("azure")
        )
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

        try:
            response = self.client.complete(
                messages=[
                    SystemMessage(content=system_message),
                    UserMessage(content=user_prompt),
                ],
                max_tokens=max_tokens,
                model=self.model,
            )
            return response.choices[0].message.content
        except Exception as exc:
            error_text = str(exc)
            if "404" in error_text or "Resource not found" in error_text:
                raise RuntimeError(
                    "Azure AI request returned 404 (Resource not found). "
                    "Verify 'ai.azure_endpoint' points to your Azure AI Foundry endpoint "
                    "(usually ending with '/models') and 'ai.azure_model' matches the "
                    "deployed model name exactly. Some models are available only on specific "
                    "API versions, so try setting the 'ai.azure_api_version' config key or the "
                    "AZURE_AI_API_VERSION env var to a version supported by your deployment."
                ) from exc
            raise

    @staticmethod
    def _normalize_endpoint(endpoint: str) -> str:
        endpoint = endpoint.strip().rstrip("/")
        host = urlparse(endpoint).netloc.lower()

        if "openai.azure.com" in host:
            raise ValueError(
                "Detected an Azure OpenAI endpoint. The 'azure' provider expects an "
                "Azure AI Foundry endpoint like 'https://<name>.services.ai.azure.com/models'."
            )

        if "services.ai.azure.com" in host and not endpoint.endswith("/models"):
            endpoint = f"{endpoint}/models"

        return endpoint


# -- Simple (no-AI) provider ------------------------------------------------


class SimpleBarista(AIProvider):
    """Simple non-AI processor for testing without API keys"""

    pass  # inherits generate_summary pass-through from AIProvider


# -- CLI-based providers -----------------------------------------------------


class _CLIBarista(AIProvider):
    """Base class for CLI-based AI providers.

    Sends the full prompt via subprocess stdin, reads output from stdout.
    """

    cli_command: str = ""

    def __init__(self, timeout_seconds: Optional[int] = None):
        configured_timeout = timeout_seconds or CLI_GENERATION_TIMEOUT
        self.timeout_seconds = max(configured_timeout, 120)

    def _invoke_ai(
        self,
        system_message: str,
        user_prompt: str,
        max_tokens: int = EDITORIAL_MAX_TOKENS,
    ) -> str:
        full_prompt = f"{system_message}\n\n{user_prompt}"
        attempts = 2  # one initial attempt + one retry
        for attempt in range(1, attempts + 1):
            try:
                result = subprocess.run(
                    [self.cli_command],
                    input=full_prompt,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                )
                if result.returncode != 0:
                    error_msg = (
                        result.stderr.strip()
                        or f"{self.cli_command} exited with code {result.returncode}"
                    )
                    raise RuntimeError(f"{self.cli_command} CLI error: {error_msg}")
                output = result.stdout.strip()
                if not output:
                    raise RuntimeError(f"{self.cli_command} returned empty output")
                return output
            except FileNotFoundError:
                raise RuntimeError(
                    f"'{self.cli_command}' CLI not found on PATH. "
                    f"Make sure it is installed and accessible."
                )
            except subprocess.TimeoutExpired:
                if attempt < attempts:
                    logger.warning(
                        "%s CLI timed out after %ss (attempt %s/%s), retrying once",
                        self.cli_command,
                        self.timeout_seconds,
                        attempt,
                        attempts,
                    )
                    continue
                raise RuntimeError(
                    f"'{self.cli_command}' CLI timed out after {self.timeout_seconds}s "
                    "(after 1 retry). Increase ai.cli_timeout_seconds in your config if needed."
                )

        raise RuntimeError(f"{self.cli_command} CLI failed unexpectedly")


class GitHubCopilotCLIBarista(_CLIBarista):
    """GitHub Copilot CLI-based content processor"""

    cli_command = "copilot"


class GeminiCLIBarista(_CLIBarista):
    """Gemini CLI-based content processor"""

    cli_command = "gemini"


class MistralCLIBarista(_CLIBarista):
    """Mistral CLI-based content processor"""

    cli_command = "mistral"
