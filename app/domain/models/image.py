"""
Domain model for Docker images.
"""
from typing import List, Dict, Optional
from datetime import datetime

class Image:
    """Domain model representing a Docker image."""
    
    def __init__(
        self,
        id: str,
        name: str,
        tags: List[str],
        size: int,
        created: datetime,
        labels: Dict[str, str] = None,
        context: str = "default"
    ):
        self.id = id
        self.name = name
        self.tags = tags or []
        self.size = size
        self.created = created
        self.labels = labels or {}
        self.context = context
        
    def __repr__(self):
        tags_str = ", ".join(self.tags) if self.tags else "untagged"
        return f"Image({self.name}, {self.id[:12]}, {tags_str})"
