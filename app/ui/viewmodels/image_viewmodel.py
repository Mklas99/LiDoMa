from typing import List, Dict, Optional
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from app.core.services.docker_service import DockerService

class ImageViewModel(QObject):
    """ViewModel for image operations."""
    
    # Signals
    image_operation_completed = pyqtSignal(bool, str)
    image_details_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, docker_service: DockerService):
        super().__init__()
        self.docker_service = docker_service
    
    @pyqtSlot(str, str)
    def remove_image(self, image_id: str, context: str = "default"):
        """Remove an image"""
        success = self.docker_service.remove_image(image_id, context)
        message = f"Removed image: {image_id}" if success else f"Failed to remove image: {image_id}"
        self.image_operation_completed.emit(success, message)
        
    @pyqtSlot(str, str)
    def pull_image(self, image_name: str, context: str = "default"):
        """Pull an image from registry."""
        # This operation could be run in a thread using the run_in_thread utility
        from app.ui.utils.thread_utils import run_in_thread
        
        def on_pull_complete(success_and_error):
            success, error_message = success_and_error
            if success:
                message = f"Image {image_name} pulled successfully"
                self.image_operation_completed.emit(True, message)
            else:
                user_message = self._create_user_friendly_error(error_message, image_name)
                self.error_occurred.emit(user_message)
                self.image_operation_completed.emit(False, user_message)
        
        # Inform user the operation has started
        self.error_occurred.emit(f"Started pulling image: {image_name}")
        
        # Run in background thread
        run_in_thread(
            self,
            on_pull_complete,
            self.docker_service.pull_image,
            image_name,
            context,
            error_callback=lambda e: self.error_occurred.emit(f"Error pulling image {image_name}: {str(e)}")
        )
    
    def _create_user_friendly_error(self, error_message: str, image_name: str) -> str:
        """Create a user-friendly error message for Docker errors."""
        if not error_message:
            return f"Failed to pull image: {image_name}"
            
        # Format the basic error message
        user_message = f"Error pulling image: {error_message}"
        
        # Add explanations for common error patterns
        if "invalid reference format" in error_message:
            user_message += "\n\nThe image name contains invalid characters. Docker image names must follow format: [registry/][username/]name[:tag]"
        
        elif "pull access denied" in error_message and "repository does not exist" in error_message:
            user_message += "\n\nThe image could not be found in the registry. Please check:\n" \
                           "• The image name is spelled correctly\n" \
                           "• The image exists in the registry\n" \
                           "• You have permission to access the image\n" \
                           "• You may need to log in with 'docker login' if the image is private"
                           
        elif "unauthorized" in error_message.lower():
            user_message += "\n\nAuthentication failed. Please log in with 'docker login' before pulling this image."
            
        elif "connection refused" in error_message.lower():
            user_message += "\n\nCould not connect to Docker registry. Please check your internet connection and Docker daemon status."
            
        elif "unknown: not found" in error_message.lower():
            user_message += "\n\nThe specified tag was not found for this image. Check available tags for this image in the registry."
        
        return user_message
