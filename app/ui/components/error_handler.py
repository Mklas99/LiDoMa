"""
Error handling component for the application.
"""
from PyQt5.QtWidgets import QLabel, QWidget, QPushButton, QHBoxLayout
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
        
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.error_label)
        if parent:
            self.acknowledge_btn = QPushButton("Acknowledge", parent)
            self.acknowledge_btn.setVisible(False)
            self.acknowledge_btn.setFixedWidth(100)
            self.acknowledge_btn.clicked.connect(self.clear_error)
            self.layout.addWidget(self.acknowledge_btn)
    
    def show_error(self, message: str):
        """Show an error message."""
        self.error_label.setText(message)
        self.error_label.setFixedHeight(50)
        self.error_label.setVisible(True)
        if hasattr(self, 'acknowledge_btn'):
            self.acknowledge_btn.setVisible(True)
    
    def clear_error(self):
        """Clear the current error message."""
        self.error_label.setText("")
        self.error_label.setFixedHeight(0)
        self.error_label.setVisible(False)
        if hasattr(self, 'acknowledge_btn'):
            self.acknowledge_btn.setVisible(False)
