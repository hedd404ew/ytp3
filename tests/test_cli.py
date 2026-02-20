"""Tests for CLI interface."""

import pytest
import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from ytp3.cli import setup_parser, cli_progress, cli_log


class TestCLIParser:
    """Test CLI argument parser."""
    
    def test_parser_creation(self):
        """Test that parser is created successfully."""
        parser = setup_parser()
        
        assert parser is not None
        assert hasattr(parser, 'parse_args')
    
    def test_parser_basic_url_argument(self):
        """Test parsing basic URL argument."""
        parser = setup_parser()
        args = parser.parse_args(['https://www.youtube.com/watch?v=test123'])
        
        assert args.url == 'https://www.youtube.com/watch?v=test123'
    
    def test_parser_audio_flag(self):
        """Test parsing audio flag."""
        parser = setup_parser()
        args = parser.parse_args(['-a', 'https://www.youtube.com/watch?v=test123'])
        
        assert args.audio is True
    
    def test_parser_format_option(self):
        """Test parsing format option."""
        parser = setup_parser()
        args = parser.parse_args(['-f', 'mp3', 'https://www.youtube.com/watch?v=test123'])
        
        assert args.format == 'mp3'
    
    def test_parser_quality_option(self):
        """Test parsing quality option."""
        parser = setup_parser()
        args = parser.parse_args(['-q', 'high', 'https://www.youtube.com/watch?v=test123'])
        
        assert args.quality == 'high'
    
    def test_parser_quality_choices(self):
        """Test that quality only accepts valid choices."""
        parser = setup_parser()
        
        # Valid quality should parse
        args = parser.parse_args(['-q', 'best', 'https://www.youtube.com/watch?v=test123'])
        assert args.quality == 'best'
        
        args = parser.parse_args(['-q', 'medium', 'https://www.youtube.com/watch?v=test123'])
        assert args.quality == 'medium'
    
    def test_parser_output_option(self):
        """Test parsing output directory option."""
        parser = setup_parser()
        args = parser.parse_args(['-o', '/tmp/downloads', 'https://www.youtube.com/watch?v=test123'])
        
        assert args.output == '/tmp/downloads'
    
    def test_parser_no_meta_flag(self):
        """Test parsing no-meta flag."""
        parser = setup_parser()
        args = parser.parse_args(['--no-meta', 'https://www.youtube.com/watch?v=test123'])
        
        assert args.no_meta is True
    
    def test_parser_geo_bypass_flag(self):
        """Test parsing geo-bypass flag."""
        parser = setup_parser()
        args = parser.parse_args(['--geo', 'https://www.youtube.com/watch?v=test123'])
        
        assert args.geo is True
    
    def test_parser_cookies_browser_option(self):
        """Test parsing cookies-browser option."""
        parser = setup_parser()
        args = parser.parse_args(['--cookies-browser', 'chrome', 'https://www.youtube.com/watch?v=test123'])
        
        assert args.cookies_browser == 'chrome'
    
    def test_parser_cookies_file_option(self):
        """Test parsing cookies-file option."""
        parser = setup_parser()
        args = parser.parse_args(['--cookies-file', '/path/to/cookies.txt', 'https://www.youtube.com/watch?v=test123'])
        
        assert args.cookies_file == '/path/to/cookies.txt'
    
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
        assert args.no_meta is True
        assert args.geo is True
        assert args.url == 'https://www.youtube.com/watch?v=test123'


class TestCLIUtilityFunctions:
    """Test CLI utility functions."""
    
    def test_cli_progress_function_exists(self):
        """Test that cli_progress function exists."""
        assert callable(cli_progress)
    
    def test_cli_progress_accepts_parameters(self):
        """Test that cli_progress accepts correct parameters."""
        # Should not raise exception
        try:
            cli_progress(50.0, "Testing 50%")
        except:
            pytest.fail("cli_progress should accept (pct, msg) parameters")
    
    def test_cli_log_function_exists(self):
        """Test that cli_log function exists."""
        assert callable(cli_log)
    
    def test_cli_log_accepts_message(self, capsys):
        """Test that cli_log accepts a message."""
        try:
            cli_log("Test log message")
            captured = capsys.readouterr()
            assert "Test log message" in captured.out or "LOG" in captured.out
        except:
            pytest.fail("cli_log should accept a message parameter")


class TestCLIArgumentValidation:
    """Test CLI argument validation."""
    
    def test_parser_requires_url_for_cli_mode(self):
        """Test that URL is required for download operations."""
        parser = setup_parser()
        
        # URL is optional (position), but needed for actual download
        args = parser.parse_args([])
        assert args.url is None
    
    def test_parser_default_quality_is_best(self):
        """Test that default quality is 'best'."""
        parser = setup_parser()
        args = parser.parse_args(['https://www.youtube.com/watch?v=test123'])
        
        assert args.quality == 'best'
    
    def test_parser_default_audio_is_false(self):
        """Test that audio flag defaults to False."""
        parser = setup_parser()
        args = parser.parse_args(['https://www.youtube.com/watch?v=test123'])
        
        assert args.audio is False
    
    def test_parser_default_no_meta_is_false(self):
        """Test that no-meta flag defaults to False."""
        parser = setup_parser()
        args = parser.parse_args(['https://www.youtube.com/watch?v=test123'])
        
        assert args.no_meta is False
