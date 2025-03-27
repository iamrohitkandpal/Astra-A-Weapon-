"""
DNS analyzer page for Astra
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
                            QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout, QComboBox,
                            QHeaderView, QCheckBox, QMessageBox, QSizePolicy, QScrollArea)
from PyQt6.QtCore import Qt, QThread, QSize
from PyQt6.QtGui import QFont, QResizeEvent, QDragEnterEvent, QDropEvent

from core.dns_analyzer import DNSAnalyzer
from utils.report_generator import ReportGenerator

class DNSAnalyzerThread(QThread):
    """Thread for running DNS analyzer without blocking GUI"""
    
    def __init__(self, analyzer, domain, record_types):
        super().__init__()
        self.analyzer = analyzer
        self.domain = domain
        self.record_types = record_types
    
    def run(self):
        """Run the analyzer in a thread"""
        self.analyzer.analyze(self.domain, self.record_types)

class DNSAnalyzerPage(QWidget):
    """DNS analyzer page widget"""
    
    def __init__(self):
        super().__init__()
        self.analyzer = DNSAnalyzer()
        self.thread = None
        self.report_generator = ReportGenerator()
        self.query_results = []  # Store query results for reporting
        self.setup_ui()
        self.connect_signals()
        self.setAcceptDrops(True)  # Enable drag and drop
    
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("DNS Analyzer")
        header_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Analyze DNS records for a domain")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Input form
        input_group = QGroupBox("Query Parameters")
        input_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        input_layout = QFormLayout(input_group)
        
        # Domain input
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("Enter domain (e.g., example.com)")
        input_layout.addRow("Domain:", self.domain_input)
        
        # Record types
        self.record_types = {
            'A': "A (IPv4 Address)",
            'AAAA': "AAAA (IPv6 Address)",
            'MX': "MX (Mail Exchange)",
            'NS': "NS (Name Server)",
            'TXT': "TXT (Text)",
            'SOA': "SOA (Start of Authority)",
            'CNAME': "CNAME (Canonical Name)",
            'PTR': "PTR (Pointer)",
            'SRV': "SRV (Service)",
            'CAA': "CAA (Certification Authority Authorization)"
        }
        
        # Create scroll area for record type checkboxes
        checkbox_scroll = QScrollArea()
        checkbox_scroll.setWidgetResizable(True)
        checkbox_widget = QWidget()
        checkbox_layout = QVBoxLayout(checkbox_widget)
        
        # Add all checkboxes
        self.record_checkboxes = {}
        for record_type, record_label in self.record_types.items():
            checkbox = QCheckBox(record_label)
            checkbox.setChecked(record_type in ['A', 'AAAA', 'MX', 'NS', 'TXT'])
            self.record_checkboxes[record_type] = checkbox
            checkbox_layout.addWidget(checkbox)
        
        # Add select all/none buttons
        select_buttons_layout = QHBoxLayout()
        select_all_button = QPushButton("Select All")
        select_none_button = QPushButton("Select None")
        select_all_button.clicked.connect(self.select_all_record_types)
        select_none_button.clicked.connect(self.select_none_record_types)
        
        select_buttons_layout.addWidget(select_all_button)
        select_buttons_layout.addWidget(select_none_button)
        select_buttons_layout.addStretch()
        
        checkbox_layout.addLayout(select_buttons_layout)
        checkbox_scroll.setWidget(checkbox_widget)
        
        record_group = QGroupBox("Record Types")
        record_layout = QVBoxLayout(record_group)
        record_layout.addWidget(checkbox_scroll)
        
        input_layout.addRow(record_group)
        layout.addWidget(input_group)
        
        # Button layout
        button_layout = QHBoxLayout()
        self.query_button = QPushButton("Query DNS")
        self.query_button.setFixedWidth(150)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedWidth(150)
        self.stop_button.setEnabled(False)
        
        # Report generation buttons
        self.generate_pdf_button = QPushButton("Generate PDF Report")
        self.generate_pdf_button.setFixedWidth(200)
        self.generate_pdf_button.setEnabled(False)
        
        self.generate_html_button = QPushButton("Generate HTML Report")
        self.generate_html_button.setFixedWidth(200)
        self.generate_html_button.setEnabled(False)
        
        button_layout.addWidget(self.query_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.generate_pdf_button)
        button_layout.addWidget(self.generate_html_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Results table
        self.results_table = QTableWidget(0, 3)
        self.results_table.setHorizontalHeaderLabels(["Domain", "Record Type", "Value"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout.addWidget(self.results_table)
        
        # Status label
        self.status_label = QLabel("Drag and drop a domain list file to analyze multiple domains")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
    def connect_signals(self):
        """Connect signals to slots"""
        self.query_button.clicked.connect(self.start_query)
        self.stop_button.clicked.connect(self.stop_query)
        self.generate_pdf_button.clicked.connect(self.generate_pdf_report)
        self.generate_html_button.clicked.connect(self.generate_html_report)
        
        # Connect analyzer signals
        self.analyzer.result_update.connect(self.update_result)
        self.analyzer.query_completed.connect(self.query_finished)
        self.analyzer.query_error.connect(self.show_error)
    
    def select_all_record_types(self):
        """Select all record type checkboxes"""
        for checkbox in self.record_checkboxes.values():
            checkbox.setChecked(True)
    
    def select_none_record_types(self):
        """Deselect all record type checkboxes"""
        for checkbox in self.record_checkboxes.values():
            checkbox.setChecked(False)
    
    def start_query(self):
        """Start the DNS query process"""
        # Clear previous results
        self.results_table.setRowCount(0)
        self.query_results = []
        
        # Get parameters
        domain = self.domain_input.text().strip()
        if not domain:
            self.show_error("Please enter a domain name")
            return
        
        # Get selected record types
        selected_record_types = [
            record_type for record_type, checkbox in self.record_checkboxes.items()
            if checkbox.isChecked()
        ]
        
        if not selected_record_types:
            self.show_error("Please select at least one record type")
            return
        
        # Update UI
        self.query_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.generate_pdf_button.setEnabled(False)
        self.generate_html_button.setEnabled(False)
        self.status_label.setText(f"Querying {domain}...")
        
        # Start analysis in a thread
        self.thread = DNSAnalyzerThread(
            self.analyzer,
            domain,
            selected_record_types
        )
        self.thread.start()
    
    def stop_query(self):
        """Stop the query process"""
        if self.thread and self.thread.isRunning():
            self.analyzer.stop_analysis()
            self.thread.wait()
            self.query_finished()
    
    def update_result(self, domain, record_type, value):
        """Update the results table with a new query result"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Domain
        domain_item = QTableWidgetItem(domain)
        self.results_table.setItem(row, 0, domain_item)
        
        # Record Type
        record_type_item = QTableWidgetItem(record_type)
        record_type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_table.setItem(row, 1, record_type_item)
        
        # Value
        value_item = QTableWidgetItem(value)
        self.results_table.setItem(row, 2, value_item)
        
        # Store result for report generation
        self.query_results.append((domain, record_type, value))
        
        # Sort by record type
        self.results_table.sortItems(1, Qt.SortOrder.AscendingOrder)
    
    def query_finished(self):
        """Handle query completion"""
        self.query_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.generate_pdf_button.setEnabled(True)
        self.generate_html_button.setEnabled(True)
        self.status_label.setText("Query completed")
    
    def show_error(self, message):
        """Display an error message"""
        QMessageBox.critical(self, "Error", message)
        self.query_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText(f"Error: {message}")
    
    def generate_pdf_report(self):
        """Generate a PDF report from query results"""
        if not self.query_results:
            self.show_error("No query results to report")
            return
            
        domain = self.domain_input.text().strip()
        try:
            filepath = self.report_generator.generate_pdf_report(
                "DNS Analysis Results",
                self.query_results,
                "DNS Analysis",
                domain
            )
            QMessageBox.information(
                self, 
                "Report Generated", 
                f"PDF Report has been saved to:\n{filepath}"
            )
        except Exception as e:
            self.show_error(f"Error generating PDF report: {str(e)}")
    
    def generate_html_report(self):
        """Generate an HTML report from query results"""
        if not self.query_results:
            self.show_error("No query results to report")
            return
            
        domain = self.domain_input.text().strip()
        try:
            filepath = self.report_generator.generate_html_report(
                "DNS Analysis Results",
                self.query_results,
                "DNS Analysis",
                domain
            )
            QMessageBox.information(
                self, 
                "Report Generated", 
                f"HTML Report has been saved to:\n{filepath}"
            )
        except Exception as e:
            self.show_error(f"Error generating HTML report: {str(e)}")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event for file drops"""
        if event.mimeData().hasUrls():
            # Accept only .txt files
            if event.mimeData().urls()[0].toLocalFile().endswith('.txt'):
                event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event for domain list files"""
        file_path = event.mimeData().urls()[0].toLocalFile()
        try:
            with open(file_path, 'r') as f:
                domains = [line.strip() for line in f if line.strip()]
            
            if domains:
                # Take the first domain from the list
                self.domain_input.setText(domains[0])
                if len(domains) > 1:
                    self.status_label.setText(f"Loaded 1 of {len(domains)} domains from file")
                    
                    # Ask if user wants to analyze all domains
                    reply = QMessageBox.question(
                        self, 
                        "Multiple Domains", 
                        f"File contains {len(domains)} domains. Do you want to analyze them all?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # TODO: Implement batch analysis functionality
                        self.status_label.setText(f"Batch analysis not yet implemented")
            else:
                self.status_label.setText("No valid domains found in file")
        except Exception as e:
            self.status_label.setText(f"Error loading file: {str(e)}")
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle resize events to adjust the UI layout"""
        super().resizeEvent(event)
        
        # Adjust table column widths based on available space
        width = self.results_table.width()
        if width > 200:  # Only adjust if we have enough space
            self.results_table.setColumnWidth(0, int(width * 0.3))  # Domain column
            self.results_table.setColumnWidth(1, int(width * 0.2))  # Record Type column
            self.results_table.setColumnWidth(2, int(width * 0.5))  # Value column
