from typing import List, Tuple, Dict
from app.domain.services import DockerContextService
from .container_service import ContainerService
from .image_service import ImageService
from .volume_service import VolumeService
from .network_service import NetworkService

class DockerService:
    """Facade service that coordinates all Docker operations."""
    
    def __init__(
        self, 
        context_service: DockerContextService,
        container_service: ContainerService,
        image_service: ImageService,
        volume_service: VolumeService,
        network_service: NetworkService
    ):
        self.context_service = context_service
        self.container_service = container_service
        self.image_service = image_service
        self.volume_service = volume_service
        self.network_service = network_service
        
    def get_docker_contexts(self) -> Tuple[List[str], str]:
        """Get available Docker contexts."""
        return self.context_service.get_contexts()
        
    def get_current_context(self) -> str:
        """Get currently active context."""
        return self.context_service.get_current_context()
        
    def set_context(self, context_name: str) -> bool:
        """Set the current Docker context."""
        return self.context_service.set_context(context_name)
        
    # Container operations delegated to container service
    def list_containers(self, all_containers: bool = True, context: str = "default") -> List[Dict]:
        containers = self.container_service.get_all_containers(context)
        # Convert to serializable dictionaries for the UI
        return [self._container_to_dict(c) for c in containers]
        
    def start_container(self, container_name: str, context: str = "default") -> bool:
        return self.container_service.start_container(container_name, context)
        
    def stop_container(self, container_name: str, context: str = "default") -> bool:
        return self.container_service.stop_container(container_name, context)
        
    def remove_container(self, container_name: str, context: str = "default") -> bool:
        return self.container_service.remove_container(container_name, context)
        
    def create_container(self, image: str, name: str = None, context: str = "default") -> bool:
        return self.container_service.create_container(image, name, context)
        
    def inspect_container(self, container_name: str, context: str = "default") -> dict:
        return self.container_service.get_container_details(container_name, context)
        
    # Image operations delegated to image service
    def list_images(self, context: str = "default") -> List[Dict]:
        images = self.image_service.get_all_images(context)
        # Convert to serializable dictionaries for the UI
        return [self._image_to_dict(i) for i in images]
        
    def remove_image(self, image_id: str, context: str = "default") -> bool:
        return self.image_service.remove_image(image_id, context)
        
    def pull_image(self, image_name: str, tag: str = "latest", context: str = "default") -> bool:
        return self.image_service.pull_image(image_name, tag, context)
        
    # Volume operations delegated to volume service
    def list_volumes(self, context: str = "default") -> List[Dict]:
        volumes = self.volume_service.get_all_volumes(context)
        # Convert to serializable dictionaries for the UI
        return [self._volume_to_dict(v) for v in volumes]
        
    def remove_volume(self, volume_name: str, context: str = "default") -> bool:
        return self.volume_service.remove_volume(volume_name, context)
        
    def create_volume(self, name: str, driver: str = "local", context: str = "default") -> bool:
        return self.volume_service.create_volume(name, driver, context)
        
    # Network operations delegated to network service
    def list_networks(self, context: str = "default") -> List[Dict]:
        networks = self.network_service.get_all_networks(context)
        # Convert to serializable dictionaries for the UI
        return [self._network_to_dict(n) for n in networks]
        
    def remove_network(self, network_name: str, context: str = "default") -> bool:
        return self.network_service.remove_network(network_name, context)
        
    def create_network(self, name: str, driver: str = "bridge", context: str = "default") -> bool:
        return self.network_service.create_network(name, driver, context)
        
    # Helper methods to convert domain models to dictionaries
    def _container_to_dict(self, container) -> Dict:
        """Convert Container model to dictionary for UI."""
        ports_dict = {}
        for port in container.ports:
            if port.host_port:
                if port.container_port not in ports_dict:
                    ports_dict[port.container_port] = []
                ports_dict[port.container_port].append({
                    "HostIp": port.host_ip,
                    "HostPort": port.host_port
                })
                
        return {
            "id": container.id,
            "name": container.name,
            "status": container.status,
            "ports": ports_dict,
            "context": container.context
        }
        
    def _image_to_dict(self, image) -> Dict:
        """Convert Image model to dictionary for UI."""
        return {
            "id": image.id,
            "name": image.name,
            "tags": image.tags,
            "size": image.size,
            "created": image.created.isoformat() if image.created else "",
            "context": image.context
        }
        
    def _volume_to_dict(self, volume) -> Dict:
        """Convert Volume model to dictionary for UI."""
        return {
            "name": volume.name,
            "driver": volume.driver,
            "mountpoint": volume.mountpoint,
            "context": volume.context
        }
        
    def _network_to_dict(self, network) -> Dict:
        """Convert Network model to dictionary for UI."""
        return {
            "name": network.name,
            "id": network.id,
            "driver": network.driver,
            "scope": network.scope,
            "context": network.context
        }
