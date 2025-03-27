"""
Subdomain enumeration page for Astra
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
                            QProgressBar, QTableWidget, QTableWidgetItem, QSpinBox, QGroupBox,
                            QFormLayout, QHeaderView, QMessageBox, QSizePolicy, QCheckBox,
                            QFileDialog, QRadioButton)
from PyQt6.QtCore import Qt, QThread, QSize
from PyQt6.QtGui import QFont, QColor, QResizeEvent, QDragEnterEvent, QDropEvent

from core.subdomain_enum import SubdomainEnumerator
from utils.report_generator import ReportGenerator

class EnumeratorThread(QThread):
    """Thread for running subdomain enumerator without blocking GUI"""
    
    def __init__(self, enumerator, domain, wordlist=None, max_threads=20, use_amass=False):
        super().__init__()
        self.enumerator = enumerator
        self.domain = domain
        self.wordlist = wordlist
        self.max_threads = max_threads
        self.use_amass = use_amass
    
    def run(self):
        """Run the enumerator in a thread"""
        self.enumerator.enumerate(self.domain, self.wordlist, self.max_threads, self.use_amass)

class SubdomainEnumPage(QWidget):
    """Subdomain enumeration page widget"""
    
    def __init__(self):
        super().__init__()
        self.enumerator = SubdomainEnumerator()
        self.thread = None
        self.report_generator = ReportGenerator()
        self.enum_results = []  # Store enumeration results for reporting
        self.custom_wordlist = None  # Store custom wordlist
        self.setup_ui()
        self.connect_signals()
        self.setAcceptDrops(True)  # Enable drag and drop
    
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Subdomain Enumeration")
        header_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Discover subdomains of a target domain")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Input form
        input_group = QGroupBox("Enumeration Parameters")
        input_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        input_layout = QFormLayout(input_group)
        
        # Domain input
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("Enter domain (e.g., example.com)")
        input_layout.addRow("Target Domain:", self.domain_input)
        
        # Wordlist selection
        wordlist_layout = QVBoxLayout()
        
        # Wordlist radio buttons
        self.default_wordlist_radio = QRadioButton("Use Default Wordlist")
        self.default_wordlist_radio.setChecked(True)
        self.custom_wordlist_radio = QRadioButton("Use Custom Wordlist")
        
        wordlist_layout.addWidget(self.default_wordlist_radio)
        wordlist_layout.addWidget(self.custom_wordlist_radio)
        
        # Custom wordlist input
        custom_wordlist_layout = QHBoxLayout()
        self.custom_wordlist_path = QLineEdit()
        self.custom_wordlist_path.setPlaceholderText("Select wordlist file")
        self.custom_wordlist_path.setEnabled(False)
        self.custom_wordlist_button = QPushButton("Browse")
        self.custom_wordlist_button.setEnabled(False)
        self.custom_wordlist_button.clicked.connect(self.browse_wordlist)
        
        custom_wordlist_layout.addWidget(self.custom_wordlist_path)
        custom_wordlist_layout.addWidget(self.custom_wordlist_button)
        
        wordlist_layout.addLayout(custom_wordlist_layout)
        
        # Connect radio buttons to enable/disable custom wordlist input
        self.default_wordlist_radio.toggled.connect(self.toggle_wordlist_input)
        
        input_layout.addRow("Wordlist:", wordlist_layout)
        
        # Thread count
        self.thread_count = QSpinBox()
        self.thread_count.setRange(1, 100)
        self.thread_count.setValue(20)
        self.thread_count.setSuffix(" threads")
        input_layout.addRow("Thread Count:", self.thread_count)
        
        # Use amass
        self.use_amass_check = QCheckBox("Use Amass for advanced enumeration (if available)")
        self.use_amass_check.setChecked(True)
        input_layout.addRow("", self.use_amass_check)
        
        layout.addWidget(input_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Button layout
        button_layout = QHBoxLayout()
        self.enum_button = QPushButton("Start Enumeration")
        self.enum_button.setFixedWidth(150)
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
        
        button_layout.addWidget(self.enum_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.generate_pdf_button)
        button_layout.addWidget(self.generate_html_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Results table
        self.results_table = QTableWidget(0, 2)
        self.results_table.setHorizontalHeaderLabels(["Subdomain", "IP Address"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout.addWidget(self.results_table)
        
        # Status label
        self.status_label = QLabel("Drag and drop a wordlist file to use it for enumeration")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
    def connect_signals(self):
        """Connect signals to slots"""
        self.enum_button.clicked.connect(self.start_enumeration)
        self.stop_button.clicked.connect(self.stop_enumeration)
        self.generate_pdf_button.clicked.connect(self.generate_pdf_report)
        self.generate_html_button.clicked.connect(self.generate_html_report)
        
        # Connect enumerator signals
        self.enumerator.result_update.connect(self.update_result)
        self.enumerator.progress_update.connect(self.update_progress)
        self.enumerator.enum_completed.connect(self.enumeration_finished)
        self.enumerator.enum_error.connect(self.show_error)
    
    def toggle_wordlist_input(self, checked):
        """Toggle custom wordlist input enabled state"""
        self.custom_wordlist_path.setEnabled(not checked)
        self.custom_wordlist_button.setEnabled(not checked)
    
    def browse_wordlist(self):
        """Open dialog to select wordlist file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Wordlist", "", "Text Files (*.txt)"
        )
        if file_path:
            self.custom_wordlist_path.setText(file_path)
    
    def start_enumeration(self):
        """Start the subdomain enumeration process"""
        # Clear previous results
        self.results_table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.enum_results = []
        
        # Get parameters
        domain = self.domain_input.text().strip()
        if not domain:
            self.show_error("Please enter a domain name")
            return
        
        # Get wordlist
        wordlist = None
        if self.custom_wordlist_radio.isChecked():
            wordlist_path = self.custom_wordlist_path.text().strip()
            if not wordlist_path:
                self.show_error("Please select a wordlist file")
                return
                
            try:
                with open(wordlist_path, 'r') as f:
                    wordlist = [line.strip() for line in f if line.strip()]
                if not wordlist:
                    self.show_error("Selected wordlist file is empty")
                    return
            except Exception as e:
                self.show_error(f"Error loading wordlist: {str(e)}")
                return
        
        # Get thread count and amass setting
        thread_count = self.thread_count.value()
        use_amass = self.use_amass_check.isChecked()
        
        # Update UI
        self.enum_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.generate_pdf_button.setEnabled(False)
        self.generate_html_button.setEnabled(False)
        self.status_label.setText(f"Enumerating subdomains for {domain}...")
        
        # Start enumeration in a thread
        self.thread = EnumeratorThread(
            self.enumerator,
            domain,
            wordlist,
            thread_count,
            use_amass
        )
        self.thread.start()
    
    def stop_enumeration(self):
        """Stop the enumeration process"""
        if self.thread and self.thread.isRunning():
            self.enumerator.stop_enumeration()
            self.thread.wait()
            self.enumeration_finished()
    
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_bar.setValue(value)
    
    def update_result(self, subdomain, ip):
        """Update the results table with a new enumeration result"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Subdomain
        subdomain_item = QTableWidgetItem(subdomain)
        self.results_table.setItem(row, 0, subdomain_item)
        
        # IP Address
        ip_item = QTableWidgetItem(ip)
        self.results_table.setItem(row, 1, ip_item)
        
        # Store result for report generation
        self.enum_results.append((subdomain, ip))
        
        # Sort by subdomain
        self.results_table.sortItems(0, Qt.SortOrder.AscendingOrder)
    
    def enumeration_finished(self):
        """Handle enumeration completion"""
        self.progress_bar.setValue(100)
        self.enum_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.generate_pdf_button.setEnabled(True)
        self.generate_html_button.setEnabled(True)
        
        # Update status with count of discovered subdomains
        count = self.results_table.rowCount()
        self.status_label.setText(f"Enumeration completed. Discovered {count} subdomains.")
    
    def show_error(self, message):
        """Display an error message"""
        QMessageBox.critical(self, "Error", message)
        self.enum_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText(f"Error: {message}")
    
    def generate_pdf_report(self):
        """Generate a PDF report from enumeration results"""
        if not self.enum_results:
            self.show_error("No enumeration results to report")
            return
            
        domain = self.domain_input.text().strip()
        try:
            filepath = self.report_generator.generate_pdf_report(
                "Subdomain Enumeration Results",
                self.enum_results,
                "Subdomain Enumeration",
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
        """Generate an HTML report from enumeration results"""
        if not self.enum_results:
            self.show_error("No enumeration results to report")
            return
            
        domain = self.domain_input.text().strip()
        try:
            filepath = self.report_generator.generate_html_report(
                "Subdomain Enumeration Results",
                self.enum_results,
                "Subdomain Enumeration",
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
        """Handle drop event for wordlist files"""
        file_path = event.mimeData().urls()[0].toLocalFile()
        # Enable custom wordlist mode
        self.custom_wordlist_radio.setChecked(True)
        self.custom_wordlist_path.setText(file_path)
        self.status_label.setText(f"Loaded wordlist: {file_path}")
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle resize events to adjust the UI layout"""
        super().resizeEvent(event)
        
        # Adjust table column widths based on available space
        width = self.results_table.width()
        if width > 200:  # Only adjust if we have enough space
            self.results_table.setColumnWidth(0, int(width * 0.6))  # Subdomain column
            self.results_table.setColumnWidth(1, int(width * 0.4))  # IP column

        # Adjust button layout based on window width
        if self.width() < 1000:
            self.enum_button.setFixedWidth(120)
            self.stop_button.setFixedWidth(120)
            self.generate_pdf_button.setFixedWidth(150)
            self.generate_html_button.setFixedWidth(150)
        else:
            self.enum_button.setFixedWidth(150)
            self.stop_button.setFixedWidth(150)
            self.generate_pdf_button.setFixedWidth(200)
            self.generate_html_button.setFixedWidth(200)
