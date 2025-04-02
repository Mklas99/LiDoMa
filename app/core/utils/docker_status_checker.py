import subprocess
import platform
import logging
from enum import Enum
from typing import Tuple, Dict

class DockerStatus(Enum):
    """Enum representing different Docker status states."""
    RUNNING = "running"
    INSTALLED_NOT_RUNNING = "installed_not_running"
    NOT_INSTALLED = "not_installed"
    UNKNOWN = "unknown"

class DockerStatusChecker:
    """Utility class for checking Docker installation and running status."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_docker_status(self) -> Tuple[DockerStatus, str]:
        """
        Check if Docker is installed and running.
        
        Returns:
            Tuple[DockerStatus, str]: Status enum and a descriptive message
        """
        system = platform.system().lower()
        
        if system == "windows":
            return self._check_windows()
        elif system == "linux":
            return self._check_linux()
        elif system == "darwin":  # macOS
            return self._check_mac()
        else:
            return DockerStatus.UNKNOWN, f"Unsupported platform: {system}"
    
    def _check_windows(self) -> Tuple[DockerStatus, str]:
        """Check Docker status on Windows."""
        # First check if Docker is installed by looking for docker.exe
        try:
            # Check if docker.exe is in PATH
            result = subprocess.run(
                ["where", "docker"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if result.returncode != 0:
                return DockerStatus.NOT_INSTALLED, "Docker is not installed"
                
            # Check if Docker service is running
            result = subprocess.run(
                ["sc", "query", "docker"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if "RUNNING" in result.stdout:
                # Double-check with docker version command
                version_check = subprocess.run(
                    ["docker", "version"], 
                    capture_output=True, 
                    text=True, 
                    check=False
                )
                if version_check.returncode == 0:
                    return DockerStatus.RUNNING, "Docker is installed and running"
                else:
                    return DockerStatus.INSTALLED_NOT_RUNNING, "Docker is installed but not responding"
            else:
                return DockerStatus.INSTALLED_NOT_RUNNING, "Docker is installed but not running"
                
        except Exception as e:
            self.logger.error(f"Error checking docker status: {e}")
            return DockerStatus.UNKNOWN, f"Error checking Docker status: {str(e)}"
    
    def _check_linux(self) -> Tuple[DockerStatus, str]:
        """Check Docker status on Linux."""
        # Check if Docker is installed
        try:
            which_result = subprocess.run(
                ["which", "docker"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            if which_result.returncode != 0:
                return DockerStatus.NOT_INSTALLED, "Docker is not installed"
                
            # Check if Docker daemon is running
            systemctl_result = subprocess.run(
                ["systemctl", "is-active", "docker"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if systemctl_result.stdout.strip() == "active":
                # Verify with docker version
                version_result = subprocess.run(
                    ["docker", "version"], 
                    capture_output=True, 
                    text=True, 
                    check=False
                )
                
                if version_result.returncode == 0:
                    return DockerStatus.RUNNING, "Docker is installed and running"
                else:
                    return DockerStatus.INSTALLED_NOT_RUNNING, "Docker service appears active but not responding"
            else:
                return DockerStatus.INSTALLED_NOT_RUNNING, "Docker is installed but not running"
                
        except Exception as e:
            # Try alternative check with docker version
            try:
                version_result = subprocess.run(
                    ["docker", "version"], 
                    capture_output=True, 
                    text=True, 
                    check=False
                )
                
                if version_result.returncode == 0:
                    return DockerStatus.RUNNING, "Docker is installed and running"
                else:
                    return DockerStatus.INSTALLED_NOT_RUNNING, "Docker is installed but not running"
            except Exception:
                return DockerStatus.UNKNOWN, f"Error checking Docker status: {str(e)}"
    
    def _check_mac(self) -> Tuple[DockerStatus, str]:
        """Check Docker status on macOS."""
        # Check if Docker is installed
        try:
            which_result = subprocess.run(
                ["which", "docker"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            if which_result.returncode != 0:
                return DockerStatus.NOT_INSTALLED, "Docker is not installed"
                
            # On macOS, we can check with docker version command
            version_result = subprocess.run(
                ["docker", "version"], 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            if version_result.returncode == 0:
                return DockerStatus.RUNNING, "Docker is installed and running"
            else:
                # Docker Desktop might be installed but not running
                ps_result = subprocess.run(
                    ["ps", "-ef"], 
                    capture_output=True, 
                    text=True, 
                    check=False
                )
                
                if "Docker Desktop.app" in ps_result.stdout or "com.docker.docker" in ps_result.stdout:
                    return DockerStatus.INSTALLED_NOT_RUNNING, "Docker is installed but not fully initialized"
                else:
                    return DockerStatus.INSTALLED_NOT_RUNNING, "Docker is installed but not running"
                
        except Exception as e:
            return DockerStatus.UNKNOWN, f"Error checking Docker status: {str(e)}"

    def get_installation_instructions(self) -> Dict[str, str]:
        """
        Get platform-specific Docker Engine installation instructions.
        
        Returns:
            Dict[str, str]: Dictionary containing installation instructions and URLs
        """
        system = platform.system().lower()
        
        if system == "windows":
            return {
                "title": "Install Docker Engine on Windows",
                "instructions": "Docker Engine can be installed on Windows in several ways:\n\n"
                               "1. Using WSL2 (Windows Subsystem for Linux)\n"
                               "2. Using Docker Engine on Windows Server\n"
                               "3. Manual installation with binaries\n\n"
                               "WSL2 is recommended for most users:",
                "download_url": "https://docs.docker.com/engine/install/",
                "docs_url": "https://docs.docker.com/engine/install/#server"
            }
        elif system == "linux":
            return {
                "title": "Install Docker Engine on Linux",
                "instructions": "Docker Engine installation varies by Linux distribution:\n\n"
                               "• Ubuntu: sudo apt-get update && sudo apt-get install docker-ce docker-ce-cli containerd.io\n"
                               "• Fedora: sudo dnf install docker-ce docker-ce-cli containerd.io\n"
                               "• CentOS: sudo yum install docker-ce docker-ce-cli containerd.io\n\n"
                               "See the docs for detailed instructions for your specific distribution.",
                "download_url": "https://docs.docker.com/engine/install/",
                "docs_url": "https://docs.docker.com/engine/install/"
            }
        elif system == "darwin":  # macOS
            return {
                "title": "Install Docker Engine on macOS",
                "instructions": "Docker Engine can be installed on macOS using:\n\n"
                              "1. Homebrew: brew install docker\n"
                              "2. Manual binary installation\n"
                              "3. Using Colima (recommended): brew install colima docker\n\n"
                              "After installation, start the Docker daemon with: colima start",
                "download_url": "https://github.com/abiosoft/colima",
                "docs_url": "https://docs.docker.com/engine/install/"
            }
        else:
            return {
                "title": "Install Docker Engine",
                "instructions": "Please visit the Docker website for installation instructions for your platform.",
                "download_url": "https://docs.docker.com/engine/install/",
                "docs_url": "https://docs.docker.com/engine/install/"
            }
        
    def get_start_instructions(self) -> Dict[str, str]:
        """
        Get platform-specific instructions for starting Docker Engine.
        
        Returns:
            Dict[str, str]: Dictionary containing start instructions
        """
        system = platform.system().lower()
        
        if system == "windows":
            return {
                "title": "Start Docker Engine on Windows",
                "instructions": "If using WSL2:\n\n"
                               "1. Open PowerShell as Administrator\n"
                               "2. Start WSL with: wsl\n"
                               "3. In WSL, start Docker: sudo service docker start\n\n"
                               "If using Windows Server:\n"
                               "1. Open PowerShell as Administrator\n"
                               "2. Run: Start-Service docker",
                "command": "Start-Service docker"
            }
        elif system == "linux":
            return {
                "title": "Start Docker Engine on Linux",
                "instructions": "Use the following terminal command to start the Docker service:",
                "command": "sudo systemctl start docker"
            }
        elif system == "darwin":  # macOS
            return {
                "title": "Start Docker Engine on macOS",
                "instructions": "If using Colima (recommended):\n\n"
                               "1. Open Terminal\n"
                               "2. Run: colima start\n\n"
                               "If using other methods, follow the specific instructions for your setup.",
                "command": "colima start"
            }
        else:
            return {
                "title": "Start Docker",
                "instructions": "Please refer to the Docker documentation for instructions on how to start Docker on your platform.",
                "command": None
            }
