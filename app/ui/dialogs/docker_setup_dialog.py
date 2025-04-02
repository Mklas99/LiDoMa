import webbrowser
import subprocess
import platform
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, 
                          QHBoxLayout, QTextBrowser, QMessageBox,
                          QWidget, QTabWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPixmap

from app.core.utils.docker_status_checker import DockerStatus
from app.infrastructure.docker_client import DockerClient

class DockerSetupDialog(QDialog):
    """Dialog for Docker setup assistance and status checking."""
    
    docker_check_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.docker_client = DockerClient()
        self.setWindowTitle("Docker Setup Assistant")
        self.setMinimumSize(600, 500)
        self.setup_ui()
        
        # Check Docker status when the dialog opens
        self.check_docker_status()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Docker Engine Setup Assistant")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Status section
        self.status_label = QLabel("Checking Docker status...")
        status_font = QFont()
        status_font.setPointSize(12)
        self.status_label.setFont(status_font)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        
        # Installation tab
        self.install_tab = QWidget()
        install_layout = QVBoxLayout(self.install_tab)
        
        self.install_instructions = QTextBrowser()
        self.install_instructions.setOpenExternalLinks(True)
        install_layout.addWidget(self.install_instructions)
        
        install_buttons = QHBoxLayout()
        self.download_button = QPushButton("Download Docker")
        self.download_button.clicked.connect(self.open_download_url)
        install_buttons.addWidget(self.download_button)
        
        self.docs_button = QPushButton("View Documentation")
        self.docs_button.clicked.connect(self.open_docs_url)
        install_buttons.addWidget(self.docs_button)
        
        install_layout.addLayout(install_buttons)
        self.tab_widget.addTab(self.install_tab, "Installation")
        
        # Start Docker tab
        self.start_tab = QWidget()
        start_layout = QVBoxLayout(self.start_tab)
        
        self.start_instructions = QTextBrowser()
        start_layout.addWidget(self.start_instructions)
        
        start_buttons = QHBoxLayout()
        self.start_command_button = QPushButton("Run Start Command")
        self.start_command_button.clicked.connect(self.run_start_command)
        start_buttons.addWidget(self.start_command_button)
        start_layout.addLayout(start_buttons)
        
        self.tab_widget.addTab(self.start_tab, "Start Docker")
        
        # Troubleshooting tab
        self.troubleshoot_tab = QWidget()
        troubleshoot_layout = QVBoxLayout(self.troubleshoot_tab)
        
        troubleshoot_text = QTextBrowser()
        troubleshoot_text.setHtml("""
            <h3>Docker Engine Troubleshooting</h3>
            <p>If you're having trouble with Docker Engine, try these steps:</p>
            <ol>
                <li>Ensure your system meets the minimum requirements for Docker Engine</li>
                <li>For Windows users:
                    <ul>
                        <li>Ensure virtualization is enabled in BIOS/UEFI</li>
                        <li>Ensure WSL2 is properly configured (if using WSL2 method)</li>
                        <li>Check Windows features to ensure container support is enabled</li>
                    </ul>
                </li>
                <li>For Mac users:
                    <ul>
                        <li>Ensure you have sufficient disk space</li>
                        <li>If using Colima, check its logs with: colima status</li>
                    </ul>
                </li>
                <li>For Linux users:
                    <ul>
                        <li>Ensure your user is in the docker group: <code>sudo usermod -aG docker $USER</code></li>
                        <li>Log out and log back in for group changes to take effect</li>
                        <li>Check Docker daemon logs with: <code>sudo journalctl -u docker</code></li>
                    </ul>
                </li>
            </ol>
            <p>For more detailed troubleshooting, visit the <a href="https://docs.docker.com/engine/install/troubleshoot/">Docker Engine troubleshooting guide</a>.</p>
        """)
        troubleshoot_layout.addWidget(troubleshoot_text)
        
        self.tab_widget.addTab(self.troubleshoot_tab, "Troubleshooting")
        
        # Post-Installation tab
        self.postinstall_tab = QWidget()
        postinstall_layout = QVBoxLayout(self.postinstall_tab)
        
        postinstall_text = QTextBrowser()
        postinstall_text.setHtml("""
            <h3>Docker Engine Post-Installation Setup</h3>
            <p>After installing Docker Engine, complete these recommended steps:</p>
            <ol>
                <li><strong>Create the docker group</strong>:
                    <pre>sudo groupadd docker</pre>
                </li>
                <li><strong>Add your user to the docker group</strong>:
                    <pre>sudo usermod -aG docker $USER</pre>
                </li>
                <li><strong>Apply the group change</strong>:
                    <p>Log out and log back in, or run:</p>
                    <pre>newgrp docker</pre>
                </li>
                <li><strong>Configure Docker to start on boot</strong>:
                    <p>Linux:</p>
                    <pre>sudo systemctl enable docker</pre>
                    <p>macOS (with Colima):</p>
                    <pre>mkdir -p ~/Library/LaunchAgents
colima autostart</pre>
                </li>
                <li><strong>Test your installation</strong>:
                    <pre>docker run hello-world</pre>
                </li>
            </ol>
        """)
        postinstall_layout.addWidget(postinstall_text)
        
        self.tab_widget.addTab(self.postinstall_tab, "Post-Installation")
        
        layout.addWidget(self.tab_widget)
        
        # Action buttons at the bottom
        button_layout = QHBoxLayout()
        
        self.check_again_button = QPushButton("Check Docker Status Again")
        self.check_again_button.clicked.connect(self.check_docker_status)
        button_layout.addWidget(self.check_again_button)
        
        button_layout.addStretch()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Store URLs
        self.download_url = ""
        self.docs_url = ""
        self.start_cmd = None
        
    def check_docker_status(self):
        """Check Docker status and update UI accordingly."""
        status, message = self.docker_client.get_docker_status()
        self.update_status_ui(status, message)
        
        # Emit signal so the main app knows to refresh its Docker status
        self.docker_check_requested.emit()
    
    def update_status_ui(self, status: DockerStatus, message: str):
        """Update the UI based on Docker status."""
        if status == DockerStatus.RUNNING:
            self.status_label.setText("✅ Docker is installed and running")
            self.status_label.setStyleSheet("color: green;")
            self.tab_widget.setTabEnabled(0, False)  # Disable installation tab
            self.tab_widget.setTabEnabled(1, False)  # Disable start tab
            self.tab_widget.setCurrentIndex(2)  # Show troubleshooting
        elif status == DockerStatus.INSTALLED_NOT_RUNNING:
            self.status_label.setText("⚠️ Docker is installed but not running")
            self.status_label.setStyleSheet("color: orange;")
            self.tab_widget.setTabEnabled(0, False)  # Disable installation tab
            self.tab_widget.setTabEnabled(1, True)   # Enable start tab
            self.tab_widget.setCurrentIndex(1)  # Show start tab
            
            # Update start instructions
            start_info = self.docker_client.get_start_instructions()
            self.start_instructions.setHtml(f"<h3>{start_info['title']}</h3><p>{start_info['instructions']}</p>")
            self.start_cmd = start_info.get('command')
            self.start_command_button.setEnabled(self.start_cmd is not None)
            
        elif status == DockerStatus.NOT_INSTALLED:
            self.status_label.setText("❌ Docker Engine is not installed")
            self.status_label.setStyleSheet("color: red;")
            self.tab_widget.setTabEnabled(0, True)   # Enable installation tab
            self.tab_widget.setTabEnabled(1, False)  # Disable start tab
            self.tab_widget.setCurrentIndex(0)  # Show installation tab
            
            # Update installation instructions
            install_info = self.docker_client.get_installation_instructions()
            self.install_instructions.setHtml(
                f"<h3>{install_info['title']}</h3>"
                f"<p>{install_info['instructions']}</p>"
                f"<p>Visit documentation: <a href='{install_info['docs_url']}'>{install_info['docs_url']}</a></p>"
            )
            self.download_url = install_info['download_url']
            self.docs_url = install_info['docs_url']
            
        else:  # UNKNOWN
            self.status_label.setText(f"❓ Docker status unknown: {message}")
            self.status_label.setStyleSheet("color: gray;")
            # Show all tabs
            self.tab_widget.setTabEnabled(0, True)
            self.tab_widget.setTabEnabled(1, True)
    
    def open_download_url(self):
        """Open the Docker download URL in web browser."""
        if self.download_url:
            webbrowser.open(self.download_url)
    
    def open_docs_url(self):
        """Open the Docker documentation URL in web browser."""
        if self.docs_url:
            webbrowser.open(self.docs_url)
    
    def run_start_command(self):
        """Run the start Docker command if available."""
        if not self.start_cmd:
            return
        
        try:
            if platform.system().lower() == "windows":
                # On Windows, open a command prompt to run the command
                subprocess.Popen(f"cmd.exe /c start cmd.exe /k {self.start_cmd}")
            else:
                # On Unix systems, we'd need a terminal emulator
                # This is system-dependent, but try common ones
                for terminal in ["gnome-terminal", "xterm", "konsole"]:
                    try:
                        subprocess.Popen([terminal, "-e", f"bash -c '{self.start_cmd}; read -p \"Press Enter to close...\"'"])
                        break
                    except FileNotFoundError:
                        continue
                else:
                    # If no terminal found, show the command for user to manually run
                    QMessageBox.information(
                        self, 
                        "Run Command Manually", 
                        f"Please open a terminal and run the following command:\n\n{self.start_cmd}"
                    )
                    
            # After starting Docker, check status again in a few seconds
            QTimer.singleShot(5000, self.check_docker_status)
            
        except Exception as e:
            QMessageBox.warning(
                self, 
                "Error Running Command", 
                f"Failed to run the command: {str(e)}\n\nPlease run it manually:\n{self.start_cmd}"
            )
