from typing import List, Tuple, Optional
import logging
import re
from app.domain.models import Image
from app.domain.repositories import ImageRepository
from app.infrastructure.docker_client import DockerCommandExecutor

class ImageService:
    """Service for image operations."""
    
    def __init__(self, image_repository: ImageRepository):
        self.image_repository = image_repository
        self.logger = logging.getLogger(__name__)
        
    def get_all_images(self, context: str = "default") -> List[Image]:
        """Get all images for a context."""
        try:
            return self.image_repository.list_images(context)
        except Exception as e:
            self.logger.error(f"Error listing images: {str(e)}")
            return []
        
    def get_image(self, image_id: str, context: str = "default") -> Optional[Image]:
        """Get a specific image."""
        try:
            return self.image_repository.get_image(image_id, context)
        except Exception as e:
            self.logger.error(f"Error getting image {image_id}: {str(e)}")
            return None
        
    def remove_image(self, image_id: str, context: str = "default") -> bool:
        """Remove an image."""
        try:
            return bool(self.image_repository.remove_image(image_id, context))
        except Exception as e:
            self.logger.error(f"Error removing image {image_id}: {str(e)}")
            return False
        
    def pull_image(self, image_name: str, context: str = "default") -> Tuple[bool, Optional[str]]:
        """Pull an image from a registry."""
        if not image_name:
            return False, "Image name cannot be empty"
            
        # Validate image name format
        if not self._is_valid_image_name(image_name):
            return False, "Invalid image name format. Must be [registry/][namespace/]name[:tag]"
            
        try:
            # Check if the repository implements pull_image
            if hasattr(self.image_repository, 'pull_image') and callable(getattr(self.image_repository, 'pull_image')):
                success = self.image_repository.pull_image(image_name, context)
                if success:
                    return True, None
                    
                # If we failed but don't have a specific error message, try to get one with direct CLI
                output, error = DockerCommandExecutor.run_command([
                    "docker", "--context", context, "pull", image_name
                ])
                if error:
                    return False, self._parse_docker_error(error)
                return False, "Failed to pull image"
            else:
                # Fallback implementation using Docker CLI
                output, error = DockerCommandExecutor.run_command([
                    "docker", "--context", context, "pull", image_name
                ])
                if error:
                    # Log the raw error for debugging
                    self.logger.error(f"Docker pull error: {error}")
                    return False, self._parse_docker_error(error)
                return True, None
        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Error pulling image {image_name}: {error_message}")
            return False, error_message

    def _parse_docker_error(self, error_message: str) -> str:
        """Extract the most relevant part of a Docker CLI error message."""
        # Docker errors often contain quotes with the actual error message
        if '"' in error_message:
            try:
                # Extract text between quotes which often contains the actual error
                quoted_parts = re.findall(r'"([^"]*)"', error_message)
                if quoted_parts:
                    return quoted_parts[0]
            except:
                pass
        return error_message
    
    def _is_valid_image_name(self, image_name: str) -> bool:
        """Validate Docker image name format."""
        # Basic validation pattern for Docker image names
        pattern = r'^[a-zA-Z0-9]+([-._/][a-zA-Z0-9]+)*(:[\w][\w.-]{0,127})?$'
        return bool(re.match(pattern, image_name))
