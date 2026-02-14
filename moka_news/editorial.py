"""
Editorial Generator - Creates AI-powered morning news editorials
Combines multiple articles into a single coherent editorial with source links
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from moka_news.barista import AIProvider


class EditorialGenerator:
    """Generates AI-powered editorials from news articles"""
    
    def __init__(
        self,
        ai_provider: AIProvider,
        keywords: Optional[List[str]] = None,
        editorials_dir: Optional[Path] = None
    ):
        """
        Initialize the Editorial Generator
        
        Args:
            ai_provider: AI provider instance for generating editorial content
            keywords: Optional list of keywords to focus the editorial on
            editorials_dir: Directory to save editorials (defaults to ~/.config/moka-news/editorials)
        """
        self.ai_provider = ai_provider
        self.keywords = keywords or []
        
        # Set editorials directory
        if editorials_dir:
            self.editorials_dir = Path(editorials_dir)
        else:
            config_dir = Path.home() / ".config" / "moka-news"
            self.editorials_dir = config_dir / "editorials"
        
        # Create editorials directory if it doesn't exist
        self.editorials_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_editorial(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate an editorial from a list of articles
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Dictionary containing the editorial content and metadata
        """
        if not articles:
            return {
                "title": "Good Morning!",
                "content": "No news articles available today.",
                "timestamp": datetime.now(),
                "sources": []
            }
        
        # Build editorial prompt
        prompt = self._build_editorial_prompt(articles)
        
        # Create a pseudo-article for the AI provider
        editorial_article = {
            "title": "Morning Editorial",
            "summary": prompt
        }
        
        # Generate editorial content using AI
        try:
            result = self.ai_provider.generate_summary(
                editorial_article,
                keywords=self.keywords,
                prompts=self._get_editorial_prompts()
            )
            
            editorial_content = result.get("summary", "")
            editorial_title = result.get("title", "Your Morning News")
            
        except Exception as e:
            print(f"Error generating editorial with AI: {e}")
            editorial_title = "Your Morning News"
            editorial_content = self._create_simple_editorial(articles)
        
        # Collect sources
        sources = []
        for article in articles:
            sources.append({
                "title": article.get("ai_title", article.get("title", "Untitled")),
                "url": article.get("link", ""),
                "source": article.get("source", "Unknown")
            })
        
        return {
            "title": editorial_title,
            "content": editorial_content,
            "timestamp": datetime.now(),
            "sources": sources,
            "article_count": len(articles)
        }
    
    def _build_editorial_prompt(self, articles: List[Dict[str, Any]]) -> str:
        """
        Build a prompt for editorial generation
        
        Args:
            articles: List of articles to include in the editorial
            
        Returns:
            Formatted prompt string
        """
        # Limit to most recent/important articles
        selected_articles = articles[:10]  # Take up to 10 articles
        
        articles_text = ""
        for i, article in enumerate(selected_articles, 1):
            title = article.get("ai_title", article.get("title", ""))
            summary = article.get("ai_summary", article.get("summary", ""))[:200]
            source = article.get("source", "Unknown")
            
            articles_text += f"{i}. {title}\n"
            articles_text += f"   Source: {source}\n"
            articles_text += f"   {summary}\n\n"
        
        return articles_text
    
    def _get_editorial_prompts(self) -> Dict[str, str]:
        """
        Get custom prompts for editorial generation
        
        Returns:
            Dictionary of custom prompts for editorial generation
        """
        prompts = {
            "system_message": "You are a skilled news editor creating an engaging morning editorial.",
            "user_prompt": """Create a cohesive morning news editorial from these articles:

{content}

Write an engaging editorial that:
1. Highlights the most important and relevant news
2. Connects related topics into a coherent narrative
3. Is enjoyable to read over morning coffee
4. Is approximately 300-500 words

Focus on creating a pleasant reading experience.""",
            "keywords_section": """

Pay special attention to topics related to: {keywords}""",
            "format_section": """

Format as:
TITLE: <engaging editorial title>
SUMMARY: <the editorial content>"""
        }
        
        return prompts
    
    def _create_simple_editorial(self, articles: List[Dict[str, Any]]) -> str:
        """
        Create a simple editorial without AI (fallback)
        
        Args:
            articles: List of articles
            
        Returns:
            Simple editorial text
        """
        content = "## Your Morning News Digest\n\n"
        content += f"Here are the top stories from {len(articles)} articles:\n\n"
        
        for i, article in enumerate(articles[:5], 1):
            title = article.get("ai_title", article.get("title", "Untitled"))
            summary = article.get("ai_summary", article.get("summary", ""))[:150]
            content += f"**{i}. {title}**\n{summary}\n\n"
        
        return content
    
    def save_editorial(self, editorial: Dict[str, Any]) -> Path:
        """
        Save editorial to markdown file
        
        Args:
            editorial: Editorial dictionary from generate_editorial()
            
        Returns:
            Path to saved editorial file
        """
        timestamp = editorial["timestamp"]
        filename = timestamp.strftime("%Y-%m-%d_%H-%M.md")
        filepath = self.editorials_dir / filename
        
        # Format editorial as markdown
        markdown = self._format_editorial_markdown(editorial)
        
        # Save to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown)
        
        return filepath
    
    def _format_editorial_markdown(self, editorial: Dict[str, Any]) -> str:
        """
        Format editorial as markdown
        
        Args:
            editorial: Editorial dictionary
            
        Returns:
            Formatted markdown string
        """
        timestamp = editorial["timestamp"]
        date_str = timestamp.strftime("%A, %B %d, %Y at %H:%M")
        
        md = f"# {editorial['title']}\n\n"
        md += f"*{date_str}*\n\n"
        md += "---\n\n"
        md += editorial['content']
        md += "\n\n---\n\n"
        md += "## Sources\n\n"
        
        for source in editorial['sources']:
            title = source['title']
            url = source['url']
            source_name = source['source']
            if url:
                md += f"- **{title}** - *{source_name}*  \n  [{url}]({url})\n\n"
            else:
                md += f"- **{title}** - *{source_name}*\n\n"
        
        md += f"\n*Editorial generated from {editorial['article_count']} articles*\n"
        
        return md
    
    def list_editorials(self) -> List[Dict[str, Any]]:
        """
        List all saved editorials
        
        Returns:
            List of editorial metadata dictionaries
        """
        editorials = []
        
        if not self.editorials_dir.exists():
            return editorials
        
        for filepath in sorted(self.editorials_dir.glob("*.md"), reverse=True):
            try:
                # Parse filename to get timestamp
                filename = filepath.stem
                timestamp = datetime.strptime(filename, "%Y-%m-%d_%H-%M")
                
                # Read first line as title
                with open(filepath, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    title = first_line.replace("# ", "") if first_line.startswith("# ") else "Untitled"
                
                editorials.append({
                    "title": title,
                    "timestamp": timestamp,
                    "filepath": filepath,
                    "filename": filepath.name
                })
            except Exception as e:
                print(f"Error reading editorial {filepath}: {e}")
        
        return editorials
    
    def load_editorial(self, filepath: Path) -> str:
        """
        Load an editorial from file
        
        Args:
            filepath: Path to editorial markdown file
            
        Returns:
            Editorial content as markdown string
        """
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
