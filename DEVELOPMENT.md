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

## Future Improvements

- [ ] Plugin system for custom strategies
- [ ] Database for download history
- [ ] Scheduled downloads
- [ ] Batch processing templates
- [ ] Advanced filtering/search
- [ ] Network proxy support
- [ ] Database-backed configuration
