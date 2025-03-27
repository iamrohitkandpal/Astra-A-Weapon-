"""
Main window implementation for Astra
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                            QPushButton, QLabel, QStackedWidget, QFrame,
                            QComboBox, QSizePolicy, QStatusBar)
from PyQt6.QtCore import Qt, QSize, pyqtSlot
from PyQt6.QtGui import QIcon, QFont

from ui.pages.dashboard import DashboardPage
from ui.pages.settings import SettingsPage
from ui.pages.port_scanner_page import PortScannerPage
from ui.pages.dns_analyzer_page import DNSAnalyzerPage
from ui.pages.subdomain_enum_page import SubdomainEnumPage
from ui.pages.web_vulnerability_page import WebVulnerabilityPage
from ui.pages.ssl_checker_page import SSLCheckerPage
from ui.pages.theme_editor_page import ThemeEditorPage
from ui.pages.help_page import HelpPage
# Import new pages
from ui.pages.network_mapper_page import NetworkMapperPage
from ui.pages.web_crawler_page import WebCrawlerPage
from ui.pages.password_tools_page import PasswordToolsPage

from utils.theme_loader import ThemeLoader
from utils.proxy_manager import ProxyManager
from utils.memory_optimizer import get_memory_usage, cleanup_resources

class MainWindow(QMainWindow):
    """Main application window with sidebar navigation"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # Initialize theme loader
        self.theme_loader = ThemeLoader()
        
        # Initialize proxy manager
        self.proxy_manager = ProxyManager()
        
        # Connect theme loader signals
        self.theme_loader.theme_changed.connect(self.on_theme_changed)
        
        # Connect proxy manager signals
        self.proxy_manager.status_update.connect(self.update_status_message)
        self.proxy_manager.proxy_changed.connect(self.on_proxy_changed)
        
        # Set window properties
        self.setWindowTitle("Astra - Ethical Hacking Toolkit")
        self.setMinimumSize(1000, 700)
        
        # Setup UI components
        self.setup_ui()
        
        # Apply theme
        current_theme = self.config.get('theme', 'dark')
        self.apply_theme(current_theme)
        
        # Initialize proxy from config
        self.init_proxy_from_config()
        
    def setup_ui(self):
        """Setup the user interface components"""
        # Main widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(central_widget)
        
        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setMaximumWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 20)
        sidebar_layout.setSpacing(8)
        
        # App title in sidebar
        app_title = QLabel("ASTRA")
        app_title.setObjectName("appTitle")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        sidebar_layout.addWidget(app_title)
        
        # Add spacing
        sidebar_layout.addSpacing(30)
        
        # Menu sections
        # Dashboard section
        dashboard_label = QLabel("MAIN")
        dashboard_label.setObjectName("sidebarSectionLabel")
        dashboard_label.setFont(QFont("Arial", 9))
        sidebar_layout.addWidget(dashboard_label)
        
        self.dashboard_btn = self.create_sidebar_button("Dashboard", "dashboard")
        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addSpacing(15)
        
        # Network Tools section
        network_label = QLabel("NETWORK TOOLS")
        network_label.setObjectName("sidebarSectionLabel")
        network_label.setFont(QFont("Arial", 9))
        sidebar_layout.addWidget(network_label)
        
        self.port_scanner_btn = self.create_sidebar_button("Port Scanner", "portScanner")
        self.dns_analyzer_btn = self.create_sidebar_button("DNS Analyzer", "dnsAnalyzer")
        self.subdomain_btn = self.create_sidebar_button("Subdomain Enum", "subdomain")
        self.network_mapper_btn = self.create_sidebar_button("Network Mapper", "networkMapper")
        
        sidebar_layout.addWidget(self.port_scanner_btn)
        sidebar_layout.addWidget(self.dns_analyzer_btn)
        sidebar_layout.addWidget(self.subdomain_btn)
        sidebar_layout.addWidget(self.network_mapper_btn)
        sidebar_layout.addSpacing(15)
        
        # Web Tools section
        web_label = QLabel("WEB TOOLS")
        web_label.setObjectName("sidebarSectionLabel")
        web_label.setFont(QFont("Arial", 9))
        sidebar_layout.addWidget(web_label)
        
        self.web_vulnerability_btn = self.create_sidebar_button("Vulnerability Scanner", "webVulnerability")
        self.ssl_checker_btn = self.create_sidebar_button("SSL/TLS Checker", "sslChecker")
        self.web_crawler_btn = self.create_sidebar_button("Web Crawler", "webCrawler")
        
        sidebar_layout.addWidget(self.web_vulnerability_btn)
        sidebar_layout.addWidget(self.ssl_checker_btn)
        sidebar_layout.addWidget(self.web_crawler_btn)
        sidebar_layout.addSpacing(15)
        
        # Password Tools section
        password_label = QLabel("PASSWORD TOOLS")
        password_label.setObjectName("sidebarSectionLabel")
        password_label.setFont(QFont("Arial", 9))
        sidebar_layout.addWidget(password_label)
        
        self.password_tools_btn = self.create_sidebar_button("Password Tools", "passwordTools")
        sidebar_layout.addWidget(self.password_tools_btn)
        
        # Add stretch to push settings to bottom
        sidebar_layout.addStretch()
        
        # Settings and customization buttons at bottom
        settings_label = QLabel("CUSTOMIZATION")
        settings_label.setObjectName("sidebarSectionLabel")
        settings_label.setFont(QFont("Arial", 9))
        sidebar_layout.addWidget(settings_label)
        
        self.settings_btn = self.create_sidebar_button("Settings", "settings")
        self.theme_editor_btn = self.create_sidebar_button("Theme Editor", "themeEditor")
        self.help_btn = self.create_sidebar_button("Help & Docs", "help")
        
        sidebar_layout.addWidget(self.settings_btn)
        sidebar_layout.addWidget(self.theme_editor_btn)
        sidebar_layout.addWidget(self.help_btn)
        
        # Version and memory info label
        version_label = QLabel("v0.2.0")
        version_label.setObjectName("versionLabel")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(version_label)
        
        # Memory usage display
        self.memory_label = QLabel("Mem: 0 MB")
        self.memory_label.setObjectName("memoryLabel")
        self.memory_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(self.memory_label)
        
        # Content area
        content_area = QFrame()
        content_area.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        # Stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        
        # Add pages
        self.dashboard_page = DashboardPage()
        self.port_scanner_page = PortScannerPage()
        self.dns_analyzer_page = DNSAnalyzerPage()
        self.subdomain_enum_page = SubdomainEnumPage()
        self.web_vulnerability_page = WebVulnerabilityPage()
        self.ssl_checker_page = SSLCheckerPage()
        self.settings_page = SettingsPage(self.theme_loader)
        self.theme_editor_page = ThemeEditorPage()
        self.help_page = HelpPage()
        
        # Add new pages (placeholders until fully implemented)
        self.network_mapper_page = NetworkMapperPage()
        self.web_crawler_page = WebCrawlerPage()
        self.password_tools_page = PasswordToolsPage()
        
        # Connect dashboard tool signals
        self.dashboard_page.open_tool.connect(self.open_tool_from_dashboard)
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.dashboard_page)         # Index 0
        self.stacked_widget.addWidget(self.port_scanner_page)      # Index 1
        self.stacked_widget.addWidget(self.dns_analyzer_page)      # Index 2
        self.stacked_widget.addWidget(self.subdomain_enum_page)    # Index 3
        self.stacked_widget.addWidget(self.web_vulnerability_page) # Index 4
        self.stacked_widget.addWidget(self.ssl_checker_page)       # Index 5
        self.stacked_widget.addWidget(self.settings_page)          # Index 6
        self.stacked_widget.addWidget(self.theme_editor_page)      # Index 7
        self.stacked_widget.addWidget(self.help_page)              # Index 8
        self.stacked_widget.addWidget(self.network_mapper_page)    # Index 9
        self.stacked_widget.addWidget(self.web_crawler_page)       # Index 10
        self.stacked_widget.addWidget(self.password_tools_page)    # Index 11
        
        content_layout.addWidget(self.stacked_widget)
        
        # Add sidebar and content to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)
        
        # Connect buttons to switch pages
        self.dashboard_btn.clicked.connect(lambda: self.change_page(0))
        self.port_scanner_btn.clicked.connect(lambda: self.change_page(1))
        self.dns_analyzer_btn.clicked.connect(lambda: self.change_page(2))
        self.subdomain_btn.clicked.connect(lambda: self.change_page(3))
        self.web_vulnerability_btn.clicked.connect(lambda: self.change_page(4))
        self.ssl_checker_btn.clicked.connect(lambda: self.change_page(5))
        self.settings_btn.clicked.connect(lambda: self.change_page(6))
        self.theme_editor_btn.clicked.connect(lambda: self.change_page(7))
        self.help_btn.clicked.connect(lambda: self.change_page(8))
        self.network_mapper_btn.clicked.connect(lambda: self.change_page(9))
        self.web_crawler_btn.clicked.connect(lambda: self.change_page(10))
        self.password_tools_btn.clicked.connect(lambda: self.change_page(11))
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Proxy indicator label in status bar
        self.proxy_indicator = QLabel("Direct Connection")
        self.status_bar.addPermanentWidget(self.proxy_indicator)
        
        # Set dashboard as default
        self.dashboard_btn.setChecked(True)
        
        # Update memory usage every 5 seconds
        from PyQt6.QtCore import QTimer
        self.memory_timer = QTimer(self)
        self.memory_timer.timeout.connect(self.update_memory_usage)
        self.memory_timer.start(5000)
        
    def create_sidebar_button(self, text, object_name):
        """Create a styled sidebar button"""
        button = QPushButton(text)
        button.setObjectName(object_name + "Button")
        button.setCheckable(True)
        button.setFixedHeight(36)
        button.setFont(QFont("Arial", 10))
        return button
    
    def open_tool_from_dashboard(self, tool_id):
        """Open a tool page when clicked from the dashboard"""
        # Map tool_id to sidebar buttons and trigger their click
        button_map = {
            "portScanner": self.port_scanner_btn,
            "dnsAnalyzer": self.dns_analyzer_btn,
            "subdomain": self.subdomain_btn,
            "networkMapper": self.network_mapper_btn,
            "webVulnerability": self.web_vulnerability_btn,
            "sslChecker": self.ssl_checker_btn,
            "webCrawler": self.web_crawler_btn,
            "passwordTools": self.password_tools_btn
        }
        
        if tool_id in button_map:
            button_map[tool_id].click()
        
    def change_page(self, index):
        """Change the current page and update button states"""
        # Clean up resources to reduce memory usage when switching pages
        cleanup_resources()
        
        self.stacked_widget.setCurrentIndex(index)
        
        # Uncheck all buttons
        buttons = [
            self.dashboard_btn, 
            self.port_scanner_btn, 
            self.dns_analyzer_btn,
            self.subdomain_btn,
            self.web_vulnerability_btn,
            self.ssl_checker_btn,
            self.settings_btn,
            self.theme_editor_btn,
            self.help_btn,
            self.network_mapper_btn,
            self.web_crawler_btn,
            self.password_tools_btn
        ]
        
        for button in buttons:
            button.setChecked(False)
        
        # Check the active button based on index
        if index < len(buttons):
            buttons[index].setChecked(True)
            
        # Update memory usage after page change
        self.update_memory_usage()
    
    def apply_theme(self, theme_name):
        """Apply theme using the ThemeLoader"""
        theme_data = self.theme_loader.get_theme(theme_name)
        stylesheet = self.theme_loader.generate_stylesheet(theme_data)
        self.setStyleSheet(stylesheet)
        
        # Save to config
        self.config['theme'] = theme_name
        from utils.config_loader import save_config
        save_config(self.config)
    
    def on_theme_changed(self, theme_name, theme_data):
        """Handle theme change signal from ThemeLoader"""
        stylesheet = self.theme_loader.generate_stylesheet(theme_data)
        self.setStyleSheet(stylesheet)
        
        # Save to config
        self.config['theme'] = theme_name
        from utils.config_loader import save_config
        save_config(self.config)
    
    def init_proxy_from_config(self):
        """Initialize proxy settings from config file"""
        proxy_config = self.config.get('proxy', {})
        proxy_type = proxy_config.get('type', 'direct')
        
        if proxy_type == 'direct':
            self.proxy_manager.setup_direct_connection()
            
        elif proxy_type == 'manual':
            proxy_host = proxy_config.get('host', '')
            proxy_port = proxy_config.get('port', 8080)
            proxy_protocol = proxy_config.get('proxy_type', 'http')
            
            if proxy_config.get('requires_auth', False):
                username = proxy_config.get('username', '')
                password = proxy_config.get('password', '')
                self.proxy_manager.setup_manual_proxy(
                    proxy_protocol, proxy_host, proxy_port, username, password
                )
            else:
                self.proxy_manager.setup_manual_proxy(
                    proxy_protocol, proxy_host, proxy_port
                )
                
        elif proxy_type == 'tor':
            # Start Tor if configured to use it
            self.proxy_manager.start_tor()
    
    @pyqtSlot(str)
    def update_status_message(self, message):
        """Update status bar with message"""
        self.status_bar.showMessage(message, 5000)  # Show for 5 seconds
    
    @pyqtSlot(str)
    def on_proxy_changed(self, proxy_type):
        """Handle proxy change events"""
        if proxy_type == "direct":
            self.proxy_indicator.setText("Direct Connection")
            self.proxy_indicator.setStyleSheet("color: green;")
        elif proxy_type == "manual":
            proxy_protocol = self.proxy_manager.proxy_type.upper()
            self.proxy_indicator.setText(f"{proxy_protocol} Proxy")
            self.proxy_indicator.setStyleSheet("color: orange;")
        elif proxy_type == "tor":
            self.proxy_indicator.setText("Tor Network")
            self.proxy_indicator.setStyleSheet("color: #AB47BC;")  # Purple color
    
    def update_memory_usage(self):
        """Update the memory usage display"""
        memory_info = get_memory_usage()
        rss_mb = memory_info['rss']
        self.memory_label.setText(f"Mem: {rss_mb:.1f} MB")
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Cleanup proxy settings
        self.proxy_manager.cleanup()
        
        # Clean up resources
        cleanup_resources()
        
        # Accept the close event
        event.accept()
