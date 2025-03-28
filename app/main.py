"""
Main entry point redirector - use the main.py at project root instead.
"""
import sys
import os
from pathlib import Path

# Get the project root directory
root_dir = Path(__file__).parent.parent

# Add it to path and import the real main
sys.path.insert(0, str(root_dir))
from main import main

if __name__ == "__main__":
    print("Note: This file is deprecated. Please run the main.py in the project root directory instead.")
    main()
