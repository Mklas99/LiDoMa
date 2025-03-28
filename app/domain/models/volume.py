"""
Domain model for Docker volumes.
"""
from typing import Dict, Optional

class Volume:
    """Domain model representing a Docker volume."""
    
    def __init__(
        self,
        name: str,
        driver: str,
        mountpoint: str,
        labels: Dict[str, str] = None,
        options: Dict[str, str] = None,
        context: str = "default"
    ):
        self.name = name
        self.driver = driver
        self.mountpoint = mountpoint
        self.labels = labels or {}
        self.options = options or {}
        self.context = context
        
    def __repr__(self):
        return f"Volume({self.name}, {self.driver})"
