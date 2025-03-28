from typing import List, Dict, Optional, Callable
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from app.core.services.docker_service import DockerService

class ContainerViewModel(QObject):
    """ViewModel for container operations"""
    
    # Signals
    container_operation_completed = pyqtSignal(bool, str)
    
    def __init__(self, docker_service: DockerService):
        super().__init__()
        self.docker_service = docker_service
        
    @pyqtSlot(str, str)
    def start_container(self, container_name: str, context: str = "default"):
        """Start a container"""
        success = self.docker_service.start_container(container_name, context)
        message = f"Started container: {container_name}" if success else f"Failed to start container: {container_name}"
        self.container_operation_completed.emit(success, message)
        
    @pyqtSlot(str, str)
    def stop_container(self, container_name: str, context: str = "default"):
        """Stop a container"""
        success = self.docker_service.stop_container(container_name, context)
        message = f"Stopped container: {container_name}" if success else f"Failed to stop container: {container_name}"
        self.container_operation_completed.emit(success, message)
    
    @pyqtSlot(str, str)
    def remove_container(self, container_name: str, context: str = "default"):
        """Remove a container"""
        success = self.docker_service.remove_container(container_name, context)
        message = f"Removed container: {container_name}" if success else f"Failed to remove container: {container_name}"
        self.container_operation_completed.emit(success, message)
        
    @pyqtSlot(str, str)
    def get_container_details(self, container_name: str, context: str = "default") -> Dict:
        """Get detailed information about a container"""
        return self.docker_service.inspect_container(container_name, context)
        
    @pyqtSlot(str, str, str)
    def create_container(self, image: str, name: Optional[str] = None, context: str = "default"):
        """Create a new container from an image"""
        success = self.docker_service.create_container(image, name, context)
        message = f"Created container from image: {image}" if success else f"Failed to create container from image: {image}"
        self.container_operation_completed.emit(success, message)
