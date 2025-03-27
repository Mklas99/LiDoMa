from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QTabWidget, QStyleFactory, QStyle)
from PyQt5.QtCore import QSize, Qt, QEvent
from PyQt5.QtGui import QIcon, QFont

class UIComponents:
    """UI component creation and management class."""
    
    def __init__(self, parent):
        self.parent = parent
        self.search_box = None
        self.refresh_button = None
    
    def create_header_widget(self):
        """Create the header widget with search and controls."""
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_widget.setLayout(header_layout)
        
        # Search box with icon
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_widget = QWidget()
        search_widget.setLayout(search_layout)
        
        # Create search box
        self.search_box = QLineEdit()
        self.search_box.setObjectName("searchBox")
        self.search_box.setPlaceholderText("Search...")
        self.search_box.setClearButtonEnabled(True)
        self.search_box.textChanged.connect(self.parent.filter_tables)
        
        # Add search icon
        search_icon = QLabel()
        search_icon.setPixmap(self.parent.style().standardPixmap(QStyle.SP_FileDialogContentsView).scaled(QSize(16, 16)))
        search_icon.setStyleSheet("background-color: transparent;")
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_box)
        
        # Create refresh button
        self.refresh_button = QPushButton(" Refresh")
        self.refresh_button.setIcon(self.parent.style().standardIcon(QStyle.SP_BrowserReload))
        self.refresh_button.clicked.connect(self.parent.refresh_data)
        
        # Add widgets to header
        header_layout.addWidget(search_widget, 1)
        header_layout.addWidget(self.refresh_button)
        
        return header_widget
    
    def create_hint_label(self):
        """Create a hint label for Docker usage."""
        hint_label = QLabel("Note: WSL containers can be managed through the Docker Desktop context.")
        hint_label.setStyleSheet("color: #96a6c8; font-style: italic; padding: 4px;")
        hint_label.setAlignment(Qt.AlignCenter)
        return hint_label
    
    def create_status_label(self):
        """Create the status bar label."""
        status_label = QLabel("Ready")
        status_label.setStyleSheet("color: #E1E1E1;")
        return status_label
    
    def create_docker_version_label(self, version):
        """Create the Docker version label for the status bar."""
        docker_version = QLabel(f"Docker {version}")
        docker_version.setStyleSheet("color: #96a6c8; padding-right: 10px;")
        return docker_version
