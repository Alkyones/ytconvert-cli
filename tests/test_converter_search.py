"""Tests for YouTube search parsing behavior in the converter."""

from ytconvert.converter import YouTubeConverter


class TestParseSearchResults:
    """Tests for YouTubeConverter.parse_search_results."""

    def test_normalizes_search_entries(self):
        entries = [
            {
                "id": "abc123",
                "title": "Lofi Hip Hop Radio",
                "uploader": "Lofi Girl",
                "duration": 11520,
            },
            {
                "id": "def456",
                "title": "Chill Mix",
                "channel": "Chill Channel",
                "duration": 3600,
            },
        ]

        results = YouTubeConverter.parse_search_results(entries)

        assert len(results) == 2
        assert results[0]["title"] == "Lofi Hip Hop Radio"
        assert results[0]["uploader"] == "Lofi Girl"
        assert results[0]["duration"] == 11520
        assert results[0]["url"] == "https://www.youtube.com/watch?v=abc123"

        assert results[1]["title"] == "Chill Mix"
        assert results[1]["uploader"] == "Chill Channel"
        assert results[1]["url"] == "https://www.youtube.com/watch?v=def456"

    def test_skips_entries_without_id_or_url(self):
        entries = [
            {"title": "Missing URL metadata"},
            {"id": "ghi789", "title": "Valid Entry", "uploader": "Uploader"},
        ]

        results = YouTubeConverter.parse_search_results(entries)

        assert len(results) == 1
        assert results[0]["title"] == "Valid Entry"
        assert results[0]["url"] == "https://www.youtube.com/watch?v=ghi789"
