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

Create tests in `tests/` following naming convention. YTP3 uses **pytest** for the comprehensive test suite.

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test module
pytest tests/test_core/test_engine.py -v

# Run with coverage report
pytest tests/ --cov=ytp3 --cov-report=html
```

### Example Test

```python
import pytest
from ytp3.core.engine import YTP3Engine

def test_strategy_retrieval(self, sample_opts, sample_caps):
    """Test that engine has strategies available."""
    engine = YTP3Engine(sample_opts, sample_caps)
    
    assert len(engine.strategies) > 0
    assert all('name' in s and 'extra' in s for s in engine.strategies)
```

For detailed testing documentation and running instructions, see [tests/README.md](tests/README.md).

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

**5-Layer Degradation Fallback System**:

The engine uses a comprehensive fallback strategy with 5 layers:

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

### Issue: Audio extraction fails (exit code -22)

**Root Cause**: FFmpeg audio codec incompatibility or missing codec libraries.

**Error Messages**:
```
ERROR: Post-processing failed: exit code -22
ERROR: audio conversion failed: Exiting with exit code -22
```

**Solutions**:

1. **Check FFmpeg Audio Codecs**:
   ```bash
   ffmpeg -codecs | grep -E "libmp3lame|aac|opus|vorbis"
   ```

2. **Use Alternative Audio Format**:
   - Try WAV format (uncompressed, no codec issues)
   - Use M4A instead of MP3
   - Use OPUS or VORBIS if available

3. **Verify FFmpeg Installation**:
   ```bash
   ffmpeg -version
   ffmpeg -decoders | grep audio
   ```

4. **Try Quality Selection**:
   ```bash
   python ytp3_main.py -a -f wav "URL"
   python ytp3_main.py -a -f m4a "URL"
   ```

### Issue: Metadata embedding failures

**Root Cause**: FFmpeg or mutagen fails to write metadata to video file.

**Error Messages**:
```
[Metadata] Adding metadata failed with error: ...
ERROR: Post-processing failed
```

**Solutions**:

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

**Solutions**:

1. **Install Deno** (Recommended):
   ```bash
   # Windows (with chocolatey)
   choco install deno
   
   # Or download from https://deno.land
   ```

2. **Use Fallback Strategies**:
   - Use Android/iOS bypass strategies which may avoid challenges
   - Warnings don't prevent download in most cases

3. **Accept and Continue**: 
   - Downloads usually still work despite warnings
   - Focus on alternative strategies if needed

## Edge Cases & Exceptional Scenarios

Certain combinations of download options can create processing conflicts. This table documents all known edge cases and their resolutions:

| Mode | With Sponsor Block | With Subtitles | With Metadata | Issue | Resolution |
|------|-------------------|----------------|---------------|-------|-----------|
| **Audio Only** | ❌ Disabled | ✅ Allowed | ✅ Allowed | Sponsor Block is visual-only; conflicts with audio extraction | Auto-disables Sponsor Block in audio mode |
| **Audio + SponsorBlock** | ❌ Force Skip | ✅ Allowed | ✅ Allowed | Audio extraction + SponsorBlock merging confusion | Audio mode ignores SponsorBlock setting; recommend video mode if segment removal needed |
| **Video Only** | ✅ Allowed | ✅ Allowed | ✅ Allowed | Video merging (video+audio) with SponsorBlock works correctly | No special handling needed |
| **Video + SponsorBlock** | ✅ Allowed | ✅ Allowed | ✅ Allowed | SponsorBlock removes segments, then merges audio | Processing order: SponsorBlock → Merge Streams → Metadata |
| **SponsorBlock Only** | ✅ Default | ✅ Allowed | ✅ Allowed | Requires video mode to identify visual segments | Recommended: Use Video mode for best results |

### Edge Case Details

#### Audio Mode + SponsorBlock
- **Problem**: SponsorBlock is designed to remove *visual* sponsor segments in videos. In audio-only mode, there's no video stream to process, and FFmpeg merging fails.
- **Error**: `ERROR: audio conversion failed: Exiting with exit code -22`
- **Implementation**: Audio mode **automatically disables** SponsorBlock even if user enables it
- **User Impact**: Users won't see SponsorBlock checkbox effect in audio mode
- **Recommendation**: For sponsor removal during audio extraction, use Video mode first, then extract audio

#### Video Mode + High Quality + SponsorBlock
- **Problem**: Large files with SponsorBlock can take longer due to segment removal processing
- **Mitigation**: Processing happens sequentially: SponsorBlock → Merge → Postprocessing
- **User Impact**: Minor latency increase (typically <5% slower)

#### Multiple Postprocessor Chains
- **Problem**: Metadata embedding + SponsorBlock + Audio extraction in sequence can conflict
- **Implementation**: Postprocessors are chained in correct order:
  1. SponsorBlock removal (if video mode)
  2. Format merging (if multi-stream)
  3. Audio extraction (if audio mode)
  4. Metadata embedding (if enabled)
- **User Impact**: Each stage must complete successfully; failures will skip affected postprocessor only

## Comprehensive Error Handling

### Error Detection & Recovery

The engine now:
- ✅ Detects FFmpeg exit codes (e.g., -22)
- ✅ Catches postprocessor failures (metadata, audio extraction)
- ✅ Automatically retries with fallback formats
- ✅ Continues download even if postprocessing fails
- ✅ Tracks all errors in detailed logs
- ✅ Supports multiple audio codec fallbacks (MP3, WAV, M4A, OPUS, VORBIS)

### Log Output Examples

**Successful download with fallback**:
```
[ATTEMPT 1] L1: Best quality with merged audio
[YT-DLP] Downloading with format: bestvideo[ext=mp4]+bestaudio[ext=m4a]
[DOWNLOADING] 2.5MB/s | ETA: 2:30
[SUCCESS] Download completed
```

**Audio extraction with fallback**:
```
[AUDIO] Attempting MP3 extraction
[WARNING] MP3 extraction failed, trying WAV
[SUCCESS] Audio extracted as WAV
```

**Failed attempt, retrying**:
```
[ATTEMPT 1] L1: Best quality with merged audio
[FAILED L1] Standard: Format not available
[ATTEMPT 2] L2: Auto-select best video+audio
[SUCCESS] Download completed with Standard strategy, format L2
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_core/test_engine.py -v

