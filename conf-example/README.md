# MoKa News - Configuration Examples

This directory contains complete configuration examples for different use cases. Copy any of these files to your root directory as `moka-news.yaml` or to `~/.config/moka-news/config.yaml` to use them.

## 🚀 Quick Start

1. **Copy a configuration file**: Choose one that matches your needs
2. **Rename to `moka-news.yaml`**: Place it in your project root or user config directory
3. **Set up API keys**: Either in the config file or as environment variables
4. **Run MoKa News**: `./moka-news` or `python -m moka_news.main`

## 🗂️ Available Configuration Examples

| File | Description | Best For |
|------|-------------|----------|
| `minimal-config.yaml` | Basic configuration with minimal options | Quick start, testing |
| `full-config.yaml` | Complete configuration with all options documented | Understanding all features |
| `openai-config.yaml` | Optimized for OpenAI GPT models | Users with OpenAI API access |
| `anthropic-config.yaml` | Optimized for Anthropic Claude models | Users with Anthropic API access |
| `gemini-config.yaml` | Optimized for Google Gemini (CLI & API) | Users with Google Cloud access |
| `tech-news-config.yaml` | Focused on technology and programming news | Developers, tech enthusiasts |
| `general-news-config.yaml` | Broad news coverage with various sources | General news consumption |
| `productivity-config.yaml` | Optimized for morning productivity workflow | Professional news reading |

## ⚙️ Configuration Sections

### 🤖 AI Provider Configuration (`ai`)

MoKa News supports multiple AI providers:

- **API-based providers**: `openai`, `anthropic`, `gemini`, `mistral`
- **CLI-based providers**: `copilot-cli`, `gemini-cli`, `mistral-cli` 
- **Testing**: `simple` (no AI, for demo purposes)

#### API Keys Setup

**Option 1: Configuration file**
```yaml
ai:
  api_keys:
    openai: "your-api-key-here"
    anthropic: "your-api-key-here"
```

**Option 2: Environment variables** (recommended for security)
```bash
export OPENAI_API_KEY="your-api-key-here"
export ANTHROPIC_API_KEY="your-api-key-here"
export GEMINI_API_KEY="your-api-key-here"
export MISTRAL_API_KEY="your-api-key-here"
export WRITEAS_ALIAS="your-writeas-alias"
export WRITEAS_PASS="your-writeas-pass"
export WRITEAS_COLLECTION_ALIAS="your-collection-alias" # optional
export WRITEAS_API_BASE="https://write.as/api"          # optional override
```

### 📰 RSS Feeds Configuration (`feeds`)

Add your favorite RSS feeds:

```yaml
feeds:
  urls:
    - https://news.ycombinator.com/rss
    - https://www.reddit.com/r/programming/.rss
    - https://feeds.bbci.co.uk/news/technology/rss.xml
```

### 🎨 UI Configuration (`ui`)

Customize the appearance:

```yaml
ui:
  use_tui: true  # Enable Terminal User Interface
  theme: rose-pine  # Default theme
  theme_light: rose-pine-dawn  # Light mode theme
  theme_dark: rose-pine  # Dark mode theme
```

Available themes include any Textual-supported theme (rose-pine, monokai, dracula, etc.)

### 🔄 Refresh Configuration (`refresh`)

Control when and how often news is refreshed:

```yaml
refresh:
  allowed_times: ["08:00", "20:00"]  # Morning and evening
  max_daily_refreshes: 2  # Limit refreshes per day
  require_confirmation_outside_hours: true  # Ask before refreshing outside hours
  auto_refresh_window: 60  # Time window in minutes around allowed times for automatic refresh
```

### ✍️ Editorial Configuration (`editorial`)

Configure the AI-generated morning editorial:

```yaml
editorial:
  editorials_dir: ~/Documents/moka-news-editorials  # Where to save editorials
  opener_command: "code"  # Command to open editorials (VS Code example)
  min_articles: 10         # Minimum articles needed for quality editorial
  extended_window_days: 3  # Days to look back if too few recent articles
```

**Smart Article Fetching:**
If fewer than `min_articles` are found in recent news, MoKa News automatically expands the search window to the last `extended_window_days` days. This ensures you always get a rich editorial even during slow news periods.

Popular opener commands:
- `"code"` - VS Code
- `"vim"` - Vim editor  
- `"nano"` - Nano editor
- `"open"` - Default app (macOS)
- `"xdg-open"` - Default app (Linux)

### ✍️ Write.as Publishing (`writeas`)

Publish the currently opened editorial directly from TUI (shortcut: `u`), always as full editorial:

```yaml
writeas:
  enabled: true
  api_base: https://write.as/api
  alias: null            # Prefer WRITEAS_ALIAS env var
  pass: null             # Prefer WRITEAS_PASS env var
  collection_alias: my-blog
  font: serif
```

MoKa News ottiene sempre il token con login `POST /auth/login` usando `alias` e `pass`.

### 🎯 Keywords and Prompts

Focus AI summaries on specific topics:

```yaml
ai:
  keywords:
    - technology
    - artificial intelligence
    - programming
    - startups
```

Customize AI prompts for your needs (see `full-config.yaml` for examples).

## 🔧 Advanced Configuration

### Custom Prompts

You can fully customize the AI prompts used for:
- Article title and summary generation
- Morning editorial creation

Use placeholders like `{title}`, `{content}`, `{keywords}` in your prompts.

### Token Optimization

Control AI usage and costs:

```yaml
ai:
  max_content_length: 1500  # Characters sent to AI
  max_tokens: 250          # Maximum response tokens
```

### Multiple Configuration Locations

MoKa News searches for configuration files in this order:
1. `./moka-news.yaml` (current directory)
2. `./.moka-news.yaml` (current directory, hidden)
3. `~/.config/moka-news/config.yaml` (user config directory)
4. `~/.moka-news.yaml` (user home, hidden)

## 🔒 Security Best Practices

1. **Use environment variables for API keys** instead of storing them in config files
2. **Add config files with API keys to .gitignore** if committing to version control
3. **Use CLI providers when possible** (like `gemini-cli`) to avoid storing API keys
4. **Rotate API keys regularly** and monitor usage

## 🐛 Troubleshooting

### Common Issues

**No AI summaries generated:**
- Check your API key is valid
- Verify your provider is correctly configured
- Try switching to a CLI provider (if available)

**Config file not found:**
- Ensure the file is named correctly (`moka-news.yaml`)
- Check file permissions (readable)
- Verify the file is in a searched location

**RSS feeds not loading:**
- Test feed URLs in a browser
- Check internet connectivity
- Some feeds may require user agents or have rate limits

### Getting Help

- Check the main README.md for general troubleshooting
- Review the full-config.yaml for all available options
- Run with `--help` to see command-line options

## 📚 Examples by Use Case

### 👨‍💻 For Developers
Use `tech-news-config.yaml` - includes programming, tech, and startup feeds with relevant keywords.

### 📈 For Business Professionals  
Use `general-news-config.yaml` - broader news coverage including business, politics, and world news.

### ☕ For Morning Routine
Use `productivity-config.yaml` - optimized for quick morning news consumption with editorial summaries.

### 🧪 For Testing
Use `minimal-config.yaml` - basic setup to test functionality without complex configuration.
