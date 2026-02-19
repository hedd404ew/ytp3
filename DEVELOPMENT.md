# YTP3 Development

## Architecture Overview

The refactored YTP3 follows a modular, layered architecture:

### Core Layer (`ytp3/core/`)

Handles all download operations:
- **engine.py** - Main download engine with fallback strategies
- **strategies.py** - Strategy definitions for bypassing restrictions

### UI Layer (`ytp3/ui/`)

Provides user interfaces:
- **app.py** - Main GUI application (customtkinter-based)
- **components.py** - Reusable UI components

### Utilities Layer (`ytp3/utils/`)

System-level utilities:
- **system.py** - Configuration, diagnostics, path management
- **config.py** - Configuration management exports

### CLI (`ytp3/cli.py`)

Command-line interface independent of GUI.

## Key Design Decisions

### 1. Separation of Concerns

- Core logic is completely independent of UI
- UI components can be replaced without affecting core
- Utilities are reusable across both interfaces

### 2. Strategy Pattern

Download strategies encapsulate different retry approaches, allowing:
- Easy addition of new strategies
- Fallback on failure
- Testing individual strategies

### 3. Configuration Management

Centralized configuration with:
- Auto-detection of config location
- Portable mode support
- Sensible defaults

### 4. Error Handling

- Custom error types for specific failures
- Graceful degradation
- Comprehensive logging

## Adding New Features

### Adding a Download Strategy

1. Add to `DownloadStrategy.STRATEGIES` in `strategies.py`
2. Engine automatically iterates and tries each

### Adding UI Components

1. Create component in `components.py`
2. Import and use in `app.py`
3. Follow customtkinter conventions

### Adding Utilities

1. Create new module in `utils/`
2. Export from `utils/__init__.py`
3. Import from main package

## Testing

Create tests in `tests/` following naming convention:
```
tests/
├── test_core/
│   ├── test_engine.py
│   └── test_strategies.py
├── test_ui/
│   └── test_components.py
└── test_utils/
    └── test_config.py
```

Example test:
```python
import unittest
from ytp3.core.engine import YTP3Engine

class TestYTP3Engine(unittest.TestCase):
    def setUp(self):
        self.engine = YTP3Engine({}, {})
    
    def test_strategy_retrieval(self):
        strategies = self.engine.strategies
        self.assertGreater(len(strategies), 0)
```

## Performance Considerations

### Threading

- Image loading uses ThreadPoolExecutor (4 workers default)
- Downloads use configurable thread pool
- UI remains responsive during operations

### Memory

- Thumbnail loading async to prevent blocking
- Streaming downloads (not in-memory)
- Efficient metadata caching

## Troubleshooting

### Issue: Downloaded videos have no audio

**Root Cause**: When yt-dlp selects `bestvideo+bestaudio`, separate video and audio streams need to be merged using FFmpeg. Without proper postprocessor configuration, videos may contain only the video stream.

**5-Layer Degradation Fallback System** (v1.2+):

The engine now uses a comprehensive fallback strategy with 5 layers:

1. **Layer 1**: `bestvideo[ext=mp4]+bestaudio[ext=m4a]` - Prefer containerized formats
2. **Layer 2**: `bestvideo+bestaudio/best` - Auto-select and merge
3. **Layer 3**: `bestvideo[height<=1080]+bestaudio` - Quality-limited selection
4. **Layer 4**: `best[ext=mp4]` - Single format fallback
5. **Layer 5**: `best` - Absolute fallback to any available

Each format is tried with each download strategy (Standard, Android, iOS, TV bypass):
- **Total attempts**: Up to 20 different format/strategy combinations
- **Automatic downgrade**: If a format fails, engine tries next fallback
- **Detailed logging**: Comprehensive error messages show which attempt failed and why

**Solutions**:

1. **Enable Comprehensive Logging** (see logs):
   ```bash
   # GUI: Check Log tab for [ATTEMPT X] messages
   # CLI: Look for [ATTEMPT], [STRATEGY], [FORMAT] logs
   ```

2. **Quality Selection** (may find combined streams):
   ```bash
   python ytp3_main.py -q medium "URL"
   ```

3. **Verify FFmpeg Installation**:
   ```bash
   ffmpeg -version
   ffmpeg -codecs | grep aac
   ```

### Issue: Thumbnail embedding fails (exit code -22)

