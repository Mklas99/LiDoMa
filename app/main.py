#!/usr/bin/env python
"""
Main entry point redirector - use the main.py at project root instead.

To run with conda base environment:
1. From command line: conda run -n base python app/main.py
2. Or activate base first: conda activate base
   Then run: python app/main.py
"""
import sys
import os
from pathlib import Path

# Add import for theme manager
from app.ui.theme_manager import ThemeManager

# Get the project root directory
root_dir = Path(__file__).parent.parent

# Add it to path and import the real main
sys.path.insert(0, str(root_dir))
from main import main

if __name__ == "__main__":
    print("Note: This file is deprecated. Please run the main.py in the project root directory instead.")
    print("To use conda base environment with the root main.py, run: conda run -n base python main.py")
    main()
