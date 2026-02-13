"""
The Barista - AI Agent for Content Processing
Generates titles and summaries using AI APIs (OpenAI/Anthropic)
"""

import os
import subprocess
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    def generate_summary(self, article: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate a summary and improved title for an article

        Args:
            article: Article dictionary with title, link, summary

        Returns:
            Dictionary with 'title' and 'summary' keys
        """
        pass


class OpenAIBarista(AIProvider):
    """OpenAI-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI provider

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        try:
            import openai

            self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )

    def generate_summary(self, article: Dict[str, Any]) -> Dict[str, str]:
        """Generate summary using OpenAI"""
        try:
            prompt = f"""Given this article:
Title: {article['title']}
Content: {article['summary'][:500]}

Generate:
1. A concise, engaging title (max 80 characters)
2. A brief summary (max 200 characters)

Format as:
TITLE: <title>
SUMMARY: <summary>"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a news editor creating engaging titles and summaries.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.7,
            )

            content = response.choices[0].message.content
            lines = content.strip().split("\n")

            result = {"title": article["title"], "summary": article["summary"][:200]}
            for line in lines:
                if line.startswith("TITLE:"):
                    result["title"] = line.replace("TITLE:", "").strip()
                elif line.startswith("SUMMARY:"):
                    result["summary"] = line.replace("SUMMARY:", "").strip()

            return result
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {"title": article["title"], "summary": article["summary"][:200]}


class AnthropicBarista(AIProvider):
    """Anthropic-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Anthropic provider

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        try:
            import anthropic

            self.client = anthropic.Anthropic(
                api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
            )
        except ImportError:
            raise ImportError(
                "anthropic package is required. Install with: pip install anthropic"
            )

    def generate_summary(self, article: Dict[str, Any]) -> Dict[str, str]:
        """Generate summary using Anthropic"""
        try:
            prompt = f"""Given this article:
Title: {article['title']}
Content: {article['summary'][:500]}

Generate:
1. A concise, engaging title (max 80 characters)
2. A brief summary (max 200 characters)

Format as:
TITLE: <title>
SUMMARY: <summary>"""

            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}],
            )

            content = response.content[0].text
            lines = content.strip().split("\n")

            result = {"title": article["title"], "summary": article["summary"][:200]}
            for line in lines:
                if line.startswith("TITLE:"):
                    result["title"] = line.replace("TITLE:", "").strip()
                elif line.startswith("SUMMARY:"):
                    result["summary"] = line.replace("SUMMARY:", "").strip()

            return result
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {"title": article["title"], "summary": article["summary"][:200]}


class GeminiBarista(AIProvider):
    """Google Gemini-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini provider

        Args:
            api_key: Google API key (defaults to GEMINI_API_KEY env var)
        """
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel("gemini-pro")
        except ImportError:
            raise ImportError(
                "google-generativeai package is required. Install with: pip install google-generativeai"
            )

    def generate_summary(self, article: Dict[str, Any]) -> Dict[str, str]:
        """Generate summary using Google Gemini"""
        try:
            prompt = f"""Given this article:
Title: {article['title']}
Content: {article['summary'][:500]}

Generate:
1. A concise, engaging title (max 80 characters)
2. A brief summary (max 200 characters)

Format as:
TITLE: <title>
SUMMARY: <summary>"""

            response = self.model.generate_content(prompt)
            content = response.text
            lines = content.strip().split("\n")

            result = {"title": article["title"], "summary": article["summary"][:200]}
            for line in lines:
                if line.startswith("TITLE:"):
                    result["title"] = line.replace("TITLE:", "").strip()
                elif line.startswith("SUMMARY:"):
                    result["summary"] = line.replace("SUMMARY:", "").strip()

            return result
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {"title": article["title"], "summary": article["summary"][:200]}


