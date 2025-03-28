from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QTabWidget, QStyle)
from PyQt5.QtCore import QSize, Qt, QEvent
from PyQt5.QtGui import QIcon, QFont

class SearchWidget(QWidget):
    """Search widget with icon and search box."""
    
    def __init__(self, parent=None, search_callback=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Create search box
        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setPlaceholderText("Search...")
        self.search_box.setClearButtonEnabled(True)
        if search_callback:
            self.search_box.textChanged.connect(search_callback)
        
        # Add search icon
        search_icon = QLabel()
        search_icon.setPixmap(self.style().standardPixmap(QStyle.SP_FileDialogContentsView).scaled(QSize(16, 16)))
        search_icon.setStyleSheet("background-color: transparent;")
        
        layout.addWidget(search_icon)
        layout.addWidget(self.search_box)
    
    def get_search_text(self):
        """Get the current search text."""
        return self.search_box.text()
    
    def set_focus(self):
        """Set focus to the search box."""
        self.search_box.setFocus()
        
    def clear(self):
        """Clear the search box."""
        self.search_box.clear()

class HeaderWidget(QWidget):
    """Header widget with search and refresh button."""
    
    def __init__(self, parent=None, search_callback=None, refresh_callback=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Create search widget
        self.search_widget = SearchWidget(self, search_callback)
        
        # Create refresh button
        self.refresh_button = QPushButton(" Refresh")
        self.refresh_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        if refresh_callback:
            self.refresh_button.clicked.connect(refresh_callback)
        
        # Add widgets to header
        layout.addWidget(self.search_widget, 1)
        layout.addWidget(self.refresh_button)
    
    def disable_refresh(self):
        """Disable the refresh button."""
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText(" Refreshing...")
        
    def enable_refresh(self):
        """Enable the refresh button."""
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText(" Refresh")
        
    def get_search_widget(self):
        """Get the search widget."""
        return self.search_widget

class StatusBarComponents:
    """Factory for status bar components."""
    
    @staticmethod
    def create_status_label(text="Ready"):
        """Create a status label for the status bar."""
        status_label = QLabel(text)
        status_label.setStyleSheet("color: #E1E1E1;")
        return status_label
    
    @staticmethod
    def create_docker_version_label(version):
        """Create a Docker version label for the status bar."""
        docker_version = QLabel(f"Docker {version}")
        docker_version.setStyleSheet("color: #96a6c8; padding-right: 10px;")
        return docker_version
    
    @staticmethod
    def create_hint_label():
        """Create a hint label for Docker usage."""
        hint_label = QLabel("Note: WSL containers can be managed through the Docker Desktop context.")
        hint_label.setStyleSheet("color: #96a6c8; font-style: italic; padding: 4px;")
        hint_label.setAlignment(Qt.AlignCenter)
        return hint_label
