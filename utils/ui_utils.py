"""
UI utilities for common UI operations across the application
"""
from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QWidget, QMessageBox
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
import os

def create_reset_button(parent=None, tooltip="Clear all fields and reset to default values"):
    """Create a standardized reset button for tool interfaces"""
    reset_button = QPushButton(parent)
    reset_button.setToolTip(tooltip)
    reset_button.setMinimumWidth(90)
    reset_button.setText("Reset")
    
    # Set icon if available
    icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "reset.png")
    if os.path.exists(icon_path):
        reset_button.setIcon(QIcon(icon_path))
    
    return reset_button

def add_reset_button_to_layout(layout, callback, position=-1):
    """Add a reset button to an existing layout with confirmation dialog"""
    
    # Create a new layout for reset button (right-aligned)
    reset_layout = QHBoxLayout()
    reset_layout.addStretch()
    
    # Create the reset button
    reset_button = create_reset_button()
    
    # Add confirmation before reset
    def confirm_reset():
        reply = QMessageBox.question(
            None, 
            "Confirm Reset",
            "Are you sure you want to reset all fields? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            callback()
    
    reset_button.clicked.connect(confirm_reset)
    reset_layout.addWidget(reset_button)
    
    # Add to the parent layout
    if position < 0:
        layout.addLayout(reset_layout)
    else:
        layout.insertLayout(position, reset_layout)
    
    return reset_button
