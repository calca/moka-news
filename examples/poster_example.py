#!/usr/bin/env python3
"""Example: deterministic poster generation from editorial markdown.

The poster now uses:
1. Editorial title
2. First cleaned editorial paragraph

No GenAI prompt or poster summarization is used.
"""

import tempfile
from pathlib import Path

from moka_news.poster import PosterGenerator


SAMPLE_EDITORIAL = {
    "title": "The Week in Tech: Breakthroughs and Bold Moves",
    "content": """# The Week in Tech: Breakthroughs and Bold Moves

*Tuesday, February 24, 2026 at 08:00*

---

The past week has been one of the most eventful in recent memory for the technology sector. Across the Atlantic, legislators finalised a sweeping AI governance framework that obligates large model providers to publish safety audits.

Meanwhile, quantum computing edged closer to practical relevance with lower error rates in real workloads.

## Sources

- [Example source](https://example.com)
""",
}


def main() -> None:
    print("☕ MoKa News — Poster Generation Example\n")

    with tempfile.TemporaryDirectory() as tmpdir:
        poster_config = {
            "method": "local",
            "default_template": "story",
        }

        poster_gen = PosterGenerator(
            config=poster_config,
            posters_dir=Path(tmpdir),
        )

        poster_path = poster_gen.generate_poster(
            {
                "title": SAMPLE_EDITORIAL["title"],
                "content": SAMPLE_EDITORIAL["content"],
            },
            template_name="story",
        )

        print(f"✓ Poster saved: {poster_path}")
        print(f"  File size: {poster_path.stat().st_size // 1024} KB")
        print("  Body text source: first cleaned editorial paragraph (automatic)")


if __name__ == "__main__":
    main()
