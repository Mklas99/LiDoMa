from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models import Network

class NetworkRepository(ABC):
    """Interface for network data access."""
    
    @abstractmethod
    def list_networks(self, context: str = "default") -> List[Network]:
        """List all networks."""
        pass
        
    @abstractmethod
    def get_network(self, network_id: str, context: str = "default") -> Optional[Network]:
        """Get a specific network by ID."""
        pass
        
    @abstractmethod
    def remove_network(self, network_id: str, context: str = "default") -> bool:
        """Remove a network."""
        pass
        
    @abstractmethod
    def create_network(self, name: str, driver: str = "bridge", context: str = "default") -> bool:
        """Create a new network."""
        pass
