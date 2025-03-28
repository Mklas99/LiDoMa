"""
Implementation of Docker Compose service using Docker CLI.
"""
from typing import Tuple, List, Dict
import os
import json
from app.domain.services.docker_compose_service import DockerComposeService
from app.infrastructure.docker_client import DockerCommandExecutor

class DockerComposeServiceImpl(DockerComposeService):
    """Implementation of Docker Compose service using Docker CLI."""
    
    def compose_up(self, project_dir: str, detach: bool = True, context: str = "default") -> Tuple[bool, str]:
        """Start a Docker Compose project."""
        # Verify docker-compose.yml exists
        compose_file = os.path.join(project_dir, "docker-compose.yml")
        if not os.path.exists(compose_file):
            return False, f"docker-compose.yml not found in {project_dir}"
            
        cmd = ["docker-compose"]
        
        # Add context if not default
        if context != "default":
            cmd.extend(["--context", context])
            
        # Add project directory
        cmd.extend(["-f", compose_file])
        
        # Add up command and options
        cmd.append("up")
        if detach:
            cmd.append("-d")
            
        # Run command
        output, error = DockerCommandExecutor.run_command(cmd)
        
        if error:
            return False, error
            
        return True, "Successfully started compose project"
    
    def compose_down(self, project_dir: str, volumes: bool = False, context: str = "default") -> Tuple[bool, str]:
        """Stop and remove containers, networks from a Docker Compose project."""
        # Verify docker-compose.yml exists
        compose_file = os.path.join(project_dir, "docker-compose.yml")
        if not os.path.exists(compose_file):
            return False, f"docker-compose.yml not found in {project_dir}"
            
        cmd = ["docker-compose"]
        
        # Add context if not default
        if context != "default":
            cmd.extend(["--context", context])
            
        # Add project directory
        cmd.extend(["-f", compose_file])
        
        # Add down command and options
        cmd.append("down")
        if volumes:
            cmd.append("-v")
            
        # Run command
        output, error = DockerCommandExecutor.run_command(cmd)
        
        if error:
            return False, error
            
        return True, "Successfully stopped compose project"
    
    def compose_ps(self, project_dir: str, context: str = "default") -> Tuple[List[Dict], str]:
        """List containers for a Docker Compose project."""
        # Verify docker-compose.yml exists
        compose_file = os.path.join(project_dir, "docker-compose.yml")
        if not os.path.exists(compose_file):
            return [], f"docker-compose.yml not found in {project_dir}"
            
        cmd = ["docker-compose"]
        
        # Add context if not default
        if context != "default":
            cmd.extend(["--context", context])
            
        # Add project directory
        cmd.extend(["-f", compose_file])
        
        # Add ps command with json format
        cmd.extend(["ps", "--format", "json"])
            
        # Run command
        output, error = DockerCommandExecutor.run_command(cmd)
        
        if error:
            return [], error
            
        # Parse JSON output
        try:
            containers = json.loads(output)
            return containers, ""
        except json.JSONDecodeError:
            # If json format isn't supported, return the raw output
            return [], "Could not parse docker-compose ps output"
    
    def compose_logs(self, project_dir: str, service: str = None, context: str = "default") -> Tuple[str, str]:
        """Fetch logs from a Docker Compose project."""
        # Verify docker-compose.yml exists
        compose_file = os.path.join(project_dir, "docker-compose.yml")
        if not os.path.exists(compose_file):
            return "", f"docker-compose.yml not found in {project_dir}"
            
        cmd = ["docker-compose"]
        
        # Add context if not default
        if context != "default":
            cmd.extend(["--context", context])
            
        # Add project directory
        cmd.extend(["-f", compose_file])
        
        # Add logs command
        cmd.append("logs")
        
        # Add specific service if provided
        if service:
            cmd.append(service)
            
        # Run command
        output, error = DockerCommandExecutor.run_command(cmd)
        
        if error:
            return "", error
            
        return output, ""
