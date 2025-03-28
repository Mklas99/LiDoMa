from typing import List, Dict, Optional
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from app.core.services.docker_service import DockerService

class ImageViewModel(QObject):
    """ViewModel for image operations"""
    
    # Signals
    image_operation_completed = pyqtSignal(bool, str)
    
    def __init__(self, docker_service: DockerService):
        super().__init__()
        self.docker_service = docker_service
    
    @pyqtSlot(str, str)
    def remove_image(self, image_id: str, context: str = "default"):
        """Remove an image"""
        success = self.docker_service.remove_image(image_id, context)
        message = f"Removed image: {image_id}" if success else f"Failed to remove image: {image_id}"
        self.image_operation_completed.emit(success, message)
        
    @pyqtSlot(str, str, str)
    def pull_image(self, image_name: str, tag: str = "latest", context: str = "default"):
        """Pull an image from a registry"""
        success = self.docker_service.pull_image(image_name, tag, context)
        message = f"Pulled image: {image_name}:{tag}" if success else f"Failed to pull image: {image_name}:{tag}"
        self.image_operation_completed.emit(success, message)
