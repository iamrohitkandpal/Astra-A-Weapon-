"""
Help page for Astra application
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTabWidget, 
                             QTextBrowser, QScrollArea, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

class HelpPage(QWidget):
    """Help page providing documentation for Astra tools"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the help UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Help & Documentation")
        header_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Learn how to use Astra's tools effectively")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Create tab widget for different help sections
        self.tabs = QTabWidget()
        
        # Add tabs for each tool
        self.tabs.addTab(self.create_overview_tab(), "Overview")
        self.tabs.addTab(self.create_port_scanner_tab(), "Port Scanner")
        self.tabs.addTab(self.create_dns_analyzer_tab(), "DNS Analyzer")
        self.tabs.addTab(self.create_subdomain_tab(), "Subdomain Enum")
        self.tabs.addTab(self.create_web_vuln_tab(), "Web Vulnerability Scanner")
        self.tabs.addTab(self.create_ssl_checker_tab(), "SSL/TLS Checker")
        self.tabs.addTab(self.create_theme_editor_tab(), "Theme Editor")
        
        layout.addWidget(self.tabs)
    
    def create_overview_tab(self):
        """Create content for the overview tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QTextBrowser()
        content.setOpenExternalLinks(True)
        
        html_content = """
        <h2>Welcome to Astra - Ethical Hacking Toolkit</h2>
        
        <p>Astra is an educational desktop application designed to help you learn and practice ethical hacking techniques and network security assessment in a safe, controlled environment.</p>
        
        <h3>Getting Started</h3>
        
        <p>The application is organized into several key tools accessible from the sidebar:</p>
        
        <ul>
            <li><strong>Port Scanner</strong> - Scan systems for open ports</li>
            <li><strong>DNS Analyzer</strong> - Analyze DNS records for domains</li>
            <li><strong>Subdomain Enum</strong> - Discover subdomains for a target domain</li>
            <li><strong>Vulnerability Scanner</strong> - Check websites for security issues</li>
            <li><strong>SSL/TLS Checker</strong> - Validate security of TLS configurations</li>
        </ul>
        
        <p>Each tool provides a specific set of functionality related to different aspects of cybersecurity assessment.</p>
        
        <h3>Ethical Use</h3>
        
        <p><strong>Important:</strong> Always obtain proper authorization before scanning or testing any systems. Use Astra only on systems you own or have explicit permission to test.</p>
        
        <h3>Navigation</h3>
        
        <p>Use the sidebar to navigate between different tools. Each tool has its own dedicated interface with specific options and settings.</p>
        
        <h3>Customization</h3>
        
        <p>You can customize the application's appearance using the Theme Editor, accessible from the sidebar. Choose from built-in themes or create your own custom themes.</p>
        
        <h3>Need Help?</h3>
        
        <p>For detailed information about each tool, click on the corresponding tab in this Help section.</p>
        """
        
        content.setHtml(html_content)
        scroll.setWidget(content)
        return scroll
    
    def create_port_scanner_tab(self):
        """Create content for port scanner help tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QTextBrowser()
        content.setOpenExternalLinks(True)
        
        html_content = """
        <h2>Port Scanner</h2>
        
        <p>The Port Scanner allows you to scan target systems for open network ports, helping identify running services and potential entry points.</p>
        
        <h3>How to Use</h3>
        
        <ol>
            <li><strong>Target</strong>: Enter the hostname or IP address you want to scan (e.g., example.com or 192.168.1.1)</li>
            <li><strong>Port Range</strong>: Select the range of ports to scan
                <ul>
                    <li>Common ranges: 1-1000 for common services, 1-65535 for all ports</li>
                    <li>Smaller ranges complete faster</li>
                </ul>
            </li>
            <li><strong>Timeout</strong>: Set the connection timeout in seconds (1-10)</li>
            <li>Click <strong>Start Scan</strong> to begin scanning</li>
        </ol>
        
        <h3>Results Interpretation</h3>
        
        <ul>
            <li><span style="color: green;"><strong>Open</strong></span> - The port is open and accepting connections</li>
            <li><span style="color: red;"><strong>Closed</strong></span> - The port is not accessible</li>
            <li><strong>Service</strong> - The likely service running on the port (based on common port assignments)</li>
        </ul>
        
        <h3>Performance Tips</h3>
        
        <ul>
            <li>Scan smaller port ranges for faster results</li>
            <li>Reduce timeout for faster scanning (but may miss slower-responding ports)</li>
            <li>Scanning from within the same network provides more accurate results</li>
        </ul>
        
        <h3>Example Use Cases</h3>
        
        <ul>
            <li>Identifying exposed services on your server</li>
            <li>Checking firewall configuration effectiveness</li>
            <li>Finding unexpected open ports that may indicate security issues</li>
        </ul>
        
        <h3>Limitations</h3>
        
        <ul>
            <li>Some firewalls and IDS systems may block or detect port scans</li>
            <li>Results show port status only from your current network perspective</li>
            <li>Service identification is based on common port assignments and may not be 100% accurate</li>
        </ul>
        """
        
        content.setHtml(html_content)
        scroll.setWidget(content)
        return scroll
    
    def create_dns_analyzer_tab(self):
        """Create content for DNS analyzer help tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QTextBrowser()
        content.setOpenExternalLinks(True)
        
        html_content = """
        <h2>DNS Analyzer</h2>
        
        <p>The DNS Analyzer allows you to query various DNS record types for a domain, providing insights into its DNS configuration and network setup.</p>
        
        <h3>How to Use</h3>
        
        <ol>
            <li><strong>Domain</strong>: Enter the domain name you want to analyze (e.g., example.com)</li>
            <li><strong>Record Types</strong>: Select the DNS record types you want to query:
                <ul>
                    <li><strong>A</strong> - IPv4 addresses for the domain</li>
                    <li><strong>AAAA</strong> - IPv6 addresses for the domain</li>
                    <li><strong>MX</strong> - Mail exchange servers</li>
                    <li><strong>NS</strong> - Nameservers responsible for the domain</li>
                    <li><strong>TXT</strong> - Text records (often used for SPF, DKIM, verification)</li>
                    <li><strong>SOA</strong> - Start of Authority record</li>
                    <li><strong>CNAME</strong> - Canonical name records (aliases)</li>
                    <li><strong>PTR</strong> - Pointer records (reverse DNS)</li>
                    <li><strong>SRV</strong> - Service records</li>
                    <li><strong>CAA</strong> - Certificate Authority Authorization records</li>
                </ul>
            </li>
            <li>Click <strong>Query DNS</strong> to retrieve the records</li>
        </ol>
        
        <h3>Results Interpretation</h3>
        
        <p>The results table shows three columns:</p>
        <ul>
            <li><strong>Domain</strong> - The queried domain name</li>
            <li><strong>Record Type</strong> - The type of DNS record</li>
            <li><strong>Value</strong> - The actual record content</li>
        </ul>
        
        <h3>Common Use Cases</h3>
        
        <ul>
            <li><strong>Email Configuration Analysis</strong> - Check MX, SPF, and DKIM records</li>
            <li><strong>Server Infrastructure</strong> - Analyze A, AAAA, and CNAME records</li>
            <li><strong>Security Verification</strong> - Examine TXT and CAA records</li>
            <li><strong>Domain Administration</strong> - Review NS and SOA records</li>
        </ul>
        
        <h3>Tips</h3>
        
        <ul>
            <li>Select only the record types you need to speed up query times</li>
            <li>TXT records often contain valuable information about domain configuration and security policies</li>
            <li>Compare NS records with the domain registrar's settings to ensure consistency</li>
        </ul>
        """
        
        content.setHtml(html_content)
        scroll.setWidget(content)
        return scroll
    
    def create_subdomain_tab(self):
        """Create content for subdomain enumeration help tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QTextBrowser()
        content.setOpenExternalLinks(True)
        
        html_content = """
        <h2>Subdomain Enumeration</h2>
        
        <p>The Subdomain Enumeration tool discovers subdomains associated with a target domain using various techniques including brute force and Amass integration (if available).</p>
        
        <h3>How to Use</h3>
        
        <ol>
            <li><strong>Domain</strong>: Enter the target domain to scan for subdomains (e.g., example.com)</li>
            <li><strong>Wordlist</strong>: Choose between:
                <ul>
                    <li><strong>Default wordlist</strong> - A built-in list of common subdomain names</li>
                    <li><strong>Custom wordlist</strong> - Upload your own list of potential subdomains</li>
                </ul>
            </li>
            <li><strong>Thread Count</strong>: Set the number of concurrent threads (higher = faster but more resource-intensive)</li>
            <li>Click <strong>Start Enumeration</strong> to begin the discovery process</li>
        </ol>
        
        <h3>Advanced Features</h3>
        
        <ul>
            <li><strong>Amass Integration</strong>: If Amass is installed on your system, Astra can use it for more comprehensive subdomain discovery</li>
            <li><strong>DNS Verification</strong>: Each discovered subdomain is verified via DNS resolution</li>
            <li><strong>IP Resolution</strong>: Discovered subdomains are resolved to their IP addresses when possible</li>
        </ul>
        
        <h3>Results Interpretation</h3>
        
        <ul>
            <li><strong>Subdomain</strong> - The discovered subdomain name</li>
            <li><strong>IP Address</strong> - The resolved IP address (if resolution was successful)</li>
            <li>"Could not resolve" indicates the subdomain name exists in DNS but doesn't resolve to an IP</li>
        </ul>
        
        <h3>Creating Effective Wordlists</h3>
        
        <p>For custom wordlists:</p>
        <ul>
            <li>Include common subdomain prefixes (www, mail, blog, api, etc.)</li>
            <li>Add organization-specific terms (company names, products, services)</li>
            <li>Consider including numbered patterns (test1, test2, etc.)</li>
            <li>One potential subdomain per line in a plain text file</li>
        </ul>
        
        <h3>Performance Considerations</h3>
        
        <ul>
            <li>Larger wordlists will take longer to process</li>
            <li>Higher thread counts speed up enumeration but increase system load</li>
            <li>Extensive enumeration may trigger rate limiting or alerting on target DNS servers</li>
        </ul>
        """
        
        content.setHtml(html_content)
        scroll.setWidget(content)
        return scroll
    
    def create_web_vuln_tab(self):
        """Create content for web vulnerability scanner help tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QTextBrowser()
        content.setOpenExternalLinks(True)
        
        html_content = """
        <h2>Web Vulnerability Scanner</h2>
        
        <p>The Web Vulnerability Scanner checks websites for common security issues including cross-site scripting (XSS), SQL injection vulnerabilities, missing security headers, and information disclosure.</p>
        
        <h3>How to Use</h3>
        
        <ol>
            <li><strong>URL</strong>: Enter the website URL to scan (e.g., https://example.com)</li>
            <li><strong>Scan Options</strong>: Select which vulnerabilities to check for:
                <ul>
                    <li><strong>Thorough Scan</strong> - More comprehensive but slower scan</li>
                    <li><strong>XSS Vulnerabilities</strong> - Check for cross-site scripting issues</li>
                    <li><strong>SQL Injection</strong> - Test for SQL injection vulnerabilities</li>
                    <li><strong>Security Headers</strong> - Check for missing HTTP security headers</li>
                    <li><strong>Information Disclosure</strong> - Look for exposed sensitive information</li>
                </ul>
            </li>
            <li>Click <strong>Start Scan</strong> to begin the security assessment</li>
        </ol>
        
        <h3>Results Interpretation</h3>
        
        <p>The results table shows:</p>
        <ul>
            <li><strong>Vulnerability</strong> - The type of security issue found</li>
            <li><strong>URL</strong> - The specific URL where the vulnerability was detected</li>
            <li><strong>Description</strong> - Details about the vulnerability</li>
            <li><strong>Severity</strong> - Impact rating (High, Medium, Low)</li>
        </ul>
        
        <h3>Understanding Severity Levels</h3>
        
        <ul>
            <li><strong style="color: #cc0000;">High</strong> - Critical issues that require immediate attention</li>
            <li><strong style="color: #e67e00;">Medium</strong> - Important issues that should be addressed soon</li>
            <li><strong style="color: #007700;">Low</strong> - Minor issues that represent best practice improvements</li>
        </ul>
        
        <h3>Vulnerability Types Explained</h3>
        
        <ul>
            <li><strong>XSS (Cross-Site Scripting)</strong> - Allows attackers to inject malicious scripts into web pages</li>
            <li><strong>SQL Injection</strong> - Allows attackers to interfere with database queries</li>
            <li><strong>Missing Security Headers</strong> - Absence of HTTP headers that enhance security</li>
            <li><strong>Information Disclosure</strong> - Sensitive information exposed in page content or headers</li>
        </ul>
        
        <h3>Limitations</h3>
        
        <ul>
            <li>The scanner performs basic checks and may not detect all vulnerabilities</li>
            <li>False positives are possible - always verify findings manually</li>
            <li>Some websites may block or rate-limit scanning attempts</li>
            <li>The scanner does not exploit vulnerabilities, only detects potential issues</li>
        </ul>
        
        <h3>Recommendations</h3>
        
        <ul>
            <li>Always scan your own websites or those you have permission to test</li>
            <li>Address high severity issues first</li>
            <li>Implement recommended security headers for all web applications</li>
            <li>Regular scanning helps maintain security posture over time</li>
        </ul>
        """
        
        content.setHtml(html_content)
        scroll.setWidget(content)
        return scroll
    
    def create_ssl_checker_tab(self):
        """Create content for SSL/TLS checker help tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QTextBrowser()
        content.setOpenExternalLinks(True)
        
        html_content = """
        <h2>SSL/TLS Checker</h2>
        
        <p>The SSL/TLS Checker analyzes a website's SSL/TLS configuration to identify security issues, certificate problems, and best practice violations.</p>
        
        <h3>How to Use</h3>
        
        <ol>
            <li><strong>Hostname</strong>: Enter the domain name to check (e.g., example.com)</li>
            <li><strong>Port</strong>: Specify the port (default is 443 for HTTPS)</li>
            <li>Click <strong>Check Security</strong> to analyze the SSL/TLS configuration</li>
        </ol>
        
        <h3>Results Interpretation</h3>
        
        <p>The checker provides a comprehensive report including:</p>
        
        <h4>Connection Information</h4>
        <ul>
            <li><strong>Hostname</strong> - The target domain name</li>
            <li><strong>Port</strong> - The port used for the connection</li>
            <li><strong>Protocol</strong> - The SSL/TLS protocol version in use</li>
            <li><strong>Protocol Security</strong> - Assessment of the protocol security</li>
            <li><strong>Cipher Suite</strong> - The encryption algorithm combination used</li>
            <li><strong>Cipher Bits</strong> - The encryption key length</li>
        </ul>
        
        <h4>Certificate Information</h4>
        <ul>
            <li><strong>Subject</strong> - Who the certificate was issued to</li>
            <li><strong>Issuer</strong> - The certificate authority that issued the certificate</li>
            <li><strong>Valid From/Until</strong> - Certificate validity period</li>
            <li><strong>Expiration Status</strong> - Whether the certificate is valid, expired, or nearing expiration</li>
            <li><strong>Technical Details</strong> - Version, serial number, and signature algorithm</li>
        </ul>
        
        <h4>Security Assessment</h4>
        <ul>
            <li><strong>Overall Security Rating</strong> - A general assessment of the configuration security</li>
            <li><strong>Recommendations</strong> - Specific advice for improving security</li>
        </ul>
        
        <h3>Common Issues</h3>
        
        <ul>
            <li><strong>Outdated Protocols</strong> - SSLv2, SSLv3, TLSv1.0, and TLSv1.1 are considered insecure</li>
            <li><strong>Weak Ciphers</strong> - Cipher suites with less than 128-bit encryption</li>
            <li><strong>Certificate Problems</strong> - Expired certificates, self-signed certificates, or wrong domain</li>
            <li><strong>Missing HSTS</strong> - Strict Transport Security header not implemented</li>
        </ul>
        
        <h3>Best Practices</h3>
        
        <ul>
            <li>Use TLSv1.2 or TLSv1.3 protocols only</li>
            <li>Implement strong cipher suites (256-bit encryption when possible)</li>
            <li>Keep certificates up to date (renew at least 30 days before expiration)</li>
            <li>Implement HSTS to prevent downgrade attacks</li>
            <li>Use certificates from trusted certificate authorities</li>
        </ul>
        
        <h3>Troubleshooting</h3>
        
        <p>If the checker fails to connect:</p>
        <ul>
            <li>Verify the hostname is correct</li>
            <li>Check if the server is online and accessible</li>
            <li>Ensure the correct port is specified</li>
            <li>Confirm your network allows the connection</li>
        </ul>
        """
        
        content.setHtml(html_content)
        scroll.setWidget(content)
        return scroll
    
    def create_theme_editor_tab(self):
        """Create content for theme editor help tab"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        content = QTextBrowser()
        content.setOpenExternalLinks(True)
        
        html_content = """
        <h2>Theme Editor</h2>
        
        <p>The Theme Editor allows you to customize the appearance of Astra by modifying existing themes or creating your own.</p>
        
        <h3>How to Use</h3>
        
        <h4>Working with Existing Themes</h4>
        <ol>
            <li><strong>Select Theme</strong>: Choose a theme from the dropdown menu</li>
            <li><strong>Load</strong>: Click "Load" to load the theme for editing</li>
            <li><strong>Modify</strong>: Make changes to colors and other properties</li>
            <li><strong>Save</strong>: Click "Save Theme" to update the theme</li>
            <li><strong>Apply</strong>: Click "Apply Theme" to use the theme immediately</li>
        </ol>
        
        <h4>Creating a New Theme</h4>
        <ol>
            <li>Click <strong>New Theme</strong> button</li>
            <li>Enter a name for your theme</li>
            <li>Click <strong>Create</strong></li>
            <li>Customize colors and settings</li>
            <li>Save and apply your new theme</li>
        </ol>
        
        <h3>Theme Components</h3>
        
        <h4>Basic Colors Tab</h4>
        <ul>
            <li><strong>Window Colors</strong> - Main application window background and text</li>
            <li><strong>Sidebar Colors</strong> - Navigation sidebar appearance</li>
            <li><strong>Button Colors</strong> - Button states (normal, hover, checked, disabled)</li>
            <li><strong>Input Controls</strong> - Text fields, dropdowns, and other input elements</li>
            <li><strong>Table Colors</strong> - Result tables appearance</li>
        </ul>
        
        <h4>Advanced Settings Tab</h4>
        <ul>
            <li><strong>Font Family</strong> - Choose typography for the interface</li>
            <li><strong>Border Radius</strong> - Adjust the roundness of UI elements</li>
            <li><strong>JSON Preview</strong> - View and edit the theme's raw JSON data</li>
        </ul>
        
        <h3>Theme Management</h3>
        
        <ul>
            <li><strong>Export Theme</strong> - Save a theme to a JSON file to share or backup</li>
            <li><strong>Import Theme</strong> - Load a theme from a JSON file</li>
            <li><strong>Delete Theme</strong> - Remove a custom theme (note: default themes cannot be deleted)</li>
        </ul>
        
        <h3>Tips for Creating Great Themes</h3>
        
        <ul>
            <li>Maintain good contrast between text and background colors for readability</li>
            <li>Use a consistent color palette (3-5 main colors)</li>
            <li>Consider accessibility - extreme color combinations may be difficult for some users</li>
            <li>Test your theme with different tools to ensure good visibility</li>
            <li>The "Apply Theme" button lets you preview changes without saving</li>
        </ul>
        
        <h3>Default Themes</h3>
        
        <ul>
            <li><strong>Dark</strong> - A modern dark interface with blue accents</li>
            <li><strong>Light</strong> - A clean, bright interface with good contrast</li>
            <li><strong>Hacker</strong> - A classic terminal-inspired theme with green text on black</li>
        </ul>
        """
        
        content.setHtml(html_content)
        scroll.setWidget(content)
        return scroll
