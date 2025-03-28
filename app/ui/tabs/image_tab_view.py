"""
Tab view for displaying and managing Docker images.
"""
from typing import Dict, List
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                           QPushButton, QHBoxLayout, QHeaderView, QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt, QPoint

from app.ui.viewmodels.image_viewmodel import ImageViewModel

class ImageTabView(QWidget):
    """View for displaying and managing Docker images."""
    
    def __init__(self, parent, viewmodel: ImageViewModel):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.viewmodel.image_operation_completed.connect(self.on_operation_completed)
        
        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Create button bar
        button_layout = QHBoxLayout()
        
        # Pull button
        self.pull_button = QPushButton("Pull")
        self.pull_button.clicked.connect(self.pull_image)
        button_layout.addWidget(self.pull_button)
        
        # Delete button
        self.delete_button = QPushButton("Delete")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_selected_image)
        button_layout.addWidget(self.delete_button)
        
        # Add spacer
        button_layout.addStretch()
        
        # Add button bar to layout
        layout.addLayout(button_layout)
        
        # Create image table
        self.image_table = QTableWidget(0, 4)
        self.image_table.setHorizontalHeaderLabels(["Repository", "Tag", "ID", "Size"])
        self.image_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.image_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.image_table.setSelectionMode(QTableWidget.SingleSelection)
        self.image_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.image_table.setAlternatingRowColors(True)
        self.image_table.verticalHeader().setVisible(False)
        
        # Connect selection change signal
        self.image_table.itemSelectionChanged.connect(self.update_button_states)
        
        # Connect context menu
        self.image_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Add table to layout
        layout.addWidget(self.image_table)
        
    def update_button_states(self):
        """Enable/disable buttons based on selection state"""
        has_selection = len(self.image_table.selectedItems()) > 0
        self.delete_button.setEnabled(has_selection)
    
    def add_image_row(self, image):
        """Add an image to the table."""
        row = self.image_table.rowCount()
        self.image_table.insertRow(row)
        
        # Parse repo and tag
        name = image.get("name", "")
        tags = image.get("tags", [])
        tag = tags[0] if tags else "latest"
        
        # Repository cell
        repo_item = QTableWidgetItem(name)
        repo_item.setData(Qt.UserRole, image)  # Store image data
        self.image_table.setItem(row, 0, repo_item)
        
        # Tag cell
        tag_item = QTableWidgetItem(tag)
        self.image_table.setItem(row, 1, tag_item)
        
        # ID cell (shortened)
        id_val = image.get("id", "")
        id_short = id_val[:12] if id_val else ""
        id_item = QTableWidgetItem(id_short)
        self.image_table.setItem(row, 2, id_item)
        
        # Size cell (formatted)
        size = image.get("size", 0)
        size_str = self._format_size(size)
        size_item = QTableWidgetItem(size_str)
        self.image_table.setItem(row, 3, size_item)
    
    def clear_table(self):
        """Clear all images from the table."""
        self.image_table.setRowCount(0)
        
    def filter_table(self, search_text):
        """Filter the table based on search text."""
        for row in range(self.image_table.rowCount()):
            should_show = False
            for col in range(self.image_table.columnCount()):
                item = self.image_table.item(row, col)
                if item and search_text in item.text().lower():
                    should_show = True
                    break
            
            self.image_table.setRowHidden(row, not should_show)
    
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
        """Show context menu for image operations."""
        image_data = self.get_selected_image()
        if not image_data:
            return
            
        menu = QMenu()
        
        # Delete action
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected_image)
        menu.addAction(delete_action)
        
        # Show menu at cursor position
        menu.exec_(self.image_table.mapToGlobal(position))
    
    def get_selected_image(self):
        """Get the currently selected image's data."""
        selected_rows = self.image_table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        image_item = self.image_table.item(row, 0)
        if image_item:
            return image_item.data(Qt.UserRole)
        return None
    
    def delete_selected_image(self):
        """Delete the selected image."""
        image_data = self.get_selected_image()
        if not image_data:
            return
        
        image_id = image_data.get("id")
        image_name = image_data.get("name")
        context = image_data.get("context", "default")
        
        if not image_id:
            return
        
        # Confirm with the user
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete image '{image_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.viewmodel.remove_image(image_id, context)
    
    def pull_image(self):
        """Pull an image from registry."""
        from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QDialogButtonBox, QFormLayout
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Pull Image")
        dialog.setMinimumWidth(400)
        
        layout = QFormLayout(dialog)
        
        # Image name input
        name_input = QLineEdit()
        layout.addRow("Image Name:", name_input)
        
        # Tag input
        tag_input = QLineEdit()
        tag_input.setText("latest")
        layout.addRow("Tag:", tag_input)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        # Show dialog
        if dialog.exec_() == QDialog.Accepted:
            image_name = name_input.text().strip()
            tag = tag_input.text().strip() or "latest"
            
            if image_name:
                self.viewmodel.pull_image(image_name, tag)
    
    def _format_size(self, size_bytes):
        """Format size in bytes to human-readable format."""
        if not isinstance(size_bytes, (int, float)):
            return "Unknown"
            
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
            
        return f"{size_bytes:.2f} PB"
