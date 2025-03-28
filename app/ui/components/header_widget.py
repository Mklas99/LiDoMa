"""
Header widget containing search and controls.
"""
from typing import Callable
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class SearchWidget(QWidget):
    """Search input widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create search label
        self.search_label = QLabel("Search:")
        self.layout.addWidget(self.search_label)
        
        # Create search input
        from PyQt5.QtWidgets import QLineEdit
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter containers, images, etc...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self.search_changed)
        self.layout.addWidget(self.search_input)
        
        self.callback = None
    
    def search_changed(self):
        """Handle search text change."""
        if self.callback:
            self.callback()
    
    def set_search_callback(self, callback: Callable):
        """Set callback for search text changes."""
        self.callback = callback
    
    def get_search_text(self) -> str:
        """Get current search text."""
        return self.search_input.text()
    
    def set_focus(self):
        """Focus the search input."""
        self.search_input.setFocus()

class HeaderWidget(QWidget):
    """Header widget with search and controls."""
    
    def __init__(self, parent=None, search_callback: Callable = None, refresh_callback: Callable = None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create title
        self.title_label = QLabel("Docker Manager")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.layout.addWidget(self.title_label)
        
        # Add stretching space
        self.layout.addStretch()
        
        # Create search widget
        self.search_widget = SearchWidget()
        if search_callback:
            self.search_widget.set_search_callback(search_callback)
        self.layout.addWidget(self.search_widget)
        
        # Create refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(refresh_callback if refresh_callback else lambda: None)
        self.layout.addWidget(self.refresh_button)
    
    def get_search_widget(self) -> SearchWidget:
        """Get the search widget."""
        return self.search_widget
    
    def disable_refresh(self):
        """Disable the refresh button."""
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Refreshing...")
    
    def enable_refresh(self):
        """Enable the refresh button."""
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("Refresh")
