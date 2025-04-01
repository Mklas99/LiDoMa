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
    """Header widget with search box and control buttons."""
    
    def __init__(self, parent, search_callback=None, refresh_callback=None):
        super().__init__(parent)
        self.search_callback = search_callback
        self.refresh_callback = refresh_callback
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add search widget
        self.search_widget = SearchWidget(self)
        self.search_widget.set_search_callback(self.search_callback)
        layout.addWidget(self.search_widget)
        
        # Add refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setIcon(QIcon.fromTheme("view-refresh"))
        self.refresh_button.setToolTip("Refresh all Docker contexts and resources (Ctrl+R)")
        self.refresh_button.clicked.connect(self.on_refresh_clicked)
        layout.addWidget(self.refresh_button)
        
        # Add settings button if needed
        # ...
        
    def on_refresh_clicked(self):
        """Handle refresh button click."""
        if self.refresh_callback:
            # Call the refresh callback provided by the parent
            self.refresh_callback()
            
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
