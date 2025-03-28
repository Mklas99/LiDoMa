from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from app.domain.models import Volume

class VolumeRepository(ABC):
    """Interface for volume data access."""
    
    @abstractmethod
    def list_volumes(self, context: str = "default") -> List[Volume]:
        """List all volumes."""
        pass
        
    @abstractmethod
    def get_volume(self, volume_name: str, context: str = "default") -> Optional[Volume]:
        """Get a specific volume by name."""
        pass
        
    @abstractmethod
    def remove_volume(self, volume_name: str, context: str = "default") -> bool:
        """Remove a volume."""
        pass
        
    @abstractmethod
    def create_volume(self, name: str, driver: str = "local", context: str = "default", **kwargs) -> bool:
        """Create a new volume."""
        pass
