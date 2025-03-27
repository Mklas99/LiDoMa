from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QPushButton, QHBoxLayout, QMenu, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from docker_utils import run_docker_command

class VolumeTab(QWidget):
    """Tab for displaying and managing Docker volumes."""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.docker_service = parent.docker_service
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create table for volumes with resizable columns
        self.volume_table = QTableWidget(0, 4)
        self.volume_table.setHorizontalHeaderLabels(["Name", "Driver", "Mountpoint", "Context"])
        
        # Make all columns resizable
        for i in range(self.volume_table.columnCount()):
            self.volume_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Set default stretch for name column
        self.volume_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Set corner button styling for consistent header appearance
        self.volume_table.setStyleSheet("""
            QTableCornerButton::section {
                background-color: #333337;
                border: 0px;
                border-right: 1px solid #3E3E42;
                border-bottom: 1px solid #3E3E42;
            }
        """)
        
        self.volume_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.volume_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.volume_table.customContextMenuRequested.connect(self.show_context_menu)
        self.volume_table.itemSelectionChanged.connect(self.update_button_states)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.delete_button = QPushButton("Delete Volume")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_selected_volume)
        self.delete_button.setEnabled(False)
        
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        
        # Add widgets to layout
        layout.addWidget(self.volume_table)
        layout.addLayout(button_layout)
    
    def update_button_states(self):
        """Enable/disable buttons based on selection state"""
        has_selection = len(self.volume_table.selectedItems()) > 0
        self.delete_button.setEnabled(has_selection)
        
    def add_volume_row(self, volume):
        """Add a volume to the table."""
        row_position = self.volume_table.rowCount()
        self.volume_table.insertRow(row_position)
        
        # Set volume data
        self.volume_table.setItem(row_position, 0, QTableWidgetItem(volume.get("name", "")))
        self.volume_table.setItem(row_position, 1, QTableWidgetItem(volume.get("driver", "")))
        self.volume_table.setItem(row_position, 2, QTableWidgetItem(volume.get("mountpoint", "")))
        self.volume_table.setItem(row_position, 3, QTableWidgetItem(volume.get("context", "default")))
        
        # Store the complete volume info in the first column item
        self.volume_table.item(row_position, 0).setData(Qt.UserRole, volume)
    
    def clear_table(self):
        """Clear all volumes from the table."""
        self.volume_table.setRowCount(0)
    
    def filter_table(self, search_text):
        """Filter the table based on search text."""
        for row in range(self.volume_table.rowCount()):
            match = False
            for col in range(self.volume_table.columnCount()):
                item = self.volume_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            
            self.volume_table.setRowHidden(row, not match)
    
    def show_context_menu(self, position):
        """Show context menu for volume operations."""
        menu = QMenu()
        delete_action = QAction("Delete Volume", self)
        delete_action.triggered.connect(self.delete_selected_volume)
        menu.addAction(delete_action)
        
        # Show the menu
        menu.exec_(QCursor.pos())
    
    def get_selected_volume(self):
        """Get the currently selected volume's data."""
        selected_rows = self.volume_table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        volume_item = self.volume_table.item(row, 0)
        if volume_item:
            return volume_item.data(Qt.UserRole)
        return None
    
    def delete_selected_volume(self):
        """Delete the selected volume."""
        volume_data = self.get_selected_volume()
        if not volume_data:
            return
        
        volume_name = volume_data.get("name")
        context = volume_data.get("context", "default")
        
        # Confirm with the user
        from PyQt5.QtWidgets import QMessageBox
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete volume '{volume_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success = self.docker_service.remove_volume(volume_name, context)
            if success:
                self.parent.log(f"Deleted volume: {volume_name}")
                # Refresh to show the updated list
                self.parent.refresh_data()
            else:
                error_msg = f"Failed to delete volume '{volume_name}'."
                self.parent.log(error_msg)
                self.parent.error_handler.show_error(error_msg)
