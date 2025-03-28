"""
Report generator for Astra tool outputs
"""

import os
import time
from datetime import datetime
import webbrowser
import json

try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

class ReportGenerator:
    """Generate reports from scan results"""
    
    def __init__(self):
        # Create reports directory if it doesn't exist
        self.reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_pdf_report(self, title, results, scan_type, target):
        """
        Generate a PDF report
        
        Args:
            title (str): Report title
            results (list): Scan results
            scan_type (str): Type of scan performed
            target (str): Scan target (e.g., URL, hostname)
            
        Returns:
            str: Path to the generated PDF file
        """
        if not PDF_AVAILABLE:
            raise ImportError("fpdf module not installed. Install it with 'pip install fpdf'")
            
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Set up title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, title, 0, 1, "C")
        
        # Date and time
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "R")
        
        # Scan details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Scan Details", 0, 1)
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Scan Type: {scan_type}", 0, 1)
        pdf.cell(0, 6, f"Target: {target}", 0, 1)
        
        # Results
        if results:
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, "Scan Results", 0, 1)
            
            # Add each result
            for i, result in enumerate(results, 1):
                pdf.set_font("Arial", "B", 10)
                
                # Handle different result formats
                if isinstance(result, dict):
                    # For JSON/dict format
                    vulnerability = result.get('type', 'Unknown')
                    vulnerability_url = result.get('url', 'N/A')
                    description = result.get('description', 'No description')
                    severity = result.get('severity', 'Unknown')
                elif isinstance(result, tuple) and len(result) >= 3:
                    # For tuple format (vulnerability, url, description, [severity])
                    vulnerability = result[0]
                    vulnerability_url = result[1]
                    description = result[2]
                    severity = result[3] if len(result) > 3 else 'Unknown'
                else:
                    # Generic fallback
                    vulnerability = "Unknown"
                    vulnerability_url = "N/A"
                    description = str(result)
                    severity = "Unknown"
                
                # Add result header
                pdf.cell(0, 10, f"Finding #{i}: {vulnerability} [{severity}]", 0, 1)
                
                # Add details
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, f"URL: {vulnerability_url}", 0, 1)
                
                # Add wrapped description
                pdf.multi_cell(0, 6, f"Description: {description}")
                
                # Add separator
                pdf.cell(0, 6, "", 0, 1)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.cell(0, 6, "", 0, 1)
        else:
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 10, "No vulnerabilities found.", 0, 1)
        
        # Save the PDF
        timestamp = int(time.time())
        filename = f"{scan_type.replace(' ', '_').lower()}_{timestamp}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        pdf.output(filepath)
        
        return filepath
    
    def generate_html_report(self, title, results, scan_type, target):
        """
        Generate an HTML report
        
        Args:
            title (str): Report title
            results (list): Scan results
            scan_type (str): Type of scan performed
            target (str): Scan target (e.g., URL, hostname)
            
        Returns:
            str: Path to the generated HTML file
        """
        # Create HTML content
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; margin-top: 30px; }}
                .details {{ background-color: #f8f9fa; padding: 10px; border-radius: 5px; }}
                .result {{ background-color: #fff; border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
                .severity-HIGH {{ color: #e74c3c; }}
                .severity-MEDIUM {{ color: #f39c12; }}
                .severity-LOW {{ color: #27ae60; }}
                .severity-UNKNOWN {{ color: #7f8c8d; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="details">
                <h2>Scan Details</h2>
                <p><strong>Scan Type:</strong> {scan_type}</p>
                <p><strong>Target:</strong> {target}</p>
            </div>
            
            <h2>Scan Results</h2>
        """
        
        if results:
            html += "<div class='results'>"
            
            for i, result in enumerate(results, 1):
                # Handle different result formats
                if isinstance(result, dict):
                    # For JSON/dict format
                    vulnerability = result.get('type', 'Unknown')
                    vulnerability_url = result.get('url', 'N/A')
                    description = result.get('description', 'No description')
                    severity = result.get('severity', 'Unknown')
                elif isinstance(result, tuple) and len(result) >= 3:
                    # For tuple format (vulnerability, url, description, [severity])
                    vulnerability = result[0]
                    vulnerability_url = result[1]
                    description = result[2]
                    severity = result[3] if len(result) > 3 else 'Unknown'
                else:
                    # Generic fallback
                    vulnerability = "Unknown"
                    vulnerability_url = "N/A"
                    description = str(result)
                    severity = "Unknown"
                
                html += f"""
                <div class="result">
                    <h3>Finding #{i}: <span class="severity-{severity}">{vulnerability} [{severity}]</span></h3>
                    <p><strong>URL:</strong> {vulnerability_url}</p>
                    <p><strong>Description:</strong><br>{description.replace('\n', '<br>')}</p>
                </div>
                """
            
            html += "</div>"
        else:
            html += "<p>No vulnerabilities found.</p>"
        
        html += """
        </body>
        </html>
        """
        
        # Save the HTML
        timestamp = int(time.time())
        filename = f"{scan_type.replace(' ', '_').lower()}_{timestamp}.html"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Open in browser
        webbrowser.open(f"file://{filepath}")
        
        return filepath
        
    def generate_enhanced_pdf_report(self, title, results, scan_type, target, summary=None):
        """
        Generate an enhanced PDF report with AI-generated content
        
        Args:
            title (str): Report title
            results (list): Scan results with enhanced AI data
            scan_type (str): Type of scan performed
            target (str): Scan target (e.g., URL, hostname)
            summary (str): Executive summary
            
        Returns:
            str: Path to the generated PDF file
        """
        if not PDF_AVAILABLE:
            raise ImportError("fpdf module not installed. Install it with 'pip install fpdf'")
            
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Set up title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, title, 0, 1, "C")
        
        # Date and time
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "R")
        
        # Executive summary if provided
        if summary:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Executive Summary", 0, 1)
            
            pdf.set_font("Arial", "", 10)
            for line in summary.split('\n'):
                pdf.multi_cell(0, 6, line)
                
            pdf.cell(0, 6, "", 0, 1)  # Add some space
        
        # Scan details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Scan Details", 0, 1)
        
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Scan Type: {scan_type}", 0, 1)
        pdf.cell(0, 6, f"Target: {target}", 0, 1)
        
        # Count severity levels
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'UNKNOWN': 0}
        for result in results:
            if isinstance(result, dict):
                severity = result.get('severity', 'UNKNOWN')
            else:
                severity = result[3] if len(result) > 3 else 'UNKNOWN'
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Add severity summary
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Risk Summary", 0, 1)
        
        pdf.set_font("Arial", "", 10)
        for severity, count in severity_counts.items():
            if count > 0:
                pdf.cell(0, 6, f"{severity}: {count}", 0, 1)
        
        # Results
        if results:
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Vulnerability Details", 0, 1)
            
            # Sort results by risk score if available, then by severity
            sorted_results = sorted(
                results,
                key=lambda r: (
                    -(r.get('risk_score', 0) if isinstance(r, dict) else 0),
                    {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'UNKNOWN': 4}.get(
                        r.get('severity', 'UNKNOWN') if isinstance(r, dict) else r[3] if len(r) > 3 else 'UNKNOWN',
                        5
                    )
                )
            )
            
            # Add each result
            for i, result in enumerate(sorted_results, 1):
                pdf.set_font("Arial", "B", 12)
                
                # Handle different result formats
                if isinstance(result, dict):
                    # For JSON/dict format
                    vulnerability = result.get('type', 'Unknown')
                    vulnerability_url = result.get('url', 'N/A')
                    description = result.get('description', 'No description')
                    severity = result.get('severity', 'Unknown')
                    risk_score = result.get('risk_score', 'N/A')
                else:
                    # For tuple format (vulnerability, url, description, severity)
                    vulnerability = result[0]
                    vulnerability_url = result[1]
                    description = result[2]
                    severity = result[3] if len(result) > 3 else 'Unknown'
                    risk_score = 'N/A'
                
                # Add finding header with risk score
                risk_score_text = f" (Risk Score: {risk_score})" if risk_score != 'N/A' else ""
                pdf.cell(0, 10, f"Finding #{i}: {vulnerability} [{severity}]{risk_score_text}", 0, 1)
                
                # Add URL
                pdf.set_font("Arial", "", 10)
                pdf.cell(0, 6, f"URL: {vulnerability_url}", 0, 1)
                
                # Check if description contains AI-suggested mitigations
                if "AI-Suggested Mitigations:" in description:
                    # Split description and mitigations
                    parts = description.split("AI-Suggested Mitigations:", 1)
                    main_desc = parts[0].strip()
                    mitigations = "AI-Suggested Mitigations:" + parts[1]
                    
                    # Add main description
                    pdf.multi_cell(0, 6, f"Description: {main_desc}")
                    
                    # Add mitigations with formatting
                    pdf.set_font("Arial", "B", 10)
                    pdf.cell(0, 6, "AI-Suggested Mitigations:", 0, 1)
                    
                    pdf.set_font("Arial", "", 10)
                    for line in parts[1].strip().split('\n'):
                        pdf.multi_cell(0, 6, line)
                else:
                    # Just add the whole description
                    pdf.multi_cell(0, 6, f"Description: {description}")
                
                # Add separator
                pdf.cell(0, 6, "", 0, 1)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.cell(0, 6, "", 0, 1)
        else:
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 10, "No vulnerabilities found.", 0, 1)
        
        # Save the PDF
        timestamp = int(time.time())
        filename = f"{scan_type.replace(' ', '_').lower()}_enhanced_{timestamp}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        pdf.output(filepath)
        
        return filepath
        
    def generate_enhanced_html_report(self, title, results, scan_type, target, summary=None):
        """
        Generate an enhanced HTML report with AI-generated content
        
        Args:
            title (str): Report title
            results (list): Scan results with enhanced AI data
            scan_type (str): Type of scan performed
            target (str): Scan target (e.g., URL, hostname)
            summary (str): Executive summary
            
        Returns:
            str: Path to the generated HTML file
        """
        # Create HTML content
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; margin-top: 30px; }}
                h3 {{ color: #2980b9; }}
                .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .summary {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .result {{ background-color: #fff; border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .severity-CRITICAL {{ color: #7d0000; }}
                .severity-HIGH {{ color: #e74c3c; }}
                .severity-MEDIUM {{ color: #f39c12; }}
                .severity-LOW {{ color: #27ae60; }}
                .severity-UNKNOWN {{ color: #7f8c8d; }}
                .risk-score {{ font-size: 16px; font-weight: bold; margin: 10px 0; }}
                .risk-CRITICAL {{ color: #7d0000; }}
                .risk-HIGH {{ color: #e74c3c; }}
                .risk-MEDIUM {{ color: #f39c12; }}
                .risk-LOW {{ color: #27ae60; }}
                .mitigations {{ background-color: #f0f7fb; padding: 10px; border-left: 4px solid #3498db; margin: 10px 0; }}
                table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .description {{ line-height: 1.5; }}
            </style>
        </head>
        <body>
            <h1>{title}</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        # Add executive summary if provided
        if summary:
            html += f"""
            <div class="summary">
                <h2>Executive Summary</h2>
                {summary.replace('\n', '<br>')}
            </div>
            """
        
        # Add scan details
        html += f"""
        <div class="details">
            <h2>Scan Details</h2>
            <p><strong>Scan Type:</strong> {scan_type}</p>
            <p><strong>Target:</strong> {target}</p>
        """
        
        # Count severity levels
        severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'UNKNOWN': 0}
        for result in results:
            if isinstance(result, dict):
                severity = result.get('severity', 'UNKNOWN')
            else:
                severity = result[3] if len(result) > 3 else 'UNKNOWN'
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Add severity summary
        html += """
            <h3>Risk Summary</h3>
            <table>
                <tr>
                    <th>Severity</th>
                    <th>Count</th>
                </tr>
        """
        
        for severity, count in severity_counts.items():
            if count > 0:
                html += f"""
                <tr>
                    <td class="severity-{severity}">{severity}</td>
                    <td>{count}</td>
                </tr>
                """
                
        html += """
            </table>
        </div>
        
        <h2>Vulnerability Details</h2>
        """
        
        # Add results
        if results:
            # Sort results by risk score if available, then by severity
            sorted_results = sorted(
                results,
                key=lambda r: (
                    -(r.get('risk_score', 0) if isinstance(r, dict) else 0),
                    {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'UNKNOWN': 4}.get(
                        r.get('severity', 'UNKNOWN') if isinstance(r, dict) else r[3] if len(r) > 3 else 'UNKNOWN',
                        5
                    )
                )
            )
            
            for i, result in enumerate(sorted_results, 1):
                # Handle different result formats
                if isinstance(result, dict):
                    # For JSON/dict format
                    vulnerability = result.get('type', 'Unknown')
                    vulnerability_url = result.get('url', 'N/A')
                    description = result.get('description', 'No description')
                    severity = result.get('severity', 'Unknown')
                    risk_score = result.get('risk_score', None)
                else:
                    # For tuple format (vulnerability, url, description, severity)
                    vulnerability = result[0]
                    vulnerability_url = result[1]
                    description = result[2]
                    severity = result[3] if len(result) > 3 else 'Unknown'
                    risk_score = None
                
                # Determine risk level for styling
                risk_level = "UNKNOWN"
                if risk_score is not None:
                    if risk_score >= 85:
                        risk_level = "CRITICAL"
                    elif risk_score >= 70:
                        risk_level = "HIGH"
                    elif risk_score >= 40:
                        risk_level = "MEDIUM"
                    else:
                        risk_level = "LOW"
                
                html += f"""
                <div class="result">
                    <h3>Finding #{i}: <span class="severity-{severity}">{vulnerability} [{severity}]</span></h3>
                    <p><strong>URL:</strong> {vulnerability_url}</p>
                """
                
                # Add risk score if available
                if risk_score is not None:
                    html += f"""
                    <p class="risk-score risk-{risk_level}">Risk Score: {risk_score}/100</p>
                    """
                
                # Check if description contains AI-suggested mitigations
                if "AI-Suggested Mitigations:" in description:
                    # Split description and mitigations
                    parts = description.split("AI-Suggested Mitigations:", 1)
                    main_desc = parts[0].strip()
                    mitigations = parts[1].strip()
                    
                    # Add main description
                    html += f"""
                    <div class="description">
                        <p><strong>Description:</strong><br>{main_desc.replace('\n', '<br>')}</p>
                    </div>
                    
                    <div class="mitigations">
                        <h4>AI-Suggested Mitigations:</h4>
                        {mitigations.replace('\n', '<br>')}
                    </div>
                    """
                else:
                    # Just add the whole description
                    html += f"""
                    <div class="description">
                        <p><strong>Description:</strong><br>{description.replace('\n', '<br>')}</p>
                    </div>
                    """
                
                html += "</div>"
        else:
            html += "<p>No vulnerabilities found.</p>"
        
        html += """
        </body>
        </html>
        """
        
        # Save the HTML
        timestamp = int(time.time())
        filename = f"{scan_type.replace(' ', '_').lower()}_enhanced_{timestamp}.html"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Open in browser
        webbrowser.open(f"file://{filepath}")
        
        return filepath
