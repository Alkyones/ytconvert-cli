"""Tests for CLI behavior."""

from pathlib import Path

from typer.testing import CliRunner

from ytconvert.cli import app
from ytconvert.exceptions import ExitCode

runner = CliRunner()


def test_root_help_includes_search_command():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "search" in result.output
    assert "Search YouTube and download a selected result" in result.output


def test_search_help_shows_expected_options():
    result = runner.invoke(app, ["search", "--help"])

    assert result.exit_code == 0
    assert "--limit" in result.output
    assert "--audio" in result.output
    assert "--video" in result.output


def test_search_without_query_shows_helpful_error():
    result = runner.invoke(app, ["search"])

    assert result.exit_code == ExitCode.INVALID_URL
    assert "Please provide a search query" in result.output


def test_search_invalid_selection_handled(monkeypatch):
    def fake_search_videos(self, search_query: str, limit: int):
        return [
            {
                "title": "Lofi Hip Hop Radio",
                "uploader": "Lofi Girl",
                "duration": 3600,
                "url": "https://www.youtube.com/watch?v=abc123",
            }
        ]

    monkeypatch.setattr("ytconvert.converter.YouTubeConverter.search_videos", fake_search_videos)
    monkeypatch.setattr("ytconvert.cli.typer.prompt", lambda _label: "9")

    result = runner.invoke(app, ["search", "lofi hip hop"])

    assert result.exit_code == ExitCode.INVALID_URL
    assert "Invalid selection" in result.output


def test_search_parses_limit_and_video_flag(monkeypatch, tmp_path: Path):
    calls: dict[str, object] = {}

    def fake_search_videos(self, search_query: str, limit: int):
        calls["query"] = search_query
        calls["limit"] = limit
        return [
            {
                "title": "Chill Mix",
                "uploader": "Channel",
                "duration": 90,
                "url": "https://www.youtube.com/watch?v=def456",
            }
        ]

    def fake_convert(self, url: str, format_type: str, quality: str = "best"):
        calls["url"] = url
        calls["format_type"] = format_type
        calls["quality"] = quality
        return tmp_path / "chill-mix.mp4"

    monkeypatch.setattr("ytconvert.converter.YouTubeConverter.search_videos", fake_search_videos)
    monkeypatch.setattr("ytconvert.converter.YouTubeConverter.convert", fake_convert)
    monkeypatch.setattr("ytconvert.cli.typer.prompt", lambda _label: "1")

    result = runner.invoke(app, ["search", "chill beats", "--limit", "5", "--video"])

    assert result.exit_code == ExitCode.SUCCESS
    assert calls["query"] == "chill beats"
    assert calls["limit"] == 5
    assert calls["format_type"] == "mp4"
