import logging
from PyQt5.QtWidgets import QMainWindow, QStatusBar

from app.ui.utils.error_manager import ErrorManager
from app.ui.utils.thread_manager import ThreadManager
from app.ui.widgets.enhanced_status_bar import EnhancedStatusBar
from app.ui.viewmodels.docker_availability_checker import DockerAvailabilityChecker

class DockerErrorHandlingMixin:
    """Mixin class for Docker error handling in main windows."""
    
    def setup_docker_error_handling(self):
        """Setup Docker error handling for the main window.
        
        Call this method after the UI is initialized.
        """
        # Ensure this is a QMainWindow
        if not isinstance(self, QMainWindow):
            raise TypeError("DockerErrorHandlingMixin can only be used with QMainWindow")
        
        self.logger = logging.getLogger(__name__)
        
        # Replace standard status bar with enhanced one
        if not hasattr(self, 'status_bar') or not isinstance(self.status_bar, EnhancedStatusBar):
            self.status_bar = EnhancedStatusBar(self)
            self.setStatusBar(self.status_bar)
        
        # Get singletons
        self.error_manager = ErrorManager.instance()
        self.thread_manager = ThreadManager.instance()
        
        # Initialize docker features enabled flag
        self.docker_available = False
        
        # Check Docker availability
        self.check_docker_availability()
        
    def check_docker_availability(self):
        """Check Docker availability and show appropriate messages for errors."""
        # Create availability checker
        docker_checker = DockerAvailabilityChecker(self)
        
        # Connect signals
        docker_checker.signals.available.connect(self.on_docker_availability_checked)
        docker_checker.signals.error.connect(self.on_docker_check_error)
        
        # Start the thread safely with manager
        self.thread_manager.start_thread(docker_checker)
        
    def on_docker_availability_checked(self, available, message):
        """Handle the result of Docker availability check."""
        self.docker_available = available
        
        # Show status message (will disappear after timeout)
        self.status_bar.showMessage(message, 5000)
        
        # Enable/disable Docker-dependent features
        self.update_docker_feature_availability(available)
        
        # Log the status
        self.logger.info(f"Docker availability: {available}, {message}")
        
    def on_docker_check_error(self, error_type, message):
        """Handle Docker availability check errors."""
        # Show persistent error in status bar
        self.status_bar.showPersistentError(f"Docker Error: {message}")
        
        # Store the last error message
        self._last_docker_error = message
        
        # Log the error to help with debugging
        self.logger.error(f"Docker error: {error_type} - {message}")
        
        # Show modal error dialog that requires acknowledgment
        QTimer.singleShot(100, lambda: self.error_manager.show_docker_error(message))
        
        # Disable Docker-dependent features
        self.update_docker_feature_availability(False)
        
    def update_docker_feature_availability(self, available):
        """Update the availability of Docker-dependent features.
        
        Override this method in your main window to enable/disable Docker-
        dependent UI elements based on Docker availability.
        """
        # Default implementation - can be overridden
        if hasattr(self, 'docker_action_group'):
            self.docker_action_group.setEnabled(available)
            
        if hasattr(self, 'docker_menu'):
            self.docker_menu.setEnabled(available)
        
    def closeEvent(self, event):
        """Handle window close event to clean up threads."""
        # Clean up threads
        if hasattr(self, 'thread_manager'):
            self.thread_manager.cleanup_all()
            
        # Call parent implementation (make sure this is properly chained in multi-inheritance)
        super().closeEvent(event)
