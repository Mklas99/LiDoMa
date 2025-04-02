import platform
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QComboBox, QFormLayout, QCheckBox,
                             QTabWidget, QWidget, QRadioButton, QButtonGroup,
                             QSpacerItem, QSizePolicy, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class DockerQuickInstallDialog(QDialog):
    """Dialog for Docker installation configuration with auto and manual options."""
    
    install_requested = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Docker Installation")
        self.setMinimumWidth(600)
        self.current_system = platform.system().lower()
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI components."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Docker Installation")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Description
        description = QLabel(
            "This utility will help you install Docker on your system. "
            "You can choose between automatic installation with recommended settings "
            "or customize the installation options."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Installation mode selection
        mode_group = QGroupBox("Installation Mode")
        mode_layout = QVBoxLayout(mode_group)
        
        self.auto_mode_radio = QRadioButton("Automatic Installation (Recommended)")
        self.auto_mode_radio.setChecked(True)
        self.auto_mode_radio.toggled.connect(self.toggle_installation_mode)
        mode_layout.addWidget(self.auto_mode_radio)
        
        auto_description = QLabel("Uses recommended settings for your platform with minimal configuration required.")
        auto_description.setIndent(20)
        auto_description.setWordWrap(True)
        mode_layout.addWidget(auto_description)
        
        self.custom_mode_radio = QRadioButton("Custom Installation")
        self.custom_mode_radio.toggled.connect(self.toggle_installation_mode)
        mode_layout.addWidget(self.custom_mode_radio)
        
        custom_description = QLabel("Allows you to customize installation options for your platform.")
        custom_description.setIndent(20)
        custom_description.setWordWrap(True)
        mode_layout.addWidget(custom_description)
        
        layout.addWidget(mode_group)
        
        # Create tabs for platform-specific options
        self.tab_widget = QTabWidget()
        
        # Add platform-specific tabs
        if self.current_system == "windows":
            self.tab_widget.addTab(self.create_windows_tab(), "Windows")
        elif self.current_system == "darwin":  # macOS
            self.tab_widget.addTab(self.create_mac_tab(), "macOS")
        elif self.current_system == "linux":
            self.tab_widget.addTab(self.create_linux_tab(), "Linux")
        else:
            # Generic tab for unsupported platforms
            unsupported_widget = QWidget()
            unsupported_layout = QVBoxLayout(unsupported_widget)
            unsupported_label = QLabel(
                "Your platform is not directly supported for automatic installation. "
                "Please visit the Docker documentation for manual installation instructions."
            )
            unsupported_label.setWordWrap(True)
            unsupported_layout.addWidget(unsupported_label)
            self.tab_widget.addTab(unsupported_widget, "Unsupported")
        
        layout.addWidget(self.tab_widget)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        button_layout.addStretch()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        install_button = QPushButton("Install Docker")
        install_button.clicked.connect(self.request_installation)
        button_layout.addWidget(install_button)
        
        layout.addLayout(button_layout)
        
        # Initialize UI state
        self.toggle_installation_mode()
    
    def toggle_installation_mode(self):
        """Toggle between automatic and custom installation mode."""
        is_auto = self.auto_mode_radio.isChecked()
        self.tab_widget.setEnabled(not is_auto)
    
    def create_windows_tab(self):
        """Create Windows-specific installation options."""
        windows_widget = QWidget()
        layout = QFormLayout(windows_widget)
        
        # Installation type
        self.windows_install_type = QComboBox()
        self.windows_install_type.addItem("Docker Desktop (Recommended)", "desktop")
        self.windows_install_type.addItem("Docker Engine with WSL2", "engine")
        layout.addRow("Installation Type:", self.windows_install_type)
        
        # WSL2 option
        self.windows_use_wsl2 = QCheckBox("Use WSL2 backend (recommended)")
        self.windows_use_wsl2.setChecked(True)
        layout.addRow("", self.windows_use_wsl2)
        
        # Auto-start option
        self.windows_autostart = QCheckBox("Start Docker at system startup")
        self.windows_autostart.setChecked(True)
        layout.addRow("", self.windows_autostart)
        
        # License agreement
        self.windows_accept_license = QCheckBox("Accept Docker license agreement")
        self.windows_accept_license.setChecked(True)
        layout.addRow("", self.windows_accept_license)
        
        return windows_widget
    
    def create_mac_tab(self):
        """Create macOS-specific installation options."""
        mac_widget = QWidget()
        layout = QFormLayout(mac_widget)
        
        # Installation type
        self.mac_install_type = QComboBox()
        self.mac_install_type.addItem("Docker Desktop (Full features)", "desktop")
        self.mac_install_type.addItem("Colima (Lightweight alternative)", "colima")
        layout.addRow("Installation Type:", self.mac_install_type)
        
        # Auto-start option
        self.mac_autostart = QCheckBox("Start Docker at system startup")
        self.mac_autostart.setChecked(True)
        layout.addRow("", self.mac_autostart)
        
        return mac_widget
    
    def create_linux_tab(self):
        """Create Linux-specific installation options."""
        linux_widget = QWidget()
        layout = QFormLayout(linux_widget)
        
        # Add user to docker group
        self.linux_add_user = QCheckBox("Add current user to docker group")
        self.linux_add_user.setChecked(True)
        layout.addRow("", self.linux_add_user)
        
        # Auto-start option
        self.linux_autostart = QCheckBox("Start Docker service at system startup")
        self.linux_autostart.setChecked(True)
        layout.addRow("", self.linux_autostart)
        
        return linux_widget
    
    def get_installation_config(self):
        """Get the installation configuration based on user selections."""
        config = {
            "platform": self.current_system,
            "auto_mode": self.auto_mode_radio.isChecked()
        }
        
        if not self.auto_mode_radio.isChecked():
            # Only add custom options if in custom mode
            if self.current_system == "windows":
                config.update({
                    "install_type": self.windows_install_type.currentData(),
                    "use_wsl2": self.windows_use_wsl2.isChecked(),
                    "autostart": self.windows_autostart.isChecked(),
                    "accept_license": self.windows_accept_license.isChecked()
                })
            elif self.current_system == "darwin":  # macOS
                config.update({
                    "install_type": self.mac_install_type.currentData(),
                    "autostart": self.mac_autostart.isChecked()
                })
            elif self.current_system == "linux":
                config.update({
                    "add_user": self.linux_add_user.isChecked(),
                    "autostart": self.linux_autostart.isChecked()
                })
        
        return config
    
    def request_installation(self):
        """Emit signal to request Docker installation with current configuration."""
        config = self.get_installation_config()
        
        # Show different confirmation message based on mode
        if self.auto_mode_radio.isChecked():
            message = "Docker will be installed with recommended settings for your platform."
        else:
            message = "Docker will be installed with your custom settings."
        
        # Confirm installation
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setText("Are you sure you want to install Docker?")
        msg_box.setInformativeText(message)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        response = msg_box.exec_()
        if response == QMessageBox.Yes:
            self.install_requested.emit(config)
            self.accept()
