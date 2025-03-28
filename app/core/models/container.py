from dataclasses import dataclass, field
from typing import Dict, Optional, List

@dataclass
class Port:
    container_port: str
    host_port: Optional[str] = None
    host_ip: Optional[str] = "0.0.0.0"

@dataclass
class Container:
    id: str
    name: str
    status: str
    image: str
    context: str = "default"
    ports: List[Port] = field(default_factory=list)
    
    @property
    def is_running(self) -> bool:
        return "running" in self.status.lower()
        
    @property
    def is_exited(self) -> bool:
        return "exited" in self.status.lower() or "stopped" in self.status.lower()
        
    @property
    def is_created(self) -> bool:
        return "created" in self.status.lower()
