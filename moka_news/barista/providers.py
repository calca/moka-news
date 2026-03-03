"""Concrete AI provider implementations."""

import os
import subprocess
from typing import Dict, Any, Optional

from moka_news.logger import get_logger
from moka_news.constants import (
    DEFAULT_AI_MODELS,
    EDITORIAL_MAX_TOKENS,
    CLI_GENERATION_TIMEOUT,
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

    def _invoke_ai(self, system_message: str, user_prompt: str, max_tokens: int = EDITORIAL_MAX_TOKENS) -> str:
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

    def _invoke_ai(self, system_message: str, user_prompt: str, max_tokens: int = EDITORIAL_MAX_TOKENS) -> str:
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

    def _invoke_ai(self, system_message: str, user_prompt: str, max_tokens: int = EDITORIAL_MAX_TOKENS) -> str:
        full_prompt = f"{system_message}\n\n{user_prompt}"
        response = self.model.generate_content(full_prompt)
        return response.text


class MistralBarista(AIProvider):
    """Mistral AI-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            from mistralai.client import MistralClient

            self.client = MistralClient(
                api_key=api_key or os.getenv("MISTRAL_API_KEY")
            )
        except ImportError:
            raise ImportError(
                "mistralai package is required. Install with: pip install mistralai"
            )

    def _invoke_ai(self, system_message: str, user_prompt: str, max_tokens: int = EDITORIAL_MAX_TOKENS) -> str:
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

    def _invoke_ai(self, system_message: str, user_prompt: str, max_tokens: int = EDITORIAL_MAX_TOKENS) -> str:
        full_prompt = f"{system_message}\n\n{user_prompt}"
        try:
            result = subprocess.run(
                [self.cli_command],
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=max(CLI_GENERATION_TIMEOUT, 120),
            )
            if result.returncode != 0:
                error_msg = result.stderr.strip() or f"{self.cli_command} exited with code {result.returncode}"
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
            raise RuntimeError(
                f"'{self.cli_command}' CLI timed out after {max(CLI_GENERATION_TIMEOUT, 120)}s"
            )


class GitHubCopilotCLIBarista(_CLIBarista):
    """GitHub Copilot CLI-based content processor"""
    cli_command = "copilot"


class GeminiCLIBarista(_CLIBarista):
    """Gemini CLI-based content processor"""
    cli_command = "gemini"


class MistralCLIBarista(_CLIBarista):
    """Mistral CLI-based content processor"""
    cli_command = "mistral"