class MistralBarista(AIProvider):
    """Mistral AI-based content processor"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Mistral provider

        Args:
            api_key: Mistral API key (defaults to MISTRAL_API_KEY env var)
        """
        try:
            from mistralai.client import MistralClient

            self.client = MistralClient(api_key=api_key or os.getenv("MISTRAL_API_KEY"))
        except ImportError:
            raise ImportError(
                "mistralai package is required. Install with: pip install mistralai"
            )

    def generate_summary(self, article: Dict[str, Any]) -> Dict[str, str]:
        """Generate summary using Mistral AI"""
        try:
            prompt = f"""Given this article:
Title: {article['title']}
Content: {article['summary'][:500]}

Generate:
1. A concise, engaging title (max 80 characters)
2. A brief summary (max 200 characters)

Format as:
TITLE: <title>
SUMMARY: <summary>"""

            response = self.client.chat(
                model="mistral-tiny",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7,
            )

            content = response.choices[0].message.content
            lines = content.strip().split("\n")

            result = {"title": article["title"], "summary": article["summary"][:200]}
            for line in lines:
                if line.startswith("TITLE:"):
                    result["title"] = line.replace("TITLE:", "").strip()
                elif line.startswith("SUMMARY:"):
                    result["summary"] = line.replace("SUMMARY:", "").strip()

            return result
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {"title": article["title"], "summary": article["summary"][:200]}


class SimpleBarista(AIProvider):
    """Simple non-AI processor for testing without API keys"""

    def generate_summary(self, article: Dict[str, Any]) -> Dict[str, str]:
        """Generate a simple summary by truncating the content"""
        return {
            "title": article.get("title", "No Title")[:80],
            "summary": (
                article.get("summary", "No summary available.")[:200]
                if article.get("summary")
                else "No summary available."
            ),
        }


