from PyQt5.QtCore import QThread, pyqtSignal, QObject

from app.infrastructure.docker_client import DockerClient
from app.ui.utils.error_manager import ErrorManager
from app.core.utils.docker_status_checker import DockerStatus

class DockerAvailabilitySignals(QObject):
    """Signals for Docker availability checker."""
    available = pyqtSignal(bool, str)
    error = pyqtSignal(str, str)
    finished = pyqtSignal()
    status_changed = pyqtSignal(DockerStatus, str)
    
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
            
            # Get detailed Docker status
            status, message = docker_client.get_docker_status()
            
            # Emit the detailed status signal
            self.signals.status_changed.emit(status, message)
            
            if status == DockerStatus.RUNNING:
                # Docker is running - get version for additional info
                version = docker_client.get_version()
                self.signals.available.emit(True, f"Docker is available (version: {version})")
            else:
                # Docker is not running - emit appropriate error
                if status == DockerStatus.INSTALLED_NOT_RUNNING:
                    error_msg = "Docker is installed but not running. Use the Docker Setup Assistant to start it."
                elif status == DockerStatus.NOT_INSTALLED:
                    error_msg = "Docker is not installed. Use the Docker Setup Assistant to install it."
                else:
                    error_msg = f"Docker is not available: {message}"
                    
                self.signals.available.emit(False, error_msg)
                
                # Emit detailed error for modal display
                error_title = "Docker Not Available"
                if status == DockerStatus.INSTALLED_NOT_RUNNING:
                    error_title = "Docker Not Running"
                elif status == DockerStatus.NOT_INSTALLED:
                    error_title = "Docker Not Installed"
                    
                self.signals.error.emit(error_title, error_msg)
                
                # Log the error
                self.error_manager.log_error("Docker Availability", error_msg)
                
        except Exception as e:
            error_msg = f"Error checking Docker: {str(e)}"
            self.signals.available.emit(False, error_msg)
            self.signals.error.emit("Docker Check Error", error_msg)
            self.error_manager.log_error("Docker Check Exception", error_msg)
        finally:
            self.is_running = False
            self.signals.finished.emit()
