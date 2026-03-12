#!/usr/bin/env python3
"""
Example: Using Azure AI Foundry for AI-powered summaries

Before running this example:
1. Install the Azure AI Inference SDK:
   pip install "moka-news[azure]"
   # or: pip install azure-ai-inference

2. Set your Azure AI Foundry credentials:
   export AZURE_AI_API_KEY='your-api-key-here'
   export AZURE_AI_ENDPOINT='https://my-foundry.services.ai.azure.com/models'
   export AZURE_AI_MODEL='gpt-4o'   # or the deployed model name
    export AZURE_AI_API_VERSION='2024-05-01-preview'  # optional override for model compatibility

3. Or create a .env file with:
   AZURE_AI_API_KEY=your-api-key-here
   AZURE_AI_ENDPOINT=https://my-foundry.services.ai.azure.com/models
   AZURE_AI_MODEL=gpt-4o
   AZURE_AI_API_VERSION=2024-05-01-preview

Required Azure resources:
  - An Azure AI Foundry project with a deployed model endpoint
  - A Serverless API or Managed Compute endpoint
  - The endpoint URL and API key from the Deployments + Endpoints page

Note:
    - Different models can support different API versions.
    - If you receive HTTP 404 from Azure, check endpoint/model first, then try another API version
        via AZURE_AI_API_VERSION (or ai.azure_api_version in config).
"""

import os
from dotenv import load_dotenv
from moka_news.barista import AzureAIBarista, SimpleBarista


def _brew(provider, articles):
    """Process articles through an AI provider, adding ai_title/ai_summary."""
    processed = []
    for article in articles:
        result = provider.generate_summary(article)
        out = article.copy()
        out["ai_title"] = result["title"]
        out["ai_summary"] = result["summary"]
        processed.append(out)
    return processed


# Sample articles for demonstration
sample_articles = [
    {
        "title": "Python 3.13 Released with New Features",
        "summary": (
            "The Python Software Foundation announced the release of Python 3.13, "
            "featuring improved performance, new syntax enhancements, and better error messages. "
            "The new version includes experimental features like free-threaded mode and "
            "an improved interactive interpreter with multi-line editing support."
        ),
        "link": "https://example.com/python-3.13",
        "published": "2024-10-01",
        "source": "Python News",
    },
    {
        "title": "AI Models Continue to Advance",
        "summary": (
            "Recent developments in artificial intelligence show significant improvements "
            "in model capabilities, with new architectures achieving better performance on "
            "various benchmarks while using less computational resources."
        ),
        "link": "https://example.com/ai-advances",
        "published": "2024-10-02",
        "source": "Tech Review",
    },
]


def demo_azure():
    """Demonstrate using Azure AI Foundry for article summarization."""
    print("\n" + "=" * 80)
    print("DEMO: Azure AI Foundry Integration")
    print("=" * 80)

    api_key = os.getenv("AZURE_AI_API_KEY")
    endpoint = os.getenv("AZURE_AI_ENDPOINT")
    model = os.getenv("AZURE_AI_MODEL")

    if not api_key or not endpoint or not model:
        missing = [
            v
            for v, val in [
                ("AZURE_AI_API_KEY", api_key),
                ("AZURE_AI_ENDPOINT", endpoint),
                ("AZURE_AI_MODEL", model),
            ]
            if not val
        ]
        print(f"⚠️  Missing environment variable(s): {', '.join(missing)}")
        print("   Using SimpleBarista instead.")
        print("   To use Azure AI Foundry, set:")
        print("     export AZURE_AI_API_KEY='your-key'")
        print(
            "     export AZURE_AI_ENDPOINT='https://my-foundry.services.ai.azure.com/models'"
        )
        print("     export AZURE_AI_MODEL='gpt-4o'")
        provider = SimpleBarista()
    else:
        try:
            print(f"✓ Using Azure AI Foundry — model: {model}")
            provider = AzureAIBarista(api_key=api_key, endpoint=endpoint, model=model)
        except ImportError as e:
            print(f"⚠️  Error: {e}")
            print("   Install with: pip install 'moka-news[azure]'")
            provider = SimpleBarista()
        except ValueError as e:
            print(f"⚠️  Configuration error: {e}")
            provider = SimpleBarista()

    # Process articles
    processed = _brew(provider, sample_articles)

    # Display results
    for i, article in enumerate(processed, 1):
        print(f"\n[{i}] {article['ai_title']}")
        print(f"    {article['ai_summary']}")


def demo_config_file():
    """Demonstrate using a config file with Azure AI Foundry."""
    print("\n" + "=" * 80)
    print("DEMO: Configuration File Usage with Azure AI Foundry")
    print("=" * 80)

    print("""
To use Azure AI Foundry via a configuration file:

1. Create a config file (see conf-example/azure-config.yaml for a full example):

   ai:
     provider: azure
     api_keys:
       azure: your-api-key-here
     azure_endpoint: https://my-foundry.services.ai.azure.com/models
     azure_model: gpt-4o   # or Mistral-Large-3, Llama-3-8B-Instruct, etc.
     azure_api_version: 2024-05-01-preview  # optional; change if your model needs another version

2. Run with the config:
   $ moka-news --config path/to/azure-config.yaml

Or pass --ai azure on the command line to override the provider:
   $ moka-news --ai azure
""")


if __name__ == "__main__":
    # Load environment variables from .env file if present
    load_dotenv()

    print("☕ MoKa News - Azure AI Foundry Integration Example")

    demo_azure()
    demo_config_file()

    print("\n" + "=" * 80)
    print("For more information, see: moka-news --help")
    print("=" * 80 + "\n")
