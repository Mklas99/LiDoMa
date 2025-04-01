import os
import logging
from datetime import datetime
from typing import Optional
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import Qt, QObject, pyqtSignal

class ErrorManager(QObject):
    """Centralized manager for handling and displaying critical application errors."""
    
    # Signal to trigger error dialog display from any thread
    error_occurred = pyqtSignal(str, str)
    
    _instance = None
    
    @classmethod
    def instance(cls):
        """Singleton pattern to ensure only one error manager exists."""
        if cls._instance is None:
            cls._instance = ErrorManager()
        return cls._instance
    
    def __init__(self):
        """Initialize the error manager."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Connect the signal to the handler that must run in the main thread
        self.error_occurred.connect(self.show_error_dialog)
        
        # Setup error log directory
        log_dir = os.path.join(os.path.expanduser('~'), '.lidoma', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        self.error_log_path = os.path.join(log_dir, 'docker_errors.log')
        self.logger.info(f"Docker error log will be stored at: {self.error_log_path}")
    
    def log_error(self, error_type: str, message: str):
        """Log error to file with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.error_log_path, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {error_type}: {message}\n")
            
        self.logger.error(f"{error_type}: {message}")
    
    def show_docker_error(self, message: str, details: str = ""):
        """Show a Docker-specific error message dialog."""
        self.log_error("Docker Error", message)
        
        # Emit signal to show error dialog (safe from any thread)
        self.error_occurred.emit("Docker Connectivity Error", 
                                f"{message}\n\n{details}" if details else message)
    
    def show_error_dialog(self, title: str, message: str):
        """Display an error dialog that requires user acknowledgment.
        
        This method must be called from the main thread.
        """
        # Ensure we're on the main thread
        if QApplication.instance().thread() != self.thread():
            self.logger.warning("show_error_dialog called from non-main thread, re-emitting signal")
            # Re-emit the signal to process in main thread
            self.error_occurred.emit(title, message)
            return
            
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        # Add guidance about Docker issues
        if "Docker" in title:
            msg_box.setInformativeText(
                "Docker appears to be unavailable. Please ensure that:\n"
                "1. Docker Desktop is installed\n"
                "2. Docker service is running\n"
                "3. You have proper permissions\n\n"
                "Some features will be unavailable until Docker is properly configured."
            )
        
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setDefaultButton(QMessageBox.Ok)
        msg_box.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        # Modal dialog - blocks until user acknowledges
        msg_box.exec_()
