"""
Real-time theme editor for customizing application appearance
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QComboBox, QPushButton, QColorDialog,
                           QScrollArea, QFormLayout, QCheckBox, QGroupBox,
                           QDialog, QMessageBox, QFrame, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QColor

class ColorPicker(QWidget):
    """Color picker widget with preview"""
    
    color_changed = pyqtSignal(str, QColor)
    
    def __init__(self, property_name, color_value, parent=None):
        super().__init__(parent)
        self.property_name = property_name
        self.color = QColor(color_value)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Color preview
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(24, 24)
        self.color_preview.setStyleSheet(f"background-color: {self.color.name()}; border: 1px solid #ccc;")
        
        # Color value
        self.color_value = QLineEdit(self.color.name())
        self.color_value.setFixedWidth(80)
        self.color_value.textChanged.connect(self.update_from_text)
        
        # Pick button
        self.pick_button = QPushButton("Pick")
        self.pick_button.setFixedWidth(60)
        self.pick_button.clicked.connect(self.show_color_dialog)
        
        # Add to layout
        layout.addWidget(self.color_preview)
        layout.addWidget(self.color_value)
        layout.addWidget(self.pick_button)
    
    def show_color_dialog(self):
        """Show color picker dialog"""
        color = QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.set_color(color)
    
    def update_from_text(self):
        """Update color from text input"""
        try:
            color = QColor(self.color_value.text())
            if color.isValid():
                self.set_color(color, emit_signal=True)
        except:
            # Invalid color format, ignore
            pass
    
    def set_color(self, color, emit_signal=True):
        """Set the current color"""
        self.color = color
        self.color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")
        self.color_value.setText(color.name())
        
        if emit_signal:
            self.color_changed.emit(self.property_name, color)

class ThemeEditorDialog(QDialog):
    """Dialog for real-time theme customization"""
    
    theme_updated = pyqtSignal(dict)
    theme_saved = pyqtSignal(dict, str)
    
    def __init__(self, theme_data, parent=None):
        super().__init__(parent)
        self.theme_data = theme_data.copy()
        self.original_theme = theme_data.copy()
        self.color_pickers = {}
        self.preview_widgets = []
        
        self.setup_ui()
        self.setWindowTitle("Theme Editor")
        self.resize(800, 600)
    
    def setup_ui(self):
        """Setup the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Create a splitter for editor and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        
        # Theme name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Theme Name:")
        self.name_input = QLineEdit(self.theme_data.get("name", "Custom Theme"))
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        
        editor_layout.addLayout(name_layout)
        
        # Scroll area for color pickers
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QFormLayout(scroll_content)
        
        # Add color pickers for all color properties
        for property_name, value in self.theme_data.items():
            if isinstance(value, str) and value.startswith("#"):
                picker = ColorPicker(property_name, value)
                picker.color_changed.connect(self.update_theme_property)
                scroll_layout.addRow(property_name.replace("_", " ").title() + ":", picker)
                self.color_pickers[property_name] = picker
        
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        editor_layout.addWidget(scroll_area)
        
        # Right side - Preview
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        preview_label = QLabel("Live Preview")
        preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(preview_label)
        
        # Preview container
        preview_container = QWidget()
        preview_container_layout = QVBoxLayout(preview_container)
        
        # Add preview widgets
        self.add_preview_widgets(preview_container_layout)
        
        preview_layout.addWidget(preview_container)
        
        # Add widgets to splitter
        splitter.addWidget(editor_widget)
        splitter.addWidget(preview_widget)
        
        # Set initial sizes (40% for editor, 60% for preview)
        splitter.setSizes([320, 480])
        
        main_layout.addWidget(splitter, 1)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_theme)
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_theme)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
    
    def add_preview_widgets(self, layout):
        """Add preview widgets to show theme changes in real-time"""
        # Main window preview
        window_preview = QGroupBox("Window")
        window_layout = QVBoxLayout(window_preview)
        
        # Add a sample header
        header = QLabel("Sample Header")
        header.setStyleSheet("font-weight: bold; font-size: 16px;")
        window_layout.addWidget(header)
        
        # Add sample buttons
        buttons_layout = QHBoxLayout()
        normal_button = QPushButton("Normal Button")
        self.preview_widgets.append(normal_button)
        
        primary_button = QPushButton("Primary Action")
        primary_button.setProperty("primary", True)
        self.preview_widgets.append(primary_button)
        
        danger_button = QPushButton("Danger")
        danger_button.setProperty("danger", True)
        self.preview_widgets.append(danger_button)
        
        buttons_layout.addWidget(normal_button)
        buttons_layout.addWidget(primary_button)
        buttons_layout.addWidget(danger_button)
        window_layout.addLayout(buttons_layout)
        
        # Add sample input elements
        form_layout = QFormLayout()
        text_input = QLineEdit("Sample text input")
        self.preview_widgets.append(text_input)
        form_layout.addRow("Text Input:", text_input)
        
        combo = QComboBox()
        combo.addItems(["Option 1", "Option 2", "Option 3"])
        self.preview_widgets.append(combo)
        form_layout.addRow("Dropdown:", combo)
        
        checkbox = QCheckBox("Enable feature")
        checkbox.setChecked(True)
        self.preview_widgets.append(checkbox)
        form_layout.addRow("Checkbox:", checkbox)
        
        window_layout.addLayout(form_layout)
        
        layout.addWidget(window_preview)
        
        # Add a sample sidebar
        sidebar_preview = QGroupBox("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar_preview)
        
        sidebar_buttons = [
            QPushButton("Dashboard"),
            QPushButton("Scans"),
            QPushButton("Settings"),
            QPushButton("Help")
        ]
        
        for button in sidebar_buttons:
            button.setProperty("sidebar_button", True)
            sidebar_layout.addWidget(button)
            self.preview_widgets.append(button)
        
        sidebar_layout.addStretch()
        
        # Create a horizontal layout to contain the sidebar and content
        split_layout = QHBoxLayout()
        split_layout.addWidget(sidebar_preview)
        
        # Main content area
        content_preview = QFrame()
        content_preview.setFrameShape(QFrame.Shape.StyledPanel)
        content_preview.setMinimumWidth(300)
        content_preview.setMinimumHeight(200)
        content_preview.setProperty("content_area", True)
        split_layout.addWidget(content_preview, 1)
        self.preview_widgets.append(content_preview)
        
        layout.addLayout(split_layout)
    
    def update_theme_property(self, property_name, color):
        """Update a theme property and refresh preview"""
        self.theme_data[property_name] = color.name()
        self.update_preview()
        
        # Emit theme_updated signal
        self.theme_updated.emit(self.theme_data)
    
    def update_preview(self):
        """Update the preview widgets with current theme"""
        stylesheet = self.generate_stylesheet()
        
        # Apply to all preview widgets
        for widget in self.preview_widgets:
            widget.setStyleSheet(stylesheet)
        
        # Additional styling for specific widget types
        self.update_specific_widgets()
    
    def update_specific_widgets(self):
        """Apply specific styling to certain widget types"""
        for widget in self.preview_widgets:
            # Apply specific styling based on widget type or properties
            if isinstance(widget, QPushButton):
                if widget.property("primary"):
                    widget.setStyleSheet(f"background-color: {self.theme_data.get('primary_color', '#3498db')}; color: white;")
                elif widget.property("danger"):
                    widget.setStyleSheet(f"background-color: {self.theme_data.get('error_color', '#e74c3c')}; color: white;")
                elif widget.property("sidebar_button"):
                    widget.setStyleSheet(f"background-color: {self.theme_data.get('sidebar_background', '#1e1e1e')}; "
                                         f"color: {self.theme_data.get('text_color', '#e0e0e0')}; "
                                         f"border: none; text-align: left; padding: 8px 16px;")
            elif isinstance(widget, QFrame) and widget.property("content_area"):
                widget.setStyleSheet(f"background-color: {self.theme_data.get('card_background', '#ffffff')}; "
                                    f"border: 1px solid {self.theme_data.get('border_color', '#dddddd')};")
    
    def generate_stylesheet(self):
        """Generate a stylesheet from the current theme data"""
        bg_color = self.theme_data.get("background_color", "#f5f5f5")
        text_color = self.theme_data.get("text_color", "#333333")
        accent_color = self.theme_data.get("accent_color", "#27ae60")
        
        return f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
            }}
            
            QPushButton {{
                background-color: {self.theme_data.get("secondary_color", "#2980b9")};
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }}
            
            QPushButton:hover {{
                background-color: {self.theme_data.get("primary_color", "#3498db")};
            }}
            
            QLineEdit {{
                border: 1px solid {self.theme_data.get("border_color", "#dddddd")};
                padding: 4px;
                border-radius: 2px;
                background-color: {self.theme_data.get("card_background", "#ffffff")};
            }}
            
            QComboBox {{
                border: 1px solid {self.theme_data.get("border_color", "#dddddd")};
                padding: 4px;
                border-radius: 2px;
                background-color: {self.theme_data.get("card_background", "#ffffff")};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {accent_color};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {self.theme_data.get("border_color", "#dddddd")};
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
    
    def reset_theme(self):
        """Reset to original theme values"""
        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Reset Theme",
            "Are you sure you want to reset all changes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset theme data
            self.theme_data = self.original_theme.copy()
            
            # Update UI
            self.name_input.setText(self.theme_data.get("name", "Custom Theme"))
            
            # Update color pickers
            for property_name, value in self.theme_data.items():
                if isinstance(value, str) and value.startswith("#") and property_name in self.color_pickers:
                    self.color_pickers[property_name].set_color(QColor(value), emit_signal=False)
            
            # Update preview
            self.update_preview()
            
            # Emit theme_updated signal
            self.theme_updated.emit(self.theme_data)
    
    def save_theme(self):
        """Save the current theme and accept the dialog"""
        theme_name = self.name_input.text().strip()
        if not theme_name:
            QMessageBox.warning(self, "Invalid Name", "Please enter a valid theme name.")
            return
        
        # Update name in theme data
        self.theme_data["name"] = theme_name
        
        # Emit save signal
        self.theme_saved.emit(self.theme_data, theme_name)
        
        # Accept dialog
        self.accept()
