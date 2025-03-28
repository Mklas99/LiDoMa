from typing import List, Dict, Optional
from app.domain.models import Image
from app.domain.repositories import ImageRepository

class ImageService:
    """Service for image operations."""
    
    def __init__(self, image_repository: ImageRepository):
        self.image_repository = image_repository
        
    def get_all_images(self, context: str = "default") -> List[Image]:
        """Get all images for a context."""
        return self.image_repository.list_images(context)
        
    def get_image(self, image_id: str, context: str = "default") -> Optional[Image]:
        """Get a specific image."""
        return self.image_repository.get_image(image_id, context)
        
    def remove_image(self, image_id: str, context: str = "default") -> bool:
        """Remove an image."""
        return self.image_repository.remove_image(image_id, context)
        
    def pull_image(self, image_name: str, tag: str = "latest", context: str = "default") -> bool:
        """Pull an image from a registry."""
        return self.image_repository.pull_image(image_name, tag, context)
