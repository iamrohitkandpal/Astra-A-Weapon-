"""
Theme loader utility for Astra
"""

import os
import json
from PyQt6.QtCore import QObject, pyqtSignal
from pathlib import Path

class ThemeLoader(QObject):
    """Load and apply themes"""
    
    # Signals
    theme_changed = pyqtSignal(str, dict)
    error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.themes_dir = Path("config/themes")
        self.themes = {}
        self.current_theme = "dark"
        self._load_built_in_themes()
        self._load_custom_themes()
    
    def _load_built_in_themes(self):
        """Load built-in themes"""
        self.themes = {
            "dark": self._dark_theme(),
            "light": self._light_theme(),
            "hacker": self._hacker_theme(),
            "obsidian": self._obsidian_theme()  # Add Obsidian-inspired theme
        }
    
    def _load_custom_themes(self):
        """Load custom themes from config directory"""
        # Create themes directory if it doesn't exist
        if not self.themes_dir.exists():
            self.themes_dir.mkdir(parents=True, exist_ok=True)
        
        # Load each JSON theme file
        for theme_file in self.themes_dir.glob("*.json"):
            try:
                with open(theme_file, 'r') as f:
                    theme_data = json.load(f)
                    # Only add if it has a name
                    if "name" in theme_data:
                        self.themes[theme_data["name"]] = theme_data
            except Exception as e:
                print(f"Error loading theme from {theme_file}: {e}")
    
    def get_available_themes(self):
        """Get a list of available theme names"""
        return list(self.themes.keys())
    
    def get_theme(self, theme_name):
        """Get a specific theme by name"""
        return self.themes.get(theme_name, self.themes["dark"])
    
    def get_current_theme_name(self):
        """Get the current theme name"""
        return self.current_theme
    
    def set_current_theme(self, theme_name):
        """Set the current theme"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.theme_changed.emit(theme_name, self.themes[theme_name])
            return True
        return False
    
    def save_theme(self, theme_name, theme_data):
        """Save a custom theme to file"""
        # Make sure the themes directory exists
        if not self.themes_dir.exists():
            self.themes_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the theme
        theme_file = self.themes_dir / f"{theme_name}.json"
        try:
            with open(theme_file, 'w') as f:
                json.dump(theme_data, f, indent=4)
            
            # Update our themes dictionary
            self.themes[theme_name] = theme_data
            
            # Emit signal if this is the current theme
            if theme_name == self.current_theme:
                self.theme_changed.emit(theme_name, theme_data)
            return True
        except Exception as e:
            self.error.emit(f"Error saving theme: {str(e)}")
            return False
    
    def create_theme(self, theme_name, theme_data):
        """Create a new theme"""
        if theme_name in self.themes:
            self.error.emit(f"Theme '{theme_name}' already exists")
            return False
        
        return self.save_theme(theme_name, theme_data)
    
    def update_theme(self, theme_name, theme_data):
        """Update an existing theme"""
        if theme_name not in self.themes:
            self.error.emit(f"Theme '{theme_name}' does not exist")
            return False
        
        return self.save_theme(theme_name, theme_data)
    
    def delete_theme(self, theme_name):
        """Delete a theme file and remove it from the themes dictionary"""
        # Don't allow deleting built-in themes
        if theme_name in ["dark", "light", "hacker", "obsidian"]:
            return False
        
        # Check if theme exists
        if theme_name not in self.themes:
            return False
            
        # Remove from themes dictionary
        del self.themes[theme_name]
        
        # Delete the theme file if it exists
        theme_file = self.themes_dir / f"{theme_name}.json"
        if theme_file.exists():
            try:
                theme_file.unlink()
            except Exception as e:
                print(f"Error deleting theme file {theme_file}: {e}")
                return False
        
        # If the deleted theme was the current theme, switch to dark theme
        if theme_name == self.current_theme:
            self.set_current_theme("dark")
            
        return True
    
    def generate_stylesheet(self, theme_data):
        """Generate a stylesheet from theme data"""
        if isinstance(theme_data, dict) and "stylesheet" in theme_data:
            return theme_data["stylesheet"]
        return self._dark_theme()["stylesheet"]
    
    def _obsidian_theme(self):
        """Obsidian-inspired theme"""
        return {
            "name": "obsidian",
            "stylesheet": """
                /* Base Colors */
                QMainWindow, QDialog {
                    background-color: #202225;
                    color: #dcddde;
                }
                QWidget {
                    background-color: #202225;
                    color: #dcddde;
                }
                
                /* Sidebar */
                #sidebar {
                    background-color: #2f3136;
                    border-right: none;
                }
                #contentArea {
                    background-color: #36393f;
                    border-top-left-radius: 8px;
                    border-bottom-left-radius: 8px;
                }
                
                /* Buttons */
                QPushButton {
                    background-color: #4f545c;
                    color: #dcddde;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QPushButton:hover {
                    background-color: #5d6269;
                }
                QPushButton:checked {
                    background-color: #7289da;
                    color: white;
                }
                QPushButton:disabled {
                    background-color: #3b3e45;
                    color: #72767d;
                }
                
                /* App Title */
                #appTitle {
                    color: #7289da;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-weight: bold;
                }
                
                /* Combo Box */
                QComboBox {
                    background-color: #40444b;
                    color: #dcddde;
                    border: none;
                    padding: 6px;
                    border-radius: 4px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QComboBox QAbstractItemView {
                    background-color: #40444b;
                    color: #dcddde;
                    selection-background-color: #7289da;
                    border: none;
                }
                
                /* Text Inputs */
                QLineEdit, QTextEdit, QSpinBox {
                    background-color: #40444b;
                    color: #dcddde;
                    border: none;
                    border-radius: 4px;
                    padding: 6px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #4f545c;
                    border: none;
                    width: 16px;
                    border-radius: 2px;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #5d6269;
                }
                
                /* Group Box */
                QGroupBox {
                    border: 1px solid #40444b;
                    border-radius: 6px;
                    margin-top: 1.5ex;
                    padding-top: 10px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 8px;
                    color: #dcddde;
                }
                
                /* Tables */
                QTableWidget {
                    background-color: #40444b;
                    alternate-background-color: #36393f;
                    color: #dcddde;
                    border: none;
                    gridline-color: #4f545c;
                    border-radius: 6px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QTableWidget::item {
                    padding: 6px;
                    border-bottom: 1px solid #36393f;
                }
                QTableWidget::item:selected {
                    background-color: #7289da;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #2f3136;
                    color: #dcddde;
                    padding: 6px;
                    border: none;
                    font-weight: bold;
                }
                
                /* Progress Bar */
                QProgressBar {
                    border: none;
                    border-radius: 3px;
                    text-align: center;
                    background-color: #40444b;
                    color: #dcddde;
                    height: 14px;
                }
                QProgressBar::chunk {
                    background-color: #7289da;
                }
                
                /* Check Box */
                QCheckBox {
                    spacing: 6px;
                    color: #dcddde;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: none;
                    border-radius: 3px;
                    background-color: #40444b;
                }
                QCheckBox::indicator:checked {
                    background-color: #7289da;
                    image: url(ui/assets/check.png);
                }
                QCheckBox::indicator:hover {
                    background-color: #4f545c;
                }
                
                /* Radio Button */
                QRadioButton {
                    spacing: 6px;
                    color: #dcddde;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                    border: none;
                    border-radius: 8px;
                    background-color: #40444b;
                }
                QRadioButton::indicator:checked {
                    background-color: #7289da;
                    border: 4px solid #40444b;
                }
                QRadioButton::indicator:hover {
                    background-color: #4f545c;
                }
                
                /* Sidebar Sections */
                #sidebarSectionLabel {
                    color: #72767d;
                    font-weight: bold;
                    margin-top: 6px;
                    margin-bottom: 6px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 11px;
                }
                
                /* Tool Cards */
                #toolCard {
                    background-color: #36393f;
                    border: none;
                    border-radius: 6px;
                    padding: 8px;
                }
                #toolCard:hover {
                    background-color: #4f545c;
                }
                
                /* Tool Card Title and Description */
                #toolCardTitle {
                    color: #ffffff;
                    font-weight: bold;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                #toolCardDescription {
                    color: #b9bbbe;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                /* Version and Memory Labels */
                #versionLabel, #memoryLabel {
                    color: #72767d;
                    font-size: 10px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                /* Dashboard Header and Section Titles */
                #dashboardHeader, #sectionTitle {
                    color: #ffffff;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                /* Placeholder Text */
                #placeholderText {
                    color: #72767d;
                    font-style: italic;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                /* Welcome Message */
                #welcomeMessage {
                    color: #7289da;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
            """
        }
    
    def _dark_theme(self):
        """Built-in dark theme"""
        return {
            "name": "dark",
            "stylesheet": """
                QMainWindow, QDialog {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                }
                QWidget {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                }
                #sidebar {
                    background-color: #1e1e1e;
                    border-right: 1px solid #3a3a3a;
                }
                #contentArea {
                    background-color: #2b2b2b;
                }
                QPushButton {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #454545;
                }
                QPushButton:checked {
                    background-color: #0078d7;
                    color: white;
                }
                QPushButton:disabled {
                    background-color: #2a2a2a;
                    color: #606060;
                }
                #appTitle {
                    color: #0078d7;
                }
                QComboBox {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                    padding: 5px;
                    border-radius: 3px;
                }
                QComboBox QAbstractItemView {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    selection-background-color: #0078d7;
                }
                QLineEdit, QTextEdit, QSpinBox {
                    background-color: #333333;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 5px;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #3a3a3a;
                    border: none;
                    width: 16px;
                    border-radius: 2px;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #454545;
                }
                QGroupBox {
                    border: 1px solid #555555;
                    border-radius: 5px;
                    margin-top: 1ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 5px;
                }
                QTableWidget {
                    border: 1px solid #555555;
                    border-radius: 8px;
                    background-color: #333333;
                }
                QRadioButton::indicator:checked {
                    background-color: #0078d7;
                    border: 4px solid #333333;
                }
                QRadioButton::indicator:hover {
                    border: 1px solid #0078d7;
                }
                #sidebarSectionLabel {
                    color: #8a8a8a;
                    font-weight: bold;
                    margin-top: 5px;
                    margin-bottom: 5px;
                }
                #toolCard {
                    background-color: #333333;
                    border: 1px solid #555555;
                    border-radius: 5px;
                }
                /* Tool Card Title and Description */
                #toolCardTitle {
                    color: #ffffff;
                    font-weight: bold;
                }
                #toolCardDescription {
                    color: #b9bbbe;
                }
                #versionLabel {
                    color: #8a8a8a;
                    font-size: 10px;
                }
                #memoryLabel {
                    color: #8a8a8a;
                    font-size: 10px;
                }
                /* Dashboard Header and Section Titles */
                #dashboardHeader, #sectionTitle {
                    color: #ffffff;
                }
                /* Placeholder Text */
                #placeholderText {
                    color: #8a8a8a;
                    font-style: italic;
                }
                /* Welcome Message */
                #welcomeMessage {
                    color: #0078d7;
                }
            """
        }
    
    def _light_theme(self):
        """Built-in light theme"""
        return {
            "name": "light",
            "stylesheet": """
                QMainWindow, QDialog {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                QWidget {
                    background-color: #f5f5f5;
                    color: #333333;
                }
                #sidebar {
                    background-color: #e5e5e5;
                    border-right: 1px solid #cccccc;
                }
                #contentArea {
                    background-color: #f5f5f5;
                }
                QPushButton {
                    background-color: #d8d8d8;
                    color: #333333;
                    border: none;
                    padding: 8px 15px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #c8c8c8;
                }
                QPushButton:checked {
                    background-color: #0078d7;
                    color: white;
                }
                QPushButton:disabled {
                    background-color: #f0f0f0;
                    color: #aaaaaa;
                }
                #appTitle {
                    color: #0078d7;
                }
                QComboBox {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #cccccc;
                    padding: 5px;
                    border-radius: 3px;
                }
                QComboBox QAbstractItemView {
                    background-color: #ffffff;
                    color: #333333;
                    selection-background-color: #0078d7;
                }
                QLineEdit, QTextEdit, QSpinBox {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    padding: 5px;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #e0e0e0;
                    border: none;
                    width: 16px;
                    border-radius: 2px;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #d0d0d0;
                }
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    margin-top: 1ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 5px;
                }
                QTableWidget {
                    background-color: #ffffff;
                    alternate-background-color: #f9f9f9;
                    border: 1px solid #cccccc;
                }
                QTableWidget::item {
                    padding: 5px;
                }
                QTableWidget::item:selected {
                    background-color: #0078d7;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #f0f0f0;
                    color: #333333;
                    padding: 5px;
                    border: 1px solid #cccccc;
                }
                QProgressBar {
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    text-align: center;
                    background-color: #ffffff;
                    color: #333333;
                    height: 14px;
                }
                QProgressBar::chunk {
                    background-color: #0078d7;
                    width: 10px;
                }
                QCheckBox {
                    spacing: 5px;
                    color: #333333;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    background-color: #ffffff;
                }
                QCheckBox::indicator:checked {
                    background-color: #0078d7;
                    image: url(ui/assets/check.png);
                }
                QCheckBox::indicator:hover {
                    border: 1px solid #0078d7;
                }
                QRadioButton {
                    spacing: 5px;
                    color: #333333;
                }
                QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                    border: 1px solid #cccccc;
                    border-radius: 8px;
                    background-color: #ffffff;
                }
                QRadioButton::indicator:checked {
                    background-color: #0078d7;
                    border: 4px solid #ffffff;
                }
                QRadioButton::indicator:hover {
                    border: 1px solid #0078d7;
                }
                #sidebarSectionLabel {
                    color: #757575;
                    font-weight: bold;
                    margin-top: 5px;
                    margin-bottom: 5px;
                }
                #toolCard {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                }
                /* Tool Card Title and Description */
                #toolCardTitle {
                    color: #333333;
                    font-weight: bold;
                }
                #toolCardDescription {
                    color: #555555;
                }
                #versionLabel {
                    color: #757575;
                    font-size: 10px;
                }
                #memoryLabel {
                    color: #757575;
                    font-size: 10px;
                }
                /* Dashboard Header and Section Titles */
                #dashboardHeader, #sectionTitle {
                    color: #333333;
                }
                /* Placeholder Text */
                #placeholderText {
                    color: #757575;
                    font-style: italic;
                }
                /* Welcome Message */
                #welcomeMessage {
                    color: #0078d7;
                }
            """
        }
    
    def _hacker_theme(self):
        """Hacker theme stylesheet"""
        return {
            "name": "hacker",
            "stylesheet": """
                QMainWindow, QDialog {
                    background-color: #0a0a0a;
                    color: #00ff00;
                }
                QWidget {
                    background-color: #0a0a0a;
                    color: #00ff00;
                }
                #sidebar {
                    background-color: #0f0f0f;
                    border-right: 1px solid #1a1a1a;
                }
                #contentArea {
                    background-color: #0a0a0a;
                }
                QPushButton {
                    background-color: #1a1a1a;
                    color: #00ff00;
                    border: 1px solid #00ff00;
                    padding: 8px 15px;
                    border-radius: 0px;
                    font-family: monospace;
                }
                QPushButton:hover {
                    background-color: #1a1a1a;
                    border: 1px solid #00ff8a;
                    color: #00ff8a;
                }
                QPushButton:checked {
                    background-color: #00ff00;
                    color: #000000;
                    font-weight: bold;
                }
                QPushButton:disabled {
                    background-color: #1a1a1a;
                    color: #005500;
                    border: 1px solid #005500;
                }
                #appTitle {
                    color: #00ff00;
                    font-family: monospace;
                    font-weight: bold;
                    font-size: 18px;
                }
                QComboBox {
                    background-color: #1a1a1a;
                    color: #00ff00;
                    border: 1px solid #00ff00;
                    padding: 5px;
                    border-radius: 0px;
                    font-family: monospace;
                }
                QComboBox QAbstractItemView {
                    background-color: #1a1a1a;
                    color: #00ff00;
                    selection-background-color: #005500;
                }
                QLineEdit, QTextEdit, QSpinBox {
                    background-color: #1a1a1a;
                    color: #00ff00;
                    border: 1px solid #00ff00;
                    border-radius: 0px;
                    padding: 5px;
                    font-family: monospace;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #1a1a1a;
                    border: 1px solid #00ff00;
                    width: 16px;
                    border-radius: 0px;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #2a2a2a;
                    border: 1px solid #00ff8a;
                }
                QGroupBox {
                    border: 1px solid #00ff00;
                    border-radius: 0px;
                    margin-top: 1ex;
                    padding-top: 10px;
                    font-family: monospace;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 5px;
                    color: #00ff00;
                }
                QTableWidget {
                    background-color: #1a1a1a;
                    alternate-background-color: #0f0f0f;
                    border: 1px solid #00ff00;
                    font-family: monospace;
                }
                QTableWidget::item {
                    padding: 5px;
                }
                QTableWidget::item:selected {
                    background-color: #005500;
                    color: #00ff00;
                }
                QHeaderView::section {
                    background-color: #1a1a1a;
                    color: #00ff00;
                    padding: 5px;
                    border: 1px solid #00ff00;
                    font-weight: bold;
                }
                QProgressBar {
                    border: 1px solid #00ff00;
                    border-radius: 0px;
                    text-align: center;
                    background-color: #1a1a1a;
                    color: #00ff00;
                    height: 14px;
                    font-family: monospace;
                }
                QProgressBar::chunk {
                    background-color: #00ff00;
                    width: 10px;
                }
                QCheckBox {
                    spacing: 5px;
                    color: #00ff00;
                    font-family: monospace;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                    border: 1px solid #00ff00;
                    border-radius: 0px;
                    background-color: #1a1a1a;
                }
                QCheckBox::indicator:checked {
                    background-color: #00ff00;
                    image: url(ui/assets/check_hacker.png);
                }
                QCheckBox::indicator:hover {
                    border: 1px solid #00ff8a;
                }
                QRadioButton {
                    spacing: 5px;
                    color: #00ff00;
                    font-family: monospace;
                }
                QRadioButton::indicator {
                    width: 16px;
                    height: 16px;
                    border: 1px solid #00ff00;
                    border-radius: 0px;
                    background-color: #1a1a1a;
                }
                QRadioButton::indicator:checked {
                    background-color: #00ff00;
                    border: 4px solid #1a1a1a;
                }
                QRadioButton::indicator:hover {
                    border: 1px solid #00ff8a;
                }
                #sidebarSectionLabel {
                    color: #008800;
                    font-weight: bold;
                    margin-top: 5px;
                    margin-bottom: 5px;
                    font-family: monospace;
                }
                #toolCard {
                    background-color: #1a1a1a;
                    border: 1px solid #00ff00;
                    border-radius: 0px;
                }
                /* Tool Card Title and Description */
                #toolCardTitle {
                    color: #00ff00;
                    font-weight: bold;
                    font-family: monospace;
                }
                #toolCardDescription {
                    color: #008800;
                    font-family: monospace;
                }
                #versionLabel {
                    color: #008800;
                    font-size: 10px;
                    font-family: monospace;
                }
                #memoryLabel {
                    color: #008800;
                    font-size: 10px;
                    font-family: monospace;
                }
                /* Dashboard Header and Section Titles */
                #dashboardHeader, #sectionTitle {
                    color: #00ff00;
                    font-family: monospace;
                }
                /* Placeholder Text */
                #placeholderText {
                    color: #008800;
                    font-style: italic;
                    font-family: monospace;
                }
                /* Welcome Message */
                #welcomeMessage {
                    color: #00ff00;
                    font-family: monospace;
                }
                QLabel {
                    font-family: monospace;
                }
            """
        }
