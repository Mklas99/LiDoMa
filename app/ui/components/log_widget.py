"""
Log display widget for the application.
"""
from PyQt5.QtWidgets import QTextEdit, QWidget
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QTextCursor

class LogWidget(QTextEdit):
    """Widget for displaying log messages."""
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        
        # Set a monospace font for better log display
        font = QFont("Consolas", 9)
        self.setFont(font)
        
        # Load max lines from settings
        settings = QSettings("LiDoMa", "DockerManager")
        self.max_lines = settings.value("maxLogEntries", 1000, type=int)
    
    def append(self, text: str):
        """Append text to the log with automatic scrolling and line limiting."""
        # Add text to the log
        super().append(text)
        
        # Auto-scroll to bottom
        self.moveCursor(QTextCursor.End)
        
        # Limit number of lines in the log
        if self.document().lineCount() > self.max_lines:
            cursor = QTextCursor(self.document())
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, 
                               self.document().lineCount() - self.max_lines)
            cursor.removeSelectedText()
    
    def clear(self):
        """Clear the log content."""
        super().clear()
    
    def update_max_lines(self):
        """Update max lines from settings."""
        settings = QSettings("LiDoMa", "DockerManager")
        self.max_lines = settings.value("maxLogEntries", 1000, type=int)
