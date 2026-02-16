# MoKa News — Copilot Instructions

## Architecture Overview

MoKa News is a TUI RSS aggregator with AI-powered editorial generation, built around a **coffee metaphor** with three core components:

1. **Grinder** (`moka_news/grinder/`) — Fetches and parses RSS feeds via `feedparser`. Returns `(articles, last_update)` tuples. Filters articles by date using `DownloadTracker`.
2. **Barista** (`moka_news/barista/`) — AI provider abstraction layer. Individual articles are **not** AI-processed; the `AIProvider` subclasses exist to provide the provider instance used only by `EditorialGenerator`. All providers inherit from `AIProvider` (ABC) and implement `generate_summary()`. Factory: `create_ai_provider(name, config)`.
3. **Cup** (`moka_news/cup/`) — Textual-based TUI (`textual` library). The `serve()` function is the entry point, receiving articles, editorial content, callbacks, and config. Contains modal dialogs (`ConfirmationDialog`, `LoadingDialog`, `InfoDialog`) and the main `Cup` app class.

**Data flow:** `main.py` orchestrates: Grinder → Barista (pass-through) → EditorialGenerator (AI here) → Cup (display).

## Key Patterns

- **AI processing happens only in editorial generation**, not on individual articles. The `EditorialGenerator` (`moka_news/editorial.py`) calls `ai_provider.generate_summary()` with a combined prompt of all articles. The Barista's `brew()` method just copies `title`→`ai_title` and `summary`→`ai_summary`.
- **Article dict shape** used everywhere: `{title, link, summary, published, published_dt, source, ai_title, ai_summary}`.
- **Config deep-merge**: `merge_configs()` in `config.py` recursively merges user YAML over `DEFAULT_CONFIG`. Config lookup order: `./moka-news.yaml` → `./.moka-news.yaml` → `~/.config/moka-news/config.yaml` → `~/.moka-news.yaml`.
- **Editorial prompts** use `{content}` and `{keywords}` placeholders. Default prompts live in `DEFAULT_EDITORIAL_PROMPTS` in `config.py`. The output format is `TITLE: ...\nSUMMARY: ...`.
- **Feed storage**: OPML format via `OPMLManager` (`opml_manager.py`), stored at `~/.config/moka-news/feeds.opml`.
- **State files** in `~/.config/moka-news/`: `config.yaml`, `feeds.opml`, `last_download.json`, `editorials/` directory.

## Adding a New AI Provider

1. Create a class inheriting `AIProvider` in `moka_news/barista/__init__.py`.
2. Implement `generate_summary(article, max_content_length, max_tokens) -> {"title": str, "summary": str}`.
3. Register it in the `provider_map` dict inside `create_ai_provider()`.
4. If CLI-based, add to `AI_PROVIDERS` in `first_run_setup.py` with `cli_command` and `install_info`.
5. Add the provider name to the `--ai` choices in `main.py`'s argparse.

## Development Commands

```bash
pip install -e ".[dev]"          # Install with dev deps (pytest, black, ruff)
pip install -e ".[all]"          # Install all optional AI providers
pytest                           # Run tests
black moka_news/                 # Format code (line-length=88)
ruff check moka_news/            # Lint
```

## Testing Conventions

- Tests in `tests/` mirror module names: `test_barista.py`, `test_grinder.py`, `test_editorial.py`, etc.
- Use `SimpleBarista()` as the AI provider in tests (no API keys needed).
- Use `tempfile.TemporaryDirectory()` for file-system-dependent tests (editorials, OPML, tracker).
- Use `unittest.mock.patch` / `monkeypatch` for environment variables and filesystem mocking.
- No conftest.py; fixtures are defined inline per test file.

## Project Conventions

- **Python ≥3.8** compatibility required.
- **Logging**: Use `from moka_news.logger import get_logger; logger = get_logger(__name__)`. Logger outputs to stderr with color.
- **Constants**: All magic numbers live in `moka_news/constants.py` (`MAX_CONTENT_LENGTH=1500`, `MAX_TOKENS=250`, `CLI_GENERATION_TIMEOUT=30`, etc.).
- **Entry point**: `moka-news` CLI → `moka_news.main:main`. First run triggers interactive setup wizard (`first_run_setup.py`).
- **Themes**: Textual themes (`rose-pine`, `rose-pine-dawn`). Toggle in TUI with `t` key.
- **Dependencies**: Core: `feedparser`, `textual`, `openai`, `anthropic`, `python-dotenv`, `pyyaml`. Optional: `google-generativeai`, `mistralai`.
