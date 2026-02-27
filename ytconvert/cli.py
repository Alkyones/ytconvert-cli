"""
CLI entry point for ytconvert-cli.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from ytconvert import __version__
from ytconvert.converter import YouTubeConverter
from ytconvert.exceptions import (
    ExitCode,
    InvalidURLError,
    DownloadError,
    FormatUnavailableError,
    YTConvertError,
)
from ytconvert.utils import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)
from ytconvert.validators import VALID_FORMATS, VALID_QUALITIES


def version_callback(value: bool) -> None:
    if value:
        print(f"ytconvert-cli version {__version__}")
        raise typer.Exit()


def main(
    url: Annotated[
        str,
        typer.Argument(help="YouTube video URL to convert"),
    ],
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: mp3 or mp4"),
    ] = "mp3",
    quality: Annotated[
        str,
        typer.Option("--quality", "-q", help="Video quality for MP4 (360p, 720p, 1080p, best)"),
    ] = "best",
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output directory"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
    info_only: Annotated[
        bool,
        typer.Option("--info", "-i", help="Only show video info, don't download"),
    ] = False,
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-V", help="Show version", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """Convert YouTube videos to MP3 or MP4 format."""
    setup_logging(verbose=verbose)
    
    if info_only:
        try:
            converter = YouTubeConverter(verbose=verbose)
            info = converter.get_video_info(url)
            print()
            print_info(f"Title: {info.get('title', 'Unknown')}")
            duration = info.get('duration', 0) or 0
            print_info(f"Duration: {int(duration) // 60}:{int(duration) % 60:02d}")
            print_info(f"Uploader: {info.get('uploader', 'Unknown')}")
            views = info.get('view_count', 0) or 0
            print_info(f"Views: {views:,}")
            sys.exit(ExitCode.SUCCESS)
        except YTConvertError as e:
            print_error(str(e))
            sys.exit(e.exit_code)
        except SystemExit:
            raise
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            raise typer.Exit(code=ExitCode.UNEXPECTED_ERROR)
    
    format_lower = format.lower()
    if format_lower not in VALID_FORMATS:
        print_error(f"Invalid format '{format}'. Must be: {', '.join(VALID_FORMATS)}")
        raise typer.Exit(code=ExitCode.INVALID_URL)
    
    quality_lower = quality.lower()
    if format_lower == "mp4" and quality_lower not in VALID_QUALITIES:
        print_error(f"Invalid quality '{quality}'. Must be: {', '.join(VALID_QUALITIES)}")
        raise typer.Exit(code=ExitCode.FORMAT_UNAVAILABLE)
    
    output_dir = output if output else Path.cwd()
    
    print_info(f"URL: {url}")
    print_info(f"Format: {format_lower.upper()}")
    if format_lower == "mp4":
        print_info(f"Quality: {quality_lower}")
    print_info(f"Output: {output_dir}")
    print()
    
    try:
        converter = YouTubeConverter(output_dir=output_dir, verbose=verbose)
        output_path = converter.convert(url=url, format_type=format_lower, quality=quality_lower)
        print()
        print_success("Conversion completed successfully!")
        print_success(f"Output file: {output_path}")
        sys.exit(ExitCode.SUCCESS)
    except InvalidURLError as e:
        print_error(str(e))
        sys.exit(ExitCode.INVALID_URL)
    except DownloadError as e:
        print_error(str(e))
        sys.exit(ExitCode.DOWNLOAD_FAILURE)
    except FormatUnavailableError as e:
        print_error(str(e))
        sys.exit(ExitCode.FORMAT_UNAVAILABLE)
    except YTConvertError as e:
        print_error(str(e))
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        print_error("Operation cancelled by user")
        sys.exit(ExitCode.UNEXPECTED_ERROR)
    except SystemExit:
        raise
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(ExitCode.UNEXPECTED_ERROR)


def cli() -> None:
    typer.run(main)


if __name__ == "__main__":
    cli()
