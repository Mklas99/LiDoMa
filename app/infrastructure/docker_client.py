"""
Docker client infrastructure implementation.
"""
import subprocess
from typing import Tuple, Optional, Dict, Any
import docker

class DockerCommandExecutor:
    """Static utility for executing Docker CLI commands."""
    
    @staticmethod
    def run_command(command: list) -> Tuple[str, Optional[str]]:
        """Run a Docker command and return output and error."""
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout.strip(), None
        except subprocess.CalledProcessError as e:
            return "", e.stderr.strip()
        except Exception as e:
            return "", str(e)

class DockerClient:
    """Client for Docker SDK and CLI commands."""
    
    def __init__(self):
        """Initialize Docker client."""
        try:
            self.client = docker.from_env()
        except Exception as e:
            # Log the error here, but let the app continue
            print(f"Error connecting to Docker: {str(e)}")
            self.client = None
