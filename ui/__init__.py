"""UI components for Docker Manager application."""

# Make main window class available directly from ui package
from .main_window import DockerManagerApp
from .styles import get_application_style

__all__ = ['DockerManagerApp', 'get_application_style']
