import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtWidgets import QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import Qt

from app.ui.mixins.docker_error_handling_mixin import DockerErrorHandlingMixin
from app.ui.utils.error_manager import ErrorManager
from app.ui.utils.thread_manager import ThreadManager
from app.ui.widgets.enhanced_status_bar import EnhancedStatusBar

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DockerErrorDebug")

class DockerErrorDebugApp(QMainWindow, DockerErrorHandlingMixin):
    """Debug app to test Docker error handling."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Docker Error Handling Debug")
        self.resize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add a title
        label = QLabel("Docker Error Handling Debug Interface")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; margin: 20px;")
        layout.addWidget(label)
        
        # Add a button layout
        button_layout = QHBoxLayout()
        
        # Add a button that will check Docker availability
        docker_btn = QPushButton("Check Docker Availability")
        docker_btn.clicked.connect(self.check_docker_availability)
        button_layout.addWidget(docker_btn)
        
        # Add a button to simulate a Docker error
        error_btn = QPushButton("Simulate Docker Error")
        error_btn.clicked.connect(self.simulate_docker_error)
        button_layout.addWidget(error_btn)
        
        # Add a button to clear status messages
        clear_btn = QPushButton("Clear Status")
        clear_btn.clicked.connect(self.clear_status)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # Add a log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)
        
        # Add a button to close
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        # Initialize the Docker error handling
        self.setup_docker_error_handling()
        
        # Log the startup
        self.log("Debug window initialized")

    def log(self, message):
        """Add a message to the log display."""
        self.log_display.append(message)
        
    def simulate_docker_error(self):
        """Simulate a Docker error for testing."""
        self.log("Simulating Docker error...")
        
        # Simulate an error
        error_message = "This is a simulated Docker error for testing purposes"
        
        # Show persistent error in status bar
        self.status_bar.showPersistentError(f"Docker Error: {error_message}")
        
        # Show error dialog requiring acknowledgment
        ErrorManager.instance().show_docker_error(error_message)
        
    def clear_status(self):
        """Clear all status messages."""
        self.log("Clearing status messages...")
        self.status_bar.clearMessage()
        self.status_bar.clear_error()
        
    def on_docker_availability_checked(self, available, message):
        """Override to add logging to the UI."""
        super().on_docker_availability_checked(available, message)
        self.log(f"Docker availability: {available}, {message}")
        
    def on_docker_check_error(self, error_type, message):
        """Override to add logging to the UI."""
        super().on_docker_check_error(error_type, message)
        self.log(f"Docker error: {error_type} - {message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DockerErrorDebugApp()
    window.show()
    sys.exit(app.exec_())
