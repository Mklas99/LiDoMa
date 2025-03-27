from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit, 
                            QFormLayout, QComboBox, QCheckBox, QGroupBox, QHBoxLayout)

class CreateContainerDialog(QDialog):
    def __init__(self, image_id, docker_service, context="default", parent=None):
        super().__init__(parent)
        self.image_id = image_id
        self.docker_service = docker_service
        self.context = context
        self.setWindowTitle(f"Create Container from {image_id}")
        self.setMinimumSize(500, 300)

        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        image_label = QLabel(f"Image: {image_id}")
        image_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(image_label)
        
        context_label = QLabel(f"Context: {context}")
        header_layout.addWidget(context_label)
        layout.addLayout(header_layout)
        
        # Container settings
        settings_group = QGroupBox("Container Settings")
        form_layout = QFormLayout(settings_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Container Name")
        form_layout.addRow("Name:", self.name_edit)
        
        # Port mapping could be added here
        self.port_edit = QLineEdit()
        self.port_edit.setPlaceholderText("host:container, e.g. 8080:80")
        form_layout.addRow("Port Mapping:", self.port_edit)
        
        # Environment variables
        self.env_edit = QLineEdit()
        self.env_edit.setPlaceholderText("key=value,key2=value2")
        form_layout.addRow("Environment:", self.env_edit)
        
        # Auto-remove when stopped
        self.auto_remove = QCheckBox("Auto-remove when stopped")
        form_layout.addRow("", self.auto_remove)
        
        layout.addWidget(settings_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self._on_create)
        button_layout.addWidget(create_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _on_create(self):
        name = self.name_edit.text().strip()
        if not name:
            name = None
            
        # Here we'd parse ports, env variables, etc.
        
        # For now, basic container creation only
        success = self.docker_service.create_container(
            image=self.image_id, 
            name=name,
            context=self.context
        )
        
        if success:
            print(f"Created container from {self.image_id}")
        else:
            print(f"Failed to create container from {self.image_id}")
        
        self.close()
