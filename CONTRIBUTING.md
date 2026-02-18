# Contributing to YTP3Downloader

Thank you for your interest in contributing! This document provides guidelines for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. Check if the issue already exists
2. Include Python version and OS
3. Provide reproduction steps
4. Attach relevant error messages or logs

### Suggesting Features

1. Check if feature is already planned
2. Clearly describe the use case
3. Explain expected behavior
4. Provide examples if possible

### Submitting Code

1. Fork the repository
2. Create a feature branch
3. Follow code style guidelines
4. Add tests for new functionality
5. Submit a pull request with clear description

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and modular

## Development Setup

```bash
git clone <your-fork>
cd ytp3downloader
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

## Testing

```bash
python -m pytest tests/
python -m pytest tests/ -v  # Verbose
```

## Project Structure Guidelines

- `ytp3/core/` - Download engine logic
- `ytp3/ui/` - GUI components
- `ytp3/utils/` - Utilities and helpers
- `tests/` - Unit tests

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add new feature description
fix: Fix specific bug
docs: Update documentation
refactor: Improve code structure
test: Add or update tests
```

## Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

## Questions?

Feel free to open a discussion or issue for questions!
