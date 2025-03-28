from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional

class DockerComposeService(ABC):
    """Interface for Docker Compose operations."""
    
    @abstractmethod
    def list_compose_projects(self, context: str = "default") -> List[Dict]:
        """List all Docker Compose projects.
        
        Returns:
            List of project dictionaries containing name, path, status
        """
        pass
    
    @abstractmethod
    def get_project_services(self, project_dir: str, context: str = "default") -> List[Dict]:
        """Get all services defined in a Compose project.
        
        Args:
            project_dir: Directory containing docker-compose.yml
            context: Docker context to use
            
        Returns:
            List of service dictionaries with name, status
        """
        pass
    
    @abstractmethod
    def compose_up(self, project_dir: str, detach: bool = True, context: str = "default") -> Tuple[bool, str]:
        """Start a Docker Compose project.
        
        Args:
            project_dir: Directory containing docker-compose.yml
            detach: Run in background
            context: Docker context to use
            
        Returns:
            Tuple of (success, message)
        """
        pass
    
    @abstractmethod
    def compose_down(self, project_dir: str, remove_volumes: bool = False, context: str = "default") -> Tuple[bool, str]:
        """Stop a Docker Compose project.
        
        Args:
            project_dir: Directory containing docker-compose.yml
            remove_volumes: Also remove volumes
            context: Docker context to use
            
        Returns:
            Tuple of (success, message)
        """
        pass
