from typing import List, Dict, Optional
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from app.core.services.docker_service import DockerService

class VolumeViewModel(QObject):
    """ViewModel for volume operations"""
    
    # Signals
    volume_operation_completed = pyqtSignal(bool, str)
    
    def __init__(self, docker_service: DockerService):
        super().__init__()
        self.docker_service = docker_service
    
    @pyqtSlot(str, str)
    def remove_volume(self, volume_name: str, context: str = "default"):
        """Remove a volume"""
        success = self.docker_service.remove_volume(volume_name, context)
        message = f"Removed volume: {volume_name}" if success else f"Failed to remove volume: {volume_name}"
        self.volume_operation_completed.emit(success, message)
        
    @pyqtSlot(str, str, str)
    def create_volume(self, name: str, driver: str = "local", context: str = "default"):
        """Create a new volume"""
        success = self.docker_service.create_volume(name, driver, context)
        message = f"Created volume: {name}" if success else f"Failed to create volume: {name}"
        self.volume_operation_completed.emit(success, message)
