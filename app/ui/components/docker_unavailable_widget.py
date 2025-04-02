from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                           QHBoxLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap

from app.ui.dialogs.docker_setup_dialog import DockerSetupDialog
from app.core.utils.docker_status_checker import DockerStatusChecker, DockerStatus
from app.ui.dialogs.docker_quick_install_dialog import DockerQuickInstallDialog
from app.ui.dialogs.docker_installation_progress_dialog import DockerInstallationProgressDialog

class DockerUnavailableWidget(QWidget):
    """Widget displayed when Docker is not available."""
    
    retry_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_checker = DockerStatusChecker()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Add spacer at top for aesthetic reasons
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Add warning icon and header
        header_layout = QHBoxLayout()
        
        # You could add a Docker icon here if available
        icon_label = QLabel()
        icon_label.setFixedSize(64, 64)
        try:
            # Try to load an icon - could be replaced with an appropriate Docker icon
            pixmap = QPixmap(":/icons/warning.png")
            if not pixmap.isNull():
                icon_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            # Fallback if icon isn't available
            icon_label.setText("⚠️")
            icon_label.setFont(QFont("Arial", 32))
            icon_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addStretch()
        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Check Docker status to provide more specific message
        status, message = self.status_checker.check_docker_status()
        
        # Add title
        title_text = "Docker is not available"
        if status == DockerStatus.INSTALLED_NOT_RUNNING:
            title_text = "Docker is not running"
        elif status == DockerStatus.NOT_INSTALLED:
            title_text = "Docker is not installed"
            
        self.title_label = QLabel(title_text)
        self.title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
        
        # Add description
        if status == DockerStatus.INSTALLED_NOT_RUNNING:
            desc_text = (
                "Docker Engine is installed but not currently running. Please ensure that:\n\n"
                "• Docker service/daemon is running\n"
                "• You have the necessary permissions to access Docker\n"
                "• If using WSL2, ensure the WSL instance is running"
            )
        elif status == DockerStatus.NOT_INSTALLED:
            desc_text = (
                "Docker Engine does not appear to be installed on your system. You need to:\n\n"
                "• Install Docker Engine for your platform\n"
                "• Complete the post-installation steps\n"
                "• Start the Docker daemon"
            )
        else:
            desc_text = (
                "Docker Engine appears to be unavailable. Please ensure that:\n\n"
                "• Docker Engine is installed on your system\n"
                "• Docker daemon is running\n"
                "• You have the necessary permissions to access Docker\n"
                "• Docker API endpoints are accessible"
            )
            
        desc_label = QLabel(desc_text)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Modify button layout to combine quick install and auto-install options
        button_layout = QHBoxLayout()

        # Add combined install button
        install_button = QPushButton("Install Docker")
        install_button.setMinimumWidth(180)
        install_button.setStyleSheet("font-weight: bold; background-color: #0078d7; color: white;")
        install_button.clicked.connect(self.show_install_dialog)
        button_layout.addWidget(install_button)
        
        # Add setup assistant button
        setup_button = QPushButton("Docker Setup Assistant")
        setup_button.setMinimumWidth(150)
        setup_button.clicked.connect(self.show_setup_assistant)
        button_layout.addWidget(setup_button)
        
        # Add retry button
        retry_button = QPushButton("Retry Connection")
        retry_button.setMinimumWidth(150)
        retry_button.clicked.connect(self.retry_requested.emit)
        button_layout.addWidget(retry_button)
        
        layout.addLayout(button_layout)
        
        # Add another spacer at the bottom
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
    
    def show_setup_assistant(self):
        """Show the Docker setup assistant dialog."""
        dialog = DockerSetupDialog(self)
        dialog.docker_check_requested.connect(self.retry_requested.emit)
        dialog.exec_()
    
    def show_install_dialog(self):
        """Show the Docker installation dialog that combines auto and quick install options."""
        dialog = DockerQuickInstallDialog(self)
        dialog.install_requested.connect(self.start_installation)
        dialog.exec_()

    def start_installation(self, config):
        """Start the Docker installation with the provided configuration."""
        progress_dialog = DockerInstallationProgressDialog(config, self)
        progress_dialog.installation_completed.connect(self.on_installation_completed)
        progress_dialog.exec_()

    def on_installation_completed(self, success, message):
        """Handle Docker installation completion."""
        if (success):
            self.retry_requested.emit()  # Check Docker availability again
