from typing import List, Optional, Dict, Any
import json
from datetime import datetime

from app.domain.models import Container, Port
from app.domain.repositories import ContainerRepository
from app.infrastructure.docker_client import DockerClient, DockerCommandExecutor

class DockerContainerRepository(ContainerRepository):
    """Implementation of ContainerRepository using Docker SDK and CLI."""
    
    def __init__(self, docker_client: DockerClient):
        self.docker_client = docker_client
    
    def list_containers(self, all_containers: bool = True, context: str = "default") -> List[Container]:
        """List all containers."""
        if context != "default":
            return self._get_containers_for_context(context)
            
        try:
            containers = self.docker_client.client.containers.list(all=all_containers)
            result = []
            
            for c in containers:
                ports = []
                ports_dict = c.attrs.get("NetworkSettings", {}).get("Ports", {})
                
                for container_port, host_bindings in ports_dict.items():
                    if host_bindings:
                        for binding in host_bindings:
                            ports.append(Port(
                                container_port=container_port,
                                host_port=binding.get("HostPort"),
                                host_ip=binding.get("HostIp", "0.0.0.0")
                            ))
                    else:
                        ports.append(Port(container_port=container_port))
                
                # Get image name safely
                image_name = ""
                if hasattr(c, 'image') and hasattr(c.image, 'tags') and c.image.tags:
                    image_name = c.image.tags[0]
                elif hasattr(c, 'image') and hasattr(c.image, 'id'):
                    image_name = c.image.id

                # Try to get created timestamp safely
                try:
                    created_ts = int(c.attrs.get("Created", 0)) 
                    created_date = datetime.fromtimestamp(created_ts)
                except (ValueError, TypeError):
                    # If created is not a valid timestamp
                    created_date = datetime.now()
                
                # Create Container object with the data
                container = Container(
                    id=c.id,
                    name=c.name,
                    image=image_name,
                    status=c.status,
                    created=created_date,
                    ports=ports,
                    networks=list(c.attrs.get("NetworkSettings", {}).get("Networks", {}).keys()),
                    labels=c.labels,
                    context="default"
                )
                result.append(container)
            
            return result
                
        except Exception as e:
            print(f"Error listing containers: {str(e)}")
            return []
    
    # Add other required methods from the interface
    def get_container(self, container_id: str, context: str = "default") -> Optional[Container]:
        """Get a specific container by ID."""
        pass
        
    def start_container(self, container_id: str, context: str = "default") -> bool:
        """Start a container."""
        pass
        
    def stop_container(self, container_id: str, context: str = "default") -> bool:
        """Stop a container."""
        pass
        
    def remove_container(self, container_id: str, context: str = "default") -> bool:
        """Remove a container."""
        pass
    
    def create_container(self, image_id: str, name: Optional[str] = None, 
                       context: str = "default", **kwargs) -> bool:
        """Create a new container."""
        pass
        
    def get_container_details(self, container_id: str, context: str = "default") -> Dict[str, Any]:
        """Get detailed container information."""
        try:
            if context != "default":
                # Use CLI for non-default contexts
                output, err = DockerCommandExecutor.run_command([
                    "docker", "--context", context, "container", "inspect", container_id
                ])
                
                if err:
                    return {}
                    
                try:
                    return json.loads(output)[0]
                except (json.JSONDecodeError, IndexError):
                    return {}
            
            # Use SDK for default context
            if not self.docker_client or not self.docker_client.client:
                return {}
                
            container = self.docker_client.client.containers.get(container_id)
            return container.attrs
        except Exception as e:
            print(f"Error getting container details: {str(e)}")
            return {}
        
    def _get_containers_for_context(self, context: str) -> List[Container]:
        """Get containers for a specific Docker context using CLI."""
        pass
