"""
Interface for Docker Compose operations.
"""
from typing import Tuple, List, Dict
from abc import ABC, abstractmethod

class DockerComposeService(ABC):
    """Interface for Docker Compose operations."""
    
    @abstractmethod
    def compose_up(self, project_dir: str, detach: bool = True, context: str = "default") -> Tuple[bool, str]:
        """Start a Docker Compose project."""
        pass
        
    @abstractmethod
    def compose_down(self, project_dir: str, volumes: bool = False, context: str = "default") -> Tuple[bool, str]:
        """Stop and remove containers, networks from a Docker Compose project."""
        pass
        
    @abstractmethod
    def compose_ps(self, project_dir: str, context: str = "default") -> Tuple[List[Dict], str]:
        """List containers for a Docker Compose project."""
        pass
        
    @abstractmethod
    def compose_logs(self, project_dir: str, service: str = None, context: str = "default") -> Tuple[str, str]:
        """Fetch logs from a Docker Compose project."""
        pass
