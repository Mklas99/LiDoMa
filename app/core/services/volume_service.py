from typing import List, Dict, Optional
from app.domain.models import Volume
from app.domain.repositories import VolumeRepository

class VolumeService:
    """Service for volume operations."""
    
    def __init__(self, volume_repository: VolumeRepository):
        self.volume_repository = volume_repository
        
    def get_all_volumes(self, context: str = "default") -> List[Volume]:
        """Get all volumes for a context."""
        return self.volume_repository.list_volumes(context)
        
    def get_volume(self, volume_name: str, context: str = "default") -> Optional[Volume]:
        """Get a specific volume."""
        return self.volume_repository.get_volume(volume_name, context)
        
    def remove_volume(self, volume_name: str, context: str = "default") -> bool:
        """Remove a volume."""
        return self.volume_repository.remove_volume(volume_name, context)
        
    def create_volume(self, name: str, driver: str = "local", context: str = "default", **kwargs) -> bool:
        """Create a new volume."""
        return self.volume_repository.create_volume(name, driver, context, **kwargs)
