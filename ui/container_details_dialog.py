from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QTextEdit, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import json

class ContainerDetailsDialog(QDialog):
    """Dialog for displaying detailed container information."""
    
    def __init__(self, parent, container_name, container_info):
        super().__init__(parent)
        self.container_name = container_name
        self.container_info = container_info
        self.setWindowTitle(f"Container Details: {container_name}")
        self.resize(700, 500)
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create tab widget for organizing details
        tab_widget = QTabWidget()
        
        # Overview tab
        overview_widget = self.create_overview_tab()
        tab_widget.addTab(overview_widget, "Overview")
        
        # Environment variables tab
        env_widget = self.create_env_tab()
        tab_widget.addTab(env_widget, "Environment")
        
        # Mounts tab
        mounts_widget = self.create_mounts_tab()
        tab_widget.addTab(mounts_widget, "Mounts")
        
        # Networks tab
        networks_widget = self.create_networks_tab()
        tab_widget.addTab(networks_widget, "Networks")
        
        # JSON tab (raw data)
        json_widget = self.create_json_tab()
        tab_widget.addTab(json_widget, "JSON")
        
        layout.addWidget(tab_widget)
    
    def create_overview_tab(self):
        """Create the overview tab with basic container info."""
        widget = QTextEdit()
        widget.setReadOnly(True)
        
        # Extract relevant information
        state = self.container_info.get("State", {})
        config = self.container_info.get("Config", {})
        network = self.container_info.get("NetworkSettings", {})
        host_config = self.container_info.get("HostConfig", {})
        
        overview_html = f"""
        <h2>{self.container_name}</h2>
        <table>
            <tr><td><b>ID:</b></td><td>{self.container_info.get('Id', 'N/A')}</td></tr>
            <tr><td><b>Created:</b></td><td>{self.container_info.get('Created', 'N/A')}</td></tr>
            <tr><td><b>Image:</b></td><td>{config.get('Image', 'N/A')}</td></tr>
            <tr><td><b>Status:</b></td><td>{state.get('Status', 'N/A')}</td></tr>
            <tr><td><b>Running:</b></td><td>{state.get('Running', False)}</td></tr>
            <tr><td><b>Restart Policy:</b></td><td>{host_config.get('RestartPolicy', {}).get('Name', 'N/A')}</td></tr>
            <tr><td><b>IP Address:</b></td><td>{network.get('IPAddress', 'N/A')}</td></tr>
        </table>
        
        <h3>Ports</h3>
        """
        
        # Add port mappings
        ports = network.get("Ports", {})
        if ports:
            overview_html += "<table><tr><th>Container Port</th><th>Host Bindings</th></tr>"
            for container_port, bindings in ports.items():
                if bindings:
                    for binding in bindings:
                        host_ip = binding.get("HostIp", "")
                        host_port = binding.get("HostPort", "")
                        overview_html += f"<tr><td>{container_port}</td><td>{host_ip}:{host_port}</td></tr>"
                else:
                    overview_html += f"<tr><td>{container_port}</td><td>Not published</td></tr>"
            overview_html += "</table>"
        else:
            overview_html += "<p>No port mappings found.</p>"
        
        widget.setHtml(overview_html)
        return widget
    
    def create_env_tab(self):
        """Create tab showing environment variables."""
        widget = QTableWidget(0, 2)
        widget.setHorizontalHeaderLabels(["Variable", "Value"])
        widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Get environment variables
        env_vars = self.container_info.get("Config", {}).get("Env", [])
        
        for i, env in enumerate(env_vars):
            if "=" in env:
                name, value = env.split("=", 1)
                widget.insertRow(i)
                widget.setItem(i, 0, QTableWidgetItem(name))
                widget.setItem(i, 1, QTableWidgetItem(value))
        
        # If no environment variables, add a message
        if widget.rowCount() == 0:
            widget = QLabel("No environment variables found.")
            widget.setAlignment(Qt.AlignCenter)
        
        return widget
    
    def create_mounts_tab(self):
        """Create tab showing volume mounts."""
        widget = QTableWidget(0, 4)
        widget.setHorizontalHeaderLabels(["Type", "Source", "Destination", "Mode"])
        widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Get mounts
        mounts = self.container_info.get("Mounts", [])
        
        for i, mount in enumerate(mounts):
            widget.insertRow(i)
            widget.setItem(i, 0, QTableWidgetItem(mount.get("Type", "N/A")))
            widget.setItem(i, 1, QTableWidgetItem(mount.get("Source", "N/A")))
            widget.setItem(i, 2, QTableWidgetItem(mount.get("Destination", "N/A")))
            widget.setItem(i, 3, QTableWidgetItem(mount.get("Mode", "N/A")))
        
        # If no mounts, add a message
        if widget.rowCount() == 0:
            widget = QLabel("No mounts found.")
            widget.setAlignment(Qt.AlignCenter)
        
        return widget
    
    def create_networks_tab(self):
        """Create tab showing network settings."""
        widget = QTableWidget(0, 4)
        widget.setHorizontalHeaderLabels(["Network", "IP Address", "Gateway", "MAC Address"])
        widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Get networks
        networks = self.container_info.get("NetworkSettings", {}).get("Networks", {})
        
        i = 0
        for network_name, network_config in networks.items():
            widget.insertRow(i)
            widget.setItem(i, 0, QTableWidgetItem(network_name))
            widget.setItem(i, 1, QTableWidgetItem(network_config.get("IPAddress", "N/A")))
            widget.setItem(i, 2, QTableWidgetItem(network_config.get("Gateway", "N/A")))
            widget.setItem(i, 3, QTableWidgetItem(network_config.get("MacAddress", "N/A")))
            i += 1
        
        # If no networks, add a message
        if widget.rowCount() == 0:
            widget = QLabel("No network configurations found.")
            widget.setAlignment(Qt.AlignCenter)
        
        return widget
    
    def create_json_tab(self):
        """Create tab showing raw JSON data."""
        widget = QTextEdit()
        widget.setReadOnly(True)
        widget.setFont(QFont("Consolas", 9))
        
        # Format JSON with indentation
        json_text = json.dumps(self.container_info, indent=2)
        widget.setText(json_text)
        
        return widget
