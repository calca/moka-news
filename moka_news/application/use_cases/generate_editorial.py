"""Use-case helpers for editorial generation context."""

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from moka_news.barista import SimpleBarista, create_ai_provider
from moka_news.editorial import EditorialGenerator
from moka_news.logger import get_logger
from moka_news.models import Article

logger = get_logger(__name__)


def build_editorial_context(
    config: Dict[str, Any],
    args: argparse.Namespace,
    ai_provider: str,
    articles: List[Article],
) -> Tuple[EditorialGenerator, Optional[str], Optional[Path]]:
    """Generate editorial content or fallback to the most recent saved editorial."""
    editorial_content: Optional[str] = None

    keywords = config["ai"].get("keywords", [])
    editorial_prompts = config["ai"].get("editorial_prompts", None)
    language = args.language if args.language else config["ai"].get("language", "en")

    editorial_config = config.get("editorial", {})
    editorials_dir = editorial_config.get("editorials_dir", None)

    ai_instance = create_ai_provider(ai_provider, config)
    if ai_instance is None:
        ai_instance = SimpleBarista()

    editorial_generator = EditorialGenerator(
        ai_instance,
        keywords,
        editorials_dir=editorials_dir,
        editorial_prompts=editorial_prompts,
        language=language,
    )

    editorial_path = None
    try:
        if articles:
            editorial = editorial_generator.generate_editorial(articles)
            editorial_path = editorial_generator.save_editorial(editorial)
            editorial_content = editorial_generator.load_editorial(editorial_path)
            print(f"✓ Editorial generated and saved to: {editorial_path}")
        else:
            recent_editorials = editorial_generator.list_editorials()
            if recent_editorials:
                most_recent = recent_editorials[-1]
                editorial_path = most_recent.filepath
                editorial_content = editorial_generator.load_editorial(editorial_path)
                print(f"✓ Loading most recent editorial: {editorial_path}")
            else:
                print("ℹ️  No articles and no previous editorials found")
    except Exception as exc:
        logger.warning("Error while building editorial context: %s", exc)
        print(f"⚠️  Error with editorial: {exc}")
        previous_editorial = editorial_generator.load_most_recent_editorial()
        if previous_editorial:
            editorial_path = previous_editorial.filepath
            editorial_content = previous_editorial.content
            print(f"↩️  Loaded previous editorial: {editorial_path}")
        else:
            editorial_path = None
            print("ℹ️  No previous editorial available")

    return editorial_generator, editorial_content, editorial_path
