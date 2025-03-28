from typing import List, Dict, Optional
from app.domain.models import Network
from app.domain.repositories import NetworkRepository

class NetworkService:
    """Service for network operations."""
    
    def __init__(self, network_repository: NetworkRepository):
        self.network_repository = network_repository
        
    def get_all_networks(self, context: str = "default") -> List[Network]:
        """Get all networks for a context."""
        return self.network_repository.list_networks(context)
        
    def get_network(self, network_id: str, context: str = "default") -> Optional[Network]:
        """Get a specific network."""
        return self.network_repository.get_network(network_id, context)
        
    def remove_network(self, network_id: str, context: str = "default") -> bool:
        """Remove a network."""
        return self.network_repository.remove_network(network_id, context)
        
    def create_network(self, name: str, driver: str = "bridge", context: str = "default", **kwargs) -> bool:
        """Create a new network."""
        return self.network_repository.create_network(name, driver, context, **kwargs)
