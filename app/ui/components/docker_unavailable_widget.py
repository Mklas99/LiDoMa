from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                           QHBoxLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QPixmap

class DockerUnavailableWidget(QWidget):
    """Widget displayed when Docker is not available."""
    
    retry_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Add spacer at top for aesthetic reasons
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Add warning icon and header
        header_layout = QHBoxLayout()
        
        # You could add a Docker icon here if available
        icon_label = QLabel()
        icon_label.setFixedSize(64, 64)
        try:
            # Try to load an icon - could be replaced with an appropriate Docker icon
            pixmap = QPixmap(":/icons/warning.png")
            if not pixmap.isNull():
                icon_label.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            # Fallback if icon isn't available
            icon_label.setText("⚠️")
            icon_label.setFont(QFont("Arial", 32))
            icon_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addStretch()
        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Add title
        title_label = QLabel("Docker is not available")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Add description
        desc_label = QLabel(
            "Docker service appears to be unavailable. Please ensure that:\n\n"
            "• Docker is installed on your system\n"
            "• Docker service is running\n"
            "• You have the necessary permissions to access Docker\n"
            "• Docker API endpoints are accessible"
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Add retry button
        button_layout = QHBoxLayout()
        retry_button = QPushButton("Retry Connection")
        retry_button.setMinimumWidth(150)
        retry_button.clicked.connect(self.retry_requested.emit)
        
        button_layout.addStretch()
        button_layout.addWidget(retry_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Add another spacer at the bottom
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
