"""
YouTube video converter using yt-dlp.

This module provides the core conversion functionality for downloading
YouTube videos and converting them to MP3 or MP4 format.
"""

import os
from pathlib import Path
from typing import Any, Callable

import imageio_ffmpeg
import yt_dlp

from ytconvert.exceptions import (
    DownloadError,
    FormatUnavailableError,
    InvalidURLError,
    UnexpectedError,
)
from ytconvert.utils import (
    ensure_directory,
    format_duration,
    format_filesize,
    get_logger,
    get_quality_height,
    print_info,
    print_progress,
    print_success,
    sanitize_filename,
)
from ytconvert.validators import extract_video_id, validate_youtube_url


class ProgressHook:
    """Progress hook for yt-dlp to display download progress."""
    
    def __init__(self, callback: Callable[[dict[str, Any]], None] | None = None):
        self.callback = callback
        self._last_percent = -1
    
    def __call__(self, d: dict[str, Any]) -> None:
        """Handle progress updates from yt-dlp."""
        status = d.get("status")
        
        if status == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            
            if total > 0:
                percent = int((downloaded / total) * 100)
                # Only print on significant changes to reduce noise
                if percent != self._last_percent and percent % 10 == 0:
                    speed = d.get("speed", 0)
                    speed_str = f"{format_filesize(speed)}/s" if speed else "-- KB/s"
                    eta = d.get("eta", 0)
                    eta_str = format_duration(eta) if eta else "--:--"
                    
                    print_progress(
                        f"Downloading: {percent}% | "
                        f"Speed: {speed_str} | "
                        f"ETA: {eta_str}"
                    )
                    self._last_percent = percent
        
        elif status == "finished":
            filename = d.get("filename", "Unknown")
            print_success(f"Download complete: {Path(filename).name}")
        
        elif status == "error":
            get_logger().error("Download encountered an error")
        
        if self.callback:
            self.callback(d)


