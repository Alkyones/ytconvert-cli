"""CLI entry point for ytconvert-cli."""

from __future__ import annotations

import sys
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Optional

import typer
from typing_extensions import Annotated

from ytconvert import __version__
from ytconvert.converter import YouTubeConverter
from ytconvert.exceptions import (
    DownloadError,
    ExitCode,
    FormatUnavailableError,
    InvalidURLError,
    YTConvertError,
)
from ytconvert.utils import (
    format_duration,
    print_error,
    print_info,
    print_success,
    print_warning,
    setup_logging,
)
from ytconvert.validators import VALID_FORMATS, VALID_QUALITIES, validate_youtube_url

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Convert YouTube videos or search YouTube and download from the terminal.",
)

CANCELLED_MESSAGE = "Operation cancelled by user"
SEARCH_USAGE_HINT = "Please provide a search query. Example: ytconvert search \"lofi hip hop\""
KNOWN_SUBCOMMANDS = {"convert", "search", "batch"}

OutputOption = Annotated[
    Optional[Path],
    typer.Option("--output", "-o", help="Output directory"),
]
VerboseOption = Annotated[
    bool,
    typer.Option("--verbose", "-v", help="Enable verbose output"),
]


def version_callback(value: bool) -> None:
    if value:
        print(f"ytconvert-cli version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-V", help="Show version", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """ytconvert command group."""
    _ = version


def _validate_format_and_quality(format_type: str, quality: str) -> tuple[str, str]:
    format_lower = format_type.lower()
    if format_lower not in VALID_FORMATS:
        print_error(f"Invalid format '{format_type}'. Must be: {', '.join(VALID_FORMATS)}")
        raise typer.Exit(code=ExitCode.INVALID_URL)

    quality_lower = quality.lower()
    if format_lower == "mp4" and quality_lower not in VALID_QUALITIES:
        print_error(f"Invalid quality '{quality}'. Must be: {', '.join(VALID_QUALITIES)}")
        raise typer.Exit(code=ExitCode.FORMAT_UNAVAILABLE)

    return format_lower, quality_lower


def _print_conversion_success(output_path: Path) -> None:
    print()
    print_success("Conversion completed successfully!")
    print_success(f"Output file: {output_path}")


def _convert_url(
    converter: YouTubeConverter,
    url: str,
    format_type: str,
    quality: str,
    output_dir: Path,
) -> Path:
    print_info(f"URL: {url}")
    print_info(f"Format: {format_type.upper()}")
    if format_type == "mp4":
        print_info(f"Quality: {quality}")
    print_info(f"Output: {output_dir}")
    print()
    return converter.convert(url=url, format_type=format_type, quality=quality)


def _show_video_info(converter: YouTubeConverter, url: str) -> None:
    info = converter.get_video_info(url)
    duration = info.get("duration", 0) or 0
    views = info.get("view_count", 0) or 0

    print()
    print_info(f"Title: {info.get('title', 'Unknown')}")
    print_info(f"Duration: {int(duration) // 60}:{int(duration) % 60:02d}")
    print_info(f"Uploader: {info.get('uploader', 'Unknown')}")
    print_info(f"Views: {views:,}")


def _print_search_results(results: list[dict[str, Any]]) -> None:
    print()
    for index, result in enumerate(results, start=1):
        duration = result.get("duration")
        duration_text = format_duration(duration) if isinstance(duration, (int, float)) and duration >= 0 else "Unknown"

        print(f"[{index}] {result.get('title') or 'Unknown title'}")
        print(f"Channel: {result.get('uploader') or 'Unknown'}")
        print(f"Duration: {duration_text}")
        print()


def _prompt_for_selection(total_results: int) -> int:
    try:
        selected_number = int(typer.prompt("Select video number"))
    except ValueError as exc:
        raise ValueError("Selection must be a number") from exc

    if not 1 <= selected_number <= total_results:
        raise ValueError(f"Invalid selection. Choose a number between 1 and {total_results}")

    return selected_number - 1


def _raise_for_handled_error(error: Exception) -> None:
    for error_type, exit_code in (
        (InvalidURLError, ExitCode.INVALID_URL),
        (DownloadError, ExitCode.DOWNLOAD_FAILURE),
        (FormatUnavailableError, ExitCode.FORMAT_UNAVAILABLE),
        (ValueError, ExitCode.INVALID_URL),
    ):
        if isinstance(error, error_type):
            print_error(str(error))
            raise typer.Exit(code=exit_code)

    if isinstance(error, YTConvertError):
        print_error(str(error))
        raise typer.Exit(code=error.exit_code)

    if isinstance(error, (KeyboardInterrupt, typer.Abort)):
        print_error(CANCELLED_MESSAGE)
        raise typer.Exit(code=ExitCode.UNEXPECTED_ERROR)

    print_error(f"Unexpected error: {error}")
    raise typer.Exit(code=ExitCode.UNEXPECTED_ERROR)


def _run_command(verbose: bool, action: Callable[[], None]) -> None:
    setup_logging(verbose=verbose)
    try:
        action()
    except typer.Exit:
        raise
    except Exception as error:
        _raise_for_handled_error(error)


@app.command("convert", help="Convert a YouTube URL to MP3 or MP4")
def convert_command(
    url: Annotated[
        str,
        typer.Argument(help="YouTube video URL to convert", metavar="URL"),
    ],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: mp3 or mp4"),
    ] = "mp3",
    quality: Annotated[
        str,
        typer.Option("--quality", "-q", help="Video quality for MP4 (360p, 720p, 1080p, best)"),
    ] = "best",
    output: OutputOption = None,
    verbose: VerboseOption = False,
    info_only: Annotated[
        bool,
        typer.Option("--info", "-i", help="Only show video info, don't download"),
    ] = False,
) -> None:
    """Convert YouTube videos to MP3 or MP4 format."""

    def action() -> None:
        output_dir = output or Path.cwd()
        converter = YouTubeConverter(output_dir=output_dir, verbose=verbose)

        if info_only:
            _show_video_info(converter=converter, url=url)
            raise typer.Exit(code=ExitCode.SUCCESS)

        format_lower, quality_lower = _validate_format_and_quality(format_type=format, quality=quality)
        output_path = _convert_url(
            converter=converter,
            url=url,
            format_type=format_lower,
            quality=quality_lower,
            output_dir=output_dir,
        )
        _print_conversion_success(output_path)
        raise typer.Exit(code=ExitCode.SUCCESS)

    _run_command(verbose=verbose, action=action)


