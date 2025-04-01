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
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        label = QLabel("Docker Context:")
        layout.addWidget(label)
        
        # Context dropdown
        self.context_combo = QComboBox()
        self.context_combo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.context_combo.setMinimumWidth(150)
        
        # Add "All" option as first item
        self.context_combo.addItem("All")
        
        # Connect signal
        self.context_combo.currentTextChanged.connect(self.on_context_changed)
        
        layout.addWidget(self.context_combo)
        layout.addStretch()
        
    def set_contexts(self, contexts: List[str], current_context: str = None):
        """Set the available contexts and select the current one."""
        # Remember current selection
        previous_selection = self.get_current_context()
        
        # Block signals while updating
        self.context_combo.blockSignals(True)
        
        # Clear existing items (except "All")
        while self.context_combo.count() > 1:
            self.context_combo.removeItem(1)
        
        # Add contexts
        for ctx in contexts:
            if ctx != "All":  # Avoid duplicating "All" item
                self.context_combo.addItem(ctx)
        
        # Set current selection
        if current_context and current_context in contexts:
            index = self.context_combo.findText(current_context)
            if index >= 0:
                self.context_combo.setCurrentIndex(index)
        elif previous_selection and previous_selection != "All":
            index = self.context_combo.findText(previous_selection)
            if index >= 0:
                self.context_combo.setCurrentIndex(index)
        else:
            # Default to "All" - always select "All" first
            self.context_combo.setCurrentIndex(0)
        
        # Unblock signals
        self.context_combo.blockSignals(False)
        
        # DO NOT emit context_changed signal here - this was causing infinite recursion
        # We only want to emit when the user actually changes the selection
        
    def get_current_context(self) -> str:
        """Get the currently selected context."""
        return self.context_combo.currentText()
    
    def on_context_changed(self, context_name: str):
        """Handle context changed by user."""
        if context_name:
            self.context_changed.emit(context_name)
