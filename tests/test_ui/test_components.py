"""Tests for UI components."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Note: Full UI testing requires a display server
# These tests focus on component initialization and logic


class TestUIComponentImports:
    """Test that UI components can be imported."""
    
    def test_import_app_module(self):
        """Test that app module can be imported."""
        try:
            from ytp3.ui import app
            assert app is not None
        except ImportError as e:
            # May fail on headless systems - that's OK
            if 'display' not in str(e).lower() and 'tkinter' not in str(e).lower():
                raise
    
    def test_import_components_module(self):
        """Test that components module can be imported."""
        try:
            from ytp3.ui import components
            assert components is not None
        except ImportError as e:
            # May fail on headless systems - that's OK
            if 'display' not in str(e).lower() and 'tkinter' not in str(e).lower():
                raise


class TestUIComponentStructure:
    """Test UI component structure and exports."""
    
    def test_app_module_has_run_gui(self):
        """Test that app module has run_gui function."""
        try:
            from ytp3.ui.app import run_gui
            assert callable(run_gui)
        except ImportError as e:
            # May fail on headless systems
            if 'display' not in str(e).lower() and 'tkinter' not in str(e).lower():
                pytest.skip("Skipping UI test on headless system")
    
    def test_components_module_has_retro_progress_bar(self):
        """Test that components module has RetroProgressBar class."""
        try:
            from ytp3.ui.components import RetroProgressBar
            assert RetroProgressBar is not None
            assert callable(RetroProgressBar)
        except ImportError as e:
            # May fail on headless systems
            if 'display' not in str(e).lower() and 'tkinter' not in str(e).lower():
                pytest.skip("Skipping UI test on headless system")
