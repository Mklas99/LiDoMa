from PyQt5.QtCore import QThread, pyqtSignal, QObject

from app.infrastructure.docker_client import DockerClient
from app.ui.utils.error_manager import ErrorManager

class DockerAvailabilitySignals(QObject):
    """Signals for Docker availability checker."""
    available = pyqtSignal(bool, str)
    error = pyqtSignal(str, str)
    finished = pyqtSignal()
    
class DockerAvailabilityChecker(QThread):
    """Worker thread for checking Docker availability."""
    
    def __init__(self, parent=None):
        """Initialize the Docker availability checker worker."""
        super().__init__(parent)
        self.signals = DockerAvailabilitySignals()
        self.is_running = False
        self.error_manager = ErrorManager.instance()
        
    def run(self):
        """Check Docker availability in a background thread."""
        self.is_running = True
        
        try:
            # Create a dedicated Docker client for this check
            docker_client = DockerClient()
            
            # Check connectivity
            docker_available = docker_client.is_connected()
            
            if docker_available:
                version = docker_client.get_version()
                self.signals.available.emit(True, f"Docker is available (version: {version})")
            else:
                error_msg = "Docker is not available. Please ensure Docker is installed and running."
                self.signals.available.emit(False, error_msg)
                
                # Emit detailed error for modal display
                self.signals.error.emit("Docker Connection Error", 
                               "Unable to connect to Docker. Please ensure Docker is installed and running.")
                
                # Log the error
                self.error_manager.log_error("Docker Connectivity", error_msg)
        except Exception as e:
            error_msg = f"Error checking Docker: {str(e)}"
            self.signals.available.emit(False, error_msg)
            self.signals.error.emit("Docker Check Error", error_msg)
            self.error_manager.log_error("Docker Check Exception", error_msg)
        finally:
            self.is_running = False
            self.signals.finished.emit()
