# Contributing to MoKa News

Thank you for your interest in contributing to MoKa News!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/calca/moka-news.git
cd moka-news
```

2. Install in development mode:
```bash
pip install -e ".[dev]"
```

3. Run the example:
```bash
python examples/demo.py
```

## Project Structure

```
moka-news/
├── moka_news/
│   ├── grinder/      # RSS feed parser (The Grinder)
│   ├── barista/      # AI processing (The Barista)
│   ├── cup/          # TUI interface (The Cup)
│   └── main.py       # Main entry point
├── examples/         # Example scripts
└── tests/           # Test suite (coming soon)
```

## The Three Components

### The Grinder (Il Macinino)
Responsible for fetching and parsing RSS feeds using `feedparser`.

**Key files:**
- `moka_news/grinder/__init__.py`

**What it does:**
- Fetches RSS feeds from multiple sources
- Parses feed data into a standard format
- Handles errors gracefully

### The Barista (L'Agente AI)
Processes raw article text and generates summaries using AI.

**Key files:**
- `moka_news/barista/__init__.py`

**What it does:**
- Takes raw article data
- Generates concise titles (max 80 chars)
- Creates brief summaries (max 200 chars)
- Supports multiple AI providers (OpenAI, Anthropic, Simple)

### The Cup (La Tazzina)
Displays the news digest in a beautiful TUI.

**Key files:**
- `moka_news/cup/__init__.py`

**What it does:**
- Creates a Textual-based terminal UI
- Displays articles in cards
- Supports clicking to open links
- Provides keyboard shortcuts

## Code Style

We use:
- `black` for code formatting
- `ruff` for linting

Format your code before committing:
```bash
black moka_news/
ruff check moka_news/
```

## Testing

Run tests with:
```bash
pytest
```

## Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Ensure code is formatted
6. Submit a pull request

## Ideas for Contributions

- Add more RSS feed sources
- Improve AI prompt engineering
- Add more TUI features (search, filtering, etc.)
- Add caching for articles
- Add configuration file support
- Improve error handling
- Add more tests
- Improve documentation

## Questions?

Feel free to open an issue for questions or discussions!
