"""Tests for the batch download command."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ytconvert.cli import _parse_urls_from_file, app
from ytconvert.exceptions import ExitCode

runner = CliRunner()

VALID_URL_1 = "https://www.youtube.com/watch?v=abc123def45"
VALID_URL_2 = "https://www.youtube.com/watch?v=xyz789ghi01"
VALID_URL_3 = "https://youtu.be/abc12345678a"


class TestParseUrlsFromFile:
    def test_returns_valid_urls(self, tmp_path: Path) -> None:
        url_file = tmp_path / "urls.txt"
        url_file.write_text(f"{VALID_URL_1}\n{VALID_URL_2}\n")

        result = _parse_urls_from_file(url_file)

        assert result == [VALID_URL_1, VALID_URL_2]

    def test_skips_empty_lines(self, tmp_path: Path) -> None:
        url_file = tmp_path / "urls.txt"
        url_file.write_text(f"{VALID_URL_1}\n\n   \n{VALID_URL_2}\n")

        result = _parse_urls_from_file(url_file)

        assert result == [VALID_URL_1, VALID_URL_2]

    def test_skips_invalid_urls(self, tmp_path: Path) -> None:
        url_file = tmp_path / "urls.txt"
        url_file.write_text(f"{VALID_URL_1}\nnot-a-url\n{VALID_URL_2}\n")

        result = _parse_urls_from_file(url_file)

        assert result == [VALID_URL_1, VALID_URL_2]

    def test_empty_file_returns_empty_list(self, tmp_path: Path) -> None:
        url_file = tmp_path / "urls.txt"
        url_file.write_text("")

        result = _parse_urls_from_file(url_file)

        assert result == []

    def test_file_not_found_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            _parse_urls_from_file(tmp_path / "nonexistent.txt")

    def test_strips_whitespace_from_urls(self, tmp_path: Path) -> None:
        url_file = tmp_path / "urls.txt"
        url_file.write_text(f"  {VALID_URL_1}  \n  {VALID_URL_2}  \n")

        result = _parse_urls_from_file(url_file)

        assert result == [VALID_URL_1, VALID_URL_2]

    def test_all_invalid_lines_returns_empty_list(self, tmp_path: Path) -> None:
        url_file = tmp_path / "urls.txt"
        url_file.write_text("not-a-url\nanother-bad-line\n")

        result = _parse_urls_from_file(url_file)

        assert result == []


class TestBatchCommand:
    def test_batch_help_shows_options(self) -> None:
        result = runner.invoke(app, ["batch", "--help"])

        assert result.exit_code == 0
        assert "--audio" in result.output
        assert "--video" in result.output
        assert "--parallel" in result.output

    def test_root_help_includes_batch_command(self) -> None:
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "batch" in result.output

    def test_batch_missing_file_exits_with_error(self) -> None:
        result = runner.invoke(app, ["batch", "/nonexistent/path/urls.txt"])

        assert result.exit_code == ExitCode.DOWNLOAD_FAILURE
        assert "File not found" in result.output

    def test_batch_audio_and_video_flags_are_mutually_exclusive(self, tmp_path: Path) -> None:
        url_file = tmp_path / "urls.txt"
        url_file.write_text(f"{VALID_URL_1}\n")

        result = runner.invoke(app, ["batch", str(url_file), "--audio", "--video"])

        assert result.exit_code == ExitCode.INVALID_URL
        assert "not both" in result.output

    def test_batch_empty_file_exits_gracefully(self, tmp_path: Path) -> None:
        url_file = tmp_path / "urls.txt"
        url_file.write_text("")

        result = runner.invoke(app, ["batch", str(url_file)])

        assert result.exit_code == ExitCode.INVALID_URL
        assert "No valid URLs" in result.output

    def test_batch_sequential_download(self, monkeypatch, tmp_path: Path) -> None:
        url_file = tmp_path / "urls.txt"
        url_file.write_text(f"{VALID_URL_1}\n{VALID_URL_2}\n")

        calls: list[str] = []

        def fake_convert(self, url: str, format_type: str, quality: str = "best") -> Path:
            calls.append(url)
            return tmp_path / "output.mp3"

        monkeypatch.setattr("ytconvert.converter.YouTubeConverter.convert", fake_convert)

        result = runner.invoke(app, ["batch", str(url_file)])

        assert result.exit_code == ExitCode.SUCCESS
        assert calls == [VALID_URL_1, VALID_URL_2]
        assert "succeeded" in result.output

    def test_batch_parallel_download(self, monkeypatch, tmp_path: Path) -> None:
        url_file = tmp_path / "urls.txt"
        url_file.write_text(f"{VALID_URL_1}\n{VALID_URL_2}\n{VALID_URL_3}\n")

        calls: list[str] = []

        def fake_convert(self, url: str, format_type: str, quality: str = "best") -> Path:
            calls.append(url)
            return tmp_path / "output.mp3"

        monkeypatch.setattr("ytconvert.converter.YouTubeConverter.convert", fake_convert)

        result = runner.invoke(app, ["batch", str(url_file), "--parallel", "3"])

        assert result.exit_code == ExitCode.SUCCESS
        assert sorted(calls) == sorted([VALID_URL_1, VALID_URL_2, VALID_URL_3])
        assert "succeeded" in result.output

    def test_batch_continues_after_failed_download(self, monkeypatch, tmp_path: Path) -> None:
        url_file = tmp_path / "urls.txt"
        url_file.write_text(f"{VALID_URL_1}\n{VALID_URL_2}\n")

        call_count = [0]

        def fake_convert(self, url: str, format_type: str, quality: str = "best") -> Path:
            call_count[0] += 1
            if url == VALID_URL_1:
                raise Exception("Network error")
            return tmp_path / "output.mp3"

        monkeypatch.setattr("ytconvert.converter.YouTubeConverter.convert", fake_convert)

        result = runner.invoke(app, ["batch", str(url_file)])

        assert result.exit_code == ExitCode.DOWNLOAD_FAILURE
        assert call_count[0] == 2
        assert "1 succeeded" in result.output
        assert "1 failed" in result.output

    def test_batch_uses_audio_flag(self, monkeypatch, tmp_path: Path) -> None:
        url_file = tmp_path / "urls.txt"
        url_file.write_text(f"{VALID_URL_1}\n")

        format_used: list[str] = []

        def fake_convert(self, url: str, format_type: str, quality: str = "best") -> Path:
            format_used.append(format_type)
            return tmp_path / "output.mp3"

        monkeypatch.setattr("ytconvert.converter.YouTubeConverter.convert", fake_convert)

        result = runner.invoke(app, ["batch", str(url_file), "--audio"])

        assert result.exit_code == ExitCode.SUCCESS
        assert format_used == ["mp3"]

    def test_batch_uses_video_flag(self, monkeypatch, tmp_path: Path) -> None:
        url_file = tmp_path / "urls.txt"
        url_file.write_text(f"{VALID_URL_1}\n")

        format_used: list[str] = []

        def fake_convert(self, url: str, format_type: str, quality: str = "best") -> Path:
            format_used.append(format_type)
            return tmp_path / "output.mp4"

        monkeypatch.setattr("ytconvert.converter.YouTubeConverter.convert", fake_convert)

        result = runner.invoke(app, ["batch", str(url_file), "--video"])

        assert result.exit_code == ExitCode.SUCCESS
        assert format_used == ["mp4"]

    def test_batch_shows_progress_index(self, monkeypatch, tmp_path: Path) -> None:
        url_file = tmp_path / "urls.txt"
        url_file.write_text(f"{VALID_URL_1}\n{VALID_URL_2}\n")

        def fake_convert(self, url: str, format_type: str, quality: str = "best") -> Path:
            return tmp_path / "output.mp3"

        monkeypatch.setattr("ytconvert.converter.YouTubeConverter.convert", fake_convert)

        result = runner.invoke(app, ["batch", str(url_file)])

        assert "[1/2]" in result.output
        assert "[2/2]" in result.output
