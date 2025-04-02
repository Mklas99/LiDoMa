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
        self.progress_updated.emit(5, "Preparing Windows environment...")
        
        # Get installation options
        install_type = self.config.get("install_type", "engine")
        use_wsl2 = self.config.get("use_wsl2", True)
        auto_start = self.config.get("autostart", True)
        accept_license = self.config.get("accept_license", True)
        auto_mode = self.config.get("auto_mode", False)
        
        # If auto mode, set sensible defaults
        if auto_mode:
            install_type = "engine"
            use_wsl2 = True
            auto_start = True
            
        self.log_message.emit(f"Installing Docker Engine for Windows (Type: {install_type})")
        
        try:
            # Create temporary directory for installation files
            temp_dir = tempfile.mkdtemp(prefix="docker_install_")
            self.log_message.emit(f"Created temporary directory at {temp_dir}")
            
            # Step 1: Check for WSL2 if needed
            if use_wsl2:
                self.progress_updated.emit(10, "Checking WSL2 prerequisites...")
                self.log_message.emit("Checking WSL2 status...")
                
                # Check if WSL is installed
                wsl_check = subprocess.run(
                    ["wsl", "--status"], 
                    capture_output=True, 
                    text=True, 
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if "WSL 2" not in wsl_check.stdout and "WSL 2" not in wsl_check.stderr:
                    self.log_message.emit("WSL2 not detected. Installing prerequisites...")
                    
                    # Enable WSL feature
                    self.log_message.emit("Enabling Windows Subsystem for Linux...")
                    subprocess.run(
                        ["dism.exe", "/online", "/enable-feature", "/featurename:Microsoft-Windows-Subsystem-Linux", "/all", "/norestart"],
                        capture_output=True,
                        check=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    # Enable Virtual Machine Platform
                    self.log_message.emit("Enabling Virtual Machine Platform...")
                    subprocess.run(
                        ["dism.exe", "/online", "/enable-feature", "/featurename:VirtualMachinePlatform", "/all", "/norestart"],
                        capture_output=True,
                        check=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    # Download WSL2 kernel update
                    self.progress_updated.emit(15, "Downloading WSL2 kernel update...")
                    wsl_update_url = "https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi"
                    wsl_update_file = os.path.join(temp_dir, "wsl_update_x64.msi")
                    
                    self.download_file(wsl_update_url, wsl_update_file)
                    
                    # Install WSL2 kernel update
                    self.progress_updated.emit(20, "Installing WSL2 kernel update...")
                    self.log_message.emit("Installing WSL2 kernel update...")
                    subprocess.run(
                        ["msiexec.exe", "/i", wsl_update_file, "/quiet", "/norestart"],
                        check=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    # Set WSL2 as default
                    self.log_message.emit("Setting WSL2 as default...")
                    subprocess.run(
                        ["wsl", "--set-default-version", "2"],
                        check=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    self.log_message.emit("WSL2 is already installed")
            
            # Step 2: Install Docker based on install_type
            self.progress_updated.emit(30, "Downloading Docker installation files...")
            
            if install_type in ["engine", "wsl2"]:
                # Download Docker Engine for Windows
                docker_url = "https://download.docker.com/win/static/stable/x86_64/docker-24.0.6.zip"
                docker_zip = os.path.join(temp_dir, "docker.zip")
                
                self.download_file(docker_url, docker_zip)
                
                # Extract Docker
                self.progress_updated.emit(50, "Extracting Docker Engine...")
                self.log_message.emit("Extracting Docker Engine...")
                
                import zipfile
                with zipfile.ZipFile(docker_zip, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Create installation directory
                docker_install_dir = os.path.join(os.environ["ProgramFiles"], "Docker")
                os.makedirs(docker_install_dir, exist_ok=True)
                
                # Copy Docker files
                self.progress_updated.emit(60, "Installing Docker Engine...")
                self.log_message.emit(f"Copying Docker files to {docker_install_dir}...")
                
                docker_bin_dir = os.path.join(temp_dir, "docker")
                for file in os.listdir(docker_bin_dir):
                    src = os.path.join(docker_bin_dir, file)
                    dst = os.path.join(docker_install_dir, file)
                    shutil.copy2(src, dst)
                
                # Add Docker to PATH
                self.progress_updated.emit(70, "Setting up environment...")
                self.log_message.emit("Adding Docker to PATH...")
                
                # Create PowerShell script to update PATH
                path_script = os.path.join(temp_dir, "update_path.ps1")
                with open(path_script, 'w') as f:
                    f.write(f'$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";{docker_install_dir}"\n')
                    f.write(f'[Environment]::SetEnvironmentVariable("Path", $env:Path, "Machine")\n')
                
                # Run PowerShell script as admin
                subprocess.run(
                    ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", path_script],
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                # Install Docker service
                self.progress_updated.emit(80, "Installing Docker service...")
                self.log_message.emit("Registering Docker service...")
                
                dockerd_path = os.path.join(docker_install_dir, "dockerd.exe")
                subprocess.run(
                    [dockerd_path, "--register-service"],
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                # Start Docker service if auto_start is enabled
                if auto_start:
                    self.log_message.emit("Starting Docker service...")
                    subprocess.run(
                        ["sc", "start", "docker"],
                        check=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    if use_wsl2:
                        # Configure Docker to use WSL2
                        config_dir = os.path.join(os.environ['USERPROFILE'], '.docker')
                        os.makedirs(config_dir, exist_ok=True)
                        
                        config_file = os.path.join(config_dir, 'daemon.json')
                        with open(config_file, 'w') as f:
                            f.write('{\n')
                            f.write('  "hosts": ["tcp://0.0.0.0:2375", "npipe://"],\n')
                            f.write('  "experimental": true\n')
                            f.write('}\n')
                        
                        self.log_message.emit("Configured Docker to use WSL2")
                
            elif install_type == "cli":
                # Install Docker CLI only
                docker_url = "https://github.com/docker/cli/releases/download/v24.0.6/docker-24.0.6-windows-x86_64.zip"
                docker_zip = os.path.join(temp_dir, "docker-cli.zip")
                
                self.download_file(docker_url, docker_zip)
                
                # Extract Docker CLI
                self.progress_updated.emit(50, "Extracting Docker CLI...")
                self.log_message.emit("Extracting Docker CLI...")
                
                import zipfile
                with zipfile.ZipFile(docker_zip, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Create installation directory
                docker_install_dir = os.path.join(os.environ["ProgramFiles"], "Docker")
                os.makedirs(docker_install_dir, exist_ok=True)
                
                # Copy Docker CLI files
                self.progress_updated.emit(70, "Installing Docker CLI...")
                self.log_message.emit(f"Copying Docker CLI files to {docker_install_dir}...")
                
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith('.exe'):
                            src = os.path.join(root, file)
                            dst = os.path.join(docker_install_dir, file)
                            shutil.copy2(src, dst)
                
                # Add Docker to PATH
                self.progress_updated.emit(80, "Setting up environment...")
                self.log_message.emit("Adding Docker CLI to PATH...")
                
                # Create PowerShell script to update PATH
                path_script = os.path.join(temp_dir, "update_path.ps1")
                with open(path_script, 'w') as f:
                    f.write(f'$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";{docker_install_dir}"\n')
                    f.write(f'[Environment]::SetEnvironmentVariable("Path", $env:Path, "Machine")\n')
                
                # Run PowerShell script as admin
                subprocess.run(
                    ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", path_script],
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            
            # Clean up temporary files
            self.progress_updated.emit(95, "Cleaning up...")
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Final check - verify Docker installation
            self.progress_updated.emit(98, "Verifying installation...")
            
            try:
                subprocess.run(
                    ["docker", "--version"],
                    capture_output=True,
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.log_message.emit("Docker successfully installed!")
                return True, "Docker Engine was successfully installed on Windows"
            except subprocess.CalledProcessError:
                self.log_message.emit("Docker installation completed, but verification failed. You may need to restart your computer.")
                return True, "Docker Engine was installed. Please restart your computer to complete setup."
                
        except Exception as e:
            self.log_message.emit(f"ERROR: {str(e)}")
            return False, f"Failed to install Docker: {str(e)}"
    
    def install_on_mac(self):
        """Install Docker on macOS."""
        self.progress_updated.emit(5, "Preparing macOS environment...")
        
        # Get installation options
        install_type = self.config.get("install_type", "colima") if not self.config.get("auto_mode", False) else "colima"
        auto_start = self.config.get("autostart", True)
        
        self.log_message.emit(f"Installing Docker Engine for macOS (Type: {install_type})")
        
        try:
            # Check for Homebrew
            self.progress_updated.emit(10, "Checking for Homebrew...")
            self.log_message.emit("Checking if Homebrew is installed...")
            
            try:
                brew_path = subprocess.run(["which", "brew"], capture_output=True, text=True, check=True)
                self.log_message.emit("Homebrew is installed")
            except subprocess.CalledProcessError:
                # Install Homebrew
                self.progress_updated.emit(15, "Installing Homebrew...")
                self.log_message.emit("Installing Homebrew...")
                
                homebrew_script = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
                process = subprocess.Popen(
                    homebrew_script,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                while process.poll() is None:
                    if self.cancelled:
                        process.terminate()
                        return False, "Installation cancelled"
                    time.sleep(0.5)
                
                if process.returncode != 0:
                    error_output = process.stderr.read()
                    self.log_message.emit(f"ERROR: Failed to install Homebrew: {error_output}")
                    return False, "Failed to install Homebrew"
                
                self.log_message.emit("Homebrew installed successfully")
            
            # Install Docker based on install_type
            if install_type == "colima":
                # Install Docker CLI and Colima
                self.progress_updated.emit(30, "Installing Docker CLI...")
                self.log_message.emit("Installing Docker CLI...")
                
                # Install Docker CLI
                subprocess.run(["brew", "install", "docker"], check=True)
                self.log_message.emit("Docker CLI installed")
                
                self.progress_updated.emit(50, "Installing Colima...")
                self.log_message.emit("Installing Colima...")
                
                # Install Colima
                subprocess.run(["brew", "install", "colima"], check=True)
                self.log_message.emit("Colima installed")
                
                # Start Colima if auto_start is enabled
                if auto_start:
                    self.progress_updated.emit(70, "Starting Colima...")
                    self.log_message.emit("Starting Colima...")
                    
                    # Start Colima
                    subprocess.run(["colima", "start"], check=True)
                    self.log_message.emit("Colima started")
                    
                    # Configure Colima to start on login
                    self.progress_updated.emit(80, "Configuring auto-start...")
                    
                    # Create LaunchAgent directory if it doesn't exist
                    launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
                    os.makedirs(launch_agents_dir, exist_ok=True)
                    
                    # Configure auto-start
                    subprocess.run(["colima", "autostart"], check=True)
                    self.log_message.emit("Colima configured to start automatically")
                
            elif install_type == "cli":
                # Install Docker CLI only
                self.progress_updated.emit(50, "Installing Docker CLI...")
                self.log_message.emit("Installing Docker CLI...")
                
                # Install Docker CLI
                subprocess.run(["brew", "install", "docker"], check=True)
                self.log_message.emit("Docker CLI installed")
                
            elif install_type == "desktop":
                # Install Docker with Docker Desktop GUI
                self.progress_updated.emit(30, "Downloading Docker Desktop...")
                self.log_message.emit("Downloading Docker Desktop...")
                
                # Download Docker Desktop DMG
                docker_dmg_url = "https://desktop.docker.com/mac/main/amd64/Docker.dmg"
                docker_dmg = os.path.expanduser("~/Downloads/Docker.dmg")
                
                self.download_file(docker_dmg_url, docker_dmg)
                
                # Mount DMG
                self.progress_updated.emit(60, "Mounting Docker Desktop image...")
                self.log_message.emit("Mounting Docker Desktop image...")
                
                subprocess.run(["hdiutil", "attach", docker_dmg], check=True)
                
                # Copy Docker to Applications
                self.progress_updated.emit(70, "Installing Docker Desktop...")
                self.log_message.emit("Copying Docker Desktop to Applications folder...")
                
                subprocess.run(["cp", "-R", "/Volumes/Docker/Docker.app", "/Applications/"], check=True)
                
                # Unmount DMG
                self.progress_updated.emit(80, "Finalizing installation...")
                self.log_message.emit("Unmounting Docker Desktop image...")
                
                subprocess.run(["hdiutil", "detach", "/Volumes/Docker"], check=True)
                
                # Start Docker if auto_start is enabled
                if auto_start:
                    self.progress_updated.emit(90, "Starting Docker Desktop...")
                    self.log_message.emit("Starting Docker Desktop...")
                    
                    subprocess.run(["open", "/Applications/Docker.app"], check=True)
            
            # Verify installation
            self.progress_updated.emit(95, "Verifying installation...")
            self.log_message.emit("Verifying Docker installation...")
            
            try:
                subprocess.run(["docker", "--version"], check=True)
                self.log_message.emit("Docker successfully installed!")
                return True, f"Docker Engine was successfully installed on macOS using {install_type}"
            except subprocess.CalledProcessError:
                self.log_message.emit("Docker installation completed, but verification failed.")
                return True, "Docker Engine was installed but needs additional configuration"
                
        except Exception as e:
            self.log_message.emit(f"ERROR: {str(e)}")
            return False, f"Failed to install Docker: {str(e)}"
    
    def install_on_linux(self):
        """Install Docker on Linux."""
        self.progress_updated.emit(5, "Preparing Linux environment...")
        
        # Get installation options
        add_user = self.config.get("add_user", True) if not self.config.get("auto_mode", False) else True
        auto_start = self.config.get("autostart", True) if not self.config.get("auto_mode", False) else True
        
        try:
            # Detect Linux distribution
            self.log_message.emit("Detecting Linux distribution...")
            
            distro = self.get_linux_distro()
            if not distro:
                self.log_message.emit("ERROR: Could not determine Linux distribution")
                return False, "Could not determine Linux distribution"
            
            self.log_message.emit(f"Detected Linux distribution: {distro}")
            
            # Create install script based on distribution
            self.progress_updated.emit(10, "Creating installation script...")
            
            with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".sh") as script_file:
                script_path = script_file.name
                
                script_file.write("#!/bin/bash\n")
                script_file.write("set -e\n\n")
                script_file.write("echo 'Starting Docker installation...'\n\n")
                
                if distro in ["ubuntu", "debian"]:
                    # Ubuntu/Debian installation
                    script_file.write("""
# Remove old versions if any
apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Update apt repos
apt-get update

# Install dependencies
apt-get install -y \\
    apt-transport-https \\
    ca-certificates \\
    curl \\
    gnupg \\
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \\
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# Configure Docker to start on boot
systemctl enable docker
""")
                    # Add user to docker group if needed
                    if add_user:
                        script_file.write("""
# Add current user to docker group
usermod -aG docker $SUDO_USER
""")
                    
                    # Start Docker if needed
                    if auto_start:
                        script_file.write("""
# Start Docker service
systemctl start docker
""")
                    
                elif distro in ["fedora", "centos", "rhel"]:
                    # Fedora/CentOS/RHEL installation
                    script_file.write("""
# Remove old versions if any
dnf remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine podman 2>/dev/null || true

# Install required packages
dnf -y install dnf-plugins-core

# Add Docker repo
dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

# Install Docker
dnf install -y docker-ce docker-ce-cli containerd.io

# Configure Docker to start on boot
systemctl enable docker
""")
                    # Add user to docker group if needed
                    if add_user:
                        script_file.write("""
# Add current user to docker group
usermod -aG docker $SUDO_USER
""")
                    
                    # Start Docker if needed
                    if auto_start:
                        script_file.write("""
# Start Docker service
systemctl start docker
""")
                    
                else:
                    # Generic Linux installation
                    script_file.write("""
# Using convenience script for other distributions
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Configure Docker to start on boot
systemctl enable docker 2>/dev/null || true
""")
                    # Add user to docker group if needed
                    if add_user:
                        script_file.write("""
# Add current user to docker group
usermod -aG docker $SUDO_USER 2>/dev/null || usermod -aG docker $USER
""")
                    
                    # Start Docker if needed
                    if auto_start:
                        script_file.write("""
# Start Docker service
systemctl start docker 2>/dev/null || service docker start
""")
                    
                script_file.write("\necho 'Docker installation completed successfully'\n")
            
            # Make script executable
            os.chmod(script_path, 0o755)
            
            # Run script with sudo
            self.progress_updated.emit(20, "Installing Docker...")
            self.log_message.emit("Running installation script (requires sudo)...")
            
            with subprocess.Popen(
                ["sudo", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            ) as process:
                
                for line in process.stdout:
                    self.log_message.emit(line.strip())
                    if self.cancelled:
                        process.terminate()
                        return False, "Installation cancelled"
                
                # Wait for process to complete and get return code
                process.wait()
                if process.returncode != 0:
                    error_output = process.stderr.read()
                    self.log_message.emit(f"ERROR: Installation failed: {error_output}")
                    return False, f"Installation failed with code {process.returncode}"
            
            # Clean up script
            os.unlink(script_path)
            
            # Verify installation
            self.progress_updated.emit(90, "Verifying installation...")
            self.log_message.emit("Verifying Docker installation...")
            
            try:
                # We need to run docker as the user, not as root
                if add_user:
                    self.log_message.emit("Docker was installed successfully, but you may need to log out and log back in to use it without sudo")
                    return True, "Docker was installed successfully. Log out and log back in to use Docker without sudo."
                else:
                    # Try to verify with sudo
                    result = subprocess.run(
                        ["sudo", "docker", "--version"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    self.log_message.emit(f"Docker verified: {result.stdout.strip()}")
                    return True, "Docker was installed successfully"
            except Exception as e:
                self.log_message.emit(f"WARNING: Docker installation completed, but verification failed: {str(e)}")
                return True, "Docker was installed but verification failed. You might need to restart your system."
                
        except Exception as e:
            self.log_message.emit(f"ERROR: {str(e)}")
            return False, f"Failed to install Docker: {str(e)}"
    
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