class GitHubCopilotCLIBarista(AIProvider):
    """GitHub Copilot CLI-based content processor"""

    def __init__(self):
        """Initialize GitHub Copilot CLI provider"""
        # Check if gh CLI is available
        try:
            result = subprocess.run(
                ["gh", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                raise RuntimeError("GitHub CLI (gh) is not available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            raise RuntimeError(
                "GitHub CLI (gh) is not installed. Install from: https://cli.github.com/"
            )

    def generate_summary(self, article: Dict[str, Any]) -> Dict[str, str]:
        """Generate summary using GitHub Copilot CLI"""
        try:
            prompt = f"""Given this article:
Title: {article['title']}
Content: {article['summary'][:500]}

Generate:
1. A concise, engaging title (max 80 characters)
2. A brief summary (max 200 characters)

Format your response EXACTLY as:
TITLE: <title>
SUMMARY: <summary>"""

            # Run gh copilot with the prompt
            result = subprocess.run(
                [
                    "gh",
                    "copilot",
                    "-p",
                    prompt,
                    "--allow-all-tools",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise RuntimeError(f"GitHub Copilot CLI error: {result.stderr}")

            content = result.stdout
            lines = content.strip().split("\n")

            result_dict = {
                "title": article["title"],
                "summary": article["summary"][:200],
            }
            for line in lines:
                if line.startswith("TITLE:"):
                    result_dict["title"] = line.replace("TITLE:", "").strip()
                elif line.startswith("SUMMARY:"):
                    result_dict["summary"] = line.replace("SUMMARY:", "").strip()

            return result_dict
        except subprocess.TimeoutExpired:
            print("GitHub Copilot CLI timeout")
            return {"title": article["title"], "summary": article["summary"][:200]}
        except Exception as e:
            print(f"Error generating summary with GitHub Copilot CLI: {e}")
            return {"title": article["title"], "summary": article["summary"][:200]}


class GeminiCLIBarista(AIProvider):
    """Gemini CLI-based content processor using gcloud"""

    def __init__(self):
        """Initialize Gemini CLI provider"""
        # Check if gcloud CLI is available
        try:
            result = subprocess.run(
                ["gcloud", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                raise RuntimeError("gcloud CLI is not available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            raise RuntimeError(
                "gcloud CLI is not installed. Install from: https://cloud.google.com/sdk/docs/install"
            )

    def generate_summary(self, article: Dict[str, Any]) -> Dict[str, str]:
        """Generate summary using gcloud CLI with Gemini"""
        try:
            prompt = f"""Given this article:
Title: {article['title']}
Content: {article['summary'][:500]}

Generate:
1. A concise, engaging title (max 80 characters)
2. A brief summary (max 200 characters)

Format as:
TITLE: <title>
SUMMARY: <summary>"""

            # Run gcloud with Gemini
            result = subprocess.run(
                [
                    "gcloud",
                    "ai",
                    "models",
                    "generate-content",
                    "--model=gemini-pro",
                    f"--prompt={prompt}",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Gemini CLI error: {result.stderr}")

            content = result.stdout
            lines = content.strip().split("\n")

            result_dict = {
                "title": article["title"],
                "summary": article["summary"][:200],
            }
            for line in lines:
                if line.startswith("TITLE:"):
                    result_dict["title"] = line.replace("TITLE:", "").strip()
                elif line.startswith("SUMMARY:"):
                    result_dict["summary"] = line.replace("SUMMARY:", "").strip()

            return result_dict
        except subprocess.TimeoutExpired:
            print("Gemini CLI timeout")
            return {"title": article["title"], "summary": article["summary"][:200]}
        except Exception as e:
            print(f"Error generating summary with Gemini CLI: {e}")
            return {"title": article["title"], "summary": article["summary"][:200]}


class MistralCLIBarista(AIProvider):
    """Mistral CLI-based content processor"""

    def __init__(self):
        """Initialize Mistral CLI provider"""
        # Check if mistral CLI is available
        try:
            result = subprocess.run(
                ["mistral", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                raise RuntimeError("Mistral CLI is not available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            raise RuntimeError(
                "Mistral CLI is not installed. Install with: pip install mistralai-cli or from: https://docs.mistral.ai/cli/"
            )

    def generate_summary(self, article: Dict[str, Any]) -> Dict[str, str]:
        """Generate summary using Mistral CLI"""
        try:
            prompt = f"""Given this article:
Title: {article['title']}
Content: {article['summary'][:500]}

Generate:
1. A concise, engaging title (max 80 characters)
2. A brief summary (max 200 characters)

Format as:
TITLE: <title>
SUMMARY: <summary>"""

            # Run mistral CLI
            result = subprocess.run(
                [
                    "mistral",
                    "chat",
                    "--model",
                    "mistral-tiny",
                    "--message",
                    prompt,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Mistral CLI error: {result.stderr}")

            content = result.stdout
            lines = content.strip().split("\n")

            result_dict = {
                "title": article["title"],
                "summary": article["summary"][:200],
            }
            for line in lines:
                if line.startswith("TITLE:"):
                    result_dict["title"] = line.replace("TITLE:", "").strip()
                elif line.startswith("SUMMARY:"):
                    result_dict["summary"] = line.replace("SUMMARY:", "").strip()

            return result_dict
        except subprocess.TimeoutExpired:
            print("Mistral CLI timeout")
            return {"title": article["title"], "summary": article["summary"][:200]}
        except Exception as e:
            print(f"Error generating summary with Mistral CLI: {e}")
            return {"title": article["title"], "summary": article["summary"][:200]}


class Barista:
    """Main Barista class that coordinates AI processing"""

    def __init__(self, provider: Optional[AIProvider] = None):
        """
        Initialize the Barista with an AI provider

        Args:
            provider: AI provider instance (defaults to SimpleBarista)
        """
        self.provider = provider or SimpleBarista()

    def brew(self, articles: list) -> list:
        """
        Process a list of articles through the AI provider

        Args:
            articles: List of article dictionaries

        Returns:
            List of processed articles with enhanced titles and summaries
        """
        processed = []

        for article in articles:
            try:
                enhanced = self.provider.generate_summary(article)
                processed_article = article.copy()
                processed_article["ai_title"] = enhanced["title"]
                processed_article["ai_summary"] = enhanced["summary"]
                processed.append(processed_article)
            except Exception as e:
                print(f"Error processing article: {e}")
                article["ai_title"] = article["title"]
                article["ai_summary"] = article["summary"][:200]
                processed.append(article)

        return processed
