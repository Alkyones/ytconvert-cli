"""
ytconvert-cli: A YouTube video converter CLI tool.

Convert YouTube videos to MP3 or MP4 using yt-dlp.
"""

__version__ = "1.1.0"
__author__ = "ytconvert-cli"

from ytconvert.converter import YouTubeConverter
from ytconvert.exceptions import (
    YTConvertError,
    InvalidURLError,
    DownloadError,
    FormatUnavailableError,
    UnexpectedError,
)

__all__ = [
    "YouTubeConverter",
    "YTConvertError",
    "InvalidURLError",
    "DownloadError",
    "FormatUnavailableError",
    "UnexpectedError",
    "__version__",
]
