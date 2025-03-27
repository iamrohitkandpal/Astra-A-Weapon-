"""
Controller for managing themes and integrating the real-time theme editor
"""
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QMessageBox

from utils.theme_manager import ThemeManager
from ui.theme_editor import ThemeEditorDialog

class ThemeController(QObject):
    """
    Controller for managing themes and providing a bridge between
    the theme manager and UI components
    """
    
    # Signal emitted when the theme changes
    theme_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager()
        
        # Connect theme manager signals
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # Load initial theme
        self._initialize_theme()
    
    def _initialize_theme(self):
        """Initialize the application theme"""
        # Get current system theme preference if auto-detect is enabled
        if self.theme_manager.is_auto_detect_enabled():
            system_theme = self.theme_manager.get_system_theme()
            self.theme_manager.load_theme(system_theme)
        else:
            # Get the current theme
            current_theme = self.theme_manager.get_current_theme()
            self.theme_changed.emit(current_theme)
    
    @pyqtSlot(dict)
    def on_theme_changed(self, theme_data):
        """Handle theme change from theme manager"""
        # Forward the signal
        self.theme_changed.emit(theme_data)
    
    def get_available_themes(self):
        """Get list of available themes"""
        return self.theme_manager.get_available_themes()
    
    def get_current_theme(self):
        """Get current theme data"""
        return self.theme_manager.get_current_theme()
    
    def set_theme(self, theme_name):
        """Set the current theme by name"""
        return self.theme_manager.load_theme(theme_name)
    
    def enable_auto_detect(self, enabled=True):
        """Enable or disable auto-detection of system theme"""
        self.theme_manager.enable_auto_detect(enabled)
    
    def is_auto_detect_enabled(self):
        """Check if auto-detect is enabled"""
        return self.theme_manager.is_auto_detect_enabled()
    
    def open_theme_editor(self, parent=None):
        """Open the theme editor dialog"""
        # Get current theme data
        current_theme = self.theme_manager.get_current_theme()
        
        # Create and show dialog
        dialog = ThemeEditorDialog(current_theme, parent)
        
        # Connect signals
        dialog.theme_updated.connect(self._on_theme_preview)
        dialog.theme_saved.connect(self._on_theme_saved)
        
        # Show dialog
        if dialog.exec():
            return True
        else:
            # Reset to current theme on cancel
            self.theme_changed.emit(current_theme)
            return False
    
    @pyqtSlot(dict)
    def _on_theme_preview(self, theme_data):
        """Handle real-time theme preview updates"""
        # Emit the updated theme for preview
        self.theme_changed.emit(theme_data)
    
    @pyqtSlot(dict, str)
    def _on_theme_saved(self, theme_data, theme_name):
        """Handle theme save from editor"""
        # Save theme to storage
        success = self.theme_manager.save_custom_theme(theme_data, theme_name)
        
        if success:
            # Apply the theme
            self.theme_manager.load_theme("custom/" + theme_name)
            
            # Show success message
            QApplication.instance().processEvents()  # Process pending events
            QMessageBox.information(
                None, 
                "Theme Saved", 
                f"Theme '{theme_name}' has been saved and applied."
            )
        else:
            # Show error message
            QMessageBox.warning(
                None, 
                "Save Failed", 
                f"Failed to save theme '{theme_name}'."
            )
