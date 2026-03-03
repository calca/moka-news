<p align="center">
  <img src="assets/moka-news-logo.png" alt="MoKa News Logo" width="200"/>
</p>

# ☕ MoKa News

**Morning News** - A beautiful TUI (Text User Interface) RSS news aggregator with AI-powered editorial generation.

## Architecture

MoKa News now follows a layered architecture so CLI, orchestration, storage, and UI are clearly separated:

- `moka_news/cli` - Argument parsing and first-run setup wizard
- `moka_news/application` - Use-cases and services (fetch, editorial generation, TUI workflows)
- `moka_news/infrastructure` - Config and storage adapters (OPML, trackers, editorial repository)
- `moka_news/tui` - Textual UI implementation
- `moka_news/grinder`, `moka_news/barista`, `moka_news/poster`, `moka_news/publisher` - Core feature modules

### 🔄 The Grinder (Il Macinino)
A Python module using `feedparser` to extract data from RSS feeds. It gathers articles from multiple sources, filters them by date (only new articles since last download), and prepares them for processing.

### 📝 The Editorial Generator (AI-Powered)
Uses AI to create a cohesive morning editorial from multiple articles, combining the most important news into a single, enjoyable reading experience. Editorials are saved as markdown files with source links for future reference.

Supports multiple AI providers:
- **API-based providers:**
  - OpenAI (GPT models)
  - Anthropic (Claude models)
  - Google Gemini (Gemini Pro)
  - Mistral AI (Mistral models)
- **CLI-based providers:**
  - GitHub Copilot CLI
  - Gemini CLI
  - Mistral CLI
- Simple mode (no AI, for testing)

### ☕ The TUI (La Tazzina)
A beautiful Textual-based TUI that displays your personalized morning editorial in the terminal. Features editorial-focused reading, past editorial browsing, poster generation, and publishing.

## Features

- 📰 Parse multiple RSS feeds simultaneously
- 🤖 **AI-powered editorial generation** with multiple providers (OpenAI, Anthropic, Gemini, Mistral)
- 📝 **AI-Generated Morning Editorials** - Get a single, cohesive editorial combining the most important news
- 🎯 **Smart first-run setup** - Interactive wizard to configure AI provider and feeds
- 🔑 **Keyword-focused editorials** - Configure keywords to focus AI editorials on topics you care about
- 📅 **Smart date filtering** - Only fetch articles since your last download
- 💾 **Editorial archive** - All editorials saved as markdown files for future reference
- 🗂️  **Browse past editorials** - Access and read previous morning editions through the TUI
- 📚 **Collapsible source section** - Sources list appears in a collapsible widget in the TUI for cleaner reading
- ⚙️  Configuration file support (YAML)
- 🎨 Beautiful terminal user interface
- ⌨️  Keyboard shortcuts for navigation (h: history, t: toggle theme, r: refresh)
- 🔄 **Scheduled refreshes** - Automatic updates at morning (8 AM) and evening (8 PM)
- ⚠️  **Smart refresh control** - Asks for confirmation when refreshing outside scheduled times
- 📅 **Last update display** - Always know when your feed was refreshed
- ✍️ **Publish from TUI** - Publish current editorial to all enabled providers (Write.as, Buttondown)
- 🔗 Source links in editorial markdown for easy access
- 🚀 Fast and lightweight
- 💾 RSS feed management with OPML storage

## TUI

<p align="center">
  <img src="assets/screenshot.png" alt="MoKa News TUI" width="500"/>
</p>

## Installation

### Prerequisites
- Python 3.8 or higher
- pip
- (Optional) AI provider CLI tools: `copilot`, `gemini`, `mistral`

### Install from PyPI (Coming Soon)

Once the package is published to PyPI, you'll be able to install it with:

```bash
# Basic installation
pip install moka-news

# With additional AI providers
pip install moka-news[gemini]    # For Google Gemini support
pip install moka-news[mistral]   # For Mistral AI support
pip install moka-news[all]       # Install all AI providers

# With development dependencies
pip install moka-news[dev]
```

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
2. **Configure keywords** (optional) - Set keywords to focus AI editorials on topics you care about
3. **Configure RSS feeds** - Accept our curated list of 5 tech feeds (stored as OPML) or add your own later with `moka-news --add-feed`

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
- Optionally configure keywords to focus editorials on your interests
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
# Note: RSS feeds are managed via OPML (moka-news --add-feed / --list-feeds),
# not in this YAML file.

