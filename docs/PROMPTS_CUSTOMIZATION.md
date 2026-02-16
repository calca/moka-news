# Customizing AI Prompts in MoKa News

MoKa News now supports external, customizable AI prompts! This guide will help you understand and customize the prompts used for generating article summaries.

## What Are AI Prompts?

AI prompts are the instructions sent to AI models (OpenAI, Anthropic, Gemini, Mistral, etc.) to generate article titles and summaries. By customizing these prompts, you can control how the AI interprets and summarizes your news articles.

## Default Prompts

MoKa News comes with well-tested default prompts that work great for most users. You don't need to customize them unless you want specific behavior.

The default prompts include:
- **system_message**: Instructions that set the AI's role
- **user_prompt**: The main prompt template for processing articles
- **keywords_section**: How to integrate your configured keywords
- **format_section**: Instructions for output formatting

## How to Customize Prompts

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

Here's the prompts section in the config file:

```yaml
ai:
  prompts:
    system_message: "You are a news editor creating engaging titles and summaries."
    user_prompt: |
      Given this article:
      Title: {title}
      Content: {content}

      Generate:
      1. A concise, engaging title (max 80 characters)
      2. A brief summary (max 200 characters)
    keywords_section: |

      Focus on these keywords/topics if relevant: {keywords}
    format_section: |

      Format as:
      TITLE: <title>
      SUMMARY: <summary>
```

## Available Placeholders

When customizing prompts, you can use these placeholders:

- `{title}` - The original article title
- `{content}` - The article content (automatically truncated to 500 characters)
- `{keywords}` - Your configured keywords (comma-separated)

These placeholders will be automatically replaced with actual values when processing articles.

## Customization Examples

### Example 1: More Concise Summaries

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

### Example 2: Technical Focus

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

### Example 3: Business News Focus

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
