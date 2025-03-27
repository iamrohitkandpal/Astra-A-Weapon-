"""
Enhanced theme manager with auto-detection and real-time customization
"""
import os
import json
import platform
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal

class ThemeManager(QObject):
    """Theme manager with enhanced capabilities"""
    
    # Signal emitted when theme changes
    theme_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "themes")
        self.custom_themes_dir = os.path.join(self.themes_dir, "custom")
        self.current_theme = {}
        self.auto_detect_enabled = False
        self.current_theme_name = "default"
        
        # Ensure directories exist
        os.makedirs(self.themes_dir, exist_ok=True)
        os.makedirs(self.custom_themes_dir, exist_ok=True)
        
        # Load default themes if no themes exist
        if not os.path.exists(os.path.join(self.themes_dir, "light.json")):
            self._create_default_themes()
    
    def _create_default_themes(self):
        """Create default light and dark themes"""
        light_theme = {
            "name": "Light",
            "primary_color": "#3498db",
            "secondary_color": "#2980b9",
            "background_color": "#f5f5f5",
            "card_background": "#ffffff",
            "text_color": "#333333",
            "accent_color": "#27ae60",
            "warning_color": "#e67e22",
            "error_color": "#e74c3c",
            "success_color": "#2ecc71",
            "border_color": "#dddddd",
            "highlight_color": "#f39c12",
            "font_family": "Segoe UI, Arial, sans-serif",
            "is_dark": False
        }
        
        dark_theme = {
            "name": "Dark",
            "primary_color": "#3498db",
            "secondary_color": "#2980b9",
            "background_color": "#2c3e50",
            "card_background": "#34495e",
            "text_color": "#ecf0f1",
            "accent_color": "#27ae60",
            "warning_color": "#e67e22",
            "error_color": "#e74c3c",
            "success_color": "#2ecc71",
            "border_color": "#7f8c8d",
            "highlight_color": "#f39c12",
            "font_family": "Segoe UI, Arial, sans-serif",
            "is_dark": True
        }
        
        # Save default themes
        with open(os.path.join(self.themes_dir, "light.json"), "w") as f:
            json.dump(light_theme, f, indent=4)
        
        with open(os.path.join(self.themes_dir, "dark.json"), "w") as f:
            json.dump(dark_theme, f, indent=4)
    
    def get_available_themes(self):
        """Get list of all available themes"""
        themes = []
        # Load themes from main directory
        for file in os.listdir(self.themes_dir):
            if file.endswith(".json"):
                themes.append(os.path.splitext(file)[0])
        
        # Load custom themes
        for file in os.listdir(self.custom_themes_dir):
            if file.endswith(".json"):
                themes.append("custom/" + os.path.splitext(file)[0])
        
        return themes
    
    def load_theme(self, theme_name):
        """Load a theme by name"""
        self.auto_detect_enabled = False
        
        theme_path = ""
        if theme_name.startswith("custom/"):
            # Custom theme
            theme_path = os.path.join(self.custom_themes_dir, theme_name[7:] + ".json")
        else:
            # Standard theme
            theme_path = os.path.join(self.themes_dir, theme_name + ".json")
        
        try:
            with open(theme_path, "r") as f:
                self.current_theme = json.load(f)
                self.current_theme_name = theme_name
                self.theme_changed.emit(self.current_theme)
                return True
        except Exception as e:
            print(f"Error loading theme: {e}")
            return False
    
    def save_custom_theme(self, theme_data, name):
        """Save a custom theme"""
        if not name:
            name = "custom_theme"
            
        # Ensure the theme has a name property
        theme_data["name"] = name.title()
        
        # Save the theme
        theme_path = os.path.join(self.custom_themes_dir, name + ".json")
        try:
            with open(theme_path, "w") as f:
                json.dump(theme_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving theme: {e}")
            return False
    
    def update_theme_property(self, property_name, value):
        """Update a single property in the current theme and emit signal"""
        if property_name in self.current_theme:
            self.current_theme[property_name] = value
            self.theme_changed.emit(self.current_theme)
    
    def get_current_theme(self):
        """Get the current theme"""
        return self.current_theme
    
    def get_system_theme(self):
        """Detect if the system is using a dark theme"""
        system = platform.system()
        
        if system == "Windows":
            try:
                import winreg
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return "dark" if value == 0 else "light"
            except:
                return "light"
        
        elif system == "Darwin":  # macOS
            try:
                import subprocess
                cmd = "defaults read -g AppleInterfaceStyle"
                result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
                return "dark" if result.stdout.strip() == "Dark" else "light"
            except:
                return "light"
        
        else:  # Linux or others - simplistic approach
            app = QApplication.instance()
            if app:
                return "dark" if app.palette().color(app.palette().Window).lightness() < 128 else "light"
            return "light"
    
    def enable_auto_detect(self, enabled=True):
        """Enable or disable auto-detection of system theme"""
        self.auto_detect_enabled = enabled
        if enabled:
            system_theme = self.get_system_theme()
            self.load_theme(system_theme)
    
    def is_auto_detect_enabled(self):
        """Check if auto-detect is enabled"""
        return self.auto_detect_enabled
