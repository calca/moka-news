"""Write.as publisher integration for creating posts via API."""

import os
import re
from typing import Any, Dict, Optional

from moka_news.logger import get_logger
from moka_news.publisher._http import requests

logger = get_logger(__name__)

WRITEAS_API_BASE = "https://write.as/api"


class WriteAsPublisherError(Exception):
    """Raised when publishing to Write.as fails."""


class WriteAsPublisher:
    """Create posts on Write.as through its HTTP API."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        cfg = config or {}

        self.enabled = bool(cfg.get("enabled", False))
        self.api_base = str(cfg.get("api_base") or WRITEAS_API_BASE).rstrip("/")

        self.alias = str(cfg.get("alias") or os.getenv("WRITEAS_ALIAS") or "").strip()
        self.passphrase = str(
            cfg.get("pass") or os.getenv("WRITEAS_PASS") or ""
        ).strip()
        self._access_token_cache = None

        self.collection_alias = str(
            cfg.get("collection_alias")
            or os.getenv("WRITEAS_COLLECTION_ALIAS")
            or os.getenv("WRITEAS_COLLECTION")
            or ""
        ).strip()

        self.default_font = self._clean_optional_text(cfg.get("font"))
        self.default_lang = self._clean_optional_text(cfg.get("lang"))
        self.default_created = self._clean_optional_text(cfg.get("created"))
        self.default_title = self._clean_optional_text(cfg.get("title"))
        self.default_rtl = bool(cfg.get("rtl", False))

        try:
            self.timeout_seconds = int(cfg.get("timeout_seconds", 20))
        except (TypeError, ValueError):
            self.timeout_seconds = 20

        self.verify_ssl = bool(cfg.get("verify_ssl", True))

    def is_configured(self) -> bool:
        """Return True when auth configuration is sufficient to publish."""
        return bool(self.alias and self.passphrase)

    def publish_post(
        self,
        title: str,
        content: str,
        collection_alias: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Publish a Write.as post and return the created post payload."""
        if not self.enabled:
            raise WriteAsPublisherError(
                "Write.as publishing is disabled. Set writeas.enabled=true in config."
            )

        clean_content = (content or "").strip()
        if not clean_content:
            raise WriteAsPublisherError("Write.as post body cannot be empty.")

        token = self._resolve_access_token()

        effective_collection = (
            self._clean_optional_text(collection_alias) or self.collection_alias
        )
        if effective_collection:
            endpoint = f"{self.api_base}/collections/{effective_collection}/posts"
        else:
            endpoint = f"{self.api_base}/posts"

        clean_title = self._clean_optional_text(title) or self.default_title
        payload: Dict[str, Any] = {
            "body": self._prepare_body_for_posting(clean_content, clean_title or ""),
            "rtl": self.default_rtl,
        }

        if clean_title:
            payload["title"] = clean_title

        if self.default_font:
            payload["font"] = self.default_font
        if self.default_lang:
            payload["lang"] = self.default_lang
        if self.default_created:
            payload["created"] = self.default_created

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {token}",
        }

        logger.info("Publishing editorial to Write.as")

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=self.timeout_seconds,
                verify=self.verify_ssl,
            )
        except ModuleNotFoundError as exc:
            raise WriteAsPublisherError(
                "requests library is required for Write.as publishing. Install with: pip install requests"
            ) from exc
        except requests.RequestException as exc:
            raise WriteAsPublisherError(f"Could not reach Write.as API: {exc}") from exc

        try:
            response_data = response.json()
        except ValueError as exc:
            raise WriteAsPublisherError(
                f"Write.as API returned invalid JSON (HTTP {response.status_code})."
            ) from exc

        api_code = self._safe_int(response_data.get("code"), response.status_code)
        if response.status_code >= 400 or api_code >= 400:
            message = self._extract_error_message(response_data) or (
                f"Write.as API request failed with HTTP {response.status_code}."
            )
            raise WriteAsPublisherError(message)

        post_data = response_data.get("data")
        if not isinstance(post_data, dict):
            raise WriteAsPublisherError(
                "Write.as API returned an unexpected post response."
            )

        normalized = dict(post_data)
        normalized["url"] = self._extract_post_url(normalized, effective_collection)
        return normalized

    def _resolve_access_token(self) -> str:
        if self._access_token_cache:
            return self._access_token_cache

        if not self.alias or not self.passphrase:
            raise WriteAsPublisherError("Missing Write.as alias/pass credentials.")

        login_endpoint = f"{self.api_base}/auth/login"
        login_payload = {
            "alias": self.alias,
            "pass": self.passphrase,
        }

        logger.debug("Requesting Write.as access token via login")

        try:
            response = requests.post(
                login_endpoint,
                json=login_payload,
                timeout=self.timeout_seconds,
                verify=self.verify_ssl,
            )
        except ModuleNotFoundError as exc:
            raise WriteAsPublisherError(
                "requests library is required for Write.as publishing. Install with: pip install requests"
            ) from exc
        except requests.RequestException as exc:
            raise WriteAsPublisherError(
                f"Could not login to Write.as API: {exc}"
            ) from exc

        try:
            response_data = response.json()
        except ValueError as exc:
            raise WriteAsPublisherError(
                f"Write.as login endpoint returned invalid JSON (HTTP {response.status_code})."
            ) from exc

        api_code = self._safe_int(response_data.get("code"), response.status_code)
        if response.status_code >= 400 or api_code >= 400:
            message = self._extract_error_message(response_data) or (
                f"Write.as login failed with HTTP {response.status_code}."
            )
            raise WriteAsPublisherError(message)

        token = str(response_data.get("data", {}).get("access_token") or "").strip()
        if not token:
            raise WriteAsPublisherError(
                "Write.as login response did not include access_token."
            )

        self._access_token_cache = token
        return token

    def _extract_post_url(
        self, post_data: Dict[str, Any], collection_alias: str
    ) -> Optional[str]:
        post_id = self._clean_optional_text(post_data.get("id"))
        slug = self._clean_optional_text(post_data.get("slug"))

        collection_url = self._clean_optional_text(
            post_data.get("collection", {}).get("url")
            if isinstance(post_data.get("collection"), dict)
            else None
        )

        if collection_url and slug:
            return f"{collection_url.rstrip('/')}/{slug}"
        if collection_url and post_id:
            return f"{collection_url.rstrip('/')}/{post_id}"

        host_base = self._derive_writeas_host_base()

        if collection_alias and slug:
            return f"{host_base}/{collection_alias}/{slug}"
        if collection_alias and post_id:
            return f"{host_base}/{collection_alias}/{post_id}"
        if post_id:
            return f"{host_base}/{post_id}"

        return None

    def _derive_writeas_host_base(self) -> str:
        base = self.api_base
        if base.endswith("/api"):
            base = base[:-4]
        elif "/api/" in base:
            base = base.split("/api/", 1)[0]
        return base.rstrip("/")

    @staticmethod
    def _extract_error_message(response_data: Any) -> Optional[str]:
        if isinstance(response_data, dict):
            for key in ("error_msg", "error", "message"):
                value = response_data.get(key)
                if value:
                    return str(value)
        return None

    @staticmethod
    def _safe_int(value: Any, fallback: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return int(fallback)

    @staticmethod
    def _clean_optional_text(value: Optional[Any]) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text if text else None

    def _prepare_body_for_posting(self, content: str, title: str) -> str:
        """Remove leading duplicate title markers/headings from markdown body."""
        lines = content.splitlines()
        if not lines:
            return content

        normalized_title = self._normalize_title_text(title)
        if not normalized_title:
            return content

        def first_non_empty_idx() -> Optional[int]:
            for idx, line in enumerate(lines):
                if line.strip():
                    return idx
            return None

        idx = first_non_empty_idx()
        if idx is None:
            return content

        title_marker_re = re.compile(
            r"^\s*(?:\*\*)?TITLE(?:\*\*)?\s*:\s*(.+?)\s*$",
            re.IGNORECASE,
        )
        heading_re = re.compile(r"^\s*#{1,6}\s+(.+?)\s*$")

        # Strip leading "TITLE: ..." line if it matches the chosen title.
        marker_match = title_marker_re.match(lines[idx])
        if marker_match:
            marker_title = self._normalize_title_text(marker_match.group(1))
            if marker_title == normalized_title:
                del lines[idx]
                while idx < len(lines) and not lines[idx].strip():
                    del lines[idx]

        idx = first_non_empty_idx()
        if idx is None:
            return content

        # Strip leading markdown heading if it matches the chosen title.
        heading_match = heading_re.match(lines[idx])
        if heading_match:
            heading_title = self._normalize_title_text(heading_match.group(1))
            if heading_title == normalized_title:
                del lines[idx]
                while idx < len(lines) and not lines[idx].strip():
                    del lines[idx]

        body = "\n".join(lines).strip()
        return body or content

    @staticmethod
    def _normalize_title_text(value: str) -> str:
        text = (value or "").strip().lower()
        text = re.sub(r"[*_`]", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip(" -:#")
