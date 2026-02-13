"""
OPML Manager - Manages RSS feeds in OPML format
Handles loading, saving, adding, and removing RSS feed URLs
"""

import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Dict, Optional
from pathlib import Path


class OPMLManager:
    """Manages RSS feeds stored in OPML format"""

    DEFAULT_OPML_PATH = os.path.expanduser("~/.config/moka-news/feeds.opml")

    def __init__(self, opml_path: Optional[str] = None):
        """
        Initialize OPML manager

        Args:
            opml_path: Path to OPML file (default: ~/.config/moka-news/feeds.opml)
        """
        self.opml_path = opml_path or self.DEFAULT_OPML_PATH
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Ensure the config directory exists"""
        config_dir = os.path.dirname(self.opml_path)
        Path(config_dir).mkdir(parents=True, exist_ok=True)

    def _get_rfc822_date(self) -> str:
        """Get current date in RFC 822 format"""
        return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    def _create_default_opml(self) -> ET.Element:
        """
        Create a default OPML structure

        Returns:
            Root OPML element
        """
        opml = ET.Element("opml", version="2.0")

        # Create head section
        head = ET.SubElement(opml, "head")
        title = ET.SubElement(head, "title")
        title.text = "MoKa News Feeds"
        date_created = ET.SubElement(head, "dateCreated")
        date_created.text = self._get_rfc822_date()
        date_modified = ET.SubElement(head, "dateModified")
        date_modified.text = self._get_rfc822_date()

        # Create body section
        ET.SubElement(opml, "body")

        return opml

    def load_feeds(self) -> List[str]:
        """
        Load RSS feed URLs from OPML file

        Returns:
            List of RSS feed URLs
        """
        if not os.path.exists(self.opml_path):
            return []

        try:
            tree = ET.parse(self.opml_path)
            root = tree.getroot()

            feeds = []
            # Find all outline elements with type="rss" and xmlUrl attribute
            for outline in root.findall('.//outline[@type="rss"][@xmlUrl]'):
                xml_url = outline.get("xmlUrl")
                if xml_url:
                    feeds.append(xml_url)

            return feeds
        except ET.ParseError as e:
            print(f"Error parsing OPML file '{self.opml_path}': {e}")
            print("The file may be corrupted. Try removing it and adding feeds again.")
            return []
        except PermissionError:
            print(f"Permission denied reading OPML file: {self.opml_path}")
            return []
        except Exception as e:
            print(f"Unexpected error loading OPML file '{self.opml_path}': {e}")
            return []

    def save_feeds(self, feeds: List[Dict[str, str]]):
        """
        Save RSS feeds to OPML file

        Args:
            feeds: List of feed dictionaries with 'url' and optional 'title', 'htmlUrl'
        """
        opml = self._create_default_opml()
        body = opml.find("body")

        # Add each feed as an outline element
        for feed in feeds:
            outline = ET.SubElement(body, "outline")
            outline.set("type", "rss")
            outline.set("text", feed.get("title", feed["url"]))
            outline.set("xmlUrl", feed["url"])
            if "htmlUrl" in feed:
                outline.set("htmlUrl", feed["htmlUrl"])

        # Update dateModified
        date_modified = opml.find(".//dateModified")
        if date_modified is not None:
            date_modified.text = self._get_rfc822_date()

        # Write to file with proper XML declaration
        tree = ET.ElementTree(opml)
        # Pretty print for Python 3.9+, otherwise write as-is
        try:
            ET.indent(tree, space="  ")
        except AttributeError:
            pass  # ET.indent not available in Python < 3.9
        tree.write(self.opml_path, encoding="utf-8", xml_declaration=True)

    def add_feed(
        self, url: str, title: Optional[str] = None, html_url: Optional[str] = None
    ) -> bool:
        """
        Add a new RSS feed

        Args:
            url: RSS feed URL
            title: Optional feed title
            html_url: Optional website URL

        Returns:
            True if feed was added, False if it already exists
        """
        existing_feeds = self.load_feeds()

        # Check if feed already exists
        if url in existing_feeds:
            return False

        # Load existing feed data or create new list
        feeds_data = self._load_feeds_with_metadata()

        # Add new feed
        new_feed = {"url": url}
        if title:
            new_feed["title"] = title
        if html_url:
            new_feed["htmlUrl"] = html_url

        feeds_data.append(new_feed)

        # Save updated feeds
        self.save_feeds(feeds_data)
        return True

    def remove_feed(self, url: str) -> bool:
        """
        Remove an RSS feed

        Args:
            url: RSS feed URL to remove

        Returns:
            True if feed was removed, False if it wasn't found
        """
        feeds_data = self._load_feeds_with_metadata()

        # Find and remove the feed
        original_count = len(feeds_data)
        feeds_data = [f for f in feeds_data if f["url"] != url]

        if len(feeds_data) == original_count:
            return False

        # Save updated feeds
        self.save_feeds(feeds_data)
        return True

    def _load_feeds_with_metadata(self) -> List[Dict[str, str]]:
        """
        Load feeds with all metadata from OPML file

        Returns:
            List of feed dictionaries with url, title, and optional htmlUrl
        """
        if not os.path.exists(self.opml_path):
            return []

        try:
            tree = ET.parse(self.opml_path)
            root = tree.getroot()

            feeds = []
            for outline in root.findall('.//outline[@type="rss"][@xmlUrl]'):
                feed = {
                    "url": outline.get("xmlUrl"),
                    "title": outline.get("text", outline.get("xmlUrl")),
                }
                html_url = outline.get("htmlUrl")
                if html_url:
                    feed["htmlUrl"] = html_url
                feeds.append(feed)

            return feeds
        except ET.ParseError as e:
            print(f"Error parsing OPML file '{self.opml_path}': {e}")
            print("The file may be corrupted. Try removing it and adding feeds again.")
            return []
        except PermissionError:
            print(f"Permission denied reading OPML file: {self.opml_path}")
            return []
        except Exception as e:
            print(f"Unexpected error loading OPML file '{self.opml_path}': {e}")
            return []

    def list_feeds(self) -> List[Dict[str, str]]:
        """
        List all RSS feeds with metadata

        Returns:
            List of feed dictionaries
        """
        return self._load_feeds_with_metadata()
