#!/usr/bin/env python3
"""
Kutti - Your Personal AI CLI Agent

OpenCode-compatible authentication & provider system

Usage:
    python kutti.py --help
    python kutti.py login
    python kutti.py logout
    python kutti.py providers list
    python kutti.py models list
    python kutti.py session
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the CLI main module
from cli.main import main

if __name__ == "__main__":
    main()