from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QTimer

class ErrorHandler:
    """Handles error display and management."""
    
    def __init__(self, parent):
        self.parent = parent
        
        # Create error message label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("""
            background-color: #E74C3C;
            color: white;
            border-radius: 4px;
            padding: 10px;
            font-weight: bold;
        """)
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        
        # Timer for auto-hiding errors
        self.error_timer = QTimer()
        self.error_timer.setSingleShot(True)
        self.error_timer.timeout.connect(self.clear_error)
    
    def show_error(self, message, duration=5000):
        """Display an error message for the given duration (ms)."""
        self.error_label.setText(message)
        self.error_label.show()
        
        # Reset and start the timer
        self.error_timer.stop()
        self.error_timer.start(duration)
    
    def clear_error(self):
        """Hide the error message."""
        self.error_label.hide()
