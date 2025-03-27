"""
Settings page for Astra application
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox,
                           QHBoxLayout, QGroupBox, QPushButton, QFileDialog,
                           QTabWidget, QLineEdit, QCheckBox, QSpinBox, 
                           QMessageBox, QFrame, QRadioButton, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QIcon

from utils.proxy_manager import ProxyManager
from ui.controllers.theme_controller import ThemeController

class SettingsPage(QWidget):
    """Settings page for configuring application preferences"""
    
    def __init__(self, theme_loader):
        super().__init__()
        self.theme_loader = theme_loader
        self.proxy_manager = ProxyManager()
        self.theme_controller = ThemeController()
        
        # Connect proxy manager signals
        self.proxy_manager.status_update.connect(self.update_proxy_status)
        self.proxy_manager.error_occurred.connect(self.show_proxy_error)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the settings UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Settings")
        header_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Create tab widget
        self.settings_tabs = QTabWidget()
        
        # Create tabs
        general_tab = self.setup_general_tab()
        proxy_tab = self.setup_proxy_tab()
        advanced_tab = self.setup_advanced_tab()
        
        # Add tabs to the tab widget
        self.settings_tabs.addTab(general_tab, "General")
        self.settings_tabs.addTab(proxy_tab, "Proxy Settings")
        self.settings_tabs.addTab(advanced_tab, "Advanced")
        
        layout.addWidget(self.settings_tabs)
        
        # Save button
        self.save_button = QPushButton("Save Settings")
        self.save_button.setFixedWidth(150)
        self.save_button.clicked.connect(self.save_settings)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
    
    def setup_general_tab(self):
        """Setup the general settings tab"""
        general_tab = QWidget()
        tab_layout = QVBoxLayout(general_tab)
        
        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout(appearance_group)
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        
        # Add available themes
        available_themes = self.theme_loader.get_available_themes()
        self.theme_combo.addItems(available_themes)
        
        # Set current theme
        current_theme = self.theme_loader.get_current_theme_name()
        current_index = available_themes.index(current_theme)
        self.theme_combo.setCurrentIndex(current_index)
        
        # Connect theme change signal
        self.theme_combo.currentTextChanged.connect(self.theme_loader.set_current_theme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        
        appearance_layout.addLayout(theme_layout)
        tab_layout.addWidget(appearance_group)
        
        # General settings group
        general_group = QGroupBox("File Locations")
        general_layout = QVBoxLayout(general_group)
        
        # Add more settings here as needed
        save_reports_layout = QHBoxLayout()
        save_reports_label = QLabel("Save Reports Location:")
        self.save_reports_path = QLineEdit("reports")
        save_reports_button = QPushButton("Browse")
        save_reports_button.clicked.connect(self.browse_reports_path)
        
        save_reports_layout.addWidget(save_reports_label)
        save_reports_layout.addWidget(self.save_reports_path)
        save_reports_layout.addWidget(save_reports_button)
        
        general_layout.addLayout(save_reports_layout)
        tab_layout.addWidget(general_group)
        
        # Add theme settings group
        theme_group = QGroupBox("Theme Settings")
        theme_layout = QVBoxLayout(theme_group)
        
        # Theme selector
        theme_selector_layout = QHBoxLayout()
        theme_label = QLabel("Application Theme:")
        self.theme_selector = QComboBox()
        self.load_available_themes()
        
        theme_selector_layout.addWidget(theme_label)
        theme_selector_layout.addWidget(self.theme_selector)
        
        # Theme buttons
        theme_buttons_layout = QHBoxLayout()
        self.apply_theme_button = QPushButton("Apply Theme")
        self.apply_theme_button.clicked.connect(self.apply_selected_theme)
        
        self.edit_theme_button = QPushButton("Edit Theme")
        self.edit_theme_button.clicked.connect(self.open_theme_editor)
        
        theme_buttons_layout.addWidget(self.apply_theme_button)
        theme_buttons_layout.addWidget(self.edit_theme_button)
        theme_buttons_layout.addStretch()
        
        # Auto-detect theme checkbox
        self.auto_detect_theme = QCheckBox("Auto-detect system theme (light/dark)")
        self.auto_detect_theme.setChecked(self.theme_controller.is_auto_detect_enabled())
        self.auto_detect_theme.toggled.connect(self.toggle_auto_detect_theme)
        
        # Add to theme layout
        theme_layout.addLayout(theme_selector_layout)
        theme_layout.addLayout(theme_buttons_layout)
        theme_layout.addWidget(self.auto_detect_theme)
        
        # Add to tab layout
        tab_layout.addWidget(theme_group)
        
        # Add a stretch to push widgets to the top
        tab_layout.addStretch()
        
        return general_tab
    
    def setup_proxy_tab(self):
        """Setup the proxy settings tab"""
        proxy_tab = QWidget()
        tab_layout = QVBoxLayout(proxy_tab)
        
        # Proxy settings group
        proxy_group = QGroupBox("Proxy Configuration")
        proxy_layout = QVBoxLayout(proxy_group)
        
        # Proxy connection type
        self.direct_radio = QRadioButton("Direct Connection (No Proxy)")
        self.direct_radio.setChecked(True)
        self.manual_radio = QRadioButton("Manual Proxy Configuration")
        self.tor_radio = QRadioButton("Use Tor Network")
        
        # Connect radio buttons
        self.direct_radio.toggled.connect(self.toggle_proxy_settings)
        self.manual_radio.toggled.connect(self.toggle_proxy_settings)
        self.tor_radio.toggled.connect(self.toggle_proxy_settings)
        
        proxy_layout.addWidget(self.direct_radio)
        proxy_layout.addWidget(self.manual_radio)
        proxy_layout.addWidget(self.tor_radio)
        
        # Manual proxy settings
        self.manual_settings_frame = QFrame()
        manual_layout = QGridLayout(self.manual_settings_frame)
        
        # Proxy type
        manual_layout.addWidget(QLabel("Proxy Type:"), 0, 0)
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(["HTTP", "SOCKS4", "SOCKS5"])
        manual_layout.addWidget(self.proxy_type_combo, 0, 1, 1, 2)
        
        # Proxy host and port
        manual_layout.addWidget(QLabel("Host:"), 1, 0)
        self.proxy_host = QLineEdit()
        manual_layout.addWidget(self.proxy_host, 1, 1, 1, 2)
        
        manual_layout.addWidget(QLabel("Port:"), 2, 0)
        self.proxy_port = QSpinBox()
        self.proxy_port.setRange(1, 65535)
        self.proxy_port.setValue(8080)
        manual_layout.addWidget(self.proxy_port, 2, 1, 1, 2)
        
        # Authentication
        self.proxy_auth_checkbox = QCheckBox("Requires Authentication")
        manual_layout.addWidget(self.proxy_auth_checkbox, 3, 0, 1, 3)
        
        self.proxy_auth_frame = QFrame()
        auth_layout = QGridLayout(self.proxy_auth_frame)
        
        auth_layout.addWidget(QLabel("Username:"), 0, 0)
        self.proxy_username = QLineEdit()
        auth_layout.addWidget(self.proxy_username, 0, 1)
        
        auth_layout.addWidget(QLabel("Password:"), 1, 0)
        self.proxy_password = QLineEdit()
        self.proxy_password.setEchoMode(QLineEdit.EchoMode.Password)
        auth_layout.addWidget(self.proxy_password, 1, 1)
        
        manual_layout.addWidget(self.proxy_auth_frame, 4, 0, 1, 3)
        self.proxy_auth_frame.setVisible(False)
        self.proxy_auth_checkbox.toggled.connect(self.toggle_auth_settings)
        
        proxy_layout.addWidget(self.manual_settings_frame)
        self.manual_settings_frame.setVisible(False)
        
        # Tor settings
        self.tor_settings_frame = QFrame()
        tor_layout = QVBoxLayout(self.tor_settings_frame)
        
        # Tor controls
        tor_control_layout = QHBoxLayout()
        self.start_tor_button = QPushButton("Start Tor")
        self.start_tor_button.clicked.connect(self.start_tor)
        self.new_identity_button = QPushButton("New Identity")
        self.new_identity_button.clicked.connect(self.renew_tor_identity)
        self.new_identity_button.setEnabled(False)
        
        tor_control_layout.addWidget(self.start_tor_button)
        tor_control_layout.addWidget(self.new_identity_button)
        tor_control_layout.addStretch()
        
        tor_layout.addLayout(tor_control_layout)
        
        # Tor status
        tor_status_layout = QHBoxLayout()
        tor_status_layout.addWidget(QLabel("Status:"))
        self.tor_status_label = QLabel("Not running")
        tor_status_layout.addWidget(self.tor_status_label)
        tor_status_layout.addStretch()
        
        tor_layout.addLayout(tor_status_layout)
        
        proxy_layout.addWidget(self.tor_settings_frame)
        self.tor_settings_frame.setVisible(False)
        
        # Apply button
        apply_layout = QHBoxLayout()
        self.apply_proxy_button = QPushButton("Apply Proxy Settings")
        self.apply_proxy_button.clicked.connect(self.apply_proxy_settings)
        apply_layout.addStretch()
        apply_layout.addWidget(self.apply_proxy_button)
        
        proxy_layout.addLayout(apply_layout)
        
        # Status indicator
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Connection Status:"))
        self.proxy_status_label = QLabel("Direct connection (No proxy)")
        status_layout.addWidget(self.proxy_status_label)
        status_layout.addStretch()
        
        proxy_layout.addLayout(status_layout)
        
        tab_layout.addWidget(proxy_group)
        
        # Add a stretch to push widgets to the top
        tab_layout.addStretch()
        
        return proxy_tab
    
    def setup_advanced_tab(self):
        """Setup the advanced settings tab"""
        advanced_tab = QWidget()
        tab_layout = QVBoxLayout(advanced_tab)
        
        # Advanced settings group
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QVBoxLayout(advanced_group)
        
        # Enable/disable advanced options
        advanced_options_layout = QHBoxLayout()
        advanced_options_label = QLabel("Enable Advanced Tools:")
        self.advanced_options_combo = QComboBox()
        self.advanced_options_combo.addItems(["Enabled", "Disabled"])
        
        advanced_options_layout.addWidget(advanced_options_label)
        advanced_options_layout.addWidget(self.advanced_options_combo)
        advanced_options_layout.addStretch()
        
        advanced_layout.addLayout(advanced_options_layout)
        
        # Memory optimization
        memory_layout = QHBoxLayout()
        memory_label = QLabel("Memory Optimization:")
        self.memory_optimization_combo = QComboBox()
        self.memory_optimization_combo.addItems(["Normal", "Aggressive"])
        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(self.memory_optimization_combo)
        memory_layout.addStretch()
        
        advanced_layout.addLayout(memory_layout)
        
        # Threading settings
        threading_layout = QHBoxLayout()
        threading_label = QLabel("Maximum Worker Threads:")
        self.max_threads_spin = QSpinBox()
        self.max_threads_spin.setRange(1, 100)
        self.max_threads_spin.setValue(20)
        threading_layout.addWidget(threading_label)
        threading_layout.addWidget(self.max_threads_spin)
        threading_layout.addStretch()
        
        advanced_layout.addLayout(threading_layout)
        
        # Timeouts
        timeout_layout = QHBoxLayout()
        timeout_label = QLabel("Default Connection Timeout (seconds):")
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setValue(5)
        timeout_layout.addWidget(timeout_label)
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        
        advanced_layout.addLayout(timeout_layout)
        
        tab_layout.addWidget(advanced_group)
        
        # Add a stretch to push widgets to the top
        tab_layout.addStretch()
        
        return advanced_tab
    
    def toggle_proxy_settings(self):
        """Toggle visibility of proxy settings based on radio button selection"""
        self.manual_settings_frame.setVisible(self.manual_radio.isChecked())
        self.tor_settings_frame.setVisible(self.tor_radio.isChecked())
    
    def toggle_auth_settings(self, checked):
        """Toggle visibility of authentication settings"""
        self.proxy_auth_frame.setVisible(checked)
    
    def apply_proxy_settings(self):
        """Apply the current proxy settings"""
        # Stop existing Tor if it's running
        if self.proxy_manager.current_proxy == "tor":
            self.proxy_manager.stop_tor()
            self.start_tor_button.setText("Start Tor")
            self.new_identity_button.setEnabled(False)
        
        if self.direct_radio.isChecked():
            self.proxy_manager.setup_direct_connection()
        
        elif self.manual_radio.isChecked():
            host = self.proxy_host.text()
            port = self.proxy_port.value()
            
            if not host:
                QMessageBox.warning(self, "Invalid Settings", "Please enter a proxy host.")
                return
            
            proxy_type = self.proxy_type_combo.currentText().lower()
            
            username = None
            password = None
            
            if self.proxy_auth_checkbox.isChecked():
                username = self.proxy_username.text()
                password = self.proxy_password.text()
                
                if not username or not password:
                    QMessageBox.warning(self, "Invalid Settings", 
                                        "Please enter both username and password.")
                    return
            
            self.proxy_manager.setup_manual_proxy(proxy_type, host, port, username, password)
        
        elif self.tor_radio.isChecked():
            self.start_tor()
    
    def start_tor(self):
        """Start the Tor process"""
        if self.start_tor_button.text() == "Start Tor":
            # Start Tor
            if self.proxy_manager.start_tor():
                self.start_tor_button.setText("Stop Tor")
                self.new_identity_button.setEnabled(True)
                self.tor_status_label.setText("Running")
        else:
            # Stop Tor
            if self.proxy_manager.stop_tor():
                self.start_tor_button.setText("Start Tor")
                self.new_identity_button.setEnabled(False)
                self.tor_status_label.setText("Not running")
    
    def renew_tor_identity(self):
        """Request a new Tor identity"""
        self.proxy_manager.renew_tor_identity()
    
    @pyqtSlot(str)
    def update_proxy_status(self, status):
        """Update the proxy status label"""
        self.proxy_status_label.setText(status)
    
    @pyqtSlot(str)
    def show_proxy_error(self, error):
        """Show error message from proxy manager"""
        QMessageBox.critical(self, "Proxy Error", error)
    
    def browse_reports_path(self):
        """Open dialog to select reports path"""
        path = QFileDialog.getExistingDirectory(self, "Select Reports Directory")
        if path:
            self.save_reports_path.setText(path)
    
    def save_settings(self):
        """Save settings to configuration"""
        from utils.config_loader import load_config, save_config
        
        # Load current config
        config = load_config()
        
        # Update config with new settings
        config['theme'] = self.theme_combo.currentText()
        config['save_reports_path'] = self.save_reports_path.text()
        config['advanced_tools_enabled'] = self.advanced_options_combo.currentText() == "Enabled"
        
        # Add proxy settings
        config['proxy'] = {
            'type': 'direct'  # Default
        }
        
        if self.manual_radio.isChecked():
            config['proxy'] = {
                'type': 'manual',
                'proxy_type': self.proxy_type_combo.currentText().lower(),
                'host': self.proxy_host.text(),
                'port': self.proxy_port.value(),
                'requires_auth': self.proxy_auth_checkbox.isChecked(),
                'username': self.proxy_username.text() if self.proxy_auth_checkbox.isChecked() else '',
                'password': self.proxy_password.text() if self.proxy_auth_checkbox.isChecked() else ''
            }
        elif self.tor_radio.isChecked():
            config['proxy'] = {
                'type': 'tor'
            }
        
        # Add advanced settings
        config['advanced'] = {
            'memory_optimization': self.memory_optimization_combo.currentText().lower(),
            'max_threads': self.max_threads_spin.value(),
            'timeout': self.timeout_spin.value()
        }
        
        # Save config
        if save_config(config):
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")
        else:
            QMessageBox.warning(self, "Save Failed", "Failed to save settings.")
    
    def load_available_themes(self):
        """Load available themes into the selector"""
        self.theme_selector.clear()
        
        # Get available themes
        themes = self.theme_controller.get_available_themes()
        
        # Add themes to selector
        for theme in themes:
            display_name = theme.replace("custom/", "Custom: ")
            self.theme_selector.addItem(display_name, theme)
        
        # Set current theme
        current_theme = self.theme_controller.get_current_theme()
        current_name = current_theme.get("name", "").lower()
        
        # Find index of current theme
        for i in range(self.theme_selector.count()):
            theme_data = self.theme_selector.itemData(i)
            if theme_data.lower() == current_name:
                self.theme_selector.setCurrentIndex(i)
                break
    
    def apply_selected_theme(self):
        """Apply the selected theme"""
        # Get selected theme
        current_index = self.theme_selector.currentIndex()
        theme_id = self.theme_selector.itemData(current_index)
        
        # Apply theme
        if theme_id:
            self.theme_controller.set_theme(theme_id)
    
    def open_theme_editor(self):
        """Open the theme editor dialog"""
        # Open the theme editor
        self.theme_controller.open_theme_editor(self)
        
        # Reload available themes
        self.load_available_themes()
    
    def toggle_auto_detect_theme(self, checked):
        """Toggle auto-detect theme mode"""
        self.theme_controller.enable_auto_detect(checked)
        
        # Update UI if auto-detect is enabled
        if checked:
            self.theme_selector.setEnabled(False)
            self.apply_theme_button.setEnabled(False)
        else:
            self.theme_selector.setEnabled(True)
            self.apply_theme_button.setEnabled(True)
