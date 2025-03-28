from typing import List, Dict, Tuple, Callable
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from app.core.services.service_locator import ServiceLocator
from app.core.services.docker_service import DockerService
from app.infrastructure.docker_client import DockerCommandExecutor

class MainViewModel(QObject):
    """ViewModel for the main application window"""
    
    # Signals
    refresh_started = pyqtSignal()
    refresh_completed = pyqtSignal(list, list, list, list, str)
    log_message = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    contexts_changed = pyqtSignal(list)
    
    def __init__(self, docker_service: DockerService):
        super().__init__()
        self.docker_service = docker_service
        
    @pyqtSlot()
    def get_docker_contexts(self) -> Tuple[List[str], str]:
        """Get the list of available Docker contexts"""
        contexts, error = self.docker_service.get_docker_contexts()
        if not error:
            self.contexts_changed.emit(contexts)
        return contexts, error
        
    @pyqtSlot(str)
    def set_docker_context(self, context_name: str) -> bool:
        """Set the current Docker context"""
        return self.docker_service.set_context(context_name)
        
    @pyqtSlot(str)
    def log(self, message: str):
        """Log a message to the application log"""
        self.log_message.emit(message)
        
    @pyqtSlot(str)
    def report_error(self, error_message: str):
        """Report an error to be displayed to the user"""
        self.error_occurred.emit(error_message)
        
    @pyqtSlot()
    def get_docker_version(self) -> str:
        """Get the Docker version string"""
        output, _ = DockerCommandExecutor.run_command(["docker", "version", "--format", "{{.Server.Version}}"])
        return output if output else "Unknown"

    @pyqtSlot()
    def get_current_context(self) -> str:
        """Get the current Docker context."""
        return self.docker_service.get_current_context()
