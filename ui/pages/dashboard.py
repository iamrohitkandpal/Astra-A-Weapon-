"""
Dashboard page widget for Astra
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QColor
from utils.activity_tracker import ActivityTracker, ActivityType

class ToolCard(QFrame):
    """Custom tool card widget with click functionality"""
    
    clicked = pyqtSignal(str)  # Signal to emit the tool name when clicked
    
    def __init__(self, title, description, tool_id):
        super().__init__()
        self.tool_id = tool_id
        self.setObjectName("toolCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumHeight(120)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Create layout
        card_layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title_label.setObjectName("toolCardTitle")
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setObjectName("toolCardDescription")
        
        # Add to layout
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)
        card_layout.addStretch()
    
    def mousePressEvent(self, event):
        """Handle mouse press events to emit the clicked signal"""
        self.clicked.emit(self.tool_id)
        super().mousePressEvent(event)

class DashboardPage(QWidget):
    """Dashboard page showing overview of tools and system information"""
    
    # Signal to request a page change
    open_tool = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.activity_tracker = ActivityTracker()
        self.setup_ui()
        
        # Connect to activity tracker signals
        self.activity_tracker.activities_updated.connect(self.update_recent_activities)
        
        # Load resource widgets
        self.load_resource_widgets()
        
    def setup_ui(self):
        """Setup the dashboard UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Dashboard")
        header_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header_label.setObjectName("dashboardHeader")
        layout.addWidget(header_label)
        
        # Resource monitoring section
        resources_layout = QHBoxLayout()
        
        # Placeholder for resource monitor widget
        self.resource_container = QWidget()
        self.resource_container.setMinimumHeight(200)
        self.resource_container.setLayout(QVBoxLayout())
        resources_layout.addWidget(self.resource_container)
        
        layout.addLayout(resources_layout)
        
        # Tool cards section
        tools_label = QLabel("Quick Access Tools")
        tools_label.setFont(QFont("Arial", 16))
        tools_label.setObjectName("sectionTitle")
        layout.addWidget(tools_label)
        
        # Grid for tool cards
        tools_grid = QGridLayout()
        tools_grid.setSpacing(15)
        
        # Define tool cards with their IDs
        tool_cards = [
            ("Port Scanner", "Scan open ports on target systems", "portScanner"),
            ("DNS Analyzer", "Perform DNS information gathering", "dnsAnalyzer"),
            ("Network Mapper", "Map network structure visually", "networkMapper"),
            ("Web Crawler", "Crawl websites for information", "webCrawler"),
            ("Vulnerability Scanner", "Scan for common vulnerabilities", "webVulnerability"),
            ("Password Tools", "Password generation and testing", "passwordTools")
        ]
        
        # Add tool cards to grid
        for i, (title, desc, tool_id) in enumerate(tool_cards):
            row, col = divmod(i, 3)  # 3 columns per row
            card = ToolCard(title, desc, tool_id)
            card.clicked.connect(self.on_tool_card_clicked)
            tools_grid.addWidget(card, row, col)
        
        layout.addLayout(tools_grid)
        
        # Recent activity section
        recent_section_layout = QHBoxLayout()
        
        recent_label = QLabel("Recent Activity")
        recent_label.setFont(QFont("Arial", 16))
        recent_label.setObjectName("sectionTitle")
        recent_section_layout.addWidget(recent_label)
        
        # Add clear activities button
        self.clear_activities_btn = QPushButton("Clear History")
        self.clear_activities_btn.clicked.connect(self.clear_activities)
        recent_section_layout.addStretch()
        recent_section_layout.addWidget(self.clear_activities_btn)
        
        layout.addLayout(recent_section_layout)
        
        # Recent activities container
        self.activities_container = QWidget()
        self.activities_layout = QVBoxLayout(self.activities_container)
        
        # Initial placeholder
        self.no_activity_label = QLabel("No recent activities found.")
        self.no_activity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_activity_label.setObjectName("placeholderText")
        self.activities_layout.addWidget(self.no_activity_label)
        
        layout.addWidget(self.activities_container)
        
        # Update recent activities
        self.update_recent_activities()
        
        # Add stretching space
        layout.addStretch()
        
        # Footer with welcome message
        welcome_label = QLabel("Welcome to Astra - Your Ethical Hacking Toolkit")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setObjectName("welcomeMessage")
        layout.addWidget(welcome_label)
    
    def on_tool_card_clicked(self, tool_id):
        """Handle tool card clicks by emitting the open_tool signal"""
        self.open_tool.emit(tool_id)
    
    def update_recent_activities(self):
        """Update the recent activities display"""
        # Clear current activities
        for i in reversed(range(self.activities_layout.count())):
            item = self.activities_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # Get recent activities
        activities = self.activity_tracker.get_recent_activities(limit=5)
        
        if not activities:
            # Show no activities message
            self.no_activity_label = QLabel("No recent activities found.")
            self.no_activity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.no_activity_label.setObjectName("placeholderText")
            self.activities_layout.addWidget(self.no_activity_label)
            return
        
        # Add activity items
        for activity in activities:
            activity_item = self.create_activity_item(activity)
            self.activities_layout.addWidget(activity_item)
    
    def create_activity_item(self, activity):
        """Create a widget to display an activity item"""
        item = QFrame()
        item.setFrameShape(QFrame.Shape.StyledPanel)
        item.setObjectName("activityItem")
        
        item_layout = QVBoxLayout(item)
        item_layout.setContentsMargins(10, 10, 10, 10)
        
        # Activity type and time
        header_layout = QHBoxLayout()
        
        # Icon based on activity type
        type_label = QLabel(activity["type"].capitalize())
        type_label.setObjectName("activityType")
        
        # Timestamp
        time_label = QLabel(activity["formatted_time"])
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        time_label.setObjectName("activityTime")
        
        header_layout.addWidget(type_label)
        header_layout.addWidget(time_label)
        
        # Description
        desc_label = QLabel(activity["description"])
        desc_label.setWordWrap(True)
        desc_label.setObjectName("activityDescription")
        
        item_layout.addLayout(header_layout)
        item_layout.addWidget(desc_label)
        
        # Add tool info if available
        if "tool_id" in activity:
            tool_label = QLabel(f"Tool: {self.get_tool_name(activity['tool_id'])}")
            tool_label.setObjectName("activityTool")
            item_layout.addWidget(tool_label)
        
        return item
    
    def get_tool_name(self, tool_id):
        """Get the display name for a tool ID"""
        tool_names = {
            "portScanner": "Port Scanner",
            "dnsAnalyzer": "DNS Analyzer",
            "networkMapper": "Network Mapper",
            "webCrawler": "Web Crawler",
            "webVulnerability": "Vulnerability Scanner",
            "passwordTools": "Password Tools"
        }
        return tool_names.get(tool_id, tool_id)
    
    def clear_activities(self):
        """Clear all activities history"""
        reply = QMessageBox.question(
            self, 
            "Clear Activity History",
            "Are you sure you want to clear all activity history? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.activity_tracker.clear_activities()
    
    def load_resource_widgets(self):
        """Load resource monitoring widgets"""
        # Clear current widgets
        layout = self.resource_container.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        
        # Create horizontal layout for the widgets
        resource_layout = QHBoxLayout()
        
        # Add CPU/Memory monitor
        from ui.components.dashboard_widgets import ResourceMonitor, ScanHistoryChart
        
        resource_monitor = ResourceMonitor(self)
        resource_layout.addWidget(resource_monitor, 1)
        
        # Add scan history chart
        scan_chart = ScanHistoryChart(self)
        resource_layout.addWidget(scan_chart, 1)
        
        # Add the layout to the container
        layout.addLayout(resource_layout)
