from abc import ABC, abstractmethod
from typing import List, Tuple

class DockerContextService(ABC):
    """Interface for Docker context operations."""
    
    @abstractmethod
    def get_contexts(self) -> Tuple[List[str], str]:
        """Get available Docker contexts.
        
        Returns:
            Tuple containing a list of context names and any error message
        """
        pass
        
    @abstractmethod
    def get_current_context(self) -> str:
        """Get the currently active Docker context."""
        pass
        
    @abstractmethod
    def set_context(self, context_name: str) -> bool:
        """Set the current Docker context."""
        pass
