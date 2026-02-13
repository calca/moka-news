# ☕ MoKa News

**Morning Persona News** - A beautiful TUI (Text User Interface) RSS news aggregator with AI-powered summaries.

## Architecture

MoKa News consists of three main components working together:

### 🔄 The Grinder (Il Macinino)
A Python module using `feedparser` to extract data from RSS feeds. It gathers articles from multiple sources and prepares them for processing.

### 🤖 The Barista (L'Agente AI)
An AI agent that takes raw article text and generates engaging titles and concise summaries using:
- **API-based providers:**
  - OpenAI (GPT models)
  - Anthropic (Claude models)
  - Google Gemini (Gemini Pro)
  - Mistral AI (Mistral models)
- **CLI-based providers:**
  - GitHub Copilot CLI (gh copilot)
  - Gemini CLI (gcloud)
  - Mistral CLI
- Simple mode (no AI, for testing)

### ☕ The Cup (La Tazzina)
A beautiful Textual-based TUI that displays your personalized news digest in the terminal.

## Features

- 📰 Parse multiple RSS feeds simultaneously
- 🤖 AI-powered article summarization with multiple providers (OpenAI, Anthropic, Gemini, Mistral)
- ⚙️  Configuration file support (YAML)
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

# Optional: Install additional AI providers
pip install -e ".[gemini]"    # For Google Gemini support
pip install -e ".[mistral]"   # For Mistral AI support
pip install -e ".[all]"       # Install all AI providers
```

## Configuration

MoKa News can be configured in multiple ways:

### 1. Configuration File (Recommended)

Create a configuration file for persistent settings:

```bash
# Create a sample configuration file
moka-news --create-config

# This creates 'moka-news.yaml' in your current directory
```

Edit the `moka-news.yaml` file:

```yaml
# AI Provider Configuration
ai:
  provider: simple  # Options: simple, openai, anthropic, gemini, mistral
  
  api_keys:
    openai: your-key-here
    anthropic: your-key-here
    gemini: your-key-here
    mistral: your-key-here

# RSS Feed Configuration
feeds:
  urls:
    - https://news.ycombinator.com/rss
    - https://www.reddit.com/r/programming/.rss
    - https://github.blog/feed/

# UI Configuration
ui:
  use_tui: true  # Set to false to use console output
```

You can place the config file in:
- Current directory: `./moka-news.yaml` or `./.moka-news.yaml`
- User config: `~/.config/moka-news/config.yaml`
- Home directory: `~/.moka-news.yaml`

### 2. Environment Variables

For AI-powered summaries, you can set environment variables:

```bash
# For OpenAI
export OPENAI_API_KEY=your-openai-api-key-here

# For Anthropic
export ANTHROPIC_API_KEY=your-anthropic-api-key-here

# For Google Gemini
export GEMINI_API_KEY=your-gemini-api-key-here

# For Mistral AI
export MISTRAL_API_KEY=your-mistral-api-key-here
```

Or create a `.env` file in the project root with the same variables.

### 3. Command Line Arguments

CLI arguments override both config file and environment variables.

## Usage

### Basic Usage

Run with default feeds and simple (non-AI) processing:

```bash
moka-news
```

### With AI Processing

**API-based providers:**

Use OpenAI for intelligent summaries:

```bash
moka-news --ai openai
```

Use Anthropic Claude for summaries:

```bash
moka-news --ai anthropic
```

Use Google Gemini for summaries:

```bash
moka-news --ai gemini
```

Use Mistral AI for summaries:

```bash
moka-news --ai mistral
```

**CLI-based providers:**

Use GitHub Copilot CLI (requires `gh` CLI):

```bash
moka-news --ai copilot-cli
```

Use Gemini CLI via gcloud (requires `gcloud` CLI):

```bash
moka-news --ai gemini-cli
```

Use Mistral CLI (requires `mistral` CLI):

```bash
moka-news --ai mistral-cli
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
# Use custom config file
moka-news --config myconfig.yaml

# Use OpenAI with custom feeds
moka-news --ai openai --feeds https://news.ycombinator.com/rss

# Console output instead of TUI
moka-news --no-tui
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
