"""
Tab view for displaying and managing Docker containers.
"""
from typing import Dict, List
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                           QPushButton, QHBoxLayout, QHeaderView, QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt, QPoint

from app.ui.viewmodels.container_viewmodel import ContainerViewModel
from app.ui.dialogs.container_details_dialog import ContainerDetailsDialog

class ContainerTabView(QWidget):
    """View for displaying and managing Docker containers."""
    
    def __init__(self, parent, viewmodel: ContainerViewModel):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.viewmodel.container_operation_completed.connect(self.on_operation_completed)
        
        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Create button bar
        button_layout = QHBoxLayout()
        
        # Start button
        self.start_button = QPushButton("Start")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_selected_container)
        button_layout.addWidget(self.start_button)
        
        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_selected_container)
        button_layout.addWidget(self.stop_button)
        
        # Delete button
        self.delete_button = QPushButton("Delete")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_selected_container)
        button_layout.addWidget(self.delete_button)
        
        # Inspect button
        self.inspect_button = QPushButton("Inspect")
        self.inspect_button.setEnabled(False)
        self.inspect_button.clicked.connect(self.inspect_selected_container)
        button_layout.addWidget(self.inspect_button)
        
        # Add spacer
        button_layout.addStretch()
        
        # Add button bar to layout
        layout.addLayout(button_layout)
        
        # Create container table
        self.container_table = QTableWidget(0, 4)
        self.container_table.setHorizontalHeaderLabels(["Name", "Image", "Status", "Ports"])
        self.container_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.container_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.container_table.setSelectionMode(QTableWidget.SingleSelection)
        self.container_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.container_table.setAlternatingRowColors(True)
        self.container_table.verticalHeader().setVisible(False)
        
        # Connect selection change signal
        self.container_table.itemSelectionChanged.connect(self.update_button_states)
        
        # Connect double click signal
        self.container_table.doubleClicked.connect(self.on_table_double_clicked)
        
        # Connect context menu
        self.container_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.container_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Add table to layout
        layout.addWidget(self.container_table)
        
    def update_button_states(self):
        """Enable/disable buttons based on selection state"""
        has_selection = len(self.container_table.selectedItems()) > 0
        self.start_button.setEnabled(has_selection)
        self.stop_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.inspect_button.setEnabled(has_selection)
        
    def add_container_row(self, container):
        """Add a container to the table."""
        row = self.container_table.rowCount()
        self.container_table.insertRow(row)
        
        # Name cell
        name_item = QTableWidgetItem(container["name"])
        name_item.setData(Qt.UserRole, container)  # Store container data
        self.container_table.setItem(row, 0, name_item)
        
        # Image cell
        image_item = QTableWidgetItem(container["image"] if "image" in container else "")
        self.container_table.setItem(row, 1, image_item)
        
        # Status cell
        status_item = QTableWidgetItem(container["status"] if "status" in container else "")
        self.container_table.setItem(row, 2, status_item)
        
        # Ports cell
        ports_text = self._format_ports(container.get("ports", {}))
        ports_item = QTableWidgetItem(ports_text)
        self.container_table.setItem(row, 3, ports_item)
        
        # Set row color based on status
        self._set_row_color(row, container.get("status", ""))
    
    def clear_table(self):
        """Clear all containers from the table."""
        self.container_table.setRowCount(0)
        
    def filter_table(self, search_text):
        """Filter the table based on search text."""
        for row in range(self.container_table.rowCount()):
            should_show = False
            for col in range(self.container_table.columnCount()):
                item = self.container_table.item(row, col)
                if item and search_text in item.text().lower():
                    should_show = True
                    break
            
            self.container_table.setRowHidden(row, not should_show)
    
    def on_operation_completed(self, success, message):
        """Handle operation completion."""
        parent = self.parent()
        
        # Log the operation result
        if hasattr(parent, 'log'):
            parent.log(message)
        
        # Show error if failed
        if not success and hasattr(parent, 'error_handler'):
            parent.error_handler.show_error(message)
    
    def show_context_menu(self, position):
        """Show context menu for container operations."""
        container_data = self.get_selected_container()
        if not container_data:
            return
            
        menu = QMenu()
        
        # Start action
        start_action = QAction("Start", self)
        start_action.triggered.connect(self.start_selected_container)
        menu.addAction(start_action)
        
        # Stop action
        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self.stop_selected_container)
        menu.addAction(stop_action)
        
        menu.addSeparator()
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected_container)
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # Inspect action
        inspect_action = QAction("Inspect", self)
        inspect_action.triggered.connect(self.inspect_selected_container)
        menu.addAction(inspect_action)
        
        # Show menu at cursor position
        menu.exec_(self.container_table.mapToGlobal(position))
    
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
        
        self.viewmodel.start_container(container_name, context)
    
    def stop_selected_container(self):
        """Stop the selected container."""
        container_data = self.get_selected_container()
        if not container_data:
            return
        
        container_name = container_data.get("name")
        context = container_data.get("context", "default")
        
        self.viewmodel.stop_container(container_name, context)
    
    def delete_selected_container(self):
        """Delete the selected container."""
        container_data = self.get_selected_container()
        if not container_data:
            return
        
        container_name = container_data.get("name")
        context = container_data.get("context", "default")
        
        # Confirm with the user
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete container '{container_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.viewmodel.remove_container(container_name, context)
    
    def inspect_selected_container(self):
        """Show detailed information about the selected container."""
        container_data = self.get_selected_container()
        if not container_data:
            return
        
        container_name = container_data.get("name")
        context = container_data.get("context", "default")
        
        # Get detailed container info
        container_details = self.viewmodel.get_container_details(container_name, context)
        
        # Show container details in a dialog
        dialog = ContainerDetailsDialog(self, container_name, container_details)
        dialog.exec_()
    
    def on_table_double_clicked(self, index):
        """Handle double click on table to show container details."""
        self.inspect_selected_container()
    
    def _format_ports(self, ports):
        """Format port mappings for display."""
        if not ports:
            return ""
            
        result = []
        for container_port, host_bindings in ports.items():
            if host_bindings:
                for binding in host_bindings:
                    host_ip = binding.get("HostIp", "0.0.0.0")
                    host_port = binding.get("HostPort", "")
                    if host_ip == "0.0.0.0":
                        result.append(f"{host_port}:{container_port}")
                    else:
                        result.append(f"{host_ip}:{host_port}:{container_port}")
            else:
                result.append(container_port)
                
        return ", ".join(result)
    
    def _set_row_color(self, row, status):
        """Set row color based on container status."""
        for col in range(self.container_table.columnCount()):
            item = self.container_table.item(row, col)
            if not item:
                continue
                
            if "running" in status.lower():
                item.setBackground(Qt.green)
            elif "exited" in status.lower() or "stopped" in status.lower():
                item.setBackground(Qt.red)
            elif "created" in status.lower():
                item.setBackground(Qt.yellow)
