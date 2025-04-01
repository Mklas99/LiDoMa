from typing import List, Optional
import logging
from app.domain.models import Network
from app.domain.repositories import NetworkRepository

class NetworkService:
    """Service for Docker network operations."""
    
    def __init__(self, network_repository: NetworkRepository):
        self.network_repository = network_repository
        self.logger = logging.getLogger(__name__)
        
    def get_all_networks(self, context: str = "default") -> List[Network]:
        """Get all networks."""
        try:
            return self.network_repository.list_networks(context)
        except Exception as e:
            self.logger.error(f"Error listing networks: {str(e)}")
            return []
        
    def get_network(self, network_id: str, context: str = "default") -> Optional[Network]:
        """Get a specific network."""
        try:
            return self.network_repository.get_network(network_id, context)
        except Exception as e:
            self.logger.error(f"Error getting network {network_id}: {str(e)}")
            return None
        
    def remove_network(self, network_id: str, context: str = "default") -> bool:
        """Remove a network."""
        try:
            result = self.network_repository.remove_network(network_id, context)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error removing network {network_id}: {str(e)}")
            return False
        
    def create_network(self, name: str, driver: str = "bridge", context: str = "default") -> bool:
        """Create a new network."""
        try:
            result = self.network_repository.create_network(name, driver, context)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error creating network {name}: {str(e)}")
            return False
        
    def get_network_details(self, network_id: str, context: str = "default") -> dict:
        """Get detailed information about a network."""
        try:
            return self.network_repository.get_network_details(network_id, context)
        except Exception as e:
            self.logger.error(f"Error getting network details: {str(e)}")
            return {}