# AI Provider Configuration
ai:
  provider: gemini-cli  # Options: openai, anthropic, gemini, mistral, copilot-cli, gemini-cli, mistral-cli
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
  use_tui: true  # TUI is the primary interface
  theme: rose-pine  # Default theme (dark, relaxing)
  theme_light: rose-pine-dawn  # Light theme option
  theme_dark: rose-pine  # Dark theme option

# Refresh Configuration
refresh:
  allowed_times:
    - "08:00"  # Morning refresh time
    - "20:00"  # Evening refresh time
  max_daily_refreshes: 2  # Maximum number of refreshes per day
  require_confirmation_outside_hours: true  # Ask for confirmation outside scheduled times
  auto_refresh_window: 60  # Time window in minutes around allowed times for automatic refresh
```

**Refresh Configuration:**

MoKa News focuses on editorial quality by limiting refreshes to specific times:
- **Morning refresh:** 8:00 AM - Start your day with fresh news
- **Evening refresh:** 20:00 (8:00 PM) - Catch up on the day's events
- **Auto-refresh window:** 60 minutes around each allowed time (e.g., 7:30-8:30, 19:30-20:30)
- **Manual refresh control:** When you press 'r' outside scheduled hours, you'll be asked to confirm
- **First run:** On the first run, articles from the previous day are fetched to provide initial content

This approach ensures you get quality editorials at predictable times without information overload.

**Theme Configuration:**

MoKa News includes two beautiful, relaxing themes optimized for comfortable reading:
- **Dark theme:** `rose-pine` - Soft purple tones that are easy on the eyes
- **Light theme:** `rose-pine-dawn` - Warm, gentle light theme for daytime reading

Switch between themes anytime by pressing `t` in the TUI!

Other available Textual themes include: `textual-dark`, `textual-light`, `nord`, `gruvbox`, `catppuccin-mocha`, `dracula`, `tokyo-night`, `monokai`, `solarized-light`, `solarized-dark`, and more.

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

# For Write.as publishing
export WRITEAS_ALIAS=your-writeas-alias
export WRITEAS_PASS=your-writeas-pass
export WRITEAS_COLLECTION_ALIAS=your-collection-alias
export WRITEAS_API_BASE=https://write.as/api

# For Buttondown publishing
export BUTTONDOWN_API_KEY=your-buttondown-api-key
```

Or create a `.env` file in the project root with the same variables.

### 4. Keywords Configuration

You can configure keywords to help focus AI-generated editorials on specific topics you're interested in.

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

When keywords are configured, the AI will receive these as context when generating editorials:
- The AI will prioritize these topics when creating the morning editorial
- Helps customize editorials to your specific interests
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

On first run, this will launch the setup wizard. On subsequent runs, it will use your saved configuration to fetch and display news with AI-powered editorials.

### Basic Usage

Run with default settings (uses your configured AI provider):

```bash
moka-news
```

### With Specific AI Provider

Override your configured provider:

**API-based providers:**

Use OpenAI for editorial generation:

```bash
moka-news --ai openai
```

Use Anthropic Claude for editorial generation:

```bash
moka-news --ai anthropic
```

Use Google Gemini for editorial generation:

```bash
moka-news --ai gemini
```

Use Mistral AI for editorial generation:

```bash
moka-news --ai mistral
```

**CLI-based providers:**

Use GitHub Copilot CLI (requires `copilot` command available):

```bash
moka-news --ai copilot-cli
```

Use Gemini CLI (requires `gemini` command available):

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

**Note:** Simple mode is for demo/testing only and does not use AI for editorial generation.

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

### Combined Options

```bash
# Use custom config file
moka-news --config myconfig.yaml

# Use OpenAI with custom feeds
moka-news --ai openai --feeds https://news.ycombinator.com/rss
```

## Keyboard Shortcuts

While in the TUI:

- `q` or `Ctrl+C` - Quit the application
- `r` - Refresh feed (asks for confirmation if outside scheduled hours)
- `g` - Generate poster from current editorial
- `u` - Publish current editorial to enabled providers
- `h` - Browse past editorials (history)
- `t` - Toggle between light and dark theme

The TUI displays your morning editorial, with easy access to past editorials through the history feature. It automatically refreshes at 8:00 AM and 8:00 PM daily. Manual refreshes outside these times will prompt for confirmation to maintain editorial quality. ☕

## Morning Editorial Feature

MoKa News generates a single, AI-powered editorial that combines your news articles into a coherent morning reading experience:

