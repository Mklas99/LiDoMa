from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QPushButton, QHBoxLayout, QMenu, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QColor, QBrush
from ui.container_details_dialog import ContainerDetailsDialog

class ContainerTab(QWidget):
    """Tab for displaying and managing Docker containers."""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.docker_service = parent.docker_service
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create table for containers with resizable columns
        self.container_table = QTableWidget(0, 4)
        self.container_table.setHorizontalHeaderLabels(["Name", "Status", "Ports", "Context"])
        
        # Make all columns resizable
        for i in range(self.container_table.columnCount()):
            self.container_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Make name column stretch by default
        self.container_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Set corner button styling for consistent header appearance
        self.container_table.setStyleSheet("""
            QTableCornerButton::section {
                background-color: #333337;
                border: 0px;
                border-right: 1px solid #3E3E42;
                border-bottom: 1px solid #3E3E42;
            }
        """)
        
        self.container_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.container_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.container_table.customContextMenuRequested.connect(self.show_context_menu)
        self.container_table.itemSelectionChanged.connect(self.update_button_states)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_selected_container)
        self.start_button.setEnabled(False)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.clicked.connect(self.stop_selected_container)
        self.stop_button.setEnabled(False)
        
        self.details_button = QPushButton("Show Details")
        self.details_button.clicked.connect(self.inspect_selected_container)
        self.details_button.setEnabled(False)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_selected_container)
        self.delete_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.details_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        
        # Add widgets to layout
        layout.addWidget(self.container_table)
        layout.addLayout(button_layout)
    
    def update_button_states(self):
        """Enable/disable buttons based on selection state"""
        has_selection = len(self.container_table.selectedItems()) > 0
        self.start_button.setEnabled(has_selection)
        self.stop_button.setEnabled(has_selection)
        self.details_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        
    def add_container_row(self, container):
        """Add a container to the table."""
        row_position = self.container_table.rowCount()
        self.container_table.insertRow(row_position)
        
        # Set container data
        self.container_table.setItem(row_position, 0, QTableWidgetItem(container.get("name", "")))
        
        # Set status with color coding
        status_text = container.get("status", "")
        status_item = QTableWidgetItem(status_text)
        
        # Color based on status
        if "running" in status_text.lower():
            status_item.setForeground(QBrush(QColor("#2ECC71")))  # Green for running
        elif "exited" in status_text.lower() or "stopped" in status_text.lower():
            status_item.setForeground(QBrush(QColor("#E74C3C")))  # Red for stopped/exited
        elif "created" in status_text.lower():
            status_item.setForeground(QBrush(QColor("#F39C12")))  # Orange for created
        elif "paused" in status_text.lower():
            status_item.setForeground(QBrush(QColor("#3498DB")))  # Blue for paused
            
        self.container_table.setItem(row_position, 1, status_item)
        
        # Format ports
        ports_text = ""
        ports_dict = container.get("ports", {})
        for container_port, host_bindings in ports_dict.items():
            if host_bindings:
                for binding in host_bindings:
                    host_ip = binding.get("HostIp", "")
                    host_port = binding.get("HostPort", "")
                    ports_text += f"{host_ip}:{host_port}->{container_port}, "
            else:
                ports_text += f"{container_port}, "
        ports_text = ports_text.rstrip(", ")
        
        self.container_table.setItem(row_position, 2, QTableWidgetItem(ports_text))
        self.container_table.setItem(row_position, 3, QTableWidgetItem(container.get("context", "default")))
        
        # Store the complete container info in the first column item
        self.container_table.item(row_position, 0).setData(Qt.UserRole, container)
    
    def clear_table(self):
        """Clear all containers from the table."""
        self.container_table.setRowCount(0)
    
    def filter_table(self, search_text):
        """Filter the table based on search text."""
        for row in range(self.container_table.rowCount()):
            match = False
            for col in range(self.container_table.columnCount()):
                item = self.container_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            
            self.container_table.setRowHidden(row, not match)
    
    def show_context_menu(self, position):
        """Show context menu for container operations."""
        menu = QMenu()
        start_action = QAction("Start", self)
        start_action.triggered.connect(self.start_selected_container)
        
        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self.stop_selected_container)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected_container)
        
        inspect_action = QAction("Inspect", self)
        inspect_action.triggered.connect(self.inspect_selected_container)
        
        menu.addAction(start_action)
        menu.addAction(stop_action)
        menu.addAction(delete_action)
        menu.addSeparator()
        menu.addAction(inspect_action)
        
        # Show the menu
        menu.exec_(QCursor.pos())
    
    def get_selected_container(self):
        """Get the currently selected container's data."""
        selected_rows = self.container_table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        container_item = self.container_table.item(row, 0)
        if container_item:
            return container_item.data(Qt.UserRole)
        return None
    
    def start_selected_container(self):
        """Start the selected container."""
        container_data = self.get_selected_container()
        if not container_data:
            return
        
        container_name = container_data.get("name")
        context = container_data.get("context", "default")
        
        success = self.docker_service.start_container(container_name, context)
        if success:
            self.parent.log(f"Started container: {container_name}")
            # Refresh to show the updated status
            self.parent.refresh_data()
        else:
            error_msg = f"Failed to start container '{container_name}'."
            self.parent.log(error_msg)
            self.parent.error_handler.show_error(error_msg)
    
    def stop_selected_container(self):
        """Stop the selected container."""
        container_data = self.get_selected_container()
        if not container_data:
            return
        
        container_name = container_data.get("name")
        context = container_data.get("context", "default")
        
        success = self.docker_service.stop_container(container_name, context)
        if success:
            self.parent.log(f"Stopped container: {container_name}")
            # Refresh to show the updated status
            self.parent.refresh_data()
        else:
            error_msg = f"Failed to stop container '{container_name}'."
            self.parent.log(error_msg)
            self.parent.error_handler.show_error(error_msg)
    
    def delete_selected_container(self):
        """Delete the selected container."""
        container_data = self.get_selected_container()
        if not container_data:
            return
        
        container_name = container_data.get("name")
        context = container_data.get("context", "default")
        
        # Confirm with the user
        from PyQt5.QtWidgets import QMessageBox
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete container '{container_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success = self.docker_service.remove_container(container_name, context)
            if success:
                self.parent.log(f"Deleted container: {container_name}")
                # Refresh to show the updated list
                self.parent.refresh_data()
            else:
                error_msg = f"Failed to delete container '{container_name}'."
                self.parent.log(error_msg)
                self.parent.error_handler.show_error(error_msg)
    
    def inspect_selected_container(self):
        """Show detailed information about the selected container."""
        container_data = self.get_selected_container()
        if not container_data:
            return
        
        container_name = container_data.get("name")
        context = container_data.get("context", "default")
        
        # Get detailed container info
        container_info = self.docker_service.inspect_container(container_name, context)
        
        # Show container details in a dialog
        dialog = ContainerDetailsDialog(self, container_name, container_info)
        dialog.exec_()
