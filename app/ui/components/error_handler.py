"""
Error handling component for the application.
"""
from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt

class ErrorHandler:
    """Error handling for the application UI."""
    
    def __init__(self, parent: QWidget = None):
        """Initialize error handler."""
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("background-color: #ffcccc; color: #990000; padding: 5px; border-radius: 3px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setFixedHeight(0)  # Start hidden
        self.error_label.setVisible(False)
    
    def show_error(self, message: str):
        """Show an error message."""
        self.error_label.setText(message)
        self.error_label.setFixedHeight(50)
        self.error_label.setVisible(True)
    
    def clear_error(self):
        """Clear the current error message."""
        self.error_label.setText("")
        self.error_label.setFixedHeight(0)
        self.error_label.setVisible(False)