**Root Cause** (Fixed in v1.3): FFmpeg and mutagen consistently fail to embed webp thumbnails in mp4 containers due to format compatibility issues.

**Previous Error Messages**:
```
ERROR: Unable to embed using ffprobe & ffmpeg; Exiting with exit code -22
WARNING: unable to embed using mutagen; incompatible image type: webp
```

**Solution Implemented** (v1.3+):

Thumbnail embedding has been **disabled completely** to eliminate this source of download failures. This decision was made because:

1. **Root cause is fundamental**: webp→mp4 embedding fails across FFmpeg versions
2. **Workarounds cause complexity**: thumbnail conversion added significant code without solving the core issue
3. **Videos are usable without thumbnails**: Core functionality (video+audio) works perfectly
4. **Focus on reliability**: Downloads succeed reliably even if thumbnails are skipped

**New Behavior**:
- All downloads embed metadata (title, description, duration, artist, etc.)
- Thumbnail embedding is entirely skipped
- Videos always contain proper audio+video merged streams
- No more `exit code -22` or mutagen compatibility errors

**If you previously needed thumbnails**:
- You can extract them separately using FFmpeg after download
- Most video players (VLC, Windows Media Player, etc.) don't display embedded thumbnails anyway
- The focus is now on download reliability over metadata richness

### Issue: Metadata embedding failures

**Root Cause**: FFmpeg or mutagen fails to write metadata to video file.

**Error Messages**:
```
[Metadata] Adding metadata failed with error: ...
ERROR: Post-processing failed
```

**Solutions** (v1.2+):

1. **Automatic Retry** (Enabled by default):
   - If metadata embedding fails, video is still usable
   - Download succeeds with or without metadata

2. **Disable Metadata Embedding**:
   ```bash
   # CLI
   python ytp3_main.py --no-meta "URL"
   
   # GUI: Uncheck "Embed Metadata" checkbox
   ```

3. **Check FFmpeg Metadata Support**:
   ```bash
   ffmpeg -version | grep -i metadata
   ```

### Issue: "n challenge solving failed" warnings

**Root Cause**: YouTube has JavaScript challenges that require deno/Node.js to solve.

**Warnings**:
```
WARNING: [youtube] [jsc] Remote components challenge solver script (deno)...
WARNING: [youtube] [...]: n challenge solving failed: Some formats may be missing...
```

**Solutions** (v1.2+):

1. **Install Deno** (Recommended):
   ```bash
   # Windows (with chocolatey)
   choco install deno
   
   # Or download from https://deno.land
   ```

2. **Use CLI Option** (if deno installed):
   ```bash
   python ytp3_main.py --remote-components ejs:github "URL"
   ```

3. **Ignore Warnings**: 
   - Downloads usually still work despite warnings
   - Use fallback strategies (Android, iOS) which may avoid challenges
   - Warnings don't prevent download

## Comprehensive Error Handling (v1.2+)

### Error Detection & Recovery

The engine now:
- ✅ Detects FFmpeg exit codes (e.g., -22)
- ✅ Catches postprocessor failures (metadata, thumbnail)
- ✅ Automatically retries without failing postprocessors
- ✅ Converts webp/png thumbnails to jpg
- ✅ Continues download even if metadata fails
- ✅ Tracks all errors in detailed logs

### Log Output Examples

**Successful with postprocessor fallback**:
```
[ATTEMPT 1] L1: Best quality with merged audio
[YT-DLP] Downloading with format: bestvideo[ext=mp4]+bestaudio[ext=m4a]
[DOWNLOADING] 2.5MB/s | ETA: 2:30
[WARNING] Postprocessor error detected: exit code -22
[RETRY] Attempting download without problematic postprocessors...
[SUCCESS] Download completed (without thumbnails/metadata)
```

**Failed attempt, retrying**:
```
[ATTEMPT 1] L1: Best quality with merged audio
[FAILED L1] Standard: Format not available
[ATTEMPT 2] L2: Auto-select best video+audio
[SUCCESS] Download completed with Standard strategy, format L2
```

## Future Improvements

- [ ] Plugin system for custom strategies
- [ ] Database for download history
- [ ] Scheduled downloads
- [ ] Batch processing templates
- [ ] Advanced filtering/search
- [ ] Network proxy support
- [ ] Database-backed configuration
- [ ] Custom retry configuration UI
- [ ] Download speed optimization
- [ ] Subtitle language selection
