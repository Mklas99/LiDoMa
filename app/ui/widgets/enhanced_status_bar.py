from PyQt5.QtWidgets import QStatusBar, QLabel, QPushButton, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPalette

class EnhancedStatusBar(QStatusBar):
    """Status bar with support for persistent error messages."""
    
    error_acknowledged = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the enhanced status bar."""
        super().__init__(parent)
        
        # Create error container widget
        self.error_container = QWidget(self)
        self.error_layout = QHBoxLayout(self.error_container)
        self.error_layout.setContentsMargins(5, 0, 5, 0)
        self.error_layout.setSpacing(5)
        
        # Create error icon/indicator
        self.error_icon = QLabel("⚠️", self)
        
        # Create error message label
        self.error_label = QLabel(self)
        self.error_label.setStyleSheet("color: red; font-weight: bold;")
        
        # Create acknowledge button
        self.acknowledge_btn = QPushButton("Acknowledge", self)
        self.acknowledge_btn.setMaximumHeight(20)
        self.acknowledge_btn.clicked.connect(self.clear_error)
        
        # Assemble layout
        self.error_layout.addWidget(self.error_icon)
        self.error_layout.addWidget(self.error_label, 1)  # Stretch to use available space
        self.error_layout.addWidget(self.acknowledge_btn)
        
        self.error_container.setLayout(self.error_layout)
        self.error_container.setVisible(False)
        
        # Add error container as permanent widget
        self.addPermanentWidget(self.error_container, 1)
        
    def showMessage(self, message, timeout=0):
        """Show a transient message in the status bar."""
        if not self.error_container.isVisible():
            super().showMessage(message, timeout)
        
    def showPersistentError(self, message):
        """Show a persistent error message that requires acknowledgment."""
        # Clear any transient message first
        self.clearMessage()
        
        # Set and show the error
        self.error_label.setText(message)
        self.error_container.setVisible(True)
        
        # Ensure the error container is brought to the top
        self.error_container.raise_()
        
    def clear_error(self):
        """Clear the persistent error message."""
        self.error_container.setVisible(False)
        self.error_acknowledged.emit()
