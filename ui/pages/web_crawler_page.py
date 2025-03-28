"""
Web Crawler page for Astra
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from ui.tools.web_crawler_tool import WebCrawlerTool

class WebCrawlerPage(QWidget):
    """Web crawler page for scanning websites and mapping site structure"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create and add the web crawler tool
        self.crawler_tool = WebCrawlerTool()
        layout.addWidget(self.crawler_tool)
