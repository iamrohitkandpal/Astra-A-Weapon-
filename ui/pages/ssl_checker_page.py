"""
SSL/TLS checker page for Astra
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
                            QTableWidget, QTableWidgetItem, QGroupBox, QFormLayout, QSpinBox,
                            QHeaderView, QMessageBox, QSizePolicy, QTextEdit, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QThread, QSize
from PyQt6.QtGui import QFont, QColor, QResizeEvent, QDragEnterEvent, QDropEvent

from core.ssl_checker import SSLChecker
from utils.report_generator import ReportGenerator
import datetime

class SSLCheckerThread(QThread):
    """Thread for running SSL checker without blocking GUI"""
    
    def __init__(self, checker, hostname, port):
        super().__init__()
        self.checker = checker
        self.hostname = hostname
        self.port = port
    
    def run(self):
        """Run the checker in a thread"""
        self.checker.check(self.hostname, self.port)

class SSLCheckerPage(QWidget):
    """SSL/TLS checker page widget"""
    
    def __init__(self):
        super().__init__()
        self.checker = SSLChecker()
        self.thread = None
        self.report_generator = ReportGenerator()
        self.check_results = {}  # Store check results for reporting
        self.setup_ui()
        self.connect_signals()
        self.setAcceptDrops(True)  # Enable drag and drop
    
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("SSL/TLS Checker")
        header_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Check SSL/TLS security for a website")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Input form
        input_group = QGroupBox("Connection Parameters")
        input_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        input_layout = QFormLayout(input_group)
        
        # Hostname input
        self.hostname_input = QLineEdit()
        self.hostname_input.setPlaceholderText("Enter hostname (e.g., example.com)")
        input_layout.addRow("Hostname:", self.hostname_input)
        
        # Port input
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(443)
        input_layout.addRow("Port:", self.port_input)
        
        layout.addWidget(input_group)
        
        # Button layout
        button_layout = QHBoxLayout()
        self.check_button = QPushButton("Check Security")
        self.check_button.setFixedWidth(150)
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
        
        button_layout.addWidget(self.check_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.generate_pdf_button)
        button_layout.addWidget(self.generate_html_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Results section
        results_scroll = QScrollArea()
        results_scroll.setWidgetResizable(True)
        results_scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Certificate Info Group
        self.cert_group = QGroupBox("Certificate Information")
        self.cert_group.setVisible(False)
        cert_layout = QFormLayout(self.cert_group)
        
        self.subject_label = QLabel("")
        self.issuer_label = QLabel("")
        self.valid_from_label = QLabel("")
        self.valid_until_label = QLabel("")
        self.days_left_label = QLabel("")
        
        # Make labels selectable and with word wrap
        for label in [self.subject_label, self.issuer_label, self.valid_from_label, 
                      self.valid_until_label, self.days_left_label]:
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            label.setWordWrap(True)
        
        cert_layout.addRow("Subject:", self.subject_label)
        cert_layout.addRow("Issuer:", self.issuer_label)
        cert_layout.addRow("Valid From:", self.valid_from_label)
        cert_layout.addRow("Valid Until:", self.valid_until_label)
        cert_layout.addRow("Days Remaining:", self.days_left_label)
        
        results_layout.addWidget(self.cert_group)
        
        # Connection Info Group
        self.conn_group = QGroupBox("Connection Information")
        self.conn_group.setVisible(False)
        conn_layout = QFormLayout(self.conn_group)
        
        self.protocol_label = QLabel("")
        self.cipher_suite_label = QLabel("")
        self.cipher_bits_label = QLabel("")
        self.security_label = QLabel("")
        
        # Make labels selectable
        for label in [self.protocol_label, self.cipher_suite_label, 
                      self.cipher_bits_label, self.security_label]:
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            label.setWordWrap(True)
        
        conn_layout.addRow("Protocol:", self.protocol_label)
        conn_layout.addRow("Cipher Suite:", self.cipher_suite_label)
        conn_layout.addRow("Cipher Strength:", self.cipher_bits_label)
        conn_layout.addRow("Security Status:", self.security_label)
        
        results_layout.addWidget(self.conn_group)
        
        # Other certificate details
        self.details_group = QGroupBox("Technical Details")
        self.details_group.setVisible(False)
        details_layout = QVBoxLayout(self.details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        results_layout.addWidget(self.details_group)
        
        # Security rating
        self.rating_group = QGroupBox("Security Rating")
        self.rating_group.setVisible(False)
        rating_layout = QVBoxLayout(self.rating_group)
        
        self.rating_label = QLabel("")
        self.rating_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.rating_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Recommendations
        self.recommendations_label = QLabel("Recommendations:")
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setReadOnly(True)
        
        rating_layout.addWidget(self.rating_label)
        rating_layout.addWidget(self.recommendations_label)
        rating_layout.addWidget(self.recommendations_text)
        
        results_layout.addWidget(self.rating_group)
        
        # Add a stretch to push everything to the top
        results_layout.addStretch()
        
        results_scroll.setWidget(results_widget)
        layout.addWidget(results_scroll)
        
        # Status label
        self.status_label = QLabel("Enter a hostname to check SSL/TLS security")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
    
    def connect_signals(self):
        """Connect signals to slots"""
        self.check_button.clicked.connect(self.start_check)
        self.stop_button.clicked.connect(self.stop_check)
        self.generate_pdf_button.clicked.connect(self.generate_pdf_report)
        self.generate_html_button.clicked.connect(self.generate_html_report)
        
        # Connect checker signals
        self.checker.result_update.connect(self.update_result)
        self.checker.check_completed.connect(self.check_finished)
        self.checker.check_error.connect(self.show_error)
    
    def start_check(self):
        """Start the SSL/TLS check process"""
        # Reset UI
        self.check_results = {}
        self.cert_group.setVisible(False)
        self.conn_group.setVisible(False)
        self.details_group.setVisible(False)
        self.rating_group.setVisible(False)
        
        # Get parameters
        hostname = self.hostname_input.text().strip()
        if not hostname:
            self.show_error("Please enter a hostname")
            return
        
        port = self.port_input.value()
        
        # Update UI
        self.check_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.generate_pdf_button.setEnabled(False)
        self.generate_html_button.setEnabled(False)
        self.status_label.setText(f"Checking {hostname}:{port}...")
        
        # Start check in a thread
        self.thread = SSLCheckerThread(
            self.checker,
            hostname,
            port
        )
        self.thread.start()
    
    def stop_check(self):
        """Stop the check process"""
        if self.thread and self.thread.isRunning():
            self.checker.stop_check()
            self.thread.wait()
            self.check_finished()
    
    def update_result(self, results):
        """Update the UI with check results"""
        # Store results for reporting
        self.check_results = results
        
        # Make all result groups visible
        self.cert_group.setVisible(True)
        self.conn_group.setVisible(True)
        self.details_group.setVisible(True)
        self.rating_group.setVisible(True)
        
        # Process certificate information
        cert_info = results.get('certificate', {})
        if cert_info:
            self.subject_label.setText(str(cert_info.get('subject', 'N/A')))
            self.issuer_label.setText(str(cert_info.get('issuer', 'N/A')))
            self.valid_from_label.setText(str(cert_info.get('valid_from', 'N/A')))
            self.valid_until_label.setText(str(cert_info.get('valid_until', 'N/A')))
            
            days_left = cert_info.get('days_left', 0)
            self.days_left_label.setText(f"{days_left} days")
            
            if days_left < 0:
                self.days_left_label.setStyleSheet("color: red; font-weight: bold;")
            elif days_left < 30:
                self.days_left_label.setStyleSheet("color: orange; font-weight: bold;")
            else:
                self.days_left_label.setStyleSheet("color: green; font-weight: bold;")
            
            # Populate technical details
            details_text = ""
            for key, value in cert_info.items():
                if key not in ['subject', 'issuer', 'valid_from', 'valid_until', 'days_left', 'is_expired']:
                    details_text += f"{key.replace('_', ' ').title()}: {value}\n"
            
            self.details_text.setText(details_text)
        
        # Process connection information
        self.protocol_label.setText(results.get('protocol', 'N/A'))
        self.cipher_suite_label.setText(results.get('cipher_suite', 'N/A'))
        self.cipher_bits_label.setText(f"{results.get('cipher_bits', 'N/A')} bits")
        
        # Set security status
        secure_protocol = results.get('secure_protocol', False)
        if secure_protocol:
            self.security_label.setText("Secure")
            self.security_label.setStyleSheet("color: green; font-weight: bold;")
            self.rating_label.setText("✅ Good")
            self.rating_label.setStyleSheet("color: green;")
        else:
            self.security_label.setText("Insecure")
            self.security_label.setStyleSheet("color: red; font-weight: bold;")
            self.rating_label.setText("❌ Needs Improvement")
            self.rating_label.setStyleSheet("color: red;")
        
        # Generate recommendations
        recommendations = []
        if not secure_protocol:
            recommendations.append("- Upgrade to TLSv1.2 or TLSv1.3 protocol")
        
        if cert_info.get('is_expired', False):
            recommendations.append("- Certificate has expired. Renew immediately.")
        elif cert_info.get('days_left', 0) < 30:
            recommendations.append(f"- Certificate expiring soon ({cert_info.get('days_left', 0)} days). Plan renewal.")
        
        cipher_bits = results.get('cipher_bits', 0)
        if cipher_bits < 128:
            recommendations.append("- Cipher strength is weak. Configure server to use stronger ciphers (128+ bits)")
        
        if not recommendations:
            recommendations.append("- No critical issues detected. Keep monitoring regularly.")
        
        self.recommendations_text.setText("\n".join(recommendations))
    
    def check_finished(self):
        """Handle check completion"""
        self.check_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.generate_pdf_button.setEnabled(True)
        self.generate_html_button.setEnabled(True)
        
        # Update status
        self.status_label.setText("Check completed")
    
    def show_error(self, message):
        """Display an error message"""
        QMessageBox.critical(self, "Error", message)
        self.check_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText(f"Error: {message}")
    
    def generate_pdf_report(self):
        """Generate a PDF report from check results"""
        if not self.check_results:
            self.show_error("No check results to report")
            return
            
        hostname = self.hostname_input.text().strip()
        try:
            filepath = self.report_generator.generate_pdf_report(
                "SSL/TLS Security Check Results",
                self.check_results,
                "SSL/TLS Check",
                hostname
            )
            QMessageBox.information(
                self, 
                "Report Generated", 
                f"PDF Report has been saved to:\n{filepath}"
            )
        except Exception as e:
            self.show_error(f"Error generating PDF report: {str(e)}")
    
    def generate_html_report(self):
        """Generate an HTML report from check results"""
        if not self.check_results:
            self.show_error("No check results to report")
            return
            
        hostname = self.hostname_input.text().strip()
        try:
            filepath = self.report_generator.generate_html_report(
                "SSL/TLS Security Check Results",
                self.check_results,
                "SSL/TLS Check",
                hostname
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
        """Handle drop event for hostname list files"""
        file_path = event.mimeData().urls()[0].toLocalFile()
        try:
            with open(file_path, 'r') as f:
                hostnames = [line.strip() for line in f if line.strip()]
            
            if hostnames:
                # Take the first hostname from the list
                self.hostname_input.setText(hostnames[0])
                if len(hostnames) > 1:
                    self.status_label.setText(f"Loaded 1 of {len(hostnames)} hostnames from file")
                    
                    # Ask if user wants to check all hostnames
                    reply = QMessageBox.question(
                        self, 
                        "Multiple Hostnames", 
                        f"File contains {len(hostnames)} hostnames. Do you want to check them all?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        # TODO: Implement batch checking functionality
                        self.status_label.setText(f"Batch checking not yet implemented")
            else:
                self.status_label.setText("No valid hostnames found in file")
        except Exception as e:
            self.status_label.setText(f"Error loading file: {str(e)}")
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle resize events to adjust the UI layout"""
        super().resizeEvent(event)
        
        # Adjust layout based on width
        width = self.width()
        if width < 800:
            # When window is narrow, ensure elements don't get too squished
            self.check_button.setFixedWidth(120)
            self.stop_button.setFixedWidth(120)
            self.generate_pdf_button.setFixedWidth(150)
            self.generate_html_button.setFixedWidth(150)
        else:
            # When window is wider, give buttons more space
            self.check_button.setFixedWidth(150)
            self.stop_button.setFixedWidth(150)
            self.generate_pdf_button.setFixedWidth(200)
            self.generate_html_button.setFixedWidth(200)
