"""Use-case for generating a poster from editorial content."""

from datetime import datetime
from typing import Any, Dict


def generate_poster_from_editorial(
    content: str,
    title: str,
    poster_config: Dict[str, Any],
    posters_dir: Any,
):
    """Generate a poster file and return the output path."""
    from moka_news.poster import PosterGenerator

    poster_gen = PosterGenerator(config=poster_config, posters_dir=posters_dir)

    editorial_data = {
        "title": title,
        "content": content,
        "timestamp": datetime.now(),
    }

    template_name = poster_config.get("default_template", "story")
    return poster_gen.generate_poster(editorial_data, template_name)