@app.command("search", help="Search YouTube and download a selected result")
def search_command(
    query: Annotated[
        Optional[str],
        typer.Argument(help="Search query text", metavar="QUERY"),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", help="Number of search results (default: 10)", min=1),
    ] = 10,
    audio: Annotated[
        bool,
        typer.Option("--audio", help="Download selected result as MP3"),
    ] = False,
    video: Annotated[
        bool,
        typer.Option("--video", help="Download selected result as MP4"),
    ] = False,
    output: OutputOption = None,
    verbose: VerboseOption = False,
) -> None:
    """Search YouTube from the terminal and choose one result to download.

    Usage:
    ytconvert search <query> [options]
    """
    search_query = (query or "").strip()
    if not search_query:
        print_error(SEARCH_USAGE_HINT)
        raise typer.Exit(code=ExitCode.INVALID_URL)

    if audio and video:
        print_error("Use either --audio or --video, not both")
        raise typer.Exit(code=ExitCode.INVALID_URL)

    def action() -> None:
        output_dir = output or Path.cwd()
        format_type = "mp4" if video else "mp3"
        converter = YouTubeConverter(output_dir=output_dir, verbose=verbose)

        results = converter.search_videos(search_query=search_query, limit=limit)
        if not results:
            print_warning("No videos found for that search query")
            raise typer.Exit(code=ExitCode.DOWNLOAD_FAILURE)

        _print_search_results(results)
        selected_video = results[_prompt_for_selection(total_results=len(results))]

        print_info(f"Downloading: {selected_video['title']}...")
        output_path = converter.convert(
            url=selected_video["url"],
            format_type=format_type,
            quality="best",
        )
        _print_conversion_success(output_path)
        raise typer.Exit(code=ExitCode.SUCCESS)

    _run_command(verbose=verbose, action=action)


