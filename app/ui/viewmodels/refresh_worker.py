"""Worker for refreshing Docker data in a background thread."""
import traceback
import sys
from typing import Dict, List, Tuple
from PyQt5.QtCore import pyqtSignal, QThread, QObject

from app.core.services.docker_service import DockerService

class WorkerSignals(QObject):
    """Signals for the worker thread."""
    error = pyqtSignal(str)  # Changed from tuple to str to avoid traceback issues
    log = pyqtSignal(str)

class RefreshWorker(QThread):
    """Worker thread for refreshing Docker data."""
    
    results_ready = pyqtSignal(list, list, list, list, str)
    
    def __init__(self, docker_service: DockerService):
        """Initialize the refresh worker with the Docker service."""
        super().__init__()
        self.docker_service = docker_service
        self.signals = WorkerSignals()
        self.is_running = False
    
    def run(self):
        """Execute the refresh operation."""
        self.is_running = True
        try:
            # Fetch all Docker resources
            self.signals.log.emit("Fetching containers...")
            containers = self.docker_service.list_containers(True)
            
            self.signals.log.emit("Fetching images...")
            images = self.docker_service.list_images()
            
            self.signals.log.emit("Fetching volumes...")
            volumes = self.docker_service.list_volumes()
            
            self.signals.log.emit("Fetching networks...")
            networks = self.docker_service.list_networks()
            
            # Emit results
            self.results_ready.emit(containers, images, volumes, networks, "")
        
        except Exception as e:
            error_msg = f"Error refreshing Docker data: {str(e)}"
            self.signals.log.emit(error_msg)
            self.signals.error.emit(error_msg)  # Just pass the error message
            self.results_ready.emit([], [], [], [], str(e))
        
        finally:
            self.is_running = False
