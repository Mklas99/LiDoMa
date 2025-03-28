import docker
import subprocess
from typing import List, Dict, Tuple, Optional, Any
from docker.errors import NotFound, APIError

class DockerCommandExecutor:
    """Executes Docker CLI commands with error handling."""
    
    @staticmethod
    def run_command(args: List[str]) -> Tuple[str, str]:
        """Execute Docker CLI commands with error handling.
        
        Args:
            args: List of command arguments
            
        Returns:
            Tuple containing stdout and stderr
        """
        try:
            process = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return process.stdout.strip(), ""
        except subprocess.CalledProcessError as e:
            return e.stdout.strip(), e.stderr.strip()

class DockerClient:
    """Wrapper around Docker SDK client with context support."""
    
    def __init__(self):
        self._client = None
        self.initialize_client()
        
    def initialize_client(self):
        """Initialize Docker client from environment."""
        try:
            self._client = docker.from_env()
        except Exception as e:
            print(f"Error initializing Docker client: {e}")
            self._client = None
            
    @property
    def client(self):
        """Get the Docker client instance."""
        if self._client is None:
            self.initialize_client()
        return self._client
        
    def is_connected(self) -> bool:
        """Check if Docker daemon is accessible."""
        try:
            if self.client:
                self.client.ping()
                return True
        except Exception:
            return False
        return False
        
    def get_docker_version(self) -> str:
        """Get Docker daemon version."""
        try:
            if self.client:
                return self.client.version().get("Version", "Unknown")
            return "Unknown"
        except Exception:
            output, _ = DockerCommandExecutor.run_command(["docker", "version", "--format", "{{.Server.Version}}"])
            return output if output else "Unknown"