- **Smart Content Selection**: The AI processes all articles filtered by date (since last download) based on your keywords
- **Cohesive Narrative**: Articles are combined into a single, flowing editorial rather than separate summaries
- **Source Links**: All source articles are linked at the end of the editorial
- **Markdown Archive**: Each editorial is saved as a markdown file (default: `~/.config/moka-news/editorials/`)
- **Date-based Filename**: Editorials are saved as `YYYY-MM-DD_HH-MM.md` for easy organization
- **History Access**: Press `h` in the TUI to browse and read past editorials
- **Customizable Prompts**: Fine-tune how the AI generates editorials by customizing prompts in your config file
- **Configurable Location**: Save editorials to any directory of your choice

### Configuring Editorial Settings

You can customize editorial settings in your `config.yaml`:

```yaml
editorial:
  # Directory to save editorials (defaults to ~/.config/moka-news/editorials if not specified)
  editorials_dir: ~/Documents/my-news-editorials
  
  # Smart article fetching
  min_articles: 10         # Minimum articles needed for quality editorial
  extended_window_days: 3  # Days to look back if too few recent articles
```

**Smart Article Fetching:**

MoKa News automatically ensures you have enough articles for a quality editorial:
- If fewer than `min_articles` are found in the recent time window, MoKa News automatically expands the search to the last `extended_window_days` days
- This ensures you always get a rich, informative editorial even during slow news periods
- Defaults: 10 minimum articles, 3-day extended window
- Configurable to match your reading preferences

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

### Publishing From The TUI

From the TUI you can publish the current editorial with:
- `u` (keyboard shortcut).

Add this section to `config.yaml`:

```yaml
publish:
  providers:
    - type: writeas
      enabled: true
      api_base: https://write.as/api
      alias: null            # or WRITEAS_ALIAS env var
      pass: null             # or WRITEAS_PASS env var
      collection_alias: my-blog
      font: serif

    - type: buttondown
      enabled: false
      api_key: null          # or BUTTONDOWN_API_KEY env var
      api_base: https://api.buttondown.com/v1
      status: draft
```

All enabled providers are executed on publish.

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

Build and quality checks are defined in [`.github/workflows/ci.yml`](.github/workflows/ci.yml).
The CI pipeline runs:
- `ruff check moka_news tests examples`
- `black --check moka_news tests examples`
- `pytest tests/ -v`
- `mypy` (on Python 3.11 only)

### Local Setup

```bash
# Install project with dev dependencies
pip install -e ".[dev]"
```

### Run The Same Gates As CI

```bash
# Lint with ruff
ruff check moka_news tests examples

# Check formatting with black (same as CI)
black --check moka_news tests examples

# Type check critical modules
mypy

# Run tests
pytest tests/ -v
```

## Default Configuration

After the first-run setup, MoKa News uses:
- **AI Mode:** AI-powered editorial generation is enabled by default (Gemini CLI or your chosen provider)
- **Editorial Generation:** Automatically creates morning editorials from fetched articles
- **Date Filtering:** Only fetches articles published since the last download
- **Simple Mode:** Available as `--ai simple` for demo/testing only (no AI for editorials)
- **RSS Feeds:** Stored in `~/.config/moka-news/feeds.opml`
- **Config File:** Located at `~/.config/moka-news/config.yaml`
- **Editorials Archive:** Saved in `~/.config/moka-news/editorials/` by default (configurable)
- **Download Tracking:** Last download timestamp in `~/.config/moka-news/last_download.json`

The first-run wizard makes it easy to get started with AI-powered morning editorials!

## Project Structure

```
moka-news/
├── moka_news/
│   ├── __init__.py
│   ├── main.py                # Entry point
│   ├── cli/                   # Parser + first-run wizard
│   ├── application/           # Use-cases and services
│   ├── infrastructure/        # Config + storage adapters
│   ├── tui/                   # Primary Textual UI implementation
│   ├── grinder/               # RSS feed parser
│   ├── barista/               # AI providers
│   ├── poster/                # Poster generation
│   └── publisher/             # Publish providers
├── pyproject.toml        # Project configuration
├── CHANGELOG.md          # Version history
├── .github/workflows/ci.yml  # CI quality gates
├── README.md
└── LICENSE
```

## Contributing

Contributions are welcome via Pull Request.

Before opening a PR, run the same gates used in CI:

```bash
ruff check moka_news tests examples
black --check moka_news tests examples
pytest tests/ -v
mypy
```

A PR is considered ready when all CI checks pass across the Python version matrix (`3.8` to `3.12`).

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Gianluigi Calcaterra

## Acknowledgments

- Built with [Textual](https://textual.textualize.io/) for the TUI
- Uses [feedparser](https://feedparser.readthedocs.io/) for RSS parsing
- Powered by OpenAI, Anthropic, Google Gemini, and Mistral AI for editorial generation
