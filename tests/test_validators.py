"""
Tests for the validators module.
"""

import pytest

from ytconvert.validators import (
    validate_youtube_url,
    extract_video_id,
    validate_format,
    validate_quality,
    VALID_FORMATS,
    VALID_QUALITIES,
)
from ytconvert.exceptions import InvalidURLError


class TestValidateYouTubeUrl:
    """Tests for validate_youtube_url function."""

    def test_standard_watch_url(self):
        """Test standard YouTube watch URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert validate_youtube_url(url) == url

    def test_short_url(self):
        """Test YouTube short URL (youtu.be)."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert validate_youtube_url(url) == url

    def test_embed_url(self):
        """Test YouTube embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert validate_youtube_url(url) == url

    def test_shorts_url(self):
        """Test YouTube Shorts URL."""
        url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        assert validate_youtube_url(url) == url

    def test_mobile_url(self):
        """Test mobile YouTube URL."""
        url = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        assert validate_youtube_url(url) == url

    def test_no_protocol(self):
        """Test URL without https://."""
        url = "www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert validate_youtube_url(url) == url

    def test_http_protocol(self):
        """Test URL with http:// instead of https://."""
        url = "http://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert validate_youtube_url(url) == url

    def test_invalid_url_raises_error(self):
        """Test that invalid URLs raise InvalidURLError."""
        with pytest.raises(InvalidURLError):
            validate_youtube_url("https://example.com/video")

    def test_empty_url_raises_error(self):
        """Test that empty URLs raise InvalidURLError."""
        with pytest.raises(InvalidURLError):
            validate_youtube_url("")

    def test_vimeo_url_raises_error(self):
        """Test that non-YouTube URLs raise InvalidURLError."""
        with pytest.raises(InvalidURLError):
            validate_youtube_url("https://vimeo.com/123456")


class TestExtractVideoId:
    """Tests for extract_video_id function."""

    def test_standard_url(self):
        """Test extracting ID from standard URL."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url(self):
        """Test extracting ID from short URL."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_embed_url(self):
        """Test extracting ID from embed URL."""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_shorts_url(self):
        """Test extracting ID from Shorts URL."""
        url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_url_with_extra_params(self):
        """Test extracting ID from URL with additional parameters."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120"
        assert extract_video_id(url) == "dQw4w9WgXcQ"


class TestValidateFormat:
    """Tests for validate_format function."""

    def test_mp3_lowercase(self):
        """Test mp3 format validation."""
        assert validate_format("mp3") == "mp3"

    def test_mp4_lowercase(self):
        """Test mp4 format validation."""
        assert validate_format("mp4") == "mp4"

    def test_mp3_uppercase(self):
        """Test MP3 format validation (case insensitive)."""
        assert validate_format("MP3") == "mp3"

    def test_mp4_mixed_case(self):
        """Test Mp4 format validation (case insensitive)."""
        assert validate_format("Mp4") == "mp4"

    def test_invalid_format_raises_error(self):
        """Test that invalid formats raise ValueError."""
        with pytest.raises(ValueError):
            validate_format("avi")


class TestValidateQuality:
    """Tests for validate_quality function."""

    def test_720p(self):
        """Test 720p quality validation."""
        assert validate_quality("720p") == "720p"

    def test_1080p(self):
        """Test 1080p quality validation."""
        assert validate_quality("1080p") == "1080p"

    def test_best(self):
        """Test 'best' quality validation."""
        assert validate_quality("best") == "best"

    def test_uppercase(self):
        """Test quality validation is case insensitive."""
        assert validate_quality("720P") == "720p"

    def test_invalid_quality_raises_error(self):
        """Test that invalid quality raises ValueError."""
        with pytest.raises(ValueError):
            validate_quality("500p")
