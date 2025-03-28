"""
Interface for Docker context management operations.
"""
from typing import List, Tuple
from abc import ABC, abstractmethod

class DockerContextService(ABC):
    """Interface for Docker context operations."""
    
    @abstractmethod
    def get_contexts(self) -> Tuple[List[str], str]:
        """Get available Docker contexts."""
        pass
        
    @abstractmethod
    def get_current_context(self) -> str:
        """Get the current active context."""
        pass
        
    @abstractmethod
    def set_context(self, context_name: str) -> bool:
        """Set the current Docker context."""
        pass
