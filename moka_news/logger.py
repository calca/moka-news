"""
Logging utility for MoKa News
Provides structured logging with emoji support for console output
"""

import logging
import sys
from typing import Optional

# ANSI color codes for terminal output (module-private, immutable)
_COLORS = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[35m",  # Magenta
    "RESET": "\033[0m",  # Reset
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""

    def format(self, record: logging.LogRecord) -> str:
        # Add color to level name
        if hasattr(sys.stderr, "isatty") and sys.stderr.isatty():
            levelname = record.levelname
            if levelname in _COLORS:
                record.levelname = f"{_COLORS[levelname]}{levelname}{_COLORS['RESET']}"
        return super().format(record)


def setup_logger(name: str = "moka_news", level: int = logging.INFO) -> logging.Logger:
    """
    Setup and return a configured logger

    Args:
        name: Logger name (default: "moka_news")
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only add handler if logger doesn't have one already
    if not logger.handlers:
        logger.setLevel(level)

        # Console handler with colored output
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)

        # Format: timestamp - level - message
        formatter = ColoredFormatter(
            fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name (defaults to "moka_news" if None)

    Returns:
        Logger instance
    """
    if name is None:
        name = "moka_news"
    return logging.getLogger(name)
