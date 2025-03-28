"""
Domain model for Docker containers.
"""
from typing import List, Dict, Optional
from datetime import datetime

class Port:
    """Model representing a port mapping in a container."""
    
    def __init__(self, container_port: str, host_port: Optional[str] = None, host_ip: str = "0.0.0.0"):
        self.container_port = container_port
        self.host_port = host_port
        self.host_ip = host_ip
        
    def __repr__(self):
        if self.host_port:
            return f"{self.host_ip}:{self.host_port}->{self.container_port}"
        return f"{self.container_port}"

class Container:
    """Domain model representing a Docker container."""
    
    def __init__(
        self,
        id: str,
        name: str,
        image: str,
        status: str,
        created: datetime,
        ports: List[Port] = None,
        networks: List[str] = None,
        labels: Dict[str, str] = None,
        context: str = "default"
    ):
        self.id = id
        self.name = name
        self.image = image
        self.status = status
        self.created = created
        self.ports = ports or []
        self.networks = networks or []
        self.labels = labels or {}
        self.context = context
        
    def __repr__(self):
        return f"Container({self.name}, {self.id[:12]}, {self.status})"
