# Quick Start Guide

## Project Structure at a Glance

```
ytp3/
│
├── 📄 ytp3_main.py              ← Run this to start
├── 📄 setup.py                  ← For PyPI package
├── 📄 requirements.txt          ← Dependencies
│
├── 📁 ytp3/                     ← Main package
│   ├── cli.py                   ← CLI interface
│   │
│   ├── 📁 core/                 ← Download engine
│   │   ├── engine.py            ← Main download logic
│   │   └── strategies.py        ← Bypass strategies
│   │
│   ├── 📁 ui/                   ← GUI components
│   │   ├── app.py               ← Main application
│   │   └── components.py        ← UI components
│   │
│   └── 📁 utils/                ← Utilities
│       ├── config.py            ← Configuration
│       └── system.py            ← System tools
│
├── � README.md                 ← Main user guide
├── 📄 QUICKSTART.md             ← Quick reference (this file)
├── 📄 CONTRIBUTING.md           ← How to contribute
├── 📄 DEVELOPMENT.md            ← For developers
├── 📄 INDEX.md                  ← Documentation index
├── 📄 LICENSE                   ← MIT License
│
└── 📄 .gitignore                ← Git configuration
```

## Quick Commands

```bash
# Setup
pip install -r requirements.txt

# Run GUI (default)
python ytp3_main.py

# Download video
python ytp3_main.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Download audio
python ytp3_main.py -a -f mp3 "https://www.youtube.com/watch?v=VIDEO_ID"

# Download playlist
python ytp3_main.py "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Install as package
pip install -e .
ytp3 "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Import Examples

```python
# Download engine only
from ytp3.core.engine import YTP3Engine
engine = YTP3Engine({}, {})
metadata = engine.resolve_metadata(url)

# Configuration management
from ytp3.utils.config import ConfigManager
config = ConfigManager()
settings = config.load()

# System diagnostics
from ytp3.utils.system import SystemDoctor
doctor = SystemDoctor()
report = doctor.run_diagnostics(".")

# Launch GUI
from ytp3.ui.app import run_gui
run_gui()

# Run CLI
from ytp3.cli import main as cli_main
cli_main()
```

## Key Classes

| Class | Module | Purpose |
|-------|--------|---------|
| `YTP3Engine` | `core.engine` | Main download orchestrator |
| `DownloadStrategy` | `core.strategies` | Strategy management |
| `YTP3App` | `ui.app` | Main GUI window |
| `RetroProgressBar` | `ui.components` | Animated progress display |
| `VideoItemRow` | `ui.components` | Queue item widget |
| `ConfigManager` | `utils.system` | Configuration I/O |
| `SystemDoctor` | `utils.system` | System diagnostics |
| `PathManager` | `utils.system` | Path utilities |
| `CrashHandler` | `utils.system` | Error logging |

## File Purposes

### Core Files
- **engine.py** - Download logic, metadata resolution, retry strategies
- **strategies.py** - Strategy definitions (Android, iOS, TV bypass)

### UI Files
- **app.py** - Main window, tabs, event handlers (620 lines)
- **components.py** - Reusable widgets (progress bar, video rows)

### Utility Files
- **system.py** - Config, diagnostics, paths, crashes
- **config.py** - Re-exports from system.py

### Entry Points
- **ytp3_main.py** - Main entry (GUI or CLI)
- **cli.py** - CLI argument parsing and execution

## Most Common Tasks

### If you want to...

**Use the GUI:**
```bash
python ytp3_main.py
```

**Download a video from CLI:**
```bash
python ytp3_main.py "https://www.youtube.com/watch?v=..."
```

**Extract just audio:**
```bash
python ytp3_main.py -a -f mp3 "https://www.youtube.com/watch?v=..."
```

**Add a new download strategy:**
Edit `ytp3/core/strategies.py`:
```python
STRATEGIES = [
    # ... existing strategies ...
    {
        "name": "My Strategy",
        "description": "My description",
        "extra": {'custom_option': value}
    }
]
```

**Integrate core engine elsewhere:**
```python
from ytp3.core.engine import YTP3Engine

engine = YTP3Engine(options, capabilities)
metadata = engine.resolve_metadata(url)
engine.download_single_item(url, progress_callback)
```

**Check system health:**
```python
from ytp3.utils.system import SystemDoctor

doctor = SystemDoctor()
report = doctor.run_diagnostics(".")
print(report)
```

## Dependencies

**Core:**
- yt-dlp - Video downloading
- requests - HTTP requests

**GUI:**
- customtkinter - Modern UI
- Pillow - Image processing

**Optional:**
- FFmpeg - Video/audio processing
- Node.js or Deno - JavaScript runtime

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "FFmpeg not found" | Install FFmpeg, add to PATH |
| Import errors | Run `pip install -r requirements.txt` |
| GUI won't start | Check customtkinter: `pip install customtkinter --upgrade` |
| Download fails | Check System Health, try different strategy |

## Next Steps

1. Read [README.md](README.md) for full documentation
2. Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
3. See [DEVELOPMENT.md](DEVELOPMENT.md) for architecture details
4. Use [INDEX.md](INDEX.md) for documentation navigation

---

**Need Help?**
- Check documentation files
- Open an issue on GitHub
- See troubleshooting section
