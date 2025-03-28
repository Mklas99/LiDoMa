"""
Service locator for dependency injection and service creation.
"""
from app.domain.repositories import (
    ContainerRepository,
    ImageRepository,
    VolumeRepository,
    NetworkRepository
)
from app.domain.services import (
    DockerContextService,
    DockerComposeService
)

from app.infrastructure.docker_client import DockerClient
from app.infrastructure.repositories import (
    DockerContainerRepository,
    DockerImageRepository,
    DockerVolumeRepository,
    DockerNetworkRepository
)
from app.infrastructure.docker_context_service_impl import DockerContextServiceImpl
from app.infrastructure.docker_compose_service_impl import DockerComposeServiceImpl

from app.core.services.docker_service import DockerService
from app.core.services.container_service import ContainerService
from app.core.services.image_service import ImageService
from app.core.services.volume_service import VolumeService
from app.core.services.network_service import NetworkService

class ServiceLocator:
    """Service locator to manage dependencies and services."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceLocator, cls).__new__(cls)
            cls._instance._initialize_services()
        return cls._instance
    
    def _initialize_services(self):
        """Initialize all services and dependencies."""
        # Create core client
        self.docker_client = DockerClient()
        
        # Create repositories
        self.container_repository = DockerContainerRepository(self.docker_client)
        self.image_repository = DockerImageRepository(self.docker_client)
        self.volume_repository = DockerVolumeRepository(self.docker_client)
        self.network_repository = DockerNetworkRepository(self.docker_client)
        
        # Create services
        self.context_service = DockerContextServiceImpl()
        self.compose_service = DockerComposeServiceImpl()
        
        # Create application services
        self.container_service = ContainerService(self.container_repository)
        self.image_service = ImageService(self.image_repository)
        self.volume_service = VolumeService(self.volume_repository)
        self.network_service = NetworkService(self.network_repository)
        
        # Create facade service
        self.docker_service = DockerService(
            self.context_service,
            self.container_service,
            self.image_service,
            self.volume_service,
            self.network_service
        )
    
    def get_docker_service(self) -> DockerService:
        """Get the Docker service facade."""
        return self.docker_service
    
    def get_container_service(self) -> ContainerService:
        """Get the container service."""
        return self.container_service
    
    def get_image_service(self) -> ImageService:
        """Get the image service."""
        return self.image_service
    
    def get_volume_service(self) -> VolumeService:
        """Get the volume service."""
        return self.volume_service
    
    def get_network_service(self) -> NetworkService:
        """Get the network service."""
        return self.network_service
    
    def get_context_service(self) -> DockerContextService:
        """Get the Docker context service."""
        return self.context_service
        
    def get_compose_service(self) -> DockerComposeService:
        """Get the Docker Compose service."""
        return self.compose_service
