from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from domain.models import Container

class ContainerRepository(ABC):
    """Interface for container data access."""
    
    @abstractmethod
    def list_containers(self, all_containers: bool = True, context: str = "default") -> List[Container]:
        """List all containers."""
        pass
        
    @abstractmethod
    def get_container(self, container_id: str, context: str = "default") -> Optional[Container]:
        """Get a specific container by ID."""
        pass
        
    @abstractmethod
    def start_container(self, container_id: str, context: str = "default") -> bool:
        """Start a container."""
        pass
        
    @abstractmethod
    def stop_container(self, container_id: str, context: str = "default") -> bool:
        """Stop a container."""
        pass
        
    @abstractmethod
    def remove_container(self, container_id: str, context: str = "default") -> bool:
        """Remove a container."""
        pass
        
    @abstractmethod
    def create_container(self, image_id: str, name: Optional[str] = None, 
                        context: str = "default", **kwargs) -> bool:
        """Create a new container."""
        pass
        
    @abstractmethod
    def get_container_details(self, container_id: str, context: str = "default") -> Dict[str, Any]:
        """Get detailed container information."""
        pass
