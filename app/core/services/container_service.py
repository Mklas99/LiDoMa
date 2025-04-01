from typing import List, Dict, Optional
import logging
from app.domain.models import Container
from app.domain.repositories import ContainerRepository

class ContainerService:
    """Service for Docker container operations."""
    
    def __init__(self, container_repository: ContainerRepository):
        self.container_repository = container_repository
        self.logger = logging.getLogger(__name__)
        
    def get_all_containers(self, context: str = "default") -> List[Container]:
        """Get all containers."""
        try:
            return self.container_repository.list_containers(True, context)
        except Exception as e:
            self.logger.error(f"Error listing containers: {str(e)}")
            return []
        
    def get_container(self, container_id: str, context: str = "default") -> Optional[Container]:
        """Get a specific container."""
        try:
            return self.container_repository.get_container(container_id, context)
        except Exception as e:
            self.logger.error(f"Error getting container {container_id}: {str(e)}")
            return None
        
    def start_container(self, container_id: str, context: str = "default") -> bool:
        """Start a container."""
        try:
            return self.container_repository.start_container(container_id, context)
        except Exception as e:
            self.logger.error(f"Error starting container {container_id}: {str(e)}")
            return False
            
    def stop_container(self, container_id: str, context: str = "default") -> bool:
        """Stop a container."""
        try:
            return self.container_repository.stop_container(container_id, context)
        except Exception as e:
            self.logger.error(f"Error stopping container {container_id}: {str(e)}")
            return False
            
    def remove_container(self, container_id: str, context: str = "default") -> bool:
        """Remove a container."""
        try:
            return self.container_repository.remove_container(container_id, context)
        except Exception as e:
            self.logger.error(f"Error removing container {container_id}: {str(e)}")
            return False
            
    def create_container(self, image: str, name: Optional[str] = None, context: str = "default") -> bool:
        """Create a new container from an image."""
        try:
            return self.container_repository.create_container(image, name, context)
        except Exception as e:
            self.logger.error(f"Error creating container from image {image}: {str(e)}")
            return False
            
    def get_container_details(self, container_id: str, context: str = "default") -> Dict:
        """Get detailed information about a container."""
        try:
            return self.container_repository.get_container_details(container_id, context)
        except Exception as e:
            self.logger.error(f"Error getting container details: {str(e)}")
            return {}
            
    def get_container_logs(self, container_id: str, context: str = "default") -> str:
        """Get logs from a container."""
        try:
            if hasattr(self.container_repository, 'get_container_logs'):
                return self.container_repository.get_container_logs(container_id, context)
            else:
                # Implement a fallback if the repository doesn't have the method
                from app.infrastructure.docker_client import DockerCommandExecutor
                output, error = DockerCommandExecutor.run_command([
                    "docker", "--context", context, "logs", container_id
                ])
                if error:
                    return f"Error retrieving logs: {error}"
                return output
        except Exception as e:
            self.logger.error(f"Error getting container logs: {str(e)}")
            return f"Error retrieving logs: {str(e)}"
