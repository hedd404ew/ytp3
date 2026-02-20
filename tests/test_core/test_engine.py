"""Tests for YTP3Engine class."""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ytp3.core.engine import YTP3Engine


class TestYTP3EngineInitialization:
    """Test engine initialization and configuration."""
    
    def test_engine_init_basic(self, sample_opts, sample_caps):
        """Test basic engine initialization."""
        engine = YTP3Engine(sample_opts, sample_caps)
        
        assert engine.opts == sample_opts
        assert engine.caps == sample_caps
        assert engine.log_cb is None
        assert engine.last_detailed_error == ""
    
    def test_engine_init_with_callback(self, sample_opts, sample_caps):
        """Test engine initialization with log callback."""
        def dummy_callback(msg):
            pass
        
        engine = YTP3Engine(sample_opts, sample_caps, log_callback=dummy_callback)
        
        assert engine.log_cb == dummy_callback
        assert engine.last_detailed_error == ""
    
    def test_engine_strategies_available(self, sample_opts, sample_caps):
        """Test that engine has strategies available."""
        engine = YTP3Engine(sample_opts, sample_caps)
        
        assert len(engine.strategies) > 0
        assert all('name' in s and 'extra' in s for s in engine.strategies)
    
    def test_format_fallbacks_structure(self, sample_opts, sample_caps):
        """Test format fallbacks are properly structured."""
        engine = YTP3Engine(sample_opts, sample_caps)
        
        assert 'best' in engine.FORMAT_FALLBACKS
        assert 'high' in engine.FORMAT_FALLBACKS
        assert 'medium' in engine.FORMAT_FALLBACKS
        assert 'low' in engine.FORMAT_FALLBACKS
        
        # Each quality level should have fallback formats
        for quality, fallbacks in engine.FORMAT_FALLBACKS.items():
            assert len(fallbacks) == 5, f"Quality {quality} should have 5 fallbacks"
            assert all(isinstance(f, tuple) and len(f) == 2 for f in fallbacks)


class TestYTP3EngineFormatFallbacks:
    """Test format fallback logic."""
    
    def test_fallback_for_best_quality(self, sample_opts, sample_caps):
        """Test fallback formats for best quality."""
        engine = YTP3Engine(sample_opts, sample_caps)
        
        fallbacks = engine.FORMAT_FALLBACKS['best']
        assert len(fallbacks) == 5
        
        # Layer 1 should prefer containerized formats
        assert 'mp4' in fallbacks[0][0]
        assert 'm4a' in fallbacks[0][0]
    
    def test_fallback_for_high_quality(self, sample_opts, sample_caps):
        """Test fallback formats for high (1080p) quality."""
        engine = YTP3Engine(sample_opts, sample_caps)
        
        fallbacks = engine.FORMAT_FALLBACKS['high']
        assert len(fallbacks) == 5
        
        # Should be capped at 1080p
        assert '1080' in fallbacks[0][0]
    
    def test_fallback_for_medium_quality(self, sample_opts, sample_caps):
        """Test fallback formats for medium (720p) quality."""
        engine = YTP3Engine(sample_opts, sample_caps)
        
        fallbacks = engine.FORMAT_FALLBACKS['medium']
        assert len(fallbacks) == 5
        
        # Should be capped at 720p
        assert '720' in fallbacks[0][0]
    
    def test_fallback_for_low_quality(self, sample_opts, sample_caps):
        """Test fallback formats for low (480p) quality."""
        engine = YTP3Engine(sample_opts, sample_caps)
        
        fallbacks = engine.FORMAT_FALLBACKS['low']
        assert len(fallbacks) == 5
        
        # Should be capped at 480p
        assert '480' in fallbacks[0][0]


class TestYTP3EngineLogging:
    """Test engine logging functionality."""
    
    def test_log_without_callback(self, sample_opts, sample_caps, capsys):
        """Test logging without callback prints to stdout."""
        engine = YTP3Engine(sample_opts, sample_caps)
        
        engine.log("Test message")
        captured = capsys.readouterr()
        
        assert "Test message" in captured.out
    
    def test_log_with_callback(self, sample_opts, sample_caps):
        """Test logging with callback."""
        logged_messages = []
        
        def callback(msg):
            logged_messages.append(msg)
        
        engine = YTP3Engine(sample_opts, sample_caps, log_callback=callback)
        engine.log("Test message")
        
        assert "Test message" in logged_messages


class TestYTP3EngineErrorTracking:
    """Test error tracking and detailed error messages."""
    
    def test_last_detailed_error_initialization(self, sample_opts, sample_caps):
        """Test that detailed error is initialized as empty string."""
        engine = YTP3Engine(sample_opts, sample_caps)
        
        assert engine.last_detailed_error == ""
    
    def test_last_detailed_error_can_be_set(self, sample_opts, sample_caps):
        """Test that detailed error can be set during operations."""
        engine = YTP3Engine(sample_opts, sample_caps)
        
        engine.last_detailed_error = "Test error message"
        assert engine.last_detailed_error == "Test error message"