class YouTubeConverter:
    """
    YouTube video converter using yt-dlp.
    
    Provides methods to download and convert YouTube videos to MP3 or MP4 format.
    """
    
    def __init__(
        self,
        output_dir: str | Path = ".",
        verbose: bool = False,
        progress_callback: Callable[[dict[str, Any]], None] | None = None,
    ):
        """
        Initialize the YouTube converter.
        
        Args:
            output_dir: Directory where converted files will be saved
            verbose: If True, enable verbose logging
            progress_callback: Optional callback for progress updates
        """
        self.output_dir = ensure_directory(Path(output_dir))
        self.verbose = verbose
        self.progress_callback = progress_callback
        self.logger = get_logger()
    
    def _get_ffmpeg_path(self) -> str:
        """Get the path to the bundled FFmpeg executable."""
        return imageio_ffmpeg.get_ffmpeg_exe()
    
    def _get_base_options(self) -> dict[str, Any]:
        """Get base yt-dlp options common to all downloads."""
        return {
            "outtmpl": str(self.output_dir / "%(title)s.%(ext)s"),
            "restrictfilenames": False,
            "noplaylist": True,
            "quiet": not self.verbose,
            "no_warnings": not self.verbose,
            "progress_hooks": [ProgressHook(self.progress_callback)],
            "retries": 3,
            "fragment_retries": 3,
            "ignoreerrors": False,
            "nocheckcertificate": False,
            "ffmpeg_location": self._get_ffmpeg_path(),
        }
    
    def _get_mp3_options(self) -> dict[str, Any]:
        """Get yt-dlp options for MP3 conversion."""
        options = self._get_base_options()
        options.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "outtmpl": str(self.output_dir / "%(title)s.%(ext)s"),
        })
        return options
    
    def _get_mp4_options(self, quality: str = "best") -> dict[str, Any]:
        """
        Get yt-dlp options for MP4 download.
        
        Args:
            quality: Video quality (e.g., "720p", "1080p", "best")
        """
        options = self._get_base_options()
        
        height = get_quality_height(quality)
        
        if height:
            # Request specific quality with fallback
            format_str = (
                f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/"
                f"bestvideo[height<={height}]+bestaudio/best[height<={height}]/best"
            )
        else:
            # Best quality available
            format_str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/bestvideo+bestaudio/best"
        
        options.update({
            "format": format_str,
            "merge_output_format": "mp4",
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }],
        })
        return options
    
    def get_video_info(self, url: str) -> dict[str, Any]:
        """
        Get information about a YouTube video without downloading.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Dictionary containing video metadata
            
        Raises:
            InvalidURLError: If the URL is invalid
            DownloadError: If video info cannot be retrieved
        """
        url = validate_youtube_url(url)
        
        options = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }
        
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise DownloadError("Failed to retrieve video information")
                
                return {
                    "id": info.get("id"),
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "description": info.get("description"),
                    "thumbnail": info.get("thumbnail"),
                    "uploader": info.get("uploader"),
                    "view_count": info.get("view_count"),
                    "like_count": info.get("like_count"),
                    "formats": [
                        {
                            "format_id": f.get("format_id"),
                            "ext": f.get("ext"),
                            "resolution": f.get("resolution"),
                            "filesize": f.get("filesize"),
                        }
                        for f in info.get("formats", [])
                    ],
                }
        
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if "Video unavailable" in error_msg or "Private video" in error_msg:
                raise DownloadError(f"Video is unavailable or private: {error_msg}")
            raise DownloadError(f"Failed to get video info: {error_msg}")
        except Exception as e:
            raise UnexpectedError(f"Unexpected error getting video info: {e}")

    @staticmethod
    def parse_search_results(entries: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
        """
        Normalize yt-dlp search entries for CLI consumption.

        Args:
            entries: Raw entries returned by yt-dlp search

        Returns:
            List of dictionaries with normalized search metadata
        """
        normalized_results: list[dict[str, Any]] = []

        for entry in entries or []:
            if not entry:
                continue

            video_id = entry.get("id")
            webpage_url = entry.get("webpage_url")
            if not webpage_url and video_id:
                webpage_url = f"https://www.youtube.com/watch?v={video_id}"

            if not webpage_url:
                continue

            normalized_results.append(
                {
                    "id": video_id,
                    "title": entry.get("title") or "Unknown title",
                    "uploader": entry.get("uploader") or entry.get("channel") or "Unknown",
                    "duration": entry.get("duration"),
                    "url": webpage_url,
                }
            )

        return normalized_results

    def search_videos(self, search_query: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Search YouTube videos using yt-dlp search syntax.

        Args:
            search_query: Human-readable search query text
            limit: Maximum number of results to fetch

        Returns:
            List of normalized search results

        Raises:
            ValueError: If query or limit are invalid
            DownloadError: If yt-dlp search fails
        """
        if not search_query or not search_query.strip():
            raise ValueError("Search query cannot be empty")

        if limit < 1:
            raise ValueError("Search limit must be at least 1")

        query = f"ytsearch{limit}:{search_query.strip()}"
        options = {
            "quiet": not self.verbose,
            "no_warnings": not self.verbose,
            "extract_flat": False,
            "ignoreerrors": True,
        }

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(query, download=False)

                if not info:
                    return []

                entries = info.get("entries")
                return self.parse_search_results(entries)

        except yt_dlp.utils.DownloadError as e:
            raise DownloadError(f"Search failed: {e}")
        except Exception as e:
            if isinstance(e, (DownloadError, ValueError)):
                raise
            raise UnexpectedError(f"Unexpected error during search: {e}")
    
    def convert_to_mp3(self, url: str) -> Path:
        """
        Download and convert a YouTube video to MP3.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Path to the converted MP3 file
            
        Raises:
            InvalidURLError: If the URL is invalid
            DownloadError: If download fails
            FormatUnavailableError: If MP3 conversion fails
        """
        url = validate_youtube_url(url)
        
        print_info("Starting MP3 conversion...")
        self.logger.info(f"Converting to MP3: {url}")
        
        options = self._get_mp3_options()
        
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if not info:
                    raise DownloadError("Failed to download video")
                
                # Determine output filename
                title = sanitize_filename(info.get("title", "video"))
                output_path = self.output_dir / f"{title}.mp3"
                
                # yt-dlp might use a different filename, try to find it
                if not output_path.exists():
                    # Look for any recently created mp3 file
                    mp3_files = list(self.output_dir.glob("*.mp3"))
                    if mp3_files:
                        # Get the most recently modified mp3 file
                        output_path = max(mp3_files, key=lambda p: p.stat().st_mtime)
                
                print_success(f"Successfully converted to MP3: {output_path.name}")
                return output_path
        
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if "format" in error_msg.lower():
                raise FormatUnavailableError(f"Audio format unavailable: {error_msg}")
            raise DownloadError(f"Download failed: {error_msg}")
        except Exception as e:
            if isinstance(e, (InvalidURLError, DownloadError, FormatUnavailableError)):
                raise
            raise UnexpectedError(f"Unexpected error during MP3 conversion: {e}")
    
    def convert_to_mp4(self, url: str, quality: str = "best") -> Path:
        """
        Download a YouTube video as MP4.
        
        Args:
            url: YouTube video URL
            quality: Video quality (e.g., "720p", "1080p", "best")
            
        Returns:
            Path to the downloaded MP4 file
            
        Raises:
            InvalidURLError: If the URL is invalid
            DownloadError: If download fails
            FormatUnavailableError: If requested quality is unavailable
        """
        url = validate_youtube_url(url)
        
        print_info(f"Starting MP4 download (quality: {quality})...")
        self.logger.info(f"Converting to MP4 with quality '{quality}': {url}")
        
        options = self._get_mp4_options(quality)
        
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if not info:
                    raise DownloadError("Failed to download video")
                
                # Determine output filename
                title = sanitize_filename(info.get("title", "video"))
                output_path = self.output_dir / f"{title}.mp4"
                
                # yt-dlp might use a different filename, try to find it
                if not output_path.exists():
                    # Look for any recently created mp4 file
                    mp4_files = list(self.output_dir.glob("*.mp4"))
                    if mp4_files:
                        # Get the most recently modified mp4 file
                        output_path = max(mp4_files, key=lambda p: p.stat().st_mtime)
                
                print_success(f"Successfully downloaded MP4: {output_path.name}")
                return output_path
        
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if "format" in error_msg.lower() or "quality" in error_msg.lower():
                raise FormatUnavailableError(
                    f"Requested quality '{quality}' unavailable: {error_msg}"
                )
            raise DownloadError(f"Download failed: {error_msg}")
        except Exception as e:
            if isinstance(e, (InvalidURLError, DownloadError, FormatUnavailableError)):
                raise
            raise UnexpectedError(f"Unexpected error during MP4 download: {e}")
    
    def convert(self, url: str, format_type: str, quality: str = "best") -> Path:
        """
        Convert a YouTube video to the specified format.
        
        Args:
            url: YouTube video URL
            format_type: Output format ("mp3" or "mp4")
            quality: Video quality for MP4 (ignored for MP3)
            
        Returns:
            Path to the converted file
        """
        format_type = format_type.lower()
        
        if format_type == "mp3":
            return self.convert_to_mp3(url)
        elif format_type == "mp4":
            return self.convert_to_mp4(url, quality)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
