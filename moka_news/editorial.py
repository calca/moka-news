"""Editorial generator facade.

Public API remains stable while implementation is split between:
- service logic: ``moka_news.application.services.editorial_service``
- persistence: ``moka_news.infrastructure.storage.editorial_repository``
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from moka_news.application.services import EditorialService
from moka_news.barista import AIProvider
from moka_news.infrastructure.storage import EditorialRepository
from moka_news.paths import APP_CONFIG_DIR, EDITORIALS_DIR, POSTERS_DIR


class EditorialGenerator:
    """Generates, stores, and loads AI-powered morning editorials."""

    def __init__(
        self,
        ai_provider: AIProvider,
        keywords: Optional[List[str]] = None,
        editorials_dir: Optional[Path] = None,
        editorial_prompts: Optional[Dict[str, str]] = None,
        language: str = "en",
    ):
        self.ai_provider = ai_provider
        self.keywords = keywords or []
        self.editorial_prompts = editorial_prompts
        self.language = language

        self.config_dir = APP_CONFIG_DIR
        self.editorials_dir = Path(editorials_dir) if editorials_dir else EDITORIALS_DIR
        self.posters_dir = POSTERS_DIR

        self.editorials_dir.mkdir(parents=True, exist_ok=True)
        self.posters_dir.mkdir(parents=True, exist_ok=True)

        self._service = EditorialService(
            ai_provider=ai_provider,
            keywords=self.keywords,
            editorial_prompts=self.editorial_prompts,
            language=self.language,
        )
        self._repository = EditorialRepository(self.editorials_dir)
        self._service.log_configuration(self.editorials_dir, self.posters_dir)

    def generate_editorial(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate an editorial dictionary from a list of article dictionaries."""
        return self._service.generate_editorial(articles)

    def _build_editorial_prompt(self, articles: List[Dict[str, Any]]) -> str:
        """Compatibility wrapper around editorial prompt construction."""
        return self._service.build_editorial_prompt(articles)

    def _get_editorial_prompts(self) -> Dict[str, str]:
        """Compatibility wrapper around prompt resolution and language injection."""
        return self._service.get_editorial_prompts()

    def _create_simple_editorial(self, articles: List[Dict[str, Any]]) -> str:
        """Compatibility wrapper for non-AI fallback editorial creation."""
        return self._service.create_simple_editorial(articles)

    def save_editorial(self, editorial: Dict[str, Any]) -> Path:
        """Save editorial markdown and return path."""
        return self._repository.save(editorial)

    def _format_editorial_markdown(self, editorial: Dict[str, Any]) -> str:
        """Compatibility wrapper around markdown rendering."""
        return self._repository.format_markdown(editorial)

    def list_editorials(self) -> List[Dict[str, Any]]:
        """List saved editorials sorted by timestamp (oldest to newest)."""
        return self._repository.list()

    def load_most_recent_editorial(self) -> Optional[Dict[str, Any]]:
        """Load the most recent saved editorial, if available."""
        return self._repository.load_most_recent()

    def load_editorial(self, filepath: Path) -> str:
        """Load editorial markdown content from a file."""
        return self._repository.load(filepath)
