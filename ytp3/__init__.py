"""
YTP3Downloader - A modern YouTube downloader with GUI and CLI support.

Version: 3.0.0
"""

__version__ = "3.0.0"
__author__ = "YTP3 Development Team"

from .core.engine import YTP3Engine
from .utils.config import ConfigManager
from .utils.system import SystemDoctor

__all__ = ["YTP3Engine", "ConfigManager", "SystemDoctor"]
