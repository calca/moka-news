"""Buttondown publish provider — create newsletter emails via Buttondown API."""

import os
from typing import Any, Dict

from moka_news.logger import get_logger
from moka_news.publisher._http import requests
from moka_news.publisher import PublishProvider, PublishProviderError

logger = get_logger(__name__)

BUTTONDOWN_API_BASE = "https://api.buttondown.com/v1"


class ButtondownProvider(PublishProvider):
    """Publish provider for Buttondown email newsletters."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.api_key = str(
            config.get("api_key") or os.getenv("BUTTONDOWN_API_KEY") or ""
        ).strip()

        self.api_base = str(config.get("api_base") or BUTTONDOWN_API_BASE).rstrip("/")

        self.status = str(config.get("status", "draft")).strip().lower()
        if self.status not in ("draft", "about_to_send"):
            logger.warning(
                "Invalid Buttondown status %r, defaulting to 'draft'",
                self.status,
            )
            self.status = "draft"

        self.email_type = str(config.get("email_type", "public")).strip().lower()
        if self.email_type not in ("public", "private"):
            logger.warning(
                "Invalid Buttondown email_type %r, defaulting to 'public'",
                self.email_type,
            )
            self.email_type = "public"

        try:
            self.timeout_seconds = int(config.get("timeout_seconds", 20))
        except (TypeError, ValueError):
            self.timeout_seconds = 20

        self.verify_ssl = bool(config.get("verify_ssl", True))

    @property
    def name(self) -> str:
        return "buttondown"

    def is_configured(self) -> bool:
        """Return True when an API key is available."""
        return bool(self.api_key)

    def publish(self, title: str, content: str) -> Dict[str, Any]:
        """Create an email on Buttondown.

        Returns dict with ``url``, ``provider``, ``id``, and ``slug`` keys.
        """
        if not self.enabled:
            raise PublishProviderError(
                "Buttondown publishing is disabled. Set enabled: true in config."
            )

        if not self.api_key:
            raise PublishProviderError(
                "Missing Buttondown API key. Set api_key in config or BUTTONDOWN_API_KEY env var."
            )

        clean_content = (content or "").strip()
        if not clean_content:
            raise PublishProviderError("Email body cannot be empty.")

        clean_title = (title or "").strip() or "Morning Editorial"

        endpoint = f"{self.api_base}/emails"
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "subject": clean_title,
            "body": clean_content,
            "status": self.status,
            "email_type": self.email_type,
        }

        logger.info(
            "Publishing to Buttondown (status=%s, email_type=%s)",
            self.status,
            self.email_type,
        )

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=self.timeout_seconds,
                verify=self.verify_ssl,
            )
        except ModuleNotFoundError as exc:
            raise PublishProviderError(
                "requests library is required for Buttondown publishing. "
                "Install with: pip install requests"
            ) from exc
        except requests.RequestException as exc:
            raise PublishProviderError(
                f"Could not reach Buttondown API: {exc}"
            ) from exc

        try:
            response_data = response.json()
        except ValueError as exc:
            raise PublishProviderError(
                f"Buttondown API returned invalid JSON (HTTP {response.status_code})."
            ) from exc

        if response.status_code >= 400:
            error_detail = self._extract_error(response_data)
            raise PublishProviderError(
                f"Buttondown API error (HTTP {response.status_code}): {error_detail}"
            )

        email_id = response_data.get("id", "")
        absolute_url = response_data.get("absolute_url")
        slug = response_data.get("slug", "")

        logger.info("Buttondown email created: id=%s slug=%s", email_id, slug)

        return {
            "url": absolute_url,
            "provider": self.name,
            "id": email_id,
            "slug": slug,
            "status": response_data.get("status", self.status),
        }

    @staticmethod
    def _extract_error(response_data: Any) -> str:
        """Extract a human-readable error from the API response."""
        if isinstance(response_data, dict):
            # Buttondown may return {"detail": "..."} or {"non_field_errors": [...]}
            for key in ("detail", "error", "message"):
                value = response_data.get(key)
                if value:
                    return str(value)
            # Field-level errors
            errors = []
            for field, messages in response_data.items():
                if isinstance(messages, list):
                    errors.append(f"{field}: {', '.join(str(m) for m in messages)}")
            if errors:
                return "; ".join(errors)
        if isinstance(response_data, list) and response_data:
            return str(response_data[0])
        return str(response_data)
