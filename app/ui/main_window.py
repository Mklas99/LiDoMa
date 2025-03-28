from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QApplication, QSplitter, 
                            QShortcut, QStatusBar, QTabWidget, QFrame, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt, QSettings, QTimer
from PyQt5.QtGui import QFont, QKeySequence
from datetime import datetime
import logging
import traceback

"""
Main window implementation for the Docker Manager application.
"""
# Fix imports
from app.core.services.docker_service import DockerService
from app.ui.viewmodels.main_viewmodel import MainViewModel
from app.ui.viewmodels.container_viewmodel import ContainerViewModel
from app.ui.viewmodels.image_viewmodel import ImageViewModel
from app.ui.viewmodels.volume_viewmodel import VolumeViewModel
from app.ui.viewmodels.network_viewmodel import NetworkViewModel
from app.ui.viewmodels.refresh_worker import RefreshWorker

# Import UI components
from app.ui.components.header_widget import HeaderWidget
from app.ui.components.status_bar_components import StatusBarComponents
from app.ui.components.error_handler import ErrorHandler
from app.ui.components.log_widget import LogWidget
from app.ui.components.context_selector import ContextSelector

# Import tab views
from app.ui.tabs.container_tab_view import ContainerTabView
from app.ui.tabs.image_tab_view import ImageTabView
from app.ui.tabs.volume_tab_view import VolumeTabView
from app.ui.tabs.network_tab_view import NetworkTabView

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DockerManagerApp(QMainWindow):
    """Main application window for Docker Manager."""
    
    def __init__(self, main_viewmodel: MainViewModel):
        super().__init__()
        self.setWindowTitle("Docker Manager")
        self.resize(1000, 700)
        
        # Set up application settings
        self.settings = QSettings("LiDoMa", "DockerManager")
        self.load_settings()
        
        # Store the main viewmodel
        self.main_viewmodel = main_viewmodel
        
        # Get the docker service from the main viewmodel
        self.docker_service = main_viewmodel.docker_service
        
        # Create view models
        self.container_viewmodel = ContainerViewModel(self.docker_service)
        self.image_viewmodel = ImageViewModel(self.docker_service)
        self.volume_viewmodel = VolumeViewModel(self.docker_service)
        self.network_viewmodel = NetworkViewModel(self.docker_service)
        
        # Initialize UI components
        self.error_handler = ErrorHandler(self)
        self.log_widget = LogWidget(self)
        
        # Connect viewmodel signals
        self.main_viewmodel.log_message.connect(self.log)
        self.main_viewmodel.error_occurred.connect(self.error_handler.show_error)
        self.main_viewmodel.contexts_changed.connect(self.update_contexts)
        
        # Initialize thread tracking
        self.refresh_worker = None
        self.active_workers = []
        
        # Initialize UI
        self.init_ui()
        self.setup_shortcuts()
        self.setup_menu()
        
        # Log loading message
        logger.info("Docker Manager UI initialized")
        self.log("Application started")
        
        # Load Docker contexts after a short delay to ensure UI is visible first
        QTimer.singleShot(500, self.load_contexts)
        
        # Start initial data load after UI is shown
        QTimer.singleShot(1000, self.refresh_data)

    def init_ui(self):
        """Initialize the UI components."""        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        central_widget.setLayout(main_layout)

        # Add error label to the top
        main_layout.addWidget(self.error_handler.error_label)
        
        # Add header with search and controls
        self.header_widget = HeaderWidget(
            self, 
            search_callback=self.filter_tables,
            refresh_callback=self.refresh_data
        )
        main_layout.addWidget(self.header_widget)
        
        # Add context selector
        self.context_selector = ContextSelector()
        self.context_selector.context_changed.connect(self.change_context)
        main_layout.addWidget(self.context_selector)
        
        self.main_splitter = QSplitter(Qt.Vertical)
        self.main_splitter.setHandleWidth(8)
        self.main_splitter.setChildrenCollapsible(True)
        
        # Create tab container
        tabs_container = QFrame()
        tabs_container.setFrameShape(QFrame.StyledPanel)
        tabs_layout = QVBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setMovable(True)
        self.tabs.setDocumentMode(True)
        self.tabs.setElideMode(Qt.ElideRight)
        
        # Create tab views
        self.container_tab = ContainerTabView(self, self.container_viewmodel)
        self.image_tab = ImageTabView(self, self.image_viewmodel)
        self.volume_tab = VolumeTabView(self, self.volume_viewmodel)
        self.network_tab = NetworkTabView(self, self.network_viewmodel)
        
        # Add tabs to tab widget
        self.tabs.addTab(self.container_tab, "Containers")
        self.tabs.addTab(self.image_tab, "Images")
        self.tabs.addTab(self.volume_tab, "Volumes")
        self.tabs.addTab(self.network_tab, "Networks")
        
        tabs_layout.addWidget(self.tabs)
        
        # Add tab container and log widget to splitter
        self.main_splitter.addWidget(tabs_container)
        self.main_splitter.addWidget(self.log_widget)
        
        # Set initial sizes
        self.main_splitter.setSizes([600, 100])
        
        main_layout.addWidget(self.main_splitter)
        
        # Add hint for WSL containers
        main_layout.addWidget(StatusBarComponents.create_hint_label())
        
        # Status bar setup
        self.status_bar = QStatusBar()
        self.status_bar.setFixedHeight(28)
        self.setStatusBar(self.status_bar)
        
        # Status label
        self.status_label = StatusBarComponents.create_status_label()
        self.status_bar.addPermanentWidget(self.status_label)
        
        # Docker version info
        version = self.main_viewmodel.get_docker_version()
        docker_version = StatusBarComponents.create_docker_version_label(version)
        self.status_bar.addPermanentWidget(docker_version)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts for common actions"""
        # Refresh shortcut (Ctrl+R)
        refresh_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        refresh_shortcut.activated.connect(self.refresh_data)
        
        # Search focus shortcut (Ctrl+F)
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.focus_search)
        
        # Switch tabs shortcuts
        for i in range(4):
            tab_shortcut = QShortcut(QKeySequence(f"Ctrl+{i+1}"), self)
            tab_shortcut.activated.connect(lambda idx=i: self.tabs.setCurrentIndex(idx))
        
        # Clear log (Ctrl+L)
        clear_log_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        clear_log_shortcut.activated.connect(self.log_widget.clear)

    def load_settings(self):
        """Load application settings."""        
        # Window geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        # Window state
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
        
        # Splitter state
        splitter_state = self.settings.value("splitterState")
        if splitter_state and hasattr(self, 'main_splitter'):
            self.main_splitter.restoreState(splitter_state)

    def save_settings(self):
        """Save application settings."""        
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        if hasattr(self, 'main_splitter'):
            self.settings.setValue("splitterState", self.main_splitter.saveState())

    def closeEvent(self, event):
        """Handle window close event to save settings and clean up threads."""        
        # Terminate any running worker threads
        for worker in self.active_workers:
            if worker.is_running:
                worker.terminate()
                worker.wait()  # Wait for thread to finish
        
        self.save_settings()
        super().closeEvent(event)

    def focus_search(self):
        """Set focus to search box."""        
        self.header_widget.get_search_widget().set_focus()

    def filter_tables(self):
        """Filter all resource tables based on search text"""        
        search_text = self.header_widget.get_search_widget().get_search_text().lower()
        self.container_tab.filter_table(search_text)
        self.image_tab.filter_table(search_text)
        self.volume_tab.filter_table(search_text)
        self.network_tab.filter_table(search_text)

    def log(self, message):
        """Append a log message with timestamp."""        
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_widget.append(formatted_message)
        
        # Update status bar with last action
        self.status_label.setText(message.split('\n')[0])

    def refresh_data(self, refresh_contexts=True):
        """Starts the worker thread to refresh all Docker resource data."""
        # Cancel any existing refresh operation
        if self.refresh_worker and self.refresh_worker.is_running:
            self.refresh_worker.terminate()
            self.refresh_worker.wait()
        
        # Disable refresh button
        self.header_widget.disable_refresh()
        self.error_handler.clear_error()
        
        # Clear tables
        self.container_tab.clear_table()
        self.image_tab.clear_table()
        self.volume_tab.clear_table()
        self.network_tab.clear_table()
        
        # Also refresh Docker contexts if requested
        if refresh_contexts:
            self.load_contexts(from_refresh=True)
        
        # Show current context in log
        current_context = self.context_selector.get_current_context()
        if (current_context):
            self.log(f"Refreshing Docker data for context: {current_context}...")
        else:
            self.log("Refreshing Docker data...")
            
        self.status_label.setText("Refreshing...")
        
        # Create and start worker thread
        try:
            print("Starting RefreshWorker thread...")
            self.refresh_worker = RefreshWorker(self.docker_service)
            self.refresh_worker.results_ready.connect(self.on_refresh_complete)
            self.refresh_worker.signals.error.connect(self.on_refresh_error)
            self.refresh_worker.signals.log.connect(self.log)
            self.refresh_worker.start()
            self.active_workers.append(self.refresh_worker)
            print(f"RefreshWorker started - thread ID: {self.refresh_worker.currentThreadId()}")
        except Exception as e:
            error_msg = f"Failed to start refresh worker: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            self.error_handler.show_error(error_msg)
            self.header_widget.enable_refresh()

    def on_refresh_error(self, error_msg):
        """Handle errors from the refresh worker."""        
        logger.error(error_msg)
        
        self.error_handler.show_error(error_msg)
        self.status_label.setText("Error refreshing data")
        self.header_widget.enable_refresh()

    def on_refresh_complete(self, containers, images, volumes, networks, error):
        """Slot called when the refresh worker finishes."""        
        try:
            # Clean up worker
            if self.refresh_worker in self.active_workers:
                self.active_workers.remove(self.refresh_worker)
            
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
            
            self.header_widget.enable_refresh()
            
            # Reapply any active filters
            if self.header_widget.get_search_widget().get_search_text():
                self.filter_tables()
        except Exception as e:
            error_msg = f"Error updating UI with Docker data: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            self.error_handler.show_error(error_msg)
            self.header_widget.enable_refresh()

    def update_contexts(self, contexts):
        """Update context selector with new contexts."""        
        current_context = self.context_selector.get_current_context()
        self.context_selector.set_contexts(contexts, current_context)
    
    def load_contexts(self, from_refresh=False):
        """Load available Docker contexts."""        
        contexts, error = self.main_viewmodel.get_docker_contexts()
        if error:
            self.error_handler.show_error(f"Error loading Docker contexts: {error}")
            return
        
        # Get current context from the main viewmodel
        current_context = self.main_viewmodel.get_current_context()
        
        # Update context selector
        self.context_selector.set_contexts(contexts, current_context)
        
        # Set the last used context if available, but only if not called from refresh_data()
        # to avoid recursion
        if not from_refresh and hasattr(self, 'last_context') and self.last_context in contexts:
            self.change_context(self.last_context)

    def change_context(self, context_name):
        """Change the active Docker context."""        
        if not context_name:
            return
            
        # Try to set the context
        success = self.main_viewmodel.set_docker_context(context_name)
        if (success):
            self.log(f"Switched to Docker context: {context_name}")
            # Refresh data for new context, but don't refresh contexts again
            self.refresh_data(refresh_contexts=False)
        else:
            self.error_handler.show_error(f"Failed to switch to context: {context_name}")

    def setup_menu(self):
        """Set up application menu."""        
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # Settings action
        settings_action = file_menu.addAction("&Settings")
        settings_action.triggered.connect(self.show_settings)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = file_menu.addAction("E&xit")
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        # About action
        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.show_about)
    
    def show_settings(self):
        """Show the settings dialog."""        
        from app.ui.dialogs import SettingsDialog
        dialog = SettingsDialog(self)
        result = dialog.exec_()
        if result == dialog.Accepted:
            # Apply settings
            self.apply_settings()
            
    def apply_settings(self):
        """Apply changes from settings."""        
        self.settings = QSettings("LiDoMa", "DockerManager")
        
        # Apply font size
        font_size = self.settings.value("fontSize", 9, type=int)
        app_font = QApplication.font()
        app_font.setPointSize(font_size)
        QApplication.setFont(app_font)
        
        # Other settings can be applied as needed
        
    def show_about(self):
        """Show about dialog."""        
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(self, "About Docker Manager",
                         "<h1>Docker Manager</h1>"
                         "<p>Version 1.0.0</p>"
                         "<p>A lightweight Docker management UI</p>"
                         "<p>Created by LiDoMa</p>"
                         "<p><a href='https://github.com/yourusername/docker-manager'>GitHub</a></p>")
