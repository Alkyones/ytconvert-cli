"""
Utility functions for ytconvert-cli.
"""

import logging
import sys
from pathlib import Path
from typing import Any

# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal styling."""
    
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Set up logging for the CLI application.
    
    Args:
        verbose: If True, set log level to DEBUG; otherwise INFO
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("ytconvert")
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler with formatting
    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


def get_logger() -> logging.Logger:
    """Get the ytconvert logger instance."""
    return logging.getLogger("ytconvert")


def print_success(message: str) -> None:
    """Print a success message in green."""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str) -> None:
    """Print an error message in red."""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}", file=sys.stderr)


def print_warning(message: str) -> None:
    """Print a warning message in yellow."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}", file=sys.stderr)


def print_info(message: str) -> None:
    """Print an info message in blue."""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")


def print_progress(message: str) -> None:
    """Print a progress message in cyan."""
    print(f"{Colors.CYAN}→ {message}{Colors.RESET}")


def ensure_directory(path: Path) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Path to the directory
        
    Returns:
        The resolved absolute path to the directory
    """
    path = Path(path).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_filesize(size_bytes: int | float) -> str:
    """
    Format a file size in bytes to a human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human-readable size string (e.g., "15.5 MB")
    """
    if size_bytes < 0:
        return "Unknown"
    
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} PB"


def format_duration(seconds: int | float) -> str:
    """
    Format a duration in seconds to HH:MM:SS format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 0:
        return "Unknown"
    
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename safe for use on most filesystems
    """
    # Characters not allowed in filenames on Windows
    invalid_chars = '<>:"/\\|?*'
    
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(". ")
    
    # Ensure filename is not empty
    if not filename:
        filename = "untitled"
    
    return filename


def get_quality_height(quality: str) -> int | None:
    """
    Convert a quality string to a height value.
    
    Args:
        quality: Quality string (e.g., "720p", "1080p")
        
    Returns:
        Height in pixels, or None for "best"
    """
    quality_map = {
        "360p": 360,
        "480p": 480,
        "720p": 720,
        "1080p": 1080,
        "1440p": 1440,
        "2160p": 2160,
        "best": None,
    }
    return quality_map.get(quality.lower())
