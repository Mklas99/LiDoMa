import os
import platform
import subprocess
import tempfile
import time
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                           QProgressBar, QTextEdit, QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont

class InstallationWorker(QThread):
    """Worker thread for Docker installation."""
    progress_updated = pyqtSignal(int, str)
    log_message = pyqtSignal(str)
    installation_completed = pyqtSignal(bool, str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.current_platform = platform.system().lower()
        self.cancelled = False
    
    def run(self):
        """Run the installation process based on platform."""
        try:
            self.log_message.emit("Starting Docker installation...")
            
            # Check if using auto mode
            auto_mode = self.config.get("auto_mode", False)
            self.log_message.emit(f"Installation mode: {'Automatic' if auto_mode else 'Custom'}")
            
            if self.current_platform == "windows":
                success, message = self.install_on_windows()
            elif self.current_platform == "darwin":  # macOS
                success, message = self.install_on_mac()
            elif self.current_platform == "linux":
                success, message = self.install_on_linux()
            else:
                success, message = False, f"Unsupported platform: {self.current_platform}"
                
            self.installation_completed.emit(success, message)
            
        except Exception as e:
            self.log_message.emit(f"ERROR: {str(e)}")
            self.installation_completed.emit(False, f"Installation failed: {str(e)}")
    
    def install_on_windows(self):
        """Install Docker on Windows."""
        # Implementation would go here - this is a placeholder
        self.progress_updated.emit(10, "Preparing Windows environment...")
        self.log_message.emit("Starting Windows Docker installation...")
        # Simulate installation steps
        for i in range(10, 100, 10):
            if self.cancelled:
                return False, "Installation cancelled"
            time.sleep(1)
            self.progress_updated.emit(i, f"Installation progress: {i}%")
        return True, "Docker installation completed successfully on Windows"
    
    def install_on_mac(self):
        """Install Docker on macOS."""
        # Implementation would go here - this is a placeholder
        self.progress_updated.emit(10, "Preparing macOS environment...")
        self.log_message.emit("Starting macOS Docker installation...")
        # Simulate installation steps
        for i in range(10, 100, 10):
            if self.cancelled:
                return False, "Installation cancelled"
            time.sleep(1)
            self.progress_updated.emit(i, f"Installation progress: {i}%")
        return True, "Docker installation completed successfully on macOS"
    
    def install_on_linux(self):
        """Install Docker on Linux."""
        # Implementation would go here - this is a placeholder
        self.progress_updated.emit(10, "Preparing Linux environment...")
        self.log_message.emit("Starting Linux Docker installation...")
        # Simulate installation steps
        for i in range(10, 100, 10):
            if self.cancelled:
                return False, "Installation cancelled"
            time.sleep(1)
            self.progress_updated.emit(i, f"Installation progress: {i}%")
        return True, "Docker installation completed successfully on Linux"
    
    def cancel(self):
        """Cancel the installation process."""
        self.cancelled = True
        self.log_message.emit("Installation cancelled by user.")

class DockerInstallationProgressDialog(QDialog):
    """Dialog for monitoring Docker installation progress."""
    
    installation_completed = pyqtSignal(bool, str)
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Installing Docker")
        self.setMinimumSize(600, 400)
        self.setup_ui()
        self.start_installation()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Docker Installation")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Status label
        self.status_label = QLabel("Preparing installation...")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Log display
        log_label = QLabel("Installation Log:")
        layout.addWidget(log_label)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setMinimumHeight(200)
        layout.addWidget(self.log_display)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_installation)
        button_layout.addWidget(self.cancel_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def start_installation(self):
        """Start the Docker installation process."""
        self.worker = InstallationWorker(self.config)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.log_message.connect(self.add_log_message)
        self.worker.installation_completed.connect(self.on_installation_completed)
        self.worker.start()
    
    def update_progress(self, value, message):
        """Update the progress bar and status message."""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def add_log_message(self, message):
        """Add a message to the log display."""
        self.log_display.append(message)
        # Auto-scroll to bottom
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )
    
    def on_installation_completed(self, success, message):
        """Handle installation completion."""
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("Installation completed successfully")
            self.add_log_message(f"SUCCESS: {message}")
        else:
            self.status_label.setText("Installation failed")
            self.add_log_message(f"ERROR: {message}")
        
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)
        self.installation_completed.emit(success, message)
    
    def cancel_installation(self):
        """Cancel the installation process."""
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.cancel()
            self.cancel_button.setEnabled(False)
            self.status_label.setText("Cancelling installation...")
