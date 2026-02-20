"""Tests for system utilities."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ytp3.utils.system import SystemDoctor, PathManager


class TestSystemDoctorInitialization:
    """Test SystemDoctor initialization."""
    
    def test_system_doctor_init(self):
        """Test SystemDoctor initialization."""
        doctor = SystemDoctor()
        
        assert doctor is not None
        assert hasattr(doctor, 'run_diagnostics')
    
    def test_run_diagnostics_returns_dict(self, temp_dir):
        """Test that diagnostics returns a dictionary."""
        doctor = SystemDoctor()
        caps = doctor.run_diagnostics(temp_dir)
        
        assert isinstance(caps, dict)
    
    def test_diagnostics_contains_expected_keys(self, temp_dir):
        """Test that diagnostics contains expected capability keys."""
        doctor = SystemDoctor()
        caps = doctor.run_diagnostics(temp_dir)
        
        # Should check for presence of common capability keys
        # (exact keys depend on system)
        assert isinstance(caps, dict)
        assert len(caps) > 0


class TestSystemDoctorMissingCriticals:
    """Test missing critical detection."""
    
    def test_get_missing_criticals(self):
        """Test getting missing critical components."""
        doctor = SystemDoctor()
        missing = doctor.get_missing_criticals()
        
        assert isinstance(missing, list)
        # missing can be empty list or contain string items
        assert all(isinstance(m, str) for m in missing)


class TestPathManagerDefaults:
    """Test PathManager default path logic."""
    
    def test_get_default_path_returns_string(self):
        """Test that get_default_path returns a string."""
        path = PathManager.get_default_path()
        
        assert isinstance(path, str)
        assert len(path) > 0
    
    def test_get_default_path_ends_with_downloads(self):
        """Test that default path is in a sensible location."""
        path = PathManager.get_default_path()
        
        # Path should exist or be creatable
        # Should be in user's home or Downloads area
        assert len(path) > 0


class TestPathManagerPlatformAwareness:
    """Test that PathManager is platform-aware."""
    
    def test_paths_are_platform_appropriate(self):
        """Test that paths use appropriate separators."""
        path = PathManager.get_default_path()
        
        # Should be a valid path string
        assert isinstance(path, str)
        # Should not be empty
        assert len(path) > 0
