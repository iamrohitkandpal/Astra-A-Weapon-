"""
Password tools page for Astra
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, 
                            QGroupBox, QFormLayout, QTabWidget, QSpinBox, QCheckBox, 
                            QTextEdit, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import random
import string
import re
from PyQt6.QtGui import QClipboard
from PyQt6.QtWidgets import QApplication

class PasswordToolsPage(QWidget):
    """Password tools page widget"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Password Tools")
        header_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Generate and analyze passwords for security testing")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Tabs for different tools
        tabs = QTabWidget()
        
        # Password Generator Tab
        generator_tab = QWidget()
        generator_layout = QVBoxLayout(generator_tab)
        
        # Generator options
        options_group = QGroupBox("Generator Options")
        options_layout = QFormLayout(options_group)
        
        self.length_input = QSpinBox()
        self.length_input.setRange(8, 64)
        self.length_input.setValue(16)
        options_layout.addRow("Password Length:", self.length_input)
        
        self.uppercase_check = QCheckBox("Include uppercase letters (A-Z)")
        self.uppercase_check.setChecked(True)
        options_layout.addRow("", self.uppercase_check)
        
        self.lowercase_check = QCheckBox("Include lowercase letters (a-z)")
        self.lowercase_check.setChecked(True)
        options_layout.addRow("", self.lowercase_check)
        
        self.numbers_check = QCheckBox("Include numbers (0-9)")
        self.numbers_check.setChecked(True)
        options_layout.addRow("", self.numbers_check)
        
        self.symbols_check = QCheckBox("Include symbols (!@#$%^&*)")
        self.symbols_check.setChecked(True)
        options_layout.addRow("", self.symbols_check)
        
        generator_layout.addWidget(options_group)
        
        # Generate button
        generate_button = QPushButton("Generate Password")
        generate_button.setFixedWidth(200)
        generate_button.clicked.connect(self.generate_password)
        generator_layout.addWidget(generate_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Password output
        self.password_output = QLineEdit()
        self.password_output.setReadOnly(True)
        self.password_output.setPlaceholderText("Generated password will appear here")
        generator_layout.addWidget(self.password_output)
        
        # Copy button
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.setFixedWidth(200)
        copy_button.clicked.connect(self.copy_to_clipboard)
        generator_layout.addWidget(copy_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Add stretch
        generator_layout.addStretch()
        
        # Password Strength Analyzer Tab
        analyzer_tab = QWidget()
        analyzer_layout = QVBoxLayout(analyzer_tab)
        
        # Password input
        self.analyze_input = QLineEdit()
        self.analyze_input.setPlaceholderText("Enter a password to analyze")
        analyzer_layout.addWidget(self.analyze_input)
        
        # Analyze button
        analyze_button = QPushButton("Analyze Strength")
        analyze_button.setFixedWidth(200)
        analyze_button.clicked.connect(self.analyze_password)
        analyzer_layout.addWidget(analyze_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Analysis results
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout(results_group)
        
        self.strength_label = QLabel("Strength: Not analyzed")
        results_layout.addWidget(self.strength_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText("Password analysis details will appear here")
        results_layout.addWidget(self.details_text)
        
        analyzer_layout.addWidget(results_group)
        
        # Add tabs
        tabs.addTab(generator_tab, "Password Generator")
        tabs.addTab(analyzer_tab, "Password Strength Analyzer")
        
        layout.addWidget(tabs)
        
        # Note about data security
        note_label = QLabel("Note: All operations are performed locally. No passwords are transmitted over the network.")
        note_label.setStyleSheet("color: gray; font-style: italic;")
        note_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(note_label)
    
    def generate_password(self):
        """Generate a random password based on the selected options"""
        # Build character set based on options
        chars = ""
        if self.uppercase_check.isChecked():
            chars += string.ascii_uppercase
        if self.lowercase_check.isChecked():
            chars += string.ascii_lowercase
        if self.numbers_check.isChecked():
            chars += string.digits
        if self.symbols_check.isChecked():
            chars += "!@#$%^&*()-_=+[]{}|;:,.<>?/~"
        
        # Check if we have any characters to use
        if not chars:
            self.password_output.setText("Please select at least one option")
            return
        
        # Generate password
        length = self.length_input.value()
        password = ''.join(random.choice(chars) for _ in range(length))
        
        # Update output
        self.password_output.setText(password)
        
        # Auto-analyze the generated password
        self.analyze_input.setText(password)
        self.analyze_password()
    
    def copy_to_clipboard(self):
        """Copy generated password to clipboard"""
        password = self.password_output.text()
        if password and not password.startswith("Please select"):
            clipboard = QApplication.clipboard()
            clipboard.setText(password)
            self.password_output.setStyleSheet("background-color: #e0ffe0;")  # Green tint
            self.password_output.setText("Password copied to clipboard!")
            # Reset style after a short delay
            QApplication.processEvents()
            import time
            time.sleep(0.5)
            self.password_output.setStyleSheet("")
            self.password_output.setText(password)
    
    def analyze_password(self):
        """Analyze password strength"""
        password = self.analyze_input.text()
        if not password:
            self.strength_label.setText("Strength: Not analyzed")
            self.details_text.setPlainText("Please enter a password to analyze.")
            return
        
        # Calculate base score
        score = 0
        feedback = []
        
        # Length score: 0-15
        length = len(password)
        length_score = min(15, length // 2)
        score += length_score
        
        if length < 8:
            feedback.append("❌ Password is too short (minimum 8 characters recommended)")
        elif length >= 16:
            feedback.append("✅ Good password length")
        else:
            feedback.append("⚠️ Password length is acceptable but could be longer")
        
        # Character variety score: 0-20
        has_lowercase = any(c.islower() for c in password)
        has_uppercase = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(not c.isalnum() for c in password)
        
        variety_score = 0
        if has_lowercase:
            variety_score += 5
            feedback.append("✅ Contains lowercase letters")
        else:
            feedback.append("❌ Missing lowercase letters")
            
        if has_uppercase:
            variety_score += 5
            feedback.append("✅ Contains uppercase letters")
        else:
            feedback.append("❌ Missing uppercase letters")
            
        if has_digit:
            variety_score += 5
            feedback.append("✅ Contains numbers")
        else:
            feedback.append("❌ Missing numbers")
            
        if has_symbol:
            variety_score += 5
            feedback.append("✅ Contains symbols")
        else:
            feedback.append("❌ Missing symbols")
        
        score += variety_score
        
        # Check for common patterns
        has_sequential = re.search(r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz|012|123|234|345|456|567|678|789)', password.lower())
        has_repeated = re.search(r'(.)\1{2,}', password)  # Same character 3+ times in a row
        
        pattern_penalty = 0
        if has_sequential:
            pattern_penalty += 10
            feedback.append("❌ Contains sequential characters")
        
        if has_repeated:
            pattern_penalty += 10
            feedback.append("❌ Contains repeated characters")
        
        score = max(0, score - pattern_penalty)
        
        # Common words check
        common_words = ["password", "qwerty", "admin", "welcome", "123456", "letmein"]
        for word in common_words:
            if word in password.lower():
                score = max(0, score - 15)
                feedback.append(f"❌ Contains common password element: {word}")
                break
        
        # Determine strength rating
        if score >= 30:
            strength = "Strong"
            color = "darkgreen"
        elif score >= 20:
            strength = "Moderate"
            color = "darkorange"
        else:
            strength = "Weak"
            color = "darkred"
        
        # Update UI
        self.strength_label.setText(f"Strength: {strength} (Score: {score}/35)")
        self.strength_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # Add score breakdown
        feedback.insert(0, f"Length score: {length_score}/15")
        feedback.insert(1, f"Variety score: {variety_score}/20")
        feedback.insert(2, f"Pattern penalty: -{pattern_penalty}")
        
        self.details_text.setPlainText("\n".join(feedback))
