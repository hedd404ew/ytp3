#!/usr/bin/env python3
"""
YTP3Downloader - Main entry point.

This script handles both GUI and CLI modes.
"""

import sys

from ytp3.cli import main as cli_main
from ytp3.ui.app import run_gui
from ytp3.utils.system import CrashHandler


def main():
    """Main application entry point."""
    try:
        # Check for CLI arguments
        if len(sys.argv) > 1:
            cli_main()
        else:
            # Launch GUI
            run_gui()
    except Exception as e:
        CrashHandler.handle(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
