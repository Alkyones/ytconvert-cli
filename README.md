
# ytconvert-cli

**Production-ready YouTube to MP3/MP4 converter.**

[![PyPI](https://img.shields.io/pypi/v/ytconvert-cli.svg)](https://pypi.org/project/ytconvert-cli/)

**PyPI:** [ytconvert-cli 1.0.0](https://pypi.org/project/ytconvert-cli/1.0.0/)

[![PyPI version](https://img.shields.io/pypi/v/ytconvert-cli.svg)](https://pypi.org/project/ytconvert-cli/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🚀 Features

- Convert YouTube videos to **MP3** (audio extraction)
- Download YouTube videos as **MP4** (with quality selection)
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
git clone https://github.com/yourusername/ytconvert-cli.git
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

# Show help
ytconvert --help
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
│   ├── exceptions.py    # Custom exceptions
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
