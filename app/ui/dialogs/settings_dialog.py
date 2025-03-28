from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTabWidget, QWidget, QFormLayout, QLineEdit, 
                           QCheckBox, QLabel, QSpinBox, QComboBox, QDialogButtonBox)
from PyQt5.QtCore import Qt, QSettings

class SettingsDialog(QDialog):
    """Dialog for application settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Docker Manager Settings")
        self.resize(500, 400)
        self.setModal(True)
        
        # Load settings
        self.settings = QSettings("LiDoMa", "DockerManager")
        
        self.initUI()
        self.loadSettings()
    
    def initUI(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # General tab
        general_tab = self.create_general_tab()
        tab_widget.addTab(general_tab, "General")
        
        # Docker tab
        docker_tab = self.create_docker_tab()
        tab_widget.addTab(docker_tab, "Docker")
        
        # Display tab
        display_tab = self.create_display_tab()
        tab_widget.addTab(display_tab, "Display")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch(1)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def create_general_tab(self):
        """Create the general settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Check for updates on startup
        self.check_updates = QCheckBox("Check for updates on startup")
        layout.addRow("Updates:", self.check_updates)
        
        # Log settings
        self.log_level = QComboBox()
        self.log_level.addItems(["Info", "Debug", "Warning", "Error"])
        layout.addRow("Log Level:", self.log_level)
        
        self.max_log_entries = QSpinBox()
        self.max_log_entries.setRange(100, 10000)
        self.max_log_entries.setSingleStep(100)
        layout.addRow("Max Log Entries:", self.max_log_entries)
        
        return widget
    
    def create_docker_tab(self):
        """Create the Docker settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Docker path
        self.docker_path = QLineEdit()
        layout.addRow("Docker Executable:", self.docker_path)
        
        # Docker compose path
        self.compose_path = QLineEdit()
        layout.addRow("Docker Compose Executable:", self.compose_path)
        
        # Auto-refresh interval
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(0, 60)
        self.refresh_interval.setSingleStep(5)
        self.refresh_interval.setSpecialValueText("Disabled")
        self.refresh_interval.setSuffix(" seconds")
        layout.addRow("Auto-refresh Interval:", self.refresh_interval)
        
        return widget
    
    def create_display_tab(self):
        """Create the display settings tab."""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Theme selection
        self.theme = QComboBox()
        self.theme.addItems(["Dark", "Light", "System"])
        layout.addRow("Theme:", self.theme)
        
        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 16)
        self.font_size.setSingleStep(1)
        self.font_size.setSuffix(" pt")
        layout.addRow("UI Font Size:", self.font_size)
        
        return widget
    
    def loadSettings(self):
        """Load settings from QSettings."""
        # General tab
        self.check_updates.setChecked(self.settings.value("checkUpdates", True, type=bool))
        self.log_level.setCurrentText(self.settings.value("logLevel", "Info"))
        self.max_log_entries.setValue(self.settings.value("maxLogEntries", 1000, type=int))
        
        # Docker tab
        self.docker_path.setText(self.settings.value("dockerPath", "docker"))
        self.compose_path.setText(self.settings.value("composePath", "docker-compose"))
        self.refresh_interval.setValue(self.settings.value("refreshInterval", 0, type=int))
        
        # Display tab
        self.theme.setCurrentText(self.settings.value("theme", "Dark"))
        self.font_size.setValue(self.settings.value("fontSize", 9, type=int))
    
    def save_settings(self):
        """Save settings to QSettings."""
        # General tab
        self.settings.setValue("checkUpdates", self.check_updates.isChecked())
        self.settings.setValue("logLevel", self.log_level.currentText())
        self.settings.setValue("maxLogEntries", self.max_log_entries.value())
        
        # Docker tab
        self.settings.setValue("dockerPath", self.docker_path.text())
        self.settings.setValue("composePath", self.compose_path.text())
        self.settings.setValue("refreshInterval", self.refresh_interval.value())
        
        # Display tab
        self.settings.setValue("theme", self.theme.currentText())
        self.settings.setValue("fontSize", self.font_size.value())
        
        self.accept()
