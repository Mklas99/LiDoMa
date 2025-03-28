from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QPushButton, QHBoxLayout, QMenu, QAction, 
                           QMessageBox, QInputDialog, QLineEdit, QDialog, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from app.ui.viewmodels.volume_viewmodel import VolumeViewModel

class CreateVolumeDialog(QDialog):
    """Dialog for creating a new volume."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Volume")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        form.addRow("Name:", self.name_edit)
        
        self.driver_edit = QLineEdit()
        self.driver_edit.setText("local")
        form.addRow("Driver:", self.driver_edit)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def get_volume_data(self):
        """Get the volume data from the form."""
        return {
            "name": self.name_edit.text(),
            "driver": self.driver_edit.text()
        }

class VolumeTabView(QWidget):
    """View for displaying and managing Docker volumes."""
    
    def __init__(self, parent, viewmodel: VolumeViewModel):
        super().__init__()
        self.parent = parent
        self.viewmodel = viewmodel
        
        # Connect viewmodel signals
        self.viewmodel.volume_operation_completed.connect(self.on_operation_completed)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create volume table
        self.volume_table = QTableWidget(0, 4)
        self.volume_table.setHorizontalHeaderLabels(["Name", "Driver", "Mountpoint", "Context"])
        
        # Make columns resizable
        for i in range(self.volume_table.columnCount()):
            self.volume_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Make name column stretch by default
        self.volume_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.volume_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Style corner button
        self.volume_table.setStyleSheet("""
            QTableCornerButton::section {
                background-color: #333337;
                border: 0px;
                border-right: 1px solid #3E3E42;
                border-bottom: 1px solid #3E3E42;
            }
        """)
        
        # Set table behaviors
        self.volume_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.volume_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.volume_table.customContextMenuRequested.connect(self.show_context_menu)
        self.volume_table.itemSelectionChanged.connect(self.update_button_states)
        
        # Create action buttons
        button_layout = QHBoxLayout()
        
        self.create_button = QPushButton("Create Volume")
        self.create_button.clicked.connect(self.create_volume)
        
        self.delete_button = QPushButton("Delete Volume")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_selected_volume)
        self.delete_button.setEnabled(False)
        
        button_layout.addWidget(self.create_button)
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
        self.volume_table.setItem(row_position, 1, QTableWidgetItem(volume.get("driver", "local")))
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
    
    def on_operation_completed(self, success, message):
        """Handle operation completion."""
        self.parent.log(message)
        if not success:
            self.parent.error_handler.show_error(message)
        self.parent.refresh_data()
    
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
    
    def create_volume(self):
        """Create a new volume."""
        dialog = CreateVolumeDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            volume_data = dialog.get_volume_data()
            if volume_data["name"]:
                self.viewmodel.create_volume(
                    volume_data["name"],
                    volume_data["driver"],
                    "default"
                )
            else:
                self.parent.error_handler.show_error("Volume name cannot be empty")
    
    def delete_selected_volume(self):
        """Delete the selected volume."""
        volume_data = self.get_selected_volume()
        if not volume_data:
            return
        
        volume_name = volume_data.get("name")
        context = volume_data.get("context", "default")
        
        # Confirm with the user
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete volume '{volume_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.viewmodel.remove_volume(volume_name, context)
