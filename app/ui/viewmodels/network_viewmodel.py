from typing import List, Dict, Optional
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from app.core.services.docker_service import DockerService

class NetworkViewModel(QObject):
    """ViewModel for network operations"""
    
    # Signals
    network_operation_completed = pyqtSignal(bool, str)
    
    def __init__(self, docker_service: DockerService):
        super().__init__()
        self.docker_service = docker_service
    
    @pyqtSlot(str, str)
    def remove_network(self, network_name: str, context: str = "default"):
        """Remove a network"""
        success = self.docker_service.remove_network(network_name, context)
        message = f"Removed network: {network_name}" if success else f"Failed to remove network: {network_name}"
        self.network_operation_completed.emit(success, message)
        
    @pyqtSlot(str, str, str)
    def create_network(self, name: str, driver: str = "bridge", context: str = "default"):
        """Create a new network"""
        success = self.docker_service.create_network(name, driver, context)
        message = f"Created network: {name}" if success else f"Failed to create network: {name}"
        self.network_operation_completed.emit(success, message)
