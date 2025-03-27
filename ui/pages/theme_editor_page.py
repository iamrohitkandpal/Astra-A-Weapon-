"""
Theme editor page for Astra
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
                           QGroupBox, QFormLayout, QComboBox, QColorDialog, QTabWidget,
                           QScrollArea, QCheckBox, QMessageBox, QFileDialog, QTextEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import json

from utils.theme_loader import ThemeLoader

class ColorButton(QPushButton):
    """Custom button for selecting colors"""
    
    def __init__(self, initial_color="#333333"):
        super().__init__()
        self.color = initial_color
        self.setFixedSize(60, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setColor(initial_color)
        self.clicked.connect(self.show_color_dialog)
    
    def setColor(self, color):
        """Set the button color"""
        self.color = color
        self.setStyleSheet(f"background-color: {color}; border: 1px solid #999999;")
    
    def show_color_dialog(self):
        """Show color picker dialog"""
        color = QColorDialog.getColor(QColor(self.color), self)
        if color.isValid():
            self.setColor(color.name())

class ThemeEditorPage(QWidget):
    """Theme editor page for creating and modifying themes"""
    
    def __init__(self):
        super().__init__()
        self.theme_loader = ThemeLoader()
        self.current_theme_data = None
        self.color_buttons = {}
        self.setup_ui()
        self.connect_signals()
        
        # Load available themes
        self.load_available_themes()
    
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Theme Editor")
        header_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Create and customize themes for Astra")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Theme selection and creation
        selection_group = QGroupBox("Theme Selection")
        selection_layout = QFormLayout(selection_group)
        
        # Theme selector
        theme_layout = QHBoxLayout()
        self.theme_selector = QComboBox()
        self.load_button = QPushButton("Load")
        self.new_button = QPushButton("New Theme")
        
        theme_layout.addWidget(self.theme_selector)
        theme_layout.addWidget(self.load_button)
        theme_layout.addWidget(self.new_button)
        selection_layout.addRow("Select Theme:", theme_layout)
        
        # New theme name input (initially hidden)
        self.new_theme_layout = QHBoxLayout()
        self.new_theme_name = QLineEdit()
        self.new_theme_name.setPlaceholderText("Enter theme name")
        self.create_button = QPushButton("Create")
        self.cancel_button = QPushButton("Cancel")
        
        self.new_theme_layout.addWidget(self.new_theme_name)
        self.new_theme_layout.addWidget(self.create_button)
        self.new_theme_layout.addWidget(self.cancel_button)
        selection_layout.addRow("New Theme:", self.new_theme_layout)
        
        # Hide new theme row initially
        self.new_theme_name.hide()
        self.create_button.hide()
        self.cancel_button.hide()
        
        layout.addWidget(selection_group)
        
        # Theme editor tabs
        self.editor_tabs = QTabWidget()
        
        # Basic colors tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Create scrollable area for the color groups
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Window colors
        window_group = QGroupBox("Window Colors")
        window_layout = QFormLayout(window_group)
        self.add_color_buttons(window_layout, [
            ("window_background", "Background Color"),
            ("window_text", "Text Color")
        ])
        scroll_layout.addWidget(window_group)
        
        # Sidebar colors
        sidebar_group = QGroupBox("Sidebar Colors")
        sidebar_layout = QFormLayout(sidebar_group)
        self.add_color_buttons(sidebar_layout, [
            ("sidebar_background", "Background Color"),
            ("sidebar_border", "Border Color"),
            ("sidebar_section_label", "Section Label Color")
        ])
        scroll_layout.addWidget(sidebar_group)
        
        # Button colors
        button_group = QGroupBox("Button Colors")
        button_layout = QFormLayout(button_group)
        self.add_color_buttons(button_layout, [
            ("button_background", "Background Color"),
            ("button_text", "Text Color"),
            ("button_hover_background", "Hover Background Color"),
            ("button_checked_background", "Checked Background Color"),
            ("button_checked_text", "Checked Text Color"),
            ("button_disabled_background", "Disabled Background Color"),
            ("button_disabled_text", "Disabled Text Color")
        ])
        scroll_layout.addWidget(button_group)
        
        # Input colors
        input_group = QGroupBox("Input Colors")
        input_layout = QFormLayout(input_group)
        self.add_color_buttons(input_layout, [
            ("input_background", "Background Color"),
            ("input_border", "Border Color"),
            ("input_text", "Text Color")
        ])
        scroll_layout.addWidget(input_group)
        
        # Table colors
        table_group = QGroupBox("Table Colors")
        table_layout = QFormLayout(table_group)
        self.add_color_buttons(table_layout, [
            ("table_background", "Background Color"),
            ("table_alternate_background", "Alternate Row Color"),
            ("table_border", "Border Color"),
            ("table_header_background", "Header Background Color"),
            ("table_header_text", "Header Text Color"),
            ("table_selected_background", "Selected Background Color"),
            ("table_selected_text", "Selected Text Color")
        ])
        scroll_layout.addWidget(table_group)
        
        scroll_area.setWidget(scroll_content)
        basic_layout.addWidget(scroll_area)
        
        # Advanced settings tab
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        # Font settings
        font_group = QGroupBox("Font Settings")
        font_layout = QFormLayout(font_group)
        
        self.font_family = QComboBox()
        self.font_family.addItems(["Default", "Arial", "Helvetica", "Segoe UI", "Roboto", "Source Sans Pro"])
        font_layout.addRow("Font Family:", self.font_family)
        
        self.monospace_checkbox = QCheckBox("Use Monospace Font (overrides font family)")
        font_layout.addRow("", self.monospace_checkbox)
        
        advanced_layout.addWidget(font_group)
        
        # Border settings
        border_group = QGroupBox("Border Settings")
        border_layout = QFormLayout(border_group)
        
        self.border_radius = QLineEdit("4px")
        border_layout.addRow("Border Radius:", self.border_radius)
        
        advanced_layout.addWidget(border_group)
        
        # Add stretch to push everything to the top
        advanced_layout.addStretch()
        
        # JSON preview tab
        json_tab = QWidget()
        json_layout = QVBoxLayout(json_tab)
        
        self.json_preview = QTextEdit()
        self.json_preview.setReadOnly(True)
        self.json_preview.setFont(QFont("Courier New", 10))
        json_layout.addWidget(self.json_preview)
        
        # Add tabs
        self.editor_tabs.addTab(basic_tab, "Basic Colors")
        self.editor_tabs.addTab(advanced_tab, "Advanced Settings")
        self.editor_tabs.addTab(json_tab, "JSON Preview")
        
        layout.addWidget(self.editor_tabs)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Theme")
        self.save_button.setMinimumWidth(120)
        self.export_button = QPushButton("Export Theme")
        self.export_button.setMinimumWidth(120)
        self.import_button = QPushButton("Import Theme")
        self.import_button.setMinimumWidth(120)
        self.apply_button = QPushButton("Apply Theme")
        self.apply_button.setMinimumWidth(120)
        self.delete_button = QPushButton("Delete Theme")
        self.delete_button.setMinimumWidth(120)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def add_color_buttons(self, layout, colors):
        """Add color selection buttons to a layout"""
        for key, label in colors:
            button = ColorButton("#333333")
            layout.addRow(label + ":", button)
            self.color_buttons[key] = button
    
    def connect_signals(self):
        """Connect signals to slots"""
        self.load_button.clicked.connect(self.load_theme)
        self.new_button.clicked.connect(self.show_new_theme_input)
        self.create_button.clicked.connect(self.create_new_theme)
        self.cancel_button.clicked.connect(self.hide_new_theme_input)
        self.save_button.clicked.connect(self.save_theme)
        self.export_button.clicked.connect(self.export_theme)
        self.import_button.clicked.connect(self.import_theme)
        self.apply_button.clicked.connect(self.apply_theme)
        self.delete_button.clicked.connect(self.delete_theme)
        
        # Update JSON preview when tabs change
        self.editor_tabs.currentChanged.connect(self.update_json_preview)
    
    def load_available_themes(self):
        """Load available themes into the selector"""
        # Clear current items
        self.theme_selector.clear()
        
        # Add available themes
        available_themes = self.theme_loader.get_available_themes()
        for theme_name in available_themes:
            self.theme_selector.addItem(theme_name)
        
        # Set current theme
        current_theme = self.theme_loader.get_current_theme_name()
        index = self.theme_selector.findText(current_theme)
        if index >= 0:
            self.theme_selector.setCurrentIndex(index)
    
    def show_new_theme_input(self):
        """Show the new theme input field"""
        self.new_theme_name.show()
        self.create_button.show()
        self.cancel_button.show()
        self.new_theme_name.setFocus()
    
    def hide_new_theme_input(self):
        """Hide the new theme input field"""
        self.new_theme_name.hide()
        self.create_button.hide()
        self.cancel_button.hide()
        self.new_theme_name.clear()
    
    def create_new_theme(self):
        """Create a new theme"""
        theme_name = self.new_theme_name.text().strip()
        if not theme_name:
            self.show_error("Please enter a name for the new theme")
            return
        
        # Create new theme from default dark theme
        default_theme = self.theme_loader.get_theme("dark")
        
        # Set new name
        theme_data = default_theme.copy()
        theme_data["name"] = theme_name
        
        # Create the theme
        self.theme_loader.save_theme(theme_name, theme_data)
        
        # Hide input
        self.hide_new_theme_input()
        
        # Reload themes and select the new one
        self.load_available_themes()
        index = self.theme_selector.findText(theme_name)
        if index >= 0:
            self.theme_selector.setCurrentIndex(index)
            self.load_theme()
    
    def load_theme(self):
        """Load the selected theme for editing"""
        theme_name = self.theme_selector.currentText()
        if not theme_name:
            return
        
        # Get theme data
        self.current_theme_data = self.theme_loader.get_theme(theme_name)
        
        # Update UI with theme colors
        if self.current_theme_data:
            self.update_color_buttons()
            self.update_advanced_settings()
            self.update_json_preview()
    
    def update_color_buttons(self):
        """Update color buttons with current theme colors"""
        if not self.current_theme_data:
            return
        
        colors = self.current_theme_data.get("colors", {})
        
        # Window colors
        if "window" in colors:
            window = colors["window"]
            if "background" in window:
                self.color_buttons["window_background"].setColor(window["background"])
            if "text" in window:
                self.color_buttons["window_text"].setColor(window["text"])
        
        # Sidebar colors
        if "sidebar" in colors:
            sidebar = colors["sidebar"]
            if "background" in sidebar:
                self.color_buttons["sidebar_background"].setColor(sidebar["background"])
            if "border" in sidebar:
                self.color_buttons["sidebar_border"].setColor(sidebar["border"])
            if "section_label" in sidebar:
                self.color_buttons["sidebar_section_label"].setColor(sidebar["section_label"])
        
        # Button colors
        if "button" in colors:
            button = colors["button"]
            if "background" in button:
                self.color_buttons["button_background"].setColor(button["background"])
            if "text" in button:
                self.color_buttons["button_text"].setColor(button["text"])
            if "hover_background" in button:
                self.color_buttons["button_hover_background"].setColor(button["hover_background"])
            if "checked_background" in button:
                self.color_buttons["button_checked_background"].setColor(button["checked_background"])
            if "checked_text" in button:
                self.color_buttons["button_checked_text"].setColor(button["checked_text"])
            if "disabled_background" in button:
                self.color_buttons["button_disabled_background"].setColor(button["disabled_background"])
            if "disabled_text" in button:
                self.color_buttons["button_disabled_text"].setColor(button["disabled_text"])
        
        # Input colors
        if "input" in colors:
            input_colors = colors["input"]
            if "background" in input_colors:
                self.color_buttons["input_background"].setColor(input_colors["background"])
            if "border" in input_colors:
                self.color_buttons["input_border"].setColor(input_colors["border"])
            if "text" in input_colors:
                self.color_buttons["input_text"].setColor(input_colors["text"])
        
        # Table colors
        if "table" in colors:
            table = colors["table"]
            if "background" in table:
                self.color_buttons["table_background"].setColor(table["background"])
            if "alternate_background" in table:
                self.color_buttons["table_alternate_background"].setColor(table["alternate_background"])
            if "border" in table:
                self.color_buttons["table_border"].setColor(table["border"])
            if "header_background" in table:
                self.color_buttons["table_header_background"].setColor(table["header_background"])
            if "header_text" in table:
                self.color_buttons["table_header_text"].setColor(table["header_text"])
            if "selected_background" in table:
                self.color_buttons["table_selected_background"].setColor(table["selected_background"])
            if "selected_text" in table:
                self.color_buttons["table_selected_text"].setColor(table["selected_text"])
    
    def update_advanced_settings(self):
        """Update advanced settings with current theme data"""
        if not self.current_theme_data:
            return
        
        # Check for special settings
        special = self.current_theme_data.get("special", {})
        
        # Font family
        font_family = special.get("font_family", "")
        if font_family:
            index = self.font_family.findText(font_family.capitalize())
            if index >= 0:
                self.font_family.setCurrentIndex(index)
            else:
                self.font_family.setCurrentIndex(0)  # Default
        else:
            self.font_family.setCurrentIndex(0)  # Default
        
        # Monospace checkbox
        self.monospace_checkbox.setChecked(font_family == "monospace")
        
        # Border radius
        border_radius = special.get("border_radius", "4px")
        self.border_radius.setText(border_radius)
    
    def update_json_preview(self):
        """Update the JSON preview with current theme data"""
        if not self.current_theme_data:
            return
        
        # Format JSON with indentation
        formatted_json = json.dumps(self.current_theme_data, indent=4)
        self.json_preview.setText(formatted_json)
    
    def gather_theme_data(self):
        """Gather theme data from UI components"""
        if not self.current_theme_data:
            return None
        
        # Create a copy of the current theme data
        theme_data = self.current_theme_data.copy()
        
        # Ensure colors dictionary exists
        if "colors" not in theme_data:
            theme_data["colors"] = {}
        
        # Update window colors
        if "window" not in theme_data["colors"]:
            theme_data["colors"]["window"] = {}
            
        theme_data["colors"]["window"]["background"] = self.color_buttons["window_background"].color
        theme_data["colors"]["window"]["text"] = self.color_buttons["window_text"].color
        
        # Update sidebar colors
        if "sidebar" not in theme_data["colors"]:
            theme_data["colors"]["sidebar"] = {}
            
        theme_data["colors"]["sidebar"]["background"] = self.color_buttons["sidebar_background"].color
        theme_data["colors"]["sidebar"]["border"] = self.color_buttons["sidebar_border"].color
        theme_data["colors"]["sidebar"]["section_label"] = self.color_buttons["sidebar_section_label"].color
        
        # Update button colors
        if "button" not in theme_data["colors"]:
            theme_data["colors"]["button"] = {}
            
        theme_data["colors"]["button"]["background"] = self.color_buttons["button_background"].color
        theme_data["colors"]["button"]["text"] = self.color_buttons["button_text"].color
        theme_data["colors"]["button"]["hover_background"] = self.color_buttons["button_hover_background"].color
        theme_data["colors"]["button"]["checked_background"] = self.color_buttons["button_checked_background"].color
        theme_data["colors"]["button"]["checked_text"] = self.color_buttons["button_checked_text"].color
        theme_data["colors"]["button"]["disabled_background"] = self.color_buttons["button_disabled_background"].color
        theme_data["colors"]["button"]["disabled_text"] = self.color_buttons["button_disabled_text"].color
        
        # Update input colors
        if "input" not in theme_data["colors"]:
            theme_data["colors"]["input"] = {}
            
        theme_data["colors"]["input"]["background"] = self.color_buttons["input_background"].color
        theme_data["colors"]["input"]["border"] = self.color_buttons["input_border"].color
        theme_data["colors"]["input"]["text"] = self.color_buttons["input_text"].color
        
        # Update table colors
        if "table" not in theme_data["colors"]:
            theme_data["colors"]["table"] = {}
            
        theme_data["colors"]["table"]["background"] = self.color_buttons["table_background"].color
        theme_data["colors"]["table"]["alternate_background"] = self.color_buttons["table_alternate_background"].color
        theme_data["colors"]["table"]["border"] = self.color_buttons["table_border"].color
        theme_data["colors"]["table"]["header_background"] = self.color_buttons["table_header_background"].color
        theme_data["colors"]["table"]["header_text"] = self.color_buttons["table_header_text"].color
        theme_data["colors"]["table"]["selected_background"] = self.color_buttons["table_selected_background"].color
        theme_data["colors"]["table"]["selected_text"] = self.color_buttons["table_selected_text"].color
        
        # Update special settings
        if "special" not in theme_data:
            theme_data["special"] = {}
        
        # Font family
        if self.font_family.currentText() != "Default":
            theme_data["special"]["font_family"] = self.font_family.currentText().lower()
        else:
            # Remove font_family if it exists
            if "font_family" in theme_data["special"]:
                del theme_data["special"]["font_family"]
        
        # Override with monospace if checkbox is checked
        if self.monospace_checkbox.isChecked():
            theme_data["special"]["font_family"] = "monospace"
        
        # Border radius
        border_radius = self.border_radius.text().strip()
        if border_radius:
            theme_data["special"]["border_radius"] = border_radius
        else:
            theme_data["special"]["border_radius"] = "4px"  # Default
        
        return theme_data
    
    def save_theme(self):
        """Save the current theme"""
        theme_name = self.theme_selector.currentText()
        if not theme_name:
            self.show_error("No theme selected")
            return
        
        # Gather theme data
        theme_data = self.gather_theme_data()
        if not theme_data:
            self.show_error("Failed to gather theme data")
            return
        
        # Update theme
        self.theme_loader.save_theme(theme_name, theme_data)
        QMessageBox.information(self, "Theme Saved", f"Theme '{theme_name}' has been saved successfully.")
    
    def apply_theme(self):
        """Apply the current theme"""
        theme_name = self.theme_selector.currentText()
        if not theme_name:
            self.show_error("No theme selected")
            return
        
        # Apply theme
        self.theme_loader.set_current_theme(theme_name)
        QMessageBox.information(self, "Theme Applied", f"Theme '{theme_name}' has been applied successfully.")
    
    def export_theme(self):
        """Export the current theme to a file"""
        theme_name = self.theme_selector.currentText()
        if not theme_name:
            self.show_error("No theme selected")
            return
        
        # Gather theme data
        theme_data = self.gather_theme_data()
        if not theme_data:
            self.show_error("Failed to gather theme data")
            return
        
        # Get export path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Theme",
            f"{theme_name}.json",
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        # Save to file
        try:
            with open(file_path, 'w') as f:
                json.dump(theme_data, f, indent=4)
            QMessageBox.information(self, "Theme Exported", f"Theme '{theme_name}' has been exported to {file_path}")
        except Exception as e:
            self.show_error(f"Error exporting theme: {str(e)}")
    
    def import_theme(self):
        """Import a theme from a file"""
        # Get import path
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Theme",
            "",
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        # Load from file
        try:
            with open(file_path, 'r') as f:
                theme_data = json.load(f)
            
            # Extract theme name from file or data
            if "name" in theme_data:
                theme_name = theme_data["name"]
            else:
                # Use file name without extension
                import os
                theme_name = os.path.splitext(os.path.basename(file_path))[0]
                theme_data["name"] = theme_name
            
            # Save the theme
            self.theme_loader.save_theme(theme_name, theme_data)
            QMessageBox.information(
                self, 
                "Theme Imported", 
                f"Theme '{theme_name}' has been imported successfully."
            )
            
            # Reload available themes
            self.load_available_themes()
            
            # Select the imported theme
            index = self.theme_selector.findText(theme_name)
            if index >= 0:
                self.theme_selector.setCurrentIndex(index)
                self.load_theme()
            
        except Exception as e:
            self.show_error(f"Error importing theme: {str(e)}")
    
    def delete_theme(self):
        """Delete the current theme"""
        theme_name = self.theme_selector.currentText()
        if not theme_name:
            self.show_error("No theme selected")
            return
            
        # Don't allow deleting built-in themes
        if theme_name in ["dark", "light", "hacker", "obsidian"]:
            self.show_error("Cannot delete built-in themes")
            return
        
        # Confirm deletion
        result = QMessageBox.question(
            self,
            "Delete Theme",
            f"Are you sure you want to delete the theme '{theme_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if result == QMessageBox.StandardButton.Yes:
            # Delete theme
            success = self.theme_loader.delete_theme(theme_name)
            if success:
                QMessageBox.information(self, "Theme Deleted", f"Theme '{theme_name}' has been deleted.")
                
                # Reload available themes
                self.load_available_themes()
                
                # Load the current theme
                self.load_theme()
    
    def show_error(self, message):
        """Display an error message"""
        QMessageBox.critical(self, "Error", message)
