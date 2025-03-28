from typing import List, Dict, Any, Optional

from app.domain.models import Container
from app.domain.repositories import ContainerRepository

class ContainerService:
    """Service for container operations."""
    
    def __init__(self, container_repository: ContainerRepository):
        self.container_repository = container_repository
        
    def get_all_containers(self, context: str = "default") -> List[Container]:
        """Get all containers for a context."""
        return self.container_repository.list_containers(all_containers=True, context=context)
        
    def get_container(self, container_id: str, context: str = "default") -> Optional[Container]:
        """Get a specific container."""
        return self.container_repository.get_container(container_id, context)
        
    def start_container(self, container_id: str, context: str = "default") -> bool:
        """Start a container."""
        return self.container_repository.start_container(container_id, context)
        
    def stop_container(self, container_id: str, context: str = "default") -> bool:
        """Stop a container."""
        return self.container_repository.stop_container(container_id, context)
        
    def remove_container(self, container_id: str, context: str = "default") -> bool:
        """Remove a container."""
        return self.container_repository.remove_container(container_id, context)
        
    def create_container(self, image_id: str, name: Optional[str] = None, 
                        context: str = "default", **kwargs) -> bool:
        """Create a new container."""
        return self.container_repository.create_container(image_id, name, context, **kwargs)
        
    def get_container_details(self, container_id: str, context: str = "default") -> Dict[str, Any]:
        """Get detailed container information."""
        return self.container_repository.get_container_details(container_id, context)
