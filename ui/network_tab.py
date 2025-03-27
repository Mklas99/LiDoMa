from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QPushButton, QHBoxLayout, QMenu, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

class NetworkTab(QWidget):
    """Tab for displaying and managing Docker networks."""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.docker_service = parent.docker_service
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create table for networks with resizable columns
        self.network_table = QTableWidget(0, 5)
        self.network_table.setHorizontalHeaderLabels(["Name", "ID", "Driver", "Scope", "Context"])
        
        # Make all columns resizable
        for i in range(self.network_table.columnCount()):
            self.network_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Set default stretch for name column
        self.network_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Set corner button styling for consistent header appearance
        self.network_table.setStyleSheet("""
            QTableCornerButton::section {
                background-color: #333337;
                border: 0px;
                border-right: 1px solid #3E3E42;
                border-bottom: 1px solid #3E3E42;
            }
        """)
        
        self.network_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.network_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.network_table.customContextMenuRequested.connect(self.show_context_menu)
        self.network_table.itemSelectionChanged.connect(self.update_button_states)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.delete_button = QPushButton("Delete Network")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(self.delete_selected_network)
        self.delete_button.setEnabled(False)
        
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
    
    def delete_selected_network(self):
        """Delete the selected network."""
        network_data = self.get_selected_network()
        if not network_data:
            return
        
        network_name = network_data.get("name")
        context = network_data.get("context", "default")
        
        # Confirm with the user
        from PyQt5.QtWidgets import QMessageBox
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete network '{network_name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            success = self.docker_service.remove_network(network_name, context)
            if success:
                self.parent.log(f"Deleted network: {network_name}")
                # Refresh to show the updated list
                self.parent.refresh_data()
            else:
                error_msg = f"Failed to delete network '{network_name}'."
                self.parent.log(error_msg)
                self.parent.error_handler.show_error(error_msg)
