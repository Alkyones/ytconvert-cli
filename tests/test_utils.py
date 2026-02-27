"""
Tests for the utils module.
"""

import pytest
from pathlib import Path
import tempfile
import os

from ytconvert.utils import (
    format_filesize,
    format_duration,
    sanitize_filename,
    get_quality_height,
    ensure_directory,
)


class TestFormatFilesize:
    """Tests for format_filesize function."""

    def test_bytes(self):
        """Test formatting bytes."""
        assert format_filesize(500) == "500.0 B"

    def test_kilobytes(self):
        """Test formatting kilobytes."""
        assert format_filesize(1024) == "1.0 KB"

    def test_megabytes(self):
        """Test formatting megabytes."""
        assert format_filesize(1024 * 1024) == "1.0 MB"

    def test_gigabytes(self):
        """Test formatting gigabytes."""
        assert format_filesize(1024 * 1024 * 1024) == "1.0 GB"

    def test_negative_returns_unknown(self):
        """Test negative values return 'Unknown'."""
        assert format_filesize(-1) == "Unknown"

    def test_decimal_values(self):
        """Test decimal formatting."""
        result = format_filesize(1536)  # 1.5 KB
        assert "KB" in result


class TestFormatDuration:
    """Tests for format_duration function."""

    def test_seconds_only(self):
        """Test formatting seconds."""
        assert format_duration(45) == "0:45"

    def test_minutes_and_seconds(self):
        """Test formatting minutes and seconds."""
        assert format_duration(125) == "2:05"

    def test_hours(self):
        """Test formatting hours."""
        assert format_duration(3665) == "1:01:05"

    def test_negative_returns_unknown(self):
        """Test negative values return 'Unknown'."""
        assert format_duration(-1) == "Unknown"

    def test_zero(self):
        """Test zero duration."""
        assert format_duration(0) == "0:00"


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_removes_invalid_chars(self):
        """Test removal of invalid characters."""
        result = sanitize_filename('test<>:"/\\|?*file')
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert '"' not in result
        assert "/" not in result
        assert "\\" not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result

    def test_strips_dots_and_spaces(self):
        """Test stripping leading/trailing dots and spaces."""
        result = sanitize_filename("  ..test.. ")
        assert not result.startswith(".")
        assert not result.startswith(" ")
        assert not result.endswith(".")
        assert not result.endswith(" ")

    def test_empty_becomes_untitled(self):
        """Test empty filename becomes 'untitled'."""
        result = sanitize_filename("")
        assert result == "untitled"

    def test_preserves_valid_chars(self):
        """Test valid characters are preserved."""
        result = sanitize_filename("test-file_name (123)")
        assert "test" in result
        assert "file" in result
        assert "name" in result


class TestGetQualityHeight:
    """Tests for get_quality_height function."""

    def test_360p(self):
        """Test 360p returns 360."""
        assert get_quality_height("360p") == 360

    def test_720p(self):
        """Test 720p returns 720."""
        assert get_quality_height("720p") == 720

    def test_1080p(self):
        """Test 1080p returns 1080."""
        assert get_quality_height("1080p") == 1080

    def test_2160p(self):
        """Test 2160p (4K) returns 2160."""
        assert get_quality_height("2160p") == 2160

    def test_best_returns_none(self):
        """Test 'best' returns None."""
        assert get_quality_height("best") is None

    def test_case_insensitive(self):
        """Test quality parsing is case insensitive."""
        assert get_quality_height("720P") == 720


class TestEnsureDirectory:
    """Tests for ensure_directory function."""

    def test_creates_directory(self):
        """Test directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "new" / "nested" / "dir"
            result = ensure_directory(new_dir)
            assert result.exists()
            assert result.is_dir()

    def test_existing_directory(self):
        """Test existing directory is handled correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ensure_directory(tmpdir)
            assert result.exists()
            assert result.is_dir()

    def test_returns_resolved_path(self):
        """Test returned path is absolute."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ensure_directory(tmpdir)
            assert result.is_absolute()
