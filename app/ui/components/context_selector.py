"""
Docker context selector widget.
"""
from typing import List
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal

class ContextSelector(QWidget):
    """Widget for selecting Docker contexts."""
    
    # Signal emitted when context is changed
    context_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create context label
        self.context_label = QLabel("Docker Context:")
        self.layout.addWidget(self.context_label)
        
        # Create context dropdown
        self.context_dropdown = QComboBox()
        self.context_dropdown.setMinimumWidth(150)
        self.context_dropdown.currentTextChanged.connect(self.on_context_changed)
        self.layout.addWidget(self.context_dropdown)
        
        # Add a spacer
        self.layout.addStretch()
    
    def set_contexts(self, contexts: List[str], current_context: str = None):
        """Set the available contexts and select the current one."""
        # Block signals to prevent triggering on_context_changed
        self.context_dropdown.blockSignals(True)
        
        # Clear and populate the dropdown
        self.context_dropdown.clear()
        self.context_dropdown.addItems(contexts)
        
        # Set current context if provided
        if current_context and current_context in contexts:
            index = self.context_dropdown.findText(current_context)
            self.context_dropdown.setCurrentIndex(index)
        
        # Unblock signals
        self.context_dropdown.blockSignals(False)
    
    def on_context_changed(self, context_name: str):
        """Handle context changed by user."""
        if context_name:
            self.context_changed.emit(context_name)
    
    def get_current_context(self) -> str:
        """Get the currently selected context."""
        return self.context_dropdown.currentText()
