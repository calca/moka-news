<p align="center">
  <img src="assets/logo.png" alt="MOKA NEWS Logo" width="400"/>
</p>

> **Note**: If the logo is not displaying, run `./download-logo.sh` to download it, or manually download it from [here](https://github.com/user-attachments/assets/b7ba51ff-ecc2-478e-a652-698b7c1b31ca) and save it as `assets/logo.png`.

# ☕ MoKa News

**Morning Persona News** - A beautiful TUI (Text User Interface) RSS news aggregator with AI-powered summaries.

## Architecture

MoKa News consists of four main components working together:

### 🔄 The Grinder (Il Macinino)
A Python module using `feedparser` to extract data from RSS feeds. It gathers articles from multiple sources, filters them by date (only new articles since last download), and prepares them for processing.

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

### 📝 The Editorial Generator
Creates a cohesive morning editorial from multiple articles, combining the most important news into a single, enjoyable reading experience. Editorials are saved as markdown files with source links for future reference.

### ☕ The Cup (La Tazzina)
A beautiful Textual-based TUI that displays your personalized news digest in the terminal. Features multiple views (editorial/articles), past editorial browsing, and keyboard navigation.

## Features

- 📰 Parse multiple RSS feeds simultaneously
- 🤖 AI-powered article summarization with multiple providers (OpenAI, Anthropic, Gemini, Mistral)
- 📝 **AI-Generated Morning Editorials** - Get a single, cohesive editorial combining the most important news
- 🎯 **Smart first-run setup** - Interactive wizard to configure AI provider and feeds
- 🔑 **Keyword-focused summaries** - Configure keywords to focus AI summaries on topics you care about
- 📅 **Smart date filtering** - Only fetch articles since your last download
- 💾 **Editorial archive** - All editorials saved as markdown files for future reference
- 🗂️  **Browse past editorials** - Access and read previous morning editions through the TUI
- ⚙️  Configuration file support (YAML)
- 🎨 Beautiful terminal user interface
- ⌨️  Keyboard shortcuts for navigation (e: editorial, a: articles, h: history)
- 🔄 **Manual refresh** - Press 'r' to fetch latest articles
- ⏰ **Auto-refresh at 8:00 AM** - Wake up to fresh news with your morning coffee! ☕
- 📅 **Last update display** - Always know when your feed was refreshed
- 🔗 Click to open articles in browser
- 🚀 Fast and lightweight
- 💾 RSS feed management with OPML storage

## Installation

### Prerequisites
- Python 3.8 or higher
- pip
- (Optional) AI provider CLI tools: `gh` for GitHub Copilot, `gcloud` for Gemini, `mistral` for Mistral

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

### First Run

On your first run, MoKa News will launch an interactive setup wizard that will:

1. **Select your AI provider** - Choose from OpenAI, Anthropic, Gemini, Mistral, or CLI-based providers
2. **Configure keywords** (optional) - Set keywords to focus AI summaries on topics you care about
3. **Configure RSS feeds** - Accept our curated list of 5 tech feeds or configure your own later

Simply run:

```bash
moka-news
```

The wizard will guide you through the setup and create:
- Configuration file at `~/.config/moka-news/config.yaml`
- OPML feeds file at `~/.config/moka-news/feeds.opml`

**Note:** AI providers require API keys (set via environment variables) or CLI tools installed and configured.

## Configuration

MoKa News can be configured in multiple ways:

### 1. First-Run Setup Wizard (Recommended)

On first launch, MoKa News will automatically run an interactive setup wizard to help you:
- Choose your preferred AI provider
- Optionally configure keywords to focus summaries on your interests
- Configure your RSS feeds with our curated tech feed suggestions

Simply run `moka-news` and follow the prompts!

### 2. Configuration File

After the first-run setup, your configuration is saved to `~/.config/moka-news/config.yaml`.

You can also create a configuration file manually:

```bash
# Create a sample configuration file
moka-news --create-config

# This creates 'moka-news.yaml' in your current directory
```

Edit the `moka-news.yaml` file:

```yaml
# AI Provider Configuration
ai:
  provider: openai  # Options: openai, anthropic, gemini, mistral, copilot-cli, gemini-cli, mistral-cli
                     # Note: 'simple' mode is for demo/testing only
  
  api_keys:
    openai: your-key-here
    anthropic: your-key-here
    gemini: your-key-here
    mistral: your-key-here
  
  # Keywords for summary generation (optional)
  # These keywords help focus the AI on specific topics or aspects
  keywords:
    - technology
    - artificial intelligence
    - programming
  
  # Editorial Prompts (optional)
  # Customize how the AI generates morning editorials
  editorial_prompts:
    system_message: "You are a skilled news editor creating an engaging morning editorial."
    user_prompt: |
      Create a cohesive morning news editorial from these articles:
      {content}
      
      Write an engaging editorial that highlights important news and
      connects topics into a coherent narrative enjoyable over morning coffee.
    keywords_section: |
      Pay special attention to topics related to: {keywords}

# UI Configuration
ui:
  use_tui: true  # Set to false to use console output
```

You can place the config file in:
- Current directory: `./moka-news.yaml` or `./.moka-news.yaml`
- User config: `~/.config/moka-news/config.yaml`
- Home directory: `~/.moka-news.yaml`

### 3. Environment Variables

For API-based AI providers, you can set environment variables:

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

### 4. Keywords Configuration

You can configure keywords to help focus AI-generated summaries on specific topics you're interested in.

**During first-run setup:** The setup wizard will prompt you to optionally configure keywords.

**Manual configuration:** Add them to your configuration file:

```yaml
ai:
  keywords:
    - technology
    - artificial intelligence
    - machine learning
    - cybersecurity
    - programming
```

When keywords are configured, the AI will receive these as context when generating summaries:
- The AI will prioritize these topics when relevant to the article
- Helps customize summaries to your specific interests
- Optional - the system works perfectly without keywords
- All AI providers support keywords (OpenAI, Anthropic, Gemini, Mistral, CLI variants)

**Example use cases:**
- Focus on specific technologies: `python`, `rust`, `kubernetes`
- Emphasize certain domains: `fintech`, `healthcare`, `education`
- Highlight particular aspects: `security`, `performance`, `user experience`

To see keywords in action, check out the example:
```bash
python examples/keywords_example.py
```

### 5. Command Line Arguments

CLI arguments override both config file and environment variables.

## Usage

### Quick Start

Simply run:

```bash
moka-news
```

On first run, this will launch the setup wizard. On subsequent runs, it will use your saved configuration to fetch and display news with AI-powered summaries.

### Basic Usage

Run with default settings (uses your configured AI provider):

```bash
moka-news
```

### With Specific AI Provider

Override your configured provider:

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

### Demo Mode (No AI)

For testing without AI:

```bash
moka-news --ai simple
```

**Note:** Simple mode is for demo/testing only and does not generate AI summaries.

### Custom RSS Feeds

Specify your own RSS feeds on the command line:

```bash
moka-news --feeds https://example.com/feed.xml https://another.com/rss
```

### Feed Management

MoKa News stores your RSS feeds in OPML format for easy management and portability. The first-run wizard will suggest 5 curated tech feeds:

1. **Hacker News** - https://news.ycombinator.com/rss
2. **GitHub Blog** - https://github.blog/feed/
3. **The Verge - Tech** - https://www.theverge.com/rss/index.xml
4. **TechCrunch** - https://techcrunch.com/feed/
5. **Ars Technica** - https://feeds.arstechnica.com/arstechnica/index

#### Add a feed

```bash
moka-news --add-feed https://example.com/feed.xml
```

#### Remove a feed

```bash
moka-news --remove-feed https://example.com/feed.xml
```

#### List configured feeds

```bash
moka-news --list-feeds
```

#### Custom OPML file location

By default, feeds are stored in `~/.config/moka-news/feeds.opml`. You can specify a custom location:

```bash
moka-news --opml /path/to/custom/feeds.opml
```

The OPML file is stored in standard OPML 2.0 format at `~/.config/moka-news/feeds.opml`, making it compatible with other RSS readers and aggregators.

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
- `r` - Refresh feed (fetch latest articles)
- `e` - Toggle between editorial and articles view
- `a` - Show articles view
- `h` - Browse past editorials (history)
- Mouse click on article - Open in browser

The TUI displays your morning editorial by default, with easy access to individual articles and past editorials. It also automatically refreshes at 8:00 AM daily for your morning coffee! ☕

## Morning Editorial Feature

MoKa News generates a single, AI-powered editorial that combines your news articles into a coherent morning reading experience:

- **Smart Content Selection**: The AI processes all articles filtered by date (since last download) based on your keywords
- **Cohesive Narrative**: Articles are combined into a single, flowing editorial rather than separate summaries
- **Source Links**: All source articles are linked at the end of the editorial
- **Markdown Archive**: Each editorial is saved as a markdown file in `~/.config/moka-news/editorials/`
- **Date-based Filename**: Editorials are saved as `YYYY-MM-DD_HH-MM.md` for easy organization
- **History Access**: Press `h` in the TUI to browse and read past editorials
- **Customizable Prompts**: Fine-tune how the AI generates editorials by customizing prompts in your config file

### Customizing Editorial Generation

You can customize the editorial generation by adding `editorial_prompts` to your `config.yaml`:

```yaml
ai:
  editorial_prompts:
    system_message: "You are a skilled news editor..."
    user_prompt: |
      Create a cohesive morning news editorial from these articles:
      {content}
      
      [Your custom instructions here]
    keywords_section: |
      Pay special attention to: {keywords}
```

This allows you to fine-tune:
- The editorial style and tone
- How topics are connected
- The level of detail
- Focus areas and priorities

Example editorial structure:
```markdown
# Your Morning News

*Monday, February 14, 2026 at 08:00*

---

[AI-generated editorial content combining multiple articles...]

---

## Sources

- **Article Title** - *Source Name*
  [https://example.com/article](https://example.com/article)
...
```

The editorial feature respects your configured keywords and processes all articles (not just a subset), ensuring comprehensive coverage of the day's news!

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

## Default Configuration

After the first-run setup, MoKa News uses:
- **AI Mode:** AI-powered summaries are enabled by default (OpenAI or your chosen provider)
- **Editorial Generation:** Automatically creates morning editorials from fetched articles
- **Date Filtering:** Only fetches articles published since the last download
- **Simple Mode:** Available as `--ai simple` for demo/testing only (no AI summaries)
- **RSS Feeds:** Stored in `~/.config/moka-news/feeds.opml`
- **Config File:** Located at `~/.config/moka-news/config.yaml`
- **Editorials Archive:** Saved in `~/.config/moka-news/editorials/`
- **Download Tracking:** Last download timestamp in `~/.config/moka-news/last_download.json`

The first-run wizard makes it easy to get started with intelligent news summaries!

## Project Structure

```
moka-news/
├── moka_news/
│   ├── __init__.py
│   ├── main.py           # Main entry point
│   ├── opml_manager.py   # OPML feed management
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
