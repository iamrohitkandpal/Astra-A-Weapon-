"""
Web Crawler UI with improved performance and reset functionality
"""
import os
import json
import time
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QProgressBar, QCheckBox, QSpinBox, 
                           QTabWidget, QTextEdit, QTreeWidget, QTreeWidgetItem,
                           QSplitter, QFormLayout, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont

from tools.web_crawler import WebCrawlerWorker
from utils.ui_utils import add_reset_button_to_layout
from utils.activity_tracker import ActivityTracker, ActivityType
from ui.components.log_panel import LogPanel, LogLevel

class WebCrawlerTool(QWidget):
    """Web crawler tool for scanning websites"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.worker_thread = None
        self.crawl_in_progress = False
        self.setup_ui()
        
        # Activity tracker
        self.activity_tracker = ActivityTracker()
    
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("Web Crawler")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Description
        desc = QLabel(
            "Crawl websites to discover links, assets, and site structure. "
            "Use this tool to map out a website or gather information."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Input form
        form_layout = QFormLayout()
        
        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter website URL (e.g., https://example.com)")
        form_layout.addRow("Target URL:", self.url_input)
        
        # Max URLs to crawl
        self.max_urls_spin = QSpinBox()
        self.max_urls_spin.setRange(10, 1000)
        self.max_urls_spin.setValue(100)
        self.max_urls_spin.setSingleStep(10)
        form_layout.addRow("Max URLs to crawl:", self.max_urls_spin)
        
        # Max depth
        self.max_depth_spin = QSpinBox()
        self.max_depth_spin.setRange(1, 10)
        self.max_depth_spin.setValue(3)
        form_layout.addRow("Max depth level:", self.max_depth_spin)
        
        # Stay within domain
        self.stay_in_domain = QCheckBox("Stay within same domain")
        self.stay_in_domain.setChecked(True)
        form_layout.addRow("", self.stay_in_domain)
        
        layout.addLayout(form_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start Crawling")
        self.start_button.clicked.connect(self.start_crawl)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_crawl)
        self.stop_button.setEnabled(False)
        
        self.export_button = QPushButton("Export Results")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.export_button)
        
        layout.addLayout(button_layout)
        
        # Add reset button - reset all fields to default
        add_reset_button_to_layout(layout, self.reset_tool)
        
        # Results tabs
        self.results_tabs = QTabWidget()
        
        # Create tab for discovered URLs
        self.urls_tree = QTreeWidget()
        self.urls_tree.setHeaderLabels(["URL", "Type"])
        self.results_tabs.addTab(self.urls_tree, "Discovered URLs")
        
        # Create tab for log output
        self.log_panel = LogPanel()
        self.results_tabs.addTab(self.log_panel, "Logs")
        
        # Create tab for crawl summary
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.results_tabs.addTab(self.summary_text, "Summary")
        
        layout.addWidget(self.results_tabs, 1)  # Give it stretch factor
    
    def start_crawl(self):
        """Start the crawling process"""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Required", "Please enter a URL to crawl.")
            return
        
        # Clear previous results
        self.clear_results()
        
        # Update UI
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.export_button.setEnabled(False)
        self.crawl_in_progress = True
        
        # Create worker
        self.worker = WebCrawlerWorker()
        
        # Connect signals
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.url_discovered.connect(self.add_url)
        self.worker.log_message.connect(self.log_message)
        self.worker.error_occurred.connect(self.log_error)
        self.worker.crawl_complete.connect(self.crawl_complete)
        
        # Get settings
        max_urls = self.max_urls_spin.value()
        max_depth = self.max_depth_spin.value()
        stay_within_domain = self.stay_in_domain.isChecked()
        
        # Log start
        self.log_panel.add_log(LogLevel.INFO, f"Starting crawl of {url}")
        self.log_panel.add_log(LogLevel.INFO, f"Settings: Max URLs: {max_urls}, Max Depth: {max_depth}, Stay in Domain: {stay_within_domain}")
        
        # Start worker in a thread
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(lambda: self.worker.start_crawl(url, max_urls, max_depth, stay_within_domain))
        self.worker_thread.start()
        
        # Log to activity tracker
        self.activity_tracker.log_activity(
            ActivityType.SCAN, 
            f"Web Crawl of {url}", 
            {"max_urls": max_urls, "max_depth": max_depth}, 
            "webCrawler"
        )
    
    def stop_crawl(self):
        """Stop the crawling process"""
        if self.worker and self.crawl_in_progress:
            self.log_panel.add_log(LogLevel.WARNING, "Stopping crawl...")
            self.worker.stop_crawl()
            
            # Update UI
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.export_button.setEnabled(True)
            self.crawl_in_progress = False
    
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_bar.setValue(value)
    
    def add_url(self, url):
        """Add a discovered URL to the tree"""
        item = QTreeWidgetItem([url, self._determine_url_type(url)])
        self.urls_tree.addTopLevelItem(item)
        
        # Auto scroll to keep latest items visible
        self.urls_tree.scrollToItem(item)
    
    def _determine_url_type(self, url):
        """Determine the type of URL"""
        lower_url = url.lower()
        if lower_url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            return "Image"
        elif lower_url.endswith('.css'):
            return "Stylesheet"
        elif lower_url.endswith('.js'):
            return "JavaScript"
        elif lower_url.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx')):
            return "Document"
        else:
            return "Page"
    
    def log_message(self, message):
        """Add a log message"""
        self.log_panel.add_log(LogLevel.INFO, message)
    
    def log_error(self, error):
        """Add an error message"""
        self.log_panel.add_log(LogLevel.ERROR, error)
    
    def crawl_complete(self, results):
        """Handle crawl completion"""
        # Update UI
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.export_button.setEnabled(True)
        self.crawl_in_progress = False
        
        # Store results
        self.crawl_results = results
        
        # Update summary
        self.update_summary(results)
        
        # Switch to summary tab
        self.results_tabs.setCurrentIndex(2)  # Summary tab
        
        # Log completion
        self.log_panel.add_log(LogLevel.SUCCESS, "Crawl completed successfully.")
        
        # Update activity tracker
        url = self.url_input.text().strip()
        self.activity_tracker.log_activity(
            ActivityType.REPORT, 
            f"Web Crawl of {url} completed", 
            {"urls_discovered": len(results['discovered_urls'])}, 
            "webCrawler"
        )
    
    def update_summary(self, results):
        """Update the summary text with crawl results"""
        summary = f"""
        <h2>Crawl Summary</h2>
        
        <p><b>URLs Visited:</b> {len(results['visited_urls'])}</p>
        <p><b>URLs Discovered:</b> {len(results['discovered_urls'])}</p>
        <p><b>External Links:</b> {len(results['external_links'])}</p>
        
        <h3>Resources</h3>
        <p><b>Images:</b> {len(results['resources']['images'])}</p>
        <p><b>Scripts:</b> {len(results['resources']['scripts'])}</p>
        <p><b>Stylesheets:</b> {len(results['resources']['stylesheets'])}</p>
        <p><b>Documents:</b> {len(results['resources']['documents'])}</p>
        
        <h3>Status Codes</h3>
        """
        
        # Count status codes
        status_counts = {}
        for status in results['status_codes'].values():
            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts[status] = 1
        
        # Add status code counts to summary
        for status, count in sorted(status_counts.items()):
            summary += f"<p><b>Status {status}:</b> {count}</p>"
        
        self.summary_text.setHtml(summary)
    
    def export_results(self):
        """Export the crawl results to file"""
        if not hasattr(self, 'crawl_results'):
            QMessageBox.warning(self, "No Results", "There are no crawl results to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Crawl Results", "", "JSON Files (*.json);;HTML Report (*.html);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.lower().endswith('.html'):
                self.export_html_report(file_path)
            else:
                # Default to JSON
                with open(file_path, 'w') as f:
                    json.dump(self.crawl_results, f, indent=4)
            
            QMessageBox.information(self, "Export Successful", f"Results exported to {file_path}")
            
            # Log to activity tracker
            self.activity_tracker.log_activity(
                ActivityType.EXPORT, 
                f"Exported web crawl results", 
                {"file_path": file_path}, 
                "webCrawler"
            )
            
            # Log to panel
            self.log_panel.add_log(LogLevel.SUCCESS, f"Results exported to {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export results: {str(e)}")
            self.log_panel.add_log(LogLevel.ERROR, f"Export failed: {str(e)}")
    
    def export_html_report(self, file_path):
        """Export results as an HTML report"""
        results = self.crawl_results
        
        # Create an HTML report
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Web Crawler Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .summary {{ background-color: #eef; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Web Crawler Report</h1>
            <p>Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><b>URLs Visited:</b> {len(results['visited_urls'])}</p>
                <p><b>URLs Discovered:</b> {len(results['discovered_urls'])}</p>
                <p><b>External Links:</b> {len(results['external_links'])}</p>
                
                <h3>Resources</h3>
                <p><b>Images:</b> {len(results['resources']['images'])}</p>
                <p><b>Scripts:</b> {len(results['resources']['scripts'])}</p>
                <p><b>Stylesheets:</b> {len(results['resources']['stylesheets'])}</p>
                <p><b>Documents:</b> {len(results['resources']['documents'])}</p>
            </div>
            
            <h2>Visited URLs</h2>
            <table>
                <tr>
                    <th>URL</th>
                    <th>Title</th>
                </tr>
        """
        
        # Add visited URLs
        for url in results['visited_urls']:
            title = results.get('page_titles', {}).get(url, "")
            html += f"<tr><td>{url}</td><td>{title}</td></tr>"
        
        html += """
            </table>
            
            <h2>External Links</h2>
            <table>
                <tr>
                    <th>URL</th>
                </tr>
        """
        
        # Add external links
        for url in results['external_links']:
            html += f"<tr><td>{url}</td></tr>"
        
        html += """
            </table>
            
            <h2>Resources</h2>
            <h3>Images</h3>
            <table>
                <tr>
                    <th>URL</th>
                </tr>
        """
        
        # Add images
        for url in results['resources']['images']:
            html += f"<tr><td>{url}</td></tr>"
        
        html += """
            </table>
            
            <h3>Scripts</h3>
            <table>
                <tr>
                    <th>URL</th>
                </tr>
        """
        
        # Add scripts
        for url in results['resources']['scripts']:
            html += f"<tr><td>{url}</td></tr>"
        
        html += """
            </table>
            
            <h3>Stylesheets</h3>
            <table>
                <tr>
                    <th>URL</th>
                </tr>
        """
        
        # Add stylesheets
        for url in results['resources']['stylesheets']:
            html += f"<tr><td>{url}</td></tr>"
        
        html += """
            </table>
            
            <h3>Documents</h3>
            <table>
                <tr>
                    <th>URL</th>
                </tr>
        """
        
        # Add documents
        for url in results['resources']['documents']:
            html += f"<tr><td>{url}</td></tr>"
        
        html += """
            </table>
        </body>
        </html>
        """
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def clear_results(self):
        """Clear all current results"""
        # Clear tree widget
        self.urls_tree.clear()
        
        # Clear logs
        self.log_panel.clear_logs()
        
        # Clear summary
        self.summary_text.clear()
        
        # Reset progress bar
        self.progress_bar.setValue(0)
        
        # Reset crawl results
        if hasattr(self, 'crawl_results'):
            delattr(self, 'crawl_results')
    
    def reset_tool(self):
        """Reset the tool to default state"""
        # Stop any crawling in progress
        if self.crawl_in_progress:
            self.stop_crawl()
        
        # Clear results
        self.clear_results()
        
        # Reset input fields
        self.url_input.clear()
        self.max_urls_spin.setValue(100)
        self.max_depth_spin.setValue(3)
        self.stay_in_domain.setChecked(True)
        
        # Reset buttons
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.export_button.setEnabled(False)
        
        # Log reset
        self.log_panel.add_log(LogLevel.INFO, "Tool has been reset to default state.")
