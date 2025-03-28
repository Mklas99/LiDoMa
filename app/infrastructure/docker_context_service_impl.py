"""
Implementation of the Docker context service using Docker CLI.
"""
from typing import List, Tuple
import os
from app.domain.services.docker_context_service import DockerContextService
from app.infrastructure.docker_client import DockerCommandExecutor

class DockerContextServiceImpl(DockerContextService):
    """Implementation of the Docker context service using Docker CLI."""
    
    def get_contexts(self) -> Tuple[List[str], str]:
        """Get the list of available Docker contexts."""
        output, error = DockerCommandExecutor.run_command(["docker", "context", "ls", "--format", "{{.Name}}"])
        contexts = output.splitlines() if output else []
        return contexts, error
    
    def get_current_context(self) -> str:
        """Get the currently active Docker context."""
        output, _ = DockerCommandExecutor.run_command(["docker", "context", "show", "--format", "{{.Name}}"])
        return output.strip() if output else "default"
    
    def set_context(self, context_name: str) -> bool:
        """Set the current Docker context."""
        _, error = DockerCommandExecutor.run_command(["docker", "context", "use", context_name])
        return error is None