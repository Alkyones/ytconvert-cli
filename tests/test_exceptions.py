"""
Tests for the exceptions module.
"""

import pytest

from ytconvert.exceptions import (
    ExitCode,
    YTConvertError,
    InvalidURLError,
    DownloadError,
    FormatUnavailableError,
    UnexpectedError,
)


class TestExitCodes:
    """Tests for exit code values."""

    def test_success_code(self):
        """Test SUCCESS exit code is 0."""
        assert ExitCode.SUCCESS == 0

    def test_invalid_url_code(self):
        """Test INVALID_URL exit code is 1."""
        assert ExitCode.INVALID_URL == 1

    def test_download_failure_code(self):
        """Test DOWNLOAD_FAILURE exit code is 2."""
        assert ExitCode.DOWNLOAD_FAILURE == 2

    def test_format_unavailable_code(self):
        """Test FORMAT_UNAVAILABLE exit code is 3."""
        assert ExitCode.FORMAT_UNAVAILABLE == 3

    def test_unexpected_error_code(self):
        """Test UNEXPECTED_ERROR exit code is 4."""
        assert ExitCode.UNEXPECTED_ERROR == 4


class TestInvalidURLError:
    """Tests for InvalidURLError exception."""

    def test_default_message(self):
        """Test default error message."""
        error = InvalidURLError()
        assert "Invalid YouTube URL" in str(error)

    def test_custom_message(self):
        """Test custom error message."""
        error = InvalidURLError("Custom message")
        assert str(error) == "Custom message"

    def test_exit_code(self):
        """Test exit code is set correctly."""
        error = InvalidURLError()
        assert error.exit_code == ExitCode.INVALID_URL


class TestDownloadError:
    """Tests for DownloadError exception."""

    def test_default_message(self):
        """Test default error message."""
        error = DownloadError()
        assert "download" in str(error).lower()

    def test_exit_code(self):
        """Test exit code is set correctly."""
        error = DownloadError()
        assert error.exit_code == ExitCode.DOWNLOAD_FAILURE


class TestFormatUnavailableError:
    """Tests for FormatUnavailableError exception."""

    def test_default_message(self):
        """Test default error message."""
        error = FormatUnavailableError()
        assert "format" in str(error).lower() or "quality" in str(error).lower()

    def test_exit_code(self):
        """Test exit code is set correctly."""
        error = FormatUnavailableError()
        assert error.exit_code == ExitCode.FORMAT_UNAVAILABLE


class TestUnexpectedError:
    """Tests for UnexpectedError exception."""

    def test_default_message(self):
        """Test default error message."""
        error = UnexpectedError()
        assert "unexpected" in str(error).lower()

    def test_exit_code(self):
        """Test exit code is set correctly."""
        error = UnexpectedError()
        assert error.exit_code == ExitCode.UNEXPECTED_ERROR


class TestYTConvertError:
    """Tests for base YTConvertError exception."""

    def test_inheritance(self):
        """Test all custom errors inherit from YTConvertError."""
        assert issubclass(InvalidURLError, YTConvertError)
        assert issubclass(DownloadError, YTConvertError)
        assert issubclass(FormatUnavailableError, YTConvertError)
        assert issubclass(UnexpectedError, YTConvertError)

    def test_custom_exit_code(self):
        """Test custom exit code can be passed."""
        error = YTConvertError("Test", exit_code=99)
        assert error.exit_code == 99
