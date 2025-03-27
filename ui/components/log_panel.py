"""
Collapsible log panel for real-time monitoring
"""
import time
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTextEdit, QLabel, QSplitter, QFrame, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QColor, QTextCursor, QIcon

class LogLevel:
    """Log level enumeration"""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    DEBUG = "DEBUG"

class LogPanel(QWidget):
    """Collapsible panel to display real-time logs"""
    
    # Signal to notify something important happened in logs
    log_notification = pyqtSignal(str, str)  # level, message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.collapsed = False
        self.setup_ui()
        self.log_colors = {
            LogLevel.INFO: QColor("#3498db"),      # Blue
            LogLevel.WARNING: QColor("#f39c12"),   # Orange
            LogLevel.ERROR: QColor("#e74c3c"),     # Red
            LogLevel.SUCCESS: QColor("#2ecc71"),   # Green
            LogLevel.DEBUG: QColor("#9b59b6")      # Purple
        }
        
        # Store maximum number of log entries
        self.max_log_entries = 1000
        self.current_log_count = 0
    
    def setup_ui(self):
        """Setup the UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with title and collapse button
        header_layout = QHBoxLayout()
        header_frame = QFrame()
        header_frame.setObjectName("logPanelHeader")
        header_frame.setStyleSheet("#logPanelHeader { background-color: #2c3e50; }")
        header_frame.setLayout(header_layout)
        
        self.title_label = QLabel("Log Output")
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        
        # Buttons
        self.collapse_button = QPushButton("▲")
        self.collapse_button.setMaximumWidth(30)
        self.collapse_button.clicked.connect(self.toggle_collapse)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.setMaximumWidth(60)
        self.clear_button.clicked.connect(self.clear_logs)
        
        self.save_button = QPushButton("Save")
        self.save_button.setMaximumWidth(60)
        self.save_button.clicked.connect(self.save_logs)
        
        self.copy_button = QPushButton("Copy")
        self.copy_button.setMaximumWidth(60)
        self.copy_button.clicked.connect(self.copy_logs)
        
        # Add to header layout
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.copy_button)
        header_layout.addWidget(self.save_button)
        header_layout.addWidget(self.clear_button)
        header_layout.addWidget(self.collapse_button)
        
        # Log text area
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 9))
        self.log_display.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Set minimum height
        self.log_display.setMinimumHeight(100)
        
        # Add widgets to main layout
        main_layout.addWidget(header_frame)
        main_layout.addWidget(self.log_display)
    
    def toggle_collapse(self):
        """Toggle the collapsed state of the log panel"""
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.log_display.hide()
            self.collapse_button.setText("▼")
            self.setMaximumHeight(self.title_label.height() + 20)
        else:
            self.log_display.show()
            self.collapse_button.setText("▲")
            self.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX
    
    def clear_logs(self):
        """Clear all logs"""
        self.log_display.clear()
        self.current_log_count = 0
    
    def save_logs(self):
        """Save logs to a file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Logs", "", "Log Files (*.log);;Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.log_display.toPlainText())
                self.add_log(LogLevel.SUCCESS, f"Logs saved to {file_path}")
            except Exception as e:
                self.add_log(LogLevel.ERROR, f"Failed to save logs: {str(e)}")
    
    def copy_logs(self):
        """Copy logs to clipboard"""
        self.log_display.selectAll()
        self.log_display.copy()
        self.log_display.moveCursor(QTextCursor.MoveOperation.Start)
        self.add_log(LogLevel.INFO, "Logs copied to clipboard")
    
    def add_log(self, level, message):
        """Add a log entry with timestamp and level"""
        # Check if we need to limit the number of entries
        if self.current_log_count >= self.max_log_entries:
            self._trim_logs()
        
        timestamp = time.strftime("%H:%M:%S")
        cursor = self.log_display.textCursor()
        
        # Format log entry
        log_format = self.log_display.currentCharFormat()
        log_format.setForeground(self.log_colors.get(level, QColor("#333333")))
        
        # Add timestamp
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_display.setTextCursor(cursor)
        
        cursor.insertText(f"[{timestamp}] ")
        
        # Add level with color
        cursor.insertText(f"[{level}] ", log_format)
        
        # Add message
        cursor.insertText(f"{message}\n")
        
        # Auto-scroll to bottom
        self.log_display.verticalScrollBar().setValue(
            self.log_display.verticalScrollBar().maximum()
        )
        
        # Emit notification for certain log levels
        if level in [LogLevel.ERROR, LogLevel.WARNING]:
            self.log_notification.emit(level, message)
        
        self.current_log_count += 1
    
    def _trim_logs(self):
        """Remove older log entries to keep size manageable"""
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor, 
                            self.max_log_entries // 5)  # Remove 20% of logs
        cursor.removeSelectedText()
        self.current_log_count -= self.max_log_entries // 5
