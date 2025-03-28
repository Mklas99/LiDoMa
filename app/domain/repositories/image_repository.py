from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from app.domain.models import Image

class ImageRepository(ABC):
    """Interface for image data access."""
    
    @abstractmethod
    def list_images(self, context: str = "default") -> List[Image]:
        """List all images."""
        pass
        
    @abstractmethod
    def get_image(self, image_id: str, context: str = "default") -> Optional[Image]:
        """Get a specific image by ID."""
        pass
        
    @abstractmethod
    def remove_image(self, image_id: str, context: str = "default") -> bool:
        """Remove an image."""
        pass
        
    @abstractmethod
    def pull_image(self, image_name: str, tag: str = "latest", context: str = "default") -> bool:
        """Pull an image from a registry."""
        pass
