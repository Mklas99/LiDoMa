from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt

class LogWidget(QTextEdit):
    """Widget for displaying log messages."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                color: #E1E1E1;
                border: 1px solid #3E3E42;
                border-radius: 4px;
                font-family: Consolas, monospace;
                font-size: 9pt;
            }
        """)
        
        # Welcome message
        self.append("[System] Docker Manager started. Ready to manage Docker resources.")
    
    def append(self, message):
        """Add message to the log"""
        super().append(message)
        
    def clear(self):
        """Clear all log content"""
        self.clear()
