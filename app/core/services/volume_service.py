from typing import List, Optional
import logging
from app.domain.models import Volume
from app.domain.repositories import VolumeRepository

class VolumeService:
    """Service for Docker volume operations."""
    
    def __init__(self, volume_repository: VolumeRepository):
        self.volume_repository = volume_repository
        self.logger = logging.getLogger(__name__)
        
    def get_all_volumes(self, context: str = "default") -> List[Volume]:
        """Get all volumes."""
        try:
            return self.volume_repository.list_volumes(context)
        except Exception as e:
            self.logger.error(f"Error listing volumes: {str(e)}")
            return []
        
    def get_volume(self, volume_name: str, context: str = "default") -> Optional[Volume]:
        """Get a specific volume."""
        try:
            return self.volume_repository.get_volume(volume_name, context)
        except Exception as e:
            self.logger.error(f"Error getting volume {volume_name}: {str(e)}")
            return None
        
    def remove_volume(self, volume_name: str, context: str = "default") -> bool:
        """Remove a volume."""
        try:
            result = self.volume_repository.remove_volume(volume_name, context)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error removing volume {volume_name}: {str(e)}")
            return False
        
    def create_volume(self, name: str, driver: str = "local", context: str = "default") -> bool:
        """Create a new volume."""
        try:
            result = self.volume_repository.create_volume(name, driver, context)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error creating volume {name}: {str(e)}")
            return False
        
    def get_volume_details(self, volume_name: str, context: str = "default") -> dict:
        """Get detailed information about a volume."""
        try:
            return self.volume_repository.get_volume_details(volume_name, context)
        except Exception as e:
            self.logger.error(f"Error getting volume details: {str(e)}")
            return {}
