# ☕ MoKa News

**Morning Persona News** - A beautiful TUI (Text User Interface) RSS news aggregator with AI-powered summaries.

## Architecture

MoKa News consists of three main components working together:

### 🔄 The Grinder (Il Macinino)
A Python module using `feedparser` to extract data from RSS feeds. It gathers articles from multiple sources and prepares them for processing.

### 🤖 The Barista (L'Agente AI)
An AI agent that takes raw article text and generates engaging titles and concise summaries using:
- OpenAI (GPT models)
- Anthropic (Claude models)
- Simple mode (no AI, for testing)

### ☕ The Cup (La Tazzina)
A beautiful Textual-based TUI that displays your personalized news digest in the terminal.

## Features

- 📰 Parse multiple RSS feeds simultaneously
- 🤖 AI-powered article summarization (optional)
- 🎨 Beautiful terminal user interface
- ⌨️  Keyboard shortcuts for navigation
- 🔗 Click to open articles in browser
- 🚀 Fast and lightweight

## Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Install from source

```bash
# Clone the repository
git clone https://github.com/calca/moka-news.git
cd moka-news

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Configuration

### API Keys (Optional)

For AI-powered summaries, create a `.env` file in the project root:

```bash
# For OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# For Anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

## Usage

### Basic Usage

Run with default feeds and simple (non-AI) processing:

```bash
moka-news
```

### With AI Processing

Use OpenAI for intelligent summaries:

```bash
moka-news --ai openai
```

Use Anthropic Claude for summaries:

```bash
moka-news --ai anthropic
```

### Custom RSS Feeds

Specify your own RSS feeds:

```bash
moka-news --feeds https://example.com/feed.xml https://another.com/rss
```

### Console Output

Display articles in console instead of TUI:

```bash
moka-news --no-tui
```

### Combined Options

```bash
moka-news --ai openai --feeds https://news.ycombinator.com/rss
```

## Keyboard Shortcuts

While in the TUI:

- `q` or `Ctrl+C` - Quit the application
- `r` - Refresh feed (coming soon)
- Mouse click on article - Open in browser

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Format code with black
black moka_news/

# Lint with ruff
ruff check moka_news/
```

## Default RSS Feeds

MoKa News comes with these default feeds:
- Hacker News
- Reddit Programming
- GitHub Blog

You can easily customize this list by providing your own feeds.

## Project Structure

```
moka-news/
├── moka_news/
│   ├── __init__.py
│   ├── main.py           # Main entry point
│   ├── grinder/          # RSS feed parser
│   │   └── __init__.py
│   ├── barista/          # AI processing
│   │   └── __init__.py
│   └── cup/              # TUI interface
│       └── __init__.py
├── pyproject.toml        # Project configuration
├── README.md
└── LICENSE
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Gianluigi Calcaterra

## Acknowledgments

- Built with [Textual](https://textual.textualize.io/) for the TUI
- Uses [feedparser](https://feedparser.readthedocs.io/) for RSS parsing
- Powered by OpenAI and Anthropic for AI summaries
