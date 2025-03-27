from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QApplication, QSplitter, 
                            QShortcut, QStatusBar, QTabWidget, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence
from datetime import datetime

from docker_service import DockerService
from refresh_worker import RefreshWorker
from ui.styles import get_application_style
from ui.components import UIComponents
from ui.container_tab import ContainerTab
from ui.image_tab import ImageTab
from ui.volume_tab import VolumeTab
from ui.network_tab import NetworkTab
from ui.error_handler import ErrorHandler
from ui.log_widget import LogWidget

class DockerManagerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Docker Manager")
        self.resize(900, 700)
        
        # Initialize Docker service
        self.docker_service = DockerService()
        
        # Initialize components
        self.error_handler = ErrorHandler(self)
        self.ui_components = UIComponents(self)
        self.log_widget = LogWidget(self)
        self.container_tab = ContainerTab(self)
        self.image_tab = ImageTab(self)
        self.volume_tab = VolumeTab(self)
        self.network_tab = NetworkTab(self)
        
        self.initUI()
        self.refresh_worker = None
        self.setup_shortcuts()
        self.refresh_data()

    def apply_modern_style(self):
        """Apply modern styling to the application"""
        # Set application-wide font
        app_font = QFont("Segoe UI", 9)
        QApplication.setFont(app_font)
        
        # Apply stylesheet
        self.setStyleSheet(get_application_style())

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        central_widget.setLayout(main_layout)

        # Add error label
        main_layout.addWidget(self.error_handler.error_label)
        
        # Add header with search and controls
        main_layout.addWidget(self.ui_components.create_header_widget())

        # Create splitter with tabs and log area
        self.main_splitter = QSplitter(Qt.Vertical)
        self.main_splitter.setHandleWidth(8)
        self.main_splitter.setChildrenCollapsible(True)  # Allow log widget to be collapsed
        
        # Create tab container widget
        tabs_container = QFrame()
        tabs_container.setFrameShape(QFrame.StyledPanel)
        tabs_layout = QVBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget without icons
        self.tabs = QTabWidget()
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setElideMode(Qt.ElideRight)
        
        # Add tabs for different resources (without icons)
        self.tabs.addTab(self.container_tab, "Containers")
        self.tabs.addTab(self.image_tab, "Images")
        self.tabs.addTab(self.volume_tab, "Volumes")
        self.tabs.addTab(self.network_tab, "Networks")
        
        tabs_layout.addWidget(self.tabs)
        
        # Add tab container and log widget to splitter
        self.main_splitter.addWidget(tabs_container)
        self.main_splitter.addWidget(self.log_widget)
        
        # Set initial sizes - making the log widget smaller
        self.main_splitter.setSizes([600, 100])
        
        main_layout.addWidget(self.main_splitter)
        
        # Add hint for WSL containers
        main_layout.addWidget(self.ui_components.create_hint_label())
        
        # Status bar setup
        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(28)
        self.setStatusBar(self.status_bar)
        
        # Status label
        self.status_label = self.ui_components.create_status_label()
        self.status_bar.addPermanentWidget(self.status_label)
        
        # Docker version info
        version_output, _ = self.docker_service.run_docker_command(["docker", "version", "--format", "{{.Server.Version}}"])
        if version_output:
            docker_version = self.ui_components.create_docker_version_label(version_output)
            self.status_bar.addPermanentWidget(docker_version)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for common actions"""
        # Refresh shortcut (Ctrl+R)
        refresh_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        refresh_shortcut.activated.connect(self.refresh_data)
        
        # Search focus shortcut (Ctrl+F)
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(lambda: self.ui_components.search_box.setFocus())
        
        # Switch tabs shortcuts
        for i in range(4):  # For 4 tabs (updated for network tab)
            tab_shortcut = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            tab_shortcut.activated.connect(lambda idx=i: self.tabs.setCurrentIndex(idx))
        
        # Clear log (Ctrl+L)
        clear_log_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        clear_log_shortcut.activated.connect(self.log_widget.clear)

    def filter_tables(self):
        """Filter all resource tables based on search text"""
        search_text = self.ui_components.search_box.text().lower()
        self.container_tab.filter_table(search_text)
        self.image_tab.filter_table(search_text)
        self.volume_tab.filter_table(search_text)
        self.network_tab.filter_table(search_text)  # Add filtering for networks

    def log(self, message):
        """Append a log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_widget.append(formatted_message)
        
        # Update status bar with last action
        self.status_label.setText(message.split('\n')[0])

    def refresh_data(self):
        """Starts the worker thread to refresh all Docker resource data."""
        self.ui_components.refresh_button.setEnabled(False)
        self.error_handler.clear_error()
        
        # Clear tables
        self.container_tab.clear_table()
        self.image_tab.clear_table()
        self.volume_tab.clear_table()
        self.network_tab.clear_table()  # Clear network table
        
        self.log("Refreshing Docker data...")
        self.status_label.setText("Refreshing...")

        # Animate refresh button during refresh
        self.ui_components.refresh_button.setText(" Refreshing...")
        
        self.refresh_worker = RefreshWorker(self.docker_service)  # Pass docker_service to worker
        self.refresh_worker.results_ready.connect(self.on_refresh_complete)
        self.refresh_worker.start()

    def on_refresh_complete(self, containers, images, volumes, networks, error):
        """Slot called when the refresh worker finishes."""
        if error:
            self.log(error)
            self.error_handler.show_error(error)
            self.status_label.setText("Error refreshing data")
        else:
            self.status_label.setText(f"Found {len(containers)} containers, {len(images)} images, {len(volumes)} volumes, {len(networks)} networks")
        
        # Update resource tables
        for container in containers:
            self.container_tab.add_container_row(container)
            
        for image in images:
            self.image_tab.add_image_row(image)
            
        for volume in volumes:
            self.volume_tab.add_volume_row(volume)
            
        for network in networks:
            self.network_tab.add_network_row(network)
            
        self.log("Docker data refreshed.")
        self.ui_components.refresh_button.setEnabled(True)
        self.ui_components.refresh_button.setText(" Refresh")
        
        # Reapply any active filters
        if self.ui_components.search_box.text():
            self.filter_tables()
