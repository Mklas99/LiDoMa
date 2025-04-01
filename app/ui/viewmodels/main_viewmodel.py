from typing import List, Dict, Tuple, Callable
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from app.core.services.service_locator import ServiceLocator
from app.core.services.docker_service import DockerService
from app.infrastructure.docker_client import DockerCommandExecutor
from app.ui.theme_manager import ThemeManager

class MainViewModel(QObject):
    """ViewModel for the main application window"""
    
    # Signals
    refresh_started = pyqtSignal()
    refresh_completed = pyqtSignal(list, list, list, list, str)
    log_message = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    contexts_changed = pyqtSignal(list)
    
    def __init__(self, docker_service: DockerService):
        super().__init__()
        self.docker_service = docker_service
        
    @pyqtSlot()
    def invalidate_contexts_cache(self):
        """Invalidate any cached Docker contexts to force a refresh."""
        # If the context service has a method to invalidate cache, call it
        if hasattr(self.docker_service.context_service, 'invalidate_cache'):
            self.docker_service.context_service.invalidate_cache()

    @pyqtSlot()
    def get_docker_contexts(self) -> Tuple[List[str], str]:
        """Get the list of available Docker contexts"""
        contexts, error = self.docker_service.get_docker_contexts()
        
        # Always add "All" as an option if it's not already there
        if not error and "All" not in contexts:
            contexts.insert(0, "All")
            
        if not error:
            self.contexts_changed.emit(contexts)
        return contexts, error
        
    @pyqtSlot(str)
    def set_docker_context(self, context_name: str) -> bool:
        """Set the current Docker context"""
        return self.docker_service.set_context(context_name)
        
    @pyqtSlot(str)
    def log(self, message: str):
        """Log a message to the application log"""
        self.log_message.emit(message)
        
    @pyqtSlot(str)
    def report_error(self, error_message: str):
        """Report an error to be displayed to the user"""
        self.error_occurred.emit(error_message)
        
    @pyqtSlot()
    def get_docker_version(self) -> str:
        """Get the Docker version string"""
        output, _ = DockerCommandExecutor.run_command(["docker", "version", "--format", "{{.Server.Version}}"])
        return output if output else "Unknown"

    @pyqtSlot()
    def get_current_context(self) -> str:
        """Get the current Docker context."""
        return self.docker_service.get_current_context()
        
    @pyqtSlot()
    def refresh_all_resources(self):
        """Refresh all Docker resources and emit appropriate signals"""
        # First, invalidate contexts cache to ensure fresh data
        self.invalidate_contexts_cache()
        
        # Get current context
        current_context = self.get_current_context()
        
        # Log the refresh operation
        if current_context == "All":
            self.log("Starting refresh of Docker resources across all contexts...")
        else:
            self.log(f"Starting refresh of Docker resources for context: {current_context}...")
            
        self.refresh_started.emit()
        
        try:
            # Use the built-in "All" context handling in docker_service
            containers = self.docker_service.list_containers(context=current_context)
            images = self.docker_service.list_images(context=current_context)
            volumes = self.docker_service.list_volumes(context=current_context)
            networks = self.docker_service.list_networks(context=current_context)
            
            # Log resource counts
            if current_context == "All":
                self.log(f"Resources found across all contexts: {len(containers)} containers, " +
                         f"{len(images)} images, {len(volumes)} volumes, {len(networks)} networks")
            else:
                self.log(f"Resources found in context '{current_context}': {len(containers)} containers, " +
                        f"{len(images)} images, {len(volumes)} volumes, {len(networks)} networks")
                    
            self.refresh_completed.emit(containers, images, volumes, networks, "")
        except Exception as e:
            error_message = f"Error refreshing Docker resources: {str(e)}"
            self.report_error(error_message)
            self.refresh_completed.emit([], [], [], [], error_message)

    def create_some_ui_component(self):
        # Create the component
        component = SomeUIComponent()
        
        # Ensure the theme is applied
        ThemeManager.refresh_widget_style(component)
        
        return component
