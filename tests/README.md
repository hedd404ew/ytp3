# YTP3 Test Suite

This directory contains comprehensive tests for the YTP3 downloader application.

## Installation

To run tests, first install the test dependencies:

```bash
pip install pytest pytest-cov
```

## Running Tests

### All Tests
```bash
python -m pytest tests/ -v
```

### Specific Test Module
```bash
# Test the engine
python -m pytest tests/test_core/test_engine.py -v

# Test strategies
python -m pytest tests/test_core/test_strategies.py -v

# Test configuration
python -m pytest tests/test_utils/test_config.py -v

# Test system utilities
python -m pytest tests/test_utils/test_system.py -v

# Test CLI
python -m pytest tests/test_cli.py -v

# Test UI components
python -m pytest tests/test_ui/test_components.py -v
```

### Specific Test
```bash
python -m pytest tests/test_core/test_engine.py::TestYTP3EngineInitialization::test_engine_init_basic -v
```

### Coverage Report
```bash
# Generate coverage report
python -m pytest tests/ --cov=ytp3 --cov-report=html

# View HTML report
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

## Test Structure

### `test_core/`
Tests for the core download engine and strategies:
- **test_engine.py** - Engine initialization, format fallbacks, logging, error tracking
- **test_strategies.py** - Strategy retrieval, validation, configuration

### `test_utils/`
Tests for utility modules:
- **test_config.py** - Configuration management (save/load roundtrips)
- **test_system.py** - System diagnostics and path management

### `test_ui/`
Tests for UI components:
- **test_components.py** - UI component structure and imports

### `test_cli.py`
Tests for CLI interface:
- Argument parser functionality
- All CLI flags and options
- Default values

## Test Categories

### Unit Tests
Tests for individual components in isolation.

```bash
python -m pytest tests/ -m unit -v
```

### Integration Tests
Tests that verify components work together.

```bash
python -m pytest tests/ -m integration -v
```

### Headless-Safe Tests
Tests that don't require a graphical display (suitable for CI/CD).

```bash
python -m pytest tests/ -m headless -v
```

## Fixtures

Shared test fixtures are defined in `conftest.py`:

- **temp_dir** - Provides a temporary directory for file operations
- **sample_opts** - Sample yt-dlp options dictionary
- **sample_caps** - Sample system capabilities dictionary
- **sample_config** - Sample configuration dictionary

## Coverage Goals

Current test coverage targets:
- ✅ Core engine: Format selection, initialization, logging
- ✅ Strategies: Retrieval, validation, compatibility
- ✅ Configuration: Save/load, data type preservation
- ✅ System: Diagnostics, path management
- ✅ CLI: Argument parsing, all options
- ✅ Error handling: Audio extraction, rate limiting, authentication

## CI/CD Integration

For continuous integration, use:

```bash
# Run tests with coverage in CI environment
python -m pytest tests/ --cov=ytp3 --cov-report=xml --cov-report=term

# Exit with error if coverage drops below threshold
python -m pytest tests/ --cov=ytp3 --cov-fail-under=70
```

## Known Limitations

### UI Testing
UI tests on headless systems (CI/CD) may be skipped due to missing display server. These tests are marked with `@pytest.mark.skip` in such cases.

### Network-Dependent Tests
Tests that require actual YouTube data extraction are not included (would require mocking large amounts of yt-dlp behavior). Instead, we focus on:
- Configuration and engine initialization
- Format fallback logic
- Error handling paths

## Contributing Tests

When adding new features:

1. Write tests first (TDD approach)
2. Place tests in appropriate subdirectory under `tests/`
3. Follow naming convention: `test_*.py`
4. Use descriptive test method names
5. Add docstrings to test classes and methods
6. Use fixtures from `conftest.py`

Example test:

```python
def test_new_feature(self, sample_opts, sample_caps):
    """Test that feature X works correctly."""
    engine = YTP3Engine(sample_opts, sample_caps)
    
    result = engine.some_new_method()
    
    assert result == expected_value
```

## Troubleshooting

### Import Errors
If you see import errors when running tests, ensure:
1. You've installed YTP3 in development mode: `pip install -e .`
2. Or add the project root to PYTHONPATH: `export PYTHONPATH=$(pwd):$PYTHONPATH`

### Display Server Errors
On headless systems, UI tests will be skipped automatically. This is expected.

### ConfigManager Errors
Ensure temp directories have write permissions for config file tests.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `pytest tests/` | Run all tests |
| `pytest tests/ -v` | Run all tests with verbose output |
| `pytest tests/test_core/` | Run only core tests |
| `pytest tests/ -k test_engine` | Run tests matching "test_engine" |
| `pytest tests/ --cov=ytp3` | Run with coverage report |
| `pytest tests/ -x` | Stop on first failure |
| `pytest tests/ -s` | Show print statements |
| `pytest tests/ --tb=short` | Short traceback format |
