"""
Docker client infrastructure implementation.
"""
import subprocess
import logging
import docker
from typing import Tuple, Optional, List, Union

class DockerCommandExecutor:
    """Execute Docker CLI commands."""
    
    @staticmethod
    def run_command(command: List[str]) -> Tuple[str, str]:
        """
        Run a Docker command using subprocess.
        
        Args:
            command: Command to run as a list of strings
            
        Returns:
            Tuple of (stdout, stderr)
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False  # Don't raise an exception on non-zero exit
            )
            return result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return "", str(e)

class DockerClient:
    """Docker client wrapper."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = None
        try:
            self.client = docker.from_env()
            self.logger.info("Docker client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Docker client: {e}")
    
    def is_connected(self) -> bool:
        """Check if connected to Docker daemon."""
        if not self.client:
            return False
            
        try:
            # Simple operation to check connectivity
            self.client.ping()
            return True
        except Exception:
            return False
    
    def get_version(self) -> Optional[str]:
        """Get Docker version."""
        if not self.client:
            return None
            
        try:
            version_info = self.client.version()
            return version_info.get("Version", "Unknown")
        except Exception as e:
            self.logger.error(f"Error getting Docker version: {e}")
            return None
