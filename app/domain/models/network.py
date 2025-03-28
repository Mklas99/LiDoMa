"""
Domain model for Docker networks.
"""
from typing import Dict, List, Optional

class Network:
    """Domain model representing a Docker network."""
    
    def __init__(
        self,
        id: str,
        name: str,
        driver: str,
        scope: str,
        subnet: Optional[str] = None,
        gateway: Optional[str] = None,
        containers: List[str] = None,
        labels: Dict[str, str] = None,
        context: str = "default"
    ):
        self.id = id
        self.name = name
        self.driver = driver
        self.scope = scope
        self.subnet = subnet
        self.gateway = gateway
        self.containers = containers or []
        self.labels = labels or {}
        self.context = context
        
    def __repr__(self):
        return f"Network({self.name}, {self.id[:12]}, {self.driver})"
