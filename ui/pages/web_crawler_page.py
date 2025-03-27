"""
Web crawler page for Astra
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, 
                            QGroupBox, QFormLayout, QSpinBox, QCheckBox, QProgressBar,
                            QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class WebCrawlerPage(QWidget):
    """Web crawler page widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Web Crawler")
        header_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Crawl websites to discover structure and content")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Input form
        input_group = QGroupBox("Crawl Parameters")
        input_layout = QFormLayout(input_group)
        
        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL (e.g., https://example.com)")
        input_layout.addRow("Starting URL:", self.url_input)
        
        # Depth input
        self.depth_input = QSpinBox()
        self.depth_input.setRange(1, 10)
        self.depth_input.setValue(3)
        input_layout.addRow("Crawl Depth:", self.depth_input)
        
        # Options
        self.respect_robots = QCheckBox("Respect robots.txt")
        self.respect_robots.setChecked(True)
        input_layout.addRow("", self.respect_robots)
        
        self.extract_emails = QCheckBox("Extract email addresses")
        self.extract_emails.setChecked(True)
        input_layout.addRow("", self.extract_emails)
        
        self.follow_external = QCheckBox("Follow external links")
        self.follow_external.setChecked(False)
        input_layout.addRow("", self.follow_external)
        
        layout.addWidget(input_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Button layout
        button_layout = QHBoxLayout()
        self.crawl_button = QPushButton("Start Crawling")
        self.crawl_button.setFixedWidth(150)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedWidth(150)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.crawl_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Results table
        self.results_table = QTableWidget(0, 3)
        self.results_table.setHorizontalHeaderLabels(["URL", "Type", "Status"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.results_table)
        
        # Status label
        self.status_label = QLabel("Ready to crawl")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Connect signals
        self.crawl_button.clicked.connect(self.start_crawling)
        self.stop_button.clicked.connect(self.stop_crawling)
    
    def start_crawling(self):
        """Start the crawling process"""
        # This is a placeholder - would be implemented with actual crawling logic
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText("Please enter a starting URL")
            return
            
        self.crawl_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(10)
        self.status_label.setText(f"Crawling: {url}...")
        
        # Add placeholder data to the table
        example_data = [
            (f"{url}", "Page", "200 OK"),
            (f"{url}/about", "Page", "200 OK"),
            (f"{url}/contact", "Page", "200 OK"),
            (f"{url}/style.css", "Resource", "200 OK"),
            (f"{url}/logo.png", "Image", "200 OK")
        ]
        
        for url, type_, status in example_data:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            self.results_table.setItem(row, 0, QTableWidgetItem(url))
            self.results_table.setItem(row, 1, QTableWidgetItem(type_))
            self.results_table.setItem(row, 2, QTableWidgetItem(status))
    
    def stop_crawling(self):
        """Stop the crawling process"""
        self.crawl_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Crawling stopped")
