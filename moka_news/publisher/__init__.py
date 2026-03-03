"""
Publisher — Multi-provider publishing system for editorials.

All enabled and configured providers are executed when the user publishes.
Providers are defined as subclasses of ``PublishProvider`` and registered
via ``create_publish_providers()``.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from moka_news.logger import get_logger

logger = get_logger(__name__)


class PublishProviderError(Exception):
    """Raised when a publish provider encounters an error."""


class PublishResult:
    """Result of a single publish operation."""

    __slots__ = ("provider", "success", "url", "error")

    def __init__(
        self,
        provider: str,
        success: bool,
        url: Optional[str] = None,
        error: Optional[str] = None,
    ):
        self.provider = provider
        self.success = success
        self.url = url
        self.error = error

    def __repr__(self) -> str:
        status = "ok" if self.success else "FAIL"
        return f"<PublishResult provider={self.provider!r} {status}>"


class PublishProvider(ABC):
    """Abstract base class for publish providers."""

    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self.enabled = bool(config.get("enabled", False))

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier for the provider, e.g. 'writeas', 'buttondown'."""

    @abstractmethod
    def is_configured(self) -> bool:
        """Return True when required credentials / settings are present."""

    @abstractmethod
    def publish(self, title: str, content: str) -> Dict[str, Any]:
        """Publish content and return a result dict with at least {"url": str | None, "provider": str}."""


class PublishManager:
    """Orchestrates publishing across all enabled providers."""

    def __init__(self, providers: List[PublishProvider]):
        self._providers = providers

    @property
    def providers(self) -> List[PublishProvider]:
        return list(self._providers)

    def has_enabled_providers(self) -> bool:
        """Return True if at least one provider is enabled and configured."""
        return any(p.enabled and p.is_configured() for p in self._providers)

    def get_enabled_provider_names(self) -> List[str]:
        """Return names of all enabled and configured providers."""
        return [p.name for p in self._providers if p.enabled and p.is_configured()]

    def publish_all(self, title: str, content: str) -> List[PublishResult]:
        """Publish to every enabled and configured provider.

        Never short-circuits on failure — every eligible provider is attempted.
        """
        results: List[PublishResult] = []

        for provider in self._providers:
            if not provider.enabled:
                logger.debug("Skipping disabled provider %s", provider.name)
                continue
            if not provider.is_configured():
                logger.warning(
                    "Provider %s is enabled but not configured — skipping",
                    provider.name,
                )
                results.append(
                    PublishResult(
                        provider=provider.name,
                        success=False,
                        error="Provider enabled but not configured (missing credentials)",
                    )
                )
                continue

            logger.info("Publishing to %s", provider.name)
            try:
                result = provider.publish(title, content)
                url = result.get("url") if isinstance(result, dict) else None
                results.append(
                    PublishResult(provider=provider.name, success=True, url=url)
                )
            except Exception as exc:
                logger.exception("Failed to publish to %s: %s", provider.name, exc)
                results.append(
                    PublishResult(provider=provider.name, success=False, error=str(exc))
                )

        return results


def create_publish_providers(config: Dict[str, Any]) -> List[PublishProvider]:
    """Build provider instances from ``config["publish"]["providers"]``."""
    from moka_news.publisher.writeas_provider import WriteAsProvider
    from moka_news.publisher.buttondown_provider import ButtondownProvider

    provider_map = {
        "writeas": WriteAsProvider,
        "buttondown": ButtondownProvider,
    }

    providers: List[PublishProvider] = []
    publish_config = config.get("publish", {})

    for entry in publish_config.get("providers", []):
        ptype = str(entry.get("type", "")).strip().lower()
        cls = provider_map.get(ptype)
        if cls is None:
            logger.warning("Unknown publish provider type: %r — skipping", ptype)
            continue
        providers.append(cls(entry))

    return providers
