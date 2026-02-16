# Customizing Editorial Prompts in MoKa News

> **⚠️ IMPORTANT NOTICE**: As of the latest version, MoKa News only processes editorials with AI, not individual articles. This document has been updated to reflect editorial prompt customization. Legacy examples referring to individual article prompts are kept for reference but are no longer functional.

MoKa News supports customizable AI prompts for editorial generation! This guide will help you understand and customize the prompts used for generating morning editorials.

## What Are Editorial Prompts?

Editorial prompts are the instructions sent to AI models (OpenAI, Anthropic, Gemini, Mistral, etc.) to generate daily editorial summaries from collected news articles. By customizing these prompts, you can control how the AI creates your morning briefing.

**Important Note**: Individual article processing has been removed from MoKa News. AI processing now focuses exclusively on editorial generation to provide you with a cohesive morning briefing.

## Default Editorial Prompts

MoKa News comes with well-tested default editorial prompts that work great for most users. You don't need to customize them unless you want specific behavior.

The default editorial prompts include:
- **system_message**: Instructions that set the AI's role as an editorial writer
- **user_prompt**: The main prompt template for creating editorials from multiple articles  
- **keywords_section**: How to integrate your configured keywords into editorial generation
- **format_section**: Instructions for editorial output formatting

## How to Customize Editorial Prompts

### 1. First-Run Setup

During the first-run setup wizard, MoKa News will ask if you want to use default prompts or customize them:

```
📝 AI Prompts Customization (Optional)

MoKa News uses AI prompts to generate article titles and summaries.
You can use the default prompts or customize them later.

Default prompts are well-tested and work great for most users.
Advanced users can customize prompts in the config file using placeholders:
  - {title}: Article title
  - {content}: Article content
  - {keywords}: Your configured keywords

Use default prompts? [Y/n]:
```

Most users should choose "Yes" to use the default prompts.

### 2. Customizing in Config File

After setup, you can customize prompts by editing your configuration file at:
- `~/.config/moka-news/config.yaml` (Linux/Mac)
- Or your current directory: `moka-news.yaml`

Here's the editorial prompts section in the config file:

```yaml
ai:
  editorial_prompts:
    system_message: "You are a skilled news editor creating an engaging morning editorial."
    user_prompt: |
      Create a cohesive morning news editorial from these articles:

      {content}

      Write an engaging editorial that:
      1. Highlights the most important and relevant news
      2. Connects related topics into a coherent narrative
      3. Is enjoyable to read over morning coffee
      4. Is approximately 300-500 words
    keywords_section: |

      Pay special attention to topics related to: {keywords}
    format_section: |

      Format as:
      TITLE: <engaging editorial title>
      SUMMARY: <the editorial content>
```

## Available Placeholders

When customizing editorial prompts, you can use these placeholders:

- `{content}` - The combined content of all collected articles
- `{keywords}` - Your configured keywords (comma-separated)

These placeholders will be automatically replaced with actual values when generating editorials.

## Current Editorial Configuration

To customize editorial prompts, edit your config file and use the `editorial_prompts` section:

```yaml
ai:
  editorial_prompts:
    system_message: "Your custom editorial role"
    user_prompt: "Your custom editorial generation instructions with {content} and {keywords}"
    keywords_section: "How to handle {keywords} in editorials"
    format_section: "Editorial output format"
```

---

## Legacy Examples (No Longer Functional)

> **Note**: The following examples are from when MoKa News processed individual articles. These are kept for historical reference but are no longer functional as MoKa News now focuses exclusively on editorial generation.

### Example 1: More Concise Summaries (LEGACY)

```yaml
ai:
  prompts:
    user_prompt: |
      Article: {title}
      Text: {content}
      
      Create:
      - Catchy title (max 60 chars)
      - Ultra-brief summary (max 100 chars)
```

### Example 2: Technical Focus (LEGACY)

```yaml
ai:
  prompts:
    system_message: "You are a technical editor focusing on engineering details."
    user_prompt: |
      Technical article:
      Title: {title}
      Content: {content}
      
      Provide:
      1. Technical title highlighting key innovation
      2. Summary focusing on technical details and impact
```

### Example 3: Business News Focus (LEGACY)

```yaml
ai:
  prompts:
    user_prompt: |
      Business news:
      {title}
      
      {content}
      
      Generate business-focused:
      - Professional title
      - Summary emphasizing market impact
    format_section: |
      
      TITLE: [your title]
      SUMMARY: [your summary]
```

### Example 4: Multi-language Support

```yaml
ai:
  prompts:
    system_message: "You are a bilingual news editor."
    user_prompt: |
      Article in English:
      Title: {title}
      Content: {content}
      
      Generate title and summary in Italian:
```

## Tips for Customizing Prompts

1. **Start with defaults**: The default prompts work well for most use cases
2. **Be specific**: Clear instructions lead to better AI responses
3. **Set constraints**: Specify length limits (e.g., "max 80 characters")
4. **Test incrementally**: Make small changes and test the results
5. **Use keywords**: Combine custom prompts with keywords for best results
6. **Keep format section**: The AI needs clear output format instructions

## How Prompts Work with Keywords

When you configure both prompts and keywords, they work together:

1. The `user_prompt` processes the article
2. If keywords are configured, the `keywords_section` is added
3. The `format_section` ensures consistent output

Example with keywords:

```yaml
ai:
  keywords:
    - artificial intelligence
    - machine learning
    - cybersecurity
  prompts:
    keywords_section: |
      
      Priority topics: {keywords}
      Emphasize these if mentioned in the article.
```

## Troubleshooting

### AI not using my custom prompts

- Verify the prompts are in the correct config file
- Check that placeholders are spelled correctly: `{title}`, `{content}`, `{keywords}`
- Ensure proper YAML formatting (indentation matters!)

### Getting unexpected summaries

- Make your instructions more specific
- Add examples in the prompt
- Adjust the system_message to set the right context
- Consider adding constraints (length, style, focus areas)

### Want to reset to defaults

Simply delete or comment out the `prompts` section in your config file:

```yaml
ai:
  # prompts:  # Commented out to use defaults
```

Or regenerate your config file:

```bash
moka-news --create-config
```

## Testing Your Prompts

You can test how your prompts work using the example script:

```bash
python examples/keywords_example.py
```

This will show you how prompts are built with and without keywords.

## Advanced: Provider-Specific Prompts

Currently, all AI providers (OpenAI, Anthropic, Gemini, Mistral) use the same prompts. The system_message is particularly important for API-based providers (OpenAI, Anthropic) as it sets the AI's role.

CLI-based providers (copilot-cli, gemini-cli, mistral-cli) use only the combined user_prompt + keywords_section + format_section.

## Need Help?

- Check the example config: `moka-news --create-config`
- Run the keywords example: `python examples/keywords_example.py`
- See default prompts: `moka_news/config.py` (DEFAULT_PROMPTS)

## Summary

✅ Prompts are now external and fully customizable  
✅ Use placeholders: `{title}`, `{content}`, `{keywords}`  
✅ Default prompts work great for most users  
✅ Customize in `~/.config/moka-news/config.yaml`  
✅ Test changes incrementally  
✅ Combine with keywords for best results  

Enjoy your personalized news summaries! ☕
