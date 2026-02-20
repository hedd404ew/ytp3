"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_opts():
    """Provide sample yt-dlp options for testing."""
    return {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'test_%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }


@pytest.fixture
def sample_caps():
    """Provide sample system capabilities for testing."""
    return {
        'ffmpeg': True,
        'ffprobe': True,
        'js_runtime': False,
        'internet': True,
    }


@pytest.fixture
def sample_config():
    """Provide sample configuration dictionary."""
    return {
        'save_path': '/tmp/ytp3_test',
        'mode': 'Video',
        'format': 'mp4',
        'resolution': 'Best Available',
        'quality': 'best',
        'concurrency': 2,
        'toggles': {
            'meta': True,
            'thumb': False,
            'subs': False,
            'sponsor': False,
            'geo': False,
            'force_ffmpeg': False,
            'archive': False,
        },
        'auth': {
            'browser': 'None',
            'file': '',
        },
        'last_urls': '',
        'browser_cookies': 'None',
        'cookie_file': '',
    }