# Run with coverage report
python -m pytest tests/ --cov=ytp3 --cov-report=html
```

### Test Structure

```
tests/
├── test_core/
│   ├── __init__.py
│   ├── test_engine.py        # Engine initialization and format fallback tests
│   └── test_strategies.py    # Strategy retrieval and validation tests
├── test_ui/
│   ├── __init__.py
│   └── test_components.py    # UI component tests
├── test_utils/
│   ├── __init__.py
│   ├── test_config.py        # Configuration management tests
│   └── test_system.py        # System diagnostics tests
├── test_cli.py               # CLI argument parsing and execution tests
└── conftest.py               # Pytest configuration and fixtures
```

### Test Coverage

The test suite covers:
- ✅ Engine initialization with various configurations
- ✅ Format fallback strategy selection and ordering
- ✅ Strategy retrieval and validation
- ✅ Configuration loading and saving
- ✅ System capability detection
- ✅ CLI argument parsing
- ✅ Error handling and recovery paths

## Architecture & Dependencies

### Design Philosophy

YTP3 is built around **yt-dlp as a base library**, not as a forked project. This means:

1. **External Dependency**: yt-dlp is used as-is from PyPI
2. **No Modifications**: We don't fork or modify yt-dlp source code
3. **Abstraction Layer**: Our engine wraps yt-dlp with:
   - Fallback strategies for format selection
   - Error recovery mechanisms
   - Custom postprocessor handling
   - Comprehensive logging and progress tracking

### Why Depend on yt-dlp?

yt-dlp provides:
- ✅ Robust YouTube data extraction and format detection
- ✅ Extensive format filtering and selection
- ✅ Multiple bypass strategies (Android, iOS, TV clients)
- ✅ FFmpeg integration for postprocessing
- ✅ Cookie and authentication handling
- ✅ Subtitle downloading and embedding
- ✅ Metadata extraction and embedding

Our role is to provide:
- ✅ Smart format fallback when extraction fails
- ✅ User-friendly GUI and CLI interfaces
- ✅ Configuration management across platforms
- ✅ Enhanced error messages and recovery suggestions
- ✅ Multi-threaded download management

### Feature Dependency on yt-dlp

Many features depend directly on yt-dlp's capabilities:

| Feature | How It Works | Status |
|---------|-------------|--------|
| Custom proxy support | Passed to yt-dlp via options | Already supported |
| Subtitle language selection | yt-dlp `--sub-langs` option | Already supported |
| Cookie handling | yt-dlp authentication features | Already supported |
| Format selection | yt-dlp format filtering | Already supported |
| Metadata embedding | yt-dlp postprocessors | Already supported |

**Note**: Most advanced features should leverage yt-dlp's configuration options passed through our configuration system, rather than implementing custom code in YTP3.

