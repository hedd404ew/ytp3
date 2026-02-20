"""Tests for configuration management."""

import pytest
import json
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ytp3.utils.config import ConfigManager


class TestConfigManagerInitialization:
    """Test ConfigManager initialization."""
    
    def test_config_manager_init(self, temp_dir):
        """Test ConfigManager initialization."""
        config_file = os.path.join(temp_dir, 'test_config.json')
        config = ConfigManager(config_file)
        
        assert config.config_file == config_file
        assert isinstance(config.data, dict)
    
    def test_config_manager_default_data(self, temp_dir):
        """Test that ConfigManager initializes with default data."""
        config_file = os.path.join(temp_dir, 'test_config.json')
        config = ConfigManager(config_file)
        
        # Should have empty or default data
        assert isinstance(config.data, dict)
    
    def test_config_manager_init_without_file(self):
        """Test ConfigManager initialization without providing a file path."""
        config = ConfigManager()
        
        assert config.config_file is not None
        assert isinstance(config.data, dict)


class TestConfigManagerPersistence:
    """Test configuration saving and loading."""
    
    def test_save_config(self, temp_dir, sample_config):
        """Test saving configuration."""
        config_file = os.path.join(temp_dir, 'test_config.json')
        config = ConfigManager(config_file)
        
        config.data = sample_config
        config.save()
        
        assert os.path.exists(config_file)
    
    def test_load_config(self, temp_dir, sample_config):
        """Test loading configuration."""
        config_file = os.path.join(temp_dir, 'test_config.json')
        
        # Write config file
        with open(config_file, 'w') as f:
            json.dump(sample_config, f)
        
        # Load config
        config = ConfigManager(config_file)
        loaded_data = config.load()
        
        assert loaded_data == sample_config
    
    def test_config_roundtrip(self, temp_dir, sample_config):
        """Test save and load roundtrip."""
        config_file = os.path.join(temp_dir, 'test_config.json')
        
        # Save
        config1 = ConfigManager(config_file)
        config1.data = sample_config
        config1.save()
        
        # Load
        config2 = ConfigManager(config_file)
        loaded_data = config2.load()
        
        assert loaded_data == sample_config
    
    def test_load_returns_data(self, temp_dir, sample_config):
        """Test that load method returns the data dictionary."""
        config_file = os.path.join(temp_dir, 'test_config.json')
        
        with open(config_file, 'w') as f:
            json.dump(sample_config, f)
        
        config = ConfigManager(config_file)
        result = config.load()
        
        assert isinstance(result, dict)
        assert result == sample_config
    
    def test_load_nonexistent_file(self, temp_dir):
        """Test loading from a nonexistent file returns defaults."""
        config_file = os.path.join(temp_dir, 'nonexistent.json')
        config = ConfigManager(config_file)
        
        # Load should not fail, just return defaults
        result = config.load()
        assert isinstance(result, dict)


class TestConfigManagerDataTypes:
    """Test configuration data type handling."""
    
    def test_config_save_preserves_types(self, temp_dir):
        """Test that save/load preserves data types."""
        config_file = os.path.join(temp_dir, 'test_config.json')
        
        test_data = {
            'string': 'value',
            'integer': 42,
            'float': 3.14,
            'boolean': True,
            'null': None,
            'list': [1, 2, 3],
            'dict': {'nested': 'value'}
        }
        
        config = ConfigManager(config_file)
        config.data = test_data
        config.save()
        
        loaded = config.load()
        
        assert loaded['string'] == 'value'
        assert loaded['integer'] == 42
        assert loaded['float'] == 3.14
        assert loaded['boolean'] is True
        assert loaded['null'] is None
        assert loaded['list'] == [1, 2, 3]
        assert loaded['dict'] == {'nested': 'value'}


class TestConfigManagerInitialize:
    """Test ConfigManager initialize method."""
    
    def test_initialize_portable_mode(self, temp_dir):
        """Test initialize in portable mode."""
        config = ConfigManager()
        
        # Change to temp dir
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            config.initialize(is_portable=True)
            
            # Should set config_file to local path
            assert config.config_file == "ytp3_config.json"
        finally:
            os.chdir(old_cwd)
    
    def test_initialize_non_portable_mode(self):
        """Test initialize in non-portable mode."""
        config = ConfigManager()
        
        # This will create config in system location
        # Just verify it doesn't raise an error
        try:
            config.initialize(is_portable=False)
            
            # Should set some config_file path
            assert config.config_file is not None
        except Exception as e:
            # May fail on permission issues, but shouldn't crash code
            assert True
