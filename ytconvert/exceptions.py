"""
Custom exceptions for ytconvert-cli.

Exit codes:
    0 = success
    1 = invalid URL
    2 = download failure
    3 = format/quality unavailable
    4 = unexpected error
"""

from enum import IntEnum


class ExitCode(IntEnum):
    """Exit codes for the CLI application."""
    
    SUCCESS = 0
    INVALID_URL = 1
    DOWNLOAD_FAILURE = 2
    FORMAT_UNAVAILABLE = 3
    UNEXPECTED_ERROR = 4


class YTConvertError(Exception):
    """Base exception for ytconvert-cli errors."""
    
    exit_code: int = ExitCode.UNEXPECTED_ERROR
    
    def __init__(self, message: str, exit_code: int | None = None):
        super().__init__(message)
        if exit_code is not None:
            self.exit_code = exit_code


class InvalidURLError(YTConvertError):
    """Raised when the provided URL is not a valid YouTube URL."""
    
    exit_code = ExitCode.INVALID_URL
    
    def __init__(self, message: str = "Invalid YouTube URL provided"):
        super().__init__(message, self.exit_code)


class DownloadError(YTConvertError):
    """Raised when the download process fails."""
    
    exit_code = ExitCode.DOWNLOAD_FAILURE
    
    def __init__(self, message: str = "Failed to download video"):
        super().__init__(message, self.exit_code)


class FormatUnavailableError(YTConvertError):
    """Raised when the requested format or quality is not available."""
    
    exit_code = ExitCode.FORMAT_UNAVAILABLE
    
    def __init__(self, message: str = "Requested format or quality unavailable"):
        super().__init__(message, self.exit_code)


class UnexpectedError(YTConvertError):
    """Raised when an unexpected error occurs."""
    
    exit_code = ExitCode.UNEXPECTED_ERROR
    
    def __init__(self, message: str = "An unexpected error occurred"):
        super().__init__(message, self.exit_code)
