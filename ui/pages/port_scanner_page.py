"""
Port scanner page for Astra
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
                            QProgressBar, QTableWidget, QTableWidgetItem, QSpinBox, QGroupBox,
                            QFormLayout, QHeaderView, QMessageBox, QSizePolicy, QComboBox,
                            QFileDialog)
from PyQt6.QtCore import Qt, QThread, QSize
from PyQt6.QtGui import QFont, QColor, QResizeEvent, QDragEnterEvent, QDropEvent

from core.port_scanner import PortScanner
from utils.report_generator import ReportGenerator

class ScannerThread(QThread):
    """Thread for running port scanner without blocking GUI"""
    
    def __init__(self, scanner, target, port_range, timeout):
        super().__init__()
        self.scanner = scanner
        self.target = target
        self.port_range = port_range
        self.timeout = timeout
    
    def run(self):
        """Run the scanner in a thread"""
        self.scanner.scan(self.target, self.port_range, timeout=self.timeout)

class PortScannerPage(QWidget):
    """Port scanner page widget"""
    
    def __init__(self):
        super().__init__()
        self.scanner = PortScanner()
        self.thread = None
        self.report_generator = ReportGenerator()
        self.scan_results = []  # Store scan results for reporting
        self.setup_ui()
        self.connect_signals()
        self.setAcceptDrops(True)  # Enable drag and drop
    
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Port Scanner")
        header_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Scan for open ports on target systems")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Input form
        input_group = QGroupBox("Scan Parameters")
        input_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        input_layout = QFormLayout(input_group)
        
        # Target input
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter hostname or IP (e.g., example.com or 192.168.1.1)")
        input_layout.addRow("Target:", self.target_input)
        
        # Port range
        port_range_layout = QHBoxLayout()
        self.start_port_input = QSpinBox()
        self.start_port_input.setRange(1, 65535)
        self.start_port_input.setValue(1)
        self.end_port_input = QSpinBox()
        self.end_port_input.setRange(1, 65535)
        self.end_port_input.setValue(1000)
        port_range_layout.addWidget(self.start_port_input)
        port_range_layout.addWidget(QLabel("-"))
        port_range_layout.addWidget(self.end_port_input)
        input_layout.addRow("Port Range:", port_range_layout)
        
        # Scan method
        self.scan_method_combo = QComboBox()
        self.scan_method_combo.addItems(["Asyncio (Faster)", "Threading (More Compatible)"])
        input_layout.addRow("Scan Method:", self.scan_method_combo)
        
        # Timeout
        self.timeout_input = QSpinBox()
        self.timeout_input.setRange(1, 10)
        self.timeout_input.setValue(1)
        self.timeout_input.setSuffix(" sec")
        input_layout.addRow("Timeout:", self.timeout_input)
        
        layout.addWidget(input_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Button layout
        button_layout = QHBoxLayout()
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.setFixedWidth(150)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedWidth(150)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.scan_button)
        button_layout.addWidget(self.stop_button)
        
        # Add report generation buttons
        self.generate_pdf_button = QPushButton("Generate PDF Report")
        self.generate_pdf_button.setFixedWidth(200)
        self.generate_pdf_button.setEnabled(False)
        self.generate_html_button = QPushButton("Generate HTML Report")
        self.generate_html_button.setFixedWidth(200)
        self.generate_html_button.setEnabled(False)
        
        button_layout.addWidget(self.generate_pdf_button)
        button_layout.addWidget(self.generate_html_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Results table
        self.results_table = QTableWidget(0, 3)
        self.results_table.setHorizontalHeaderLabels(["Port", "Status", "Service"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout.addWidget(self.results_table)
        
        # Status label
        self.status_label = QLabel("Drag and drop a target list file to scan multiple hosts")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
    def connect_signals(self):
        """Connect signals to slots"""
        self.scan_button.clicked.connect(self.start_scan)
        self.stop_button.clicked.connect(self.stop_scan)
        self.generate_pdf_button.clicked.connect(self.generate_pdf_report)
        self.generate_html_button.clicked.connect(self.generate_html_report)
        self.scan_method_combo.currentIndexChanged.connect(self.update_scan_method)
        
        # Connect scanner signals
        self.scanner.progress_update.connect(self.update_progress)
        self.scanner.result_update.connect(self.update_result)
        self.scanner.scan_completed.connect(self.scan_finished)
        self.scanner.scan_error.connect(self.show_error)
    
    def update_scan_method(self, index):
        """Update scanner method based on combobox selection"""
        if index == 0:
            self.scanner.set_scan_method("asyncio")
        else:
            self.scanner.set_scan_method("threading")
    
    def start_scan(self):
        """Start the port scanning process"""
        # Clear previous results
        self.results_table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.scan_results = []
        
        # Get parameters
        target = self.target_input.text().strip()
        if not target:
            self.show_error("Please enter a target hostname or IP address")
            return
        
        start_port = self.start_port_input.value()
        end_port = self.end_port_input.value()
        timeout = self.timeout_input.value()
        
        # Validate port range
        if start_port > end_port:
            self.show_error("Start port must be less than or equal to end port")
            return
        
        # Update UI
        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.generate_pdf_button.setEnabled(False)
        self.generate_html_button.setEnabled(False)
        self.status_label.setText(f"Scanning {target}...")
        
        # Start scanning in a thread
        self.thread = ScannerThread(
            self.scanner,
            target,
            (start_port, end_port),
            timeout
        )
        self.thread.start()
    
    def stop_scan(self):
        """Stop the scanning process"""
        if self.thread and self.thread.isRunning():
            self.scanner.stop_scan()
            self.thread.wait()
            self.scan_finished()
    
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_bar.setValue(value)
    
    def update_result(self, port, is_open, service):
        """Update the results table with a new scan result"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Port
        port_item = QTableWidgetItem(str(port))
        port_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_table.setItem(row, 0, port_item)
        
        # Status
        status_text = "Open" if is_open else "Closed"
        status_item = QTableWidgetItem(status_text)
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Set color based on status
        if is_open:
            status_item.setForeground(QColor(0, 170, 0))  # Green for open
        else:
            status_item.setForeground(QColor(200, 0, 0))  # Red for closed
            
        self.results_table.setItem(row, 1, status_item)
        
        # Service
        service_item = QTableWidgetItem(service)
        service_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_table.setItem(row, 2, service_item)
        
        # Store the result for reporting
        self.scan_results.append((str(port), status_text, service))
        
        # Sort by port number
        self.results_table.sortItems(0, Qt.SortOrder.AscendingOrder)
    
    def scan_finished(self):
        """Handle scan completion"""
        self.progress_bar.setValue(100)
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.generate_pdf_button.setEnabled(True)
        self.generate_html_button.setEnabled(True)
        self.status_label.setText("Scan completed")
    
    def show_error(self, message):
        """Display an error message"""
        QMessageBox.critical(self, "Error", message)
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText(f"Error: {message}")
    
    def generate_pdf_report(self):
        """Generate a PDF report from scan results"""
        if not self.scan_results:
            self.show_error("No scan results to report")
            return
            
        target = self.target_input.text().strip()
        try:
            filepath = self.report_generator.generate_pdf_report(
                "Port Scan Results",
                self.scan_results,
                "Port Scan",
                target
            )
            QMessageBox.information(
                self, 
                "Report Generated", 
                f"PDF Report has been saved to:\n{filepath}"
            )
        except Exception as e:
            self.show_error(f"Error generating PDF report: {str(e)}")
    
    def generate_html_report(self):
        """Generate an HTML report from scan results"""
        if not self.scan_results:
            self.show_error("No scan results to report")
            return
            
        target = self.target_input.text().strip()
        try:
            filepath = self.report_generator.generate_html_report(
                "Port Scan Results",
                self.scan_results,
                "Port Scan",
                target
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
        """Handle drop event for target list files"""
        file_path = event.mimeData().urls()[0].toLocalFile()
        try:
            with open(file_path, 'r') as f:
                targets = [line.strip() for line in f if line.strip()]
            
            if targets:
                # Take the first target from the list
                self.target_input.setText(targets[0])
                if len(targets) > 1:
                    self.status_label.setText(f"Loaded 1 of {len(targets)} targets from file")
                    
                    # Ask if user wants to scan all targets
                    reply = QMessageBox.question(
                        self, 
                        "Multiple Targets", 
                        f"File contains {len(targets)} targets. Do you want to scan them all?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # TODO: Implement batch scanning functionality
                        self.status_label.setText(f"Batch scanning not yet implemented")
            else:
                self.status_label.setText("No valid targets found in file")
        except Exception as e:
            self.status_label.setText(f"Error loading file: {str(e)}")
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle resize events to adjust the UI layout"""
        super().resizeEvent(event)
        
        # Adjust table column widths based on available space
        width = self.results_table.width()
        if width > 200:  # Only adjust if we have enough space
            self.results_table.setColumnWidth(0, int(width * 0.25))  # Port column
            self.results_table.setColumnWidth(1, int(width * 0.25))  # Status column
            self.results_table.setColumnWidth(2, int(width * 0.5))   # Service column
