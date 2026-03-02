"""Write.as publish provider — adapter around the existing WriteAsPublisher."""

from typing import Any, Dict

from moka_news.logger import get_logger
from moka_news.publisher import PublishProvider, PublishProviderError

logger = get_logger(__name__)


class WriteAsProvider(PublishProvider):
    """Publish provider for Write.as, wrapping ``WriteAsPublisher``."""

    @property
    def name(self) -> str:
        return "writeas"

    def is_configured(self) -> bool:
        """Delegate to the underlying publisher's credential check."""
        from moka_news.publisher._writeas import WriteAsPublisher

        publisher = WriteAsPublisher(self._config)
        return publisher.is_configured()

    def publish(self, title: str, content: str) -> Dict[str, Any]:
        """Publish via Write.as API.

        Returns dict with at least ``url`` and ``provider`` keys.
        """
        from moka_news.publisher._writeas import WriteAsPublisher, WriteAsPublisherError

        if not self.enabled:
            raise PublishProviderError(
                "Write.as publishing is disabled. Set enabled: true in config."
            )

        publisher = WriteAsPublisher(self._config)
        if not publisher.is_configured():
            raise PublishProviderError(
                "Missing Write.as credentials (alias/pass)."
            )

        try:
            collection_alias = self._config.get("collection_alias")
            post_data = publisher.publish_post(
                title=title,
                content=content,
                collection_alias=collection_alias,
            )
        except WriteAsPublisherError as exc:
            raise PublishProviderError(str(exc)) from exc

        post_data["provider"] = self.name
        return post_data