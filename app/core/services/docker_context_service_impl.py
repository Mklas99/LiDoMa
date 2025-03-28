from typing import List, Tuple
from domain.services import DockerContextService
from infrastructure.docker_client import DockerCommandExecutor

class DockerContextServiceImpl(DockerContextService):
    """Implementation of Docker context service."""
    
    def get_contexts(self) -> Tuple[List[str], str]:
        """Get available Docker contexts."""
        output, err = DockerCommandExecutor.run_command(["docker", "context", "ls", "--format", "{{.Name}}"])
        if err:
            return [], err
        contexts = output.splitlines()
        return contexts, ""
        
    def get_current_context(self) -> str:
        """Get the currently active Docker context."""
        output, err = DockerCommandExecutor.run_command(["docker", "context", "show"])
        if err:
            return "default"
        return output.strip()
        
    def set_context(self, context_name: str) -> bool:
        """Set the current Docker context."""
        _, err = DockerCommandExecutor.run_command(["docker", "context", "use", context_name])
        return not err
