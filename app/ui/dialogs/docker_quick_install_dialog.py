import platform
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                             QHBoxLayout, QComboBox, QFormLayout, QCheckBox,
                             QTabWidget, QWidget, QRadioButton, QButtonGroup,
                             QSpacerItem, QSizePolicy, QMessageBox, QGroupBox,
                             QTextBrowser)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from app.core.utils.admin_utils import is_admin, request_admin_privileges

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
        
        # Add installation steps collapsible section after the tabs
        self.steps_group = QGroupBox("Installation Steps (click to expand)")
        self.steps_group.setCheckable(True)
        self.steps_group.setChecked(False)  # Start collapsed
        self.steps_group.toggled.connect(self.toggle_steps_visibility)
        
        steps_layout = QVBoxLayout(self.steps_group)
        self.steps_browser = QTextBrowser()
        self.steps_browser.setMaximumHeight(0)  # Start with 0 height when collapsed
        self.steps_browser.setMinimumHeight(0)
        steps_layout.addWidget(self.steps_browser)
        
        layout.addWidget(self.steps_group)
        
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
        
        # Update the installation steps text when tabs or options change
        self.tab_widget.currentChanged.connect(self.update_installation_steps)
        self.auto_mode_radio.toggled.connect(self.update_installation_steps)
        
        # Initialize steps text
        self.update_installation_steps()
        
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
        
        # Installation type - changed options to be clearer about Docker Engine
        self.windows_install_type = QComboBox()
        self.windows_install_type.addItem("Docker Engine (Standard)", "engine")
        self.windows_install_type.addItem("Docker Engine with WSL2 backend", "wsl2")
        self.windows_install_type.addItem("Docker Engine + Docker CLI", "cli")
        self.windows_install_type.currentIndexChanged.connect(self.update_installation_steps)
        layout.addRow("Installation Type:", self.windows_install_type)
        
        # WSL2 option - only relevant for some installation types
        self.windows_use_wsl2 = QCheckBox("Use WSL2 backend (recommended for better performance)")
        self.windows_use_wsl2.setChecked(True)
        self.windows_use_wsl2.stateChanged.connect(self.update_installation_steps)
        layout.addRow("", self.windows_use_wsl2)
        
        # Auto-start option
        self.windows_autostart = QCheckBox("Start Docker at system startup")
        self.windows_autostart.setChecked(True)
        self.windows_autostart.stateChanged.connect(self.update_installation_steps)
        layout.addRow("", self.windows_autostart)
        
        # License agreement
        self.windows_accept_license = QCheckBox("Accept Docker license agreement")
        self.windows_accept_license.setChecked(True)
        self.windows_accept_license.stateChanged.connect(self.update_installation_steps)
        layout.addRow("", self.windows_accept_license)
        
        return windows_widget
    
    def create_mac_tab(self):
        """Create macOS-specific installation options."""
        mac_widget = QWidget()
        layout = QFormLayout(mac_widget)
        
        # Installation type - changed options to focus on Docker Engine
        self.mac_install_type = QComboBox()
        self.mac_install_type.addItem("Docker Engine with Colima (Recommended)", "colima")
        self.mac_install_type.addItem("Docker Engine CLI only", "cli")
        self.mac_install_type.addItem("Docker Engine + Docker Desktop GUI", "desktop")
        self.mac_install_type.currentIndexChanged.connect(self.update_installation_steps)
        layout.addRow("Installation Type:", self.mac_install_type)
        
        # Auto-start option
        self.mac_autostart = QCheckBox("Start Docker at system startup")
        self.mac_autostart.setChecked(True)
        self.mac_autostart.stateChanged.connect(self.update_installation_steps)
        layout.addRow("", self.mac_autostart)
        
        return mac_widget
    
    def create_linux_tab(self):
        """Create Linux-specific installation options."""
        linux_widget = QWidget()
        layout = QFormLayout(linux_widget)
        
        # Add user to docker group
        self.linux_add_user = QCheckBox("Add current user to docker group")
        self.linux_add_user.setChecked(True)
        self.linux_add_user.stateChanged.connect(self.update_installation_steps)
        layout.addRow("", self.linux_add_user)
        
        # Auto-start option
        self.linux_autostart = QCheckBox("Start Docker service at system startup")
        self.linux_autostart.setChecked(True)
        self.linux_autostart.stateChanged.connect(self.update_installation_steps)
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
        
        # Check for admin privileges before proceeding with installation
        if not is_admin():
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText("Administrator privileges required")
            msg_box.setInformativeText("Docker installation requires administrator privileges. " 
                                      "The application will now restart with elevated permissions.")
            msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            response = msg_box.exec_()
            
            if response == QMessageBox.Ok:
                # Request admin privileges and restart
                if not request_admin_privileges():
                    return  # Program will restart with admin rights
            else:
                return  # User cancelled
        
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
    
    def toggle_steps_visibility(self, checked):
        """Toggle the visibility of the installation steps."""
        if checked:
            # Expand
            self.steps_browser.setMaximumHeight(200)
            self.steps_group.setTitle("Installation Steps (click to collapse)")
        else:
            # Collapse
            self.steps_browser.setMaximumHeight(0)
            self.steps_group.setTitle("Installation Steps (click to expand)")

    def update_installation_steps(self):
        """Update the displayed installation steps based on current settings."""
        if self.auto_mode_radio.isChecked():
            # Auto mode steps
            steps_html = self._get_auto_mode_steps()
        else:
            # Custom mode steps
            current_index = self.tab_widget.currentIndex()
            tab_text = self.tab_widget.tabText(current_index)
            
            if "Windows" in tab_text:
                steps_html = self._get_windows_steps()
            elif "macOS" in tab_text:
                steps_html = self._get_mac_steps()
            elif "Linux" in tab_text:
                steps_html = self._get_linux_steps()
            else:
                steps_html = "<p>No installation steps available for this platform.</p>"
        
        self.steps_browser.setHtml(steps_html)

    def _get_auto_mode_steps(self):
        """Get installation steps for automatic mode."""
        if self.current_system == "windows":
            return """
            <h3>Automatic Windows Installation Steps:</h3>
            <ol>
                <li>Check system prerequisites (WSL2, Windows version)</li>
                <li>Download Docker installer</li>
                <li>Install Docker Engine with recommended settings</li>
                <li>Configure Docker to start automatically</li>
                <li>Add current user to docker group (if applicable)</li>
                <li>Verify installation</li>
            </ol>
            """
        elif self.current_system == "darwin":  # macOS
            return """
            <h3>Automatic macOS Installation Steps:</h3>
            <ol>
                <li>Check system prerequisites</li>
                <li>Install Homebrew (if not installed)</li>
                <li>Install Docker CLI via Homebrew</li>
                <li>Install and configure Colima as Docker backend</li>
                <li>Set up automatic startup</li>
                <li>Verify installation</li>
            </ol>
            """
        elif self.current_system == "linux":
            return """
            <h3>Automatic Linux Installation Steps:</h3>
            <ol>
                <li>Detect Linux distribution</li>
                <li>Add Docker repository</li>
                <li>Install Docker Engine packages</li>
                <li>Add current user to docker group</li>
                <li>Configure Docker to start on boot</li>
                <li>Start Docker service</li>
                <li>Verify installation</li>
            </ol>
            """
        else:
            return "<p>No installation steps available for this platform.</p>"

    def _get_windows_steps(self):
        """Get installation steps for Windows custom mode."""
        install_type = self.windows_install_type.currentText()
        install_data = self.windows_install_type.currentData()
        use_wsl2 = self.windows_use_wsl2.isChecked()
        auto_start = self.windows_autostart.isChecked()
        accept_license = self.windows_accept_license.isChecked()
        
        # Start with header and common steps
        steps = "<h3>Windows Installation Steps:</h3>"
        
        # Add warning if license not accepted
        if not accept_license:
            steps += """<div style="color: red; border: 1px solid red; padding: 8px; margin-bottom: 10px;">
            <strong>Warning:</strong> Docker license must be accepted to proceed with installation.
            </div>"""
        
        steps += "<ol>"
        steps += "<li>Check system prerequisites (Windows version, hardware requirements)</li>"
        
        # WSL2-specific steps
        if use_wsl2:
            steps += """<li>Enable Windows Subsystem for Linux:
                <ul>
                    <li>Enable WSL2 Windows feature</li>
                    <li>Install WSL2 kernel update if needed</li>
                    <li>Set WSL2 as default WSL version</li>
                </ul>
            </li>"""
        
        # Installation type specific steps
        if install_data == "engine":
            steps += """<li>Install Docker Engine:
                <ul>
                    <li>Download Docker Engine installer</li>
                    <li>Install Docker Engine binaries</li>
                    <li>Configure Docker Engine settings</li>
                </ul>
            </li>"""
        elif install_data == "wsl2":
            steps += """<li>Install Docker Engine with WSL2 backend:
                <ul>
                    <li>Download Docker Engine installer</li>
                    <li>Configure WSL2 integration</li>
                    <li>Install Docker Engine binaries</li>
                    <li>Set up WSL2 backend configuration</li>
                </ul>
            </li>"""
        elif install_data == "cli":
            steps += """<li>Install Docker Engine and CLI:
                <ul>
                    <li>Download Docker Engine and CLI installer</li>
                    <li>Install Docker binaries</li>
                    <li>Add Docker CLI to PATH</li>
                </ul>
            </li>"""
        
        # Auto-start configuration
        if auto_start:
            steps += """<li>Configure Docker to start automatically:
                <ul>
                    <li>Create Windows service for Docker</li>
                    <li>Set service to start automatically on boot</li>
                    <li>Start Docker service now</li>
                </ul>
            </li>"""
        else:
            steps += "<li>Configure Docker for manual start only</li>"
        
        # Final steps
        steps += """<li>Verify installation:
            <ul>
                <li>Check Docker service status</li>
                <li>Run test container to validate installation</li>
            </ul>
        </li>"""
        
        steps += "</ol>"
        return steps

    def _get_mac_steps(self):
        """Get installation steps for macOS custom mode."""
        install_type = self.mac_install_type.currentText()
        install_data = self.mac_install_type.currentData()
        auto_start = self.mac_autostart.isChecked()
        
        # Start with header and common steps
        steps = "<h3>macOS Installation Steps:</h3><ol>"
        steps += "<li>Check system prerequisites (macOS version, architecture)</li>"
        steps += "<li>Install Homebrew package manager (if not already installed)</li>"
        
        # Installation type specific steps
        if install_data == "colima":
            steps += """<li>Set up Docker with Colima:
                <ul>
                    <li>Install Docker CLI via Homebrew</li>
                    <li>Install Colima virtual machine runtime</li>
                    <li>Configure Colima for Docker compatibility</li>
                    <li>Initialize Colima environment</li>
                </ul>
            </li>"""
        elif install_data == "cli":
            steps += """<li>Install Docker CLI only:
                <ul>
                    <li>Install Docker CLI via Homebrew</li>
                    <li>Set up Docker context</li>
                    <li>Configure Docker environment variables</li>
                </ul>
            </li>"""
        elif install_data == "desktop":
            steps += """<li>Install Docker Desktop:
                <ul>
                    <li>Download Docker Desktop for Mac (.dmg)</li>
                    <li>Install Docker Desktop application</li>
                    <li>Set up Docker Desktop preferences</li>
                </ul>
            </li>"""
        
        # Auto-start configuration
        if auto_start:
            if install_data == "colima":
                steps += """<li>Configure automatic startup:
                    <ul>
                        <li>Create LaunchAgent for Colima</li>
                        <li>Register with macOS startup items</li>
                        <li>Start Colima service now</li>
                    </ul>
                </li>"""
            elif install_data == "desktop":
                steps += """<li>Configure automatic startup:
                    <ul>
                        <li>Add Docker Desktop to Login Items</li>
                        <li>Configure Docker Desktop to start on login</li>
                        <li>Start Docker Desktop now</li>
                    </ul>
                </li>"""
        else:
            steps += "<li>Skip automatic startup configuration</li>"
        
        # Final steps
        steps += """<li>Verify installation:
            <ul>
                <li>Check Docker daemon status</li>
                <li>Run test container to validate installation</li>
            </ul>
        </li>"""
        
        steps += "</ol>"
        return steps

    def _get_linux_steps(self):
        """Get installation steps for Linux custom mode."""
        add_user = self.linux_add_user.isChecked()
        auto_start = self.linux_autostart.isChecked()
        
        # Start with header and common steps
        steps = "<h3>Linux Installation Steps:</h3><ol>"
        steps += "<li>Detect Linux distribution and version</li>"
        steps += """<li>Set up Docker repository:
            <ul>
                <li>Install required dependencies</li>
                <li>Add Docker's official GPG key</li>
                <li>Add Docker repository to APT sources</li>
                <li>Update package database</li>
            </ul>
        </li>"""
        
        steps += """<li>Install Docker Engine:
            <ul>
                <li>Install Docker Engine, containerd, and Docker CLI</li>
                <li>Install Docker Compose plugin</li>
            </ul>
        </li>"""
        
        # User configuration
        if add_user:
            steps += """<li>Configure user permissions:
                <ul>
                    <li>Create docker group if it doesn't exist</li>
                    <li>Add current user to docker group</li>
                    <li>Apply group changes</li>
                </ul>
            </li>"""
        else:
            steps += "<li>Skip user group configuration (Docker will require sudo)</li>"
        
        # Auto-start configuration
        if auto_start:
            steps += """<li>Configure Docker to start on boot:
                <ul>
                    <li>Enable Docker service with systemd</li>
                    <li>Start Docker service now</li>
                </ul>
            </li>"""
        else:
            steps += "<li>Skip automatic startup configuration</li>"
        
        # Final steps
        steps += """<li>Verify installation:
            <ul>
                <li>Check Docker daemon status</li>
                <li>Run test container to validate installation</li>
                <li>Verify user permissions</li>
            </ul>
        </li>"""
        
        steps += "</ol>"
        return steps
