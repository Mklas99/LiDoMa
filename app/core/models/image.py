from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Image:
    id: str
    name: str
    tags: List[str] = field(default_factory=list)
    size: int = 0
    created: Optional[datetime] = None
    context: str = "default"
    
    def get_size_formatted(self) -> str:
        """Return human-readable size."""
        if self.size > 1_000_000_000:  # GB
            return f"{self.size / 1_000_000_000:.2f} GB"
        elif self.size > 1_000_000:  # MB
            return f"{self.size / 1_000_000:.2f} MB"
        elif self.size > 1_000:  # KB
            return f"{self.size / 1_000:.2f} KB"
        else:
            return f"{self.size} B"
            
    def get_primary_tag(self) -> str:
        """Return the main tag for display."""
        if not self.tags or len(self.tags) == 0:
            return "<none>:<none>"
        return self.tags[0]
