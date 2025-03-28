"""
Dialog for displaying detailed container information.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QTabWidget, QWidget, QTextEdit, QTableWidget, QTableWidgetItem,
                            QHeaderView, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import json

class ContainerDetailsDialog(QDialog):
    """Dialog showing detailed information about a container."""
    
    def __init__(self, parent, container_name, container_details):
        super().__init__(parent)
        self.container_name = container_name
        self.container_details = container_details or {}  # Ensure container_details is not None
        self.setWindowTitle(f"Container Details: {container_name}")
        self.resize(800, 600)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Create tabs
        tabs = QTabWidget()
        
        # Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        overview_text = QTextEdit()
        overview_text.setReadOnly(True)
        
        # Populate overview with key details
        if self.container_details:
            overview_html = "<h2>Container Overview</h2>"
            overview_html += f"<p><b>Name:</b> {self.container_name}</p>"
            overview_html += f"<p><b>ID:</b> {self.container_details.get('Id', 'N/A')}</p>"
            overview_html += f"<p><b>Created:</b> {self.container_details.get('Created', 'N/A')}</p>"
            
            # Safely access nested properties
            state = self.container_details.get('State', {}) or {}
            config = self.container_details.get('Config', {}) or {}
            
            overview_html += f"<p><b>Status:</b> {state.get('Status', 'N/A')}</p>"
            overview_html += f"<p><b>Image:</b> {config.get('Image', 'N/A')}</p>"
            
            # Network info - safely access
            network_settings = self.container_details.get('NetworkSettings', {}) or {}
            networks = network_settings.get('Networks', {}) or {}
            
            if networks:
                overview_html += "<h3>Networks</h3><ul>"
                for net_name, net_config in networks.items():
                    net_config = net_config or {}
                    overview_html += f"<li><b>{net_name}:</b> {net_config.get('IPAddress', 'No IP')}</li>"
                overview_html += "</ul>"
                
            # Port mappings - safely access
            ports = network_settings.get('Ports', {}) or {}
            
            if ports:
                overview_html += "<h3>Port Mappings</h3><ul>"
                for container_port, host_bindings in ports.items():
                    if host_bindings:
                        for binding in host_bindings:
                            host_ip = binding.get('HostIp', '0.0.0.0')
                            host_port = binding.get('HostPort', '')
                            overview_html += f"<li>{host_ip}:{host_port} -> {container_port}</li>"
                    else:
                        overview_html += f"<li>{container_port} (not published)</li>"
                overview_html += "</ul>"
                
            overview_text.setHtml(overview_html)
        else:
            overview_text.setPlainText("No container details available")
            
        overview_layout.addWidget(overview_text)
        tabs.addTab(overview_tab, "Overview")
        
        # Environment variables tab
        env_tab = QWidget()
        env_layout = QVBoxLayout(env_tab)
        env_table = QTableWidget(0, 2)
        env_table.setHorizontalHeaderLabels(["Name", "Value"])
        env_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Populate environment variables - safely access
        config = self.container_details.get('Config', {}) or {}
        env_vars = config.get('Env', []) or []
        
        for i, env in enumerate(env_vars):
            if '=' in env:
                name, value = env.split('=', 1)
                env_table.insertRow(i)
                env_table.setItem(i, 0, QTableWidgetItem(name))
                env_table.setItem(i, 1, QTableWidgetItem(value))
                
        env_layout.addWidget(env_table)
        tabs.addTab(env_tab, "Environment")
        
        # Volumes tab
        volumes_tab = QWidget()
        volumes_layout = QVBoxLayout(volumes_tab)
        volumes_table = QTableWidget(0, 2)
        volumes_table.setHorizontalHeaderLabels(["Host Path", "Container Path"])
        volumes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Populate volumes - safely access
        mounts = self.container_details.get('Mounts', []) or []
        
        for i, mount in enumerate(mounts):
            mount = mount or {}
            volumes_table.insertRow(i)
            volumes_table.setItem(i, 0, QTableWidgetItem(mount.get('Source', 'N/A')))
            volumes_table.setItem(i, 1, QTableWidgetItem(mount.get('Destination', 'N/A')))
                
        volumes_layout.addWidget(volumes_table)
        tabs.addTab(volumes_tab, "Volumes")
        
        # Raw JSON tab
        json_tab = QWidget()
        json_layout = QVBoxLayout(json_tab)
        json_text = QTextEdit()
        json_text.setReadOnly(True)
        json_text.setFont(QFont("Courier New", 10))
        
        # Format JSON string with safety check
        if self.container_details:
            try:
                json_str = json.dumps(self.container_details, indent=2)
            except Exception:
                json_str = "Error formatting container details as JSON"
        else:
            json_str = "{}"
            
        json_text.setPlainText(json_str)
        json_layout.addWidget(json_text)
        tabs.addTab(json_tab, "JSON")
        
        layout.addWidget(tabs)
        
        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
