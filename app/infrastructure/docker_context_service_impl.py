"""
Implementation of the Docker context service using Docker CLI.
"""
from typing import List, Tuple
import logging
import json
import platform
import subprocess
from app.domain.services import DockerContextService
from app.infrastructure.docker_client import DockerCommandExecutor

class DockerContextServiceImpl(DockerContextService):
    """Implementation of Docker context service."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._current_context = None
        self._cached_contexts = None
        self._is_windows = platform.system() == "Windows"
        self.logger.info(f"Docker Context Service initialized on {platform.system()} platform")
    
    def invalidate_cache(self):
        """Invalidate cached context data to force a refresh."""
        self._current_context = None
        self._cached_contexts = None
        self.logger.debug("Docker context cache invalidated")
    
    def get_contexts(self) -> Tuple[List[str], str]:
        """Get available Docker contexts."""
        # Skip using cached contexts - always get fresh data
        self._cached_contexts = None

        try:
            output, error = DockerCommandExecutor.run_command([
                "docker", "context", "ls", "--format", "{{json .}}"
            ])
            
            if error:
                self.logger.error(f"Error getting Docker contexts: {error}")
                return [], error
            
            contexts = []
            for line in output.splitlines():
                if not line.strip():
                    continue
                
                try:
                    context_data = json.loads(line)
                    name = context_data.get("Name", "")
                    if name:
                        contexts.append(name)
                except json.JSONDecodeError:
                    # Fall back to basic parsing if JSON fails
                    parts = line.split()
                    if parts and parts[0] != "NAME":  # Skip header
                        contexts.append(parts[0])
            
            # If JSON parsing returned no contexts, fall back to simple format
            if not contexts:
                output, _ = DockerCommandExecutor.run_command([
                    "docker", "context", "ls", "--format", "{{.Name}}"
                ])
                contexts = [ctx.strip() for ctx in output.splitlines() if ctx.strip()]
            
            # Cache the contexts
            self._cached_contexts = contexts
            
            # Check for wsl contexts
            wsl_contexts = [ctx for ctx in contexts if ctx.startswith("wsl-")]
            if wsl_contexts:
                self.logger.info(f"Found WSL contexts: {', '.join(wsl_contexts)}")
            
            # Log all found contexts
            self.logger.info(f"Found {len(contexts)} Docker contexts: {', '.join(contexts)}")
            
            return contexts, ""
        except Exception as e:
            error_message = f"Error getting Docker contexts: {str(e)}"
            self.logger.error(error_message)
            return [], error_message
    
    def get_current_context(self) -> str:
        """Get current Docker context."""
        if self._current_context:
            return self._current_context
            
        try:
            output, error = DockerCommandExecutor.run_command([
                "docker", "context", "show"
            ])
            
            if error:
                self.logger.error(f"Error getting current Docker context: {error}")
                return "default"
                
            self._current_context = output.strip()
            self.logger.info(f"Current Docker context: {self._current_context}")
            return self._current_context
        except Exception as e:
            self.logger.error(f"Error getting current Docker context: {str(e)}")
            return "default"
    
    def set_context(self, context_name: str) -> bool:
        """Set Docker context."""
        if not context_name:
            return False
            
        # Don't switch if already on the requested context
        if self._current_context == context_name:
            self.logger.info(f"Already using context '{context_name}', no switch needed")
            return True
            
        try:
            self.logger.info(f"Switching Docker context to: {context_name}")
            output, error = DockerCommandExecutor.run_command([
                "docker", "context", "use", context_name
            ])
            
            # Docker outputs "Current context is now X" to stderr, but it's not an error
            # It's actually a confirmation of success, so we should check for this pattern
            if error and "Current context is now" in error:
                # This is actually a success message
                self.logger.info(f"Successfully changed Docker context: {error}")
                self._current_context = context_name
                return True
            elif error:
                self.logger.error(f"Error setting Docker context: {error}")
                return False
                
            self._current_context = context_name
            self.logger.info(f"Docker context set to: {context_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting Docker context: {str(e)}")
            return False