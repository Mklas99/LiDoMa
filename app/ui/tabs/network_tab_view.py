from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                           QHeaderView, QPushButton, QHBoxLayout, QMenu, QAction, 
                           QMessageBox, QInputDialog, QLineEdit, QDialog, QFormLayout, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from app.ui.viewmodels.network_viewmodel import NetworkViewModel

class CreateNetworkDialog(QDialog):
    """Dialog for creating a new network."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Network")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        form.addRow("Name:", self.name_edit)
        
        self.driver_combo = QComboBox()
        self.driver_combo.addItems(["bridge", "host", "none", "overlay", "macvlan", "ipvlan"])
        form.addRow("Driver:", self.driver_combo)
        
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
        
    def get_network_data(self):
        """Get the network data from the form."""
        return {
            "name": self.name_edit.text(),
            "driver": self.driver_combo.currentText()
        }

class NetworkTabView(QWidget):
    """View for displaying and managing Docker networks."""
    
    def __init__(self, parent, viewmodel: NetworkViewModel):
        super().__init__()
        self.parent = parent
        self.viewmodel = viewmodel
        
        # Connect viewmodel signals
        self.viewmodel.network_operation_completed.connect(self.on_operation_completed)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create network table
        self.network_table = QTableWidget(0, 5)
        self.network_table.setHorizontalHeaderLabels(["Name", "ID", "Driver", "Scope", "Context"])
        
        # Make columns resizable
        for i in range(self.network_table.columnCount()):
            self.network_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Make name column stretch by default
        self.network_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Style corner button
        self.network_table.setStyleSheet("""
            QTableCornerButton::section {
                background-color: #333337;
                border: 0px;
                border-right: 1px solid #3E3E42;
                border-bottom: 1px solid #3E3E42;
            }
        """)
        
        # Set table behaviors
        self.network_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.network_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.network_table.customContextMenuRequested.connect(self.show_context_menu)
        self.network_table.itemSelectionChanged.connect(self.update_button_states)
        
        # Create action buttons
        button_layout = QHBoxLayout()
        
        self.create_button = QPushButton("Create Network")
        self.create_button.clicked.connect(self.create_network)
        
        self.delete_button = QPushButton("Delete Network")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_selected_network)
        self.delete_button.setEnabled(False)
        
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        
        # Add widgets to layout
        layout.addWidget(self.network_table)
        layout.addLayout(button_layout)
    
    def update_button_states(self):
        """Enable/disable buttons based on selection state"""
        has_selection = len(self.network_table.selectedItems()) > 0
        self.delete_button.setEnabled(has_selection)
        
    def add_network_row(self, network):
        """Add a network to the table."""
        row_position = self.network_table.rowCount()
        self.network_table.insertRow(row_position)
        
        # Set network data
        self.network_table.setItem(row_position, 0, QTableWidgetItem(network.get("name", "")))
        self.network_table.setItem(row_position, 1, QTableWidgetItem(network.get("id", "")))
        self.network_table.setItem(row_position, 2, QTableWidgetItem(network.get("driver", "")))
        self.network_table.setItem(row_position, 3, QTableWidgetItem(network.get("scope", "")))
        self.network_table.setItem(row_position, 4, QTableWidgetItem(network.get("context", "default")))
        
        # Store the complete network info in the first column item
        self.network_table.item(row_position, 0).setData(Qt.UserRole, network)
    
    def clear_table(self):
        """Clear all networks from the table."""
        self.network_table.setRowCount(0)
    
    def filter_table(self, search_text):
        """Filter the table based on search text."""
        for row in range(self.network_table.rowCount()):
            match = False
            for col in range(self.network_table.columnCount()):
                item = self.network_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            
            self.network_table.setRowHidden(row, not match)
    
    def on_operation_completed(self, success, message):
        """Handle operation completion."""
        self.parent.log(message)
        if not success:
            self.parent.error_handler.show_error(message)
        self.parent.refresh_data()
    
    def show_context_menu(self, position):
        """Show context menu for network operations."""
        menu = QMenu()
        delete_action = QAction("Delete Network", self)
        delete_action.triggered.connect(self.delete_selected_network)
        
        menu.addAction(delete_action)
        
        # Show the menu
        menu.exec_(QCursor.pos())
    
    def get_selected_network(self):
        """Get the currently selected network's data."""
        selected_rows = self.network_table.selectedItems()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        network_item = self.network_table.item(row, 0)
        if network_item:
            return network_item.data(Qt.UserRole)
        return None
    
    def create_network(self):
        """Create a new network."""
        dialog = CreateNetworkDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            network_data = dialog.get_network_data()
            if network_data["name"]:
                self.viewmodel.create_network(
                    network_data["name"],
                    network_data["driver"],
                    "default"
                )
            else:
                self.parent.error_handler.show_error("Network name cannot be empty")
    
    def delete_selected_network(self):
        """Delete the selected network."""
        network_data = self.get_selected_network()
        if not network_data:
            return
        
        network_name = network_data.get("name")
        context = network_data.get("context", "default")
        
        # Confirm with the user
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete network '{network_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.viewmodel.remove_network(network_name, context)
