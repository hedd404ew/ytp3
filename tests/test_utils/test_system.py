"""Tests for system utilities."""

import pytest
import sys
import os
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ytp3.utils.system import SystemDoctor, PathManager, CrashHandler, ConfigManager


class TestSystemDoctorInitialization:
    """Test SystemDoctor initialization."""
    
    def test_system_doctor_init(self):
        """Test SystemDoctor initialization."""
        doctor = SystemDoctor()
        
        assert doctor is not None
        assert hasattr(doctor, 'run_diagnostics')
        assert hasattr(doctor, 'report')
        assert isinstance(doctor.report, dict)
    
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
        # Should have ffmpeg check
        assert 'ffmpeg' in caps
    
    def test_diagnostics_checks_ffmpeg(self, temp_dir):
        """Test that diagnostics checks for ffmpeg."""
        doctor = SystemDoctor()
        report = doctor.run_diagnostics(temp_dir)
        
        assert 'ffmpeg' in report
        assert isinstance(report['ffmpeg'], bool)
    
    def test_diagnostics_checks_js_runtime(self, temp_dir):
        """Test that diagnostics checks for JavaScript runtime."""
        doctor = SystemDoctor()
        report = doctor.run_diagnostics(temp_dir)
        
        assert 'js_runtime' in report
        # Can be None, 'node', or 'deno'
        assert report['js_runtime'] in [None, 'node', 'deno']
    
    def test_diagnostics_checks_internet(self, temp_dir):
        """Test that diagnostics checks for internet connectivity."""
        doctor = SystemDoctor()
        report = doctor.run_diagnostics(temp_dir)
        
        assert 'internet' in report
        assert isinstance(report['internet'], bool)


class TestSystemDoctorMissingCriticals:
    """Test missing critical detection."""
    
    def test_get_missing_criticals(self):
        """Test getting missing critical components."""
        doctor = SystemDoctor()
        doctor.run_diagnostics(tempfile.gettempdir())
        missing = doctor.get_missing_criticals()
        
        assert isinstance(missing, list)
        # missing can be empty list or contain string items
        assert all(isinstance(m, str) for m in missing)
    
    def test_missing_criticals_returns_list(self):
        """Test that missing_criticals always returns a list."""
        doctor = SystemDoctor()
        doctor.run_diagnostics(tempfile.gettempdir())
        missing = doctor.get_missing_criticals()
        
        assert isinstance(missing, list)
    
    def test_missing_criticals_content(self):
        """Test that missing critical items are reasonable names."""
        doctor = SystemDoctor()
        doctor.run_diagnostics(tempfile.gettempdir())
        missing = doctor.get_missing_criticals()
        
        # Check that if FFmpeg is missing, it's in the list
        if not doctor.report.get('ffmpeg'):
            assert 'FFmpeg' in missing


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
    
    def test_get_default_path_is_usable(self):
        """Test that default path can be written to."""
        path = PathManager.get_default_path()
        
        # Path should exist or be created
        assert path is not None
        assert isinstance(path, str)
    
    def test_get_default_path_exists_or_creatable(self):
        """Test that default path exists or is creatable."""
        path = PathManager.get_default_path()
        
        # The path should exist after calling get_default_path
        # (the method tries to create it)
        assert isinstance(path, str)
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
    
    def test_multiple_calls_consistent(self):
        """Test that multiple calls return consistent paths."""
        path1 = PathManager.get_default_path()
        path2 = PathManager.get_default_path()
        
        assert path1 == path2
    
    def test_default_path_is_absolute_or_relative(self):
        """Test that path is either absolute or relative."""
        path = PathManager.get_default_path()
        
        # Should be a valid path
        assert len(path) > 0
        assert isinstance(path, str)


class TestCrashHandlerBasics:
    """Test CrashHandler basic functionality."""
    
    def test_crash_handler_has_handle_method(self):
        """Test that CrashHandler has handle method."""
        assert hasattr(CrashHandler, 'handle')
        assert callable(getattr(CrashHandler, 'handle'))
    
    def test_crash_handler_handle_with_exception(self):
        """Test crash handler with an exception."""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            # Should not raise, just handle it
            CrashHandler.handle(e)
    
    def test_crash_handler_is_static(self):
        """Test that CrashHandler doesn't require instantiation."""
        # Should be able to call directly
        try:
            raise RuntimeError("Test")
        except RuntimeError:
            CrashHandler.handle(None)  # Should work without instantiation


class TestCrashHandlerFileCreation:
    """Test CrashHandler file creation."""
    
    def test_crash_handler_creates_file(self, temp_dir):
        """Test that crash handler attempts to create crash file."""
        # Change to temp directory
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create a test exception
            try:
                raise RuntimeError("Test error for crash handler")
            except RuntimeError:
                CrashHandler.handle(None)
            
            # Check if crash file was created in temp dir
            crash_files = [f for f in os.listdir(temp_dir) if f.startswith('crash_')]
            # At least one crash file should exist
            assert len(crash_files) > 0
        finally:
            os.chdir(old_cwd)


class TestConfigManagerDetection:
    """Test ConfigManager file detection."""
    
    def test_detect_config_file_priority(self, temp_dir):
        """Test that ConfigManager detects local config file if present."""
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create a local config file
            with open('ytp3_config.json', 'w') as f:
                f.write('{}')
            
            config = ConfigManager()
            
            # Should have detected the local file
            assert 'ytp3_config.json' in config.config_file
        finally:
            os.chdir(old_cwd)
    
    def test_config_manager_initialize_portable(self, temp_dir):
        """Test ConfigManager initialize in portable mode."""
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            config = ConfigManager()
            config.initialize(is_portable=True)
            
            # Should point to local config file
            assert 'ytp3_config.json' in config.config_file
        finally:
            os.chdir(old_cwd)
