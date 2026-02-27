"""
URL and input validation utilities for ytconvert-cli.
"""

import re
from urllib.parse import urlparse, parse_qs

from ytconvert.exceptions import InvalidURLError


# Supported YouTube URL patterns
YOUTUBE_PATTERNS = [
    # Standard watch URLs
    r"^(https?://)?(www\.)?youtube\.com/watch\?.*v=[\w-]+",
    # Short URLs
    r"^(https?://)?(www\.)?youtu\.be/[\w-]+",
    # Embed URLs
    r"^(https?://)?(www\.)?youtube\.com/embed/[\w-]+",
    # Mobile URLs
    r"^(https?://)?(m\.)?youtube\.com/watch\?.*v=[\w-]+",
    # YouTube Shorts
    r"^(https?://)?(www\.)?youtube\.com/shorts/[\w-]+",
    # YouTube Live
    r"^(https?://)?(www\.)?youtube\.com/live/[\w-]+",
]

# Valid output formats
VALID_FORMATS = ["mp3", "mp4"]

# Valid quality options for MP4
VALID_QUALITIES = ["360p", "480p", "720p", "1080p", "1440p", "2160p", "best"]


def validate_youtube_url(url: str) -> str:
    """
    Validate that the provided URL is a valid YouTube URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        The validated URL (normalized if necessary)
        
    Raises:
        InvalidURLError: If the URL is not a valid YouTube URL
    """
    if not url:
        raise InvalidURLError("URL cannot be empty")
    
    url = url.strip()
    
    # Check against known YouTube URL patterns
    for pattern in YOUTUBE_PATTERNS:
        if re.match(pattern, url, re.IGNORECASE):
            return url
    
    raise InvalidURLError(f"Invalid YouTube URL: {url}")


def extract_video_id(url: str) -> str | None:
    """
    Extract the video ID from a YouTube URL.
    
    Args:
        url: A valid YouTube URL
        
    Returns:
        The video ID if found, None otherwise
    """
    # Handle youtu.be short URLs
    if "youtu.be" in url:
        parsed = urlparse(url)
        return parsed.path.lstrip("/").split("?")[0]
    
    # Handle youtube.com/shorts/ URLs
    if "/shorts/" in url:
        match = re.search(r"/shorts/([\w-]+)", url)
        return match.group(1) if match else None
    
    # Handle youtube.com/live/ URLs
    if "/live/" in url:
        match = re.search(r"/live/([\w-]+)", url)
        return match.group(1) if match else None
    
    # Handle youtube.com/embed/ URLs
    if "/embed/" in url:
        match = re.search(r"/embed/([\w-]+)", url)
        return match.group(1) if match else None
    
    # Handle standard watch URLs
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    video_ids = query_params.get("v", [])
    
    return video_ids[0] if video_ids else None


def validate_format(format_type: str) -> str:
    """
    Validate the output format.
    
    Args:
        format_type: The format to validate (mp3 or mp4)
        
    Returns:
        The validated format in lowercase
        
    Raises:
        ValueError: If the format is not valid
    """
    format_lower = format_type.lower()
    if format_lower not in VALID_FORMATS:
        raise ValueError(f"Invalid format '{format_type}'. Must be one of: {', '.join(VALID_FORMATS)}")
    return format_lower


def validate_quality(quality: str) -> str:
    """
    Validate the quality option for MP4.
    
    Args:
        quality: The quality to validate (e.g., 720p, 1080p)
        
    Returns:
        The validated quality string
        
    Raises:
        ValueError: If the quality is not valid
    """
    quality_lower = quality.lower()
    if quality_lower not in VALID_QUALITIES:
        raise ValueError(f"Invalid quality '{quality}'. Must be one of: {', '.join(VALID_QUALITIES)}")
    return quality_lower
