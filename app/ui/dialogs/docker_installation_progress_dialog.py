import os
import platform
import subprocess
import tempfile
import time
import shutil
import requests
import sys
from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                           QProgressBar, QTextEdit, QHBoxLayout, QScrollArea, QWidget, QFrame, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont
from app.core.docker.installation.step_manager import InstallationStepManager
from app.core.docker.installation.steps.windows_steps import WindowsWSL2Step, WindowsDockerEngineStep
from app.core.docker.installation.steps.mac_steps import HomebrewInstallStep, DockerCLIInstallStep, ColimaInstallStep, ColimaStartStep, DesktopDownloadStep, DesktopInstallStep
from app.core.docker.installation.steps.linux_steps import DetectDistroStep, DockerPackageStep, DockerVerificationStep
from app.core.docker.common.state_verifier import InstallationStateVerifier

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
        self.step_manager = None  # Make step_manager an instance attribute
    
    def run(self):
        """Run the installation process with pre-flight checks."""
        try:
            self.log_message.emit("Starting Docker installation...")
            
            # Perform pre-flight checks
            if not self.pre_flight_checks():
                self.installation_completed.emit(False, "Pre-flight checks failed")
                return
            
            # Check if using auto mode
            auto_mode = self.config.get("auto_mode", False)
            self.log_message.emit(f"Installation mode: {'Automatic' if auto_mode else 'Custom'}")
            
            # Platform-specific installation
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
    
    def pre_flight_checks(self):
        """Perform pre-flight checks to ensure system prerequisites are met."""
        self.log_message.emit("Performing pre-flight checks...")
        try:
            # Example: Check if sufficient disk space is available
            if shutil.disk_usage("/").free < 2 * 1024 * 1024 * 1024:  # 2GB
                self.log_message.emit("ERROR: Not enough disk space available")
                return False
            
            # Example: Check if required tools are installed (excluding Docker)
            required_tools = ["curl"]
            for tool in required_tools:
                if shutil.which(tool) is None:
                    self.log_message.emit(f"ERROR: Required tool '{tool}' is not installed")
                    return False
            
            self.log_message.emit("Pre-flight checks passed")
            return True
        except Exception as e:
            self.log_message.emit(f"ERROR during pre-flight checks: {str(e)}")
            return False
    
    def install_on_windows(self):
        """Install Docker on Windows using step-based architecture."""
        self.progress_updated.emit(5, "Preparing Windows environment...")
        temp_resources = []  # Track resources to clean up
        
        try:
            self.step_manager = InstallationStepManager(self)
            # Add steps
            self.step_manager.add_step(WindowsWSL2Step(self))
            self.step_manager.add_step(WindowsDockerEngineStep(self))
            
            # Execute all steps with rollback and cleanup
            success, message = self.step_manager.execute_steps()
            
            # Verify completion of each step
            for step in self.step_manager.completed_steps:
                InstallationStateVerifier.verify_step_completion(step, self)
            
            return success, message
        except Exception as e:
            self.log_message.emit(f"ERROR: {str(e)}")
            return False, f"Failed to install Docker: {str(e)}"
        finally:
            # Clean up all registered resources
            for resource in temp_resources:
                if os.path.exists(resource):
                    try:
                        shutil.rmtree(resource) if os.path.isdir(resource) else os.remove(resource)
                        self.log_message.emit(f"Cleaned up temporary resource: {resource}")
                    except Exception as e:
                        self.log_message.emit(f"Warning: Failed to clean up {resource}: {str(e)}")
            if self.step_manager:
                self.step_manager.verify_system_state()
    
    def install_on_mac(self):
        """Install Docker on macOS using step-based architecture."""
        self.progress_updated.emit(5, "Preparing macOS environment...")
        temp_resources = []  # Track resources to clean up
        
        try:
            self.step_manager = InstallationStepManager(self)
            
            # Add steps
            self.step_manager.add_step(HomebrewInstallStep(self))
            self.step_manager.add_step(DockerCLIInstallStep(self))
            self.step_manager.add_step(ColimaInstallStep(self))
            
            # Execute all steps with rollback and cleanup
            success, message = self.step_manager.execute_steps()
            
            # Verify completion of each step
            for step in self.step_manager.completed_steps:
                InstallationStateVerifier.verify_step_completion(step, self)
            
            return success, message
        except Exception as e:
            self.log_message.emit(f"ERROR: {str(e)}")
            return False, f"Failed to install Docker: {str(e)}"
        finally:
            # Clean up all registered resources
            for resource in temp_resources:
                if os.path.exists(resource):
                    try:
                        shutil.rmtree(resource) if os.path.isdir(resource) else os.remove(resource)
                        self.log_message.emit(f"Cleaned up temporary resource: {resource}")
                    except Exception as e:
                        self.log_message.emit(f"Warning: Failed to clean up {resource}: {str(e)}")
            if self.step_manager:
                self.step_manager.verify_system_state()
    
    def install_on_linux(self):
        """Install Docker on Linux using step-based architecture."""
        self.progress_updated.emit(5, "Preparing Linux environment...")
        temp_resources = []  # Track resources to clean up
        
        try:
            # Get installation options
            add_user = self.config.get("add_user", True) if not self.config.get("auto_mode", False) else True
            auto_start = self.config.get("autostart", True) if not self.config.get("auto_mode", False) else True
            
            self.step_manager = InstallationStepManager(self)
            
            # Add steps
            detect_distro_step = DetectDistroStep(self)
            self.step_manager.add_step(detect_distro_step)
            self.step_manager.add_step(DockerPackageStep(self, detect_distro_step.distro, add_user, auto_start))
            self.step_manager.add_step(DockerVerificationStep(self, add_user))
            
            # Register temporary resources
            temp_script = tempfile.NamedTemporaryFile(delete=False, suffix=".sh").name
            temp_resources.append(temp_script)
            
            # Verify prerequisites for each step
            for step in self.step_manager.steps:
                InstallationStateVerifier.verify_step_prerequisites(step, self)
            
            # Execute all steps with built-in rollback
            success, message = self.step_manager.execute_steps()
            
            # Verify completion of each step
            for step in self.step_manager.completed_steps:
                InstallationStateVerifier.verify_step_completion(step, self)
            
            return success, message
        except Exception as e:
            self.log_message.emit(f"ERROR: {str(e)}")
            return False, f"Failed to install Docker: {str(e)}"
        finally:
            # Clean up all registered resources
            for resource in temp_resources:
                if os.path.exists(resource):
                    try:
                        shutil.rmtree(resource) if os.path.isdir(resource) else os.remove(resource)
                        self.log_message.emit(f"Cleaned up temporary resource: {resource}")
                    except Exception as e:
                        self.log_message.emit(f"Warning: Failed to clean up {resource}: {str(e)}")
            if self.step_manager:
                self.step_manager.verify_system_state()
    
    def download_file(self, url, destination):
        """Download a file from a URL to a destination with progress updates."""
        self.log_message.emit(f"Downloading {url} to {destination}")
        
        try:
            # Start download
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get file size if available
            total_size = int(response.headers.get('content-length', 0))
            
            # Open destination file and download
            downloaded_size = 0
            with open(destination, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if self.cancelled:
                        return False
                    
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Update progress if we know the total size
                        if total_size > 0:
                            progress_percent = int(downloaded_size * 100 / total_size)
                            self.progress_updated.emit(progress_percent, f"Downloading: {progress_percent}%")
            
            self.log_message.emit("Download completed")
            return True
            
        except Exception as e:
            self.log_message.emit(f"ERROR: Download failed: {str(e)}")
            raise
    
    def get_linux_distro(self):
        """Detect the Linux distribution."""
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    for line in f:
                        if line.startswith("ID="):
                            return line.split("=")[1].strip().strip('"')
            
            # Fallbacks
            if os.path.exists("/etc/debian_version"):
                return "debian"
            elif os.path.exists("/etc/fedora-release"):
                return "fedora"
            elif os.path.exists("/etc/centos-release"):
                return "centos"
            elif os.path.exists("/etc/redhat-release"):
                return "rhel"
                
            return "unknown"
        except:
            return "unknown"

    def cancel(self):
        """Cancel the installation process and trigger rollback."""
        self.cancelled = True
        self.log_message.emit("Installation cancelled by user.")
        if self.step_manager:
            self.step_manager.rollback_steps()

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

    def add_info_section(self, layout, title, items):
        """Add a section to the info panel with a title and list of items."""
        section_title = QLabel(title)
        title_font = QFont()
        title_font.setBold(True)
        section_title.setFont(title_font)
        layout.addWidget(section_title)
        
        for name, description in items:
            item_layout = QVBoxLayout()
            name_label = QLabel(f"• {name}")
            name_font = QFont()
            name_font.setItalic(True)
            name_label.setFont(name_font)
            item_layout.addWidget(name_label)
            
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setIndent(15)
            item_layout.addWidget(desc_label)
            
            # Add the item layout to the main layout
            layout.addLayout(item_layout)
        
        # Add some space after each section
        spacer = QLabel("")
        spacer.setMinimumHeight(10)
        layout.addWidget(spacer)
    
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
