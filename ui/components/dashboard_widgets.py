"""
Dashboard widgets for visualization and performance monitoring
"""
import time
import psutil
from datetime import datetime, timedelta
import random  # For demo data generation
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QSizePolicy, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QFont, QPainterPath

class ResourceMonitor(QWidget):
    """Widget to monitor system resource usage"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cpu_usage = []
        self.memory_usage = []
        self.max_data_points = 60  # 1 minute of data at 1 sec intervals
        
        self.setup_ui()
        
        # Update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(1000)  # Update every second
    
    def setup_ui(self):
        """Setup the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Create title
        title_label = QLabel("System Resources")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title_label)
        
        # CPU and memory labels
        stats_layout = QHBoxLayout()
        
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_label.setStyleSheet("font-family: 'Consolas'; font-size: 12px;")
        stats_layout.addWidget(self.cpu_label)
        
        self.memory_label = QLabel("Memory: 0%")
        self.memory_label.setStyleSheet("font-family: 'Consolas'; font-size: 12px;")
        stats_layout.addWidget(self.memory_label)
        
        # Add label layout
        main_layout.addLayout(stats_layout)
        
        # Create graph area
        self.graph_widget = ResourceGraph(self)
        main_layout.addWidget(self.graph_widget)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(150)
    
    def update_stats(self):
        """Update the resource statistics"""
        # Get CPU and memory usage
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        
        # Update labels
        self.cpu_label.setText(f"CPU: {cpu:.1f}%")
        self.memory_label.setText(f"Memory: {memory:.1f}%")
        
        # Add to data lists
        self.cpu_usage.append(cpu)
        self.memory_usage.append(memory)
        
        # Trim lists if too long
        if len(self.cpu_usage) > self.max_data_points:
            self.cpu_usage.pop(0)
        if len(self.memory_usage) > self.max_data_points:
            self.memory_usage.pop(0)
        
        # Update graph
        self.graph_widget.update_data(self.cpu_usage, self.memory_usage)

