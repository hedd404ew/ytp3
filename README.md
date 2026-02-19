# YTP3

![Python Version](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A modern, feature-rich YouTube downloader with both GUI and CLI interfaces. Download videos, audio, playlists, and more with intelligent fallback strategies.

## Features

- 🎥 **Video & Audio Downloads** - Download videos or extract audio with robust 5-layer audio-video merging
- 📋 **Playlist Support** - Handle entire playlists with batch operations
- 🎞️ **Quality Selection** - Choose between best, high (1080p), medium (720p), or low (480p) quality
- 🔄 **5-Layer Fallback System** - Automatic format degradation with 20 total attempts
- 🛡️ **Comprehensive Error Logging** - [ATTEMPT X] tracking with detailed error reasons
- 🔄 **Bypass Strategies** - Multiple fallback strategies (Standard, Android, iOS, TV)
- 🖥️ **Dual Interface** - Professional GUI and powerful CLI
- 📝 **Metadata Embedding** - Automatically embed metadata (title, description, etc.)
- 🌐 **Authentication** - Browser cookie integration and custom cookie files
- 🎬 **Post-Processing** - FFmpeg integration for format conversion
- ⚡ **Concurrent Downloads** - Multi-threaded downloads (configurable)
- 💾 **Portable Config** - Store settings locally or in system directories

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for video/audio encoding)
- Optional: Deno or Node.js (for advanced features)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/hedd404ew/ytp3.git
   cd ytp3
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg** (if not already installed)
   - **Windows**: `choco install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

## Usage

### GUI Mode (Default)

Simply run the script with no arguments:

```bash
python ytp3_main.py
```

This launches the graphical interface where you can:
- Input URLs and fetch metadata
- Preview video information
- Customize download settings
- Monitor progress with visual feedback
- View logs in real-time

### CLI Mode

For command-line usage:

```bash
# Download a video
python ytp3_main.py "https://www.youtube.com/watch?v=..."

# Download as audio
python ytp3_main.py -a -f mp3 "https://www.youtube.com/watch?v=..."

# Download playlist to specific directory
python ytp3_main.py -o ~/Downloads "https://www.youtube.com/playlist?list=..."

# Advanced options
python ytp3_main.py -a --subs --geo --cookies-browser chrome "https://www.youtube.com/watch?v=..."

# Quality selection (best/high/medium/low)
python ytp3_main.py -q high "https://www.youtube.com/watch?v=..."

# Force FFmpeg merge for reliability
python ytp3_main.py --force-ffmpeg "https://www.youtube.com/watch?v=..."
```

### CLI Options

```
usage: ytp3_main.py [-h] [-a] [-f FORMAT] [-q QUALITY] [-o OUTPUT] [--no-meta] [--no-thumb] 
                    [--subs] [--geo] [--reverse] [--force-ffmpeg] [--cookies-browser COOKIES_BROWSER] 
                    [--cookies-file COOKIES_FILE] 
                    [url]

Options:
  -h, --help                     Show this help message
  -a, --audio                    Download audio only
  -f, --format FORMAT            Output format (mp4, mkv, webm, mp3, m4a, wav)
  -q, --quality QUALITY          Video quality: best/high/medium/low (default: best)
                                 best: any quality, high: max 1080p, medium: max 720p, low: max 480p
  -o, --output OUTPUT            Output directory
  --no-meta                      Don't embed metadata
  --no-thumb                     Don't embed thumbnail
  --subs                         Download subtitles
  --geo                          Enable geo-bypass
  --reverse                       Reverse playlist order
  --force-ffmpeg                 Force FFmpeg concat postprocessor for robust stream merging
  --cookies-browser BROWSER      Extract cookies from browser (chrome, firefox, edge)
  --cookies-file FILE            Path to Netscape format cookie file
```

## Project Structure

```
ytp3/
├── ytp3/
│   ├── __init__.py              # Package initialization
│   ├── core/
│   │   ├── __init__.py
│   │   ├── engine.py            # Main download engine
│   │   └── strategies.py        # Bypass strategies
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── app.py               # Main GUI application
│   │   └── components.py        # UI components
│   ├── cli.py                   # CLI interface
│   └── utils/
│       ├── __init__.py
│       ├── config.py            # Configuration management
│       └── system.py            # System diagnostics
├── ytp3_main.py                 # Main entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Configuration

### GUI Configuration

Settings are automatically saved to:
- **Windows**: `%APPDATA%\YTP3\config.json`
- **Linux/macOS**: `~/.config/YTP3/config.json`
- **Portable**: `ytp3_config.json` (in current directory)

### Manual Configuration

Edit the JSON config file directly:

```json
{
    "save_path": "/home/user/Downloads",
    "mode": "Video",
    "format": "mp4",
    "concurrency": 2,
    "toggles": {
        "meta": true,
        "thumb": true,
        "subs": false,
        "geo": false
    }
}
```

## Authentication

### Browser Cookies

The application can extract cookies directly from your browser:
- Chrome
- Firefox
- Edge
- Brave

### Cookie File

Alternatively, provide a Netscape-format cookie file:
1. Export cookies using a browser extension
2. Ensure the file header contains `# Netscape HTTP Cookie File`
3. Provide the path via CLI or GUI

## Advanced Features

### Retry Strategies

The engine automatically retries downloads with different strategies if the first fails:
1. **Standard** - Direct YouTube extraction
2. **Android Bypass** - Uses Android player client
3. **iOS Bypass** - Uses iOS player client
4. **TV Bypass** - Uses TV player client

