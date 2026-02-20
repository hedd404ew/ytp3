"""System utilities: configuration, diagnostics, and path management."""

import os
import json
import platform
import shutil
import tempfile
import traceback
import datetime


class ConfigManager:
    """Manages application configuration and persistence."""
    
    def __init__(self, config_file=None):
        """
        Initialize config manager.
        
        Args:
            config_file (str, optional): Path to config file. If not provided, 
                                        will auto-detect or use default location.
        """
        if config_file:
            self.config_file = config_file
        else:
            self.config_file = self._detect_config_file()
        self.data = self._get_defaults()

    def _get_defaults(self):
        """Get default configuration values."""
        return {
            "save_path": os.path.join(os.getcwd(), "downloads"),
            "mode": "Video",
            "format": "mp4",
            "resolution": "Best Available",
            "concurrency": 2,
            "toggles": {
                "meta": True,
                "thumb": True,
                "subs": False,
                "sponsor": False,
                "archive": False,
                "geo": False
            },
            "auth": {
                "browser": "None",
                "file": ""
            },
            "last_urls": ""
        }

    def _detect_config_file(self):
        """Auto-detect existing config file location."""
        if os.path.exists("ytp3_config.json"):
            return "ytp3_config.json"
        
        if platform.system() == "Windows":
            appdata = os.getenv('APPDATA')
            if appdata:
                conf = os.path.join(appdata, "YTP3Downloader", "config.json")
                if os.path.exists(conf):
                    return conf
        
        return None

    def initialize(self, is_portable):
        """
        Initialize config file location.
        
        Args:
            is_portable (bool): If True, use local config file
        """
        if is_portable:
            self.config_file = "ytp3_config.json"
        else:
            if platform.system() == "Windows":
                base = os.getenv('APPDATA')
            else:
                base = os.path.expanduser("~/.config")
            
            path = os.path.join(base, "YTP3Downloader")
            if not os.path.exists(path):
                os.makedirs(path)
            
            self.config_file = os.path.join(path, "config.json")
        
        self.save()

    def load(self):
        """
        Load configuration from file.
        
        Returns:
            dict: Configuration data
        """
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.data.update(json.load(f))
            except Exception as e:
                print(f"[WARN] Failed to load config: {e}")
        
        return self.data

    def save(self):
        """Save configuration to file."""
        if self.config_file:
            try:
                with open(self.config_file, 'w') as f:
                    json.dump(self.data, f, indent=4)
            except Exception as e:
                print(f"[ERROR] Failed to save config: {e}")


class SystemDoctor:
    """Performs system diagnostics and capability checks."""
    
    def __init__(self):
        """Initialize system doctor."""
        self.report = {
            "ffmpeg": False,
            "js_runtime": None,
            "internet": False
        }
        self._inject_local_paths()

    def _inject_local_paths(self):
        """Add local binary directory to PATH."""
        local_bin = os.path.dirname(os.path.abspath(__file__))
        os.environ["PATH"] += os.pathsep + local_bin

    def run_diagnostics(self, download_path):
        """
        Run system diagnostics.
        
        Args:
            download_path (str): Path where downloads will be saved
            
        Returns:
            dict: Diagnostic report
        """
        # Check for FFmpeg
        self.report["ffmpeg"] = shutil.which("ffmpeg") is not None
        
        # Check for JavaScript runtime (Deno or Node.js)
        if shutil.which("deno"):
            self.report["js_runtime"] = "deno"
        elif shutil.which("node"):
            self.report["js_runtime"] = "node"
        else:
            self.report["js_runtime"] = None
        
        # Check internet connectivity
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            self.report["internet"] = True
        except:
            self.report["internet"] = False
        
        return self.report

    def get_missing_criticals(self):
        """
        Get list of missing critical dependencies.
        
        Returns:
            list: Names of missing critical dependencies
        """
        missing = []
        
        if not self.report["ffmpeg"]:
            missing.append("FFmpeg")
        if not self.report["js_runtime"]:
            missing.append("JS Runtime (Deno/Node.js)")
        
        return missing


class PathManager:
    """Handles path management and creation."""
    
    @staticmethod
    def get_default_path():
        """
        Get default download path.
        
        Returns:
            str: Default download directory path
        """
        local = os.path.join(os.getcwd(), "downloads")
        
        if not os.path.exists(local):
            try:
                os.makedirs(local)
            except:
                return tempfile.gettempdir()
        
        return local


class CrashHandler:
    """Handles application crashes and logging."""
    
    @staticmethod
    def handle(exception):
        """
        Handle application crash and save traceback.
        
        Args:
            exception (Exception): The exception that caused the crash
        """
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"crash_{ts}.txt"
        
        try:
            with open(filename, "w") as f:
                f.write(traceback.format_exc())
            print(f"[FATAL] System Crash. Traceback saved to {filename}")
        except:
            print("[FATAL] System Crash. Could not write log file.")
            traceback.print_exc()
