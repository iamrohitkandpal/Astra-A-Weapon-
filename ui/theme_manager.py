"""
Theme manager class for handling application themes
"""

class ThemeManager:
    """Manages application themes and styles"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_theme = "dark"
        self.themes = {
            "dark": self._dark_theme(),
            "light": self._light_theme(),
            "hacker": self._hacker_theme()
        }
    
    def apply_theme(self, theme_name):
        """Apply the specified theme to the application"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.main_window.setStyleSheet(self.themes[theme_name])
            
    def get_available_themes(self):
        """Return list of available themes"""
        return list(self.themes.keys())
    
    def get_current_theme(self):
        """Return the current theme name"""
        return self.current_theme
    
    def _dark_theme(self):
        """Dark theme stylesheet"""
        return """
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
                background-color: #333333;
                alternate-background-color: #3a3a3a;
                border: 1px solid #555555;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #555555;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 3px;
                text-align: center;
                background-color: #333333;
                color: #e0e0e0;
                height: 14px;
            }
            QProgressBar::chunk {
                background-color: #0078d7;
                width: 10px;
            }
            QCheckBox {
                spacing: 5px;
                color: #e0e0e0;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #333333;
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
                color: #e0e0e0;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
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
            #versionLabel {
                color: #8a8a8a;
                font-size: 10px;
            }
        """
    
    def _light_theme(self):
        """Light theme stylesheet"""
        return """
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
            #versionLabel {
                color: #757575;
                font-size: 10px;
            }
        """
    
    def _hacker_theme(self):
        """Hacker theme stylesheet"""
        return """
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
            #versionLabel {
                color: #008800;
                font-size: 10px;
                font-family: monospace;
            }
            QLabel {
                font-family: monospace;
            }
        """
