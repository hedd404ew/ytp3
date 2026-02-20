# YTP3 Testing Guide

Comprehensive testing suite for YTP3 downloader.

## Quick Start

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=ytp3 --cov-report=html
```

## Test Suite Overview

YTP3 includes **60+ tests** covering:
- ✅ Core engine functionality (format fallbacks, initialization, logging)
- ✅ Download strategies (retrieval, validation, compatibility)
- ✅ Configuration management (save/load, data persistence)
- ✅ System utilities (diagnostics, path management)
- ✅ CLI interface (argument parsing, all flags)
- ✅ Error handling (audio extraction, rate limiting, auth)
- ✅ UI components (imports, structure)

## Test Structure

```
tests/
├── conftest.py                    # Pytest fixtures and configuration
├── pytest.ini                     # Pytest settings
├── README.md                      # Detailed testing documentation
│
├── test_core/                     # Engine and strategy tests
│   ├── test_engine.py            # Engine initialization, format fallbacks, logging
│   └── test_strategies.py        # Strategy retrieval and validation
│
├── test_utils/                    # Utility module tests
│   ├── test_config.py            # Configuration save/load
│   └── test_system.py            # System diagnostics
│
├── test_ui/                       # UI component tests
│   └── test_components.py        # UI component imports and structure
│
└── test_cli.py                    # CLI argument parsing
```

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Specific Test Module
```bash
pytest tests/test_core/test_engine.py -v
pytest tests/test_utils/test_config.py -v
pytest tests/test_cli.py -v
```

### Specific Test Class
```bash
pytest tests/test_core/test_engine.py::TestYTP3EngineInitialization -v
```

### Specific Test
```bash
pytest tests/test_core/test_engine.py::TestYTP3EngineInitialization::test_engine_init_basic -v
```

### Coverage Report
```bash
# Generate and save HTML coverage report
pytest tests/ --cov=ytp3 --cov-report=html

# View the report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Parallel Execution
```bash
# Run tests in parallel (faster)
pytest tests/ -n auto
```

### Stop on First Failure
```bash
pytest tests/ -x
```

## Test Categories

### Unit Tests
Isolated tests for individual components:
```bash
pytest tests/ -m unit -v
```

### Headless-Safe Tests
Tests suitable for CI/CD (no display required):
```bash
pytest tests/ -m headless -v
```

## Fixtures

Common fixtures defined in `conftest.py`:

| Fixture | Purpose |
|---------|---------|
| `temp_dir` | Temporary directory for file operations |
| `sample_opts` | Sample yt-dlp options dictionary |
| `sample_caps` | Sample system capabilities |
| `sample_config` | Sample configuration dictionary |

## Key Test Areas

### 1. Engine Tests (`test_core/test_engine.py`)

**Initialization**:
- Engine creation with/without callbacks
- Configuration handling
- Strategy availability

**Format Fallbacks**:
- 5-layer degradation for each quality level
- Fallback format structure validation
- Layer-specific format selection

**Logging**:
- Callback-based logging
- stdout printing without callback
- Error tracking

**Sample Test**:
```python
def test_engine_init_basic(self, sample_opts, sample_caps):
    """Test basic engine initialization."""
    engine = YTP3Engine(sample_opts, sample_caps)
    
    assert engine.opts == sample_opts
    assert engine.caps == sample_caps
    assert engine.log_cb is None
```

### 2. Strategy Tests (`test_core/test_strategies.py`)

**Strategy Retrieval**:
- All strategies available
- Required fields present
- Unique strategy names

**Configuration**:
- Extra options dictionary structure
- Engine compatibility

**Sample Test**:
```python
def test_get_all_strategies(self):
    """Test that all strategies are retrieved."""
    strategies = DownloadStrategy.get_all()
    
    assert len(strategies) > 0
    assert isinstance(strategies, list)
```

### 3. Configuration Tests (`test_utils/test_config.py`)

**Persistence**:
- Save configuration to file
- Load configuration from file
- Save/load roundtrips

**Data Types**:
- String, integer, float, boolean preservation
- Nested dictionaries and lists
- Null value handling

**Sample Test**:
```python
def test_config_roundtrip(self, temp_dir, sample_config):
    """Test save and load roundtrip."""
    config_file = os.path.join(temp_dir, 'test_config.json')
    
    # Save
    config1 = ConfigManager(config_file)
    config1.data = sample_config
    config1.save()
    
    # Load and verify
    config2 = ConfigManager(config_file)
    assert config2.load() == sample_config
```

### 4. System Tests (`test_utils/test_system.py`)

**Diagnostics**:
- Capability detection
- Missing critical components
- Path management

**Platform Support**:
- Platform-appropriate paths
- Default path generation

### 5. CLI Tests (`test_cli.py`)

**Argument Parsing**:
- URL argument handling
- All options: `-a`, `-f`, `-q`, `-o`
- Flags: `--no-meta`, `--geo`, `--subs`
- Authentication: `--cookies-browser`, `--cookies-file`

**Default Values**:
- Quality: `best`
- Audio mode: `False`
- Metadata: embedded by default

**Sample Test**:
```python
def test_parser_multiple_options(self):
    """Test parsing multiple options together."""
    parser = setup_parser()
    args = parser.parse_args([
        '-a', '-f', 'm4a', '-q', 'medium', 
        '--no-meta', '--geo',
        'https://www.youtube.com/watch?v=test123'
    ])
    
    assert args.audio is True
    assert args.format == 'm4a'
    assert args.quality == 'medium'
```

## Continuous Integration

For CI/CD pipelines:

```bash
# Run tests with XML coverage for CI systems
pytest tests/ \
  --cov=ytp3 \
  --cov-report=xml \
  --cov-report=term \
  --junitxml=test-results.xml
```

## Coverage Goals

Current coverage targets:
- Engine: 95%
- Strategies: 100%
- CLI: 95%
- Utils: 90%
- Overall: 90%+

## Troubleshooting

### Import Errors
```bash
# Install in development mode
pip install -e .
```

### Display Server Errors
UI tests on headless systems (CI/CD) are automatically skipped.

### File Permission Errors
Ensure temp directory has write permissions:
```bash
chmod 777 /tmp
```

## Contributing Tests

When adding features:

1. **Write tests first** (TDD approach)
2. **Use appropriate fixtures** from `conftest.py`
3. **Follow naming**: `test_<feature>.py`
4. **Add docstrings**: Describe what's being tested
5. **Use assertions**: Clear, specific assertions

Example:
```python
def test_new_feature(self, sample_opts, sample_caps):
    """Test that feature X works correctly."""
    engine = YTP3Engine(sample_opts, sample_caps)
    
    result = engine.new_method()
    
    assert result is not None
    assert isinstance(result, dict)
```

## Performance Testing

### Profiling
```bash
# Run tests with timing
pytest tests/ -v --durations=10
```

### Slow Tests
```bash
# Mark and run only slow tests
pytest tests/ -m slow -v
```

## Resources

- **pytest docs**: https://docs.pytest.org/
- **pytest-cov docs**: https://pytest-cov.readthedocs.io/
- **Coverage.py**: https://coverage.readthedocs.io/
- **Detailed testing guide**: [tests/README.md](tests/README.md)

## Quick Reference

| Command | Purpose |
|---------|---------|
| `pytest tests/` | Run all tests |
| `pytest tests/ -v` | Verbose output |
| `pytest tests/ --cov=ytp3` | With coverage |
| `pytest tests/ -x` | Stop on first failure |
| `pytest tests/ -s` | Show print statements |
| `pytest tests/ -k test_engine` | Run matching tests |
| `pytest tests/ --tb=short` | Short traceback format |
