from typing import List, Dict, Optional, Callable
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from app.core.services.docker_service import DockerService

class ContainerViewModel(QObject):
    """ViewModel for container operations."""
    
    # Signals
    container_operation_completed = pyqtSignal(bool, str)
    container_details_ready = pyqtSignal(dict)
    container_logs_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, docker_service: DockerService):
        super().__init__()
        self.docker_service = docker_service
    
    @pyqtSlot(str, str)
    def start_container(self, container_id: str, context: str = "default"):
        """Start a container."""
        try:
            success = self.docker_service.start_container(container_id, context)
            # Ensure success is always a boolean, never None
            success = bool(success) if success is not None else False
            message = f"Container {container_id} started successfully" if success else f"Failed to start container {container_id}"
            self.container_operation_completed.emit(success, message)
        except Exception as e:
            # Handle any exceptions and emit failure with error message
            error_message = f"Error starting container {container_id}: {str(e)}"
            self.error_occurred.emit(error_message)
            self.container_operation_completed.emit(False, error_message)
    
    @pyqtSlot(str, str)
    def stop_container(self, container_id: str, context: str = "default"):
        """Stop a container."""
        try:
            success = self.docker_service.stop_container(container_id, context)
            # Ensure success is always a boolean, never None
            success = bool(success) if success is not None else False
            message = f"Container {container_id} stopped successfully" if success else f"Failed to stop container {container_id}"
            self.container_operation_completed.emit(success, message)
        except Exception as e:
            # Handle any exceptions and emit failure with error message
            error_message = f"Error stopping container {container_id}: {str(e)}"
            self.error_occurred.emit(error_message)
            self.container_operation_completed.emit(False, error_message)
    
    @pyqtSlot(str, str)
    def remove_container(self, container_id: str, context: str = "default"):
        """Remove a container."""
        try:
            success = self.docker_service.remove_container(container_id, context)
            # Ensure success is always a boolean, never None
            success = bool(success) if success is not None else False
            message = f"Container {container_id} removed successfully" if success else f"Failed to remove container {container_id}"
            self.container_operation_completed.emit(success, message)
        except Exception as e:
            # Handle any exceptions and emit failure with error message
            error_message = f"Error removing container {container_id}: {str(e)}"
            self.error_occurred.emit(error_message)
            self.container_operation_completed.emit(False, error_message)
    
    @pyqtSlot(str, str)
    def get_container_details(self, container_id: str, context: str = "default"):
        """Get detailed information about a container."""
        try:
            details = self.docker_service.get_container_details(container_id, context)
            self.container_details_ready.emit(details)
        except Exception as e:
            error_message = f"Error getting container details: {str(e)}"
            self.error_occurred.emit(error_message)
            # Emit empty details on error
            self.container_details_ready.emit({})
    
    @pyqtSlot(str, str)
    def get_container_logs(self, container_id: str, context: str = "default"):
        """Get logs from a container."""
        try:
            logs = self.docker_service.get_container_logs(container_id, context)
            self.container_logs_ready.emit(logs)
        except Exception as e:
            error_message = f"Error getting container logs: {str(e)}"
            self.error_occurred.emit(error_message)
            # Emit empty logs on error
            self.container_logs_ready.emit("")
    
    @pyqtSlot(str, str, str)
    def create_container(self, image: str, name: Optional[str] = None, context: str = "default"):
        """Create a new container from an image"""
        try:
            success = self.docker_service.create_container(image, name, context)
            success = bool(success) if success is not None else False
            message = f"Created container from image: {image}" if success else f"Failed to create container from image: {image}"
            self.container_operation_completed.emit(success, message)
        except Exception as e:
            error_message = f"Error creating container from image {image}: {str(e)}"
            self.error_occurred.emit(error_message)
            self.container_operation_completed.emit(False, error_message)
