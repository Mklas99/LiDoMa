import sys
import os
import traceback
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QPushButton, QMessageBox, QTextEdit, QHBoxLayout)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, pyqtSlot, PYQT_VERSION_STR, QT_VERSION_STR

# Add this import at the top
from app.core.utils.logging_config import LoggingConfig

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestWorker(QThread):
    """Test worker thread to verify threading functionality."""
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    # Add progress signal to match app's refresh worker
    progress = pyqtSignal(int)
    
    def __init__(self, task_type):
        super().__init__()
        self.task_type = task_type
        self.is_running = False
    
    def run(self):
        """Execute the test task."""
        try:
            self.is_running = True
            logger.info(f"Worker thread {self.task_type} started - Thread ID: {int(QThread.currentThreadId())}")
            
            if self.task_type == "docker":
                # Try to import and access Docker
                try:
                    from infrastructure.service_locator import ServiceLocator
                    service_locator = ServiceLocator()
                    docker_service = service_locator.get_docker_service()
                    version = docker_service.get_docker_version() if hasattr(docker_service, 'get_docker_version') else "Unknown"
                    result = f"Successfully connected to Docker. Version: {version}"
                except Exception as e:
                    result = f"Docker Error: {str(e)}"
                    logger.error(f"Docker error: {e}")
                    logger.error(traceback.format_exc())
            
            elif self.task_type == "long":
                # Simulate a long-running task
                import time
                for i in range(10):
                    logger.info(f"Long task progress: {i+1}/10")
                    # Emit progress signal
                    self.progress.emit((i+1) * 10)
                    time.sleep(0.5)
                result = "Long-running task completed successfully"
            
            elif self.task_type == "contexts":
                # Test Docker contexts functionality
                try:
                    import subprocess
                    result = subprocess.check_output(["docker", "context", "ls", "--format", "{{.Name}}"]).decode().strip()
                    result = f"Available Docker contexts:\n{result}"
                except Exception as e:
                    result = f"Error listing Docker contexts: {str(e)}"
            
            else:
                # Simple info task
                result = f"Current thread ID: {int(QThread.currentThreadId())}\nMain thread ID: {int(QThread.currentThreadId())}"
            
            logger.info(f"Worker thread {self.task_type} completed")
            self.result_ready.emit(result)
        
        except Exception as e:
            error_msg = f"Error in {self.task_type} thread: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.error_occurred.emit(error_msg)
        finally:
            self.is_running = False

class SimpleDockerManager(QMainWindow):
    """A simplified version of the Docker Manager app to diagnose UI issues."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Docker Manager (Debug Mode)")
        self.resize(800, 600)
        
        # Log thread info
        logger.info(f"UI initialization - Thread ID: {int(QThread.currentThreadId())}")
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add some content
        label = QLabel("Docker Manager Debug Interface")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; margin: 20px;")
        layout.addWidget(label)
        
        # Add a button layout
        button_layout = QHBoxLayout()
        
        # Add a button that will attempt to load the Docker service
        docker_btn = QPushButton("Test Docker Connection")
        docker_btn.clicked.connect(lambda: self.run_test_task("docker"))
        button_layout.addWidget(docker_btn)
        
        # Add a button for testing threading
        thread_btn = QPushButton("Test Threading")
        thread_btn.clicked.connect(lambda: self.run_test_task("info"))
        button_layout.addWidget(thread_btn)
        
        # Add a button for testing long-running tasks
        long_btn = QPushButton("Test Long Task")
        long_btn.clicked.connect(lambda: self.run_test_task("long"))
        button_layout.addWidget(long_btn)
        
        layout.addLayout(button_layout)
        
        # Add a log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)
        
        # Add a button to close
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        # Keep track of worker threads
        self.workers = []
        
        # Log the startup
        self.log("Debug window initialized")
        self.log(f"Main thread ID: {int(QThread.currentThreadId())}")

    def log(self, message):
        """Add a message to the log display."""
        self.log_display.append(message)
    
    def run_test_task(self, task_type):
        """Run a test task in a separate thread."""
        self.log(f"Starting {task_type} task...")
        
        worker = TestWorker(task_type)
        worker.result_ready.connect(self.handle_result)
        worker.error_occurred.connect(self.handle_error)
        worker.finished.connect(lambda: self.cleanup_worker(worker))
        
        # Keep a reference to the worker
        self.workers.append(worker)
        
        # Start the worker
        worker.start()
    
    def handle_result(self, result):
        """Handle the result from a worker thread."""
        self.log(f"Task result: {result}")
    
    def handle_error(self, error):
        """Handle an error from a worker thread."""
        self.log(f"ERROR: {error}")
        QMessageBox.critical(self, "Thread Error", error)
    
    def cleanup_worker(self, worker):
        """Remove the worker from our tracking list."""
        if worker in self.workers:
            self.workers.remove(worker)
    
    def closeEvent(self, event):
        """Handle the window close event."""
        # Clean up any running workers
        for worker in self.workers:
            if worker.isRunning():
                worker.terminate()
                worker.wait()
        
        super().closeEvent(event)

def main():
    """Run the minimal debug version of the app."""
    print("Starting debug Docker Manager...")
    logger.info("Starting debug Docker Manager")
    
    # Apply log level from settings
    LoggingConfig.apply_log_level_from_settings()
    
    app = QApplication(sys.argv)
    
    # Log version information
    logger.info(f"PyQt version: {PYQT_VERSION_STR}")
    logger.info(f"Qt version: {QT_VERSION_STR}")
    
    # Log the main thread ID
    logger.info(f"Main thread ID: {int(QThread.currentThreadId())}")
    
    # Try to load app style if available
    style_path = os.path.join(os.path.dirname(__file__), "presentation", "ui", "style.qss")
    try:
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
            logger.info("Style loaded successfully")
    except Exception as e:
        print(f"Note: Could not load style: {e}")
        logger.warning(f"Could not load style: {e}")
    
    # Create the debug window
    window = SimpleDockerManager()
    
    # Display some debug info
    print(f"Debug window created: {window}")
    logger.info(f"Debug window created")
    
    def check_window():
        if window.isVisible():
            print("Debug window is visible")
            logger.info("Debug window is visible")
        else:
            print("Debug window is NOT visible!")
            logger.warning("Debug window is NOT visible!")
    
    # Set a timer to check window state after 1 second
    QTimer.singleShot(1000, check_window)
    
    # Show and raise the window
    window.show()
    window.raise_()
    
    print("Debug window should now be visible")
    logger.info("Debug window should now be visible")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
