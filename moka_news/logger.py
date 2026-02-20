"""
Logging utility for MoKa News
Provides structured logging with emoji support for console output
"""

import logging
import sys
from typing import Optional

# ANSI color codes for terminal output (module-private, immutable)
_COLORS = {
    'DEBUG': '\033[36m',    # Cyan
    'INFO': '\033[32m',     # Green
    'WARNING': '\033[33m',  # Yellow
    'ERROR': '\033[31m',    # Red
    'CRITICAL': '\033[35m', # Magenta
    'RESET': '\033[0m'      # Reset
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color support for console output"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Add color to level name
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            levelname = record.levelname
            if levelname in _COLORS:
                record.levelname = f"{_COLORS[levelname]}{levelname}{_COLORS['RESET']}"
        return super().format(record)


def setup_logger(name: str = "moka_news", level: int = logging.INFO, log_file: Optional[str] = None, file_level: Optional[int] = None) -> logging.Logger:
    """
    Setup and return a configured logger
    
    Args:
        name: Logger name (default: "moka_news")
        level: Logging level for the console handler (default: INFO)
        log_file: Optional path to log file
        file_level: Logging level for the file handler (default: same as level).
            Set to logging.DEBUG to always capture verbose output in the file
            while keeping the console less noisy.
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Clear existing handlers only for the specific logger
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()
    
    logger.setLevel(level)
    logger.propagate = False  # Prevent propagation to avoid duplicate logs
    
    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    
    # Format: timestamp - level - message
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        effective_file_level = file_level if file_level is not None else level
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')  # Append mode
        file_handler.setLevel(effective_file_level)
        
        # File format without colors but with more detail
        file_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Force flush to file
        file_handler.flush()
    
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
