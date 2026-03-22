
# ytconvert-cli

**Production-ready YouTube to MP3/MP4 converter.**

[![PyPI](https://img.shields.io/pypi/v/ytconvert-cli.svg)](https://pypi.org/project/ytconvert-cli/)

**PyPI:** [ytconvert-cli 1.0.1](https://pypi.org/project/ytconvert-cli/1.0.0/)

**Github:** [click here!](https://github.com/Alkyones/ytconvert-cli)

[![PyPI version](https://img.shields.io/pypi/v/ytconvert-cli.svg)](https://pypi.org/project/ytconvert-cli/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Features

- Convert YouTube videos to **MP3** (audio extraction)
- Download YouTube videos as **MP4** (with quality selection)
- **Batch download** multiple URLs from a text file (with optional parallel downloads)
- Custom output directory support
- Progress indicators with download speed and ETA
- Clean error handling with specific exit codes
- **FFmpeg is bundled**—no separate install needed
- Uses yt-dlp Python API (no shell calls)
- Pip-installable and PyPI-ready

---

## 📦 Installation

### From PyPI (recommended)

```bash
pip install ytconvert-cli
```

### From source

```bash
Fork https://github.com/Alkyones/ytconvert-cli

git clone https://github.com/Yourusername/ytconvert-cli
cd ytconvert-cli
pip install .
```

---

## 🖥️ CLI Usage

```bash
# Convert to MP3 (default)
ytconvert https://www.youtube.com/watch?v=VIDEO_ID

# Convert to MP4
ytconvert https://www.youtube.com/watch?v=VIDEO_ID --format mp4

# MP4 with specific quality
ytconvert https://www.youtube.com/watch?v=VIDEO_ID --format mp4 --quality 720p

# Save to custom directory
ytconvert https://www.youtube.com/watch?v=VIDEO_ID -f mp3 -o ./downloads

# Get video info only (no download)
ytconvert https://www.youtube.com/watch?v=VIDEO_ID --info

# Search YouTube and download selected result (interactive)
ytconvert search "lofi hip hop"

# Search and download selected result as MP3
ytconvert search "chill beats" --audio

# Search and download selected result as MP4
ytconvert search "chill beats" --video

# Show help
ytconvert --help

# Show search command help
ytconvert search --help
```

**Short options:**
| Long      | Short | Description         |
|-----------|-------|---------------------|
| --format  | -f    | mp3 or mp4          |
| --quality | -q    | Video quality       |
| --output  | -o    | Output directory    |
| --info    | -i    | Info only           |
| --verbose | -v    | Debug mode          |
| --version | -V    | Show version        |

Search options:

| Long      | Description                              |
|-----------|------------------------------------------|
| --limit   | Number of search results (default: 10)   |
| --audio   | Download selected search result as MP3   |
| --video   | Download selected search result as MP4   |

---

## Search YouTube from the CLI

You can search YouTube directly in the terminal and choose what to download.

```bash
ytconvert search "lofi hip hop"
```

The command:

1. Runs a YouTube search using yt-dlp
2. Shows a numbered list with title, channel, and duration
3. Prompts you to select a result number
4. Downloads the selected video through the existing download pipeline

Example interaction:

```text
$ ytconvert search "lofi hip hop"

[1] Lofi Hip Hop Radio - Beats to Relax/Study To
Channel: Lofi Girl
Duration: 3:12:00

[2] Chill Lofi Mix
Channel: Chillhop Music
Duration: 1:45:10

Select video number: 2
```

Audio/video examples:

```bash
ytconvert search "chill beats" --audio
ytconvert search "chill beats" --video
ytconvert search "study music" --limit 5
```

---

## Batch Download

Download multiple YouTube URLs in one command by providing a text file with one URL per line.

### File format (`urls.txt`)

```
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
https://youtu.be/VIDEO_ID_3
```

- One URL per line
- Empty lines and whitespace are ignored
- Invalid or non-YouTube lines are skipped with a warning

### Usage

```bash
# Download all URLs as MP3 (default)
ytconvert batch urls.txt

# Download all URLs as MP3 explicitly
ytconvert batch urls.txt --audio

# Download all URLs as MP4
ytconvert batch urls.txt --video

# Download 5 at a time in parallel
ytconvert batch urls.txt --parallel 5

# Parallel audio downloads to a custom directory
ytconvert batch urls.txt --audio --parallel 3 --output ./downloads
```

### Example output

```text
[1/3] Downloading: https://www.youtube.com/watch?v=VIDEO_ID_1
[2/3] Downloading: https://www.youtube.com/watch?v=VIDEO_ID_2
[3/3] Downloading: https://www.youtube.com/watch?v=VIDEO_ID_3

✓ All downloads completed. Completed: 3 succeeded, 0 failed
```

If any download fails, the rest continue and a summary is shown:

```text
⚠ Completed: 2 succeeded, 1 failed
```

### Use cases

- **Archiving videos**: Save a curated list of videos before they disappear
- **Bulk audio downloads**: Extract MP3s from a playlist you've exported manually
- **Downloading playlists manually**: Paste playlist URLs one per line and batch download

### Batch options

| Option        | Description                              |
|---------------|------------------------------------------|
| `--audio`     | Download all URLs as MP3                 |
| `--video`     | Download all URLs as MP4                 |
| `--parallel N`| Download N URLs concurrently (default 1) |
| `--output`    | Output directory for all downloads       |
| `--verbose`   | Show verbose yt-dlp output               |

---

## Examples

```bash
# Convert URL to MP3
ytconvert https://www.youtube.com/watch?v=VIDEO_ID

# Convert URL to MP4 at 720p
ytconvert https://www.youtube.com/watch?v=VIDEO_ID --format mp4 --quality 720p

# Search and download interactively
ytconvert search "lofi hip hop"

# Search and download selected result as MP3
ytconvert search "chill beats" --audio

# Search and download selected result as MP4
ytconvert search "chill beats" --video
```

---

## 🐍 Python API Usage

```python
from ytconvert import YouTubeConverter

# Convert to MP3
converter = YouTubeConverter(output_dir="./downloads")
mp3_path = converter.convert_to_mp3("https://youtube.com/watch?v=VIDEO_ID")
print(f"Saved: {mp3_path}")

# Convert to MP4 with quality
mp4_path = converter.convert_to_mp4("https://youtube.com/watch?v=VIDEO_ID", quality="720p")

# Get video info only
info = converter.get_video_info("https://youtube.com/watch?v=VIDEO_ID")
print(f"Title: {info['title']}")
print(f"Duration: {info['duration']} seconds")
```

---

## 🛠️ Integration Example (Django, subprocess)

```python
import subprocess
import sys

def convert_youtube_video(url: str, format: str = "mp3", quality: str = "best"):
    cmd = [
        sys.executable, "-m", "ytconvert.cli",
        url,
        "--format", format,
        "--output", "/path/to/downloads",
    ]
    if format == "mp4" and quality != "best":
        cmd.extend(["--quality", quality])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return {"success": True, "output": result.stdout}
    else:
        return {"success": False, "exit_code": result.returncode, "error": result.stderr}
```

---

## ⚠️ Exit Codes

| Code | Meaning                       |
|------|-------------------------------|
| 0    | Success                       |
| 1    | Invalid YouTube URL           |
| 2    | Download failure              |
| 3    | Format or quality unavailable |
| 4    | Unexpected error              |

---

## 🏗️ Project Structure

```
ytconvert-cli/
├── ytconvert/
│   ├── __init__.py      # Package exports
│   ├── cli.py           # CLI entry point
│   ├── converter.py     # yt-dlp logic
│   ├── validators.py    # URL/format validation
**PyPI:** [ytconvert-cli 1.0.2](https://pypi.org/project/ytconvert-cli/1.0.2/)
│   └── utils.py         # Utilities
├── pyproject.toml       # Packaging config
├── README.md            # This file
└── LICENSE              # MIT License
```

---

## 📝 Development

```bash
# Run tests
pytest

# Format code
black ytconvert/
ruff check ytconvert/ --fix

# Type check
mypy ytconvert/
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video downloader
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [FFmpeg](https://ffmpeg.org/) - Media backend (bundled)

---

## 📢 Disclaimer

This tool is intended for downloading videos you have the right to download. Please respect copyright laws and YouTube's Terms of Service. The authors are not responsible for misuse.