### Rate Limiting

Built-in protection against rate limiting:
- Random delays between downloads
- Automatic cooldown on rate limit detection
- Configurable sleep intervals

### Post-Processing

Automatic post-processing with FFmpeg:
- Audio extraction
- Format conversion
- Metadata embedding
- Thumbnail embedding
- Subtitle embedding

## Troubleshooting

### Common Issues

**"Videos downloaded without audio"**
- This is now handled by the 5-layer fallback system (v1.2+)
- The engine automatically tries different format combinations
- Check Log tab in GUI to see which [ATTEMPT X] succeeded
- Watch for [FAILED] entries to see what was tried
- **If still occurring**: Try lower quality (`-q medium`) or different format

**"FFmpeg not found"**
- Install FFmpeg (see Installation section)
- Ensure it's in your system PATH
- Check System Health in GUI (Auth tab)

**"Netscape format" cookie error**
- Ensure cookie file has proper Netscape format header
- Export from a cookie manager, not browser directly

**"Rate limit detected"**
- Normal - the app will automatically retry after cooldown
- Consider increasing delay between downloads
- Try using auth with cookies

**"Signature error"**
- App will automatically retry with different strategy
- Ensure you have internet connectivity
- Update yt-dlp: `pip install --upgrade yt-dlp`

### Understanding the Fallback System

The engine uses a 5-layer degradation strategy to ensure maximum compatibility:

| Layer | Format | Use Case |
|-------|--------|----------|
| L1 | `bestvideo[ext=mp4]+bestaudio[ext=m4a]` | Containerized formats (most reliable) |
| L2 | `bestvideo+bestaudio/best` | Standard auto-merge |
| L3 | `bestvideo[height<=1080]+bestaudio` | Quality-limited selection |
| L4 | `best[ext=mp4]` | Single format fallback |
| L5 | `best` | Absolute fallback |

Each layer is tried with 4 strategies (Standard, Android, iOS, TV), resulting in **20 total attempts**.

**Log output example**:
```
[ATTEMPT 1] L1: Best quality with merged audio
[STRATEGY] Attempting with Standard bypass...
[FAILED L1] Standard: Format not available
[ATTEMPT 2] L1: Best quality with merged audio
[STRATEGY] Attempting with Android bypass...
[FAILED L1] Android: Download failed
[ATTEMPT 3] L2: Auto-select best video+audio
[STRATEGY] Attempting with Standard bypass...
[SUCCESS] Download completed!
```

### Debug Mode

To get detailed logs:
1. **GUI**: Open Log tab and watch [ATTEMPT X], [STRATEGY], [FAILED], [SUCCESS] messages
2. **CLI**: Run with quality flag to see more details:
   ```bash
   python ytp3_main.py -q medium "URL"
   ```
3. **Check crash reports**: Look for `crash_*.txt` files in same directory

### Enabling Verbose FFmpeg Output

The engine now includes verbose FFmpeg logging:
- Show detailed codec information
- Audio/video stream details
- Merge operations
- Check Log tab for `[YT-DLP]` and `[POST-PROCESSING]` messages

### Postprocessor & Metadata Handling (v1.3+)

**What changed**:
- Thumbnail embedding disabled to prevent compatibility issues
- Downloads focus on audio/video quality and metadata stability
- Robust FFmpeg error handling with detailed logging
- Video quality never affected by postprocessor failures

**Available Postprocessors**:
- FFmpeg metadata embedding (title, description, duration, etc.)
- FFmpeg format conversion and merging (audio+video combination)
- Subtitle extraction and embedding (when requested)

**To skip extra postprocessors**:
```bash
python ytp3_main.py --no-meta "URL"
# Downloads video with audio only, no additional metadata
```

**Common FFmpeg Issues & Fixes**:

| Error | Cause | Fix |
|-------|-------|-----|
| `exit code -22` | FFmpeg postprocessor error | Usually resolved; check FFmpeg installation |
| `ERROR: Post-processing failed` | FFmpeg codec incompatibility | Update FFmpeg or use lower quality |
| `ERROR: Unable to embed using ffprobe` | Missing ffmpeg tools | Reinstall FFmpeg: verify with `ffmpeg -version` |
| `[FAILED Ln] Standard: ...` | Download format not available | Try lower quality: `-q medium` or `-q low` |

**5-Layer Fallback Strategy (v1.3+)**:
1. **L1**: Best quality with merged audio/video
2. **L2**: Auto-select best available video+audio combo
3. **L3**: Capped to 1080p maximum resolution
4. **L4**: Single best MP4 format (no merge needed)
5. **L5**: Fallback to absolute best available format

If L1 format fails, system automatically tries L2, then L3, etc. You always get a working download.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Legal Notice

This tool is for downloading content you have the right to download. Respect:
- Copyright laws
- Platform terms of service
- Creator intellectual property rights

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Core downloading library
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern GUI framework
- [Pillow](https://python-pillow.org/) - Image processing

## Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/hedd404ew/ytp3/issues)
- Check [Discussions](https://github.com/hedd404ew/ytp3/discussions)
- See [Wiki](https://github.com/hedd404ew/ytp3/wiki)

## Changelog

### Version 3.0.0
- Complete refactor into modular architecture
- Separated core, UI, and utilities
- Improved code organization and documentation
- Added comprehensive CLI
- Better error handling and logging

### Version 2.x
- Initial stable release
- GUI and CLI support
- Multi-strategy downloading
