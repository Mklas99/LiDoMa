from typing import List, Tuple, Dict, Optional
import logging
from app.domain.services import DockerContextService
from .container_service import ContainerService
from .image_service import ImageService
from .volume_service import VolumeService
from .network_service import NetworkService
from app.infrastructure.docker_client import DockerCommandExecutor

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
        self.logger = logging.getLogger(__name__)
        
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
        """Get all containers."""
        try:
            # Special handling for "All" context
            if context == "All":
                all_containers_list = []
                
                # Get list of all available contexts
                contexts, _ = self.get_docker_contexts()
                
                # Get containers from each context
                for ctx in contexts:
                    if ctx == "All":  # Skip the "All" pseudo-context
                        continue
                        
                    try:
                        ctx_containers = self.container_service.get_all_containers(ctx)
                        # Ensure context is set correctly for each container
                        for container in ctx_containers:
                            container.context = ctx
                        
                        self.logger.info(f"Found {len(ctx_containers)} containers in context '{ctx}'")
                        all_containers_list.extend(ctx_containers)
                    except Exception as e:
                        self.logger.warning(f"Failed to get containers from context {ctx}: {e}")
                        continue
                        
                # Convert to serializable dictionaries for the UI
                result = [self._container_to_dict(c) for c in all_containers_list]
                self.logger.info(f"Returning {len(result)} containers from all contexts")
                return result
            
            # Normal processing for specific context
            containers = self.container_service.get_all_containers(context)
            result = [self._container_to_dict(c) for c in containers]
            self.logger.info(f"Returning {len(result)} containers from context '{context}'")
            return result
        except Exception as e:
            self.logger.error(f"Error listing containers: {str(e)}")
            return []
        
    def start_container(self, container_name: str, context: str = "default") -> bool:
        """Start a container."""
        try:
            result = self.container_service.start_container(container_name, context)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error starting container {container_name}: {str(e)}")
            return False
        
    def stop_container(self, container_name: str, context: str = "default") -> bool:
        """Stop a container."""
        try:
            result = self.container_service.stop_container(container_name, context)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error stopping container {container_name}: {str(e)}")
            return False
    
    def remove_container(self, container_name: str, context: str = "default") -> bool:
        """Remove a container."""
        try:
            result = self.container_service.remove_container(container_name, context)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error removing container {container_name}: {str(e)}")
            return False
    
    def create_container(self, image: str, name: str = None, context: str = "default") -> bool:
        """Create a new container."""
        try:
            result = self.container_service.create_container(image, name, context)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error creating container from image {image}: {str(e)}")
            return False
        
    def inspect_container(self, container_name: str, context: str = "default") -> dict:
        return self.container_service.get_container_details(container_name, context)
        
    def get_container_details(self, container_id: str, context: str = "default") -> Dict:
        """Get detailed information about a container."""
        try:
            return self.container_service.get_container_details(container_id, context)
        except Exception as e:
            self.logger.error(f"Error getting container details: {str(e)}")
            return {}
            
    def get_container_logs(self, container_id: str, context: str = "default") -> str:
        """Get logs from a container."""
        try:
            return self.container_service.get_container_logs(container_id, context)
        except Exception as e:
            self.logger.error(f"Error getting container logs: {str(e)}")
            return f"Error retrieving logs: {str(e)}"
        
    # Image operations delegated to image service
    def list_images(self, context: str = "default") -> List[Dict]:
        """Get all images."""
        try:
            # Special handling for "All" context
            if context == "All":
                all_images_list = []
                
                # Get list of all available contexts
                contexts, _ = self.get_docker_contexts()
                
                # Get images from each context
                for ctx in contexts:
                    try:
                        ctx_images = self.image_service.get_all_images(ctx)
                        # Ensure context is set correctly for each image
                        for image in ctx_images:
                            image.context = ctx
                        
                        self.logger.info(f"Found {len(ctx_images)} images in context '{ctx}'")
                        all_images_list.extend(ctx_images)
                    except Exception as e:
                        self.logger.warning(f"Failed to get images from context {ctx}: {e}")
                        continue
                        
                # Convert to serializable dictionaries for the UI
                result = [self._image_to_dict(i) for i in all_images_list]
                self.logger.info(f"Returning {len(result)} images from all contexts")
                return result
            
            # Normal processing for specific context
            images = self.image_service.get_all_images(context)
            result = [self._image_to_dict(i) for i in images]
            self.logger.info(f"Returning {len(result)} images from context '{context}'")
            return result
        except Exception as e:
            self.logger.error(f"Error listing images: {str(e)}")
            return []
        
    def remove_image(self, image_id: str, context: str = "default") -> bool:
        """Remove an image."""
        try:
            result = self.image_service.remove_image(image_id, context)
            return bool(result)
        except Exception as e:
            self.logger.error(f"Error removing image {image_id}: {str(e)}")
            return False
        
    def pull_image(self, image_name: str, context: str = "default") -> tuple[bool, Optional[str]]:
        """Pull an image from registry."""
        if not image_name:
            return False, "Image name cannot be empty"
            
        try:
            # Properly delegate to image_service
            return self.image_service.pull_image(image_name, context)
        except Exception as e:
            # Ensure the full error message is preserved and returned
            error_message = str(e)
            self.logger.error(f"Error pulling image {image_name}: {error_message}")
            return False, error_message
        
    # Volume operations delegated to volume service
    def list_volumes(self, context: str = "default") -> List[Dict]:
        """Get all volumes."""
        try:
            # Special handling for "All" context
            if context == "All":
                all_volumes_list = []
                
                # Get list of all available contexts
                contexts, _ = self.get_docker_contexts()
                
                # Get volumes from each context
                for ctx in contexts:
                    try:
                        ctx_volumes = self.volume_service.get_all_volumes(ctx)
                        # Ensure context is set correctly for each volume
                        for volume in ctx_volumes:
                            volume.context = ctx
                        
                        self.logger.info(f"Found {len(ctx_volumes)} volumes in context '{ctx}'")
                        all_volumes_list.extend(ctx_volumes)
                    except Exception as e:
                        self.logger.warning(f"Failed to get volumes from context {ctx}: {e}")
                        continue
                        
                # Convert to serializable dictionaries for the UI
                result = [self._volume_to_dict(v) for v in all_volumes_list]
                self.logger.info(f"Returning {len(result)} volumes from all contexts")
                return result
                
            # Normal processing for specific context
            volumes = self.volume_service.get_all_volumes(context)
            result = [self._volume_to_dict(v) for v in volumes]
            self.logger.info(f"Returning {len(result)} volumes from context '{context}'")
            return result
        except Exception as e:
            self.logger.error(f"Error listing volumes: {str(e)}")
            return []
        
    def remove_volume(self, volume_name: str, context: str = "default") -> bool:
        return self.volume_service.remove_volume(volume_name, context)
        
    def create_volume(self, name: str, driver: str = "local", context: str = "default") -> bool:
        return self.volume_service.create_volume(name, driver, context)
        
    # Network operations delegated to network service
    def list_networks(self, context: str = "default") -> List[Dict]:
        """Get all networks."""
        try:
            # Special handling for "All" context
            if context == "All":
                all_networks_list = []
                
                # Get list of all available contexts
                contexts, _ = self.get_docker_contexts()
                
                # Get networks from each context
                for ctx in contexts:
                    try:
                        ctx_networks = self.network_service.get_all_networks(ctx)
                        
                        # Ensure context is set correctly for each network
                        for network in ctx_networks:
                            network.context = ctx
                        
                        self.logger.info(f"Found {len(ctx_networks)} networks in context '{ctx}'")
                        all_networks_list.extend(ctx_networks)
                    except Exception as e:
                        self.logger.warning(f"Failed to get networks from context {ctx}: {e}")
                        continue
                        
                # Convert to serializable dictionaries for the UI
                result = [self._network_to_dict(n) for n in all_networks_list]
                self.logger.info(f"Returning {len(result)} networks from all contexts")
                return result
                
            # Normal processing for specific context
            networks = self.network_service.get_all_networks(context)
            result = [self._network_to_dict(n) for n in networks]
            self.logger.info(f"Returning {len(result)} networks from context '{context}'")
            return result
        except Exception as e:
            self.logger.error(f"Error listing networks: {str(e)}")
            return []
        
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
            "image": container.image if hasattr(container, "image") else "",
            "status": container.status,
            "ports": ports_dict,
            "context": container.context  # Make sure context is always included
        }
        
    def _image_to_dict(self, image) -> Dict:
        """Convert Image model to dictionary for UI."""
        return {
            "id": image.id,
            "name": image.name,
            "tags": image.tags,
            "size": image.size,
            "created": image.created.isoformat() if image.created else "",
            "context": image.context  # Make sure context is always included
        }
        
    def _volume_to_dict(self, volume) -> Dict:
        """Convert Volume model to dictionary for UI."""
        return {
            "name": volume.name,
            "driver": volume.driver,
            "mountpoint": volume.mountpoint,
            "context": volume.context  # Make sure context is always included
        }
        
    def _network_to_dict(self, network) -> Dict:
        """Convert Network model to dictionary for UI."""
        return {
            "name": network.name,
            "id": network.id,
            "driver": network.driver,
            "scope": network.scope,
            "context": network.context  # Make sure context is always included
        }
        
    # Helper to get docker version directly
    def get_docker_version(self) -> str:
        """Get Docker version."""
        try:
            from app.infrastructure.docker_client import DockerClient
            # Try to get from docker_client if it exists
            client = getattr(self.image_service, "image_repository", None)
            if client and hasattr(client, "docker_client"):
                client = client.docker_client
                if hasattr(client, "get_version") and callable(client.get_version):
                    version = client.get_version()
                    if version:
                        return version
            
            # Fallback to CLI
            output, _ = DockerCommandExecutor.run_command(["docker", "version", "--format", "{{.Server.Version}}"])
            return output if output else "Unknown"
        except Exception as e:
            self.logger.error(f"Error getting Docker version: {e}")
            return "Unknown"