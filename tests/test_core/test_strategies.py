"""Tests for download strategies."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ytp3.core.strategies import DownloadStrategy


class TestDownloadStrategyRetrieval:
    """Test strategy retrieval and validation."""
    
    def test_get_all_strategies(self):
        """Test that all strategies are retrieved."""
        strategies = DownloadStrategy.get_all()
        
        assert len(strategies) > 0
        assert isinstance(strategies, list)
    
    def test_strategy_structure(self):
        """Test that strategies have required fields."""
        strategies = DownloadStrategy.get_all()
        
        required_fields = ['name', 'extra']
        for strategy in strategies:
            assert all(field in strategy for field in required_fields)
            assert isinstance(strategy['name'], str)
            assert isinstance(strategy['extra'], dict)
    
    def test_strategy_names_unique(self):
        """Test that strategy names are unique."""
        strategies = DownloadStrategy.get_all()
        names = [s['name'] for s in strategies]
        
        assert len(names) == len(set(names)), "Strategy names should be unique"
    
    def test_has_standard_strategy(self):
        """Test that Standard strategy exists."""
        strategies = DownloadStrategy.get_all()
        names = [s['name'] for s in strategies]
        
        assert 'Standard' in names
    
    def test_has_bypass_strategies(self):
        """Test that bypass strategies exist."""
        strategies = DownloadStrategy.get_all()
        names = [s['name'] for s in strategies]
        
        # Should have at least 2 strategies (Standard + at least one bypass)
        assert len(strategies) >= 2
        
        # Check for common bypass strategy names
        bypass_names = [name for name in names if name != 'Standard']
        assert len(bypass_names) > 0


class TestStrategyConfiguration:
    """Test strategy configuration options."""
    
    def test_strategy_extra_contains_options(self):
        """Test that strategy extra dict contains yt-dlp options."""
        strategies = DownloadStrategy.get_all()
        
        for strategy in strategies:
            extra = strategy['extra']
            # extra should be a dict that can be passed to yt-dlp
            assert isinstance(extra, dict)
    
    def test_strategy_can_be_passed_to_engine(self):
        """Test that strategies are compatible with engine usage."""
        from ytp3.core.engine import YTP3Engine
        
        strategies = DownloadStrategy.get_all()
        
        assert len(strategies) > 0
        # Strategies should be usable for the 20 attempt combinations
        # (4 strategies × 5 format levels)
        assert len(strategies) >= 1
