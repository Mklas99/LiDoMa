"""
Status bar components for the application.
"""
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

class StatusBarComponents:
    """Factory for status bar components."""
    
    @staticmethod
    def create_status_label() -> QLabel:
        """Create a status label for the status bar."""
        label = QLabel("Ready")
        label.setMinimumWidth(200)
        return label
    
    @staticmethod
    def create_docker_version_label(version: str) -> QLabel:
        """Create a Docker version label for the status bar."""
        label = QLabel(f"Docker {version}")
        label.setAlignment(Qt.AlignRight)
        return label
    
    @staticmethod
    def create_hint_label() -> QLabel:
        """Create a hint label for the main window."""
        label = QLabel("Tip: For WSL containers, use 'docker context use wsl' in the terminal")
        label.setStyleSheet("color: gray; font-style: italic;")
        label.setAlignment(Qt.AlignCenter)
        return label
