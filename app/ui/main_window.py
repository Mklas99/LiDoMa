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

# Import our custom log handler
from app.ui.components.log_handler import QtLogHandler

# Add this import at the top of the file
from app.ui.theme_manager import ThemeManager

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
        
        # Connect the previously unused signals
        self.main_viewmodel.refresh_started.connect(self.on_refresh_started)
        self.main_viewmodel.refresh_completed.connect(self.handle_refresh_completed)
        
        # Initialize thread tracking
        self.refresh_worker = None
        self.active_workers = []
        
        # Initialize UI
        self.init_ui()
        self.setup_shortcuts()
        self.setup_menu()
        
        # Ensure theme is applied to all components
        ThemeManager.refresh_widget_style(self)
        
        # Configure custom log handler to forward log messages to UI
        self.log_handler = QtLogHandler()
        self.log_handler.log_message.connect(self.append_to_log)
        self.log_handler.setLevel(logging.INFO)
        
        # Add handler to root logger to capture all app logs
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
        
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
        
        # Properly shutdown the logging handler before the Qt object is destroyed
        if hasattr(self, 'log_handler'):
            self.log_handler.shutdown()
            
        # Remove our custom log handler before closing (this is now redundant but kept for safety)
        root_logger = logging.getLogger()
        if hasattr(self, 'log_handler') and self.log_handler in root_logger.handlers:
            root_logger.removeHandler(self.log_handler)
        
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
        """Log a message through the logging system."""        
        logger.info(message)
        
        # Update status bar with last action (we still do this directly)
        self.status_label.setText(message.split('\n')[0])
    
    def append_to_log(self, formatted_message):
        """Append a pre-formatted log message to the log widget."""        
        self.log_widget.append(formatted_message)

    def refresh_data(self, refresh_contexts=True):
        """Starts the worker thread to refresh all Docker resource data."""
        # Update UI state first
        self.header_widget.disable_refresh()
        self.error_handler.clear_error()
        
        # Clear tables 
        self.container_tab.clear_table()
        self.image_tab.clear_table()
        self.volume_tab.clear_table()
        self.network_tab.clear_table()
        
        # Always refresh contexts first to ensure we have the latest Docker environments
        self.log("Refreshing Docker contexts...")
        
        # Force a refresh of the Docker contexts cache
        if hasattr(self.main_viewmodel, 'invalidate_contexts_cache'):
            self.main_viewmodel.invalidate_contexts_cache()
        
        # Get updated contexts
        contexts, error = self.main_viewmodel.get_docker_contexts()
        if error:
            self.error_handler.show_error(f"Error refreshing Docker contexts: {error}")
        else:
            # Update context selector
            current_context = self.context_selector.get_current_context()
            self.context_selector.set_contexts(contexts, current_context)
            self.log(f"Found {len(contexts)} Docker contexts")
        
        # Now refresh the selected context's resources
        current_context = self.context_selector.get_current_context()
        
        # Log refresh operation
        if current_context == "All":
            self.log("Refreshing Docker data across all contexts...")
        else:
            self.log(f"Refreshing Docker data for context: {current_context}...")
            
        self.status_label.setText("Refreshing resources...")
        
        # Perform refresh through viewmodel
        try:
            self.main_viewmodel.refresh_all_resources()
            return
        except Exception as e:
            # Fall back to the original refresh logic
            self.logger.error(f"Error using viewmodel refresh: {str(e)}")
            
            # Cancel any existing refresh operation
            if self.refresh_worker and self.refresh_worker.is_running:
                self.refresh_worker.terminate()
                self.refresh_worker.wait()
            
            # Create and start worker thread
            try:
                self.refresh_worker = RefreshWorker(self.docker_service)
                self.refresh_worker.results_ready.connect(self.on_refresh_complete)
                self.refresh_worker.signals.error.connect(self.on_refresh_error)
                self.refresh_worker.signals.log.connect(self.log)
                self.refresh_worker.start()
                self.active_workers.append(self.refresh_worker)
            except Exception as e:
                error_msg = f"Failed to start refresh worker: {str(e)}"
                self.logger.error(error_msg)
                self.logger.error(traceback.format_exc())
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
                # Add detailed status text with context info
                current_context = self.context_selector.get_current_context() 
                context_info = f" in context '{current_context}'" if current_context != "All" else " across all contexts"
                
                status_msg = f"Found {len(containers)} containers, {len(images)} images, " + \
                             f"{len(volumes)} volumes, {len(networks)} networks{context_info}"
                
                self.status_label.setText(status_msg)
                
                # Log the counts
                self.log(status_msg)
            
                # Update resource tables
                for container in containers:
                    # Make sure container has a context field
                    if "context" not in container:
                        container["context"] = "default"
                    self.container_tab.add_container_row(container)
                    
                for image in images:
                    # Make sure image has a context field
                    if "context" not in image:
                        image["context"] = "default"
                    self.image_tab.add_image_row(image)
                    
                for volume in volumes:
                    # Make sure volume has a context field
                    if "context" not in volume:
                        volume["context"] = "default"
                    self.volume_tab.add_volume_row(volume)
                    
                for network in networks:
                    # Make sure network has a context field
                    if "context" not in network:
                        network["context"] = "default"
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
        # Only refresh the cache if not called from refresh_data to avoid redundant calls
        if not from_refresh and hasattr(self.main_viewmodel, 'invalidate_contexts_cache'):
            self.main_viewmodel.invalidate_contexts_cache()
        
        # Get updated contexts
        contexts, error = self.main_viewmodel.get_docker_contexts()
        
        if error:
            self.error_handler.show_error(f"Error loading Docker contexts: {error}")
            return
        
        # Get current context from the main viewmodel or use the current selection
        current_context = self.context_selector.get_current_context() or self.main_viewmodel.get_current_context()
        
        # Always ensure "All" is in the list of contexts
        if "All" not in contexts:
            contexts.insert(0, "All")
        
        # Log the available contexts
        self.log(f"Available Docker contexts: {', '.join([c for c in contexts if c != 'All'])}")
        
        # Update context selector - maintain current selection if possible
        self.context_selector.set_contexts(contexts, current_context)
        
        # Only change context if needed and not called during a refresh operation
        if not from_refresh and hasattr(self, 'last_context') and self.last_context in contexts:
            # Use direct call to avoid triggering a refresh again
            QTimer.singleShot(100, lambda: self.change_context(self.last_context))
        elif not from_refresh and current_context != self.context_selector.get_current_context():
            # If context changed, update it
            QTimer.singleShot(100, lambda: self.change_context(current_context))

    def change_context(self, context_name):
        """Change the active Docker context."""        
        if not context_name:
            return
        
        # Handle "All" context separately
        if context_name == "All":
            self.log("Viewing all Docker contexts")
            self.refresh_data(refresh_contexts=False)
            return
            
        # Try to set the context
        success = self.main_viewmodel.set_docker_context(context_name)
        
        # The success check should now work properly with our updated DockerContextServiceImpl
        if success:
            self.log(f"Switched to Docker context: {context_name}")
            # Refresh data for new context, but don't refresh contexts again
            self.refresh_data(refresh_contexts=False)
        else:
            self.error_handler.show_error(f"Failed to switch to context: {context_name}")
            # Refresh the context selector to reset to the current context
            self.load_contexts()

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
        
        # Apply theme
        current_theme = self.settings.value("theme", "Dark")
        ThemeManager.apply_theme(current_theme)
        
        # Apply theme to main window explicitly
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        
        # Apply font size
        font_size = self.settings.value("fontSize", 9, type=int)
        app_font = QApplication.font()
        app_font.setPointSize(font_size)
        QApplication.setFont(app_font)
        
        # Force update on all widgets
        for widget in QApplication.allWidgets():
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()
            
    def show_about(self):
        """Show about dialog."""        
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(self, "About Docker Manager",
                         "<h1>Docker Manager</h1>"
                         "<p>Version 1.0.0</p>"
                         "<p>A lightweight Docker management UI</p>"
                         "<p>Created by LiDoMa</p>"
                         "<p><a href='https://github.com/yourusername/docker-manager'>GitHub</a></p>")

    def on_refresh_started(self):
        """Handle refresh started signal from the viewmodel."""        
        self.header_widget.disable_refresh()
        self.error_handler.clear_error()
        self.log("Refresh operation started...")
        self.status_label.setText("Refreshing Docker resources...")
        
        # Clear tables
        self.container_tab.clear_table()
        self.image_tab.clear_table()
        self.volume_tab.clear_table()
        self.network_tab.clear_table()
    
    def handle_refresh_completed(self, containers, images, volumes, networks, error):
        """Handle refresh completed signal from the viewmodel."""        
        self.on_refresh_complete(containers, images, volumes, networks, error)
