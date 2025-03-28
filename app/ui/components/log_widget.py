"""
Log display widget for the application.
"""
from PyQt5.QtWidgets import QTextEdit, QWidget
from PyQt5.QtCore import Qt

class LogWidget(QTextEdit):
    """Widget for displaying application logs."""
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setStyleSheet("font-family: monospace; background-color: #f0f0f0;")
        self.setMaximumHeight(200)
    
    def append(self, text: str):
        """Append text to the log and scroll to the bottom."""
        super().append(text)
        # Scroll to bottom
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        self.setTextCursor(cursor)
