#!/usr/bin/env python3
"""
Test script for the theme editor
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import QTimer

from ui.controllers.theme_controller import ThemeController

class ThemeEditorTest(QMainWindow):
    """Test window for theme editor"""
    
    def __init__(self):
        super().__init__()
        self.theme_controller = ThemeController()
        self.setup_ui()
        
        # Connect theme changed signal
        self.theme_controller.theme_changed.connect(self.apply_theme)
        
        # Apply initial theme
        self.apply_theme(self.theme_controller.get_current_theme())
    
    def setup_ui(self):
        """Setup the UI components"""
        self.setWindowTitle("Theme Editor Test")
        self.resize(800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout
        layout = QVBoxLayout(central)
        
        # Test header
        header = QLabel("Theme Editor Test")
        header.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(header)
        
        # Description
        desc = QLabel("This is a test application for the theme editor.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Open editor button
        self.edit_button = QPushButton("Open Theme Editor")
        self.edit_button.clicked.connect(self.open_editor)
        layout.addWidget(self.edit_button)
        
        # Toggle auto-detect button
        self.auto_detect_button = QPushButton("Enable Auto-Detect Theme")
        self.auto_detect_button.setCheckable(True)
        self.auto_detect_button.setChecked(self.theme_controller.is_auto_detect_enabled())
        self.auto_detect_button.clicked.connect(self.toggle_auto_detect)
        layout.addWidget(self.auto_detect_button)
        
        # Add stretch
        layout.addStretch()
    
    def open_editor(self):
        """Open the theme editor"""
        self.theme_controller.open_theme_editor(self)
    
    def toggle_auto_detect(self, checked):
        """Toggle auto-detect theme mode"""
        self.theme_controller.enable_auto_detect(checked)
        
        if checked:
            self.auto_detect_button.setText("Disable Auto-Detect Theme")
        else:
            self.auto_detect_button.setText("Enable Auto-Detect Theme")
    
    def apply_theme(self, theme_data):
        """Apply the theme to the UI"""
        # Generate stylesheet from theme data
        stylesheet = self.generate_stylesheet(theme_data)
        
        # Apply the stylesheet
        self.setStyleSheet(stylesheet)
    
    def generate_stylesheet(self, theme_data):
        """Generate stylesheet from theme data"""
        is_dark = theme_data.get("is_dark", False)
        
        background_color = theme_data.get("background_color", "#f5f5f5" if not is_dark else "#2c3e50")
        card_background = theme_data.get("card_background", "#ffffff" if not is_dark else "#34495e")
        text_color = theme_data.get("text_color", "#333333" if not is_dark else "#ecf0f1")
        primary_color = theme_data.get("primary_color", "#3498db")
        secondary_color = theme_data.get("secondary_color", "#2980b9")
        accent_color = theme_data.get("accent_color", "#27ae60")
        border_color = theme_data.get("border_color", "#dddddd" if not is_dark else "#7f8c8d")
        
        return f"""
            QMainWindow, QDialog {{
                background-color: {background_color};
                color: {text_color};
            }}
            
            QWidget {{
                background-color: {background_color};
                color: {text_color};
            }}
            
            QPushButton {{
                background-color: {secondary_color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            
            QPushButton:hover {{
                background-color: {primary_color};
            }}
            
            QPushButton:pressed {{
                background-color: {accent_color};
            }}
            
            QPushButton:checked {{
                background-color: {accent_color};
            }}
            
            QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                background-color: {card_background};
                color: {text_color};
                border: 1px solid {border_color};
                padding: 6px;
                border-radius: 4px;
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {border_color};
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Create and show the test window
    window = ThemeEditorTest()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
