"""
Network mapper page for Astra
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, 
                           QGroupBox, QFormLayout, QSpinBox, QProgressBar,
                           QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class NetworkMapperPage(QWidget):
    """Network mapper page widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Network Mapper")
        header_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Map and visualize network structure")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Input form
        input_group = QGroupBox("Mapping Parameters")
        input_layout = QFormLayout(input_group)
        
        # Target input
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Enter IP range (e.g., 192.168.1.0/24)")
        input_layout.addRow("Target Range:", self.target_input)
        
        # Scan speed
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(1, 5)
        self.speed_spin.setValue(3)
        self.speed_spin.setPrefix("Speed: ")
        self.speed_spin.setSuffix(" (1 = Slow, 5 = Fast)")
        input_layout.addRow("Scan Speed:", self.speed_spin)
        
        # Advanced options
        self.hostname_lookup = QSpinBox()
        self.hostname_lookup.setRange(0, 1)
        self.hostname_lookup.setValue(1)
        self.hostname_lookup.setPrefix("Hostname Lookup: ")
        self.hostname_lookup.setSuffix(" (0 = Off, 1 = On)")
        input_layout.addRow("Options:", self.hostname_lookup)
        
        layout.addWidget(input_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Button layout
        button_layout = QHBoxLayout()
        self.map_button = QPushButton("Start Mapping")
        self.map_button.setFixedWidth(150)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedWidth(150)
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.map_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Results table
        self.results_table = QTableWidget(0, 3)
        self.results_table.setHorizontalHeaderLabels(["IP Address", "Hostname", "Status"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.results_table)
        
        # Status label
        self.status_label = QLabel("Ready to map network")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Connect signals
        self.map_button.clicked.connect(self.start_mapping)
        self.stop_button.clicked.connect(self.stop_mapping)
    
    def start_mapping(self):
        """Start network mapping process"""
        # This is a placeholder - would be implemented with actual network mapping logic
        target = self.target_input.text().strip()
        if not target:
            self.status_label.setText("Please enter a target IP range")
            return
            
        self.map_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setValue(10)
        self.status_label.setText(f"Mapping network: {target}...")
        
        # Add placeholder data to the table
        for i in range(5):
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            ip = f"192.168.1.{i+1}"
            hostname = f"device-{i+1}.local" if i % 2 == 0 else ""
            status = "Up"
            
            self.results_table.setItem(row, 0, QTableWidgetItem(ip))
            self.results_table.setItem(row, 1, QTableWidgetItem(hostname))
            self.results_table.setItem(row, 2, QTableWidgetItem(status))
    
    def stop_mapping(self):
        """Stop the mapping process"""
        self.map_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Mapping stopped")