def _parse_urls_from_file(file_path: Path) -> list[str]:
    """Read YouTube URLs from a text file, skipping blank lines and invalid URLs."""
    try:
        with open(file_path) as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")

    urls: list[str] = []
    for line in lines:
        try:
            validate_youtube_url(line)
            urls.append(line)
        except InvalidURLError:
            print_warning(f"Skipping invalid URL: {line}")

    return urls


def _download_with_progress(
    converter: YouTubeConverter,
    url: str,
    idx: int,
    total: int,
    format_type: str,
    quality: str,
    lock: threading.Lock,
) -> bool:
    """Download a single URL with progress output. Returns True on success."""
    with lock:
        print_info(f"[{idx}/{total}] Downloading: {url}")
    try:
        converter.convert(url=url, format_type=format_type, quality=quality)
        return True
    except Exception as e:
        with lock:
            print_error(f"[{idx}/{total}] Failed: {url} — {e}")
        return False


@app.command("batch", help="Download multiple URLs from a file")
def batch_command(
    file_path: Annotated[
        str,
        typer.Argument(help="Path to a text file with one YouTube URL per line", metavar="FILE"),
    ],
    audio: Annotated[
        bool,
        typer.Option("--audio", help="Download as MP3"),
    ] = False,
    video: Annotated[
        bool,
        typer.Option("--video", help="Download as MP4"),
    ] = False,
    parallel: Annotated[
        int,
        typer.Option("--parallel", help="Number of parallel downloads", min=1),
    ] = 1,
    output: OutputOption = None,
    verbose: VerboseOption = False,
) -> None:
    """Download multiple YouTube URLs listed in a text file.

    Usage:
    ytconvert batch <file_path> [options]
    """
    if audio and video:
        print_error("Use either --audio or --video, not both")
        raise typer.Exit(code=ExitCode.INVALID_URL)

    def action() -> None:
        path = Path(file_path)
        try:
            urls = _parse_urls_from_file(path)
        except FileNotFoundError as e:
            print_error(str(e))
            raise typer.Exit(code=ExitCode.DOWNLOAD_FAILURE)

        if not urls:
            print_warning("No valid URLs found in file.")
            raise typer.Exit(code=ExitCode.INVALID_URL)

        format_type = "mp4" if video else "mp3"
        quality = "best"
        output_dir = output or Path.cwd()
        converter = YouTubeConverter(output_dir=output_dir, verbose=verbose)
        total = len(urls)
        lock = threading.Lock()

        if parallel > 1:
            with ThreadPoolExecutor(max_workers=parallel) as executor:
                futures = [
                    executor.submit(
                        _download_with_progress,
                        converter, url, i, total, format_type, quality, lock,
                    )
                    for i, url in enumerate(urls, 1)
                ]
                results = [f.result() for f in as_completed(futures)]
        else:
            results = [
                _download_with_progress(converter, url, i, total, format_type, quality, lock)
                for i, url in enumerate(urls, 1)
            ]

        succeeded = sum(results)
        failed = total - succeeded

        print()
        if failed == 0:
            print_success(f"All downloads completed. Completed: {succeeded} succeeded, {failed} failed")
        else:
            print_warning(f"Completed: {succeeded} succeeded, {failed} failed")

        if failed > 0:
            raise typer.Exit(code=ExitCode.DOWNLOAD_FAILURE)
        raise typer.Exit(code=ExitCode.SUCCESS)

    _run_command(verbose=verbose, action=action)


def _normalize_cli_args(raw_args: list[str]) -> list[str]:
    """Translate legacy `ytconvert <url>` usage into `ytconvert convert <url>`."""
    if not raw_args:
        return raw_args

    first_arg = raw_args[0]
    if first_arg.startswith("-") or first_arg in KNOWN_SUBCOMMANDS:
        return raw_args

    return ["convert", *raw_args]


def cli() -> None:
    app(args=_normalize_cli_args(sys.argv[1:]), prog_name="ytconvert")


if __name__ == "__main__":
    cli()