class ResourceGraph(QWidget):
    """Widget to display CPU and memory usage graphs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cpu_data = []
        self.memory_data = []
        
        # Color settings
        self.cpu_color = QColor(52, 152, 219)  # Blue
        self.memory_color = QColor(46, 204, 113)  # Green
        self.grid_color = QColor(200, 200, 200, 100)
        self.background_color = QColor(255, 255, 255, 30)
        
        self.setMinimumHeight(100)
    
    def update_data(self, cpu_data, memory_data):
        """Update the graph data"""
        self.cpu_data = cpu_data
        self.memory_data = memory_data
        self.update()  # Schedule repaint
    
    def paintEvent(self, event):
        """Paint the graph"""
        if not self.cpu_data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        
        # Draw background
        painter.fillRect(0, 0, width, height, self.background_color)
        
        # Draw grid lines
        painter.setPen(QPen(self.grid_color, 1, Qt.PenStyle.DotLine))
        # Horizontal grid lines
        for i in range(1, 4):
            y = height * (1 - i / 4)
            painter.drawLine(0, y, width, y)
        
        # Draw data if available
        if self.cpu_data:
            # Draw CPU usage
            self._draw_graph_line(painter, self.cpu_data, self.cpu_color, width, height)
            
        if self.memory_data:
            # Draw memory usage
            self._draw_graph_line(painter, self.memory_data, self.memory_color, width, height)
        
        # Draw legend
        legend_y = 15
        # CPU legend
        painter.setPen(QPen(self.cpu_color, 2))
        painter.drawLine(5, legend_y, 20, legend_y)
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.drawText(25, legend_y + 5, "CPU")
        
        # Memory legend
        painter.setPen(QPen(self.memory_color, 2))
        painter.drawLine(60, legend_y, 75, legend_y)
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.drawText(80, legend_y + 5, "Memory")
    
    def _draw_graph_line(self, painter, data, color, width, height):
        """Helper method to draw a graph line"""
        if not data:
            return
            
        # Set pen for the line
        painter.setPen(QPen(color, 2))
        
        # Calculate points
        points = []
        data_len = len(data)
        point_distance = width / max(1, data_len - 1) if data_len > 1 else width
        
        for i, value in enumerate(data):
            x = i * point_distance
            # Scale value from 0-100 to height-0 (inverted y-axis)
            y = height - (value / 100.0 * height)
            points.append((x, y))
        
        # Draw the line connecting all points
        for i in range(1, len(points)):
            painter.drawLine(
                int(points[i-1][0]), int(points[i-1][1]),
                int(points[i][0]), int(points[i][1])
            )

class ScanHistoryChart(QWidget):
    """Widget to display scan history as a bar chart"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Demo data structure: {date: {completed: X, issues: Y}}
        self.scan_data = {}
        self.setup_ui()
        
        # For demo, generate random data
        self._generate_demo_data()
    
    def setup_ui(self):
        """Setup the UI components"""
        main_layout = QVBoxLayout(self)
        
        # Create title
        title_label = QLabel("Scan History")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(title_label)
        
        # Create graph area
        self.graph_area = QWidget()
        self.graph_area.setMinimumHeight(200)
        self.graph_area.paintEvent = self._paint_graph
        main_layout.addWidget(self.graph_area)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(250)
    
    def _generate_demo_data(self):
        """Generate random demo data for display purposes"""
        today = datetime.now().date()
        for i in range(7):
            date = today - timedelta(days=i)
            date_str = date.strftime("%m-%d")
            self.scan_data[date_str] = {
                "completed": random.randint(3, 15),
                "issues": random.randint(0, 7)
            }
    
    def update_data(self, scan_data):
        """Update chart with new data"""
        self.scan_data = scan_data
        self.graph_area.update()
    
    def _paint_graph(self, event):
        """Paint the graph area"""
        if not self.scan_data:
            return
            
        painter = QPainter(self.graph_area)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get widget dimensions
        width = self.graph_area.width()
        height = self.graph_area.height()
        
        # Calculate bar dimensions
        num_days = len(self.scan_data)
        bar_width = width / (num_days * 3)  # 3 = 2 bars + space
        
        # Draw background
        painter.fillRect(0, 0, width, height, QColor(255, 255, 255, 30))
        
        # Draw horizontal lines (grid)
        painter.setPen(QPen(QColor(200, 200, 200, 100), 1, Qt.PenStyle.DotLine))
        for i in range(1, 5):
            y = height * (1 - i / 5)
            painter.drawLine(0, y, width, y)
        
        # Find max value for scaling
        max_value = 1  # Avoid division by zero
        for day_data in self.scan_data.values():
            day_total = day_data["completed"] + day_data["issues"]
            max_value = max(max_value, day_total)
        
        # Draw bars
        dates = list(self.scan_data.keys())
        dates.reverse()  # Most recent date first
        
        for i, date in enumerate(dates):
            day_data = self.scan_data[date]
            
            # Calculate bar positions
            bar_x = i * 3 * bar_width
            
            # Draw completed scans bar
            completed = day_data["completed"]
            bar_height = (completed / max_value) * (height - 30)
            painter.setBrush(QBrush(QColor(46, 204, 113)))  # Green
            painter.setPen(QPen(QColor(39, 174, 96)))
            painter.drawRect(bar_x, height - bar_height - 20, bar_width, bar_height)
            
            # Draw issues bar
            issues = day_data["issues"]
            bar_height = (issues / max_value) * (height - 30)
            painter.setBrush(QBrush(QColor(231, 76, 60)))  # Red
            painter.setPen(QPen(QColor(192, 57, 43)))
            painter.drawRect(bar_x + bar_width, height - bar_height - 20, bar_width, bar_height)
            
            # Draw date label
            painter.setPen(QPen(Qt.GlobalColor.black))
            painter.drawText(
                bar_x, height - 5, 
                bar_width * 2, 20, 
                Qt.AlignmentFlag.AlignCenter, 
                date
            )
        
        # Draw legend
        legend_y = 15
        # Completed legend
        painter.setBrush(QBrush(QColor(46, 204, 113)))
        painter.setPen(QPen(QColor(39, 174, 96)))
        painter.drawRect(5, legend_y - 10, 15, 10)
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.drawText(25, legend_y, "Completed")
        
        # Issues legend
        painter.setBrush(QBrush(QColor(231, 76, 60)))
        painter.setPen(QPen(QColor(192, 57, 43)))
        painter.drawRect(120, legend_y - 10, 15, 10)
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.drawText(140, legend_y, "Issues")
