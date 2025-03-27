from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QPushButton, QHBoxLayout, QMenu, QAction,
                            QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from ui.create_container_dialog import CreateContainerDialog

class ImageTab(QWidget):
    """Tab for displaying and managing Docker images."""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.docker_service = parent.docker_service
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create table for images with resizable columns
        self.image_table = QTableWidget(0, 5)
        self.image_table.setHorizontalHeaderLabels(["ID", "Name", "Size", "Created", "Context"])
        
        # Make all columns resizable
        for i in range(self.image_table.columnCount()):
            self.image_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Set default stretch for name column
        self.image_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Set corner button styling for consistent header appearance
        self.image_table.setStyleSheet("""
            QTableCornerButton::section {
                background-color: #333337;
                border: 0px;
                border-right: 1px solid #3E3E42;
                border-bottom: 1px solid #3E3E42;
            }
        """)
        
        self.image_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.image_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.image_table.customContextMenuRequested.connect(self.show_context_menu)
        self.image_table.itemSelectionChanged.connect(self.update_button_states)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.create_container_button = QPushButton("Create Container")
        self.create_container_button.clicked.connect(self.create_container_from_selected)
        self.create_container_button.setEnabled(False)
        
        self.delete_button = QPushButton("Delete Image")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_selected_image)
        self.delete_button.setEnabled(False)
        
        button_layout.addWidget(self.create_container_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        
        # Add widgets to layout
        layout.addWidget(self.image_table)
        layout.addLayout(button_layout)
    
    def update_button_states(self):
        """Enable/disable buttons based on selection state"""
        has_selection = len(self.image_table.selectedItems()) > 0
        self.create_container_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        
    def add_image_row(self, image):
        """Add an image to the table."""
        row_position = self.image_table.rowCount()
        self.image_table.insertRow(row_position)
        
        # Set image data
        self.image_table.setItem(row_position, 0, QTableWidgetItem(image.get("id", "")))
        
        # For name, use the first tag or default
        name = image.get("name", "<none>:<none>")
        self.image_table.setItem(row_position, 1, QTableWidgetItem(name))
        
        # Format size
        size = image.get("size", "")
        if isinstance(size, int):
            # Convert bytes to human-readable format
            if size > 1_000_000_000:  # GB
                size_str = f"{size / 1_000_000_000:.2f} GB"
            elif size > 1_000_000:  # MB
                size_str = f"{size / 1_000_000:.2f} MB"
            elif size > 1_000:  # KB
                size_str = f"{size / 1_000:.2f} KB"
            else:
                size_str = f"{size} B"
        else:
            size_str = str(size)
            
        self.image_table.setItem(row_position, 2, QTableWidgetItem(size_str))
        
        # Format created date
        import datetime
        created = image.get("created", "")
        created_str = ""
        if created:
            try:
                # Try to parse as ISO format
                dt = datetime.datetime.fromisoformat(created.replace('Z', '+00:00'))
                created_str = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, TypeError):
                created_str = str(created)
        
        self.image_table.setItem(row_position, 3, QTableWidgetItem(created_str))
        self.image_table.setItem(row_position, 4, QTableWidgetItem(image.get("context", "default")))
        
        # Store the complete image info in the first column item
        self.image_table.item(row_position, 0).setData(Qt.UserRole, image)
    
    def clear_table(self):
        """Clear all images from the table."""
        self.image_table.setRowCount(0)
    
    def filter_table(self, search_text):
        """Filter the table based on search text."""
        for row in range(self.image_table.rowCount()):
            match = False
            for col in range(self.image_table.columnCount()):
                item = self.image_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            
            self.image_table.setRowHidden(row, not match)
    
    def show_context_menu(self, position):
        """Show context menu for image operations."""
        menu = QMenu()
        create_container_action = QAction("Create Container", self)
        create_container_action.triggered.connect(self.create_container_from_selected)
        
        delete_action = QAction("Delete Image", self)
        delete_action.triggered.connect(self.delete_selected_image)
        
        menu.addAction(create_container_action)
        menu.addAction(delete_action)
        
        # Show the menu
        menu.exec_(QCursor.pos())
    
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
    
    def create_container_from_selected(self):
        """Create a container from the selected image."""
        image_data = self.get_selected_image()
        if not image_data:
            return
        
        image_id = image_data.get("id")
        image_name = image_data.get("name")
        context = image_data.get("context", "default")
        
        # Get container name from user
        container_name, ok = QInputDialog.getText(
            self,
            "Create Container",
            "Enter container name (leave empty for auto-generated name):"
        )
        
        if ok:
            container_name = container_name.strip() if container_name.strip() else None
            success = self.docker_service.create_container(image_name, container_name, context)
            if success:
                self.parent.log(f"Created container from image: {image_name}")
                # Refresh to show the new container
                self.parent.refresh_data()
            else:
                error_msg = f"Failed to create container from image '{image_name}'."
                self.parent.log(error_msg)
                self.parent.error_handler.show_error(error_msg)
    
    def delete_selected_image(self):
        """Delete the selected image."""
        image_data = self.get_selected_image()
        if not image_data:
            return
        
        image_id = image_data.get("id")
        image_name = image_data.get("name")
        context = image_data.get("context", "default")
        
        # Confirm with the user
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete image '{image_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success = self.docker_service.remove_image(image_id, context)
            if success:
                self.parent.log(f"Deleted image: {image_name}")
                # Refresh to show the updated list
                self.parent.refresh_data()
            else:
                error_msg = f"Failed to delete image '{image_name}'."
                self.parent.log(error_msg)
                self.parent.error_handler.show_error(error_msg)
