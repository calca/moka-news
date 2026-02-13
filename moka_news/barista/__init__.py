"""
The Barista - AI Agent for Content Processing
Generates titles and summaries using AI APIs (OpenAI/Anthropic)
"""

import os
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
            self.client = openai.OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")
    
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
                    {"role": "system", "content": "You are a news editor creating engaging titles and summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            lines = content.strip().split('\n')
            
            result = {'title': article['title'], 'summary': article['summary'][:200]}
            for line in lines:
                if line.startswith('TITLE:'):
                    result['title'] = line.replace('TITLE:', '').strip()
                elif line.startswith('SUMMARY:'):
                    result['summary'] = line.replace('SUMMARY:', '').strip()
            
            return result
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {'title': article['title'], 'summary': article['summary'][:200]}


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
            self.client = anthropic.Anthropic(api_key=api_key or os.getenv('ANTHROPIC_API_KEY'))
        except ImportError:
            raise ImportError("anthropic package is required. Install with: pip install anthropic")
    
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
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            lines = content.strip().split('\n')
            
            result = {'title': article['title'], 'summary': article['summary'][:200]}
            for line in lines:
                if line.startswith('TITLE:'):
                    result['title'] = line.replace('TITLE:', '').strip()
                elif line.startswith('SUMMARY:'):
                    result['summary'] = line.replace('SUMMARY:', '').strip()
            
            return result
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {'title': article['title'], 'summary': article['summary'][:200]}


class SimpleBarista(AIProvider):
    """Simple non-AI processor for testing without API keys"""
    
    def generate_summary(self, article: Dict[str, Any]) -> Dict[str, str]:
        """Generate a simple summary by truncating the content"""
        return {
            'title': article['title'][:80],
            'summary': article['summary'][:200] if article['summary'] else 'No summary available.'
        }


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
                processed_article['ai_title'] = enhanced['title']
                processed_article['ai_summary'] = enhanced['summary']
                processed.append(processed_article)
            except Exception as e:
                print(f"Error processing article: {e}")
                article['ai_title'] = article['title']
                article['ai_summary'] = article['summary'][:200]
                processed.append(article)
        
        return processed
